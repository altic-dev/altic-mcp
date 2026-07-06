import json
import subprocess
from pathlib import Path

from tools import notes


def read_json(value: str):
    payload = json.loads(value)
    assert payload["ok"] is True, payload
    return payload


def test_list_note_folders_invokes_manager(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"folders":["Notes","Projects"]}',
            stderr="",
        )

    monkeypatch.setattr(notes.subprocess, "run", fake_run)

    payload = read_json(notes.list_note_folders())

    assert payload["action"] == "notes.list_folders"
    assert payload["data"] == {"folders": ["Notes", "Projects"]}
    assert seen["args"][0] == "osascript"
    assert Path(seen["args"][1]).name == "notes-manager.applescript"
    assert seen["args"][2:] == ["list_folders"]


def test_get_note_rejects_empty_identifier(monkeypatch):
    def fail_run(*args, **kwargs):
        raise AssertionError("subprocess should not run")

    monkeypatch.setattr(notes.subprocess, "run", fail_run)

    payload = json.loads(notes.get_note(""))

    assert payload["ok"] is False
    assert payload["error"]["code"] == "validation_error"


def test_append_to_note_serializes_plain_text(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"note":{"name":"Plan"}}',
            stderr="",
        )

    monkeypatch.setattr(notes.subprocess, "run", fake_run)

    payload = read_json(notes.append_to_note("Plan", "new line"))

    assert payload["action"] == "notes.append"
    assert seen["args"][2:] == ["append", "Plan", "new line"]


def test_delete_note_defaults_to_dry_run(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"deleted":false}',
            stderr="",
        )

    monkeypatch.setattr(notes.subprocess, "run", fake_run)

    payload = read_json(notes.delete_note("Plan"))

    assert payload["action"] == "notes.delete"
    assert seen["args"][2:] == ["delete", "Plan", "true"]


def test_list_notes_serializes_folder_and_limit(monkeypatch):
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"notes":[]}',
            stderr="",
        )

    monkeypatch.setattr(notes.subprocess, "run", fake_run)

    payload = read_json(notes.list_notes("Projects", max_results=7))

    assert payload["action"] == "notes.list"
    assert seen["args"][2:] == ["list", "Projects", "7"]
