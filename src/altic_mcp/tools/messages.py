import subprocess
from typing import List
from .constants import SCRIPTS_PREFIX


def send_message(phone_number: str, message: str) -> str:
    send_message_script_path = SCRIPTS_PREFIX / "send-message.applescript"

    try:
        result = subprocess.run(
            ["osascript", send_message_script_path, phone_number, message],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return f"Successfully sent the message to {phone_number}"
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return f"Error: failed to send message: {error_msg}"

    except subprocess.TimeoutExpired:
        return "Error: Failed to send message: Operation timed out"
    except Exception as e:
        return f"Error: Failed to send message: {str(e)}"


def read_recent_messages(phone_number: str, recent_message_count: int = 50) -> str:
    read_recent_messages_script = SCRIPTS_PREFIX / "read-recent-messages.applescript"

    try:
        result = subprocess.run(
            [
                "osascript",
                read_recent_messages_script,
                phone_number,
                str(recent_message_count),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return f"Error: failed to read recent messages: {error_msg}"

        return result.stdout
    except Exception as e:
        return f"Error: Failed to retrieve recent {recent_message_count} messages from number: {phone_number}, {str(e)}"
