# scripts

**Role.** Shell entrypoints for the composite actions in this repo. A step in an
`action.yml` is a `uses:` or a one-line `run:`; anything longer lives here.

## Structure

| Path              | Purpose                                        |
| ----------------- | ---------------------------------------------- |
| `lint_yaml.sh`    | yamllint over the repo's YAML (`lint-yaml`)    |
| `lint_bash.sh`    | shellcheck + shfmt (`lint-bash`)               |
| `lint_docker.sh`  | hadolint over Dockerfiles (`lint-docker`)      |
| `lint_helm.sh`    | `helm lint --strict` per chart (`lint-helm`)   |

## Should contain

- Bash entrypoints called by exactly one composite action, parameterised through
  environment variables the action declares as `inputs`.

## Should NOT contain

- Python logic — that goes in a package like `notion_sync/`, with tests.
- Anything a maintained public action already does — reuse it instead.

## Rules

- `set -euo pipefail`, `shellcheck --severity=error` clean, `shfmt -i 4`.
- Inputs arrive as env vars with a default (`${VAR:-default}`); no positional args.
- An empty match set exits 0 with a message, never fails the job.
