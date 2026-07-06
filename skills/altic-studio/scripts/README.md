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
osascript "skills/altic-studio/scripts/messages-manager.applescript" list_chats 25
osascript "skills/altic-studio/scripts/messages-manager.applescript" send_file "+15551234567" "/tmp/report.pdf" "See attached" handle
osascript "skills/altic-studio/scripts/contacts-manager.applescript" get "Ada Lovelace"
osascript "skills/altic-studio/scripts/contacts-manager.applescript" create "Ada" "Lovelace" "Analytical Engines" "+15551234567" "ada@example.com" "Created by Altic"
osascript "skills/altic-studio/scripts/create-note.applescript" "Todo" "Buy milk" "Personal"
osascript "skills/altic-studio/scripts/create-calendar-event.applescript" "Team Sync" "2026-03-20 10:00" "30" "Work"
osascript "skills/altic-studio/scripts/calendar-manager.applescript" create_recurring "Standup" "2026-03-20 10:00" "30" weekly "1" "10" "" "Work" "Zoom" "Team sync"
osascript "skills/altic-studio/scripts/navigate-safari.applescript" "https://example.com"
osascript "skills/altic-studio/scripts/capture-screenshot.applescript" "/tmp/screen.png" "full"
swift "skills/altic-studio/scripts/capture-active-screen.swift" "/tmp/active-screen.png"
swift "skills/altic-studio/scripts/clipboard.swift" get-files
swift "skills/altic-studio/scripts/clipboard.swift" set-files "/Users/example/Desktop/report.pdf"
swift "skills/altic-studio/scripts/clipboard.swift" save-image "/tmp/clipboard.png"
swift "skills/altic-studio/scripts/clipboard.swift" set-image "/tmp/clipboard.png"
```
