#!/usr/bin/env swift

import AppKit
import Foundation
import ScreenCaptureKit

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

func captureDisplay(to outputPath: String, display: SCDisplay) async throws {
    let filter = SCContentFilter(display: display, excludingWindows: [])
    let config = SCStreamConfiguration()

    let image = try await SCScreenshotManager.captureImage(
        contentFilter: filter,
        configuration: config
    )

    let bitmap = NSBitmapImageRep(cgImage: image)
    guard let pngData = bitmap.representation(using: .png, properties: [:]) else {
        throw NSError(
            domain: "altic-studio.capture-active-screen",
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
}

let args = CommandLine.arguments
guard args.count >= 2 else {
    fputs("Usage: capture-active-screen.swift <output_path>\n", stderr)
    exit(1)
}

let outputPath = args[1]

do {
    let content = try await SCShareableContent.excludingDesktopWindows(false, onScreenWindowsOnly: true)
    let display = displayForFrontmostApp(content: content) ?? content.displays.first
    guard let display else {
        fputs("Could not determine a display to capture.\n", stderr)
        exit(1)
    }

    try await captureDisplay(to: outputPath, display: display)
    print(outputPath)
} catch {
    fputs("\(error.localizedDescription)\n", stderr)
    exit(1)
}
