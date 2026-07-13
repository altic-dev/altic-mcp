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
            return _error(
                result.stderr.strip() or f"window manager action failed: {action}"
            )

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
    for name, value in (("window_id", window_id), ("window_index", window_index)):
        error = _positive_int(name, value)
        if error:
            return _error(error)
    return _run_window_manager(
        "focus_window",
        _target_payload(
            app_name=app_name,
            window_id=window_id,
            window_index=window_index,
        ),
    )


def move_window(
    x: int,
    y: int,
    app_name: str = "",
    window_id: int | None = None,
    window_index: int | None = None,
    display_index: int | None = None,
) -> str:
    for name, value in (
        ("window_id", window_id),
        ("window_index", window_index),
        ("display_index", display_index),
    ):
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
    for name, value in (
        ("width", width),
        ("height", height),
        ("window_id", window_id),
        ("window_index", window_index),
        ("display_index", display_index),
    ):
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
    for name, value in (
        ("width", width),
        ("height", height),
        ("window_id", window_id),
        ("window_index", window_index),
        ("display_index", display_index),
    ):
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
    for name, value in (("window_id", window_id), ("window_index", window_index)):
        error = _positive_int(name, value)
        if error:
            return _error(error)
    return _run_window_manager(
        "minimize",
        _target_payload(
            app_name=app_name,
            window_id=window_id,
            window_index=window_index,
        ),
    )


def hide_app(app_name: str) -> str:
    if not app_name.strip():
        return _error("app_name cannot be empty")
    return _run_window_manager("hide_app", {"app_name": app_name.strip()})


def quit_app(app_name: str) -> str:
    if not app_name.strip():
        return _error("app_name cannot be empty")
    return _run_window_manager("quit_app", {"app_name": app_name.strip()})
