# altic-studio script runner reference

Run all scripts through Bash using `osascript`.
Run Swift utilities through Bash using `swift`.

Base pattern:

```bash
osascript "skills/altic-studio/scripts/<script>.applescript" [args...]
```

Examples:

```bash
osascript "skills/altic-studio/scripts/open-application.applescript" "Safari"
osascript "skills/altic-studio/scripts/send-message.applescript" "+15551234567" "On my way"
osascript "skills/altic-studio/scripts/create-note.applescript" "Todo" "Buy milk" "Personal"
osascript "skills/altic-studio/scripts/create-calendar-event.applescript" "Team Sync" "2026-03-20 10:00" "30" "Work"
osascript "skills/altic-studio/scripts/navigate-safari.applescript" "https://example.com"
osascript "skills/altic-studio/scripts/capture-screenshot.applescript" "/tmp/screen.png" "full"
swift "skills/altic-studio/scripts/capture-active-screen.swift" "/tmp/active-screen.png"
swift "skills/altic-studio/scripts/clipboard.swift" get-files
swift "skills/altic-studio/scripts/clipboard.swift" set-files "/Users/example/Desktop/report.pdf"
swift "skills/altic-studio/scripts/clipboard.swift" save-image "/tmp/clipboard.png"
swift "skills/altic-studio/scripts/clipboard.swift" set-image "/tmp/clipboard.png"
```
