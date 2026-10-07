# REQUIREMENTS — github-actions

Technical requirements traced to repo evidence. Status is **IMPLEMENTED** only
where directly verifiable in the tree; otherwise **PARTIAL** or **UNKNOWN**.

| ID | Description | Type | Source | Status | Implementation | Tests | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-TECH-001 | Provide reusable composite actions for the chrysa fleet | Functional | README, pyproject | IMPLEMENTED | 24 `*/action.yml` (`using: composite`) | n/a | `ruff-check/action.yml` etc. |
| REQ-TECH-002 | Provide reusable `workflow_call` workflows | Functional | `.github/workflows/` | IMPLEMENTED | 24 workflows with `on: workflow_call` | n/a | grep `workflow_call` |
| REQ-TECH-003 | Notion branch/roadmap sync via tested Python | Functional | README, notion_sync | IMPLEMENTED | `notion_sync/` package | 5 test modules in `tests/` | `test_branch_sync.py`, `test_roadmap_sync.py` |
| REQ-TECH-004 | Action inputs are typed & documented | Quality | action.yml convention | IMPLEMENTED | `inputs:` with `description`/`required`/`default` | n/a | `ruff-check/action.yml` |
| REQ-TECH-005 | Secrets only via caller inputs / `secrets.*`, never hardcoded | Security | SECURITY.md | IMPLEMENTED | No hardcoded secrets found | n/a | grep scan (see TRD §4) |
| REQ-TECH-006 | `secrets: inherit` forbidden | Security | SECURITY.md | IMPLEMENTED (policy) | Documented policy | UNKNOWN (not enforced by a check found) | SECURITY.md |
| REQ-TECH-007 | Shell steps inject inputs via `env:` (injection-safe) | Security | ruff-check pattern | PARTIAL | Verified in spot-checked actions | UNKNOWN | `ruff-check/action.yml`; not exhaustively audited |
| REQ-TECH-008 | Semver computed from git history | Functional | GitVersion.yml | IMPLEMENTED | GitVersion config | n/a | `GitVersion.yml`, `gitversion/action.yml` |
| REQ-TECH-009 | Release changelog auto-generated | Functional | cliff.toml | IMPLEMENTED | git-cliff | n/a | `cliff.toml`, `changelog/action.yml` |
| REQ-TECH-010 | Consumers pin floating `@v1`; latest major only supported | Operational | SECURITY.md | IMPLEMENTED (policy) | Tag-move on release | n/a | SECURITY.md, docs/reference |
| REQ-TECH-011 | Lint runs in pre-commit (SoT), CI only at release | Operational | DECISIONS D-0002 | IMPLEMENTED | `lint-python.yml` reusable | n/a | `DECISIONS.md` D-0002 |
| REQ-TECH-012 | SAST + secret-scan gates | Security | workflows | IMPLEMENTED | `sast.yml`, `secret-scan.yml` | n/a | `.github/workflows/` |
| REQ-TECH-013 | Python >= 3.12 | Constraint | pyproject | IMPLEMENTED | `requires-python = ">=3.12"` | n/a | `pyproject.toml` |
| REQ-TECH-014 | `action.yml` files self-validate in CI | Quality | test/workflow | PARTIAL | `test_actions_yaml.py`, `action-check.yml` | yes | `tests/test_actions_yaml.py` |
| REQ-TECH-015 | Third-party & internal `uses` pinned by immutable SHA | Security | chrysa CI-CD standard (INFERENCE) | NOT MET | Pinned to tags / `@main` | n/a | see [REVIEW.md](REVIEW.md), [SECURITY.md](SECURITY.md) |
| REQ-TECH-016 | Every `workflow_call` workflow sets explicit `permissions:` | Security | least-privilege (INFERENCE) | PARTIAL | 18/… set it; 9 omit | n/a | see [REVIEW.md](REVIEW.md) |

Full per-action input reference: [README.md](README.md). Design detail: [TRD.md](TRD.md).
