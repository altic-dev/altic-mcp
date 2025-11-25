import subprocess
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
