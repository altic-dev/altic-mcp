import json
import subprocess
import tempfile
import time
from pathlib import Path

from fastmcp.utilities.types import Image

from . import config, security
from .constants import SCRIPTS_PREFIX


def _json(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def _error(message: str) -> str:
    return f"Error: {message}"


def _clipboard_script() -> str:
    return str(SCRIPTS_PREFIX / "clipboard.swift")


def _run_swift(*args: str, timeout: int = 45) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["swift", _clipboard_script(), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _run_swift_json(action: str, *args: str) -> str:
    try:
        result = _run_swift(action, *args)
        if result.returncode != 0:
            return _error(result.stderr.strip() or f"clipboard {action} failed")
        try:
            return _json(json.loads(result.stdout or "{}"))
        except json.JSONDecodeError:
            return _error(f"clipboard {action} returned invalid JSON")
    except Exception as exc:
        return _error(f"failed to run clipboard {action}: {exc}")


def _resolve_existing_path(path: str, label: str = "path") -> Path:
    if not path or not path.strip():
        raise ValueError(f"{label} cannot be empty")
    resolved = security.validate_path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"{label} does not exist: {resolved}")
    return resolved


def get_clipboard_text(max_chars: int | None = None) -> str:
    """
    Read plain text from the macOS clipboard.
    """
    try:
        if max_chars is None:
            max_chars = config.get("clipboard_max_chars")
        max_chars = max(1, min(max_chars, 200000))
        result = subprocess.run(
            ["pbpaste"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return _error(result.stderr.strip() or "unable to read clipboard text")

        text = result.stdout
        truncated_text = text[:max_chars]
        return _json(
            {
                "action": "get_clipboard_text",
                "length_chars": len(text),
                "text": truncated_text,
                "truncated": len(text) > len(truncated_text),
            }
        )
    except Exception as exc:
        return _error(f"failed to get clipboard text: {exc}")


def set_clipboard_text(text: str) -> str:
    """
    Write plain text to the macOS clipboard.
    """
    try:
        result = subprocess.run(
            ["pbcopy"],
            input=text,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return _error(result.stderr.strip() or "unable to write clipboard text")
        return _json({"action": "set_clipboard_text", "length_chars": len(text)})
    except Exception as exc:
        return _error(f"failed to set clipboard text: {exc}")


def clear_clipboard() -> str:
    """
    Clear clipboard contents by replacing them with an empty text value.
    """
    try:
        result = subprocess.run(
            ["pbcopy"],
            input="",
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return _error(result.stderr.strip() or "unable to clear clipboard")
        return _json({"action": "clear_clipboard"})
    except Exception as exc:
        return _error(f"failed to clear clipboard: {exc}")


def get_clipboard_files() -> str:
    """
    Return file URLs currently available on the macOS clipboard.
    """
    return _run_swift_json("get-files")


def set_clipboard_files(paths: list[str]) -> str:
    """
    Put one or more filesystem paths on the macOS clipboard for Finder paste.
    """
    try:
        if not paths:
            return _error("paths cannot be empty")
        resolved_paths = [str(_resolve_existing_path(path)) for path in paths]
        return _run_swift_json("set-files", *resolved_paths)
    except Exception as exc:
        return _error(str(exc))


def save_clipboard_image(output_path: str = "") -> str | list[object]:
    """
    Save an image from the macOS clipboard to a PNG file and share it with the model.
    """
    try:
        target_path = output_path.strip()
        if not target_path:
            timestamp = int(time.time())
            clipboard_dir = Path(tempfile.gettempdir()) / "altic-mcp-clipboard"
            clipboard_dir.mkdir(parents=True, exist_ok=True)
            target_path = str(clipboard_dir / f"clipboard-image-{timestamp}.png")

        target = security.validate_path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        result = _run_swift("save-image", str(target))
        if result.returncode != 0:
            return _error(result.stderr.strip() or "unable to save clipboard image")

        saved_path = result.stdout.strip() or str(target)
        if not Path(saved_path).exists():
            return _error(f"clipboard image file was not created: {saved_path}")

        return [f"Saved clipboard image: {saved_path}", Image(path=saved_path)]
    except Exception as exc:
        return _error(f"failed to save clipboard image: {exc}")


def set_clipboard_image(path: str) -> str:
    """
    Put an image file on the macOS clipboard.
    """
    try:
        image_path = _resolve_existing_path(path, "image file")
        if not image_path.is_file():
            return _error(f"image file is not a file: {image_path}")
        return _run_swift_json("set-image", str(image_path))
    except Exception as exc:
        return _error(str(exc))
