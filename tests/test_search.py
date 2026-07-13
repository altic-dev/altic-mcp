import json
import subprocess
from pathlib import Path

import pytest

from tools import config, files


@pytest.fixture(autouse=True)
def _clear_search_sessions():
    files._search_sessions.clear()
    yield
    files._search_sessions.clear()


def read_json(value: str):
    assert not value.startswith("Error:"), value
    return json.loads(value)


def test_start_search_name_returns_session_and_first_batch(tmp_path):
    (tmp_path / "alpha.txt").write_text("a")
    (tmp_path / "beta.txt").write_text("b")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "alpha-report.md").write_text("r")

    payload = read_json(
        files.start_search("alpha", root=str(tmp_path), kind="name", max_results=10)
    )

    assert payload["source"] == "name"
    assert payload["search_id"] is not None
    assert payload["exhausted"] is True  # only 2 matches, under max_results
    names = sorted(Path(r["path"]).name for r in payload["results"])
    assert names == ["alpha-report.md", "alpha.txt"]


def test_start_search_spotlight_returns_no_session(tmp_path, monkeypatch):
    target = tmp_path / "spotlight-match.txt"
    target.write_text("x")

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0], returncode=0, stdout=f"{target}\n", stderr=""
        )

    monkeypatch.setattr(files.subprocess, "run", fake_run)

    payload = read_json(
        files.start_search("spotlight", root=str(tmp_path), kind="spotlight", max_results=5)
    )

    assert payload["search_id"] is None
    assert payload["source"] == "spotlight"
    assert payload["exhausted"] is True


def test_get_more_search_results_pages_name_session(tmp_path):
    for i in range(15):
        (tmp_path / f"match-{i:02d}.txt").write_text("x")

    batch1 = read_json(
        files.start_search("match", root=str(tmp_path), kind="name", max_results=5)
    )
    sid = batch1["search_id"]
    assert sid is not None
    assert len(batch1["results"]) == 5
    assert batch1["exhausted"] is False

    batch2 = read_json(files.get_more_search_results(sid, count=5))
    assert len(batch2["results"]) == 5
    assert batch2["exhausted"] is False

    batch3 = read_json(files.get_more_search_results(sid, count=5))
    assert len(batch3["results"]) == 5
    assert batch3["exhausted"] is True

    batch4 = read_json(files.get_more_search_results(sid, count=5))
    assert batch4["results"] == []
    assert batch4["exhausted"] is True


def test_get_more_search_results_rejects_unknown_id():
    error = files.get_more_search_results("nonexistent")
    assert error.startswith("Error:")


def test_stop_search_removes_session(tmp_path):
    for i in range(20):
        (tmp_path / f"keep-{i:02d}.txt").write_text("x")

    payload = read_json(
        files.start_search("keep", root=str(tmp_path), kind="name", max_results=2)
    )
    sid = payload["search_id"]

    stopped = read_json(files.stop_search(sid))
    assert stopped["stopped"] is True

    stopped_again = read_json(files.stop_search(sid))
    assert stopped_again["stopped"] is False


def test_list_searches_shows_active_sessions(tmp_path):
    for i in range(20):
        (tmp_path / f"item-{i:02d}.txt").write_text("x")

    files.start_search("item", root=str(tmp_path), kind="name", max_results=2)

    payload = read_json(files.list_searches())
    assert payload["count"] == 1
    assert payload["searches"][0]["query"] == "item"


def test_start_search_rejects_empty_query():
    error = files.start_search("")
    assert error.startswith("Error:")


def test_start_search_respects_include_hidden(tmp_path):
    (tmp_path / ".hidden-match.txt").write_text("h")
    (tmp_path / "visible-match.txt").write_text("v")

    payload = read_json(
        files.start_search(
            "match", root=str(tmp_path), kind="name", max_results=10, include_hidden=True
        )
    )
    names = sorted(Path(r["path"]).name for r in payload["results"])
    assert names == [".hidden-match.txt", "visible-match.txt"]

    payload_hidden_off = read_json(
        files.start_search(
            "match", root=str(tmp_path), kind="name", max_results=10, include_hidden=False
        )
    )
    names = [Path(r["path"]).name for r in payload_hidden_off["results"]]
    assert names == ["visible-match.txt"]


def test_start_search_without_root_stays_inside_allowlist(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    (allowed / "match-allowed.txt").write_text("a")
    (outside / "match-outside.txt").write_text("b")
    monkeypatch.setenv("ALLOWED_DIRECTORIES", str(allowed))

    payload = read_json(files.start_search("match", kind="name", max_results=10))

    assert [Path(item["path"]).name for item in payload["results"]] == [
        "match-allowed.txt"
    ]


def test_start_search_uses_configured_default_limit(tmp_path, monkeypatch):
    (tmp_path / "match-a.txt").write_text("a")
    (tmp_path / "match-b.txt").write_text("b")
    values = {
        "file_search_max_results": 1,
        "include_hidden_default": False,
        "search_visit_limit": 50000,
        "allowed_directories": [],
    }
    monkeypatch.setattr(config, "get", values.__getitem__)

    payload = read_json(files.start_search("match", str(tmp_path), kind="name"))

    assert len(payload["results"]) == 1
