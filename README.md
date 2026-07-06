# Altic MCP

## Features

50+ tools for macOS automation:
- 📱 **Messages & Contacts** - Send/read iMessages, list chats, send file attachments, search/get/create/update contacts
- 📝 **Notes & Reminders** - Create, list, search, update, show, move, complete, and delete notes/reminders
- 📅 **Calendar** - Create, list, search, update, delete, check availability, and create recurring events
- 🗂️ **Files & Finder** - Find, inspect, copy, move, rename, reveal, and trash files safely
- 📋 **Clipboard** - Read/write text, copy file paths for Finder paste, and save/set clipboard images
- 🪟 **Window & Workspace** - List/focus apps and windows, move/resize/center/tile windows, minimize windows, hide apps, and quit apps
- 🌐 **Safari** - Control tabs, navigate, execute JavaScript
- 🌍 **Chrome (CDP)** - Open sessions, navigate, click/type, extract data, screenshots
- 📸 **Screen Capture** - Capture the active display and share image output with the model
- 🖥️ **System** - Open apps, adjust brightness/volume, visual effects

## Available Skills

This repo currently includes one shareable skill:

- `altic-studio` (`skills/altic-studio/`)
  - Runs local AppleScript automations via `osascript` through the Bash tool
  - Covers Messages, Contacts, Notes, Reminders, Calendar, Safari, window management, system controls, screenshots, and Chrome CDP browser control
  - Main skill manifest: `skills/altic-studio/SKILL.md`

### Key Scripts In `altic-studio`

- Messaging: `send-message.applescript`, `read-recent-messages.applescript`, `messages-manager.applescript`
- Contacts: `fetch-all-contacts.applescript`, `contacts-manager.applescript`
- Notes/Reminders: `create-note.applescript`, `search-for-note.applescript`, `set-reminder.applescript`, `notes-manager.applescript`, `reminders-manager.applescript`
- Calendar: `create-calendar-event.applescript`, `list-all-calendar-events-for-day.applescript`, `calendar-manager.applescript`
- Safari: open/close/switch/navigate/reload/history/page-info scripts
- System: `open-application.applescript`, brightness + volume scripts
- Screenshot: `capture-screenshot.applescript`
- Files/Finder MCP: `find_files`, `list_directory`, `get_file_info`, `copy_file`, `copy_directory`, `move_file`, `rename_file`, `trash_file`, `reveal_in_finder`, `get_finder_selection`
- Clipboard MCP: `get_clipboard_text`, `set_clipboard_text`, `clear_clipboard`, `get_clipboard_files`, `set_clipboard_files`, `save_clipboard_image`, `set_clipboard_image`
- Window/Workspace MCP: `get_frontmost_app`, `list_windows`, `focus_window`, `move_window`, `resize_window`, `center_window`, `tile_windows`, `minimize`, `hide_app`, `quit_app`
- Messages MCP: `list_chats`, `send_file_message`
- Contacts MCP: `get_contact`, `create_contact`, `update_contact`
- Reminders MCP: `list_reminder_lists`, `list_reminders`, `search_reminders`, `complete_reminder`, `delete_reminder`, `reschedule_reminder`, `update_reminder`, `show_reminder`
- Calendar MCP: `list_calendars`, `list_calendar_events`, `search_calendar_events`, `update_calendar_event`, `delete_calendar_event`, `check_calendar_availability`, `create_recurring_event`
- Notes MCP: `list_note_folders`, `list_notes`, `get_note`, `append_to_note`, `update_note`, `delete_note`, `move_note`
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
- ✅ **Screen Recording** - Required for screenshot capture tools and improves window title/id discovery for list_windows on recent macOS versions

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

