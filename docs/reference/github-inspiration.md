# Deep-dive: `chrysa/github-actions`

**Repo local:** `/home/anthony/Documents/perso/projects/chrysa/github-actions`
**But (1 phrase):** Monorepo de ~22 composite GitHub Actions réutilisables (+ leurs entrypoints Python testés) partagés par toute la flotte `chrysa/*` — setup Python, lint (ruff/mypy/yaml/bash/docker/helm/terraform), tests+coverage, scans Sonar, publication PyPI/npm, sync Notion, gitversion, changelog, doc-drift, branch-policy.
**Licence projet:** MIT (Anthony Gréau, 2026) — sortie OSS possible sans contrainte.

Structure : un dossier par action avec `action.yml` (`using: composite`), logique lourde déportée dans `scripts/*.sh` + package `notion_sync/` testé sous `tests/` (pytest, coverage). `CLAUDE.md` (~99k) + `DECISIONS.md` documentent les conventions ; CI interne, pre-commit, git-cliff (`cliff.toml`), GitVersion (`GitVersion.yml`).

Ce projet est un **outillage CI interne** : il n'existe pas d'équivalent monolithique externe à copier, mais chaque action encapsule un outil OSS de référence. Les réfs ci-dessous sont les sources canoniques dont s'inspirer / qu'on wrappe déjà.

---

## pypa/gh-action-pypi-publish

- **owner/repo:** pypa/gh-action-pypi-publish
- **stars:** ~1.2k
- **activité:** très active (branche `release/v1` maintenue, `master` sunset), 427 commits
- **licence:** **BSD-3-Clause** (permissive — copiable/wrappable)
- **langage:** Python (Docker action)
- **fichier/module du pattern:** `oidc-exchange.py`, `attestations.py`, `action.yml` (inputs `repository-url`, `attestations`)
- **mécanisme réel:** publie `dist/*` vers PyPI en **Trusted Publishing OIDC** (tokenless) : échange le token OIDC GitHub contre un token PyPI court, upload via twine, génère des attestations Sigstore. Zéro secret long-terme.
- **snippet portable:**
  ```yaml
  - name: Publish to PyPI (OIDC Trusted Publishing)
    uses: pypa/gh-action-pypi-publish@release/v1
    with:
      repository-url: ${{ inputs.repository-url }}
  ```
- **intégration dans ce projet:** DÉJÀ intégré — `publish-python-package/action.yml` bascule sur cette action quand `pypi-token == ''` (branche OIDC), sinon fallback `twine upload` avec token. Caller doit accorder `permissions: id-token: write` + enregistrer le trusted publisher sur PyPI.
- **gotchas:** le job appelant DOIT déclarer `id-token: write` ; l'environnement/nom du workflow doit matcher exactement la config trusted-publisher côté PyPI ; épingler `@release/v1` (pas `master`).

## GitTools/actions (GitVersion)

- **owner/repo:** GitTools/actions
- **stars:** ~271
- **activité:** très active (3 658 commits, PRs récentes)
- **licence:** **MIT** (permissive)
- **langage:** TypeScript/JavaScript
- **fichier/module du pattern:** `gitversion/setup` + `gitversion/execute` (deux actions composables)
- **mécanisme réel:** installe l'outil .NET GitVersion puis calcule un semver déterministe depuis l'historique git (tags, branches, mode `Mainline`/`ContinuousDelivery`), exposé en outputs (`majorMinorPatch`, `fullSemVer`, …).
- **snippet portable:**
  ```yaml
  - uses: gittools/actions/gitversion/setup@v3
    with: { versionSpec: '6.x' }
  - id: gitversion
    uses: gittools/actions/gitversion/execute@v3
  # -> steps.gitversion.outputs.fullSemVer
  ```
- **intégration dans ce projet:** ce repo a sa propre action `gitversion/` + `GitVersion.yml` ; comparer la config de mode et les outputs exposés à ceux de GitTools pour rester compatible et éviter de réimplémenter le calcul.
- **gotchas:** requiert `fetch-depth: 0` (`actions/checkout`) sinon versioning faux ; le pattern deux-étapes (setup puis execute) évite de réinstaller l'outil ; mode Mainline sensible à la structure de branches.

## astral-sh/ruff-action

- **owner/repo:** astral-sh/ruff-action
- **stars:** ~260
- **activité:** active (211 commits, 11 PRs ouvertes)
- **licence:** **Apache-2.0** (permissive)
- **langage:** TypeScript
- **fichier/module du pattern:** `action.yml` (inputs `version`, `args`, `src`) + install via `astral-sh/setup-uv`
- **mécanisme réel:** installe une version épinglée de ruff (cache uv) et lance `ruff check`/`ruff format --check` ; version résolue depuis `pyproject.toml`/`uv.lock` si non fournie.
- **snippet portable:**
  ```yaml
  - uses: astral-sh/ruff-action@v3
    with:
      version-file: pyproject.toml
      args: check --output-format github
  ```
- **intégration dans ce projet:** `ruff-check/action.yml` installe actuellement ruff en fallback non épinglé (`python -m pip install ruff`, avec `::warning::`). Adopter le modèle astral : résoudre la version depuis `[lint]`/lockfile pour un lint reproductible, et utiliser `--output-format github` pour des annotations inline.
- **gotchas:** ruff non épinglé = drift de règles entre runs (le repo l'admet déjà via warning) ; `--output-format github` produit les annotations PR ; garder le report JSON uniquement sur le Python "latest" de la matrice (déjà fait).

## SonarSource/sonarqube-scan-action

- **owner/repo:** SonarSource/sonarqube-scan-action
- **stars:** ~391
- **activité:** active (158 commits)
- **licence:** **LGPL-3.0** (copyleft faible — utilisable tel quel en tant qu'action référencée `uses:`, mais NE PAS copier/forker le code source dans une action MIT sans respecter LGPL ; le wrapping par `uses:` est OK)
- **langage:** JavaScript (Node, bundle rollup)
- **fichier/module du pattern:** `action.yml` + `sonar-project.properties`
- **mécanisme réel:** télécharge le sonar-scanner CLI, lit `sonar-project.properties` + env `SONAR_TOKEN`/`SONAR_HOST_URL`, pousse l'analyse vers SonarCloud/SonarQube.
- **snippet portable:**
  ```yaml
  - uses: SonarSource/sonarqube-scan-action@v6
    env:
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
  ```
- **intégration dans ce projet:** les 4 actions `sonar-scan*` (python/node/js) wrappent ce scanner ; garder l'appel par `uses:` (frontière LGPL propre) plutôt que d'inliner le scanner. Attention au cap LOC du plan FREE (voir memory `sonarcloud-loc-cap`).
- **gotchas:** LGPL — frontière = référence externe, pas copie de source ; `fetch-depth: 0` recommandé pour le blame ; échoue côté serveur si quota LOC dépassé, indépendamment du code.

## super-linter/super-linter

- **owner/repo:** super-linter/super-linter
- **stars:** ~10.5k
- **activité:** très active (19 PRs, 30 issues ouvertes)
- **licence:** **MIT** (permissive)
- **langage:** Shell (image Docker agrégeant 50+ linters)
- **fichier/module du pattern:** `lib/` scripts + orchestration GNU Parallel ; détection auto des fichiers modifiés
- **mécanisme réel:** un conteneur unique embarque yamllint, shellcheck, shfmt, hadolint, etc. ; exécution parallèle sur les fichiers changés, config par variables `VALIDATE_*`.
- **snippet portable:**
  ```yaml
  - uses: super-linter/super-linter/slim@v7
    env:
      VALIDATE_YAML: true
      VALIDATE_BASH: true
      VALIDATE_DOCKERFILE_HADOLINT: true
  ```
- **intégration dans ce projet:** ce repo a choisi l'approche inverse — une action fine par linter (`lint-yaml`, `lint-bash`, `lint-docker`, `lint-helm`) déléguant à `scripts/lint_*.sh`. C'est délibéré (granularité, pas de conteneur lourd). Super-linter reste la réf pour : détection des fichiers changés, exécution parallèle, et matrice de linters à couvrir.
- **gotchas:** l'image full est lourde (utiliser `/slim`) ; par défaut il lint tout le repo (config `VALIDATE_*` + `FILTER_REGEX`) — l'approche par-linter de chrysa évite ce coût mais duplique la logique de découverte.

## orhun/git-cliff-action

- **owner/repo:** orhun/git-cliff-action
- **stars:** ~212
- **activité:** active (123 commits)
- **licence:** **Apache-2.0 OR MIT** (dual, permissive)
- **langage:** Shell (`install.sh`, `run.sh`)
- **fichier/module du pattern:** `action.yml` (inputs `config`, `args`) + `cliff.toml`
- **mécanisme réel:** installe git-cliff, génère un changelog conventional-commits depuis l'historique selon `cliff.toml`, sortie sur stdout/fichier + output d'action.
- **snippet portable:**
  ```yaml
  - uses: orhun/git-cliff-action@v4
    with:
      config: cliff.toml
      args: --latest --strip header
  ```
- **intégration dans ce projet:** `changelog/action.yml` génère le changelog avec git-cliff pour une version calculée ; `cliff.toml` est déjà présent. Aligner les `args` (`--tag`, `--latest`) avec la version issue de l'action `gitversion` pour un pipeline release cohérent (gitversion -> changelog -> publish).
- **gotchas:** requiert `fetch-depth: 0` + tags fetchés ; le format dépend entièrement de `cliff.toml` (garder synchronisé avec la convention commit du repo) ; `--latest` peut être vide si aucun tag précédent.

---

### Takeaways
1. Le repo wrappe déjà les bonnes réfs OSS (pypa OIDC, git-cliff, sonar-scanner) par `uses:` — frontière propre, à conserver.
2. Amélioration nette : épingler ruff (modèle astral-sh/ruff-action via lockfile) au lieu du fallback non versionné qui produit du drift de règles.
3. Toutes les réfs sont permissives sauf SonarSource (LGPL-3.0) — OK en référence externe `uses:`, à NE PAS inliner dans le code MIT.
