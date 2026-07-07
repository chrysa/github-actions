# github-actions

> @[claude-sonnet-4-6]

> **Claude Code**: also read `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md` for code specifications.
## Project Overview
Reusable GitHub Actions for all chrysa repositories. Provides gitversion, python-setup, ruff-check, sonar-scan, sonar-scan-node, run-tests, tool-setup, install-project actions.

## Repository Structure
See README.md for detailed structure.

## Development Setup
```bash
make install
make dev
```

## Testing
```bash
make test
```

## CI/CD
- Pre-commit hooks: `.pre-commit-config.yaml`
- CI: `.github/workflows/ci.yml`
- PR dependency check: `.github/workflows/dependencies.yml`
- Auto-labeler: `.github/workflows/labeler.yml`
- Release: `.github/workflows/release.yml`

## Code Standards
- All commits must follow conventional commit format
- Pre-commit hooks must pass before push
- CI must be green before merge

## Git Conventions
- Branch naming: `feat/`, `fix/`, `chore/`, `refactor/`, `docs/`
- Commits: conventional commits (`feat:`, `fix:`, `chore:`, etc.)
- Changelog: auto-generated via `cliff.toml`

## Key Decisions
See CHANGELOG.md for version history and notable changes.

## Skills

Shared skills from `shared-standards/.claude/skills/`:

- `ui-ux/SKILL.md` — UX/UI/ergonomics across ALL surfaces (web, CLI, VS Code, Discord, desktop, game, agent) + WCAG 2.1 AA + dark mode + i18n FR+EN (load when building any human-facing surface)

<!-- chrysa:standards-import:start -->
@.chrysa/STANDARDS.md
<!-- chrysa:standards-import:end -->

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
