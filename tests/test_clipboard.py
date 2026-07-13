import json
import subprocess
from pathlib import Path

from tools import clipboard


def read_json(value: str):
    assert not value.startswith("Error:"), value
    return json.loads(value)


def test_get_clipboard_text_truncates_and_reports_metadata(monkeypatch):
    def fake_run(args, **kwargs):
        assert args == ["pbpaste"]
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout="clipboard body",
            stderr="",
        )

    monkeypatch.setattr(clipboard.subprocess, "run", fake_run)

    payload = read_json(clipboard.get_clipboard_text(max_chars=9))

    assert payload == {
        "action": "get_clipboard_text",
        "length_chars": 14,
        "text": "clipboard",
        "truncated": True,
    }


def test_get_clipboard_text_uses_configured_default(monkeypatch):
    monkeypatch.setattr(clipboard.config, "get", lambda key: 4)
    monkeypatch.setattr(
        clipboard.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0], returncode=0, stdout="clipboard", stderr=""
        ),
    )

    payload = read_json(clipboard.get_clipboard_text())

    assert payload["text"] == "clip"
    assert payload["truncated"] is True


def test_set_clipboard_text_writes_to_pbcopy(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        seen["input"] = kwargs["input"]
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(clipboard.subprocess, "run", fake_run)

    payload = read_json(clipboard.set_clipboard_text("hello"))

    assert payload == {"action": "set_clipboard_text", "length_chars": 5}
    assert seen == {"args": ["pbcopy"], "input": "hello"}


def test_clear_clipboard_writes_empty_text_to_pbcopy(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        seen["input"] = kwargs["input"]
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(clipboard.subprocess, "run", fake_run)

    payload = read_json(clipboard.clear_clipboard())

    assert payload == {"action": "clear_clipboard"}
    assert seen == {"args": ["pbcopy"], "input": ""}


def test_get_clipboard_files_returns_swift_json(monkeypatch):
    swift_payload = {
        "action": "get_clipboard_files",
        "files": [{"path": "/Users/example/Desktop/report.pdf", "exists": True}],
        "count": 1,
    }

    def fake_run(args, **kwargs):
        assert args[0] == "swift"
        assert Path(args[1]).name == "clipboard.swift"
        assert args[2] == "get-files"
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=json.dumps(swift_payload),
            stderr="",
        )

    monkeypatch.setattr(clipboard.subprocess, "run", fake_run)

    assert read_json(clipboard.get_clipboard_files()) == swift_payload


def test_set_clipboard_files_validates_paths_and_invokes_swift(tmp_path, monkeypatch):
    target = tmp_path / "report.txt"
    target.write_text("body", encoding="utf-8")
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"action":"set_clipboard_files","count":1}',
            stderr="",
        )

    monkeypatch.setattr(clipboard.subprocess, "run", fake_run)

    payload = read_json(clipboard.set_clipboard_files([str(target)]))

    assert payload == {"action": "set_clipboard_files", "count": 1}
    assert seen["args"][2:] == ["set-files", str(target.resolve())]


def test_set_clipboard_files_rejects_missing_paths(tmp_path):
    missing = tmp_path / "missing.txt"

    result = clipboard.set_clipboard_files([str(missing)])

    assert result.startswith("Error:")
    assert "path does not exist" in result


def test_save_clipboard_image_returns_message_and_image(monkeypatch, tmp_path):
    output = tmp_path / "clipboard.png"

    def fake_run(args, **kwargs):
        assert args[0] == "swift"
        assert Path(args[1]).name == "clipboard.swift"
        assert args[2:] == ["save-image", str(output.resolve())]
        output.write_bytes(b"png")
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=str(output.resolve()),
            stderr="",
        )

    monkeypatch.setattr(clipboard.subprocess, "run", fake_run)

    result = clipboard.save_clipboard_image(str(output))

    assert isinstance(result, list)
    assert result[0] == f"Saved clipboard image: {output.resolve()}"


def test_set_clipboard_image_rejects_missing_file(tmp_path):
    result = clipboard.set_clipboard_image(str(tmp_path / "missing.png"))

    assert result.startswith("Error:")
    assert "image file does not exist" in result
