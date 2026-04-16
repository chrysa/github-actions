# Composite actions vs Reusable workflows

Doctrine for the `chrysa` ecosystem.

## Rule

| Logic varies per repo | Logic identical across repos |
|---|---|
| **Composite action** with inputs | **Reusable workflow** |
| Lives in `chrysa/github-actions` | Lives in `chrysa/shared-standards/.github/workflows/` |

## Composite actions (this repo)

Small reusable steps wired into a job. Use when:

- The step is a unit of work (setup, lint, scan)
- Calling repos need to wire it inside their own jobs
- Inputs differ meaningfully between callers

Examples in this repo: `python-setup`, `ruff-check`, `sonar-scan-python`,
`run-tests`, `gitversion`, `publish-python-package`.

```yaml
# Calling repo
- uses: chrysa/github-actions/ruff-check@v1
  with:
    python-version: ${{ matrix.python-version }}
    latest-python: '3.14'
    sources: 'src tests'
```

## Reusable workflows (`shared-standards`)

Full pipelines called as a single job. Use when:

- The pipeline shape is identical (jobs, triggers, secrets)
- Variation is limited to a few inputs
- You want a single place to update CI for many repos

Examples in `chrysa/shared-standards`: `ci-python.yml`, `release.yml`,
`sonar.yml`.

```yaml
# Calling repo
jobs:
  ci:
    uses: chrysa/shared-standards/.github/workflows/ci-python.yml@v1
    with:
      python-versions: '["3.12", "3.13", "3.14"]'
      cov-module: my_package
    secrets: inherit
```

## Decision matrix

| Question | Composite action | Reusable workflow |
|---|---|---|
| Does it need to run as one step? | yes | no |
| Does it need full job control (matrix, services, runs-on)? | no | yes |
| Will every caller use the same trigger and permissions? | no | yes |
| Does it produce/consume artifacts across jobs? | step level | job level |
| Should secrets be inherited transparently? | not directly | yes (`secrets: inherit`) |

## Versioning

- **Composite actions** (this repo): tag `v1`, `v1.x.y`. Calling repos pin `@v1`
  for stability, `@v1.2.0` for reproducibility.
- **Reusable workflows** (`shared-standards`): same tagging contract. Pin `@v1`.

## When to migrate

| Symptom | Action |
|---|---|
| Same job copy-pasted in 3+ repos | Promote to reusable workflow in `shared-standards` |
| Same step copy-pasted in 3+ workflows | Promote to composite action here |
| Composite action drift between repos | Tighten inputs, ship a new minor |
| Reusable workflow has too many inputs | Split into smaller composite actions called by the workflow |

## Anti-patterns

- A reusable workflow that wraps a single step → make it a composite action.
- A composite action that defines its own triggers → it can't; that's a workflow.
- Pinning `@main` in production → always pin `@v1` (or a specific tag).
- Leaking secrets through `inputs` → use `secrets:` in reusable workflows.

## References

- Issue #20 — audit and improvement plan
- `chrysa/shared-standards` — reusable workflows source of truth
- `EXECUTION_STANDARD.md` (in `shared-standards`) — CI requirements
