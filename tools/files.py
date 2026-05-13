import json
import shutil
import subprocess
import time
from pathlib import Path


def _json(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def _error(message: str) -> str:
    return f"Error: {message}"


def _resolve(path: str) -> Path:
    if not path or not path.strip():
        raise ValueError("path cannot be empty")
    return Path(path).expanduser().resolve(strict=False)


def _is_hidden(path: Path, root: Path | None = None) -> bool:
    try:
        parts = path.relative_to(root).parts if root else path.parts
    except ValueError:
        parts = path.parts
    return any(part.startswith(".") for part in parts if part not in ("", "."))


def _metadata(path: Path, source: str | None = None) -> dict:
    resolved = path.expanduser().resolve(strict=False)
    exists = resolved.exists()
    try:
        stat = resolved.stat() if exists else None
    except OSError:
        stat = None

    payload = {
        "path": str(resolved),
        "name": resolved.name,
        "exists": exists,
        "is_file": resolved.is_file() if exists else False,
        "is_dir": resolved.is_dir() if exists else False,
        "is_symlink": resolved.is_symlink(),
        "size_bytes": stat.st_size if stat else None,
        "modified_at": stat.st_mtime if stat else None,
        "extension": resolved.suffix,
        "parent": str(resolved.parent),
    }
    if payload["is_symlink"]:
        try:
            payload["symlink_target"] = str(resolved.readlink())
        except OSError:
            payload["symlink_target"] = None
    if source:
        payload["source"] = source
    return payload


def _require_source(path: Path) -> str | None:
    if not path.exists():
        return f"source does not exist: {path}"
    return None


def _require_destination_parent(path: Path) -> str | None:
    if not path.parent.exists():
        return f"destination parent does not exist: {path.parent}"
    if not path.parent.is_dir():
        return f"destination parent is not a directory: {path.parent}"
    return None


def _conflict_error(destination: Path, overwrite: bool) -> str | None:
    if destination.exists() and not overwrite:
        return f"destination already exists: {destination}"
    return None


def _operation_payload(
    action: str,
    source: Path | None = None,
    destination: Path | None = None,
    dry_run: bool = False,
    overwrite: bool = False,
    overwritten: bool = False,
    would: str | None = None,
) -> dict:
    payload = {
        "action": action,
        "dry_run": dry_run,
    }
    if source is not None:
        payload["source"] = str(source)
    if destination is not None:
        payload["destination"] = str(destination)
    if would:
        payload["would"] = would
    payload["overwrite"] = overwrite
    payload["overwritten"] = overwritten
    return payload


def _name_search(
    query: str,
    root_path: Path,
    max_results: int,
    include_hidden: bool,
    source: str = "name",
) -> list[dict]:
    lowered = query.casefold()
    results: list[dict] = []
    for path in root_path.rglob("*"):
        if not include_hidden and _is_hidden(path, root_path):
            if path.is_dir():
                continue
            continue
        if lowered in path.name.casefold():
            results.append(_metadata(path, source=source))
            if len(results) >= max_results:
                break
    return results


def _spotlight_search(
    query: str,
    root_path: Path | None,
    max_results: int,
    include_hidden: bool,
) -> list[dict]:
    command = ["mdfind"]
    if root_path:
        command.extend(["-onlyin", str(root_path)])
    command.append(query)

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "mdfind failed")

    results: list[dict] = []
    for line in result.stdout.splitlines():
        if len(results) >= max_results:
            break
        path = Path(line).expanduser().resolve(strict=False)
        if not path.exists():
            continue
        if not include_hidden and _is_hidden(path, root_path):
            continue
        results.append(_metadata(path, source="spotlight"))
    return results


def find_files(
    query: str,
    root: str = "",
    max_results: int = 25,
    include_hidden: bool = False,
    kind: str = "auto",
) -> str:
    if not query or not query.strip():
        return _error("query cannot be empty")
    if kind not in {"auto", "name", "spotlight"}:
        return _error("kind must be one of: auto, name, spotlight")
    max_results = max(1, min(max_results, 500))

    try:
        root_path = _resolve(root) if root.strip() else None
        if root_path and not root_path.is_dir():
            return _error(f"root is not a directory: {root_path}")

        if kind in {"auto", "spotlight"}:
            try:
                spotlight_results = _spotlight_search(
                    query=query,
                    root_path=root_path,
                    max_results=max_results,
                    include_hidden=include_hidden,
                )
                if kind == "spotlight" or spotlight_results:
                    return _json(
                        {
                            "query": query,
                            "root": str(root_path) if root_path else "",
                            "source": "spotlight",
                            "results": spotlight_results,
                            "truncated": len(spotlight_results) >= max_results,
                        }
                    )
            except Exception as exc:
                if kind == "spotlight":
                    return _error(f"spotlight search failed: {exc}")

        fallback_root = root_path or Path.home().resolve(strict=False)
        results = _name_search(
            query=query,
            root_path=fallback_root,
            max_results=max_results,
            include_hidden=include_hidden,
        )
        return _json(
            {
                "query": query,
                "root": str(fallback_root),
                "source": "name",
                "results": results,
                "truncated": len(results) >= max_results,
            }
        )
    except Exception as exc:
        return _error(f"failed to find files: {exc}")


def list_directory(
    path: str,
    include_hidden: bool = False,
    max_results: int = 200,
) -> str:
    try:
        target = _resolve(path)
        if not target.exists():
            return _error(f"path does not exist: {target}")
        if not target.is_dir():
            return _error(f"path is not a directory: {target}")

        max_results = max(1, min(max_results, 1000))
        entries = []
        for child in sorted(target.iterdir(), key=lambda item: item.name.casefold()):
            if not include_hidden and _is_hidden(child, target):
                continue
            entries.append(_metadata(child))
            if len(entries) >= max_results:
                break
        visible_count = sum(
            1
            for child in target.iterdir()
            if include_hidden or not _is_hidden(child, target)
        )
        return _json(
            {
                "path": str(target),
                "entries": entries,
                "truncated": visible_count > len(entries),
            }
        )
    except Exception as exc:
        return _error(f"failed to list directory: {exc}")


def get_file_info(path: str) -> str:
    try:
        return _json(_metadata(_resolve(path)))
    except Exception as exc:
        return _error(f"failed to get file info: {exc}")


def copy_file(
    source: str,
    destination: str,
    overwrite: bool = False,
    dry_run: bool = False,
) -> str:
    try:
        src = _resolve(source)
        dst = _resolve(destination)
        if error := _require_source(src):
            return _error(error)
        if not src.is_file():
            return _error(f"source is not a file: {src}")
        if error := _require_destination_parent(dst):
            return _error(error)
        if error := _conflict_error(dst, overwrite):
            return _error(error)

        overwritten = dst.exists()
        if dry_run:
            return _json(
                _operation_payload(
                    "copy_file",
                    src,
                    dst,
                    dry_run=True,
                    overwrite=overwrite,
                    overwritten=overwritten,
                    would="copy_file",
                )
            )

        shutil.copy2(src, dst)
        return _json(
            _operation_payload(
                "copy_file",
                src,
                dst,
                overwrite=overwrite,
                overwritten=overwritten,
            )
        )
    except Exception as exc:
        return _error(f"failed to copy file: {exc}")


def copy_directory(
    source: str,
    destination: str,
    overwrite: bool = False,
    dry_run: bool = False,
) -> str:
    try:
        src = _resolve(source)
        dst = _resolve(destination)
        if error := _require_source(src):
            return _error(error)
        if not src.is_dir():
            return _error(f"source is not a directory: {src}")
        if error := _require_destination_parent(dst):
            return _error(error)
        if error := _conflict_error(dst, overwrite):
            return _error(error)

        overwritten = dst.exists()
        if dry_run:
            return _json(
                _operation_payload(
                    "copy_directory",
                    src,
                    dst,
                    dry_run=True,
                    overwrite=overwrite,
                    overwritten=overwritten,
                    would="copy_directory",
                )
            )

        if overwritten:
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copytree(src, dst)
        return _json(
            _operation_payload(
                "copy_directory",
                src,
                dst,
                overwrite=overwrite,
                overwritten=overwritten,
            )
        )
    except Exception as exc:
        return _error(f"failed to copy directory: {exc}")


def move_file(
    source: str,
    destination: str,
    overwrite: bool = False,
    dry_run: bool = False,
) -> str:
    try:
        src = _resolve(source)
        dst = _resolve(destination)
        if error := _require_source(src):
            return _error(error)
        if error := _require_destination_parent(dst):
            return _error(error)
        if error := _conflict_error(dst, overwrite):
            return _error(error)

        overwritten = dst.exists()
        if dry_run:
            return _json(
                _operation_payload(
                    "move_file",
                    src,
                    dst,
                    dry_run=True,
                    overwrite=overwrite,
                    overwritten=overwritten,
                    would="move_file",
                )
            )

        if overwritten:
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        shutil.move(str(src), str(dst))
        return _json(
            _operation_payload(
                "move_file",
                src,
                dst,
                overwrite=overwrite,
                overwritten=overwritten,
            )
        )
    except Exception as exc:
        return _error(f"failed to move file: {exc}")


def rename_file(
    path: str,
    new_name: str,
    overwrite: bool = False,
    dry_run: bool = False,
) -> str:
    if not new_name or not new_name.strip():
        return _error("new_name cannot be empty")
    if Path(new_name).name != new_name:
        return _error("new_name must be a file name, not a path")
    try:
        src = _resolve(path)
        dst = src.parent / new_name
        result = move_file(str(src), str(dst), overwrite=overwrite, dry_run=dry_run)
        if result.startswith("Error:"):
            return result
        payload = json.loads(result)
        payload["action"] = "rename_file"
        if payload.get("would") == "move_file":
            payload["would"] = "rename_file"
        return _json(payload)
    except Exception as exc:
        return _error(f"failed to rename file: {exc}")


def trash_file(path: str, dry_run: bool = False) -> str:
    try:
        target = _resolve(path)
        if not target.exists():
            return _error(f"path does not exist: {target}")
        if dry_run:
            return _json(
                {
                    "action": "trash_file",
                    "dry_run": True,
                    "path": str(target),
                    "would": "trash_file",
                }
            )

        script = (
            'on run argv\n'
            '  tell application "Finder"\n'
            '    delete POSIX file (item 1 of argv)\n'
            "  end tell\n"
            "end run\n"
        )
        result = subprocess.run(
            ["osascript", "-e", script, str(target)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return _error(result.stderr.strip() or "unable to move item to Trash")
        return _json({"action": "trash_file", "dry_run": False, "path": str(target)})
    except Exception as exc:
        return _error(f"failed to trash file: {exc}")


def reveal_in_finder(path: str) -> str:
    try:
        target = _resolve(path)
        if not target.exists():
            return _error(f"path does not exist: {target}")
        script = (
            'on run argv\n'
            '  tell application "Finder"\n'
            '    reveal POSIX file (item 1 of argv)\n'
            "    activate\n"
            "  end tell\n"
            "end run\n"
        )
        result = subprocess.run(
            ["osascript", "-e", script, str(target)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return _error(result.stderr.strip() or "unable to reveal item in Finder")
        return _json({"action": "reveal_in_finder", "path": str(target)})
    except Exception as exc:
        return _error(f"failed to reveal in Finder: {exc}")


def get_finder_selection() -> str:
    script = (
        'tell application "Finder"\n'
        "  set selectedItems to selection\n"
        "  set output to {}\n"
        "  repeat with selectedItem in selectedItems\n"
        "    set end of output to POSIX path of (selectedItem as alias)\n"
        "  end repeat\n"
        "  set AppleScript's text item delimiters to linefeed\n"
        "  set joinedOutput to output as text\n"
        '  set AppleScript\'s text item delimiters to ""\n'
        "  return joinedOutput\n"
        "end tell\n"
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return _error(result.stderr.strip() or "unable to read Finder selection")

        items = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            items.append(_metadata(Path(line.strip())))
        return _json(
            {
                "action": "get_finder_selection",
                "captured_at": time.time(),
                "items": items,
            }
        )
    except Exception as exc:
        return _error(f"failed to get Finder selection: {exc}")
