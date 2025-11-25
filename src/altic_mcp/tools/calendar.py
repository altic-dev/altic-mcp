import subprocess
from datetime import datetime
from typing import Tuple
from .constants import SCRIPTS_PREFIX


def validate_datetime_format(datetime_str: str) -> Tuple[bool, str]:
    try:
        datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        return True, ""
    except ValueError:
        return (
            False,
            "DateTime must be in format 'YYYY-MM-DD HH:MM' (e.g., '2025-10-30 14:30')",
        )


def validate_date_format(date_str: str) -> Tuple[bool, str]:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, ""
    except ValueError:
        return (
            False,
            "Date must be in format 'YYYY-MM-DD' (e.g., '2025-10-30')",
        )


def create_calendar_event(
    title: str, start_datetime: str, duration_minutes: int, calendar_name: str = ""
) -> str:
    script_path = SCRIPTS_PREFIX / "create-calendar-event.applescript"

    is_valid, error_msg = validate_datetime_format(start_datetime)
    if not is_valid:
        return f"Error: {error_msg}"

    if duration_minutes <= 0:
        return "Error: Duration must be greater than 0 minutes"

    try:
        args = ["osascript", script_path, title, start_datetime, str(duration_minutes)]
        if calendar_name:
            args.append(calendar_name)

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            return f"Error: Unable to create calendar event: {result.stderr}"

        return "Successfully created calendar event"
    except Exception as e:
        return f"Error: Failed to create calendar event: {str(e)}"


def list_calendar_events_for_day(date: str) -> str:
    """
    List all calendar events for a specific day.

    Args:
        date: Date in format 'YYYY-MM-DD'

    Returns:
        List of events or error message
    """
    script_path = SCRIPTS_PREFIX / "list-all-calendar-events-for-day.applescript"

    is_valid, error_msg = validate_date_format(date)
    if not is_valid:
        return f"Error: {error_msg}"

    try:
        result = subprocess.run(
            ["osascript", script_path, date],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            return f"Error: Unable to list calendar events: {result.stderr}"

        return result.stdout.strip()
    except Exception as e:
        return f"Error: Failed to list calendar events: {str(e)}"
