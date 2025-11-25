#!/usr/bin/env swift

import Cocoa
import Foundation
import SwiftUI
import QuartzCore

struct PulsingBorderView: View {
    @State private var opacity: Double = 0.3
    @State private var hueRotation: Double = 0
    let edge: Edge
    
    enum Edge {
        case top, bottom, left, right
    }
    
    var body: some View {
        ZStack {
            // Create gradient that fades from edge to transparent
            let fadeGradient: LinearGradient = {
                switch edge {
                case .top:
                    return LinearGradient(
                        gradient: Gradient(colors: [
                            gradientColor(),
                            gradientColor().opacity(0.8),
                            gradientColor().opacity(0.3),
                            Color.clear
                        ]),
                        startPoint: .top,
                        endPoint: .bottom
                    )
                case .bottom:
                    return LinearGradient(
                        gradient: Gradient(colors: [
                            gradientColor(),
                            gradientColor().opacity(0.8),
                            gradientColor().opacity(0.3),
                            Color.clear
                        ]),
                        startPoint: .bottom,
                        endPoint: .top
                    )
                case .left:
                    return LinearGradient(
                        gradient: Gradient(colors: [
                            gradientColor(),
                            gradientColor().opacity(0.8),
                            gradientColor().opacity(0.3),
                            Color.clear
                        ]),
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                case .right:
                    return LinearGradient(
                        gradient: Gradient(colors: [
                            gradientColor(),
                            gradientColor().opacity(0.8),
                            gradientColor().opacity(0.3),
                            Color.clear
                        ]),
                        startPoint: .trailing,
                        endPoint: .leading
                    )
                }
            }()
            
            fadeGradient
                .hueRotation(Angle(degrees: hueRotation))
                .opacity(opacity)
                .blur(radius: 8)
        }
        .onAppear {
            // Smooth pulsing animation
            withAnimation(
                Animation.easeInOut(duration: 2.0)
                    .repeatForever(autoreverses: true)
            ) {
                opacity = 0.7
            }
            
            // Slowly rotating hue for color shift
            withAnimation(
                Animation.linear(duration: 15.0)
                    .repeatForever(autoreverses: false)
            ) {
                hueRotation = 360
            }
        }
    }
    
    private func gradientColor() -> Color {
        // Rainbow gradient base color
        Color(red: 0.8, green: 0.3, blue: 1.0)
    }
}

class ScreenGlowManager {
    static var windows: [NSWindow] = []
    
    static func addGlow() {
        guard let screen = NSScreen.main else {
            print("Error: Could not get main screen")
            exit(1)
        }
        
        let frame = screen.frame
        let thickness: CGFloat = 50  // Thicker for gradual fade
        
        // Define edge positions: (x, y, width, height, edge)
        let edges: [(CGFloat, CGFloat, CGFloat, CGFloat, PulsingBorderView.Edge)] = [
            (0, frame.height - thickness, frame.width, thickness, .top),  // Top
            (0, 0, frame.width, thickness, .bottom),                       // Bottom
            (0, 0, thickness, frame.height, .left),                        // Left
            (frame.width - thickness, 0, thickness, frame.height, .right) // Right
        ]
        
        // Create window for each edge with SwiftUI view
        for (x, y, width, height, edge) in edges {
            let rect = NSRect(x: x, y: y, width: width, height: height)
            let window = NSWindow(
                contentRect: rect,
                styleMask: [.borderless],
                backing: .buffered,
                defer: false
            )
            
            // Use SwiftUI hosting view for smooth animations
            let hostingView = NSHostingView(rootView: PulsingBorderView(edge: edge))
            window.contentView = hostingView
            
            // Configure window
            window.backgroundColor = .clear
            window.level = .statusBar
            window.isOpaque = false
            window.hasShadow = false
            window.ignoresMouseEvents = true
            window.collectionBehavior = [.canJoinAllSpaces, .stationary, .fullScreenAuxiliary]
            
            // Show window
            window.orderFrontRegardless()
            windows.append(window)
        }
        
        // Write window count to temp file for tracking
        let windowCount = windows.count
        if let homeDir = FileManager.default.homeDirectoryForCurrentUser.path as String? {
            let pidFile = "\(homeDir)/.altic_glow_pid"
            try? "\(ProcessInfo.processInfo.processIdentifier)".write(
                toFile: pidFile,
                atomically: true,
                encoding: .utf8
            )
        }
        
        print("Screen glow activated - \(windowCount) windows created")
        
        // Keep the process running
        RunLoop.main.run()
    }
    
    static func removeGlow() {
        // Kill any existing glow process
        if let homeDir = FileManager.default.homeDirectoryForCurrentUser.path as String? {
            let pidFile = "\(homeDir)/.altic_glow_pid"
            if let pidString = try? String(contentsOfFile: pidFile, encoding: .utf8),
               let pid = Int32(pidString.trimmingCharacters(in: .whitespacesAndNewlines)) {
                kill(pid, SIGTERM)
                try? FileManager.default.removeItem(atPath: pidFile)
                print("Screen glow removed - process \(pid) terminated")
            } else {
                print("No active screen glow found")
            }
        }
    }
}

// Parse command line arguments
let args = CommandLine.arguments

if args.count < 2 {
    print("Usage: screen-glow.swift [add|remove]")
    exit(1)
}

let command = args[1]

switch command {
case "add":
    ScreenGlowManager.addGlow()
case "remove":
    ScreenGlowManager.removeGlow()
default:
    print("Unknown command: \(command)")
    print("Usage: screen-glow.swift [add|remove]")
    exit(1)
}

