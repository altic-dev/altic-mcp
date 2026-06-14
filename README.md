# Altic MCP

## Features

40+ tools for macOS automation:
- 📱 **Messages & Contacts** - Send/read iMessages, search contacts
- 📝 **Notes & Reminders** - Create and search notes, set reminders  
- 📅 **Calendar** - Create and view events
- 🗂️ **Files & Finder** - Find, inspect, copy, move, rename, reveal, and trash files safely
- 📋 **Clipboard** - Read/write text, copy file paths for Finder paste, and save/set clipboard images
- 🪟 **Window & Workspace** - List/focus apps and windows, move/resize/center/tile windows, minimize windows, hide apps, and quit apps
- 🌐 **Safari** - Control tabs, navigate, execute JavaScript
- 🌍 **Chrome (CDP)** - Open sessions, navigate, click/type, extract data, screenshots
- 📸 **Screen Capture** - Capture the active display and share image output with the model
- 🔎 **Screen Text** - Extract visible text from the active display with Vision OCR, with optional macOS 27 visual summaries
- 🖥️ **System** - Open apps, adjust brightness/volume, visual effects

## Available Skills

This repo currently includes one shareable skill:

- `altic-studio` (`skills/altic-studio/`)
  - Runs local AppleScript automations via `osascript` through the Bash tool
  - Covers Messages, Contacts, Notes, Reminders, Calendar, Safari, window management, system controls, screenshots, and Chrome CDP browser control
  - Main skill manifest: `skills/altic-studio/SKILL.md`

### Key Scripts In `altic-studio`

- Messaging: `send-message.applescript`, `read-recent-messages.applescript`
- Contacts: `fetch-all-contacts.applescript`
- Notes/Reminders: `create-note.applescript`, `search-for-note.applescript`, `set-reminder.applescript`
- Calendar: `create-calendar-event.applescript`, `list-all-calendar-events-for-day.applescript`
- Safari: open/close/switch/navigate/reload/history/page-info scripts
- System: `open-application.applescript`, brightness + volume scripts
- Screenshot: `capture-screenshot.applescript`
- Screen text MCP: `extract_screen_text`
- Files/Finder MCP: `find_files`, `list_directory`, `get_file_info`, `copy_file`, `copy_directory`, `move_file`, `rename_file`, `trash_file`, `reveal_in_finder`, `get_finder_selection`
- Clipboard MCP: `get_clipboard_text`, `set_clipboard_text`, `clear_clipboard`, `get_clipboard_files`, `set_clipboard_files`, `save_clipboard_image`, `set_clipboard_image`
- Window/Workspace MCP: `get_frontmost_app`, `list_windows`, `focus_window`, `move_window`, `resize_window`, `center_window`, `tile_windows`, `minimize`, `hide_app`, `quit_app`
- Clipboard script: `clipboard.swift`
- Window script: `window-manager.swift`

## Skill Setup (Any Agent)

Install `altic-studio` directly from this repo with the Skills CLI:

```bash
# Preview available skills in this repo
npx skills add altic-dev/altic-mcp --list

# Install skill with interactive mode 
npx skills add altic-dev/altic-mcp 

```

Restart your coding agent after installation.

### Manual Symlink Setup For OpenCode (Alternative)

To make `altic-studio` available in OpenCode, symlink it into your OpenCode skills directory:

```bash
mkdir -p "$HOME/.config/opencode/skills"
ln -sfn "/Users/rohith/Documents/altic-mcp/skills/altic-studio" "$HOME/.config/opencode/skills/altic-studio"
ls "$HOME/.config/opencode/skills"
```

## Requirements

- macOS 10.13+
- Python 3.13+
- [UV package manager](https://docs.astral.sh/uv/getting-started/installation/)

## Quick Start

```bash
# Install UV if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/altic-dev/altic-mcp.git 
cd altic-mcp
uv sync

# Test locally
uv run server.py
```

## Setup with Claude Desktop

**1. Edit `~/.config/claude/claude_desktop_config.json`:**

```json
{
  "mcpServers": {
    "altic-mcp": {
      "command": "uv",
      "args": ["run", "--project", "/FULL/PATH/TO/altic-mcp", "/FULL/PATH/TO/altic-mcp/server.py"]
    }
  }
}
```

Replace `/FULL/PATH/TO/altic-mcp` with your actual path (e.g., `/Users/johndoe/Documents/altic-mcp`).

**2. Restart Claude Desktop** (Command + Q, then reopen)

**3. Look for the 🔨 hammer icon** in the chat interface to see available tools

## Permissions Required


### System Preferences → Privacy & Security:
- ✅ **Contacts** - For search_contacts
- ✅ **Calendars** - For calendar events
- ✅ **Reminders** - For creating reminders
- ✅ **Automation** - Allow Claude to control apps (Messages, Notes, Safari)
- ✅ **Finder Automation** - For Finder selection, reveal, and Trash file tools
- ✅ **Accessibility** - Required for screen glow, system controls, and window management tools such as focus_window, move_window, resize_window, center_window, tile_windows, minimize, hide_app, and quit_app
- ✅ **Screen Recording** - Required for screenshot and screen text extraction tools and improves window title/id discovery for list_windows on recent macOS versions
- ✅ **macOS 27 Apple Intelligence / Foundation Models availability** - Required only for `extract_screen_text` visual summary mode; OCR-only mode works without it

Clipboard text operations normally do not require extra permissions. Clipboard
file and image operations use macOS pasteboard APIs and may prompt for security
approval depending on the host app and OS settings.

### Safari Settings:
Safari → Develop → **Allow JavaScript from Apple Events** ✅ (Required for Safari tools)

*Note: If "Develop" menu is not visible, enable it in Safari → Settings → Advanced → Show Develop menu*

### Chrome Setup (for CDP tools):

- Install Google Chrome
- The MCP server can auto-start Chrome with `--remote-debugging-port` when opening a CDP session
- If auto-start fails, launch manually:

```bash
open -a "Google Chrome" --args --remote-debugging-port=9222
```

macOS will prompt for permissions when first used. Grant them to enable full functionality.

## Manual Smoke Tests For File Tools

Run these against temporary files before using the tools on important data:

```bash
mkdir -p /tmp/altic-file-smoke/source
echo "hello" > /tmp/altic-file-smoke/source/example.txt
```

- Use `find_files` for `example` with root `/tmp/altic-file-smoke`
- Use `copy_file` with `dry_run=true`, then repeat with `dry_run=false`
- Use `rename_file` with `dry_run=true`, then repeat with `dry_run=false`
- Use `reveal_in_finder` on the copied file
- Select a file in Finder and call `get_finder_selection`
- Use `trash_file` with `dry_run=true` before testing a real Trash move

## Manual Smoke Tests For Clipboard Tools

- Use `set_clipboard_text` with `hello`, then `get_clipboard_text`
- Use `clear_clipboard`, then `get_clipboard_text`
- Copy one or more files in Finder, then call `get_clipboard_files`
- Use `set_clipboard_files` with an existing file path, then paste in Finder
- Copy an image or screenshot, then call `save_clipboard_image`
- Use `set_clipboard_image` with an existing PNG or JPEG file, then paste into an app that accepts images

## Manual Smoke Tests For Screen Text Tools

- Open a window with visible text, then call `extract_screen_text` with `include_visual_summary=false`.
- Confirm the returned JSON includes visible text, `line_count`, `average_confidence`, and a valid `screenshot_path`.
- On macOS 27 with Foundation Models available, call `extract_screen_text` with `include_visual_summary=true` and confirm `visual_summary` is populated.
- On systems without visual summary support, confirm OCR text is still returned and `visual_error` explains the missing macOS 27/Foundation Models capability.

## Manual Smoke Tests For Window Tools

- Call `get_frontmost_app` while Finder or Safari is active.
- Call `list_windows` and confirm visible app windows include frame and display metadata.
- Open two apps, then call `tile_windows` with `layout="columns"` and their app names.
- Call `center_window` with an app name and confirm the frontmost window is centered inside the visible display area.
- Call `move_window` and `resize_window` with a test app window, then call `list_windows` to confirm the new frame.
- Call `minimize` on a test app window and confirm it minimizes.
- Call `hide_app` on a non-critical app and confirm the app is hidden.
- Call `quit_app` only on a disposable test app.
