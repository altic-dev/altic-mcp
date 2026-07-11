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

## Skill Setup (Any Agent)

Install `altic-studio` directly from this repo with the Skills CLI:

```bash
# Preview available skills in this repo
npx skills add altic-dev/altic-mcp --list

# Install skill with interactive mode 
npx skills add altic-dev/altic-mcp 

```

Restart your coding agent after installation.

## Requirements

- macOS 10.13+
- [UV package manager](https://docs.astral.sh/uv/getting-started/installation/) (auto-installed by the bash installer if missing)

> **Python note:** altic-mcp requires Python 3.13+ internally, but `uvx` manages this automatically — you do **not** need to install Python yourself when using the uvx or bash installer options below.

## How to Install

### Install in Claude Desktop

altic-mcp offers multiple installation methods for Claude Desktop.

> **📋 Update & Uninstall Information:** Options 1 and 2 have automatic updates. See [Updating & Uninstalling](#updating--uninstalling-altic-mcp) below for details.

**Option 1: Add to `claude_desktop_config` manually ⭐ Auto-Updates (Requires UV)**

Add this entry to your Claude Desktop config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "altic-mcp": {
      "command": "uvx",
      "args": ["--refresh", "--from", "git+https://github.com/altic-dev/altic-mcp.git", "altic-mcp"]
    }
  }
}
```

Restart Claude if running.

**✅ Auto-Updates:** Yes — `uvx --refresh` re-fetches the latest version from GitHub each time Claude starts
**🔄 Manual Update:** `uv cache clean altic-mcp` then restart Claude
**🗑️ Uninstall:** Remove the `"altic-mcp"` entry from your `claude_desktop_config.json`

> **Performance tip:** `--refresh` ensures you always run the latest version but adds a few seconds to startup. Remove `--refresh` for faster startup (update manually with `uv cache clean altic-mcp`).

**Option 2: Using bash script installer ⭐ Auto-Updates (Installs UV if needed)**

```bash
curl -fsSL https://raw.githubusercontent.com/altic-dev/altic-mcp/refs/heads/main/install.sh | bash
```

This script checks for UV (installs it if missing), backs up your existing Claude config, and adds the `altic-mcp` server entry automatically.

**✅ Auto-Updates:** Yes — same `uvx --refresh` mechanism as Option 1
**🔄 Manual Update:** Re-run the bash installer command above, or `uv cache clean altic-mcp`
**🗑️ Uninstall:** Remove the `"altic-mcp"` entry from your `claude_desktop_config.json`

### Install in Other Clients

altic-mcp works with any MCP-compatible client. The standard JSON configuration is:

```json
{
  "mcpServers": {
    "altic-mcp": {
      "command": "uvx",
      "args": ["--refresh", "--from", "git+https://github.com/altic-dev/altic-mcp.git", "altic-mcp"]
    }
  }
}
```

Add this to your client's MCP configuration file at the locations below:

**Cursor**

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en-US/install-mcp?name=altic-mcp&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyItLXJlZnJlc2giLCItLWZyb20iLCJnaXQraHR0cHM6Ly9naXRodWIuY29tL2FsdGljLWRldi9hbHRpYy1tY3AuZ2l0IiwiYWx0aWMtbWNwIl19)

Or add manually to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` in your project folder (project-specific).

See [Cursor MCP docs](https://docs.cursor.com/context/model-context-protocol) for more info.

**Windsurf**

Add to `~/.codeium/windsurf/mcp_config.json`. See [Windsurf MCP docs](https://docs.windsurf.com/windsurf/cascade/mcp) for more info.

**VS Code / GitHub Copilot**

Add to `.vscode/mcp.json` in your project or VS Code User Settings (JSON). Make sure MCP is enabled under Chat > MCP. Works in Agent mode.

See [VS Code MCP docs](https://code.visualstudio.com/docs/copilot/chat/mcp-servers) for more info.

**Cline**

Configure through the Cline extension settings in VS Code. Open the Cline sidebar, click the MCP Servers icon, and add the JSON configuration above. See [Cline MCP docs](https://docs.cline.bot/mcp/configuring-mcp-servers) for more info.

**Roo Code**

Add to your Roo Code MCP configuration file. See [Roo Code MCP docs](https://docs.roocode.com/features/mcp/using-mcp-in-roo) for more info.

**Claude Code**

```bash
claude mcp add --scope user altic-mcp -- uvx --refresh --from git+https://github.com/altic-dev/altic-mcp.git altic-mcp
```

Remove `--scope user` to install for the current project only. See [Claude Code MCP docs](https://docs.anthropic.com/en/docs/claude-code/mcp) for more info.

**Trae**

Use the "Add manually" feature and paste the JSON configuration above. See [Trae MCP docs](https://docs.trae.ai/ide/model-context-protocol?_lang=en) for more info.

**Kiro**

Navigate to `Kiro` > `MCP Servers`, click `+ Add`, and paste the JSON configuration above. See [Kiro MCP docs](https://kiro.dev/docs/mcp/configuration/) for more info.

**Codex (OpenAI)**

Codex uses TOML configuration. Run this command to add altic-mcp:

```bash
codex mcp add altic-mcp -- uvx --refresh --from git+https://github.com/altic-dev/altic-mcp.git altic-mcp
```

Or manually add to `~/.codex/config.toml`:

```toml
[mcp_servers.altic-mcp]
command = "uvx"
args = ["--refresh", "--from", "git+https://github.com/altic-dev/altic-mcp.git", "altic-mcp"]
```

See [Codex MCP docs](https://developers.openai.com/codex/mcp/) for more info.

**JetBrains (AI Assistant)**

In JetBrains IDEs, go to **Settings → Tools → AI Assistant → Model Context Protocol (MCP)**, click `+` Add, select **As JSON**, and paste the JSON configuration above. See [JetBrains MCP docs](https://www.jetbrains.com/help/ai-assistant/configure-an-mcp-server.html) for more info.

**Gemini CLI**

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "altic-mcp": {
      "command": "uvx",
      "args": ["--refresh", "--from", "git+https://github.com/altic-dev/altic-mcp.git", "altic-mcp"]
    }
  }
}
```

See [Gemini CLI docs](https://github.com/google-gemini/gemini-cli) for more info.

**OpenCode**

Add to your `opencode.json` (project-level) or `~/.config/opencode/opencode.json` (global):

```json
{
  "mcp": {
    "altic-mcp": {
      "type": "local",
      "command": ["uvx", "--refresh", "--from", "git+https://github.com/altic-dev/altic-mcp.git", "altic-mcp"],
      "enabled": true
    }
  }
}
```

See [OpenCode MCP docs](https://opencode.ai/docs/mcp-servers) for more info.

## Updating & Uninstalling Altic MCP

### Automatic Updates (Options 1 & 2)

Both the manual config (Option 1) and bash installer (Option 2) use `uvx --refresh`, which automatically re-fetches the latest version from GitHub whenever you restart Claude. No manual intervention needed.

### Manual Updates

If you removed `--refresh` for faster startup, force an update with:

```bash
uv cache clean altic-mcp
```

Then restart Claude Desktop.

### Uninstalling Altic MCP

#### Manual Uninstallation

1. **Locate your Claude Desktop config file:**
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

2. **Edit the config file:**
   - Open the file in a text editor
   - Find and remove the `"altic-mcp"` entry from the `"mcpServers"` section
   - Save the file

**Example — remove this section:**

```json
"altic-mcp": {
  "command": "uvx",
  "args": ["--refresh", "--from", "git+https://github.com/altic-dev/altic-mcp.git", "altic-mcp"]
}
```

Close and restart Claude Desktop to complete the removal.

#### Troubleshooting

**If Claude won't start after editing the config:**
- Check that your JSON is valid (no trailing commas, matched braces)
- Restore from the backup created by the bash installer (`.bak.*` file next to your config)
- Re-run the bash installer to regenerate a valid config

## Local Development

For contributors who want to run altic-mcp from a local checkout:

```bash
# Install UV if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/altic-dev/altic-mcp.git
cd altic-mcp
uv sync

# Run the server directly
uv run server.py

# Or build and run via the installed entry point
uv build
uvx --from dist/altic_mcp-0.1.0-py3-none-any.whl altic-mcp
```

**❌ Auto-Updates:** No — requires manual `git pull` to update
**🔄 Manual Update:** `cd altic-mcp && git pull && uv sync`
**🗑️ Uninstall:** Remove the cloned directory and the MCP server entry from your client config

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

