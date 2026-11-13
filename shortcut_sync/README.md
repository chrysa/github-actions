# shortcut_sync

**Role.** The daily Shortcut sync (decision DEC-V14-125, reduced to a native-first scope by
sc-6014): Shortcut is the source of truth for work, GitHub for code. This package only does
what no native integration does on the current free plans. Run by
`.github/workflows/shortcut-sync.yml` as `python3 -m shortcut_sync`.

## Native pieces it relies on (no code here)

| Need | Native mechanism |
|---|---|
| Pull request ↔ story | Shortcut GitHub integration: a branch, commit or pull request naming `sc-<id>` links the story; its event handlers move the story to *In Review* when the pull request opens and to *Done* when it merges. |
| Repository activity → team | Discord channel webhooks used as GitHub webhooks (`<webhook>/github` URL). |
| Code quality (SonarCloud) | The quality gate is a required check on pull requests; SonarCloud sends its e-mail notifications. |
| Security scan (GuardRails) | `guardrails/scan` is a required check on pull requests; GuardRails notifies Discord through its Slack-webhook setting pointed at a Discord `<webhook>/slack` URL. |
| Errors (Sentry) | The free Developer plan alerts by e-mail only: it cannot open GitHub issues (`GET /organizations/chrysa/available-actions/` returns `email` only). An error worth tracking becomes a story by hand, from the e-mail. |

Shortcut Free has no automations, and its GitHub event handlers only move stories that a pull
request references: the three steps below cover the rest.

## What the sync does

A repository is mapped to Shortcut through an epic whose `external_id` is `chrysa/<repo>`;
epics without it are skipped. Each run, per mapped repository:

1. **Closed issue → story done.** A story created by the sync (its `external_id` is
   `chrysa/<repo>#<n>`) moves to the done state of its workflow once the issue is closed —
   also when the issue was closed without a pull request, which the native event handlers do
   not see. Idempotent: a story already done is not touched.
2. **GitHub issues → stories.** Every open issue (pull requests excluded) without a
   Shortcut link becomes a story in the epic (`bug` if labelled `bug` or `sentry`, else
   `feature`; external link = issue URL), then the issue gets one comment
   `Shortcut: sc-<id> <story url>`. "Linked" = the body or a comment mentions `sc-<digits>`
   or an app.shortcut.com story URL, or a story of a mapped epic already links the issue.

Then, once per run, over the whole workspace (mapped epics or not):

3. **Epic and objective states** (sc-5963, reduced to state changes by sc-6014). For every
   non-archived epic holding at least one non-archived story (stories re-read, so this run's
   writes count):
   - an *unstarted* epic with a started story (one whose `started_at` Shortcut has set) moves
     to the first *started* epic state;
   - every story done → the epic moves to the first *done* epic state; a done epic with a
     not-done story moves back to *started*;
   - an objective `to do` moves to `in progress` once one of its epics has started; an
     objective is never set to done, and done or archived objectives are not touched.

   Only states are written. Shortcut stamps the native `started_at` / `completed_at` of the
   epic or objective when its state changes; `started_at_override`, `completed_at_override`,
   `planned_start_date` and `deadline` are never written (overrides are for manual
   corrections only).

Safety: no label is ever added; at most `SYNC_MAX_CREATIONS` (default 25) stories are
created per run; at most `SYNC_MAX_PROGRESS_UPDATES` (default 50) epic + objective updates
per run (one `PUT` each); `SYNC_DRY_RUN=true` only reads and reports planned counts; story
workflow states come from `GET /workflows` and epic states from `GET /epic-workflow`, never
hardcoded. Objectives have no workflow endpoint: their states are the fixed API enum
(`to do` / `in progress` / `done`).

Known limit: the native dates of an epic or objective moved by the sync are the time of the
run that moved it (the job runs daily at 05:17 UTC, so up to one day late). When that
matters, correct it by hand with the override field: the sync never writes it.

## Structure

| Path | Purpose |
|---|---|
| `entrypoint.py` | `main()`: environment → job → counts, step summary, exit code |
| `sync_job.py` | `ShortcutSyncJob`: reads, runs the two repository steps repo by repo, then the progress step |
| `closed_issue_resolver.py` · `issue_importer.py` | the repository steps |
| `epic_progress_sync.py` · `objective_progress_sync.py` | the workspace progress step (epics, then objectives) |
| `epic_progress_plan.py` · `epic_timeline.py` · `epic_workflow_states.py` | epic decision: target state |
| `story_writer.py` | the only story writes (create, move to done), dry-run aware |
| `progress_writer.py` | the only epic / objective writes, dry-run aware, within the update cap |
| `shortcut_client.py` · `github_client.py` | API clients |
| `http_client.py` | stdlib HTTPS client: pacing, retry on 429/5xx/network, same-origin redirects only (tokens never follow a redirect to another host), typed errors |
| `sync_config.py` · `sync_context.py` · `sync_report.py` · `sync_counter.py` | configuration, wiring, counters |
| `repo_mapping.py` · `repo_snapshot.py` · `workflow_states.py` · `issue_key.py` · `story_draft.py` | value objects |
| `references.py` | pure helpers (reference detection, story type, linked issues, issue comment) |
| `payloads.py` | `TypedDict` shapes of the API payloads (types only) |

## Environment

| Variable | Default | Meaning |
|---|---|---|
| `SHORTCUT_API_TOKEN` | — | Shortcut API token (secret of the `shortcut-sync` environment). Missing → the run is skipped. |
| `SYNC_GITHUB_TOKEN` | — | Fine-grained PAT on chrysa repos: Issues read/write only (secret of the `shortcut-sync` environment). |
| `SYNC_DRY_RUN` | `true` | `false` applies the writes. |
| `SYNC_MAX_CREATIONS` | `25` | Story creations allowed per run. |
| `SYNC_MAX_PROGRESS_UPDATES` | `50` | Epic + objective updates allowed per run. |
| `SHORTCUT_WORKFLOW_ID` | — | Needed only if the workspace has several workflows. |
| `SHORTCUT_API_URL` · `GITHUB_API_URL` | public endpoints | https only. |

## Should contain

- Sync logic and its API clients, stdlib only, for what no native integration covers.

## Should NOT contain

- Workflow YAML (it lives in `.github/workflows/`) or tests (they live in `tests/test_shortcut_sync_*.py`).
- Anything a native integration already does on the current plans (pull-request-driven story
  moves, quality or security gates and their notifications, date fields Shortcut stamps itself):
  see *Native pieces* above.

## Rules

- Native first: add a step only when no native integration covers it on the current plans
  (owner decision 2026-11-09, sc-6014), and record it in `DECISIONS.md` (D-0005).
- Public logs: counts and numeric ids only — never an issue title, a story name or a
  repository name (repositories may be private). Errors never carry a URL or a token.
- One class per module, keyword-only arguments, typed errors (`errors.py`).
- Tests use the `fake_http` fixture (`tests/conftest.py`): no network, no real token.
