import subprocess
import tempfile
import time
from pathlib import Path

from fastmcp.utilities.types import Image

from . import security
from .constants import SCRIPTS_PREFIX


def capture_active_screen(output_path: str = "") -> str | list[object]:
    script_path = SCRIPTS_PREFIX / "capture-active-screen.swift"

    try:
        target_path = output_path.strip()
        if not target_path:
            timestamp = int(time.time())
            shots_dir = Path(tempfile.gettempdir()) / "altic-mcp-screenshots"
            shots_dir.mkdir(parents=True, exist_ok=True)
            target_path = str(shots_dir / f"active-screen-{timestamp}.png")

        target = security.validate_path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            ["swift", str(script_path), str(target)],
            capture_output=True,
            text=True,
            timeout=45,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return f"Error: Unable to capture active screen: {error_msg}"

        saved_path = result.stdout.strip() or str(target)
        if not Path(saved_path).exists():
            return f"Error: Screenshot file was not created: {saved_path}"

        return [f"Captured active screen: {saved_path}", Image(path=saved_path)]
    except Exception as e:
        return f"Error: Failed to capture active screen: {str(e)}"
