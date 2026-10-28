---
name: add-python-entrypoint
description: "Add a Python-backed action entrypoint plus its pytest counterpart under tests/, following this repo's existing pattern (branch_sync, notion_api, roadmap_sync, sync_entrypoints, quality_gate)."
when_to_use: "add a python script for an action, new python entrypoint, python-backed composite action"
disable-model-invocation: true
---

# Add Python Entrypoint

Add a new Python script that backs a composite action, plus its pytest test
file, following the existing convention (see `scripts/quality_gate.py` +
`tests/test_sync_entrypoints.py`, `tests/test_notion_api.py`,
`tests/test_branch_sync.py`, `tests/test_roadmap_sync.py` for reference).

## Steps

1. Add the script under `scripts/<name>.py`. Keep it a single-purpose,
   testable module — no side effects on import, a `main()`/callable entry
   point the tests can call directly.
2. Add `tests/test_<name>.py` mirroring the style of the existing
   `test_*_sync.py` / `test_notion_api.py` files: mock all network/filesystem
   I/O, one test class, parametrize happy/error paths.
3. Wire the script into its action's `action.yml` `runs.steps` (a `run: python
   scripts/<name>.py ...` step, `shell: bash`).
4. Validate:
   - `ruff check scripts/<name>.py`
   - `pytest tests/test_<name>.py`
   - `actionlint <action-dir>/action.yml` if the action.yml changed

## Checklist

- [ ] Script under `scripts/`, no top-level side effects
- [ ] Matching `tests/test_<name>.py`, all I/O mocked
- [ ] Action step wired in the relevant `action.yml`
- [ ] `ruff check` + `pytest` pass
