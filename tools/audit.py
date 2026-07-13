"""Audit logging for tool calls with size-based rotation.

Every tool call routed through the MCP middleware is appended as a JSON line
to ~/.cache/altic-mcp/audit.jsonl. The file is rotated to ``.jsonl.1`` when it
exceeds 10 MB so it never grows unbounded.
"""

import json
import time
from pathlib import Path
from typing import Any

from . import config, result

_CACHE_DIR = Path.home() / ".cache" / "altic-mcp"
_AUDIT_FILE = _CACHE_DIR / "audit.jsonl"
_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _enabled() -> bool:
    return bool(config.get("audit_log_enabled"))


def _rotate_if_needed() -> None:
    """Rotate the audit file to ``.jsonl.1`` when it exceeds the size limit."""
    try:
        if _AUDIT_FILE.exists() and _AUDIT_FILE.stat().st_size >= _MAX_FILE_SIZE:
            rotated = _AUDIT_FILE.with_suffix(".jsonl.1")
            if rotated.exists():
                rotated.unlink()
            _AUDIT_FILE.rename(rotated)
    except OSError:
        pass


def _summarize(value: Any, max_len: int = 200) -> Any:
    """Truncate large string/list values so the audit log stays compact."""
    if isinstance(value, str) and len(value) > max_len:
        return value[:max_len] + "...(truncated)"
    if isinstance(value, list) and len(value) > 20:
        return [*value[:20], "...(truncated)"]
    return value


def log_tool_call(
    tool: str,
    arguments: dict[str, Any] | None,
    ok: bool,
    duration_ms: float,
) -> None:
    """Append a tool-call record to the audit log.

    Silently no-ops when ``audit_log_enabled`` is false or the write fails.
    """
    if not _enabled():
        return

    record: dict[str, Any] = {
        "ts": time.time(),
        "iso_ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
        "tool": tool,
        "ok": ok,
        "duration_ms": round(duration_ms, 2),
    }
    if arguments:
        record["arguments"] = {k: _summarize(v) for k, v in arguments.items()}

    line = json.dumps(record, sort_keys=True, default=str)
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _rotate_if_needed()
        with _AUDIT_FILE.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def get_recent_tool_calls(limit: int = 50) -> str:
    """MCP tool: return the most recent tool calls from the audit log."""
    limit = max(1, min(limit, 500))

    records: list[dict[str, Any]] = []
    if _AUDIT_FILE.exists():
        try:
            with _AUDIT_FILE.open("r", encoding="utf-8") as fh:
                lines = fh.readlines()
            for line in lines[-limit:]:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    records.append(json.loads(stripped))
                except json.JSONDecodeError:
                    continue
        except OSError:
            pass

    return result.ok(
        "audit.recent",
        {
            "calls": records,
            "count": len(records),
            "log_path": str(_AUDIT_FILE),
        },
    )
