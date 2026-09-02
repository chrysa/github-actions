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
