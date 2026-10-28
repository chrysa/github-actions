---
name: new-composite-action
description: "Scaffold a new composite GitHub Action the repo's way: kebab-case directory, action.yml with description/inputs/runs.steps, README stub, actionlint + shellcheck clean."
when_to_use: "add a new action, new composite action, scaffold an action.yml"
disable-model-invocation: true
---

# New Composite Action

Add a new action directory following this repo's existing convention (see
`ruff-check/action.yml`, `lint-bash/action.yml`, `tool-setup/action.yml` for
reference examples).

## Steps

1. Pick a kebab-case directory name at repo root, e.g. `my-new-action/`.
2. Create `my-new-action/action.yml`:
   - `name`: human-readable title.
   - `description`: one sentence, present tense ("Run X and upload Y").
   - `inputs`: each with `description` and `required`; add `default` for
     optional ones. Include a `working-directory` input (`default: .`) if the
     action can run inside a monorepo subdirectory, matching
     `ruff-check/action.yml`.
   - `runs.using: composite` and `runs.steps`, each step with `shell: bash`
     and `working-directory: ${{ inputs.working-directory }}` when relevant.
3. Add a `my-new-action/README.md` stub describing purpose, inputs, and a
   usage example (`uses: <org>/github-actions/my-new-action@<ref>`).
4. No test file edit needed — `tests/test_actions_yaml.py` auto-discovers
   every `*/action.yml` via `REPO_ROOT.glob("*/action.yml")` and validates it
   has `name`, `description`, and `runs`.
5. Validate before committing:
   - `actionlint my-new-action/action.yml`
   - `shellcheck` on any inline multi-line `run:` block extracted to a temp
     `.sh` file, or on any `scripts/*.sh` the action calls.
   - `pytest tests/test_actions_yaml.py -k my-new-action`

## Checklist

- [ ] Directory is kebab-case, action lives at `<dir>/action.yml`
- [ ] `name` + `description` + every input documented
- [ ] `working-directory` input present if action can run in a subdirectory
- [ ] README stub added
- [ ] `actionlint` passes
- [ ] `shellcheck` passes on any shell steps
- [ ] `pytest tests/test_actions_yaml.py` passes (no edit needed to that file)
