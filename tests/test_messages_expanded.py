import json
import subprocess
from pathlib import Path

from tools import messages


def read_json(value: str):
    payload = json.loads(value)
    assert payload["ok"] is True, payload
    return payload


def test_list_chats_invokes_manager(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"chats":[{"id":"iMessage;-;+15551234567","name":"+15551234567"}],"count":1}',
            stderr="",
        )

    monkeypatch.setattr(messages.subprocess, "run", fake_run)

    payload = read_json(messages.list_chats(limit=10))

    assert payload["action"] == "messages.list_chats"
    assert payload["data"]["count"] == 1
    assert seen["args"][0] == "osascript"
    assert Path(seen["args"][1]).name == "messages-manager.applescript"
    assert seen["args"][2:] == ["list_chats", "10"]
    assert seen["kwargs"]["timeout"] == 60


def test_send_file_message_validates_file_path(tmp_path):
    missing = tmp_path / "missing.pdf"

    payload = json.loads(messages.send_file_message("+15551234567", str(missing)))

    assert payload["ok"] is False
    assert payload["error"]["code"] == "validation_error"
    assert "file does not exist" in payload["error"]["message"]


def test_send_file_message_invokes_manager(tmp_path, monkeypatch):
    attachment = tmp_path / "report.pdf"
    attachment.write_text("demo", encoding="utf-8")
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"sent":true,"recipient":"+15551234567","path":"/tmp/report.pdf"}',
            stderr="",
        )

    monkeypatch.setattr(messages.subprocess, "run", fake_run)

    payload = read_json(
        messages.send_file_message(
            recipient="+15551234567",
            path=str(attachment),
            message="see attached",
            recipient_type="handle",
        )
    )

    assert payload["action"] == "messages.send_file"
    assert payload["data"]["sent"] is True
    assert seen["args"][2:] == [
        "send_file",
        "+15551234567",
        str(attachment.resolve()),
        "see attached",
        "handle",
    ]
