"""Unit tests for scripts/ci_failure_alerts.py (no network)."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import pathlib
import urllib.error

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "ci_failure_alerts.py"
spec = importlib.util.spec_from_file_location("ci_failure_alerts", SCRIPT)
assert spec and spec.loader
alerts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alerts)

NOW = dt.datetime(2026, 11, 2, 9, 0, tzinfo=dt.UTC)


def _run(run_id: int, event: str = "push", actor: str = "chrysa") -> dict:
    return {
        "id": run_id,
        "name": "CI",
        "event": event,
        "actor": {"login": actor},
        "head_branch": "main",
        "html_url": f"https://github.com/chrysa/x/actions/runs/{run_id}",
        "created_at": f"2026-11-02T08:{run_id % 60:02d}:00Z",
    }


def fake_github(repos: list[dict], runs: dict[str, list[dict]], user: str | None = None):
    def get(path: str) -> object:
        if path == "/user":
            if user is None:
                raise urllib.error.HTTPError(path, 403, "forbidden", {}, None)  # type: ignore[arg-type]
            return {"login": user}
        if "/repos?" in path:
            return repos if path.endswith("page=1") else []
        repo = path.split("/repos/")[1].split("/actions")[0]
        return {"workflow_runs": runs.get(repo, [])}

    return get


def test_public_listing_without_user_scope_skips_archived_and_foreign() -> None:
    repos = [
        {"full_name": "chrysa/a", "archived": False, "owner": {"login": "chrysa"}},
        {"full_name": "chrysa/b", "archived": True, "owner": {"login": "chrysa"}},
        {"full_name": "other/c", "archived": False, "owner": {"login": "other"}},
    ]
    assert alerts.list_repositories(fake_github(repos, {}), "chrysa") == ["chrysa/a"]


def test_failed_runs_exclude_pull_requests_and_dependabot() -> None:
    runs = {"chrysa/a": [_run(1), _run(2, event="pull_request"), _run(3, actor="dependabot[bot]")]}
    found = alerts.failed_runs(fake_github([], runs), "chrysa/a", "main", NOW)
    assert [r["id"] for r in found] == [1]


def test_collect_skips_already_sent_runs() -> None:
    repos = [{"full_name": "chrysa/a", "archived": False, "owner": {"login": "chrysa"}}]
    runs = {"chrysa/a": [_run(1), _run(2)]}
    new = alerts.collect(fake_github(repos, runs), "chrysa", ["main"], NOW, {"1": NOW.isoformat()})
    assert [run["id"] for _, run in new] == [2]


def test_state_drops_old_entries(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "state.json"
    old = (NOW - dt.timedelta(days=8)).isoformat()
    path.write_text(json.dumps({"sent": {"1": old, "2": NOW.isoformat()}}), encoding="utf-8")
    assert alerts.load_state(path, NOW) == {"2": NOW.isoformat()}


def test_state_missing_or_corrupt_is_empty(tmp_path: pathlib.Path) -> None:
    assert alerts.load_state(tmp_path / "absent.json", NOW) == {}
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    assert alerts.load_state(bad, NOW) == {}


def test_messages_are_chunked() -> None:
    lines = [f"l{i}" for i in range(23)]
    assert [len(part) for part in alerts.chunk(lines)] == [10, 10, 3]


def test_missing_webhook_posts_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GH_TOKEN", "x")
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("DRY_RUN", raising=False)
    assert alerts.main() == 0
