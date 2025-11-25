import subprocess
from datetime import datetime
from .constants import SCRIPTS_PREFIX


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
