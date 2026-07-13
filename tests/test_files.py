import json
import subprocess
from pathlib import Path

from tools import files


def read_json(value: str):
    assert not value.startswith("Error:"), value
    return json.loads(value)


def test_get_file_info_returns_metadata(tmp_path):
    target = tmp_path / "report.txt"
    target.write_text("hello", encoding="utf-8")

    info = read_json(files.get_file_info(str(target)))

    assert info["path"] == str(target.resolve())
    assert info["exists"] is True
    assert info["is_file"] is True
    assert info["is_dir"] is False
    assert info["size_bytes"] == 5
    assert info["extension"] == ".txt"
    assert info["parent"] == str(tmp_path.resolve())


def test_list_directory_excludes_hidden_and_limits_results(tmp_path):
    (tmp_path / ".secret").write_text("hidden", encoding="utf-8")
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")

    payload = read_json(files.list_directory(str(tmp_path), max_results=1))

    assert payload["path"] == str(tmp_path.resolve())
    assert payload["truncated"] is True
    assert [entry["name"] for entry in payload["entries"]] == ["a.txt"]


def test_find_files_name_backend_finds_matching_files(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "quarterly-report.md").write_text("report", encoding="utf-8")
    (tmp_path / ".hidden-report.md").write_text("hidden", encoding="utf-8")

    payload = read_json(
        files.find_files("report", root=str(tmp_path), kind="name", max_results=10)
    )

    assert payload["source"] == "name"
    assert [Path(item["path"]).name for item in payload["results"]] == [
        "quarterly-report.md"
    ]


def test_find_files_uses_configured_default_limit(tmp_path, monkeypatch):
    (tmp_path / "report-a.txt").write_text("a")
    (tmp_path / "report-b.txt").write_text("b")
    values = {"file_search_max_results": 1, "allowed_directories": []}
    monkeypatch.setattr(files.config, "get", values.__getitem__)

    payload = read_json(files.find_files("report", str(tmp_path), kind="name"))

    assert len(payload["results"]) == 1
    assert payload["truncated"] is True


def test_find_files_spotlight_backend_is_mockable(tmp_path, monkeypatch):
    target = tmp_path / "spotlight-report.txt"
    target.write_text("report", encoding="utf-8")

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0], returncode=0, stdout=f"{target}\n", stderr=""
        )

    monkeypatch.setattr(files.subprocess, "run", fake_run)

    payload = read_json(
        files.find_files("report", root=str(tmp_path), kind="spotlight", max_results=5)
    )

    assert payload["source"] == "spotlight"
    assert payload["results"][0]["path"] == str(target.resolve())


def test_find_files_auto_falls_back_to_name_search_when_spotlight_fails(
    tmp_path, monkeypatch
):
    target = tmp_path / "fallback-report.txt"
    target.write_text("report", encoding="utf-8")

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0], returncode=1, stdout="", stderr="index unavailable"
        )

    monkeypatch.setattr(files.subprocess, "run", fake_run)

    payload = read_json(
        files.find_files("report", root=str(tmp_path), kind="auto", max_results=5)
    )

    assert payload["source"] == "name"
    assert payload["results"][0]["path"] == str(target.resolve())


def test_copy_file_preserves_contents_and_blocks_collision(tmp_path):
    source = tmp_path / "source.txt"
    destination = tmp_path / "destination.txt"
    source.write_text("source body", encoding="utf-8")
    destination.write_text("existing", encoding="utf-8")

    error = files.copy_file(str(source), str(destination))

    assert error.startswith("Error:")
    assert destination.read_text(encoding="utf-8") == "existing"

    result = read_json(files.copy_file(str(source), str(destination), overwrite=True))
    assert result["action"] == "copy_file"
    assert result["overwritten"] is True
    assert destination.read_text(encoding="utf-8") == "source body"


def test_dry_run_copy_file_does_not_mutate(tmp_path):
    source = tmp_path / "source.txt"
    destination = tmp_path / "destination.txt"
    source.write_text("source body", encoding="utf-8")

    result = read_json(files.copy_file(str(source), str(destination), dry_run=True))

    assert result["dry_run"] is True
    assert result["would"] == "copy_file"
    assert not destination.exists()


def test_move_file_relocates_source(tmp_path):
    source = tmp_path / "old.txt"
    destination = tmp_path / "new.txt"
    source.write_text("body", encoding="utf-8")

    result = read_json(files.move_file(str(source), str(destination)))

    assert result["action"] == "move_file"
    assert not source.exists()
    assert destination.read_text(encoding="utf-8") == "body"


def test_rename_file_rejects_path_separators(tmp_path):
    source = tmp_path / "old.txt"
    source.write_text("body", encoding="utf-8")

    error = files.rename_file(str(source), "nested/new.txt")

    assert error.startswith("Error:")
    assert source.exists()


def test_rename_file_reports_rename_action(tmp_path):
    source = tmp_path / "old.txt"
    source.write_text("body", encoding="utf-8")

    result = read_json(files.rename_file(str(source), "new.txt"))

    assert result["action"] == "rename_file"
    assert not source.exists()
    assert (tmp_path / "new.txt").read_text(encoding="utf-8") == "body"


def test_copy_directory_handles_nested_files(tmp_path):
    source = tmp_path / "source-dir"
    nested = source / "nested"
    nested.mkdir(parents=True)
    (nested / "file.txt").write_text("nested body", encoding="utf-8")
    destination = tmp_path / "destination-dir"

    result = read_json(files.copy_directory(str(source), str(destination)))

    assert result["action"] == "copy_directory"
    assert (destination / "nested" / "file.txt").read_text(encoding="utf-8") == (
        "nested body"
    )


def test_trash_file_dry_run_does_not_call_subprocess(tmp_path, monkeypatch):
    target = tmp_path / "trash-me.txt"
    target.write_text("body", encoding="utf-8")

    def fail_run(*args, **kwargs):
        raise AssertionError("trash subprocess should not run during dry_run")

    monkeypatch.setattr(files.subprocess, "run", fail_run)

    result = read_json(files.trash_file(str(target), dry_run=True))

    assert result["dry_run"] is True
    assert target.exists()


def test_reveal_in_finder_uses_osascript(tmp_path, monkeypatch):
    target = tmp_path / "show-me.txt"
    target.write_text("body", encoding="utf-8")
    seen = {}

    def fake_run(args, **kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(files.subprocess, "run", fake_run)

    result = read_json(files.reveal_in_finder(str(target)))

    assert result["action"] == "reveal_in_finder"
    assert seen["args"][0] == "osascript"
    # Finder's `reveal` needs an alias/file reference; a bare `POSIX file`
    # specifier raises -1728 ("Can't get POSIX file ..."). Ensure we coerce.
    script = " ".join(seen["args"])
    assert "as alias" in script
    assert "reveal POSIX file (item 1 of argv)" not in script


def test_get_finder_selection_parses_alias_output(monkeypatch):
    selected = "/Users/example/Desktop/a.txt\n/Users/example/Desktop/b.txt\n"

    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess(
            args=args, returncode=0, stdout=selected, stderr=""
        )

    monkeypatch.setattr(files.subprocess, "run", fake_run)
    monkeypatch.setattr(files.Path, "exists", lambda self: True)

    payload = read_json(files.get_finder_selection())

    assert [Path(item["path"]).name for item in payload["items"]] == ["a.txt", "b.txt"]
