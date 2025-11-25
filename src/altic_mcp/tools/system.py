import subprocess
from .constants import SCRIPTS_PREFIX


def decrease_brightness(amount: float) -> str:
    script_path = SCRIPTS_PREFIX / "decrease-brightness.applescript"

    try:
        result = subprocess.run(
            ["osascript", script_path, str(amount)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to decrease brightness: {result.stderr}"

        return (
            result.stdout.strip()
            if result.stdout
            else "Brightness decreased successfully"
        )
    except Exception as e:
        return f"Error: Failed to decrease brightness: {str(e)}"


def increase_brightness(amount: float) -> str:
    script_path = SCRIPTS_PREFIX / "increase-brightness.applescript"

    try:
        result = subprocess.run(
            ["osascript", script_path, str(amount)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to increase brightness: {result.stderr}"

        return (
            result.stdout.strip()
            if result.stdout
            else "Brightness increased successfully"
        )
    except Exception as e:
        return f"Error: Failed to increase brightness: {str(e)}"


def turn_up_volume(amount: float) -> str:
    script_path = SCRIPTS_PREFIX / "turn-up-volume.applescript"

    try:
        result = subprocess.run(
            ["osascript", script_path, str(amount)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to turn up volume: {result.stderr}"

        return (
            result.stdout.strip() if result.stdout else "Volume increased successfully"
        )
    except Exception as e:
        return f"Error: Failed to turn up volume: {str(e)}"


def turn_down_volume(amount: float) -> str:
    script_path = SCRIPTS_PREFIX / "turn-down-volume.applescript"

    try:
        result = subprocess.run(
            ["osascript", script_path, str(amount)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"Error: Unable to turn down volume: {result.stderr}"

        return (
            result.stdout.strip() if result.stdout else "Volume decreased successfully"
        )
    except Exception as e:
        return f"Error: Failed to turn down volume: {str(e)}"
