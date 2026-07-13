import json

import pytest

from tools import config


@pytest.fixture(autouse=True)
def _reset_config_cache(tmp_path, monkeypatch):
    """Isolate each test: reset cache and point config at a temp file."""
    config.reset_cache()
    monkeypatch.setattr(config, "_CONFIG_DIR", tmp_path / "altic-config")
    monkeypatch.setattr(config, "_CONFIG_FILE", tmp_path / "altic-config" / "config.json")
    config.reset_cache()
    yield
    config.reset_cache()


def test_defaults_are_returned_when_no_file_exists():
    payload = json.loads(config.get_config())

    assert payload["ok"] is True
    assert payload["data"]["osascript_timeout_seconds"] == 60
    assert payload["data"]["audit_log_enabled"] is False


def test_set_config_value_persists_and_updates_cache():
    result_str = config.set_config_value("osascript_timeout_seconds", 120)

    payload = json.loads(result_str)
    assert payload["ok"] is True
    assert payload["data"] == {"key": "osascript_timeout_seconds", "value": 120}

    assert config.get("osascript_timeout_seconds") == 120

    stored = json.loads(config._CONFIG_FILE.read_text(encoding="utf-8"))
    assert stored["osascript_timeout_seconds"] == 120


def test_set_config_value_rejects_unknown_key():
    payload = json.loads(config.set_config_value("nonexistent_key", 1))

    assert payload["ok"] is False
    assert payload["error"]["code"] == "validation_error"
    assert "nonexistent_key" in payload["error"]["message"]


def test_set_config_value_rejects_wrong_type():
    payload = json.loads(config.set_config_value("audit_log_enabled", "not a bool"))

    assert payload["ok"] is False
    assert payload["error"]["code"] == "validation_error"


def test_set_config_value_coerces_float_to_int():
    payload = json.loads(config.set_config_value("file_search_max_results", 42.0))

    assert payload["ok"] is True
    assert payload["data"]["value"] == 42
    assert isinstance(payload["data"]["value"], int)


def test_persisted_values_are_loaded_on_next_access():
    config.set_config_value("include_hidden_default", True)
    config.reset_cache()  # Simulate a fresh process

    assert config.get("include_hidden_default") is True
