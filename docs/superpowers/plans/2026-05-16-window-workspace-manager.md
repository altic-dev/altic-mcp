# Window Workspace Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add macOS app and window management MCP tools so agents can focus apps, inspect windows, move/resize/place windows, tile workspaces, minimize windows, hide apps, quit apps, and identify the frontmost app.

**Architecture:** Add a dedicated `tools/window.py` Python wrapper module backed by a single Swift Accessibility helper at `tools/scripts/window-manager.swift`. Python owns validation, MCP-facing names, JSON normalization, and subprocess error handling; Swift owns macOS Accessibility, display geometry, and window mutation.

**Tech Stack:** Python 3.13, FastMCP, pytest, Swift, AppKit, ApplicationServices Accessibility APIs, CoreGraphics display/window APIs.

---

## File Structure

- Create `tools/window.py`
  - Public Python functions used by `server.py`.
  - Shared `_run_window_manager(action, payload)` helper that invokes `swift tools/scripts/window-manager.swift <action> <payload-json>`.
  - Small validators for dimensions, display index, tile layout, and app/window target parameters.
  - JSON passthrough for state-returning operations and `"Error: ..."` strings for failures, matching existing modules such as `tools/files.py` and `tools/clipboard.py`.

- Create `tools/scripts/window-manager.swift`
  - One command-line helper with subcommands: `get_frontmost_app`, `list_windows`, `focus_window`, `move_window`, `resize_window`, `center_window`, `tile_windows`, `minimize`, `hide_app`, `quit_app`.
  - Uses `NSWorkspace.shared.frontmostApplication`, `NSRunningApplication`, `AXUIElement`, `AXUIElementCopyAttributeValue`, `AXUIElementSetAttributeValue`, `CGWindowListCopyWindowInfo`, and `NSScreen.screens`.
  - Returns JSON on stdout for all successful operations.
  - Writes human-readable errors to stderr and exits non-zero for failures.

- Modify `tools/__init__.py`
  - No public exports are currently declared, so this likely remains unchanged unless the file has future explicit imports when execution starts.

- Modify `server.py`
  - Import `window`.
  - Register MCP tools:
    - `get_frontmost_app`
    - `list_windows`
    - `focus_window`
    - `move_window`
    - `resize_window`
    - `center_window`
    - `tile_windows`
    - `minimize`
    - `hide_app`
    - `quit_app`
  - Keep `open_app` in `tools/app.py`; do not move it during this feature.

- Create `tests/test_window.py`
  - Unit tests monkeypatching `tools.window.subprocess.run`.
  - Tests cover argument serialization, validation, non-zero subprocess failures, JSON normalization, and all public wrappers.

- Modify `README.md`
  - Add the Window & Workspace feature to the feature list.
  - Add macOS permissions note: Accessibility is required for window focus, movement, resize, minimize, hide, and quit operations; Screen Recording improves `list_windows` titles on modern macOS.
  - Add manual smoke tests for display-aware placement.

- Modify `skills/altic-studio/SKILL.md`
  - Add the new window/workspace tools to the shareable skill so installed agents know they exist.

---

## Behavior Contract

### Targeting

All window operations target a visible, non-desktop app window using this precedence:

1. `window_id` when provided.
2. `app_name` plus `window_index`, where `window_index` is 1-based among that app's windows sorted front-to-back.
3. Frontmost app's frontmost window when no target is provided.

Use case-insensitive substring matching for `app_name` against localized app name, bundle identifier, and process name. If multiple apps match, return an error listing the matching apps so the caller can retry with a more specific name.

### Coordinate System

MCP tools accept and return AppKit/global display coordinates. `x` and `y` are top-left coordinates. `width` and `height` are window size in points. Swift converts to `AXValue` `CGPoint` and `CGSize` for `kAXPositionAttribute` and `kAXSizeAttribute`.

### Display-Aware Placement

`display_index` is optional and 1-based. When omitted, use the display with the largest intersection with the target window. If no window is available, use the main display. Safe placement uses `NSScreen.visibleFrame`, not full frame, so windows avoid the Dock and menu bar.

### Tool Return Shapes

`get_frontmost_app` returns:

```json
{
  "action": "get_frontmost_app",
  "app": {
    "name": "Safari",
    "bundle_id": "com.apple.Safari",
    "pid": 12345,
    "is_active": true
  }
}
```

`list_windows` returns:

```json
{
  "action": "list_windows",
  "windows": [
    {
      "window_id": 101,
      "app_name": "Safari",
      "bundle_id": "com.apple.Safari",
      "pid": 12345,
      "title": "Example Page",
      "x": 40,
      "y": 80,
      "width": 1200,
      "height": 800,
      "display_index": 1,
      "is_minimized": false,
      "is_frontmost_app": true
    }
  ],
  "count": 1
}
```

Mutation tools return:

```json
{
  "action": "move_window",
  "window": {
    "window_id": 101,
    "app_name": "Safari",
    "x": 100,
    "y": 120,
    "width": 1000,
    "height": 700,
    "display_index": 1
  }
}
```

---

## Task 1: Python Window Wrapper Tests

**Files:**
- Create: `tests/test_window.py`
- Create later: `tools/window.py`

- [ ] **Step 1: Write failing wrapper tests**

Create `tests/test_window.py` with these tests:

```python
import json
import subprocess
from pathlib import Path

import pytest

from tools import window


def read_json(value: str):
    assert not value.startswith("Error:"), value
    return json.loads(value)


def completed(args, stdout='{"action":"ok"}', stderr="", returncode=0):
    return subprocess.CompletedProcess(
        args=args,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_get_frontmost_app_invokes_swift_helper(monkeypatch):
    seen = {}
    payload = {
        "action": "get_frontmost_app",
        "app": {
            "name": "Finder",
            "bundle_id": "com.apple.finder",
            "pid": 42,
            "is_active": True,
        },
    }

    def fake_run(args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return completed(args, stdout=json.dumps(payload))

    monkeypatch.setattr(window.subprocess, "run", fake_run)

    assert read_json(window.get_frontmost_app()) == payload
    assert seen["args"][0] == "swift"
    assert Path(seen["args"][1]).name == "window-manager.swift"
    assert seen["args"][2] == "get_frontmost_app"
    assert json.loads(seen["args"][3]) == {}
    assert seen["kwargs"]["timeout"] == 10


def test_move_window_serializes_target_and_coordinates(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["payload"] = json.loads(args[3])
        return completed(args, stdout='{"action":"move_window"}')

    monkeypatch.setattr(window.subprocess, "run", fake_run)

    payload = read_json(
        window.move_window(
            x=100,
            y=140,
            app_name="Safari",
            window_index=2,
            display_index=1,
        )
    )

    assert payload["action"] == "move_window"
    assert seen["payload"] == {
        "app_name": "Safari",
        "window_index": 2,
        "x": 100,
        "y": 140,
        "display_index": 1,
    }


def test_resize_window_rejects_non_positive_dimensions(monkeypatch):
    def fail_run(*args, **kwargs):
        raise AssertionError("subprocess should not run for invalid dimensions")

    monkeypatch.setattr(window.subprocess, "run", fail_run)

    assert window.resize_window(width=0, height=500).startswith("Error:")
    assert window.resize_window(width=500, height=-1).startswith("Error:")


def test_center_window_serializes_size_when_provided(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["payload"] = json.loads(args[3])
        return completed(args, stdout='{"action":"center_window"}')

    monkeypatch.setattr(window.subprocess, "run", fake_run)

    read_json(
        window.center_window(
            width=900,
            height=700,
            app_name="Terminal",
            display_index=2,
        )
    )

    assert seen["payload"] == {
        "app_name": "Terminal",
        "width": 900,
        "height": 700,
        "display_index": 2,
    }


def test_tile_windows_validates_layout(monkeypatch):
    def fail_run(*args, **kwargs):
        raise AssertionError("subprocess should not run for invalid layout")

    monkeypatch.setattr(window.subprocess, "run", fail_run)

    result = window.tile_windows(layout="spiral", app_names=["Safari", "Terminal"])

    assert result.startswith("Error:")
    assert "layout must be one of" in result


def test_tile_windows_serializes_apps_and_padding(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["payload"] = json.loads(args[3])
        return completed(args, stdout='{"action":"tile_windows","count":2}')

    monkeypatch.setattr(window.subprocess, "run", fake_run)

    payload = read_json(
        window.tile_windows(
            layout="columns",
            app_names=["Safari", "Terminal"],
            display_index=1,
            padding=12,
        )
    )

    assert payload == {"action": "tile_windows", "count": 2}
    assert seen["payload"] == {
        "layout": "columns",
        "app_names": ["Safari", "Terminal"],
        "display_index": 1,
        "padding": 12,
    }


def test_focus_minimize_hide_and_quit_serialize_targets(monkeypatch):
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args[2], json.loads(args[3])))
        return completed(args, stdout=json.dumps({"action": args[2]}))

    monkeypatch.setattr(window.subprocess, "run", fake_run)

    assert read_json(window.focus_window(app_name="Safari"))["action"] == "focus_window"
    assert read_json(window.minimize(app_name="Safari", window_index=1))["action"] == "minimize"
    assert read_json(window.hide_app("Safari"))["action"] == "hide_app"
    assert read_json(window.quit_app("Safari"))["action"] == "quit_app"

    assert calls == [
        ("focus_window", {"app_name": "Safari"}),
        ("minimize", {"app_name": "Safari", "window_index": 1}),
        ("hide_app", {"app_name": "Safari"}),
        ("quit_app", {"app_name": "Safari"}),
    ]


def test_subprocess_failure_returns_error(monkeypatch):
    def fake_run(args, **kwargs):
        return completed(args, stdout="", stderr="accessibility permission denied", returncode=1)

    monkeypatch.setattr(window.subprocess, "run", fake_run)

    assert window.get_frontmost_app() == "Error: accessibility permission denied"


def test_invalid_json_from_helper_returns_error(monkeypatch):
    def fake_run(args, **kwargs):
        return completed(args, stdout="not-json")

    monkeypatch.setattr(window.subprocess, "run", fake_run)

    assert window.get_frontmost_app().startswith("Error: invalid window manager response:")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
uv run pytest tests/test_window.py -v
```

Expected: import failure or attribute failure because `tools/window.py` does not exist yet.

---

## Task 2: Python Window Wrapper Implementation

**Files:**
- Create: `tools/window.py`
- Test: `tests/test_window.py`

- [ ] **Step 1: Implement Python wrapper**

Create `tools/window.py` with:

```python
import json
import subprocess
from typing import Any

from .constants import SCRIPTS_PREFIX


VALID_TILE_LAYOUTS = {"columns", "rows", "grid"}


def _json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def _error(message: str) -> str:
    return f"Error: {message}"


def _positive_int(name: str, value: int | None) -> str | None:
    if value is not None and value <= 0:
        return f"{name} must be greater than 0"
    return None


def _target_payload(
    app_name: str = "",
    window_id: int | None = None,
    window_index: int | None = None,
    display_index: int | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if app_name.strip():
        payload["app_name"] = app_name.strip()
    if window_id is not None:
        payload["window_id"] = window_id
    if window_index is not None:
        payload["window_index"] = window_index
    if display_index is not None:
        payload["display_index"] = display_index
    return payload


def _run_window_manager(action: str, payload: dict[str, Any] | None = None) -> str:
    script_path = SCRIPTS_PREFIX / "window-manager.swift"
    args = ["swift", str(script_path), action, json.dumps(payload or {})]
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return _error(result.stderr.strip() or f"window manager action failed: {action}")

        stdout = result.stdout.strip()
        if not stdout:
            return _error(f"empty window manager response for action: {action}")

        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            return _error(f"invalid window manager response: {stdout}")
        return _json(parsed)
    except Exception as exc:
        return _error(f"failed to run window manager action {action}: {exc}")


def get_frontmost_app() -> str:
    return _run_window_manager("get_frontmost_app")


def list_windows(app_name: str = "", include_minimized: bool = False) -> str:
    payload: dict[str, Any] = {"include_minimized": include_minimized}
    if app_name.strip():
        payload["app_name"] = app_name.strip()
    return _run_window_manager("list_windows", payload)


def focus_window(
    app_name: str = "",
    window_id: int | None = None,
    window_index: int | None = None,
) -> str:
    return _run_window_manager(
        "focus_window",
        _target_payload(app_name=app_name, window_id=window_id, window_index=window_index),
    )


def move_window(
    x: int,
    y: int,
    app_name: str = "",
    window_id: int | None = None,
    window_index: int | None = None,
    display_index: int | None = None,
) -> str:
    for name, value in (("window_id", window_id), ("window_index", window_index), ("display_index", display_index)):
        error = _positive_int(name, value)
        if error:
            return _error(error)
    payload = _target_payload(app_name, window_id, window_index, display_index)
    payload.update({"x": x, "y": y})
    return _run_window_manager("move_window", payload)


def resize_window(
    width: int,
    height: int,
    app_name: str = "",
    window_id: int | None = None,
    window_index: int | None = None,
    display_index: int | None = None,
) -> str:
    for name, value in (("width", width), ("height", height), ("window_id", window_id), ("window_index", window_index), ("display_index", display_index)):
        error = _positive_int(name, value)
        if error:
            return _error(error)
    payload = _target_payload(app_name, window_id, window_index, display_index)
    payload.update({"width": width, "height": height})
    return _run_window_manager("resize_window", payload)


def center_window(
    app_name: str = "",
    window_id: int | None = None,
    window_index: int | None = None,
    display_index: int | None = None,
    width: int | None = None,
    height: int | None = None,
) -> str:
    for name, value in (("width", width), ("height", height), ("window_id", window_id), ("window_index", window_index), ("display_index", display_index)):
        error = _positive_int(name, value)
        if error:
            return _error(error)
    payload = _target_payload(app_name, window_id, window_index, display_index)
    if width is not None:
        payload["width"] = width
    if height is not None:
        payload["height"] = height
    return _run_window_manager("center_window", payload)


def tile_windows(
    layout: str = "columns",
    app_names: list[str] | None = None,
    display_index: int | None = None,
    padding: int = 8,
) -> str:
    if layout not in VALID_TILE_LAYOUTS:
        return _error(f"layout must be one of: {', '.join(sorted(VALID_TILE_LAYOUTS))}")
    if padding < 0:
        return _error("padding must be greater than or equal to 0")
    error = _positive_int("display_index", display_index)
    if error:
        return _error(error)
    payload: dict[str, Any] = {"layout": layout, "padding": padding}
    if app_names:
        payload["app_names"] = [name.strip() for name in app_names if name.strip()]
    if display_index is not None:
        payload["display_index"] = display_index
    return _run_window_manager("tile_windows", payload)


def minimize(
    app_name: str = "",
    window_id: int | None = None,
    window_index: int | None = None,
) -> str:
    return _run_window_manager(
        "minimize",
        _target_payload(app_name=app_name, window_id=window_id, window_index=window_index),
    )


def hide_app(app_name: str) -> str:
    if not app_name.strip():
        return _error("app_name cannot be empty")
    return _run_window_manager("hide_app", {"app_name": app_name.strip()})


def quit_app(app_name: str) -> str:
    if not app_name.strip():
        return _error("app_name cannot be empty")
    return _run_window_manager("quit_app", {"app_name": app_name.strip()})
```

- [ ] **Step 2: Run wrapper tests**

Run:

```bash
uv run pytest tests/test_window.py -v
```

Expected: all tests in `tests/test_window.py` pass, except failures caused by missing Swift script only if a test did not monkeypatch subprocess correctly.

- [ ] **Step 3: Commit wrapper**

Run:

```bash
git add tools/window.py tests/test_window.py
git commit -m "feat: add window manager python wrappers"
```

---

## Task 3: Swift Window Manager Helper

**Files:**
- Create: `tools/scripts/window-manager.swift`
- Test manually with `swift tools/scripts/window-manager.swift get_frontmost_app '{}'`

- [ ] **Step 1: Implement command-line parsing**

The script must accept exactly two arguments after the script path:

```text
window-manager.swift <action> <payload-json>
```

Implementation requirements:

- Decode payload with `JSONSerialization.jsonObject`.
- Store payload as `[String: Any]`.
- Dispatch on `action`.
- On success, print one compact JSON object to stdout.
- On failure, print the error message to stderr and exit 1.

- [ ] **Step 2: Implement app/window discovery**

Implement these Swift helper types and functions:

```swift
struct ManagedApp {
    let name: String
    let bundleID: String
    let pid: pid_t
    let application: NSRunningApplication
}

struct ManagedWindow {
    let windowID: Int
    let app: ManagedApp
    let title: String
    let frame: CGRect
    let axWindow: AXUIElement?
    let isMinimized: Bool
}
```

Required behavior:

- `frontmostApp()` reads `NSWorkspace.shared.frontmostApplication`.
- `runningApps(matching:)` searches `NSWorkspace.shared.runningApplications`.
- App matching checks localized name, bundle identifier, and executable URL last path component using case-insensitive substring matching.
- `axWindows(for:)` creates `AXUIElementCreateApplication(pid)` and reads `kAXWindowsAttribute`.
- `cgWindows()` uses `CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID)` to enrich windows with IDs and titles.
- `managedWindows(appName:includeMinimized:)` combines AX windows and CG windows by matching PID plus nearest equal frame. If a CG window ID cannot be matched, use `0` for `window_id` and still allow AX-only operations.

- [ ] **Step 3: Implement display helpers**

Required helpers:

- `screens()` returns `NSScreen.screens` in their current order.
- `screenForDisplayIndex(_:)` accepts 1-based indexes and returns an error for out-of-range values.
- `screenForWindow(_:)` picks the visible frame with the largest intersection with the window frame.
- `clampedFrame(rect:screen:)` keeps width and height at least `120x80` and within `screen.visibleFrame` when possible.
- Every placement tool uses `visibleFrame`.

- [ ] **Step 4: Implement read operations**

Implement:

- `get_frontmost_app`
- `list_windows`

Success output must match the behavior contract above. Include `display_index` for each listed window by comparing the window frame to `NSScreen.visibleFrame`.

- [ ] **Step 5: Implement app operations**

Implement:

- `hide_app`: resolve one app and call `application.hide()`.
- `quit_app`: resolve one app and call `application.terminate()`.

Return JSON with `action`, `app_name`, `bundle_id`, and `pid`.

- [ ] **Step 6: Implement window operations**

Implement:

- `focus_window`: resolve target, call `application.activate(options: [.activateAllWindows, .activateIgnoringOtherApps])`, then set `kAXMainAttribute` and `kAXFocusedAttribute` to `true` on the target AX window.
- `minimize`: set `kAXMinimizedAttribute` to `true`.
- `move_window`: set `kAXPositionAttribute`.
- `resize_window`: set `kAXSizeAttribute`.
- `center_window`: optionally resize first, then calculate centered origin inside selected display visible frame.
- `tile_windows`: resolve requested apps or use visible windows from the frontmost display; calculate frames for:
  - `columns`: equal-width columns.
  - `rows`: equal-height rows.
  - `grid`: `ceil(sqrt(count))` columns and `ceil(count / columns)` rows.

Return JSON with the final window frame or list of final frames after each mutation.

- [ ] **Step 7: Run Swift smoke checks**

Run:

```bash
swift tools/scripts/window-manager.swift get_frontmost_app '{}'
swift tools/scripts/window-manager.swift list_windows '{"include_minimized":false}'
swift tools/scripts/window-manager.swift center_window '{"app_name":"Finder"}'
```

Expected:

- The first command prints valid JSON with the current frontmost app.
- The second command prints valid JSON with a `windows` array.
- The third command either centers Finder's frontmost window or prints a clear Accessibility permission error.

- [ ] **Step 8: Commit Swift helper**

Run:

```bash
git add tools/scripts/window-manager.swift
git commit -m "feat: add swift window manager helper"
```

---

## Task 4: MCP Tool Registration

**Files:**
- Modify: `server.py`
- Test: `tests/test_window.py`

- [ ] **Step 1: Import the window module**

Modify the `from tools import (...)` block in `server.py` to include `window`.

- [ ] **Step 2: Register MCP tools near `open_app`**

Add tool functions in `server.py` after `open_app`:

```python
@mcp.tool()
async def get_frontmost_app() -> str:
    """
    Get the currently frontmost macOS application.

    Returns:
        JSON string with app name, bundle id, pid, and active state.
    """
    return window.get_frontmost_app()


@mcp.tool()
async def list_windows(
    app_name: str = Field(default=""),
    include_minimized: bool = Field(default=False),
) -> str:
    """
    List manageable macOS windows.

    Args:
        app_name: Optional app name, bundle id, or process name filter
        include_minimized: Include minimized windows when available

    Returns:
        JSON string with window ids, app metadata, titles, frames, and display indexes.
    """
    return window.list_windows(app_name, include_minimized)


@mcp.tool()
async def focus_window(
    app_name: str = Field(default=""),
    window_id: int | None = Field(default=None),
    window_index: int | None = Field(default=None),
) -> str:
    """
    Focus a macOS window by window id, app name, or frontmost fallback.

    Args:
        app_name: Optional app name, bundle id, or process name
        window_id: Optional CoreGraphics window id
        window_index: Optional 1-based index among the app's windows

    Returns:
        JSON string with focused window metadata, or an error message.
    """
    return window.focus_window(app_name, window_id, window_index)
```

Also add analogous wrappers for `move_window`, `resize_window`, `center_window`, `tile_windows`, `minimize`, `hide_app`, and `quit_app` using the Python function signatures from Task 2. Use `Field` constraints for public numeric bounds:

- `window_id`: `ge=1`
- `window_index`: `ge=1`
- `display_index`: `ge=1`
- `width`: `ge=1`
- `height`: `ge=1`
- `padding`: `ge=0`, `le=100`

- [ ] **Step 3: Add registration smoke test**

Append this test to `tests/test_window.py`:

```python
def test_server_exposes_window_tools():
    import server

    tool_names = {tool.name for tool in server.mcp._tool_manager._tools.values()}

    assert {
        "get_frontmost_app",
        "list_windows",
        "focus_window",
        "move_window",
        "resize_window",
        "center_window",
        "tile_windows",
        "minimize",
        "hide_app",
        "quit_app",
    }.issubset(tool_names)
```

- [ ] **Step 4: Run tests**

Run:

```bash
uv run pytest tests/test_window.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit MCP registration**

Run:

```bash
git add server.py tests/test_window.py
git commit -m "feat: expose window manager mcp tools"
```

---

## Task 5: Documentation and Skill Manifest

**Files:**
- Modify: `README.md`
- Modify: `skills/altic-studio/SKILL.md`

- [ ] **Step 1: Update README feature list**

Add a bullet under `## Features`:

```markdown
- 🪟 **Window & Workspace** - List/focus apps and windows, move/resize/center/tile windows, minimize windows, hide apps, and quit apps
```

- [ ] **Step 2: Update permissions**

Under permissions, add or expand:

```markdown
- ✅ **Accessibility** - Required for screen glow, system controls, and window management tools such as focus_window, move_window, resize_window, center_window, tile_windows, minimize, hide_app, and quit_app
- ✅ **Screen Recording** - Required for screenshot capture tools and improves window title/id discovery for list_windows on recent macOS versions
```

- [ ] **Step 3: Add manual smoke tests**

Add a section:

```markdown
## Manual Smoke Tests For Window Tools

- Call `get_frontmost_app` while Finder or Safari is active.
- Call `list_windows` and confirm visible app windows include frame and display metadata.
- Open two apps, then call `tile_windows` with `layout="columns"` and their app names.
- Call `center_window` with an app name and confirm the frontmost window is centered inside the visible display area.
- Call `move_window` and `resize_window` with a test app window, then call `list_windows` to confirm the new frame.
- Call `minimize` on a test app window and confirm it minimizes.
- Call `hide_app` on a non-critical app and confirm the app is hidden.
- Call `quit_app` only on a disposable test app.
```

- [ ] **Step 4: Update `skills/altic-studio/SKILL.md`**

Add a concise tool group for window management. Use the exact tool names registered in `server.py`.

- [ ] **Step 5: Commit docs**

Run:

```bash
git add README.md skills/altic-studio/SKILL.md
git commit -m "docs: document window workspace tools"
```

---

## Task 6: Full Verification

**Files:**
- All files touched by previous tasks

- [ ] **Step 1: Run unit tests**

Run:

```bash
uv run pytest -v
```

Expected: all existing file/clipboard tests plus new window wrapper tests pass.

- [ ] **Step 2: Run Swift syntax check**

Run:

```bash
swift tools/scripts/window-manager.swift get_frontmost_app '{}'
```

Expected: valid JSON or a clear macOS permission error. A Swift compile error is a failure.

- [ ] **Step 3: Run MCP server import check**

Run:

```bash
uv run python - <<'PY'
import server
print(server.mcp.name)
PY
```

Expected: prints `Altic-MCP` with no import errors.

- [ ] **Step 4: Final status check**

Run:

```bash
git status --short
```

Expected: no uncommitted changes unless the executor intentionally keeps the branch unstaged for review.

---

## Open Decisions

- Add `list_windows` even though the feature list did not explicitly request it. This is necessary for reliable targeting and aligns with the competitor comparison.
- Keep `open_app` in `tools/app.py`; this plan adds complementary app operations to `tools/window.py` because they share target resolution with windows.
- Use Swift instead of AppleScript for window placement because the feature needs display-aware geometry, CG window ids, Accessibility window attributes, and more reliable multi-display behavior.

## Self-Review

- Spec coverage: the plan covers `move_window`, `resize_window`, `tile_windows`, `center_window`, `focus_window`, `minimize`, `hide_app`, `quit_app`, `get_frontmost_app`, and display-aware placement. It also adds `list_windows` to make targeting practical.
- Placeholder scan: no task depends on undefined future work; each task names exact files, commands, and expected outcomes.
- Type consistency: public Python signatures, server wrappers, JSON payload keys, and tests use the same names: `app_name`, `window_id`, `window_index`, `display_index`, `x`, `y`, `width`, `height`, `layout`, `app_names`, and `padding`.
