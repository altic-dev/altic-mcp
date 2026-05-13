---
name: altic-studio
description: macOS automation skill for AppleScript actions and Chrome browser control via MCP CDP tools.
license: Apache-2.0
---

# Altic Studio

`altic-studio` provides two automation modes:

1. AppleScript mode for macOS apps and system actions
2. MCP CDP mode for Google Chrome browser control
3. MCP file mode for safe Finder and filesystem operations

It also includes a Swift utility script for active-display screenshots on macOS.

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
- `capture-active-screen.swift` - args: `<output_path>` (captures full display containing frontmost app)

Swift command template (for active-display screenshots):

```bash
swift "skills/altic-studio/scripts/capture-active-screen.swift" "/tmp/active-screen.png"
```

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
- `capture_active_screen`

Execution pattern:

1. Open a Chrome session.
2. Navigate and wait for stable selectors.
3. Interact with click and type actions.
4. Verify state with extraction.
5. Capture screenshots on checkpoints or failures.
6. Close session.

## Mode C: File Finder and File Operations (MCP)

Use MCP file tools instead of shell commands when the user asks to find, inspect,
copy, move, rename, reveal, or trash files. These tools return JSON for
successful lookups and operations, and `Error: ...` strings for failures.

Available tools:

- `find_files` - args: `<query> [root] [max_results] [include_hidden] [kind]`
- `list_directory` - args: `<path> [include_hidden] [max_results]`
- `get_file_info` - args: `<path>`
- `copy_file` - args: `<source> <destination> [overwrite] [dry_run]`
- `copy_directory` - args: `<source> <destination> [overwrite] [dry_run]`
- `move_file` - args: `<source> <destination> [overwrite] [dry_run]`
- `rename_file` - args: `<path> <new_name> [overwrite] [dry_run]`
- `trash_file` - args: `<path> [dry_run]`
- `reveal_in_finder` - args: `<path>`
- `get_finder_selection` - args: none

File workflow rules:

- If the user refers to selected files, the current Finder window, or "this file",
  call `get_finder_selection` first.
- For ambiguous file names, call `find_files`, then `get_file_info`; ask for
  disambiguation when multiple plausible matches remain.
- Prefer `dry_run=true` before `copy_file`, `copy_directory`, `move_file`,
  `rename_file`, or `trash_file` when the target or destination is ambiguous.
- Do not overwrite unless the user explicitly asks for replacement; default
  `overwrite=false`.
- Use `trash_file`, not permanent deletion.
- Use `reveal_in_finder` after file operations when the user wants to see the
  result in Finder.

## Operational Rules

- Validate date/time format before running reminder/calendar scripts.
- If contact lookup returns multiple options, ask for disambiguation before sending.
- If script output indicates permission issues, report exact permissions to enable.
- Prefer explicit CSS selectors and call `chrome_wait_for` before click/type on dynamic pages.
- After mutating actions in Chrome, verify expected page state with `chrome_extract`.
- For file mutations, verify the target with `get_file_info` or `list_directory`
  after the operation when the user needs confirmation.

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
- Automation permission for Finder when revealing, trashing, or reading selection
