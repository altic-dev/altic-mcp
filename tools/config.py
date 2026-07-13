"""Runtime configuration for altic-mcp with on-disk persistence.

Config is loaded from ~/.config/altic-mcp/config.json on first access and
cached in-process. Changes via set_config_value persist immediately and take
effect without restarting the server.
"""

import json
import threading
from pathlib import Path
from typing import Any

from . import result

_CONFIG_DIR = Path.home() / ".config" / "altic-mcp"
_CONFIG_FILE = _CONFIG_DIR / "config.json"
_LOCK = threading.Lock()

_DEFAULTS: dict[str, Any] = {
    "file_search_max_results": 25,
    "osascript_timeout_seconds": 60,
    "clipboard_max_chars": 20000,
    "include_hidden_default": False,
    "allowed_directories": [],  # empty list = full filesystem access
    "audit_log_enabled": False,
    "search_visit_limit": 50000,  # max filesystem entries to walk per search batch
}

_TYPES: dict[str, type] = {
    "file_search_max_results": int,
    "osascript_timeout_seconds": int,
    "clipboard_max_chars": int,
    "include_hidden_default": bool,
    "allowed_directories": list,
    "audit_log_enabled": bool,
    "search_visit_limit": int,
}

_cache: dict[str, Any] | None = None


def _load() -> dict[str, Any]:
    """Load and cache the merged config (defaults + persisted overrides)."""
    global _cache
    if _cache is not None:
        return _cache

    merged = dict(_DEFAULTS)
    if _CONFIG_FILE.exists():
        try:
            stored = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(stored, dict):
                for key, value in stored.items():
                    if key in _DEFAULTS:
                        merged[key] = value
        except (json.JSONDecodeError, OSError):
            pass

    _cache = merged
    return _cache


def _persist(config: dict[str, Any]) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(
        json.dumps(config, indent=2, sort_keys=True), encoding="utf-8"
    )


def get(key: str | None = None) -> Any:
    """Get a config value by key, or the full config dict if key is None."""
    with _LOCK:
        config = _load()
    if key is None:
        return dict(config)
    return config.get(key, _DEFAULTS.get(key))


def set_value(key: str, value: Any) -> None:
    """Set a config value, update the cache, and persist to disk."""
    with _LOCK:
        config = _load()
        config[key] = value
        _persist(config)


def reset_cache() -> None:
    """Clear the in-memory cache (used by tests)."""
    global _cache
    with _LOCK:
        _cache = None


def defaults() -> dict[str, Any]:
    """Return the default config dict (no overrides)."""
    return dict(_DEFAULTS)


def get_config() -> str:
    """Return the full current configuration as a structured JSON string."""
    return result.ok("config.get", get())


def set_config_value(key: str, value: Any) -> str:
    """Set a single config key and persist. Returns the updated key/value."""
    if key not in _DEFAULTS:
        valid = ", ".join(sorted(_DEFAULTS))
        return result.error(
            "config.set",
            f"unknown config key: {key}. Valid keys: {valid}",
            code="validation_error",
        )

    expected = _TYPES.get(key)
    if expected is bool:
        if not isinstance(value, bool):
            return result.error(
                "config.set", f"{key} must be a boolean", code="validation_error"
            )
    elif expected is int:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return result.error(
                "config.set", f"{key} must be a number", code="validation_error"
            )
        value = int(value)
    elif expected is list:
        if not isinstance(value, list):
            return result.error(
                "config.set", f"{key} must be a list", code="validation_error"
            )

    set_value(key, value)
    return result.ok("config.set", {"key": key, "value": value})
