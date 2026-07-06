import json

from tools import result


def test_ok_wraps_action_and_data():
    payload = json.loads(result.ok("notes.get", {"title": "Plan"}))

    assert payload == {
        "ok": True,
        "action": "notes.get",
        "data": {"title": "Plan"},
        "error": None,
    }


def test_error_wraps_action_and_message_with_metadata():
    payload = json.loads(
        result.error(
            "calendar.delete",
            "multiple matching events",
            code="ambiguous_match",
            permission_required="Calendars",
        )
    )

    assert payload == {
        "ok": False,
        "action": "calendar.delete",
        "data": None,
        "error": {
            "message": "multiple matching events",
            "code": "ambiguous_match",
            "permission_required": "Calendars",
        },
    }
