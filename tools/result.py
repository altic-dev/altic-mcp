import json
from typing import Any

from .mcp_result import failure, success


def ok(action: str, data: Any) -> str:
    """Return compact JSON for legacy internal adapters.

    The MCP boundary converts this value to native structured content.
    """
    payload = success(data)
    payload["action"] = action
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def error(
    action: str,
    message: str,
    code: str = "tool_error",
    permission_required: str | None = None,
) -> str:
    """Return compact JSON for legacy internal adapters."""
    payload = failure(
        message,
        code=code,
        permission_required=permission_required,
    )
    payload["action"] = action
    return json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    )
