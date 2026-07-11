# Self-hosted CI for the chrysa fleet — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run private-repo CI on self-hosted ARC runners on the `ducal.me` k8s cluster so the chrysa fleet stops consuming billable GitHub-hosted Actions minutes, keeping public repos on the free hosted tier.

**Architecture:** Deploy Actions Runner Controller (`gha-runner-scale-set`, Kubernetes mode, ephemeral pods) as ArgoCD-managed catalog apps. Flip the centralized reusable workflows in `chrysa/github-actions` to a parametrized `runs-on` (default self-hosted label `chrysa-arc`, override `ubuntu-latest` for public repos), bump to `v1.3.0`, and roll out across private repos with doc-gen as the pilot. Fold in workflow-consumption hygiene.

**Tech Stack:** Kubernetes, Helm, ArgoCD, Actions Runner Controller (ARC) `gha-runner-scale-set`, Docker buildx (DinD), GitHub Actions reusable workflows, GitHub App auth.

## Global Constraints

- Self-hosted runners cover **private repos only**; public repos keep `runs-on: ubuntu-latest`.
- Runner scale set label (verbatim): **`chrysa-arc`**.
- Runners are **ephemeral** (one job per pod, container/Kubernetes mode).
- Image builds use **Docker buildx via DinD** (privileged scoped to build step), not Kaniko.
- Runner auth via a **GitHub App** (org-installed), not a PAT, except an optional bring-up bridge.
- Reusable-workflow version bump target: **`v1.2.x → v1.3.0`**.
- Catalog apps follow the existing convention: Helm `Chart.yaml` + `values.yaml` per app under `catalog/apps/dev/`, reconciled by ArgoCD; secrets under `catalog/secrets/dev` follow the existing sealing pattern.
- All workflow YAML must pass `actionlint` before commit.
- Commit style: Conventional Commits, English, trailer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.

---

## Phase 0 — Prerequisites (human-gated, blocking)

### Task 0: Gather cluster + org facts and credentials

**Files:** none (collects values consumed by Tasks 1–3).

**Interfaces:**
- Produces: `CLUSTER_FACTS` — CPU/RAM headroom on `ducal.me`, ArgoCD app-of-apps path, ingress/namespace conventions; `GH_APP` — App ID, installation ID, private key (PEM); `ORG = chrysa`.

- [ ] **Step 1 (human): Clear the billing suspension.** In GitHub → org `chrysa` → Settings → Billing & plans: resolve the failed payment / raise the limit enough that the org is **not in a payment-suspended state**. Rationale: a declined-payment suspension disables Actions *including self-hosted runners*; spending-limit-only blocks do not. Verify by re-running any workflow (`gh run rerun <id> -R chrysa/doc-gen`) and confirming it leaves `startup_failure`.

- [ ] **Step 2 (human): Create the GitHub App for ARC.** Org-level App with permissions: Actions (read/write), Administration (read/write, for runner registration), Metadata (read); installed on the `chrysa` org. Record App ID + Installation ID, generate a private key PEM. (Bring-up bridge: a classic PAT with `admin:org` + `repo` may be used for the very first controller test, then replaced by the App.)

- [ ] **Step 3 (human): Capture cluster facts.** Confirm `kubectl` context for `ducal.me`, the ArgoCD app-of-apps generator path in `catalog`, free CPU/RAM for ~4 runner pods, and the storage/secrets convention (sealed-secrets vs SOPS vs ESO) by inspecting `catalog/secrets/dev`.

- [ ] **Step 4: Record facts** into `catalog/apps/dev/arc-runner-set/NOTES.md` (created in Task 2) — defer writing until that dir exists; for now keep them in the working notes.

**Verification:** `gh run rerun` on a doc-gen workflow no longer returns `startup_failure` (billing cleared); GitHub App credentials in hand; cluster context reachable (`kubectl cluster-info`).

---

## Phase 1 — ARC controller (catalog)

### Task 1: Add the ARC controller as a catalog app

**Files:**
- Create: `catalog/apps/dev/arc-controller/Chart.yaml`
- Create: `catalog/apps/dev/arc-controller/values.yaml`
- Create: `catalog/apps/dev/arc-controller/README.md`
- Modify: ArgoCD app-of-apps generator (path discovered in Task 0 Step 3) if apps are not auto-discovered.

**Interfaces:**
- Consumes: `CLUSTER_FACTS` (namespace conventions).
- Produces: a running `gha-runner-scale-set-controller` in namespace `arc-system`; CRDs `autoscalingrunnersets.actions.github.com` available for Task 2.

- [ ] **Step 1: Write `Chart.yaml`** wrapping the upstream controller chart.

```yaml
apiVersion: v2
name: arc-controller
description: "Actions Runner Controller (gha-runner-scale-set) — chrysa self-hosted CI"
type: application
version: 1.0.0
dependencies:
  - name: gha-runner-scale-set-controller
    repository: oci://ghcr.io/actions/actions-runner-controller-charts
    version: 0.12.1
```

- [ ] **Step 2: Write `values.yaml`** (controller is light; pin the namespace).

```yaml
gha-runner-scale-set-controller:
  fullnameOverride: arc
  replicaCount: 1
  flags:
    logLevel: info
```

- [ ] **Step 3: Vendor the dependency.** Run: `helm dependency build catalog/apps/dev/arc-controller`. Expected: `Chart.lock` written, `charts/` populated.

- [ ] **Step 4: Render-test locally.** Run: `helm template arc-controller catalog/apps/dev/arc-controller -n arc-system | head -40`. Expected: a Deployment named `arc-...` renders with no template errors.

- [ ] **Step 5: Commit.**

```bash
git add catalog/apps/dev/arc-controller
git commit -m "feat(catalog): add ARC controller app (self-hosted CI)"
```

- [ ] **Step 6 (human/GitOps): Sync via ArgoCD.** Merge to catalog `main`; confirm the `arc-controller` Application reaches `Synced/Healthy` and the controller pod is `Running` in `arc-system` (`kubectl -n arc-system get pods`).

**Verification:** `kubectl get crd | grep actions.github.com` lists the runner-scale-set CRDs; controller pod Running.

---

## Phase 2 — Runner scale set + image-build capability

### Task 2: Add the `chrysa-arc` runner scale set with DinD

**Files:**
- Create: `catalog/apps/dev/arc-runner-set/Chart.yaml`
- Create: `catalog/apps/dev/arc-runner-set/values.yaml`
- Create: `catalog/apps/dev/arc-runner-set/NOTES.md`
- Create: `catalog/secrets/dev/arc-github-app.yaml` (sealed per the existing pattern from Task 0 Step 3)

**Interfaces:**
- Consumes: `GH_APP` (App ID, installation ID, private key); the controller + CRDs from Task 1.
- Produces: an org-registered runner scale set named **`chrysa-arc`** that jobs target with `runs-on: chrysa-arc`.

- [ ] **Step 1: Seal the GitHub App secret.** Using the sealing tool identified in Task 0 (e.g. `kubeseal`), create `catalog/secrets/dev/arc-github-app.yaml` holding keys `github_app_id`, `github_app_installation_id`, `github_app_private_key` in namespace `arc-runners`. Do NOT commit the plaintext key.

- [ ] **Step 2: Write `Chart.yaml`.**

```yaml
apiVersion: v2
name: arc-runner-set
description: "chrysa-arc ephemeral runner scale set (DinD buildx) — self-hosted CI"
type: application
version: 1.0.0
dependencies:
  - name: gha-runner-scale-set
    repository: oci://ghcr.io/actions/actions-runner-controller-charts
    version: 0.12.1
```

- [ ] **Step 3: Write `values.yaml`** — org scope, label `chrysa-arc`, DinD mode for buildx, min=0/max=4.

```yaml
gha-runner-scale-set:
  runnerScaleSetName: chrysa-arc
  githubConfigUrl: https://github.com/chrysa
  githubConfigSecret: arc-github-app
  minRunners: 0
  maxRunners: 4
  containerMode:
    type: dind
  template:
    spec:
      containers:
        - name: runner
          image: ghcr.io/actions/actions-runner:latest
          command: ["/home/runner/run.sh"]
```

- [ ] **Step 4: Vendor + render-test.** Run: `helm dependency build catalog/apps/dev/arc-runner-set && helm template arc-runner-set catalog/apps/dev/arc-runner-set -n arc-runners | grep -A2 runnerScaleSetName`. Expected: renders with `runnerScaleSetName: chrysa-arc`, no errors.

- [ ] **Step 5: Write `NOTES.md`** capturing `CLUSTER_FACTS` from Task 0 and the min/max rationale.

- [ ] **Step 6: Commit.**

```bash
git add catalog/apps/dev/arc-runner-set catalog/secrets/dev/arc-github-app.yaml
git commit -m "feat(catalog): add chrysa-arc runner scale set (DinD buildx)"
```

- [ ] **Step 7 (human/GitOps): Sync + verify registration.** After ArgoCD sync, confirm the scale set appears under org `chrysa` → Settings → Actions → Runners (`gh api /orgs/chrysa/actions/runner-groups` or the UI), and the listener pod is Running in `arc-runners`.

**Verification:** `chrysa-arc` listed as an org runner scale set; listener pod Running; `minRunners=0` so no idle runner pods.

---

## Phase 3 — Prove the runner works

### Task 3: Hello-world job on `chrysa-arc`

**Files:**
- Create (temp): `chrysa/github-actions/.github/workflows/arc-smoke.yml` (on a throwaway branch; removed after).

**Interfaces:**
- Consumes: the live `chrysa-arc` scale set.
- Produces: evidence a job schedules onto a self-hosted runner and that buildx works.

- [ ] **Step 1: Write the smoke workflow.**

```yaml
name: ARC smoke
on: workflow_dispatch
jobs:
  hello:
    runs-on: chrysa-arc
    steps:
      - run: echo "running on $(hostname)"; cat /etc/os-release | head -1
  buildx:
    runs-on: chrysa-arc
    steps:
      - uses: docker/setup-buildx-action@v3
      - run: docker buildx version && docker run --rm hello-world
```

- [ ] **Step 2: Dispatch + observe.** Run: `gh workflow run "ARC smoke" -R chrysa/github-actions && sleep 20 && gh run list -R chrysa/github-actions -L 1`. Expected: a runner pod spins up in `arc-runners` (`kubectl -n arc-runners get pods -w`), the run reaches `success`, NOT `startup_failure`.

- [ ] **Step 3: Confirm zero hosted minutes.** The run's billing shows 0 GitHub-hosted minutes (self-hosted jobs are unbilled).

- [ ] **Step 4: Remove the smoke workflow + commit.**

```bash
git rm .github/workflows/arc-smoke.yml
git commit -m "chore(ci): remove ARC smoke workflow (validated)"
```

**Verification:** both `hello` and `buildx` jobs green on `chrysa-arc`; ephemeral pod created then destroyed.

---

## Phase 4 — Parametrize the reusable workflows

### Task 4: Add a `runner` input to every reusable workflow and bump to v1.3.0

**Files:**
- Modify: each `chrysa/github-actions/.github/workflows/*.yml` that has `runs-on: ubuntu-latest` (inventory: `ci.yml`, `ci-python.yml`, `ci-python-app.yml`, `ci-fullstack.yml`, `lint-python.yml`, `secret-scan.yml`, `release.yml`, `deploy.yml`, `quality-gate-check.yml`, `mutation-testing.yml`, `pages.yml`, `sonar.yml`, `dependencies.yml`, `enforce-feature-branch.yml`, and the cosmetic ones).
- Modify: `shared-standards/workflows/*.yml` mirrors (`ci-python.yml`, `ci-node.yml`, `sonar.yml`, `secret-scan.yml`, `pages.yml`, `labeler.yml`, `pr-size.yml`, `notion-*`).

**Interfaces:**
- Consumes: nothing.
- Produces: reusable workflows whose runner is `${{ inputs.runner }}` defaulting to `chrysa-arc`; tag `v1.3.0`. Callers that omit `runner` get self-hosted; public-repo callers pass `runner: ubuntu-latest`.

- [ ] **Step 1: Add the input to one workflow (`ci-python.yml`) as the pattern.** In its `on.workflow_call.inputs` block add:

```yaml
    inputs:
      runner:
        description: "runs-on label (chrysa-arc self-hosted, or ubuntu-latest for public repos)"
        type: string
        default: chrysa-arc
```

and change the job's `runs-on: ubuntu-latest` → `runs-on: ${{ inputs.runner }}`.

- [ ] **Step 2: Lint it.** Run: `actionlint .github/workflows/ci-python.yml`. Expected: no errors.

- [ ] **Step 3: Apply the same edit to every remaining reusable workflow** with a `runs-on: ubuntu-latest`. Each gets the identical `runner` input (verbatim block above) and `runs-on: ${{ inputs.runner }}`. For workflows already taking inputs, append `runner` to the existing `inputs:` map.

- [ ] **Step 4: Lint all.** Run: `actionlint .github/workflows/*.yml`. Expected: clean.

- [ ] **Step 5: Mirror into `shared-standards/workflows`.** Apply the same `runner` input + default to each template there so freshly-distributed repos inherit it.

- [ ] **Step 6: Add an ADR.** Append to `chrysa/github-actions/DECISIONS.md` a `D-00XX — self-hosted runner default (chrysa-arc), public repos override to ubuntu-latest` entry (the ADR-gate pre-commit hook requires it on workflow architecture changes).

- [ ] **Step 7: Commit + tag.**

```bash
git add .github/workflows DECISIONS.md
git commit -m "feat(ci): parametrize runs-on (chrysa-arc default) for self-hosted runners"
git tag v1.3.0
```

(Push + tag publish happen after the pilot in Task 5 confirms the contract.)

**Verification:** `actionlint` clean on all workflows; every job's `runs-on` is `${{ inputs.runner }}`; `git show v1.3.0 --stat` lists all edited workflows.

---

## Phase 5 — Pilot on doc-gen

### Task 5: Migrate doc-gen to self-hosted and validate the publish chain

**Files:**
- Modify: `chrysa/doc-gen/.github/workflows/*.yml` — bump `@v1.2.x → @v1.3.0` on every `uses: chrysa/github-actions/...` reference.

**Interfaces:**
- Consumes: the published `v1.3.0` reusable workflows; the live `chrysa-arc` scale set.
- Produces: evidence that PR CI + a release publish `ghcr.io/chrysa/doc-gen` on self-hosted runners.

- [ ] **Step 1: Publish `v1.3.0`.** Push the Task 4 branch + tag: `git push origin <branch> && git push origin v1.3.0` (admin-merge the PR first if the repo gates it; CI is now self-hosted so it should run).

- [ ] **Step 2: Bump doc-gen callers.** In each doc-gen workflow, replace `@v1.2.1`/`@v1.2.3` with `@v1.3.0`. Leave no `runner:` override (doc-gen is private → inherits `chrysa-arc`).

- [ ] **Step 3: Open a doc-gen PR and watch CI.** Run: `gh pr create ...` then `gh run list -R chrysa/doc-gen -L 5`. Expected: `ci`, `secret-scan`, `quality-gate` jobs run on self-hosted runners and go green (not `startup_failure`).

- [ ] **Step 4: Validate the publish chain.** Merge, then cut a release (the existing `release.yml` → `publish.yml` on `v*`). Expected: `publish.yml` builds and pushes `ghcr.io/chrysa/doc-gen` via buildx on a self-hosted runner.

- [ ] **Step 5: Confirm the image.** Run: `gh api /orgs/chrysa/packages/container/doc-gen/versions --jq '.[0].metadata.container.tags'`. Expected: the new tag present.

- [ ] **Step 6: Commit the caller bump.**

```bash
git add .github/workflows
git commit -m "ci: adopt v1.3.0 reusable workflows (self-hosted runners)"
```

**Verification:** doc-gen PR CI green on `chrysa-arc`; `ghcr.io/chrysa/doc-gen` has a fresh tag built by a self-hosted runner; 0 hosted minutes billed.

---

## Phase 6 — Fleet rollout + billing zero

### Task 6: Roll v1.3.0 across private repos and cap hosted spend

**Files:**
- Modify: `.github/workflows/*.yml` in each remaining **private** repo (dev-nexus, devtool, catalog, +others) — bump to `@v1.3.0`.
- Modify: each **public** repo caller (guideline-checker, +public) — bump to `@v1.3.0` AND pass `runner: ubuntu-latest`.

**Interfaces:**
- Consumes: validated `v1.3.0`.
- Produces: the whole fleet on `v1.3.0`; private on self-hosted, public on hosted.

- [ ] **Step 1: Bump private repos.** For each private repo, replace `@v1.2.x` → `@v1.3.0` (no runner override). Distribute via the existing standards-sync mechanism (one PR per repo). Verify each repo's CI runs on `chrysa-arc`.

- [ ] **Step 2: Bump public repos with override.** For each public repo, bump to `@v1.3.0` and add `runner: ubuntu-latest` to the `with:` of each `uses:` call. Verify CI still runs on hosted (free) runners.

- [ ] **Step 3 (human): Set hosted spending limit to $0.** Org Billing → set the GitHub-hosted Actions spending limit to $0. Private repos now run only on the cluster; public repos use the free hosted allotment.

- [ ] **Step 4: Fleet smoke.** Trigger a no-op PR on 2–3 private repos; confirm green on `chrysa-arc`. Trigger one on guideline-checker; confirm green on `ubuntu-latest`.

**Verification:** private-repo runs schedule on `chrysa-arc`; public-repo runs on `ubuntu-latest`; hosted spending limit $0; no `startup_failure` anywhere.

---

## Phase 7 — Consumption hygiene (axis C)

### Task 7: Cut workflow load (concurrency, path filters, consolidation)

**Files:**
- Modify: `chrysa/github-actions/.github/workflows/*.yml` and `shared-standards/workflows/*.yml`.

**Interfaces:**
- Consumes: the `v1.3.0` workflows.
- Produces: `v1.3.1` with reduced redundant runs.

- [x] **Step 1: Add concurrency cancel** to the PR-triggered CI workflows (done 2026-07-11,
  independent of the ARC rollout — helps billable-minute load now):

```yaml
concurrency:
  group: <workflow>-${{ github.ref }}   # hardcoded per-file prefix, NOT github.workflow
  cancel-in-progress: true
```

Note: the plan's original `${{ github.workflow }}` prefix is wrong for *reusable*
(`workflow_call`) workflows — there it resolves to the *caller*, so two reusables
invoked by one caller would share a group and cancel each other. Each file uses a
hardcoded unique prefix instead. Applied to `ci`, `lint-python`, `pre-commit`,
`quality-gate-check`, `secret-scan`, `mutation-testing` (cancel-in-progress: true);
`release` gets `cancel-in-progress: false` (serialise, never cancel a running
release). `actionlint` clean. Tagging/distribution stays with the ARC rollout.

- [ ] **Step 2: Add path filters** to the language CI workflows (Python CI ignores frontend/docs-only diffs; Node CI ignores backend-only diffs) via `on.pull_request.paths` in the *caller* templates in `shared-standards/workflows`.

- [ ] **Step 3: Lower Dependabot load.** In the distributed `dependabot.yml` template, set `schedule.interval: weekly` and ensure update grouping is on.

- [ ] **Step 4: Audit cosmetic workflows.** Document (in `DECISIONS.md`) a proposal to merge `labeler` + `sync-labels` + `pull-request-size` + `update-pr-body` + `auto-assign` into one `pr-housekeeping.yml`. Implement the merge in `shared-standards/workflows`.

- [ ] **Step 5: Lint + tag.** Run: `actionlint .github/workflows/*.yml`. Then `git commit` + `git tag v1.3.1`.

- [ ] **Step 6: Distribute** `v1.3.1` to the fleet via standards-sync.

**Verification:** superseded PR runs auto-cancel; docs-only PRs skip language CI; one consolidated housekeeping workflow replaces five; `actionlint` clean.

---

## Self-review notes

- **Spec coverage:** §1 problem → Task 0; §2 D1 split → Tasks 4/6; D2 ARC → Tasks 1/2; D3 buildx → Tasks 2/3; D4 centralized switch → Task 4; D5 billing → Tasks 0/6. §3 architecture → Tasks 1/2. §5 hygiene → Task 7. §6 security (ephemeral, private-only, App auth) → Tasks 2/3/6. §7 rollout/exit → Tasks 5/6. All covered.
- **Human-gated steps** are explicitly marked (billing, GitHub App, ArgoCD sync, spending limit) — they cannot be automated by the worker and block the tasks that consume them.
- **Open questions (spec §9)** are resolved inside Task 0 (cluster facts, App-vs-PAT bring-up, GHCR storage check).
