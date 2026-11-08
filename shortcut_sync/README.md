# shortcut_sync

**Role.** The daily Shortcut sync (decision DEC-V14-125): Shortcut is the source of truth
for work, GitHub for code, Sentry for errors (it opens GitHub issues natively), SonarCloud
for quality. Run by `.github/workflows/shortcut-sync.yml` as `python3 -m shortcut_sync`.

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

Safety: no label is ever added; at most `SYNC_MAX_CREATIONS` (default 25) stories are
created per run (steps 1–2 first, so the cap favours them); `SYNC_DRY_RUN=true` only reads
and reports planned counts; workflow states come from `GET /workflows`, never hardcoded.

## Structure

| Path | Purpose |
|---|---|
| `entrypoint.py` | `main()`: environment → job → counts, step summary, exit code |
| `sync_job.py` | `ShortcutSyncJob`: reads, then runs the three steps repo by repo |
| `closed_issue_resolver.py` · `quality_gate_sync.py` · `issue_importer.py` | the three steps |
| `story_writer.py` | the only story writes (create, move to done), dry-run aware |
| `shortcut_client.py` · `github_client.py` · `sonar_client.py` | API clients |
| `http_client.py` | stdlib HTTPS client: pacing, retry on 429/5xx/network, same-origin redirects only (tokens never follow a redirect to another host), typed errors |
| `sync_config.py` · `sync_context.py` · `sync_report.py` · `sync_counter.py` | configuration, wiring, counters |
| `repo_mapping.py` · `repo_snapshot.py` · `workflow_states.py` · `issue_key.py` · `story_draft.py` | value objects |
| `references.py` | pure helpers (reference detection, story type, Sonar keys) |
| `payloads.py` | `TypedDict` shapes of the API payloads (types only) |

## Environment

| Variable | Default | Meaning |
|---|---|---|
| `SHORTCUT_API_TOKEN` | — | Shortcut API token (secret). Missing → the run is skipped. |
| `SYNC_GITHUB_TOKEN` | — | Fine-grained PAT, issues read/write on chrysa repos (secret). |
| `SYNC_DRY_RUN` | `true` | `false` applies the writes. |
| `SYNC_MAX_CREATIONS` | `25` | Story creations allowed per run. |
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
