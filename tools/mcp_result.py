"""Normalize legacy tool returns into compact, structured-only MCP results."""

from __future__ import annotations

import json
from typing import Any

from fastmcp.tools.tool import ToolResult


def success(data: Any, *, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": True, "data": data}
    if meta:
        payload["meta"] = meta
    return payload


def failure(
    message: str,
    *,
    code: str = "tool_error",
    permission_required: str | None = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if permission_required:
        error["permission_required"] = permission_required
    return {"ok": False, "error": error}


def _compact_file(item: Any) -> Any:
    if not isinstance(item, dict) or "path" not in item:
        return item
    compact = {"path": item["path"]}
    if item.get("is_dir"):
        compact["type"] = "directory"
    elif item.get("is_symlink"):
        compact["type"] = "symlink"
    else:
        compact["type"] = "file"
    for key in ("size_bytes", "modified_at"):
        if item.get(key) is not None:
            compact[key] = item[key]
    return compact


def _normalize_data(value: Any) -> tuple[Any, dict[str, Any]]:
    """Normalize common collection shapes and extract optional metadata."""
    if not isinstance(value, dict):
        return value, {}

    value = {key: item for key, item in value.items() if item is not None}
    meta: dict[str, Any] = {}
    for source, target in (("query", "query"), ("source", "backend"), ("root", "root")):
        if source in value and value[source] not in (None, ""):
            meta[target] = value.pop(source)

    collection_key = next(
        (key for key in ("results", "items", "calls", "entries") if isinstance(value.get(key), list)),
        None,
    )
    if collection_key:
        items = [_compact_file(item) for item in value.pop(collection_key)]
        has_more = bool(value.pop("truncated", False))
        if "exhausted" in value:
            has_more = not bool(value.pop("exhausted"))
        data: dict[str, Any] = {
            "items": items,
            "count": len(items),
            "has_more": has_more,
        }
        data.update(value)
        return data, meta

    return value, meta


def normalize_payload(value: Any) -> dict[str, Any]:
    """Convert a Python value or legacy JSON/text return to the public contract."""
    if isinstance(value, str):
        if value.startswith("Error:"):
            return failure(value.removeprefix("Error:").strip())
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return success({"value": value})

    if isinstance(value, dict) and "ok" in value:
        if value["ok"]:
            data, meta = _normalize_data(value.get("data"))
            return success(data, meta=meta)
        legacy_error = value.get("error") or {}
        if isinstance(legacy_error, str):
            return failure(legacy_error)
        return failure(
            legacy_error.get("message", "Tool failed"),
            code=legacy_error.get("code", "tool_error"),
            permission_required=legacy_error.get("permission_required"),
        )

    data, meta = _normalize_data(value)
    return success(data, meta=meta)


def structured_only(value: Any) -> ToolResult:
    """Build an MCP result with no duplicate text content."""
    return ToolResult(content=[], structured_content=normalize_payload(value))
