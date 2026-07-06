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
4. MCP clipboard mode for text, file, and image pasteboard operations
5. MCP window/workspace mode for arranging macOS apps and windows

It also includes Swift utility scripts for active-display screenshots, clipboard
file/image operations, and window/workspace management on macOS.

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
- `messages-manager.applescript` - args: `<list_chats|send_file> ...`
- `read-recent-messages.applescript` - args: `<phone_or_handle> <count>`
- `fetch-all-contacts.applescript` - args: none
- `contacts-manager.applescript` - args: `<get|create|update> ...`
- `set-reminder.applescript` - args: `<text> <YYYY-MM-DD HH:MM> [list_name]`
- `reminders-manager.applescript` - args: `<list_lists|list|search|complete|delete|reschedule|update|show> ...`
- `create-note.applescript` - args: `<title> <body> [folder]`
- `search-for-note.applescript` - args: `<query> [max_results]`
- `notes-manager.applescript` - args: `<list_folders|list|get|append|update|delete|move> ...`
- `create-calendar-event.applescript` - args: `<title> <YYYY-MM-DD HH:MM> <duration_minutes> [calendar]`
- `list-all-calendar-events-for-day.applescript` - args: `<YYYY-MM-DD>`
- `calendar-manager.applescript` - args: `<list_calendars|list|search|update|delete|availability|create_recurring> ...`
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
- `clipboard.swift` - subcommands: `get-files`, `set-files <paths...>`, `save-image <output_path>`, `set-image <image_path>`
- `window-manager.swift` - subcommands: `get_frontmost_app`, `list_windows`, `focus_window`, `move_window`, `resize_window`, `center_window`, `tile_windows`, `minimize`, `hide_app`, `quit_app`

Swift command template (for active-display screenshots):

```bash
swift "skills/altic-studio/scripts/capture-active-screen.swift" "/tmp/active-screen.png"
```

Swift command template (for window management):

```bash
swift "skills/altic-studio/scripts/window-manager.swift" "list_windows" '{"include_minimized":false}'
```

## Mode B: Reminders, Calendar, And Notes (MCP)

Use MCP tools for structured Messages, Contacts, Reminders, Calendar, and Notes workflows. These
newer tools return JSON envelopes with `ok`, `action`, `data`, and `error`.
Delete tools default to `dry_run=true`; only delete after explicit user
confirmation.

Available Messages tools:

- `list_chats` - args: `[limit]`
- `send_file_message` - args: `<recipient> <path> [message] [recipient_type]`

Available Contacts tools:

- `get_contact` - args: `<identifier>`
- `create_contact` - args: `<first_name> <last_name> [organization] [phone] [email] [note]`
- `update_contact` - args: `<identifier> [first_name] [last_name] [organization] [phone] [email] [note]`

Available Reminders tools:

- `list_reminder_lists` - args: none
- `list_reminders` - args: `[list_name] [include_completed]`
- `search_reminders` - args: `<query> [list_name] [include_completed]`
- `complete_reminder` - args: `<identifier> [list_name]`
- `delete_reminder` - args: `<identifier> [list_name] [dry_run]`
- `reschedule_reminder` - args: `<identifier> <YYYY-MM-DD HH:MM> [list_name]`
- `update_reminder` - args: `<identifier> [list_name] [name] [body] [datetime] [completed] [priority] [flagged]`
- `show_reminder` - args: `<identifier> [list_name]`

Available Calendar tools:

- `list_calendars` - args: none
- `list_calendar_events` - args: `<start_date> <end_date> [calendar_name]`
- `search_calendar_events` - args: `<query> [start_date] [end_date] [calendar_name]`
- `update_calendar_event` - args: `<identifier> [title] [start_datetime] [duration_minutes] [calendar_name] [location] [notes_text]`
- `delete_calendar_event` - args: `<identifier> [start_date] [end_date] [calendar_name] [dry_run]`
- `check_calendar_availability` - args: `<start_datetime> <duration_minutes> [calendar_name]`
- `create_recurring_event` - args: `<title> <start_datetime> <duration_minutes> <frequency> [interval] [count] [until_date] [calendar_name] [location] [notes_text]`

Available Notes tools:

- `list_note_folders` - args: none
- `list_notes` - args: `[folder] [max_results]`
- `get_note` - args: `<identifier>`
- `append_to_note` - args: `<identifier> <body>`
- `update_note` - args: `<identifier> <body>`
- `delete_note` - args: `<identifier> [dry_run]`
- `move_note` - args: `<identifier> <folder>`

Workflow rules:

- Call list/search tools before mutating when the target is ambiguous.
- Treat `identifier` as either an app-provided id or an exact title/name match.
- If a mutation returns multiple matches, ask the user to disambiguate.
- Keep destructive actions in dry-run mode until the user explicitly confirms.
- Validate dates before calling tools: dates use `YYYY-MM-DD`, date-times use
  `YYYY-MM-DD HH:MM`.
- For `send_file_message`, prefer `recipient_type="chat"` after `list_chats`
  when continuing an existing group thread; use `recipient_type="handle"` for a
  direct phone number or email handle.

## Mode C: Chrome Browser Control (MCP CDP)

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

## Mode D: File Finder and File Operations (MCP)

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

## Mode E: Clipboard Operations (MCP)

Use MCP clipboard tools instead of shell commands when the user asks to inspect,
copy, paste, clear, or save clipboard contents. These tools return JSON for text
and file operations, `Error: ...` strings for failures, and image content for
saved clipboard images.

Available tools:

- `get_clipboard_text` - args: `[max_chars]`
- `set_clipboard_text` - args: `<text>`
- `clear_clipboard` - args: none
- `get_clipboard_files` - args: none
- `set_clipboard_files` - args: `<paths>`
- `save_clipboard_image` - args: `[output_path]`
- `set_clipboard_image` - args: `<path>`

Clipboard workflow rules:

- Ask before overwriting clipboard contents unless the user explicitly asks to
  copy, set, clear, or replace the clipboard.
- Use `get_clipboard_text` first when the user asks what text is currently copied.
- Use `get_clipboard_files` when the user says they copied files in Finder or
  wants to paste copied files somewhere else.
- Use `save_clipboard_image` when the user wants to inspect, store, or transform
  an image currently on the clipboard.
- Use `set_clipboard_files` with existing paths only; resolve ambiguous file
  names with `find_files` before changing the clipboard.
- Use `set_clipboard_image` only for existing image files.

## Mode F: Window and Workspace Operations (MCP)

Use MCP window tools when the user asks to arrange the workspace, focus an app or
window, tile apps side by side, resize windows, minimize windows, hide apps, quit
apps, or inspect the frontmost app. These tools return JSON for successful
operations and `Error: ...` strings for failures.

Available tools:

- `get_frontmost_app` - args: none
- `list_windows` - args: `[app_name] [include_minimized]`
- `focus_window` - args: `[app_name] [window_id] [window_index]`
- `move_window` - args: `<x> <y> [app_name] [window_id] [window_index] [display_index]`
- `resize_window` - args: `<width> <height> [app_name] [window_id] [window_index] [display_index]`
- `center_window` - args: `[app_name] [window_id] [window_index] [display_index] [width] [height]`
- `tile_windows` - args: `[layout=columns|rows|grid] [app_names] [display_index] [padding]`
- `minimize` - args: `[app_name] [window_id] [window_index]`
- `hide_app` - args: `<app_name>`
- `quit_app` - args: `<app_name>`

Window workflow rules:

- Call `list_windows` before moving, resizing, minimizing, or focusing when the
  target app has multiple windows or the target is ambiguous.
- Prefer `app_name` for user-facing workflows and `window_id` for precise
  follow-up operations after `list_windows`.
- Use `display_index` when arranging windows on a specific display; otherwise
  tools choose the display containing the target window.
- Use `tile_windows` with explicit `app_names` when preparing a multi-app task.
- Do not call `quit_app` unless the user explicitly asked to close or quit that
  app.
- If a window mutation fails with an Accessibility error, tell the user to grant
  Accessibility permission to the host app running the MCP server.

## Operational Rules

- Validate date/time format before running reminder/calendar scripts.
- If contact lookup returns multiple options, ask for disambiguation before sending.
- If script output indicates permission issues, report exact permissions to enable.
- Prefer explicit CSS selectors and call `chrome_wait_for` before click/type on dynamic pages.
- After mutating actions in Chrome, verify expected page state with `chrome_extract`.
- For file mutations, verify the target with `get_file_info` or `list_directory`
  after the operation when the user needs confirmation.
- For clipboard mutations, verify with `get_clipboard_text`,
  `get_clipboard_files`, or `save_clipboard_image` when the user needs
  confirmation.
- For window mutations, verify with `list_windows` when the user needs
  confirmation.

## Permissions Checklist

- Contacts access
- Calendars access
- Reminders access
- Automation permission for app control
- Accessibility permission for system controls and window management
- Screen Recording permission for screenshots and improved window discovery
- Safari setting: Allow JavaScript from Apple Events
- Google Chrome installed for CDP tools
- Full Disk Access for reading Messages database
- Automation permission for Finder when revealing, trashing, or reading selection
