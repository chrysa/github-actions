"""Epic and objective progress (sc-5963) — end-to-end runs of ``main`` over a fake transport.

The epics here carry no ``chrysa/<repo>`` mapping, so only Shortcut is called.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

import pytest

from shortcut_sync.entrypoint import main

if TYPE_CHECKING:
    from tests.conftest import FakeHttp

SC = "https://api.app.shortcut.com/api/v3"
APPLY = {
    "SHORTCUT_API_TOKEN": "test-shortcut-token",
    "SYNC_GITHUB_TOKEN": "test-github-token",
    "SYNC_DRY_RUN": "false",
}
DRY_RUN = {**APPLY, "SYNC_DRY_RUN": "true"}
UNSTARTED, STARTED, DONE = 500, 501, 502
STORY_TODO, STORY_DOING, STORY_DONE = 10, 11, 12
WORKFLOWS = [
    {
        "id": 1,
        "default_state_id": STORY_TODO,
        "states": [
            {"id": STORY_TODO, "type": "unstarted", "position": 1},
            {"id": STORY_DOING, "type": "started", "position": 2},
            {"id": STORY_DONE, "type": "done", "position": 3},
        ],
    }
]
EPIC_WORKFLOW = {
    "id": 1,
    "epic_states": [
        {"id": UNSTARTED, "type": "unstarted", "position": 0},
        {"id": STARTED, "type": "started", "position": 1},
        {"id": 503, "type": "done", "position": 3},
        {"id": DONE, "type": "done", "position": 2},
    ],
}
ALLOWED_EPIC_FIELDS = {"epic_state_id", "started_at_override", "completed_at_override"}
JAN_10 = "2026-01-10T09:00:00Z"
JAN_05 = "2026-01-05T09:00:00Z"
FEB_01 = "2026-02-01T18:00:00Z"
MAR_01 = "2026-03-01T18:00:00Z"


def epic(epic_id: int, *, state: int = UNSTARTED, **fields: object) -> dict[str, object]:
    return {
        "id": epic_id,
        "archived": False,
        "external_id": None,
        "epic_state_id": state,
        "started_at": None,
        "started_at_override": None,
        "completed_at_override": None,
        "planned_start_date": "2025-12-01T00:00:00Z",
        "deadline": "2026-06-30T00:00:00Z",
        "objective_ids": [],
        **fields,
    }


def story(story_id: int, *, state: int = STORY_TODO, **fields: object) -> dict[str, object]:
    return {
        "id": story_id,
        "archived": False,
        "workflow_id": 1,
        "workflow_state_id": state,
        "started_at": None,
        "started_at_override": None,
        "completed_at": None,
        "completed_at_override": None,
        **fields,
    }


def objective(objective_id: int, *, state: str = "to do", **fields: object) -> dict[str, object]:
    return {"id": objective_id, "archived": False, "state": state, "started_at_override": None, **fields}


def world(
    fake: FakeHttp,
    *,
    epics: Sequence[dict[str, object]],
    stories: Mapping[int, Sequence[dict[str, object]]],
    objectives: Sequence[dict[str, object]] | None = None,
) -> None:
    fake.add("GET", f"{SC}/workflows", WORKFLOWS)
    fake.add("GET", f"{SC}/epics?includes_description=false", list(epics))
    fake.add("GET", f"{SC}/epic-workflow", EPIC_WORKFLOW)
    for epic_id, epic_stories in stories.items():
        fake.add("GET", f"{SC}/epics/{epic_id}/stories?includes_description=false", list(epic_stories))
        fake.add("PUT", f"{SC}/epics/{epic_id}", {"id": epic_id})
    if objectives is not None:
        fake.add("GET", f"{SC}/objectives", list(objectives))
        for item in objectives:
            fake.add("PUT", f"{SC}/objectives/{item['id']}", {"id": item["id"]})


def written(fake: FakeHttp) -> dict[str, object]:
    return {call.url.removeprefix(f"{SC}/"): call.body for call in fake.writes()}


def counters(output: str) -> dict[str, str]:
    pairs = (line.split(": ", 1) for line in output.splitlines() if ": " in line)
    return dict(pairs)


def test_a_started_story_starts_its_epic_at_the_earliest_story_start(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    world(
        fake_http,
        epics=[epic(1)],
        stories={
            1: [
                story(11, state=STORY_DOING, started_at=JAN_10),
                story(12, state=STORY_DONE, started_at=FEB_01, started_at_override=JAN_05),
                story(13, started_at="2025-01-01T00:00:00Z", archived=True),
                story(14),
            ]
        },
    )

    assert main(APPLY) == 0

    assert written(fake_http) == {"epics/1": {"epic_state_id": STARTED, "started_at_override": JAN_05}}
    output = capsys.readouterr().out
    assert counters(output)["epics_checked"] == "1"
    assert counters(output)["epics_moved_to_started"] == "1"


def test_all_stories_done_closes_the_epic_at_the_latest_completion(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    world(
        fake_http,
        epics=[epic(1, state=STARTED, started_at_override=JAN_05)],
        stories={
            1: [
                story(11, state=STORY_DONE, started_at=JAN_05, completed_at=FEB_01),
                story(
                    12, state=STORY_DONE, started_at=JAN_10, completed_at=JAN_10, completed_at_override=MAR_01
                ),
            ]
        },
    )

    assert main(APPLY) == 0

    assert written(fake_http) == {"epics/1": {"epic_state_id": DONE, "completed_at_override": MAR_01}}
    assert counters(capsys.readouterr().out)["epics_moved_to_done"] == "1"


def test_an_unstarted_epic_whose_stories_are_all_done_goes_straight_to_done(fake_http: FakeHttp) -> None:
    world(
        fake_http,
        epics=[epic(1)],
        stories={1: [story(11, state=STORY_DONE, started_at=JAN_05, completed_at=FEB_01)]},
    )

    assert main(APPLY) == 0

    assert written(fake_http) == {
        "epics/1": {"epic_state_id": DONE, "started_at_override": JAN_05, "completed_at_override": FEB_01}
    }


def test_a_story_coming_back_reopens_the_epic_and_clears_its_completion(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    world(
        fake_http,
        epics=[epic(1, state=DONE, started_at_override=JAN_05, completed_at_override=FEB_01)],
        stories={1: [story(11, state=STORY_DONE, started_at=JAN_05, completed_at=FEB_01), story(12)]},
    )

    assert main(APPLY) == 0

    assert written(fake_http) == {"epics/1": {"epic_state_id": STARTED, "completed_at_override": None}}
    assert counters(capsys.readouterr().out)["epics_moved_back_to_started"] == "1"


def test_dates_set_by_hand_are_kept_and_counted(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    world(
        fake_http,
        epics=[
            epic(1, state=STARTED, started_at_override="2025-11-01T00:00:00Z"),
            epic(
                2, state=DONE, started_at_override="2026-01-05T09:00:00+00:00", completed_at_override=MAR_01
            ),
        ],
        stories={
            1: [story(11, state=STORY_DOING, started_at=JAN_10)],
            2: [story(21, state=STORY_DONE, started_at=JAN_05, completed_at=FEB_01)],
        },
    )

    assert main(APPLY) == 0

    assert written(fake_http) == {}
    assert counters(capsys.readouterr().out)["manual_dates_kept"] == "2"


def test_a_started_epic_without_override_gets_its_start_date(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    world(
        fake_http,
        epics=[epic(1, state=STARTED)],
        stories={1: [story(11, state=STORY_DOING, started_at=JAN_10)]},
    )

    assert main(APPLY) == 0

    assert written(fake_http) == {"epics/1": {"started_at_override": JAN_10}}
    assert counters(capsys.readouterr().out)["epic_dates_set"] == "1"


def test_planned_start_date_and_deadline_are_never_written(fake_http: FakeHttp) -> None:
    world(
        fake_http,
        epics=[epic(1), epic(2, state=DONE, completed_at_override=FEB_01), epic(3, state=STARTED)],
        stories={
            1: [story(11, state=STORY_DONE, started_at=JAN_05, completed_at=FEB_01)],
            2: [story(21)],
            3: [story(31, state=STORY_DOING, started_at=JAN_10)],
        },
    )

    assert main(APPLY) == 0

    bodies = written(fake_http)
    assert set(bodies) == {"epics/1", "epics/2", "epics/3"}
    assert all(set(body) <= ALLOWED_EPIC_FIELDS for body in bodies.values())


def test_quiet_epics_are_left_alone_and_empty_ones_are_not_read(fake_http: FakeHttp) -> None:
    world(
        fake_http,
        epics=[
            epic(1),
            epic(2, stats={"num_stories_total": 0}),
            epic(3, archived=True),
            epic(4, state=999),
            epic(5),
            {"id": "not-an-id"},
        ],
        stories={
            1: [story(11)],
            4: [story(41, state=STORY_DOING, started_at=JAN_05)],
            5: [story(51, archived=True)],
        },
    )

    assert main(APPLY) == 0

    assert written(fake_http) == {}
    read = {call.url for call in fake_http.calls}
    assert f"{SC}/epics/2/stories?includes_description=false" not in read
    assert f"{SC}/epics/3/stories?includes_description=false" not in read
    assert f"{SC}/objectives" not in read


def test_objectives_start_with_their_first_started_epic(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    world(
        fake_http,
        epics=[
            epic(1, objective_ids=[7, 8, 9, 10, 11, 14]),
            epic(2, state=STARTED, started_at=JAN_05, objective_ids=[7]),
            epic(3, objective_ids=[12]),
        ],
        stories={1: [story(11, state=STORY_DOING, started_at=JAN_10)], 2: [story(21)], 3: [story(31)]},
        objectives=[
            objective(7),
            objective(8, started_at_override="2025-01-01T00:00:00Z"),
            objective(9, state="in progress"),
            objective(10, state="done"),
            objective(11, archived=True),
            objective(12),
            objective(13),
            objective(14, state="in progress", started_at_override="2026-01-10T10:00:00+01:00"),
        ],
    )

    assert main(APPLY) == 0

    bodies = written(fake_http)
    assert bodies["objectives/7"] == {"state": "in progress", "started_at_override": JAN_05}
    assert bodies["objectives/8"] == {"state": "in progress"}
    assert bodies["objectives/9"] == {"started_at_override": JAN_10}
    assert not {"objectives/10", "objectives/11", "objectives/12", "objectives/13", "objectives/14"} & set(
        bodies
    )
    output = capsys.readouterr().out
    assert counters(output)["objectives_moved_to_started"] == "2"
    assert counters(output)["objective_dates_set"] == "1"
    assert counters(output)["manual_dates_kept"] == "1"


def test_the_update_cap_defers_epics_and_their_objectives(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    world(
        fake_http,
        epics=[epic(1), epic(2, objective_ids=[7])],
        stories={
            1: [story(11, state=STORY_DOING, started_at=JAN_10)],
            2: [story(21, state=STORY_DOING, started_at=JAN_05)],
        },
        objectives=[objective(7)],
    )

    assert main({**APPLY, "SYNC_MAX_PROGRESS_UPDATES": "1"}) == 0

    assert list(written(fake_http)) == ["epics/1"]
    assert counters(capsys.readouterr().out)["progress_updates_deferred_by_cap"] == "1"


def test_dry_run_plans_progress_without_writing(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    world(
        fake_http,
        epics=[epic(1, objective_ids=[7])],
        stories={1: [story(11, state=STORY_DOING, started_at=JAN_10)]},
        objectives=[objective(7)],
    )

    assert main(DRY_RUN) == 0

    assert fake_http.writes() == []
    output = capsys.readouterr().out
    assert "[dry-run] epics_moved_to_started: epic 1" in output
    assert "[dry-run] objectives_moved_to_started: objective 7" in output


def test_epic_and_objective_failures_are_contained_and_fail_the_run(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str]
) -> None:
    world(
        fake_http,
        epics=[epic(1), epic(2, objective_ids=[7])],
        stories={1: [], 2: [story(21, state=STORY_DOING, started_at=JAN_05)]},
        objectives=[objective(7)],
    )
    fake_http.routes[f"GET {SC}/epics/1/stories?includes_description=false"] = [(500, {}, {})]
    fake_http.routes[f"PUT {SC}/objectives/7"] = [(400, {}, {})]

    assert main(APPLY) == 1

    assert ("PUT", f"{SC}/epics/2") in [(call.method, call.url) for call in fake_http.writes()]
    assert counters(capsys.readouterr().out)["progress_step_failures"] == "2"


@pytest.mark.parametrize(
    "route",
    [
        [(500, {}, {})],
        [(200, {"id": 1, "epic_states": [{"id": UNSTARTED, "type": "unstarted"}]}, {})],
        [(200, None, {})],
    ],
)
def test_an_unusable_epic_workflow_skips_the_step_and_fails_the_run(
    fake_http: FakeHttp, capsys: pytest.CaptureFixture[str], route: list[tuple[int, object, dict[str, str]]]
) -> None:
    world(fake_http, epics=[epic(1)], stories={})
    fake_http.routes[f"GET {SC}/epic-workflow"] = route

    assert main(APPLY) == 1

    output = capsys.readouterr().out
    assert counters(output)["progress_step_failures"] == "1"
    assert "epic progress step failed" in output
