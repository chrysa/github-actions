#!/usr/bin/env python3
"""Post failed GitHub Actions runs on main/develop of an account's repos to Discord.

Runs from a scheduled workflow. Only standard library. Each failed run is posted
once: the ids already sent are kept in a small JSON state file (restored from the
Actions cache between runs). Nothing identifying a repository is printed to the
job log, because the log of a public repository is public.

Environment:
    GH_TOKEN             token used to read workflow runs (required)
    DISCORD_WEBHOOK_URL  Discord webhook of the alert channel (required to post)
    ALERT_OWNER          account whose repositories are watched (default: chrysa)
    ALERT_BRANCHES       comma separated branches (default: main,develop)
    LOOKBACK_HOURS       how far back failed runs are considered (default: 2)
    STATE_FILE           JSON state path (default: .ci-failure-alerts/state.json)
    DRY_RUN              "1" to compute without posting nor saving state
"""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable

API = "https://api.github.com"
EXCLUDED_EVENTS = frozenset({"pull_request", "pull_request_target"})
EXCLUDED_ACTORS = frozenset({"dependabot[bot]"})
STATE_RETENTION_DAYS = 7
MAX_LINES_PER_MESSAGE = 10

JsonGetter = Callable[[str], object]


def _github_get(token: str) -> JsonGetter:
    def get(path: str) -> object:
        request = urllib.request.Request(
            path if path.startswith("http") else API + path,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)

    return get


def list_repositories(get: JsonGetter, owner: str) -> list[str]:
    """Non-archived repositories of ``owner``; private ones only if the token can see them."""
    try:
        login = get("/user").get("login")  # type: ignore[union-attr]
    except urllib.error.HTTPError:
        login = None  # GITHUB_TOKEN cannot call /user: public repositories only
    base = "/user/repos?affiliation=owner&visibility=all" if login == owner else f"/users/{owner}/repos?type=owner"
    repos: list[str] = []
    page = 1
    while True:
        batch = get(f"{base}&per_page=100&page={page}")
        if not isinstance(batch, list) or not batch:
            break
        repos.extend(r["full_name"] for r in batch if not r.get("archived") and r["owner"]["login"] == owner)
        page += 1
    return sorted(set(repos))


def failed_runs(get: JsonGetter, repo: str, branch: str, since: dt.datetime) -> list[dict]:
    query = urllib.parse.urlencode(
        {"branch": branch, "status": "failure", "created": f">={since:%Y-%m-%dT%H:%M:%SZ}", "per_page": 50}
    )
    try:
        payload = get(f"/repos/{repo}/actions/runs?{query}")
    except urllib.error.HTTPError as error:
        if error.code in (403, 404):  # Actions disabled or not visible to the token
            return []
        raise
    runs = payload.get("workflow_runs", []) if isinstance(payload, dict) else []
    return [
        run
        for run in runs
        if run.get("event") not in EXCLUDED_EVENTS and (run.get("actor") or {}).get("login") not in EXCLUDED_ACTORS
    ]


def load_state(path: pathlib.Path, now: dt.datetime) -> dict[str, str]:
    try:
        sent = json.loads(path.read_text(encoding="utf-8")).get("sent", {})
    except (OSError, ValueError, AttributeError):
        return {}
    cutoff = now - dt.timedelta(days=STATE_RETENTION_DAYS)
    kept = {}
    for run_id, stamp in sent.items():
        try:
            if dt.datetime.fromisoformat(stamp) >= cutoff:
                kept[str(run_id)] = stamp
        except (TypeError, ValueError):
            continue
    return kept


def save_state(path: pathlib.Path, sent: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"sent": sent}, indent=0, sort_keys=True), encoding="utf-8")


def format_line(repo: str, run: dict) -> str:
    name = run.get("name") or "workflow"
    return f"CI rouge — {repo} · {name} · {run.get('head_branch')} · <{run.get('html_url')}>"


def chunk(lines: list[str], size: int = MAX_LINES_PER_MESSAGE) -> Iterable[list[str]]:
    for start in range(0, len(lines), size):
        yield lines[start : start + size]


def post_discord(webhook_url: str, lines: list[str]) -> None:
    for part in chunk(lines):
        body = json.dumps({"content": "\n".join(part), "allowed_mentions": {"parse": []}}).encode()
        request = urllib.request.Request(
            webhook_url, data=body, method="POST", headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=30):
            pass


def collect(
    get: JsonGetter, owner: str, branches: list[str], since: dt.datetime, already_sent: dict[str, str]
) -> list[tuple[str, dict]]:
    new: list[tuple[str, dict]] = []
    for repo in list_repositories(get, owner):
        for branch in branches:
            for run in failed_runs(get, repo, branch, since):
                if str(run["id"]) not in already_sent:
                    new.append((repo, run))
    new.sort(key=lambda item: item[1].get("created_at") or "")
    return new


def main() -> int:
    token = os.environ.get("GH_TOKEN", "")
    webhook = os.environ.get("DISCORD_WEBHOOK_URL", "")
    dry_run = os.environ.get("DRY_RUN") == "1"
    if not token:
        sys.stdout.write("::error::GH_TOKEN is not set\n")
        return 1
    if not webhook and not dry_run:
        sys.stdout.write("::notice::Discord webhook secret is not configured; nothing posted\n")
        return 0
    owner = os.environ.get("ALERT_OWNER", "chrysa")
    branches = [b.strip() for b in os.environ.get("ALERT_BRANCHES", "main,develop").split(",") if b.strip()]
    now = dt.datetime.now(dt.UTC)
    since = now - dt.timedelta(hours=float(os.environ.get("LOOKBACK_HOURS", "2")))
    state_path = pathlib.Path(os.environ.get("STATE_FILE", ".ci-failure-alerts/state.json"))

    sent = load_state(state_path, now)
    new = collect(_github_get(token), owner, branches, since, sent)
    sys.stdout.write(f"failed runs not yet reported: {len(new)}\n")  # counts only: the job log is public
    if dry_run or not new:
        return 0
    post_discord(webhook, [format_line(repo, run) for repo, run in new])
    stamp = now.isoformat()
    sent.update({str(run["id"]): stamp for _, run in new})
    save_state(state_path, sent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
