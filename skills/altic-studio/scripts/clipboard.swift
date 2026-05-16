import AppKit
import Foundation

func emitJSON(_ object: [String: Any]) {
    do {
        let data = try JSONSerialization.data(
            withJSONObject: object,
            options: [.prettyPrinted, .sortedKeys]
        )
        if let output = String(data: data, encoding: .utf8) {
            print(output)
        }
    } catch {
        fputs("Unable to encode JSON: \(error.localizedDescription)\n", stderr)
        exit(1)
    }
}

func fail(_ message: String) -> Never {
    fputs(message + "\n", stderr)
    exit(1)
}

func filePayload(for url: URL) -> [String: Any] {
    let path = url.path
    let exists = FileManager.default.fileExists(atPath: path)
    return [
        "path": path,
        "name": url.lastPathComponent,
        "exists": exists,
        "is_file_url": url.isFileURL
    ]
}

func getFiles() {
    let pasteboard = NSPasteboard.general
    let urls = pasteboard.readObjects(forClasses: [NSURL.self], options: nil) as? [URL] ?? []
    let fileUrls = urls.filter { $0.isFileURL }
    emitJSON([
        "action": "get_clipboard_files",
        "count": fileUrls.count,
        "files": fileUrls.map { filePayload(for: $0) }
    ])
}

func setFiles(_ paths: ArraySlice<String>) {
    if paths.isEmpty {
        fail("paths cannot be empty")
    }

    let urls = paths.map { URL(fileURLWithPath: $0) }
    let pasteboard = NSPasteboard.general
    pasteboard.clearContents()
    if !pasteboard.writeObjects(urls as [NSURL]) {
        fail("unable to write file URLs to clipboard")
    }

    emitJSON([
        "action": "set_clipboard_files",
        "count": urls.count,
        "files": urls.map { filePayload(for: $0) }
    ])
}

func saveImage(_ path: String?) {
    guard let path else {
        fail("output path is required")
    }

    let pasteboard = NSPasteboard.general
    guard let image = NSImage(pasteboard: pasteboard) else {
        fail("clipboard does not contain an image")
    }

    guard
        let tiffData = image.tiffRepresentation,
        let bitmap = NSBitmapImageRep(data: tiffData),
        let pngData = bitmap.representation(using: .png, properties: [:])
    else {
        fail("unable to convert clipboard image to PNG")
    }

    let url = URL(fileURLWithPath: path)
    do {
        try pngData.write(to: url)
        print(url.path)
    } catch {
        fail("unable to write clipboard image: \(error.localizedDescription)")
    }
}

func setImage(_ path: String?) {
    guard let path else {
        fail("image path is required")
    }

    let url = URL(fileURLWithPath: path)
    guard let image = NSImage(contentsOf: url) else {
        fail("unable to load image file")
    }

    let pasteboard = NSPasteboard.general
    pasteboard.clearContents()
    if !pasteboard.writeObjects([image]) {
        fail("unable to write image to clipboard")
    }

    emitJSON([
        "action": "set_clipboard_image",
        "path": url.path,
        "name": url.lastPathComponent
    ])
}

let args = CommandLine.arguments.dropFirst()
guard let command = args.first else {
    fail("clipboard command is required")
}

switch command {
case "get-files":
    getFiles()
case "set-files":
    setFiles(args.dropFirst())
case "save-image":
    saveImage(args.dropFirst().first)
case "set-image":
    setImage(args.dropFirst().first)
default:
    fail("unknown clipboard command: \(command)")
}
