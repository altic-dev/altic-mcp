import json
import subprocess
from pathlib import Path

from tools import screen_text


def read_json(value: str):
    assert not value.startswith("Error:"), value
    return json.loads(value)


def completed(args, stdout="", stderr="", returncode=0):
    return subprocess.CompletedProcess(
        args=args,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_extract_screen_text_invokes_swift_helper_with_defaults(monkeypatch, tmp_path):
    output = tmp_path / "screen.png"
    seen = {}

    swift_payload = {
        "action": "extract_screen_text",
        "screenshot_path": str(output.resolve()),
        "text": "Visible title\nPrimary button",
        "line_count": 2,
        "average_confidence": 0.91,
        "visual_summary": "",
        "visual_model_available": False,
        "visual_error": "",
    }

    def fake_run(args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return completed(args, stdout=json.dumps(swift_payload))

    monkeypatch.setattr(screen_text.subprocess, "run", fake_run)

    payload = read_json(screen_text.extract_screen_text(str(output)))

    assert payload["action"] == "extract_screen_text"
    assert payload["screenshot_path"] == str(output.resolve())
    assert payload["text"] == "Visible title\nPrimary button"
    assert payload["length_chars"] == 28
    assert payload["truncated"] is False
    assert payload["line_count"] == 2
    assert payload["average_confidence"] == 0.91
    assert payload["visual_summary"] == ""
    assert payload["visual_model_available"] is False
    assert payload["visual_error"] == ""
    assert seen["args"][0] == "swift"
    assert Path(seen["args"][1]).name == "extract-screen-text.swift"
    assert seen["args"][2:] == [
        str(output.resolve()),
        "false",
        "Summarize the visible screen content and call out actionable UI text.",
    ]
    assert seen["kwargs"]["timeout"] == 90


def test_extract_screen_text_passes_visual_summary_options(monkeypatch, tmp_path):
    output = tmp_path / "screen.png"
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return completed(
            args,
            stdout=json.dumps(
                {
                    "action": "extract_screen_text",
                    "screenshot_path": str(output.resolve()),
                    "text": "Settings",
                    "line_count": 1,
                    "average_confidence": 0.88,
                    "visual_summary": "A settings page is open.",
                    "visual_model_available": True,
                    "visual_model_source": "FoundationModels.SystemLanguageModel",
                    "visual_prompt": "What is shown?",
                }
            ),
        )

    monkeypatch.setattr(screen_text.subprocess, "run", fake_run)

    payload = read_json(
        screen_text.extract_screen_text(
            str(output),
            include_visual_summary=True,
            visual_prompt="What is shown?",
        )
    )

    assert payload["visual_model_available"] is True
    assert payload["visual_model_source"] == "FoundationModels.SystemLanguageModel"
    assert payload["visual_summary"] == "A settings page is open."
    assert payload["visual_prompt"] == "What is shown?"
    assert seen["args"][2:] == [str(output.resolve()), "true", "What is shown?"]


def test_extract_screen_text_truncates_text_in_python(monkeypatch, tmp_path):
    output = tmp_path / "screen.png"

    def fake_run(args, **kwargs):
        return completed(
            args,
            stdout=json.dumps(
                {
                    "action": "extract_screen_text",
                    "screenshot_path": str(output.resolve()),
                    "text": "abcdefghijklmnopqrstuvwxyz",
                    "line_count": 1,
                    "average_confidence": 0.7,
                }
            ),
        )

    monkeypatch.setattr(screen_text.subprocess, "run", fake_run)

    payload = read_json(screen_text.extract_screen_text(str(output), max_chars=10))

    assert payload["text"] == "abcdefghij"
    assert payload["length_chars"] == 26
    assert payload["returned_length_chars"] == 10
    assert payload["truncated"] is True


def test_extract_screen_text_reports_visual_unavailable(monkeypatch, tmp_path):
    output = tmp_path / "screen.png"

    def fake_run(args, **kwargs):
        return completed(
            args,
            stdout=json.dumps(
                {
                    "action": "extract_screen_text",
                    "screenshot_path": str(output.resolve()),
                    "text": "Read me",
                    "line_count": 1,
                    "average_confidence": 0.81,
                    "visual_summary": "",
                    "visual_model_available": False,
                    "visual_error": (
                        "FoundationModels visual understanding requires macOS 27 or later"
                    ),
                }
            ),
        )

    monkeypatch.setattr(screen_text.subprocess, "run", fake_run)

    payload = read_json(
        screen_text.extract_screen_text(str(output), include_visual_summary=True)
    )

    assert payload["text"] == "Read me"
    assert payload["visual_model_available"] is False
    assert "macOS 27" in payload["visual_error"]


def test_extract_screen_text_returns_subprocess_error(monkeypatch, tmp_path):
    output = tmp_path / "screen.png"

    def fake_run(args, **kwargs):
        return completed(args, stderr="Screen Recording permission denied", returncode=1)

    monkeypatch.setattr(screen_text.subprocess, "run", fake_run)

    result = screen_text.extract_screen_text(str(output))

    assert result == "Error: Unable to extract screen text: Screen Recording permission denied"


def test_extract_screen_text_reports_invalid_json(monkeypatch, tmp_path):
    output = tmp_path / "screen.png"

    def fake_run(args, **kwargs):
        return completed(args, stdout="not-json")

    monkeypatch.setattr(screen_text.subprocess, "run", fake_run)

    result = screen_text.extract_screen_text(str(output))

    assert result.startswith("Error: invalid screen text response:")


def test_server_exposes_extract_screen_text():
    import server

    tool_names = set(server.mcp._tool_manager._tools)

    assert "extract_screen_text" in tool_names
