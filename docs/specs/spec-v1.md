# github-actions · spec v1 · 2026-05-04

> Catalogue de workflows GitHub Actions réutilisables · consommé par tous repos chrysa via `uses: chrysa/github-actions/.github/workflows/<name>@main`.

## 1. Vue

`chrysa/github-actions` = repo dédié aux workflows GitHub Actions partagés. Sépare les "templates de workflows" (executable directly) de `shared-standards` (qui contient les conventions/templates non-exécutables).

Pourquoi 2 repos distincts : workflows réutilisables nécessitent `workflow_call` triggers + versioning tag-based. shared-standards = sources statiques. Pattern : `actions/checkout` à GitHub vs `actions/setup-python` etc.

Visibilité : 🌍 PUBLIC (Tier 1).

## 2. Stack

- YAML (workflow_call)
- GitHub Actions runtime (ubuntu-latest · ubuntu-22.04)
- Composite actions (`action.yml` dans sub-folders pour réutilisation step-level)
- Versioning : tags semver (`v1.0.0`) + branche `main` floating

## 3. Repo

`https://github.com/chrysa/github-actions` (public · MIT)
- main branch · squash merge · pre-commit YAML lint
- Tags semver via GitVersion
- README catalog complet (liste workflows + paramètres + exemples)

## 4. Données

Aucune persistance. Workflows = artefacts statiques YAML.

## 5. Communication

Consommé via :
```yaml
# Repo consommateur
jobs:
  test:
    uses: chrysa/github-actions/.github/workflows/ci-python-test.yml@v1
    with:
      python-version: '3.14'
      coverage-min: 85
```

## 6. Intégrations

- GitHub Actions Marketplace (publication composite actions Tier 1+ après maturity)
- SonarCloud (workflow `sonar-scan.yml`)
- PyPI / npm (workflow `release.yml`)
- Codecov (workflow `coverage-upload.yml`)
- pre-commit.ci (mirror config from shared-standards)

## 7. Infra

- GitHub-hosted runners (ubuntu-latest par défaut)
- Self-hosted runner Kimsufi en option (workflow heavy CI · gros builds Discordium)

## 8. ADR (`github-actions/DECISIONS.md`)

D-0001 · Repo séparé des autres standards (versioning workflows critique)
D-0002 · Versioning par tags semver (vs branche main floating)
D-0003 · ubuntu-22.04 pinned (vs ubuntu-latest mouvant)
D-0004 · Composite actions pour steps réutilisables vs duplication YAML
D-0005 · Self-hosted runner Kimsufi disponible (opt-in)
D-0006 · Workflows separés par stack (python · typescript · docker · release)
D-0007 · Codecov + SonarCloud upload steps standardisés
D-0008 · pre-commit.ci miroir (réutilise shared-standards config)

## 9. Hors-scope

- Pas de workflows projet-specifiques (chaque repo a les siens · ces workflows sont génériques)
- Pas de gestion secrets (chaque repo gère via GitHub Settings)
- Pas de release tooling (release.yml = wrapper · GitVersion fait le boulot)
- Pas de Docker registry hosting (GHCR = via GitHub natif)

## 📋 Workflows prévus catalog

| Workflow | Trigger | Description |
|---|---|---|
| `ci-python-test.yml` | workflow_call | pytest + coverage upload + ruff + mypy |
| `ci-typescript-test.yml` | workflow_call | vitest + coverage + eslint + tsc |
| `ci-docker-build.yml` | workflow_call | docker build + scan trivy + push GHCR |
| `release.yml` | workflow_call | GitVersion + tag + release notes + publish PyPI/npm |
| `sonar-scan.yml` | workflow_call | SonarCloud scan + quality gate |
| `coverage-upload.yml` | workflow_call | Codecov upload (Python + TS) |
| `dependabot-auto-merge.yml` | workflow_call | auto-merge dependabot PR si CI verte |
| `enforce-issue-link.yml` | pull_request | status check : PR doit ref Closes/Fixes #N (déjà mentionné CLAUDE.md) |
| `notion-sync.yml` | schedule + push | sync DB Projets ↔ repos (notion-sync-agent existant) |

## ✅ Décisions tranchées

- Pinned ubuntu-22.04 (pas latest)
- Tags semver versioning workflows
- Repo séparé de shared-standards (granularité versioning)

## 🟠 Décisions ouvertes

- [ ] Self-hosted runner : OS Linux (Kimsufi) · Docker-in-Docker possible ?
- [ ] enforce-issue-link comme reusable workflow OU GitHub App ?
  - Reco : reusable workflow (pas besoin GitHub App pour solo dev)

## 🎫 Ticket #1

```
title: feat: bootstrap github-actions catalog v1 (9 workflows réutilisables)
labels: feat · P0 · standards
description:
- [ ] Init repo + LICENSE MIT + README catalog
- [ ] 9 workflows ci-* + release + sonar + coverage
- [ ] enforce-issue-link.yml
- [ ] Tags v1.0.0 + GitVersion config
- [ ] Tester sur cobaye chrysa-lib-py
```

## 🚀 Action items

- [ ] Bootstrap repo après shared-standards stable
- [ ] Migrer workflows existants depuis repos individuels vers ce catalog
- [ ] Documenter usage dans `shared-standards/docs/workflows.md`
- [ ] Aligner CLAUDE.md projet
