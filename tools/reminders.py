import json
import subprocess
from datetime import datetime
from .constants import SCRIPTS_PREFIX
from . import result


def validate_time_format(time: str) -> tuple[bool, str]:
    """
    Validate that time is in the format 'YYYY-MM-DD HH:MM'.
    Returns (is_valid, error_message).
    """
    try:
        datetime.strptime(time, "%Y-%m-%d %H:%M")
        return True, ""
    except ValueError:
        return (
            False,
            "Time must be in format 'YYYY-MM-DD HH:MM' (e.g., '2025-10-27 14:30')",
        )


def set_reminder(name: str, time: str, list_name: str) -> str:
    script_path = SCRIPTS_PREFIX / "set-reminder.applescript"

    is_valid, error_msg = validate_time_format(time)
    if not is_valid:
        return f"Error: {error_msg}"

    try:
        result = subprocess.run(
            ["osascript", script_path, name, time, list_name],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            return f"Error: Unable to set reminder: {result.stderr}"

        return "Successfully set reminder"
    except Exception as e:
        return f"Error: Failed to set reminder: {str(e)}"


def _bool_arg(value: bool) -> str:
    return "true" if value else "false"


def _run_manager(action: str, *args: str, timeout: int = 60) -> str:
    script_path = SCRIPTS_PREFIX / "reminders-manager.applescript"
    tool_action = f"reminders.{action}"

    try:
        completed = subprocess.run(
            ["osascript", script_path, action, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if completed.returncode != 0:
            error_msg = completed.stderr.strip() or "Unknown error"
            return result.error(
                tool_action,
                error_msg,
                permission_required="Reminders",
            )

        stdout = completed.stdout.strip()
        data = {} if not stdout else json.loads(stdout)
        return result.ok(tool_action, data)
    except subprocess.TimeoutExpired:
        return result.error(tool_action, "Operation timed out", code="timeout")
    except Exception as exc:
        return result.error(tool_action, str(exc))


def _validate_identifier(action: str, identifier: str) -> str | None:
    if not identifier or not identifier.strip():
        return result.error(
            action,
            "identifier cannot be empty",
            code="validation_error",
        )
    return None


def list_reminder_lists() -> str:
    return _run_manager("list_lists")


def list_reminders(list_name: str = "", include_completed: bool = False) -> str:
    return _run_manager("list", list_name, _bool_arg(include_completed))


def search_reminders(
    query: str,
    list_name: str = "",
    include_completed: bool = False,
) -> str:
    if not query or not query.strip():
        return result.error(
            "reminders.search",
            "query cannot be empty",
            code="validation_error",
        )
    return _run_manager("search", query, list_name, _bool_arg(include_completed))


def complete_reminder(identifier: str, list_name: str = "") -> str:
    validation = _validate_identifier("reminders.complete", identifier)
    if validation:
        return validation
    return _run_manager("complete", identifier, list_name)


def delete_reminder(
    identifier: str,
    list_name: str = "",
    dry_run: bool = True,
) -> str:
    validation = _validate_identifier("reminders.delete", identifier)
    if validation:
        return validation
    return _run_manager("delete", identifier, list_name, _bool_arg(dry_run))


def reschedule_reminder(identifier: str, datetime: str, list_name: str = "") -> str:
    validation = _validate_identifier("reminders.reschedule", identifier)
    if validation:
        return validation

    is_valid, error_msg = validate_time_format(datetime)
    if not is_valid:
        return result.error(
            "reminders.reschedule",
            error_msg,
            code="validation_error",
        )
    return _run_manager("reschedule", identifier, datetime, list_name)


def update_reminder(
    identifier: str,
    list_name: str = "",
    name: str = "",
    body: str = "",
    datetime: str = "",
    completed: bool | None = None,
    priority: int | None = None,
    flagged: bool | None = None,
) -> str:
    validation = _validate_identifier("reminders.update", identifier)
    if validation:
        return validation

    if datetime:
        is_valid, error_msg = validate_time_format(datetime)
        if not is_valid:
            return result.error("reminders.update", error_msg, code="validation_error")

    if priority is not None and not 0 <= priority <= 9:
        return result.error(
            "reminders.update",
            "priority must be between 0 and 9",
            code="validation_error",
        )

    completed_arg = "" if completed is None else _bool_arg(completed)
    priority_arg = "" if priority is None else str(priority)
    flagged_arg = "" if flagged is None else _bool_arg(flagged)

    return _run_manager(
        "update",
        identifier,
        list_name,
        name,
        body,
        datetime,
        completed_arg,
        priority_arg,
        flagged_arg,
    )


def show_reminder(identifier: str, list_name: str = "") -> str:
    validation = _validate_identifier("reminders.show", identifier)
    if validation:
        return validation
    return _run_manager("show", identifier, list_name)
