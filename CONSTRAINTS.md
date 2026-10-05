# CONSTRAINTS — github-actions

Operating constraints for this repository. Each tagged **FACT** (verified),
**INFERENCE** (reasoned), or **UNKNOWN**.

## Platform & runtime

- **C1 (FACT)** — Composite actions run on GitHub-hosted runners with `shell: bash`.
- **C2 (FACT)** — Python floor is **3.12** (`pyproject.toml requires-python`).
- **C3 (FACT)** — Packaged Python is limited to the `notion_sync` package
  (`[tool.setuptools] packages = ["notion_sync"]`); other Python (`scripts/`) is
  not installed as a package.

## Consumption model

- **C4 (FACT)** — Consumers pin the floating major tag `@v1`; **only the latest
  major is supported** (SECURITY.md, docs/reference). Breaking a `v1` action
  breaks the whole fleet at once.
- **C5 (FACT)** — `secrets: inherit` is forbidden; callers must name each secret.
- **C6 (INFERENCE)** — Because actions run in *consumer* CI with the caller's
  `GITHUB_TOKEN` and secrets, any leak/log/exfiltration is a fleet-wide incident;
  this raises the bar on input handling and third-party `uses`.

## Process constraints

- **C7 (FACT)** — Lint is owned by pre-commit and replayed in CI only at release
  time to control Actions billing (DECISIONS D-0002). Do not re-add per-push lint
  without a superseding ADR.
- **C8 (FACT)** — Conventional commits + branch-prefix naming (`feat/ fix/ chore/
  refactor/ docs/`) are required; GitVersion keys increments off these prefixes.
- **C9 (FACT)** — Changelog is generated (`cliff.toml`); do not hand-edit
  generated changelog sections.

## Standards constraints (from CLAUDE.md / vendored `standards/rules/`)

- **C10 (FACT)** — chrysa canon: *"GitHub Actions — reuse first · custom actions
  centralised · thin workflows"* — this repo **is** that central store.
- **C11 (INFERENCE)** — chrysa canon: *"every tracked file and folder must earn
  its place."* Large tracked artefacts (`graphify` 11 MB, `sys` 33 MB,
  `graphify-out/`, `guideline-report.html`) sit in tension with this; disposition
  is **UNKNOWN** — flagged in [REVIEW.md](REVIEW.md).
- **C12 (FACT)** — On-disk language is English (chrysa language rule); a hookify
  local rule warns on French in files.

## Not applicable

- No web/frontend runtime, no database, no deployed service surface — so no PRD,
  no data-model, no observability-of-a-running-app doc (the repo *provides* the
  observability workflows to others). Recorded as skipped in [REVIEW.md](REVIEW.md).
