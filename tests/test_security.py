
import json
import subprocess

import pytest

from tools import config, files, security


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    config.reset_cache()
    monkeypatch.setattr(config, "_CONFIG_DIR", tmp_path / "cfg")
    monkeypatch.setattr(config, "_CONFIG_FILE", tmp_path / "cfg" / "config.json")
    monkeypatch.delenv("ALLOWED_DIRECTORIES", raising=False)
    config.reset_cache()
    yield
    config.reset_cache()


def test_validate_path_allows_anything_when_no_allowlist(tmp_path):
    target = tmp_path / "file.txt"
    target.write_text("x")

    resolved = security.validate_path(str(target))

    assert resolved == target.resolve()


def test_validate_path_rejects_path_outside_allowlist(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside" / "secret.txt"

    monkeypatch.setenv("ALLOWED_DIRECTORIES", str(allowed))

    with pytest.raises(PermissionError):
        security.validate_path(str(outside))


def test_validate_path_allows_path_inside_allowlist(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    (allowed / "sub").mkdir(parents=True)
    target = allowed / "sub" / "file.txt"
    target.write_text("x")

    monkeypatch.setenv("ALLOWED_DIRECTORIES", str(allowed))

    resolved = security.validate_path(str(target))
    assert resolved == target.resolve()


def test_validate_path_resolves_symlink_escape(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside" / "secret.txt"
    outside.parent.mkdir()
    outside.write_text("secret")

    link = allowed / "escape"
    link.symlink_to(outside)

    monkeypatch.setenv("ALLOWED_DIRECTORIES", str(allowed))

    with pytest.raises(PermissionError):
        security.validate_path(str(link))


def test_validate_path_rejects_empty():
    with pytest.raises(ValueError):
        security.validate_path("")


def test_get_allowed_directories_from_config(tmp_path, monkeypatch):
    allowed = tmp_path / "projects"
    allowed.mkdir()
    config.set_config_value("allowed_directories", [str(allowed)])

    roots = security.get_allowed_directories()
    assert len(roots) == 1
    assert roots[0] == allowed.resolve()


def test_get_allowed_directories_env_overrides_config(tmp_path, monkeypatch):
    env_dir = tmp_path / "env-dir"
    env_dir.mkdir()
    config_dir = tmp_path / "config-dir"
    config_dir.mkdir()

    config.set_config_value("allowed_directories", [str(config_dir)])
    monkeypatch.setenv("ALLOWED_DIRECTORIES", str(env_dir))

    roots = security.get_allowed_directories()
    assert roots == [env_dir.resolve()]


def test_finder_selection_omits_paths_outside_allowlist(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside.txt"
    allowed.mkdir()
    inside = allowed / "inside.txt"
    inside.write_text("inside")
    outside.write_text("outside")
    monkeypatch.setenv("ALLOWED_DIRECTORIES", str(allowed))
    monkeypatch.setattr(
        files.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=f"{inside}\n{outside}\n",
            stderr="",
        ),
    )

    payload = json.loads(files.get_finder_selection())

    assert [item["path"] for item in payload["items"]] == [str(inside.resolve())]
