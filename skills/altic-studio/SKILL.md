---
name: altic-studio
description: macOS automation skill that runs local AppleScript files through osascript using the Bash tool.
license: Apache-2.0
---

# Altic Studio

`altic-studio` runs macOS automations by executing local scripts directly.

This skill does not rely on MCP tool bindings at runtime.
It executes scripts with `osascript` via the Bash tool.

## Required Execution Mode

- Always execute AppleScript through Bash with `osascript`.
- Always run from workspace root as the working directory.
- Quote script paths and arguments.
- Prefer direct script invocation; do not route through Python wrappers unless explicitly requested.

Command templates:

```bash
osascript "skills/altic_studio/scripts/<script>.applescript" [arg1] [arg2] ...
```

## Capabilities

The full Altic automation surface is exposed as scripts under `skills/altic_studio/scripts`:

- `open-application.applescript` - args: `<app_name>`
- `send-message.applescript` - args: `<phone_or_handle> <message>`
- `read-recent-messages.applescript` - args: `<phone_or_handle> <count>`
- `fetch-all-contacts.applescript` - args: none
- `set-reminder.applescript` - args: `<text> <YYYY-MM-DD HH:MM> [list_name]`
- `create-note.applescript` - args: `<title> <body> [folder]`
- `search-for-note.applescript` - args: `<query> [max_results]`
- `create-calendar-event.applescript` - args: `<title> <YYYY-MM-DD HH:MM> <duration_minutes> [calendar]`
- `list-all-calendar-events-for-day.applescript` - args: `<YYYY-MM-DD>`
- `open-safari-tab.applescript` - args: `[url]`
- `close-safari-tab.applescript` - args: `[tab_index|-1]`
- `get-safari-tabs.applescript` - args: none
- `switch-safari-tab.applescript` - args: `<tab_index>`
- `run-safari-javascript.applescript` - args: `<javascript_code>`
- `navigate-safari.applescript` - args: `<url>`
- `reload-safari-page.applescript` - args: none
- `safari-go-back.applescript` - args: none
- `safari-go-forward.applescript` - args: none
- `open-safari-window.applescript` - args: `[url]`
- `close-safari-window.applescript` - args: none
- `get-safari-page-info.applescript` - args: none
- `decrease-brightness.applescript` - args: `[amount_0_to_1]`
- `increase-brightness.applescript` - args: `[amount_0_to_1]`
- `turn-up-volume.applescript` - args: `[amount_0_to_100]`
- `turn-down-volume.applescript` - args: `[amount_0_to_100]`

## Operational Rules

- Validate date/time format before running reminder/calendar scripts.
- If contact lookup returns multiple options, ask for disambiguation before sending.
- If script output indicates permission issues, report exact permissions to enable.

## Permissions Checklist

- Contacts access
- Calendars access
- Reminders access
- Automation permission for app control
- Accessibility permission for some system controls
- Safari setting: Allow JavaScript from Apple Events
- Full Disk Access for reading Messages database
