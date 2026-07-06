import json
import subprocess
from pathlib import Path

from tools import contacts


def read_json(value: str):
    payload = json.loads(value)
    assert payload["ok"] is True, payload
    return payload


def test_get_contact_invokes_manager(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"found":true,"contact":{"id":"ABC","name":"Ada Lovelace"}}',
            stderr="",
        )

    monkeypatch.setattr(contacts.subprocess, "run", fake_run)

    payload = read_json(contacts.get_contact("Ada"))

    assert payload["action"] == "contacts.get"
    assert payload["data"]["found"] is True
    assert seen["args"][0] == "osascript"
    assert Path(seen["args"][1]).name == "contacts-manager.applescript"
    assert seen["args"][2:] == ["get", "Ada"]
    assert seen["kwargs"]["timeout"] == 60


def test_create_contact_requires_a_name(monkeypatch):
    def fail_run(*args, **kwargs):
        raise AssertionError("subprocess should not run")

    monkeypatch.setattr(contacts.subprocess, "run", fail_run)

    payload = json.loads(contacts.create_contact("", ""))

    assert payload["ok"] is False
    assert payload["error"]["code"] == "validation_error"


def test_create_contact_serializes_fields(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"created":true,"contact":{"id":"ABC","name":"Ada Lovelace"}}',
            stderr="",
        )

    monkeypatch.setattr(contacts.subprocess, "run", fake_run)

    payload = read_json(
        contacts.create_contact(
            first_name="Ada",
            last_name="Lovelace",
            organization="Analytical Engines",
            phone="+15551234567",
            email="ada@example.com",
            note="Test note",
        )
    )

    assert payload["action"] == "contacts.create"
    assert payload["data"]["created"] is True
    assert seen["args"][2:] == [
        "create",
        "Ada",
        "Lovelace",
        "Analytical Engines",
        "+15551234567",
        "ada@example.com",
        "Test note",
    ]


def test_update_contact_rejects_empty_identifier(monkeypatch):
    def fail_run(*args, **kwargs):
        raise AssertionError("subprocess should not run")

    monkeypatch.setattr(contacts.subprocess, "run", fail_run)

    payload = json.loads(contacts.update_contact(""))

    assert payload["ok"] is False
    assert payload["error"]["code"] == "validation_error"


def test_update_contact_serializes_optional_fields(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"updated":true,"contact":{"id":"ABC","name":"Ada Byron"}}',
            stderr="",
        )

    monkeypatch.setattr(contacts.subprocess, "run", fake_run)

    payload = read_json(
        contacts.update_contact(
            identifier="ABC",
            first_name="Ada",
            last_name="Byron",
            organization="",
            phone="+15557654321",
            email="",
            note="Updated",
        )
    )

    assert payload["action"] == "contacts.update"
    assert payload["data"]["updated"] is True
    assert seen["args"][2:] == [
        "update",
        "ABC",
        "Ada",
        "Byron",
        "",
        "+15557654321",
        "",
        "Updated",
    ]
