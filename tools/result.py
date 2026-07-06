import json
from typing import Any


def ok(action: str, data: Any) -> str:
    return json.dumps(
        {
            "ok": True,
            "action": action,
            "data": data,
            "error": None,
        },
        indent=2,
        sort_keys=True,
    )


def error(
    action: str,
    message: str,
    code: str = "tool_error",
    permission_required: str | None = None,
) -> str:
    payload = {
        "message": message,
        "code": code,
    }
    if permission_required:
        payload["permission_required"] = permission_required
    return json.dumps(
        {
            "ok": False,
            "action": action,
            "data": None,
            "error": payload,
        },
        indent=2,
        sort_keys=True,
    )
