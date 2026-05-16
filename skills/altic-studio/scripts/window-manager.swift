#!/usr/bin/env swift

import AppKit
import ApplicationServices
import CoreGraphics
import Foundation

enum WindowManagerError: Error, CustomStringConvertible {
    case message(String)

    var description: String {
        switch self {
        case .message(let value):
            return value
        }
    }
}

struct ManagedApp {
    let name: String
    let bundleID: String
    let pid: pid_t
    let application: NSRunningApplication
}

struct CGWindowRecord {
    let windowID: Int
    let pid: pid_t
    let title: String
    let frame: CGRect
}

struct ManagedWindow {
    let windowID: Int
    let app: ManagedApp
    let title: String
    var frame: CGRect
    let axWindow: AXUIElement?
    let isMinimized: Bool
}

func fail(_ message: String) throws -> Never {
    throw WindowManagerError.message(message)
}

func parsePayload(_ text: String) throws -> [String: Any] {
    guard let data = text.data(using: .utf8) else {
        try fail("payload is not valid UTF-8")
    }
    let decoded = try JSONSerialization.jsonObject(with: data)
    guard let payload = decoded as? [String: Any] else {
        try fail("payload must be a JSON object")
    }
    return payload
}

func printJSON(_ payload: [String: Any]) throws {
    let data = try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
    guard let text = String(data: data, encoding: .utf8) else {
        try fail("failed to encode JSON response")
    }
    print(text)
}

func intValue(_ payload: [String: Any], _ key: String) -> Int? {
    if let value = payload[key] as? Int {
        return value
    }
    if let value = payload[key] as? Double {
        return Int(value)
    }
    return nil
}

func stringValue(_ payload: [String: Any], _ key: String) -> String? {
    guard let value = payload[key] as? String else {
        return nil
    }
    let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
    return trimmed.isEmpty ? nil : trimmed
}

func boolValue(_ payload: [String: Any], _ key: String, default defaultValue: Bool) -> Bool {
    return (payload[key] as? Bool) ?? defaultValue
}

func stringArrayValue(_ payload: [String: Any], _ key: String) -> [String] {
    guard let values = payload[key] as? [String] else {
        return []
    }
    return values.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
}

func appPayload(_ app: ManagedApp, isActive: Bool? = nil) -> [String: Any] {
    var payload: [String: Any] = [
        "name": app.name,
        "bundle_id": app.bundleID,
        "pid": Int(app.pid),
    ]
    if let isActive {
        payload["is_active"] = isActive
    }
    return payload
}

func frontmostApp() throws -> ManagedApp {
    guard let app = NSWorkspace.shared.frontmostApplication else {
        try fail("could not determine frontmost application")
    }
    return ManagedApp(
        name: app.localizedName ?? app.bundleIdentifier ?? "Unknown",
        bundleID: app.bundleIdentifier ?? "",
        pid: app.processIdentifier,
        application: app
    )
}

func managedApp(from application: NSRunningApplication) -> ManagedApp {
    return ManagedApp(
        name: application.localizedName ?? application.bundleIdentifier ?? "Unknown",
        bundleID: application.bundleIdentifier ?? "",
        pid: application.processIdentifier,
        application: application
    )
}

func appMatches(_ app: NSRunningApplication, query: String) -> Bool {
    let needle = query.lowercased()
    let values = [
        app.localizedName,
        app.bundleIdentifier,
        app.executableURL?.lastPathComponent,
    ]
    return values.compactMap { $0?.lowercased() }.contains { $0.contains(needle) }
}

func resolveApp(named appName: String?) throws -> ManagedApp {
    guard let appName, !appName.isEmpty else {
        return try frontmostApp()
    }

    let matches = NSWorkspace.shared.runningApplications
        .filter { !$0.isTerminated && appMatches($0, query: appName) }
        .map(managedApp)

    if matches.isEmpty {
        try fail("no running app matched: \(appName)")
    }
    if matches.count > 1 {
        let names = matches.map { "\($0.name) (\($0.bundleID))" }.joined(separator: ", ")
        try fail("multiple apps matched \(appName): \(names)")
    }
    return matches[0]
}

func copyAttribute(_ element: AXUIElement, _ attribute: String) -> AnyObject? {
    var value: CFTypeRef?
    let result = AXUIElementCopyAttributeValue(element, attribute as CFString, &value)
    guard result == .success else {
        return nil
    }
    return value as AnyObject?
}

func setAttribute(_ element: AXUIElement, _ attribute: String, _ value: CFTypeRef) throws {
    let result = AXUIElementSetAttributeValue(element, attribute as CFString, value)
    if result != .success {
        try fail("failed to set \(attribute): AXError \(result.rawValue)")
    }
}

func axBool(_ value: AnyObject?) -> Bool {
    guard let value else {
        return false
    }
    return (value as? Bool) ?? false
}

func axString(_ value: AnyObject?) -> String {
    guard let value else {
        return ""
    }
    return (value as? String) ?? ""
}

func axPoint(_ value: AnyObject?) -> CGPoint? {
    guard let value else {
        return nil
    }
    if CFGetTypeID(value) != AXValueGetTypeID() {
        return nil
    }
    var point = CGPoint.zero
    let ok = AXValueGetValue(value as! AXValue, .cgPoint, &point)
    return ok ? point : nil
}

func axSize(_ value: AnyObject?) -> CGSize? {
    guard let value else {
        return nil
    }
    if CFGetTypeID(value) != AXValueGetTypeID() {
        return nil
    }
    var size = CGSize.zero
    let ok = AXValueGetValue(value as! AXValue, .cgSize, &size)
    return ok ? size : nil
}

func makeAXPoint(_ point: CGPoint) -> AXValue {
    var mutable = point
    return AXValueCreate(.cgPoint, &mutable)!
}

func makeAXSize(_ size: CGSize) -> AXValue {
    var mutable = size
    return AXValueCreate(.cgSize, &mutable)!
}

func axWindows(for app: ManagedApp) -> [AXUIElement] {
    let appElement = AXUIElementCreateApplication(app.pid)
    guard let values = copyAttribute(appElement, kAXWindowsAttribute) as? [AXUIElement] else {
        return []
    }
    return values
}

func frame(for axWindow: AXUIElement) -> CGRect? {
    guard
        let position = axPoint(copyAttribute(axWindow, kAXPositionAttribute)),
        let size = axSize(copyAttribute(axWindow, kAXSizeAttribute))
    else {
        return nil
    }
    return CGRect(origin: position, size: size)
}

func cgWindows() -> [CGWindowRecord] {
    guard
        let records = CGWindowListCopyWindowInfo(
            [.optionOnScreenOnly, .excludeDesktopElements],
            kCGNullWindowID
        ) as? [[String: Any]]
    else {
        return []
    }

    return records.compactMap { record in
        guard
            let windowID = record[kCGWindowNumber as String] as? Int,
            let pid = record[kCGWindowOwnerPID as String] as? pid_t,
            let layer = record[kCGWindowLayer as String] as? Int,
            let bounds = record[kCGWindowBounds as String] as? [String: Any]
        else {
            return nil
        }
        if layer != 0 {
            return nil
        }
        let x = (bounds["X"] as? CGFloat) ?? CGFloat(bounds["X"] as? Double ?? 0)
        let y = (bounds["Y"] as? CGFloat) ?? CGFloat(bounds["Y"] as? Double ?? 0)
        let width = (bounds["Width"] as? CGFloat) ?? CGFloat(bounds["Width"] as? Double ?? 0)
        let height = (bounds["Height"] as? CGFloat) ?? CGFloat(bounds["Height"] as? Double ?? 0)
        if width <= 0 || height <= 0 {
            return nil
        }
        let title = (record[kCGWindowName as String] as? String) ?? ""
        return CGWindowRecord(
            windowID: windowID,
            pid: pid,
            title: title,
            frame: CGRect(x: x, y: y, width: width, height: height)
        )
    }
}

func frameDistance(_ lhs: CGRect, _ rhs: CGRect) -> CGFloat {
    return abs(lhs.origin.x - rhs.origin.x)
        + abs(lhs.origin.y - rhs.origin.y)
        + abs(lhs.width - rhs.width)
        + abs(lhs.height - rhs.height)
}

func managedWindows(appName: String? = nil, includeMinimized: Bool = false) throws -> [ManagedWindow] {
    let candidateApps: [ManagedApp]
    if let appName, !appName.isEmpty {
        candidateApps = [try resolveApp(named: appName)]
    } else {
        candidateApps = NSWorkspace.shared.runningApplications
            .filter { !$0.isTerminated && $0.activationPolicy == .regular }
            .map(managedApp)
    }

    let cgRecords = cgWindows()
    var windows: [ManagedWindow] = []
    var matchedCGWindowIDs = Set<Int>()

    for app in candidateApps {
        for axWindow in axWindows(for: app) {
            let role = axString(copyAttribute(axWindow, kAXRoleAttribute))
            let subrole = axString(copyAttribute(axWindow, kAXSubroleAttribute))
            if role != kAXWindowRole {
                continue
            }
            if !subrole.isEmpty
                && subrole != kAXStandardWindowSubrole
                && subrole != kAXDialogSubrole
            {
                continue
            }
            let minimized = axBool(copyAttribute(axWindow, kAXMinimizedAttribute))
            if minimized && !includeMinimized {
                continue
            }
            guard let axFrame = frame(for: axWindow) else {
                continue
            }
            if axFrame.width <= 0 || axFrame.height <= 0 {
                continue
            }

            let matchingCG = cgRecords
                .filter { $0.pid == app.pid }
                .min { frameDistance($0.frame, axFrame) < frameDistance($1.frame, axFrame) }
            if let matchingCG {
                matchedCGWindowIDs.insert(matchingCG.windowID)
            }
            let title = axString(copyAttribute(axWindow, kAXTitleAttribute))
            windows.append(
                ManagedWindow(
                    windowID: matchingCG?.windowID ?? 0,
                    app: app,
                    title: title.isEmpty ? (matchingCG?.title ?? "") : title,
                    frame: axFrame,
                    axWindow: axWindow,
                    isMinimized: minimized
                )
            )
        }

        for cgWindow in cgRecords where cgWindow.pid == app.pid && !matchedCGWindowIDs.contains(cgWindow.windowID) {
            if cgWindow.title.isEmpty {
                continue
            }
            windows.append(
                ManagedWindow(
                    windowID: cgWindow.windowID,
                    app: app,
                    title: cgWindow.title,
                    frame: cgWindow.frame,
                    axWindow: nil,
                    isMinimized: false
                )
            )
        }
    }

    return windows
}

func area(_ rect: CGRect) -> CGFloat {
    return max(0, rect.width) * max(0, rect.height)
}

func screenForDisplayIndex(_ index: Int?) throws -> (index: Int, screen: NSScreen) {
    let screens = NSScreen.screens
    guard !screens.isEmpty else {
        try fail("no displays available")
    }
    guard let index else {
        return (1, NSScreen.main ?? screens[0])
    }
    if index < 1 || index > screens.count {
        try fail("display_index out of range: \(index)")
    }
    return (index, screens[index - 1])
}

func screenForWindow(_ window: ManagedWindow, displayIndex: Int?) throws -> (index: Int, screen: NSScreen) {
    if displayIndex != nil {
        return try screenForDisplayIndex(displayIndex)
    }
    let screens = NSScreen.screens
    guard !screens.isEmpty else {
        try fail("no displays available")
    }
    let best = screens.enumerated().max { lhs, rhs in
        area(lhs.element.visibleFrame.intersection(window.frame))
            < area(rhs.element.visibleFrame.intersection(window.frame))
    }
    if let best {
        return (best.offset + 1, best.element)
    }
    return (1, NSScreen.main ?? screens[0])
}

func displayIndex(for rect: CGRect) -> Int {
    let screens = NSScreen.screens
    guard !screens.isEmpty else {
        return 0
    }
    let best = screens.enumerated().max { lhs, rhs in
        area(lhs.element.visibleFrame.intersection(rect))
            < area(rhs.element.visibleFrame.intersection(rect))
    }
    return (best?.offset ?? 0) + 1
}

func clampedFrame(_ rect: CGRect, to screen: NSScreen) -> CGRect {
    let visible = screen.visibleFrame
    let width = min(max(rect.width, 120), visible.width)
    let height = min(max(rect.height, 80), visible.height)
    let maxX = visible.maxX - width
    let maxY = visible.maxY - height
    let x = min(max(rect.origin.x, visible.minX), maxX)
    let y = min(max(rect.origin.y, visible.minY), maxY)
    return CGRect(x: x, y: y, width: width, height: height)
}

func windowPayload(_ window: ManagedWindow) -> [String: Any] {
    return [
        "window_id": window.windowID,
        "app_name": window.app.name,
        "bundle_id": window.app.bundleID,
        "pid": Int(window.app.pid),
        "title": window.title,
        "x": Int(window.frame.origin.x.rounded()),
        "y": Int(window.frame.origin.y.rounded()),
        "width": Int(window.frame.width.rounded()),
        "height": Int(window.frame.height.rounded()),
        "display_index": displayIndex(for: window.frame),
        "is_minimized": window.isMinimized,
        "is_frontmost_app": window.app.pid == NSWorkspace.shared.frontmostApplication?.processIdentifier,
    ]
}

func resolveWindow(_ payload: [String: Any], includeMinimized: Bool = false) throws -> ManagedWindow {
    let appName = stringValue(payload, "app_name")
    let windowID = intValue(payload, "window_id")
    let windowIndex = intValue(payload, "window_index") ?? 1

    if let windowID {
        let windows = try managedWindows(appName: appName, includeMinimized: includeMinimized)
        if let window = windows.first(where: { $0.windowID == windowID }) {
            return window
        }
        try fail("no window matched window_id: \(windowID)")
    }

    let windows = try managedWindows(appName: appName, includeMinimized: includeMinimized)
    if windows.isEmpty {
        if let appName {
            try fail("no manageable windows found for app: \(appName)")
        }
        try fail("no manageable windows found")
    }
    if windowIndex < 1 || windowIndex > windows.count {
        try fail("window_index out of range: \(windowIndex)")
    }
    return windows[windowIndex - 1]
}

func requireAXWindow(_ window: ManagedWindow) throws -> AXUIElement {
    guard let axWindow = window.axWindow else {
        try fail("window does not expose Accessibility controls")
    }
    return axWindow
}

func applyFrame(_ rect: CGRect, to window: ManagedWindow) throws -> ManagedWindow {
    let axWindow = try requireAXWindow(window)
    try setAttribute(axWindow, kAXPositionAttribute, makeAXPoint(rect.origin))
    try setAttribute(axWindow, kAXSizeAttribute, makeAXSize(rect.size))
    var updated = window
    updated.frame = rect
    return updated
}

func handleGetFrontmostApp() throws -> [String: Any] {
    let app = try frontmostApp()
    return [
        "action": "get_frontmost_app",
        "app": appPayload(app, isActive: app.application.isActive),
    ]
}

func handleListWindows(_ payload: [String: Any]) throws -> [String: Any] {
    let windows = try managedWindows(
        appName: stringValue(payload, "app_name"),
        includeMinimized: boolValue(payload, "include_minimized", default: false)
    )
    return [
        "action": "list_windows",
        "windows": windows.map(windowPayload),
        "count": windows.count,
    ]
}

func handleFocusWindow(_ payload: [String: Any]) throws -> [String: Any] {
    let window = try resolveWindow(payload, includeMinimized: true)
    window.app.application.activate(options: [.activateAllWindows])
    let axWindow = try requireAXWindow(window)
    try setAttribute(axWindow, kAXMainAttribute, kCFBooleanTrue)
    try setAttribute(axWindow, kAXFocusedAttribute, kCFBooleanTrue)
    return ["action": "focus_window", "window": windowPayload(window)]
}

func handleMoveWindow(_ payload: [String: Any]) throws -> [String: Any] {
    let window = try resolveWindow(payload)
    guard let x = intValue(payload, "x"), let y = intValue(payload, "y") else {
        try fail("x and y are required")
    }
    let screen = try screenForWindow(window, displayIndex: intValue(payload, "display_index")).screen
    let target = clampedFrame(
        CGRect(x: CGFloat(x), y: CGFloat(y), width: window.frame.width, height: window.frame.height),
        to: screen
    )
    let updated = try applyFrame(target, to: window)
    return ["action": "move_window", "window": windowPayload(updated)]
}

func handleResizeWindow(_ payload: [String: Any]) throws -> [String: Any] {
    let window = try resolveWindow(payload)
    guard let width = intValue(payload, "width"), let height = intValue(payload, "height") else {
        try fail("width and height are required")
    }
    let screen = try screenForWindow(window, displayIndex: intValue(payload, "display_index")).screen
    let target = clampedFrame(
        CGRect(
            x: window.frame.origin.x,
            y: window.frame.origin.y,
            width: CGFloat(width),
            height: CGFloat(height)
        ),
        to: screen
    )
    let updated = try applyFrame(target, to: window)
    return ["action": "resize_window", "window": windowPayload(updated)]
}

func handleCenterWindow(_ payload: [String: Any]) throws -> [String: Any] {
    let window = try resolveWindow(payload)
    let (_, screen) = try screenForWindow(window, displayIndex: intValue(payload, "display_index"))
    let visible = screen.visibleFrame
    let width = CGFloat(intValue(payload, "width") ?? Int(window.frame.width.rounded()))
    let height = CGFloat(intValue(payload, "height") ?? Int(window.frame.height.rounded()))
    let rect = CGRect(
        x: visible.minX + ((visible.width - width) / 2),
        y: visible.minY + ((visible.height - height) / 2),
        width: width,
        height: height
    )
    let updated = try applyFrame(clampedFrame(rect, to: screen), to: window)
    return ["action": "center_window", "window": windowPayload(updated)]
}

func tileFrame(
    index: Int,
    count: Int,
    layout: String,
    visible: CGRect,
    padding: CGFloat
) -> CGRect {
    let padded = visible.insetBy(dx: padding, dy: padding)
    if layout == "rows" {
        let height = padded.height / CGFloat(count)
        return CGRect(
            x: padded.minX,
            y: padded.minY + (height * CGFloat(index)),
            width: padded.width,
            height: height
        ).insetBy(dx: padding / 2, dy: padding / 2)
    }
    if layout == "grid" {
        let columns = Int(ceil(sqrt(Double(count))))
        let rows = Int(ceil(Double(count) / Double(columns)))
        let column = index % columns
        let row = index / columns
        let width = padded.width / CGFloat(columns)
        let height = padded.height / CGFloat(rows)
        return CGRect(
            x: padded.minX + (width * CGFloat(column)),
            y: padded.minY + (height * CGFloat(row)),
            width: width,
            height: height
        ).insetBy(dx: padding / 2, dy: padding / 2)
    }

    let width = padded.width / CGFloat(count)
    return CGRect(
        x: padded.minX + (width * CGFloat(index)),
        y: padded.minY,
        width: width,
        height: padded.height
    ).insetBy(dx: padding / 2, dy: padding / 2)
}

func tileTargets(_ payload: [String: Any]) throws -> [ManagedWindow] {
    let appNames = stringArrayValue(payload, "app_names")
    if !appNames.isEmpty {
        return try appNames.map { appName in
            try resolveWindow(["app_name": appName])
        }
    }
    return try managedWindows().filter { !$0.isMinimized }
}

func handleTileWindows(_ payload: [String: Any]) throws -> [String: Any] {
    let layout = stringValue(payload, "layout") ?? "columns"
    if !["columns", "rows", "grid"].contains(layout) {
        try fail("layout must be one of: columns, grid, rows")
    }
    let padding = CGFloat(intValue(payload, "padding") ?? 8)
    let targets = try tileTargets(payload)
    if targets.isEmpty {
        try fail("no windows available to tile")
    }
    let screen = try screenForDisplayIndex(intValue(payload, "display_index")).screen
    var updatedWindows: [[String: Any]] = []
    for (index, window) in targets.enumerated() {
        let rect = clampedFrame(
            tileFrame(
                index: index,
                count: targets.count,
                layout: layout,
                visible: screen.visibleFrame,
                padding: padding
            ),
            to: screen
        )
        let updated = try applyFrame(rect, to: window)
        updatedWindows.append(windowPayload(updated))
    }
    return ["action": "tile_windows", "windows": updatedWindows, "count": updatedWindows.count]
}

func handleMinimize(_ payload: [String: Any]) throws -> [String: Any] {
    let window = try resolveWindow(payload, includeMinimized: true)
    let axWindow = try requireAXWindow(window)
    try setAttribute(axWindow, kAXMinimizedAttribute, kCFBooleanTrue)
    return ["action": "minimize", "window": windowPayload(window)]
}

func handleHideApp(_ payload: [String: Any]) throws -> [String: Any] {
    guard let appName = stringValue(payload, "app_name") else {
        try fail("app_name is required")
    }
    let app = try resolveApp(named: appName)
    _ = app.application.hide()
    return [
        "action": "hide_app",
        "app_name": app.name,
        "bundle_id": app.bundleID,
        "pid": Int(app.pid),
    ]
}

func handleQuitApp(_ payload: [String: Any]) throws -> [String: Any] {
    guard let appName = stringValue(payload, "app_name") else {
        try fail("app_name is required")
    }
    let app = try resolveApp(named: appName)
    _ = app.application.terminate()
    return [
        "action": "quit_app",
        "app_name": app.name,
        "bundle_id": app.bundleID,
        "pid": Int(app.pid),
    ]
}

let args = CommandLine.arguments

do {
    guard args.count == 3 else {
        try fail("Usage: window-manager.swift <action> <payload-json>")
    }

    let action = args[1]
    let payload = try parsePayload(args[2])
    let response: [String: Any]

    switch action {
    case "get_frontmost_app":
        response = try handleGetFrontmostApp()
    case "list_windows":
        response = try handleListWindows(payload)
    case "focus_window":
        response = try handleFocusWindow(payload)
    case "move_window":
        response = try handleMoveWindow(payload)
    case "resize_window":
        response = try handleResizeWindow(payload)
    case "center_window":
        response = try handleCenterWindow(payload)
    case "tile_windows":
        response = try handleTileWindows(payload)
    case "minimize":
        response = try handleMinimize(payload)
    case "hide_app":
        response = try handleHideApp(payload)
    case "quit_app":
        response = try handleQuitApp(payload)
    default:
        try fail("unknown action: \(action)")
    }

    try printJSON(response)
} catch {
    fputs("\(error)\n", stderr)
    exit(1)
}
