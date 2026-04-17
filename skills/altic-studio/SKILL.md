---
name: altic-studio
description: macOS automation skill for AppleScript actions and Chrome browser control via MCP CDP tools.
license: Apache-2.0
---

# Altic Studio

`altic-studio` provides two automation modes:

1. AppleScript mode for macOS apps and system actions
2. MCP CDP mode for Google Chrome browser control

## Mode A: AppleScript (macOS apps)

- Always execute AppleScript through Bash with `osascript`.
- Always run from workspace root as the working directory.
- Quote script paths and arguments.
- Prefer direct script invocation; do not route through Python wrappers unless explicitly requested.

Command templates:

```bash
osascript "skills/altic-studio/scripts/<script>.applescript" [arg1] [arg2] ...
```

### AppleScript Capabilities

The full Altic automation surface is exposed as scripts under `skills/altic-studio/scripts`:

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
- `capture-screenshot.applescript` - args: `[output_path] [full|interactive|window]`

## Mode B: Chrome Browser Control (MCP CDP)

Use MCP tools for deterministic Chrome automation:

- `chrome_open_session`
- `chrome_navigate`
- `chrome_wait_for`
- `chrome_click`
- `chrome_type`
- `chrome_extract`
- `chrome_screenshot`
- `chrome_close_session`
- `chrome_list_sessions`

Execution pattern:

1. Open a Chrome session.
2. Navigate and wait for stable selectors.
3. Interact with click and type actions.
4. Verify state with extraction.
5. Capture screenshots on checkpoints or failures.
6. Close session.

## Operational Rules

- Validate date/time format before running reminder/calendar scripts.
- If contact lookup returns multiple options, ask for disambiguation before sending.
- If script output indicates permission issues, report exact permissions to enable.
- Prefer explicit CSS selectors and call `chrome_wait_for` before click/type on dynamic pages.
- After mutating actions in Chrome, verify expected page state with `chrome_extract`.

## Permissions Checklist

- Contacts access
- Calendars access
- Reminders access
- Automation permission for app control
- Accessibility permission for some system controls
- Screen Recording permission for screenshots
- Safari setting: Allow JavaScript from Apple Events
- Google Chrome installed for CDP tools
- Full Disk Access for reading Messages database
