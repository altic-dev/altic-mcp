import json
import subprocess
import tempfile
import time
from pathlib import Path

from .constants import SCRIPTS_PREFIX


DEFAULT_VISUAL_PROMPT = (
    "Summarize the visible screen content and call out actionable UI text."
)


def _error(message: str) -> str:
    return f"Error: {message}"


def _json(payload: dict[str, object]) -> str:
    return json.dumps(payload)


def _script_path() -> str:
    return str(SCRIPTS_PREFIX / "extract-screen-text.swift")


def _default_output_path() -> str:
    timestamp = int(time.time())
    shots_dir = Path(tempfile.gettempdir()) / "altic-mcp-screen-text"
    shots_dir.mkdir(parents=True, exist_ok=True)
    return str(shots_dir / f"active-screen-{timestamp}.png")


def extract_screen_text(
    output_path: str = "",
    max_chars: int = 20000,
    include_visual_summary: bool = False,
    visual_prompt: str = DEFAULT_VISUAL_PROMPT,
) -> str:
    """
    Capture the active display and extract visible screen text with macOS Vision.
    Optionally ask macOS 27 Foundation Models for a visual summary.
    """
    try:
        if max_chars < 1:
            return _error("max_chars must be at least 1")

        target_path = output_path.strip() or _default_output_path()
        target = Path(target_path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)

        prompt = visual_prompt if visual_prompt else DEFAULT_VISUAL_PROMPT
        result = subprocess.run(
            [
                "swift",
                _script_path(),
                str(target),
                "true" if include_visual_summary else "false",
                prompt,
            ],
            capture_output=True,
            text=True,
            timeout=90,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return _error(f"Unable to extract screen text: {error_msg}")

        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            return _error(f"invalid screen text response: {result.stdout.strip()}")

        text = str(payload.get("text", ""))
        returned_text = text[:max_chars]
        truncated = len(returned_text) < len(text) or bool(payload.get("truncated", False))

        normalized: dict[str, object] = {
            "action": "extract_screen_text",
            "screenshot_path": str(payload.get("screenshot_path", str(target))),
            "text": returned_text,
            "length_chars": len(text),
            "returned_length_chars": len(returned_text),
            "truncated": truncated,
            "line_count": int(payload.get("line_count", 0) or 0),
            "average_confidence": float(payload.get("average_confidence", 0) or 0),
        }

        for key in (
            "visual_summary",
            "visual_model_available",
            "visual_model_source",
            "visual_prompt",
            "visual_error",
        ):
            if key in payload:
                normalized[key] = payload[key]

        return _json(normalized)
    except subprocess.TimeoutExpired:
        return _error("extract screen text timed out")
    except Exception as exc:
        return _error(f"Failed to extract screen text: {exc}")
