import json
import subprocess
import tempfile
import time
from pathlib import Path

from fastmcp.utilities.types import Image

from .constants import SCRIPTS_PREFIX


def _json(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def _error(message: str) -> str:
    return f"Error: {message}"


def _screen_text_script() -> str:
    return str(SCRIPTS_PREFIX / "extract-screen-text.swift")


def capture_active_screen(output_path: str = "") -> str | list[object]:
    script_path = SCRIPTS_PREFIX / "capture-active-screen.swift"

    try:
        target_path = output_path.strip()
        if not target_path:
            timestamp = int(time.time())
            shots_dir = Path(tempfile.gettempdir()) / "altic-mcp-screenshots"
            shots_dir.mkdir(parents=True, exist_ok=True)
            target_path = str(shots_dir / f"active-screen-{timestamp}.png")

        target = Path(target_path).expanduser().resolve()
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


def extract_screen_text(
    output_path: str = "",
    recognition_level: str = "accurate",
    languages: str = "",
    include_boxes: bool = True,
    max_chars: int = 20000,
    visual_understanding: str = "none",
) -> str:
    """
    Capture the active display and extract screen text with local Vision OCR.
    """
    valid_levels = {"accurate", "fast"}
    valid_visual_modes = {"none", "summary", "ui_map"}

    recognition_level = recognition_level.strip().lower()
    visual_understanding = visual_understanding.strip().lower()

    if recognition_level not in valid_levels:
        return _error(
            "recognition_level must be one of: accurate, fast"
        )
    if visual_understanding not in valid_visual_modes:
        return _error(
            "visual_understanding must be one of: none, summary, ui_map"
        )

    try:
        max_chars = max(1, min(max_chars, 200000))
        target_path = output_path.strip()
        if not target_path:
            timestamp = int(time.time())
            shots_dir = Path("/tmp") / "altic-mcp-screenshots"
            shots_dir.mkdir(parents=True, exist_ok=True)
            target_path = str(shots_dir / f"screen-text-{timestamp}.png")

        target = Path(target_path).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [
                "swift",
                _screen_text_script(),
                str(target),
                recognition_level,
                languages,
                str(include_boxes).lower(),
                visual_understanding,
            ],
            capture_output=True,
            text=True,
            timeout=90,
        )

        if result.returncode != 0:
            return _error(
                result.stderr.strip() or "unable to extract screen text"
            )

        try:
            payload = json.loads(result.stdout or "{}")
        except json.JSONDecodeError as exc:
            return _error(f"invalid screen text response: {exc}")

        text = str(payload.get("text", ""))
        truncated_text = text[:max_chars]
        payload["text"] = truncated_text
        payload["length_chars"] = len(text)
        payload["truncated"] = len(text) > len(truncated_text)

        return _json(payload)
    except Exception as exc:
        return _error(f"failed to extract screen text: {exc}")
