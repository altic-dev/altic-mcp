import json
import subprocess
from pathlib import Path

from tools import screenshot


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


def screen_text_payload(text: str = "Hello screen"):
    return {
        "action": "extract_screen_text",
        "source": "active_screen",
        "screenshot_path": "/tmp/screen-text.png",
        "image_size": {"width": 1200, "height": 800},
        "recognition_level": "accurate",
        "text": text,
        "length_chars": len(text),
        "truncated": False,
        "lines": [
            {
                "text": "Hello screen",
                "confidence": 0.98,
                "frame": {"x": 10, "y": 20, "width": 200, "height": 30},
            }
        ],
        "visual_understanding": None,
    }


def test_extract_screen_text_invokes_swift_helper(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return completed(args, stdout=json.dumps(screen_text_payload()))

    monkeypatch.setattr(screenshot.subprocess, "run", fake_run)

    payload = read_json(
        screenshot.extract_screen_text(
            output_path="/tmp/out.png",
            recognition_level="fast",
            languages="en-US,fr-FR",
            include_boxes=False,
            visual_understanding="summary",
        )
    )

    assert payload["action"] == "extract_screen_text"
    assert seen["args"][0] == "swift"
    assert Path(seen["args"][1]).name == "extract-screen-text.swift"
    assert seen["args"][2:] == [
        "/tmp/out.png",
        "fast",
        "en-US,fr-FR",
        "false",
        "summary",
    ]
    assert seen["kwargs"]["timeout"] == 90


def test_extract_screen_text_uses_default_temp_screenshot_path(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["target"] = args[2]
        return completed(args, stdout=json.dumps(screen_text_payload()))

    monkeypatch.setattr(screenshot.subprocess, "run", fake_run)

    read_json(screenshot.extract_screen_text())

    target = Path(seen["target"])
    assert target.parent == Path("/tmp/altic-mcp-screenshots")
    assert target.name.startswith("screen-text-")
    assert target.suffix == ".png"


def test_extract_screen_text_rejects_invalid_recognition_level(monkeypatch):
    def fail_run(*args, **kwargs):
        raise AssertionError("subprocess should not run for invalid recognition level")

    monkeypatch.setattr(screenshot.subprocess, "run", fail_run)

    result = screenshot.extract_screen_text(recognition_level="balanced")

    assert result.startswith("Error:")
    assert "recognition_level must be one of" in result


def test_extract_screen_text_rejects_invalid_visual_understanding(monkeypatch):
    def fail_run(*args, **kwargs):
        raise AssertionError("subprocess should not run for invalid visual understanding")

    monkeypatch.setattr(screenshot.subprocess, "run", fail_run)

    result = screenshot.extract_screen_text(visual_understanding="describe_everything")

    assert result.startswith("Error:")
    assert "visual_understanding must be one of" in result


def test_extract_screen_text_invalid_swift_json_returns_error(monkeypatch):
    def fake_run(args, **kwargs):
        return completed(args, stdout="not-json")

    monkeypatch.setattr(screenshot.subprocess, "run", fake_run)

    result = screenshot.extract_screen_text()

    assert result.startswith("Error: invalid screen text response:")


def test_extract_screen_text_truncates_long_text(monkeypatch):
    long_text = "abcdefghijklmnopqrstuvwxyz"

    def fake_run(args, **kwargs):
        return completed(args, stdout=json.dumps(screen_text_payload(long_text)))

    monkeypatch.setattr(screenshot.subprocess, "run", fake_run)

    payload = read_json(screenshot.extract_screen_text(max_chars=10))

    assert payload["text"] == "abcdefghij"
    assert payload["length_chars"] == len(long_text)
    assert payload["truncated"] is True


def test_server_exposes_extract_screen_text_tool():
    import server

    tool_names = set(server.mcp._tool_manager._tools)

    assert "extract_screen_text" in tool_names


def test_swift_helper_contains_macos_27_foundation_models_primary_path():
    script = Path("tools/scripts/extract-screen-text.swift").read_text(encoding="utf-8")

    assert "LanguageModelSession" in script
    assert "SystemLanguageModel.default" in script
    assert "OCRTool()" in script
    assert "Attachment(image)" in script
    assert "FoundationModels image-input OCRTool integration is gated" not in script
