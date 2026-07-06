import json
import subprocess
from pathlib import Path

from tools import reminders


def read_json(value: str):
    payload = json.loads(value)
    assert payload["ok"] is True, payload
    return payload


def test_list_reminder_lists_invokes_manager(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"lists":["Reminders","Work"]}',
            stderr="",
        )

    monkeypatch.setattr(reminders.subprocess, "run", fake_run)

    payload = read_json(reminders.list_reminder_lists())

    assert payload["action"] == "reminders.list_lists"
    assert payload["data"] == {"lists": ["Reminders", "Work"]}
    assert seen["args"][0] == "osascript"
    assert Path(seen["args"][1]).name == "reminders-manager.applescript"
    assert seen["args"][2:] == ["list_lists"]
    assert seen["kwargs"]["timeout"] == 60


def test_list_reminders_serializes_filters(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"reminders":[]}',
            stderr="",
        )

    monkeypatch.setattr(reminders.subprocess, "run", fake_run)

    payload = read_json(reminders.list_reminders("Work", include_completed=True))

    assert payload["action"] == "reminders.list"
    assert seen["args"][2:] == ["list", "Work", "true"]


def test_complete_reminder_rejects_empty_identifier(monkeypatch):
    def fail_run(*args, **kwargs):
        raise AssertionError("subprocess should not run")

    monkeypatch.setattr(reminders.subprocess, "run", fail_run)

    payload = json.loads(reminders.complete_reminder(""))

    assert payload["ok"] is False
    assert payload["error"]["code"] == "validation_error"


def test_delete_reminder_defaults_to_dry_run(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"deleted":false,"matches":[{"name":"Pay rent"}]}',
            stderr="",
        )

    monkeypatch.setattr(reminders.subprocess, "run", fake_run)

    payload = read_json(reminders.delete_reminder("Pay rent"))

    assert payload["action"] == "reminders.delete"
    assert payload["data"]["deleted"] is False
    assert seen["args"][2:] == ["delete", "Pay rent", "", "true"]


def test_reschedule_reminder_validates_datetime(monkeypatch):
    def fail_run(*args, **kwargs):
        raise AssertionError("subprocess should not run")

    monkeypatch.setattr(reminders.subprocess, "run", fail_run)

    payload = json.loads(reminders.reschedule_reminder("Pay rent", "tomorrow"))

    assert payload["ok"] is False
    assert payload["error"]["message"].startswith("Time must be in format")


def test_update_reminder_serializes_fields(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"updated":true,"reminder":{"id":"REM-1","name":"Pay rent"}}',
            stderr="",
        )

    monkeypatch.setattr(reminders.subprocess, "run", fake_run)

    payload = read_json(
        reminders.update_reminder(
            identifier="Pay rent",
            list_name="Home",
            name="Pay rent today",
            body="Use checking",
            datetime="2026-07-06 09:00",
            completed=False,
            priority=5,
            flagged=True,
        )
    )

    assert payload["action"] == "reminders.update"
    assert payload["data"]["updated"] is True
    assert seen["args"][2:] == [
        "update",
        "Pay rent",
        "Home",
        "Pay rent today",
        "Use checking",
        "2026-07-06 09:00",
        "false",
        "5",
        "true",
    ]


def test_update_reminder_validates_priority(monkeypatch):
    def fail_run(*args, **kwargs):
        raise AssertionError("subprocess should not run")

    monkeypatch.setattr(reminders.subprocess, "run", fail_run)

    payload = json.loads(reminders.update_reminder("Pay rent", priority=12))

    assert payload["ok"] is False
    assert payload["error"]["code"] == "validation_error"


def test_show_reminder_invokes_manager(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"shown":true,"reminder":{"id":"REM-1","name":"Pay rent"}}',
            stderr="",
        )

    monkeypatch.setattr(reminders.subprocess, "run", fake_run)

    payload = read_json(reminders.show_reminder("Pay rent", "Home"))

    assert payload["action"] == "reminders.show"
    assert payload["data"]["shown"] is True
    assert seen["args"][2:] == ["show", "Pay rent", "Home"]
