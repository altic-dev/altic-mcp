# Altic MCP

## Features

30+ tools for macOS automation:
- 📱 **Messages & Contacts** - Send/read iMessages, search contacts
- 📝 **Notes & Reminders** - Create and search notes, set reminders  
- 📅 **Calendar** - Create and view events
- 🗂️ **Files & Finder** - Find, inspect, copy, move, rename, reveal, and trash files safely
- 🌐 **Safari** - Control tabs, navigate, execute JavaScript
- 🌍 **Chrome (CDP)** - Open sessions, navigate, click/type, extract data, screenshots
- 📸 **Screen Capture** - Capture the active display and share image output with the model
- 🖥️ **System** - Open apps, adjust brightness/volume, visual effects

## Available Skills

This repo currently includes one shareable skill:

- `altic-studio` (`skills/altic-studio/`)
  - Runs local AppleScript automations via `osascript` through the Bash tool
  - Covers Messages, Contacts, Notes, Reminders, Calendar, Safari, system controls, screenshots, and Chrome CDP browser control
  - Main skill manifest: `skills/altic-studio/SKILL.md`

### Key Scripts In `altic-studio`

- Messaging: `send-message.applescript`, `read-recent-messages.applescript`
- Contacts: `fetch-all-contacts.applescript`
- Notes/Reminders: `create-note.applescript`, `search-for-note.applescript`, `set-reminder.applescript`
- Calendar: `create-calendar-event.applescript`, `list-all-calendar-events-for-day.applescript`
- Safari: open/close/switch/navigate/reload/history/page-info scripts
- System: `open-application.applescript`, brightness + volume scripts
- Screenshot: `capture-screenshot.applescript`
- Files/Finder MCP: `find_files`, `list_directory`, `get_file_info`, `copy_file`, `copy_directory`, `move_file`, `rename_file`, `trash_file`, `reveal_in_finder`, `get_finder_selection`

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
- ✅ **Accessibility** - For screen glow and system controls
- ✅ **Screen Recording** - Required for screenshot capture tools

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
