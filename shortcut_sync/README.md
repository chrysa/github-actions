# shortcut_sync

**Role.** The daily Shortcut sync (decision DEC-V14-125): Shortcut is the source of truth
for work, GitHub for code, Sentry for errors (it opens GitHub issues natively), SonarCloud
and GuardRails for quality and security. Run by `.github/workflows/shortcut-sync.yml` as
`python3 -m shortcut_sync`.

A repository is mapped to Shortcut through an epic whose `external_id` is `chrysa/<repo>`;
epics without it are skipped. Each run, per mapped repository:

1. **Closed issue → story done.** A story created by the sync (its `external_id` is
   `chrysa/<repo>#<n>`) moves to the done state of its workflow once the issue is closed.
2. **Quality gate → epic health.** SonarCloud `chrysa_<repo>` is read anonymously
   (private or absent project → skipped). `ERROR` → epic health *At Risk* and exactly one
   open story *SonarCloud quality gate failing* (deduped by its dashboard link);
   `OK` → *On Track* and that story moves to done. Health is only written when it changes.
3. **GitHub issues → stories.** Every open issue (pull requests excluded) without a
   Shortcut link becomes a story in the epic (`bug` if labelled `bug` or `sentry`, else
   `feature`; external link = issue URL), then the issue gets one comment
   `Shortcut: sc-<id> <story url>`. "Linked" = the body or a comment mentions `sc-<digits>`
   or an app.shortcut.com story URL, or a story of a mapped epic already links the issue.
4. **GuardRails scan → bug story** (sc-5967). The latest completed check run
   `guardrails/scan` posted by the GuardRails app on the head of the default branch
   (`GET /repos/chrysa/<repo>/commits/<default_branch>/check-runs?check_name=guardrails/scan`).
   `failure` → exactly one open `bug` story *GuardRails : failles hautes sur la branche par
   défaut* in the epic (deduped by `external_id` = `chrysa/<repo>#guardrails`, external link =
   the check run); `success` / `neutral` → that story moves to done; no run, another
   conclusion, or an unreadable check → skipped. GuardRails exposes no severity on the check
   run (title only, empty summary, no annotation), so the rule keys on `failure` alone: the
   severity threshold is the one set in GuardRails' own configuration.

Then, once per run, over the whole workspace (mapped epics or not):

5. **Epic and objective progress** (sc-5963). For every non-archived epic holding at least
   one non-archived story (stories re-read, so this run's writes count):
   - start = earliest story start (`started_at_override`, else `started_at`); an
     *unstarted* epic with a started story moves to the first *started* epic state;
   - every story done → the epic moves to the first *done* epic state, completion = latest
     story completion (`completed_at_override`, else `completed_at`); a done epic with a
     not-done story moves back to *started* and its `completed_at_override` is cleared;
   - an empty `started_at_override` / `completed_at_override` is set to the computed date;
     one already set that differs is never overwritten and is counted as
     `manual_dates_kept`; `planned_start_date` and `deadline` are never written;
   - an objective `to do` moves to `in progress` once one of its epics has started, its
     empty `started_at_override` set to the earliest epic start (same keep-manual rule); an
     objective is never set to done, and done or archived objectives are not touched.

Safety: no label is ever added; at most `SYNC_MAX_CREATIONS` (default 25) stories are
created per run (steps 1, 2 and 4 before 3, so the cap favours them); at most
`SYNC_MAX_PROGRESS_UPDATES` (default 50) epic + objective updates per run (one `PUT` each);
`SYNC_DRY_RUN=true` only reads and reports planned counts; story workflow states come from
`GET /workflows` and epic states from `GET /epic-workflow`, never hardcoded. Objectives have
no workflow endpoint: their states are the fixed API enum (`to do` / `in progress` / `done`).

Known limits: stories bulk-imported on 2026-08-23 carry that import date as their start, so
an epic started only through them gets 2026-08-23 as its start (correct it by hand once: a
date set by hand is kept); once the sync has written an override, a later change of the
story dates does not move it (it cannot tell its own past write from a manual one).

## Structure

| Path | Purpose |
|---|---|
| `entrypoint.py` | `main()`: environment → job → counts, step summary, exit code |
| `sync_job.py` | `ShortcutSyncJob`: reads, runs the four repository steps repo by repo, then the progress step |
| `closed_issue_resolver.py` · `quality_gate_sync.py` · `guardrails_sync.py` · `issue_importer.py` | the repository steps |
| `epic_progress_sync.py` · `objective_progress_sync.py` | the workspace progress step (epics, then objectives) |
| `epic_progress_plan.py` · `epic_timeline.py` · `epic_workflow_states.py` | epic decision: target state and date overrides |
| `story_writer.py` | the only story writes (create, move to done), dry-run aware |
| `progress_writer.py` | the only epic / objective writes, dry-run aware, within the update cap |
| `shortcut_client.py` · `github_client.py` · `sonar_client.py` | API clients |
| `http_client.py` | stdlib HTTPS client: pacing, retry on 429/5xx/network, same-origin redirects only (tokens never follow a redirect to another host), typed errors |
| `sync_config.py` · `sync_context.py` · `sync_report.py` · `sync_counter.py` | configuration, wiring, counters |
| `repo_mapping.py` · `repo_snapshot.py` · `workflow_states.py` · `issue_key.py` · `story_draft.py` | value objects |
| `references.py` | pure helpers (reference detection, story type, Sonar keys, GuardRails marker) |
| `timestamps.py` | pure helpers (ISO timestamps compared as instants, keep-manual override rule) |
| `payloads.py` | `TypedDict` shapes of the API payloads (types only) |

## Environment

| Variable | Default | Meaning |
|---|---|---|
| `SHORTCUT_API_TOKEN` | — | Shortcut API token (secret of the `shortcut-sync` environment). Missing → the run is skipped. |
| `SYNC_GITHUB_TOKEN` | — | Fine-grained PAT on chrysa repos: issues read/write, checks read (secret of the `shortcut-sync` environment). |
| `SYNC_DRY_RUN` | `true` | `false` applies the writes. |
| `SYNC_MAX_CREATIONS` | `25` | Story creations allowed per run. |
| `SYNC_MAX_PROGRESS_UPDATES` | `50` | Epic + objective updates allowed per run. |
| `SHORTCUT_WORKFLOW_ID` | — | Needed only if the workspace has several workflows. |
| `SHORTCUT_API_URL` · `GITHUB_API_URL` · `SONAR_HOST_URL` | public endpoints | https only. |

## Should contain

- Sync logic and its API clients, stdlib only.

## Should NOT contain

- Workflow YAML (it lives in `.github/workflows/`) or tests (they live in `tests/test_shortcut_sync_*.py`).

## Rules

- Public logs: counts and numeric ids only — never an issue title, a story name or a
  repository name (repositories may be private). Errors never carry a URL or a token.
- One class per module, keyword-only arguments, typed errors (`errors.py`).
- Tests use the `fake_http` fixture (`tests/conftest.py`): no network, no real token.
