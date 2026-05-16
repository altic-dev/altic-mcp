import json
import subprocess
from pathlib import Path

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
    assert (
        read_json(window.minimize(app_name="Safari", window_index=1))["action"]
        == "minimize"
    )
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
        return completed(
            args,
            stdout="",
            stderr="accessibility permission denied",
            returncode=1,
        )

    monkeypatch.setattr(window.subprocess, "run", fake_run)

    assert window.get_frontmost_app() == "Error: accessibility permission denied"


def test_invalid_json_from_helper_returns_error(monkeypatch):
    def fake_run(args, **kwargs):
        return completed(args, stdout="not-json")

    monkeypatch.setattr(window.subprocess, "run", fake_run)

    assert window.get_frontmost_app().startswith(
        "Error: invalid window manager response:"
    )


def test_server_exposes_window_tools():
    import server

    tool_names = set(server.mcp._tool_manager._tools)

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
