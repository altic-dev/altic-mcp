# altic-studio script runner reference

Run all scripts through Bash using `osascript`.

Base pattern:

```bash
osascript "skills/altic_studio/scripts/<script>.applescript" [args...]
```

Examples:

```bash
osascript "skills/altic_studio/scripts/open-application.applescript" "Safari"
osascript "skills/altic_studio/scripts/send-message.applescript" "+15551234567" "On my way"
osascript "skills/altic_studio/scripts/create-note.applescript" "Todo" "Buy milk" "Personal"
osascript "skills/altic_studio/scripts/create-calendar-event.applescript" "Team Sync" "2026-03-20 10:00" "30" "Work"
osascript "skills/altic_studio/scripts/navigate-safari.applescript" "https://example.com"
```
