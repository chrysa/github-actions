"""End-to-end runs of ``shortcut_sync.entrypoint.main`` over a fake HTTP transport."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import pytest

from shortcut_sync.entrypoint import main

if TYPE_CHECKING:
    from tests.conftest import FakeHttp

SC = "https://api.app.shortcut.com/api/v3"
REPO = "https://api.github.com/repos/chrysa/alpha"
ISSUES = f"{REPO}/issues?state=open&per_page=100&page=1"
SONAR = "https://sonarcloud.io/api/qualitygates/project_status?projectKey=chrysa_alpha"
DASHBOARD = "https://sonarcloud.io/dashboard?id=chrysa_alpha"
APPLY = {
    "SHORTCUT_API_TOKEN": "test-shortcut-token",
    "SYNC_GITHUB_TOKEN": "test-github-token",
    "SYNC_DRY_RUN": "false",
}
DRY_RUN = {**APPLY, "SYNC_DRY_RUN": "true"}
WORKFLOWS = [
    {
        "id": 1,
        "default_state_id": 10,
        "states": [
            {"id": 10, "type": "unstarted", "position": 1},
            {"id": 11, "type": "started", "position": 2},
            {"id": 12, "type": "done", "position": 3},
        ],
    }
]
EPICS = [
    {"id": 100, "external_id": "chrysa/alpha", "archived": False},
    {"id": 101, "external_id": None, "archived": False},
    {"id": 102, "external_id": "someone-else/alpha", "archived": False},
    {"id": 103, "external_id": "chrysa/old", "archived": True},
]


def issue(number: int, *, labels: Sequence[str] = (), body: str = "", comments: int = 0) -> dict[str, object]:
    return {
        "number": number,
        "title": f"Confidential title {number}",
        "body": body,
        "html_url": f"https://github.com/chrysa/alpha/issues/{number}",
        "state": "open",
        "comments": comments,
        "labels": [{"name": label} for label in labels],
    }


def story(
    story_id: int, *, state: int = 10, links: Sequence[str] = (), marker: str | None = None
) -> dict[str, object]:
    return {
        "id": story_id,
        "app_url": f"https://app.shortcut.com/chrysa/story/{story_id}",
        "archived": False,
        "external_id": marker,
        "external_links": list(links),
        "workflow_id": 1,
        "workflow_state_id": state,
    }


def build_world(
    fake: FakeHttp,
    *,
    issues: Sequence[dict[str, object]] = (),
    stories: Sequence[dict[str, object]] = (),
    gate: str | None = "ERROR",
    health: str = "On Track",
) -> None:
    fake.add("GET", f"{SC}/workflows", WORKFLOWS)
    fake.add("GET", f"{SC}/epics?includes_description=false", EPICS)
    fake.add("GET", f"{SC}/epics/100/stories?includes_description=false", list(stories))
    fake.add("GET", REPO, {"archived": False, "has_issues": True})
    fake.add("GET", ISSUES, list(issues))
    if gate is None:
        fake.add("GET", SONAR, {"errors": []}, status=404)
    else:
        fake.add("GET", SONAR, {"projectStatus": {"status": gate}})
    fake.add("GET", f"{SC}/epics/100/health", {"status": health})
    fake.add("POST", f"{SC}/epics/100/health", {"status": "set"})


def full_world(fake: FakeHttp) -> None:
    """Six issues: two to import (1 bug via `sentry`, 6 feature), the others already linked."""
    build_world(
        fake,
        issues=[
            issue(1, labels=["sentry"]),
            issue(2, body="tracked in sc-42"),
            {**issue(3), "pull_request": {"url": "x"}},
            issue(4, comments=1),
            issue(5),
            issue(6, comments=1),
        ],
        stories=[story(70, state=11, links=["https://github.com/chrysa/alpha/issues/5"])],
    )
    fake.add(
        "GET",
        f"{REPO}/issues/4/comments?per_page=100&page=1",
        [{"body": "https://app.shortcut.com/chrysa/story/77"}],
    )
    fake.add("GET", f"{REPO}/issues/6/comments?per_page=100&page=1", [{"body": "unrelated"}])
    for story_id in (501, 502, 503):
        fake.add(
            "POST",
            f"{SC}/stories",
            {"id": story_id, "app_url": f"https://app.shortcut.com/chrysa/story/{story_id}"},
        )
    fake.add("POST", f"{REPO}/issues/1/comments", {"id": 1})
    fake.add("POST", f"{REPO}/issues/6/comments", {"id": 2})


def writes(fake: FakeHttp) -> list[tuple[str, str]]:
    return [(call.method, call.url) for call in fake.writes()]


def counters(output: str) -> dict[str, str]:
    pairs = (line.split(": ", 1) for line in output.splitlines() if ": " in line)
    return dict(pairs)


def test_apply_run_imports_rates_and_comments(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    full_world(fake_http)

    assert main(APPLY) == 0

    assert writes(fake_http) == [
        ("POST", f"{SC}/epics/100/health"),
        ("POST", f"{SC}/stories"),
        ("POST", f"{SC}/stories"),
        ("POST", f"{REPO}/issues/1/comments"),
        ("POST", f"{SC}/stories"),
        ("POST", f"{REPO}/issues/6/comments"),
    ]
    health, quality, bug, comment, feature, _ = (call.body for call in fake_http.writes())
    assert health == {"status": "At Risk", "text": "SonarCloud quality gate failing (daily Shortcut sync)."}
    assert quality["name"] == "SonarCloud quality gate failing"
    assert quality["story_type"] == "chore"
    assert quality["external_links"] == [DASHBOARD]
    assert bug["name"] == "Confidential title 1"
    assert bug["story_type"] == "bug"
    assert bug["epic_id"] == 100
    assert bug["workflow_state_id"] == 10
    assert bug["external_links"] == ["https://github.com/chrysa/alpha/issues/1"]
    assert bug["external_id"] == "chrysa/alpha#1"
    assert feature["story_type"] == "feature"
    assert comment == {"body": "Shortcut: sc-502 https://app.shortcut.com/chrysa/story/502"}
    assert all("labels" not in body and "label_ids" not in body for body in (quality, bug, feature))

    output = capsys.readouterr().out
    assert counters(output)["stories_created_from_issues"] == "2"
    assert counters(output)["issues_already_linked"] == "3"
    assert counters(output)["issues_open"] == "5"
    assert counters(output)["quality_stories_created"] == "1"
    for secret in ("alpha", "Confidential", "test-shortcut-token", "test-github-token"):
        assert secret not in output


def test_dry_run_reads_only_and_reports_planned_counts(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    full_world(fake_http)

    assert main(DRY_RUN) == 0

    assert writes(fake_http) == []
    output = capsys.readouterr().out
    assert "mode: dry-run" in output
    assert counters(output)["stories_created_from_issues"] == "2"
    assert counters(output)["issue_comments_posted"] == "2"
    assert counters(output)["epic_health_updated"] == "1"
    assert counters(output)["quality_stories_created"] == "1"


def test_creation_cap_defers_the_rest(fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]) -> None:
    full_world(fake_http)

    assert main({**APPLY, "SYNC_MAX_CREATIONS": "1"}) == 0

    assert writes(fake_http) == [("POST", f"{SC}/epics/100/health"), ("POST", f"{SC}/stories")]
    assert counters(capsys.readouterr().out)["creations_deferred_by_cap"] == "2"


def test_closed_issue_moves_its_story_to_done(fake_http: FakeHttp) -> None:
    build_world(
        fake_http,
        issues=[issue(1)],
        stories=[
            story(80, marker="chrysa/alpha#9"),
            story(81, state=12, marker="chrysa/alpha#10"),
            story(82, marker="chrysa/alpha#1"),
            story(83, links=["https://github.com/chrysa/alpha/issues/11"]),
        ],
        gate=None,
    )
    fake_http.add("GET", f"{REPO}/issues/9", {"number": 9, "state": "closed"})
    fake_http.add("PUT", f"{SC}/stories/80", {"id": 80})

    assert main(APPLY) == 0

    assert writes(fake_http) == [("PUT", f"{SC}/stories/80")]
    assert fake_http.writes()[0].body == {"workflow_state_id": 12}


def test_passing_gate_restores_health_and_closes_the_quality_story(fake_http: FakeHttp) -> None:
    build_world(fake_http, stories=[story(90, links=[DASHBOARD])], gate="OK", health="At Risk")
    fake_http.add("PUT", f"{SC}/stories/90", {"id": 90})

    assert main(APPLY) == 0

    assert writes(fake_http) == [("POST", f"{SC}/epics/100/health"), ("PUT", f"{SC}/stories/90")]
    assert fake_http.writes()[0].body["status"] == "On Track"


def test_failing_gate_with_an_open_story_and_unchanged_health_writes_nothing(fake_http: FakeHttp) -> None:
    build_world(fake_http, stories=[story(90, links=[DASHBOARD])], gate="ERROR", health="At Risk")

    assert main(APPLY) == 0

    assert writes(fake_http) == []


def test_private_or_unrated_sonar_project_is_skipped(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    build_world(fake_http, gate=None)

    assert main(APPLY) == 0

    assert writes(fake_http) == []
    assert counters(capsys.readouterr().out)["quality_gate_skipped"] == "1"


def test_several_epics_share_one_repo(fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]) -> None:
    build_world(fake_http, issues=[issue(1)], gate=None)
    fake_http.routes[f"GET {SC}/epics?includes_description=false"] = [
        (200, [*EPICS, {"id": 105, "external_id": "chrysa/alpha"}], {})
    ]
    fake_http.add(
        "GET",
        f"{SC}/epics/105/stories?includes_description=false",
        [story(9, links=["https://github.com/chrysa/alpha/issues/1"])],
    )

    assert main(APPLY) == 0

    assert writes(fake_http) == []
    output = capsys.readouterr().out
    assert counters(output)["repos_with_several_epics"] == "1"
    assert counters(output)["issues_already_linked"] == "1"


@pytest.mark.parametrize(
    ("repository", "status", "counter"),
    [
        ({}, 404, "repos_unreachable"),
        ({"archived": True, "has_issues": True}, 200, "repos_archived"),
        ({"archived": False, "has_issues": False}, 200, "repos_without_issues"),
    ],
)
def test_out_of_scope_repositories_are_skipped(
    fake_http: FakeHttp,
    capsys: pytest.CaptureFixture[str],
    repository: dict[str, object],
    status: int,
    counter: str,
) -> None:
    build_world(fake_http)
    fake_http.routes[f"GET {REPO}"] = [(status, repository, {})]

    assert main(APPLY) == 0

    assert not any(
        call.url.startswith(f"{REPO}/issues") or "sonarcloud" in call.url for call in fake_http.calls
    )
    assert counters(capsys.readouterr().out)[counter] == "1"


def test_github_failure_is_contained_and_fails_the_run(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    build_world(fake_http)
    fake_http.routes[f"GET {ISSUES}"] = [(500, {}, {})]

    assert main(APPLY) == 1

    output = capsys.readouterr().out
    assert counters(output)["repo_step_failures"] == "1"
    assert "alpha" not in output


def test_comment_failure_keeps_the_story_and_fails_the_run(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    build_world(fake_http, issues=[issue(1)], gate=None)
    fake_http.add(
        "POST", f"{SC}/stories", {"id": 600, "app_url": "https://app.shortcut.com/chrysa/story/600"}
    )
    fake_http.add("POST", f"{REPO}/issues/1/comments", {}, status=422)

    assert main(APPLY) == 1

    assert counters(capsys.readouterr().out)["issue_comments_failed"] == "1"


def test_shortcut_failure_aborts_the_run(fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]) -> None:
    fake_http.add("GET", f"{SC}/workflows", {}, status=401)

    assert main(APPLY) == 1

    assert "Shortcut sync aborted: Shortcut GET failed: HTTP 401" in capsys.readouterr().out


def test_missing_secret_skips_without_any_call(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main({"SYNC_DRY_RUN": "true"}) == 0

    assert fake_http.calls == []
    assert "SHORTCUT_API_TOKEN is not set" in capsys.readouterr().out


def test_invalid_configuration_fails(fake_http: FakeHttp) -> None:
    assert main({**APPLY, "SYNC_MAX_CREATIONS": "lots"}) == 1
    assert fake_http.calls == []


def test_step_summary_is_written(fake_http: FakeHttp, tmp_path) -> None:
    build_world(fake_http, gate=None)
    summary = tmp_path / "summary.md"

    assert main({**DRY_RUN, "GITHUB_STEP_SUMMARY": str(summary)}) == 0

    assert "| `repos_mapped` | 1 |" in summary.read_text(encoding="utf-8")


def test_shortcut_calls_carry_the_token_header(fake_http: FakeHttp) -> None:
    build_world(fake_http, gate=None)

    main(DRY_RUN)

    shortcut_calls = [call for call in fake_http.calls if call.url.startswith(SC)]
    assert shortcut_calls
    assert all(call.headers["Shortcut-token"] == "test-shortcut-token" for call in shortcut_calls)
