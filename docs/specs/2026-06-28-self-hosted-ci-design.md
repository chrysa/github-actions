# Design — Self-hosted CI for the chrysa fleet

> Date: 2026-06-28 · Status: approved (brainstorming) · Owner repo: `chrysa/github-actions`
> Goal: exit GitHub Actions billing for the private-repo fleet by running CI on
> self-hosted runners on the existing `ducal.me` Kubernetes cluster, while keeping
> public repos on the free GitHub-hosted tier.

## 1. Problem

The chrysa org's GitHub Actions are **billing-blocked fleet-wide**: every job fails in
seconds with `startup_failure` and the annotation *"the job was not started because
recent account payments have failed or your spending limit needs to be increased."*
This blocks all CI — including the `publish.yml` chain that should produce
`ghcr.io/chrysa/doc-gen`, and the merge gates on every repo.

Confirmed scope (2026-06-28): dev-nexus, doc-gen, devtool, guideline-checker and
catalog all fail identically. 51 private + 32 public repos in the org. The four active
projects: dev-nexus, doc-gen, devtool are **private**; guideline-checker is **public**.

The user's directive: **stop paying for GitHub Actions**. Self-hosted runners are
therefore mandatory, not optional.

## 2. Key decisions

### D1 — Public/private split (load-bearing)
- **Private repos → self-hosted runners** on the cluster. They are the only ones that
  consume paid GitHub-hosted minutes; moving them to owned compute drives Actions cost
  to ~0.
- **Public repos stay on GitHub-hosted** (`ubuntu-latest`). Public repos already get
  unlimited free GitHub-hosted Actions, AND keeping them off the cluster avoids
  executing untrusted PR/fork code on owned infrastructure. Double win.

### D2 — ARC (Actions Runner Controller), Kubernetes mode
Use the official `gha-runner-scale-set` controller + scale set (the modern ARC, not the
deprecated `RunnerDeployment` CRDs). Runners are **ephemeral** (one job = one throwaway
pod). Deployed as a catalog app managed by ArgoCD, consistent with the rest of the fleet.

### D3 — Image builds via Docker buildx (DinD)
`publish.yml` / `deploy.yml` build container images, so runners need Docker. Start with
**Docker-in-Docker (buildx)** for drop-in compatibility with existing Dockerfiles,
accepting a privileged build sidecar scoped to the build step. (Rootless Kaniko/buildah
is a future hardening option, not in this scope.)

### D4 — Centralized switch
Reusable workflows live in `chrysa/github-actions/.github/workflows/*.yml` and are
consumed as `uses: chrysa/github-actions/.github/workflows/<wf>.yml@vX`. This is the
**single point** to change `runs-on`. Templates are mirrored in
`shared-standards/workflows`. A `runner` input (default self-hosted label) lets public
repos keep `ubuntu-latest`.

### D5 — Billing hygiene (user action, not code)
1. Clear any **failed-payment suspension** in the GitHub org Billing settings — a
   declined-payment state disables Actions entirely, *including self-hosted runners*, so
   this must be cleared first.
2. Set the **GitHub-hosted spending limit to $0** once private repos are off it. Public
   repos remain free; private repos run on the cluster.

## 3. Architecture

```
GitHub (chrysa org)
  │  webhook / long-poll (GitHub App auth)
  ▼
ducal.me k8s cluster
  ├── arc-system ns
  │     └── gha-runner-scale-set-controller   (Helm)
  └── arc-runners ns
        └── runner scale set "chrysa-arc"     (Helm)
              ├── listener (1 replica)
              └── ephemeral runner pods (0..N, min=0, max=~4)
                    └── dind sidecar (buildx) for image jobs
```

- **Registration scope:** org-level runner scale set, so every private repo can target
  it with `runs-on: chrysa-arc` without per-repo registration.
- **Auth:** a dedicated **GitHub App** (org-installed) — preferred over a PAT for
  scoped, rotatable credentials. App private key + IDs stored as a sealed/managed secret
  under `catalog/secrets/dev` (follow the existing secret pattern in catalog).
- **GitOps:** new app(s) under `catalog/apps/dev/` (e.g. `arc-controller`,
  `arc-runner-set`) using the catalog's Helm-chart-per-app convention (bjw-s-style
  `Chart.yaml` + `values.yaml`), reconciled by ArgoCD like every other app.

## 4. Components

| Component | Where | Purpose |
|---|---|---|
| `arc-controller` chart | `catalog/apps/dev/arc-controller` | Installs the ARC controller (`gha-runner-scale-set-controller`). |
| `arc-runner-set` chart | `catalog/apps/dev/arc-runner-set` | The `chrysa-arc` scale set: image, DinD, min/max, GitHub App secret ref. |
| GitHub App secret | `catalog/secrets/dev` | App ID, installation ID, private key for runner registration. |
| Reusable workflow edits | `chrysa/github-actions/.github/workflows/*` | `runs-on` → `${{ inputs.runner || 'chrysa-arc' }}`; bump to `v1.3.0`. |
| Template edits | `shared-standards/workflows/*` | Mirror the `runner` input + default. |
| Per-repo sync PRs | each private repo | Bump `@v1.2.x → @v1.3.0`; public repos pass `runner: ubuntu-latest`. |

## 5. Workflow consumption hygiene (axis C, folded in)

Even on owned compute, ~20 workflows/repo is wasteful. Reduce load:
- **`concurrency: { group, cancel-in-progress: true }`** on all PR-triggered workflows —
  cancels superseded runs.
- **Path filters** — skip the Python CI on docs/frontend-only diffs and vice-versa.
- **Dependabot batching** — group updates (partly done) and lower frequency to weekly.
- **Consolidate cosmetic workflows** — `labeler`, `sync-labels`, `pull-request-size`,
  `update-pr-body`, `auto-assign` are candidates to merge into one "PR housekeeping"
  workflow. (Audit + proposal; execution per-repo via the standards sync.)

## 6. Security

- **Ephemeral runners** — each job runs in a fresh pod, destroyed after; no state leaks
  between jobs.
- **Private repos only** on the cluster — fork/PR code from the public repo never runs
  on owned infra (D1).
- **DinD privilege** is scoped to the build sidecar; non-build jobs run unprivileged.
- **GitHub App** credentials over PAT; private key sealed in catalog secrets, rotatable.
- Runner pods get **no cluster-admin**; namespace-scoped, network-policied away from
  other workloads where feasible.

## 7. Rollout & exit criteria

1. **Infra up:** ARC controller + `chrysa-arc` scale set reconciled by ArgoCD; a hello
   job on `runs-on: chrysa-arc` succeeds.
2. **Pilot = doc-gen:** switch doc-gen's callers to `v1.3.0` (self-hosted). Validate the
   full chain: PR CI green, then a release produces **`ghcr.io/chrysa/doc-gen`** built by
   a self-hosted runner via buildx.
3. **Fleet rollout:** sync `v1.3.0` to the remaining private repos (one PR each).
4. **Billing:** clear failed-payment state; set GitHub-hosted spending limit to $0.

**Exit criteria:** a doc-gen release publishes its image to GHCR through a self-hosted
runner, with **0 billable GitHub-hosted minutes** consumed by the private fleet, and all
private-repo merge gates green again.

## 8. Out of scope

- Rootless image builds (Kaniko/buildah) — future hardening.
- Migrating public repos to self-hosted — intentionally kept GitHub-hosted (D1).
- Autoscaling tuning beyond a sane min=0/max=~4 — revisit if queue latency hurts.
- Replacing SonarCloud / external SaaS gates — orthogonal to runner location.

## 9. Open questions (resolve during planning)

- Exact cluster resources available for runner pods (CPU/RAM headroom on `ducal.me`).
- Whether the GitHub App can be created now, or a PAT bridge is needed for the first
  bring-up.
- GHCR private-package storage billing — minor, but confirm it isn't a second paywall
  once Actions minutes are gone.
