import subprocess

from . import applescript, result
from .constants import SCRIPTS_PREFIX


def create_note(title: str, body: str, folder: str) -> str:
    create_note_script_path = SCRIPTS_PREFIX / "create-note.applescript"

    try:
        cmd_args = ["osascript", create_note_script_path, title, body]
        if folder:
            cmd_args.append(folder)

        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return f"Successfully created note: {title}"
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return f"Error: failed to create note: {error_msg}"

    except subprocess.TimeoutExpired:
        return "Error: Failed to create note: Operation timed out"
    except Exception as e:
        return f"Error: Failed to create note: {str(e)}"


def search_notes(query: str, max_results: int) -> str:
    search_notes_script_path = SCRIPTS_PREFIX / "search-for-note.applescript"

    try:
        result = subprocess.run(
            [
                "osascript",
                search_notes_script_path,
                query,
                str(max_results),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return f"Error: failed to search notes: {error_msg}"

        return result.stdout
    except subprocess.TimeoutExpired:
        return "Error: Failed to search notes: Operation timed out"
    except Exception as e:
        return f"Error: Failed to search for notes matching '{query}': {str(e)}"


def _bool_arg(value: bool) -> str:
    return "true" if value else "false"


def _run_manager(action: str, *args: str, timeout: int | None = None) -> str:
    return applescript.run_manager(
        "notes-manager.applescript",
        "notes",
        action,
        *args,
        timeout=timeout,
        permission_required="Automation: Notes",
    )


def _validate_identifier(action: str, identifier: str) -> str | None:
    if not identifier or not identifier.strip():
        return result.error(
            action,
            "identifier cannot be empty",
            code="validation_error",
        )
    return None


def list_note_folders() -> str:
    return _run_manager("list_folders")


def list_notes(folder: str = "", max_results: int = 25) -> str:
    max_results = max(1, min(max_results, 200))
    return _run_manager("list", folder, str(max_results))


def get_note(identifier: str) -> str:
    validation = _validate_identifier("notes.get", identifier)
    if validation:
        return validation
    return _run_manager("get", identifier)


def append_to_note(identifier: str, body: str) -> str:
    validation = _validate_identifier("notes.append", identifier)
    if validation:
        return validation
    if not body:
        return result.error("notes.append", "body cannot be empty", "validation_error")
    return _run_manager("append", identifier, body)


def update_note(identifier: str, body: str) -> str:
    validation = _validate_identifier("notes.update", identifier)
    if validation:
        return validation
    return _run_manager("update", identifier, body)


def delete_note(identifier: str, dry_run: bool = True) -> str:
    validation = _validate_identifier("notes.delete", identifier)
    if validation:
        return validation
    return _run_manager("delete", identifier, _bool_arg(dry_run))


def move_note(identifier: str, folder: str) -> str:
    validation = _validate_identifier("notes.move", identifier)
    if validation:
        return validation
    if not folder or not folder.strip():
        return result.error("notes.move", "folder cannot be empty", "validation_error")
    return _run_manager("move", identifier, folder)
