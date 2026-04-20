# ⚠️ DEPRECATED — repo en cours de fusion dans `chrysa/shared-standards`

Ce repository est **obsolète**. Son contenu (12 composite actions) est en cours
de consolidation dans [`chrysa/shared-standards/.github/actions/`](https://github.com/chrysa/shared-standards/tree/main/.github/actions)
conformément à l'**ADR-0009**.

## Actions concernées

- gitversion · install-project · mypy-check · publish-python-package
- python-setup · ruff-check · run-tests · sonar-js-scan
- sonar-scan · sonar-scan-node · sonar-scan-python · tool-setup

## État

- ⚙️ **Migration en cours** — voir plan atomique :
  [shared-standards/docs/MIGRATION-ADR-0009-0010-0013.md](https://github.com/chrysa/shared-standards/blob/main/docs/MIGRATION-ADR-0009-0010-0013.md)

## Si tu appelles ce repo depuis un workflow

Remplace :

```yaml
- uses: chrysa/github-actions/ruff-check@v1
```

Par (après merge d'ADR-0009) :

```yaml
- uses: chrysa/shared-standards/.github/actions/ruff-check@v1
```

Pendant la transition, les deux adresses fonctionneront. Après archivage de ce
repo, seule la nouvelle adresse sera supportée.

## Pourquoi cette fusion

- **Source unique** pour les outils CI chrysa (workflows reusable +
  composite actions au même endroit)
- **Versioning synchronisé** : un tag `v1.2.0` de shared-standards figer l'ensemble
- **Moins de repos à maintenir** (règle 1+2 du portfolio — moins de surface
  de standardisation)

## Ne plus contribuer ici

Toute évolution doit être portée sur `chrysa/shared-standards`. Les issues
ouvertes ici seront migrées par l'owner.

## Archivage

Une fois la migration ADR-0009 terminée, ce repo sera archivé en lecture seule
via GitHub Settings → Archive. Historique préservé pour audit.
