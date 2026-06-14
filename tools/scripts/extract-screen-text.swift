#!/usr/bin/env swift

import AppKit
import Foundation
import ScreenCaptureKit
import Vision

#if canImport(FoundationModels)
import FoundationModels
#endif

#if canImport(_Vision_FoundationModels)
import _Vision_FoundationModels
#endif

struct OCRLine: Encodable {
    let text: String
    let confidence: Float
}

struct VisualSummaryResult {
    let summary: String
    let available: Bool
    let source: String
    let prompt: String
    let error: String
}

struct ScreenTextOutput: Encodable {
    let action: String
    let screenshot_path: String
    let text: String
    let line_count: Int
    let average_confidence: Float
    let truncated: Bool
    let visual_summary: String
    let visual_model_available: Bool
    let visual_model_source: String
    let visual_prompt: String
    let visual_error: String
}

func area(_ rect: CGRect) -> CGFloat {
    max(0, rect.width) * max(0, rect.height)
}

func displayForFrontmostApp(content: SCShareableContent) -> SCDisplay? {
    guard let app = NSWorkspace.shared.frontmostApplication else {
        return nil
    }

    let targetPID = app.processIdentifier
    let appWindows = content.windows.filter { window in
        window.owningApplication?.processID == targetPID
    }

    guard
        let frontWindow = appWindows.max(by: { lhs, rhs in
            area(lhs.frame) < area(rhs.frame)
        })
    else {
        return nil
    }

    let targetRect = frontWindow.frame
    return content.displays.max(by: { lhs, rhs in
        area(lhs.frame.intersection(targetRect)) < area(rhs.frame.intersection(targetRect))
    })
}

func captureDisplay(to outputPath: String, display: SCDisplay) async throws -> CGImage {
    let filter = SCContentFilter(display: display, excludingWindows: [])
    let config = SCStreamConfiguration()

    let image = try await SCScreenshotManager.captureImage(
        contentFilter: filter,
        configuration: config
    )

    let bitmap = NSBitmapImageRep(cgImage: image)
    guard let pngData = bitmap.representation(using: .png, properties: [:]) else {
        throw NSError(
            domain: "altic-mcp.extract-screen-text",
            code: 2,
            userInfo: [NSLocalizedDescriptionKey: "Could not encode screenshot as PNG."]
        )
    }

    let outputURL = URL(fileURLWithPath: outputPath)
    try FileManager.default.createDirectory(
        at: outputURL.deletingLastPathComponent(),
        withIntermediateDirectories: true
    )
    try pngData.write(to: outputURL)

    return image
}

func recognizeText(in image: CGImage) throws -> [OCRLine] {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true

    let handler = VNImageRequestHandler(cgImage: image, options: [:])
    try handler.perform([request])

    let observations = request.results ?? []
    return observations.compactMap { observation in
        guard let candidate = observation.topCandidates(1).first else {
            return nil
        }
        return OCRLine(text: candidate.string, confidence: candidate.confidence)
    }
}

func unavailableVisualSummary(prompt: String, reason: String) -> VisualSummaryResult {
    VisualSummaryResult(
        summary: "",
        available: false,
        source: "",
        prompt: prompt,
        error: reason
    )
}

@available(macOS 27.0, *)
func generateFoundationVisualSummary(imageURL: URL, prompt: String) async -> VisualSummaryResult {
    #if canImport(FoundationModels) && canImport(_Vision_FoundationModels)
    do {
        let model = SystemLanguageModel()
        let session = LanguageModelSession(model: model, tools: [OCRTool()])
        let response = try await session.respond {
            prompt
            Attachment(imageURL: imageURL)
                .label("screen")
        }

        return VisualSummaryResult(
            summary: response.content,
            available: true,
            source: "FoundationModels.SystemLanguageModel",
            prompt: prompt,
            error: ""
        )
    } catch {
        return unavailableVisualSummary(
            prompt: prompt,
            reason: "FoundationModels visual summary failed: \(error.localizedDescription)"
        )
    }
    #else
    return unavailableVisualSummary(
        prompt: prompt,
        reason: "FoundationModels visual image tools are not available in this Swift toolchain"
    )
    #endif
}

let args = CommandLine.arguments
guard args.count >= 2 else {
    fputs("Usage: extract-screen-text.swift <output_path> [include_visual_summary] [visual_prompt]\n", stderr)
    exit(1)
}

let outputPath = args[1]
let includeVisualSummary = args.count >= 3 && ["1", "true", "yes"].contains(args[2].lowercased())
let visualPrompt = args.count >= 4
    ? args.dropFirst(3).joined(separator: " ")
    : "Summarize the visible screen content and call out actionable UI text."

do {
    let content = try await SCShareableContent.excludingDesktopWindows(false, onScreenWindowsOnly: true)
    let display = displayForFrontmostApp(content: content) ?? content.displays.first
    guard let display else {
        fputs("Could not determine a display to capture.\n", stderr)
        exit(1)
    }

    let image = try await captureDisplay(to: outputPath, display: display)
    let lines = try recognizeText(in: image)
    let text = lines.map(\.text).joined(separator: "\n")
    let averageConfidence = lines.isEmpty
        ? Float(0)
        : lines.map(\.confidence).reduce(Float(0), +) / Float(lines.count)

    let visualSummary: VisualSummaryResult
    if includeVisualSummary {
        if #available(macOS 27.0, *) {
            visualSummary = await generateFoundationVisualSummary(
                imageURL: URL(fileURLWithPath: outputPath),
                prompt: visualPrompt
            )
        } else {
            visualSummary = unavailableVisualSummary(
                prompt: visualPrompt,
                reason: "FoundationModels visual understanding requires macOS 27 or later"
            )
        }
    } else {
        visualSummary = VisualSummaryResult(
            summary: "",
            available: false,
            source: "",
            prompt: "",
            error: ""
        )
    }

    let output = ScreenTextOutput(
        action: "extract_screen_text",
        screenshot_path: outputPath,
        text: text,
        line_count: lines.count,
        average_confidence: averageConfidence,
        truncated: false,
        visual_summary: visualSummary.summary,
        visual_model_available: visualSummary.available,
        visual_model_source: visualSummary.source,
        visual_prompt: visualSummary.prompt,
        visual_error: visualSummary.error
    )

    let encoder = JSONEncoder()
    encoder.outputFormatting = [.withoutEscapingSlashes]
    let data = try encoder.encode(output)
    guard let json = String(data: data, encoding: .utf8) else {
        fputs("Could not encode OCR response as JSON.\n", stderr)
        exit(1)
    }
    print(json)
} catch {
    fputs("\(error.localizedDescription)\n", stderr)
    exit(1)
}
