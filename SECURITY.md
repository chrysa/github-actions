# Security Policy

## Supported versions

This repository publishes composite GitHub Actions consumed across the chrysa
fleet. Only the latest major tag is supported; consumers pin to the floating
major (`@v1`), never to `@main`.

| Version | Supported |
| ------- | --------- |
| `v1` (latest) | ✅ |
| older majors | ❌ |

## Reporting a vulnerability

**Do not open a public issue for a security problem.**

Report privately through GitHub's
[private vulnerability reporting](https://github.com/chrysa/github-actions/security/advisories/new)
(Security → Advisories → *Report a vulnerability*).

Include:

- the affected action and version/ref,
- a reproduction (workflow snippet, inputs, logs with secrets redacted),
- the impact you observed or expect.

Never include secret values in a report — name the file and line instead.

## Response

- Acknowledgement within **3 business days**.
- Triage and a remediation plan within **10 business days** for confirmed issues.
- Fixes ship on the supported major; consumers pinned to `@v1` receive them
  automatically once the floating tag is moved.

## Scope

These actions run in consumer CI with the caller's `GITHUB_TOKEN` and secrets.
Secrets are always named explicitly by the caller; `secrets: inherit` is
forbidden. Report any action that leaks, logs, or exfiltrates caller secrets,
or that executes untrusted input, as a vulnerability.

This policy follows the chrysa
[security standard](https://github.com/chrysa/dev-kit/blob/main/standards/STANDARDS.md).

## Documentation-audit findings (2026-09-25, docs-only pass)

> Recorded by a documentation pass. **No code was changed.** Severities are the
> auditor's assessment for the repo owner to triage; none are confirmed exploits.
> No secrets were found hardcoded in `*/action.yml` or `.github/workflows/*`
> (searched for `ghp_`, `glpat_`, `AKIA`, PEM headers, inline tokens — none).

- **MEDIUM — third-party actions pinned to mutable tags, not commit SHAs.**
  `SonarSource/sonarqube-scan-action@v5` and `@v4.2.1`,
  `codecov/codecov-action@v6`, `EnricoMi/publish-unit-test-result-action@v2`,
  `gittools/actions/gitversion/{setup,execute}@v4.4.2`,
  `pypa/gh-action-pypi-publish@release/v1`, and `actions/*` are referenced by
  tag/branch. A moved tag on any of these runs new code in consumer CI. Consider
  SHA-pinning third-party `uses` (Dependabot can keep SHAs current).
  *Evidence:* `grep -rhoE "uses: [^ ]+@[^ ]+"` over `*/action.yml` and
  `.github/workflows/*` excluding 40-hex SHAs.

- **MEDIUM — internal references to `@main`.** At least one workflow uses
  `chrysa/github-actions/python-setup@main` and `.../install-project@main`,
  contradicting the SECURITY.md "never `@main`" statement for consumers.
  Confirm these are intentional (self-CI dogfooding) or pin to a tag.

- **LOW — `workflow_call` workflows without an explicit top-level
  `permissions:` block** (inherit the repo/caller default token scope):
  `action-check.yml`, `approved-label.yml`, `auto-assign.yml`,
  `detect-conflicts.yml`, `labeler.yml`, `pr-dependencies.yml`,
  `pull-request-size.yml`, `sync-labels.yml`, `update-pr-body.yml`.
  Add a least-privilege `permissions:` block to each.

These are also tracked in [REVIEW.md](REVIEW.md) and [REQUIREMENTS.md](REQUIREMENTS.md)
(REQ-TECH-015, REQ-TECH-016).
