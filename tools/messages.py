import subprocess

from . import applescript, result, security
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


def _run_manager(action: str, *args: str, timeout: int | None = None) -> str:
    return applescript.run_manager(
        "messages-manager.applescript",
        "messages",
        action,
        *args,
        timeout=timeout,
        permission_required="Automation access for Messages",
    )


def list_chats(limit: int = 50) -> str:
    limit = max(1, min(limit, 500))
    return _run_manager("list_chats", str(limit))


def send_file_message(
    recipient: str,
    path: str,
    message: str = "",
    recipient_type: str = "handle",
) -> str:
    if not recipient or not recipient.strip():
        return result.error(
            "messages.send_file",
            "recipient cannot be empty",
            code="validation_error",
        )
    if recipient_type not in {"handle", "chat"}:
        return result.error(
            "messages.send_file",
            "recipient_type must be one of: handle, chat",
            code="validation_error",
        )

    try:
        target = security.validate_path(path)
    except (ValueError, PermissionError) as exc:
        return result.error("messages.send_file", str(exc), code="validation_error")
    if not target.exists():
        return result.error(
            "messages.send_file",
            f"file does not exist: {target}",
            code="validation_error",
        )
    if not target.is_file():
        return result.error(
            "messages.send_file",
            f"path is not a file: {target}",
            code="validation_error",
        )

    return _run_manager(
        "send_file",
        recipient.strip(),
        str(target),
        message,
        recipient_type,
    )
