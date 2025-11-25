# Altic MCP

An MCP server that gives Claude hands-on control of your Mac, what Siri should've been

## Features

20+ tools for macOS automation:

- 📱 **Messages & Contacts** - Send/read iMessages, search contacts
- 📝 **Notes & Reminders** - Create and search notes, set reminders
- 📅 **Calendar** - Create and view events
- 🌐 **Safari** - Control tabs, navigate, execute JavaScript
- 🖥️ **System** - Open apps, adjust brightness/volume, visual effects

## Requirements

- macOS 10.13+
- Python 3.13+
- [UV package manager](https://docs.astral.sh/uv/getting-started/installation/)

## Quick Start

Install UV if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup with Claude Desktop

**1. Edit `~/.config/claude/claude_desktop_config.json` to include:**

```json
{
  "mcpServers": {
    "altic-mcp": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "git+https://github.com/altic-dev/altic-mcp.git",
        "altic-mcp"
      ]
    }
  }
}
```

**2. Restart Claude Desktop** (Command + Q, then reopen)

**3. Look for the 🔨 hammer icon** in the chat interface to see available tools

### Setup with Zed

**1. Edit `~/.config/zed/settings.json` to include:**

```json
{
  "context-servers": {
    "altic-mcp": {
      "source": "custom",
      "command": "uv",
      "args": [
        "tool",
        "run",
        "--from",
        "git+https://github.com/altic-dev/altic-mcp.git",
        "altic-mcp"
      ]
    }
  }
}
```

**2. Run the Zed command: `agent: open settings`**

**3. Under "Model Context Protocol (MCP) Servers", ensure "altic-mcp" is enabled. The number of registered tools will be displayed.**

## Permissions Required

### System Preferences → Privacy & Security:

- ✅ **Contacts** - For search_contacts
- ✅ **Calendars** - For calendar events
- ✅ **Reminders** - For creating reminders
- ✅ **Automation** - Allow Claude to control apps (Messages, Notes, Safari)
- ✅ **Accessibility** - For screen glow and system controls

### Safari Settings:

Safari → Develop → **Allow JavaScript from Apple Events** ✅ (Required for Safari tools)

_Note: If "Develop" menu is not visible, enable it in Safari → Settings → Advanced → Show Develop menu_

macOS will prompt for permissions when first used. Grant them to enable full functionality.
