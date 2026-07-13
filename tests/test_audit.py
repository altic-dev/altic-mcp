import json

import pytest

from tools import audit, config


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    config.reset_cache()
    monkeypatch.setattr(config, "_CONFIG_DIR", tmp_path / "cfg")
    monkeypatch.setattr(config, "_CONFIG_FILE", tmp_path / "cfg" / "config.json")
    config.reset_cache()
    config.set_config_value("audit_log_enabled", True)

    cache_dir = tmp_path / "cache"
    monkeypatch.setattr(audit, "_CACHE_DIR", cache_dir)
    monkeypatch.setattr(audit, "_AUDIT_FILE", cache_dir / "audit.jsonl")
    yield
    config.reset_cache()


def test_log_tool_call_writes_jsonl_line():
    audit.log_tool_call("send_imessage", {"phone": "+1555"}, True, 12.5)

    lines = audit._AUDIT_FILE.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1

    record = json.loads(lines[0])
    assert record["tool"] == "send_imessage"
    assert record["ok"] is True
    assert record["duration_ms"] == 12.5
    assert record["arguments"]["phone"] == "+1555"


def test_log_tool_call_noops_when_disabled():
    config.set_config_value("audit_log_enabled", False)

    audit.log_tool_call("test", None, True, 1.0)

    assert not audit._AUDIT_FILE.exists()


def test_get_recent_tool_calls_returns_chronological():
    for i in range(5):
        audit.log_tool_call(f"tool_{i}", None, True, float(i))

    payload = json.loads(audit.get_recent_tool_calls(limit=3))

    assert payload["ok"] is True
    assert payload["data"]["count"] == 3
    tools = [c["tool"] for c in payload["data"]["calls"]]
    assert tools == ["tool_2", "tool_3", "tool_4"]


def test_get_recent_tool_calls_empty_when_no_log():
    payload = json.loads(audit.get_recent_tool_calls())

    assert payload["ok"] is True
    assert payload["data"]["count"] == 0
    assert payload["data"]["calls"] == []


def test_log_truncates_long_arguments():
    long_value = "x" * 500
    audit.log_tool_call("test", {"big": long_value}, True, 1.0)

    record = json.loads(audit._AUDIT_FILE.read_text(encoding="utf-8").strip())
    assert "...(truncated)" in record["arguments"]["big"]
    assert len(record["arguments"]["big"]) < len(long_value)


def test_rotation_when_file_exceeds_limit(monkeypatch):
    monkeypatch.setattr(audit, "_MAX_FILE_SIZE", 100)

    for i in range(20):
        audit.log_tool_call(f"tool_{i}", {"data": "x" * 20}, True, 1.0)

    assert audit._AUDIT_FILE.exists()
    rotated = audit._AUDIT_FILE.with_suffix(".jsonl.1")
    assert rotated.exists()
