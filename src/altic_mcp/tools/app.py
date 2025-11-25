import subprocess
from .constants import SCRIPTS_PREFIX


def open_app(name: str) -> str:
    script_path = SCRIPTS_PREFIX / "open-application.applescript"
    result = subprocess.run(
        ["osascript", script_path, name], capture_output=True, text=True, timeout=10
    )

    if result.returncode != 0:
        return f"Unable to open app: {name}, error: {result.stderr}"

    return f"Successfully opened app: {name}"
