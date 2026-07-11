#!/usr/bin/env bash
#
# altic-mcp installer — configures Claude Desktop to use altic-mcp via uvx.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/altic-dev/altic-mcp/refs/heads/main/install.sh | bash
#
# What it does:
#   1. Verifies macOS
#   2. Checks for / installs UV package manager
#   3. Backs up the existing Claude Desktop config
#   4. Adds or updates the altic-mcp MCP server entry (uvx-based, auto-updates)
#   5. Prints next steps
#
set -euo pipefail

REPO_URL="git+https://github.com/altic-dev/altic-mcp.git"
SERVER_NAME="altic-mcp"
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

# ─── Helpers ──────────────────────────────────────────────────────────────

info()  { printf "\033[1;34m==>\033[0m %s\n" "$*"; }
ok()    { printf "\033[1;32m  ✓\033[0m %s\n" "$*"; }
warn()  { printf "\033[1;33m  !\033[0m %s\n" "$*"; }
fail()  { printf "\033[1;31m  ✗\033[0m %s\n" "$*"; exit 1; }

# ─── 1. Platform check ────────────────────────────────────────────────────

if [[ "$(uname -s)" != "Darwin" ]]; then
    fail "altic-mcp requires macOS. Aborting."
fi
ok "Running on macOS"

# ─── 2. UV check / install ────────────────────────────────────────────────

if command -v uv &>/dev/null; then
    ok "UV found: $(uv --version)"
else
    info "Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Source the env so uv is on PATH for this script
    export PATH="$HOME/.local/bin:$PATH"
    if command -v uv &>/dev/null; then
        ok "UV installed: $(uv --version)"
    else
        fail "UV installation failed. Please install manually: https://docs.astral.sh/uv/getting-started/installation/"
    fi
fi

# ─── 3. Claude Desktop config ─────────────────────────────────────────────

if [[ ! -d "$CLAUDE_CONFIG_DIR" ]]; then
    warn "Claude Desktop config directory not found at:\n    $CLAUDE_CONFIG_DIR"
    warn "Install Claude Desktop first, then re-run this installer."
    warn "Alternatively, add the config block manually (see README.md)."
    fail "Claude Desktop not detected."
fi

mkdir -p "$CLAUDE_CONFIG_DIR"

# Back up existing config
if [[ -f "$CLAUDE_CONFIG_FILE" ]]; then
    BACKUP="$CLAUDE_CONFIG_FILE.bak.$(date +%Y%m%d%H%M%S)"
    cp "$CLAUDE_CONFIG_FILE" "$BACKUP"
    ok "Backed up existing config to:\n    $BACKUP"
fi

# ─── 4. Write / merge config ──────────────────────────────────────────────

info "Configuring $SERVER_NAME in Claude Desktop..."

uv run python3 - "$CLAUDE_CONFIG_FILE" "$SERVER_NAME" "$REPO_URL" <<'PYEOF'
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
server_name = sys.argv[2]
repo_url = sys.argv[3]

# Read existing config or start fresh
if config_path.exists():
    config = json.loads(config_path.read_text())
else:
    config = {}

config.setdefault("mcpServers", {})

config["mcpServers"][server_name] = {
    "command": "uvx",
    "args": ["--refresh", "--from", repo_url, "altic-mcp"],
}

config_path.write_text(json.dumps(config, indent=2) + "\n")
print(f"  ✓ Wrote {server_name} entry to {config_path}")
PYEOF

ok "Configuration complete."

# ─── 5. Next steps ────────────────────────────────────────────────────────

echo ""
info "Installation complete!"
echo ""
echo "  Next steps:"
echo "    1. Restart Claude Desktop (Command + Q, then reopen)"
echo "    2. Look for the 🔨 hammer icon in the chat interface"
echo ""
echo "  Auto-updates:"
echo "    altic-mcp re-fetches the latest version from GitHub each time"
echo "    Claude Desktop starts (via uvx --refresh)."
echo ""
echo "  Manual update:"
echo "    Re-run this installer, or: uv cache clean altic-mcp"
echo ""
echo "  Uninstall:"
echo "    Remove the \"$SERVER_NAME\" entry from:"
echo "    $CLAUDE_CONFIG_FILE"
echo ""
