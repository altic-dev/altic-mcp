"""Path validation with allowlist enforcement and symlink traversal prevention.

Inspired by DesktopCommanderMCP's validatePath(): resolve symlinks in the full
path chain (including the parent directory for not-yet-existing paths) and
reject any resolved path that falls outside the configured allowed directories.

When no allowed directories are configured (the default), full filesystem
access is permitted — matching altic-mcp's original behaviour.
"""

import os
from pathlib import Path

from . import config


def get_allowed_directories() -> list[Path]:
    """Return resolved allowed-directory roots.

    Precedence: ALLOWED_DIRECTORIES env var (colon-separated) then the
    ``allowed_directories`` config key. An empty list means full filesystem
    access.
    """
    env_value = os.environ.get("ALLOWED_DIRECTORIES", "").strip()
    if env_value:
        raw = [p.strip() for p in env_value.split(":") if p.strip()]
    else:
        raw = config.get("allowed_directories") or []

    if not raw:
        return []

    roots: list[Path] = []
    for entry in raw:
        if isinstance(entry, str):
            roots.append(Path(entry).expanduser().resolve(strict=False))
    return roots


def _is_path_allowed(resolved: Path, allowed: list[Path]) -> bool:
    for root in allowed:
        try:
            resolved.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def validate_path(requested_path: str) -> Path:
    """Resolve and validate a user-supplied path.

    Symlinks in the path chain are resolved so that a symlink inside an
    allowed directory cannot escape to a location outside the allowlist.

    Raises:
        ValueError: if the path is empty.
        PermissionError: if the resolved path is outside allowed directories.

    Returns:
        The fully resolved ``Path``.
    """
    if not requested_path or not requested_path.strip():
        raise ValueError("path cannot be empty")

    raw = Path(requested_path).expanduser()

    # For existing paths, resolve() follows the entire symlink chain.
    # For non-existing paths, resolve the parent directory (which typically
    # exists) so symlinks embedded in the directory path are followed, then
    # re-attach the final component.
    if raw.exists():
        resolved = raw.resolve(strict=False)
    elif raw.parent.exists():
        resolved = raw.parent.resolve(strict=False) / raw.name
    else:
        resolved = raw.resolve(strict=False)

    allowed = get_allowed_directories()
    if allowed and not _is_path_allowed(resolved, allowed):
        raise PermissionError(
            f"path is outside allowed directories: {resolved}"
        )

    return resolved
