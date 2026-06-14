#!/usr/bin/env swift

import AppKit
import Foundation
import ScreenCaptureKit
import Vision

#if canImport(FoundationModels) && canImport(_Vision_FoundationModels)
import FoundationModels
import _Vision_FoundationModels
#endif

func area(_ rect: CGRect) -> CGFloat {
    max(0, rect.width) * max(0, rect.height)
}

func fail(_ message: String, code: Int32 = 1) -> Never {
    fputs("\(message)\n", stderr)
    exit(code)
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

func recognizedLines(
    in image: CGImage,
    recognitionLevel: String,
    languages: [String],
    includeBoxes: Bool
) throws -> [[String: Any]] {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = recognitionLevel == "fast" ? .fast : .accurate
    request.usesLanguageCorrection = true
    if !languages.isEmpty {
        request.recognitionLanguages = languages
    }

    let handler = VNImageRequestHandler(cgImage: image, options: [:])
    try handler.perform([request])

    let observations = request.results ?? []
    let imageWidth = Double(image.width)
    let imageHeight = Double(image.height)

    let entries = observations.compactMap { observation -> (line: [String: Any], x: Double, y: Double)? in
        guard let candidate = observation.topCandidates(1).first else {
            return nil
        }

        let box = observation.boundingBox
        let frame = [
            "x": Double(box.minX) * imageWidth,
            "y": (1.0 - Double(box.maxY)) * imageHeight,
            "width": Double(box.width) * imageWidth,
            "height": Double(box.height) * imageHeight,
        ]
        var line: [String: Any] = [
            "text": candidate.string,
            "confidence": Double(candidate.confidence),
        ]

        if includeBoxes {
            line["frame"] = frame
        }

        return (line, frame["x"] ?? 0, frame["y"] ?? 0)
    }.sorted { lhs, rhs in
        if abs(lhs.y - rhs.y) > 4 {
            return lhs.y < rhs.y
        }
        return lhs.x < rhs.x
    }

    return entries.map { $0.line }
}

struct ScreenTextExtraction {
    let engine: String
    let text: String
    let visualUnderstanding: Any
}

func linesFromText(_ text: String) -> [[String: Any]] {
    text
        .split(separator: "\n", omittingEmptySubsequences: false)
        .map { String($0).trimmingCharacters(in: .whitespacesAndNewlines) }
        .filter { !$0.isEmpty }
        .map { line in
            [
                "text": line,
                "confidence": 1.0,
            ]
        }
}

func visualUnderstandingUnavailablePayload(mode: String, reason: String) -> Any {
    if mode == "none" {
        return NSNull()
    }

    return [
        "available": false,
        "mode": mode,
        "reason": reason,
    ]
}

#if canImport(FoundationModels) && canImport(_Vision_FoundationModels)
@available(macOS 27.0, *)
func foundationModelsTextPrompt(image: CGImage) -> Prompt {
    return Prompt {
        """
        Use OCRTool on the attached image labeled "screen". Return only the exact visible text \
        from the screen, preserving line breaks where practical. Do not summarize or add commentary.
        """
        Attachment(image)
            .label("screen")
    }
}

@available(macOS 27.0, *)
func foundationModelsVisualPrompt(for mode: String, image: CGImage, extractedText: String) -> Prompt {
    let instruction: String
    switch mode {
    case "summary":
        instruction = """
        Use the attached image labeled "screen" and the OCR text below to return a concise summary \
        of what the screen is showing. Preserve important labels, warnings, numbers, and button text.

        OCR text:
        \(extractedText)
        """
    case "ui_map":
        instruction = """
        Use the attached image labeled "screen" and the OCR text below to describe the visible UI \
        structure as compact JSON with sections, controls, and important labels. Keep the response \
        short and machine-readable.

        OCR text:
        \(extractedText)
        """
    default:
        instruction = extractedText
    }

    return Prompt {
        instruction
        Attachment(image)
            .label("screen")
    }
}

@available(macOS 27.0, *)
func extractWithFoundationModels(in image: CGImage, mode: String) async throws -> ScreenTextExtraction? {
    let model = SystemLanguageModel.default
    guard model.isAvailable else {
        return nil
    }

    let session = LanguageModelSession(
        model: model,
        tools: [
            OCRTool(),
        ],
        instructions: """
        You are a local screen text extraction engine. Prefer OCRTool whenever text \
        is needed from the attached image. Return concise, faithful output.
        """
    )

    let textResponse = try await session.respond(to: foundationModelsTextPrompt(image: image))
    let extractedText = textResponse.content.trimmingCharacters(in: .whitespacesAndNewlines)
    guard !extractedText.isEmpty else {
        return nil
    }

    let visualUnderstanding: Any
    if mode == "none" {
        visualUnderstanding = NSNull()
    } else {
        let visualResponse = try await session.respond(
            to: foundationModelsVisualPrompt(for: mode, image: image, extractedText: extractedText)
        )
        let visualContent = visualResponse.content.trimmingCharacters(in: .whitespacesAndNewlines)
        visualUnderstanding = [
            "available": true,
            "engine": "foundation_models",
            "mode": mode,
            "content": visualContent,
        ]
    }

    return ScreenTextExtraction(
        engine: "foundation_models",
        text: extractedText,
        visualUnderstanding: visualUnderstanding
    )
}
#endif

func extractWithFoundationModelsIfAvailable(in image: CGImage, mode: String) async throws -> ScreenTextExtraction? {
    #if canImport(FoundationModels) && canImport(_Vision_FoundationModels)
    if #available(macOS 27.0, *) {
        return try await extractWithFoundationModels(in: image, mode: mode)
    }
    #endif

    return nil
}

func visionExtraction(
    in image: CGImage,
    recognitionLevel: String,
    languages: [String],
    includeBoxes: Bool,
    visualUnderstanding: String
) throws -> (ScreenTextExtraction, [[String: Any]]) {
    let lines = try recognizedLines(
        in: image,
        recognitionLevel: recognitionLevel,
        languages: languages,
        includeBoxes: includeBoxes
    )
    let text = lines.compactMap { $0["text"] as? String }.joined(separator: "\n")
    let extraction = ScreenTextExtraction(
        engine: "vision",
        text: text,
        visualUnderstanding: visualUnderstandingUnavailablePayload(
            mode: visualUnderstanding,
            reason: "requires macOS 27 runtime, Apple Intelligence availability, and FoundationModels SDK"
        )
    )
    return (extraction, lines)
}

func lineMetadata(
    for extraction: ScreenTextExtraction,
    image: CGImage,
    recognitionLevel: String,
    languages: [String],
    includeBoxes: Bool
) -> [[String: Any]] {
    if extraction.engine == "foundation_models" {
        do {
            return try recognizedLines(
                in: image,
                recognitionLevel: recognitionLevel,
                languages: languages,
                includeBoxes: includeBoxes
            )
        } catch {
            return linesFromText(extraction.text)
        }
    }

    return linesFromText(extraction.text)
}

func topLevelVisualUnderstanding(for extraction: ScreenTextExtraction, mode: String) -> Any {
    if extraction.engine == "foundation_models" {
        return extraction.visualUnderstanding
    }
    if mode == "none" {
        return NSNull()
    }
    return extraction.visualUnderstanding
}

func primaryExtraction(
    in image: CGImage,
    recognitionLevel: String,
    languages: [String],
    includeBoxes: Bool,
    visualUnderstanding: String
) async throws -> (ScreenTextExtraction, [[String: Any]]) {
    if let foundationExtraction = try await extractWithFoundationModelsIfAvailable(in: image, mode: visualUnderstanding) {
        let lines = lineMetadata(
            for: foundationExtraction,
            image: image,
            recognitionLevel: recognitionLevel,
            languages: languages,
            includeBoxes: includeBoxes
        )
        return (foundationExtraction, lines.isEmpty ? linesFromText(foundationExtraction.text) : lines)
    }

    return try visionExtraction(
        in: image,
        recognitionLevel: recognitionLevel,
        languages: languages,
        includeBoxes: includeBoxes,
        visualUnderstanding: visualUnderstanding
    )
}

let args = CommandLine.arguments
guard args.count >= 2 else {
    fail("Usage: extract-screen-text.swift <output_path> [accurate|fast] [languages_csv] [include_boxes] [none|summary|ui_map]")
}

let outputPath = args[1]
let recognitionLevel = args.count >= 3 ? args[2].lowercased() : "accurate"
let languages = args.count >= 4
    ? args[3].split(separator: ",").map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
    : []
let includeBoxes = args.count >= 5 ? (args[4].lowercased() != "false") : true
let visualUnderstanding = args.count >= 6 ? args[5].lowercased() : "none"

guard ["accurate", "fast"].contains(recognitionLevel) else {
    fail("recognition_level must be one of: accurate, fast")
}
guard ["none", "summary", "ui_map"].contains(visualUnderstanding) else {
    fail("visual_understanding must be one of: none, summary, ui_map")
}

do {
    let content = try await SCShareableContent.excludingDesktopWindows(false, onScreenWindowsOnly: true)
    let display = displayForFrontmostApp(content: content) ?? content.displays.first
    guard let display else {
        fail("Could not determine a display to capture.")
    }

    let image = try await captureDisplay(to: outputPath, display: display)
    let (extraction, lines) = try await primaryExtraction(
        in: image,
        recognitionLevel: recognitionLevel,
        languages: languages,
        includeBoxes: includeBoxes,
        visualUnderstanding: visualUnderstanding
    )

    let payload: [String: Any] = [
        "action": "extract_screen_text",
        "engine": extraction.engine,
        "source": "active_screen",
        "screenshot_path": outputPath,
        "image_size": [
            "width": image.width,
            "height": image.height,
        ],
        "recognition_level": recognitionLevel,
        "text": extraction.text,
        "length_chars": extraction.text.count,
        "truncated": false,
        "lines": lines,
        "visual_understanding": topLevelVisualUnderstanding(for: extraction, mode: visualUnderstanding),
    ]

    let data = try JSONSerialization.data(withJSONObject: payload, options: [.prettyPrinted, .sortedKeys])
    guard let json = String(data: data, encoding: .utf8) else {
        fail("Could not encode OCR payload as UTF-8.")
    }
    print(json)
} catch {
    fail(error.localizedDescription)
}
