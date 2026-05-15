#!make
ifneq (,)
	$(error This Makefile requires GNU Make)
endif

# ─── Variables ────────────────────────────────────────────────────────────────
PROJECT_NAME ?= github-actions

.DEFAULT_GOAL := help

.PHONY: $(shell grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | cut -d":" -f1 | tr "\n" " ")
.PHONY: install dev test test-cov lint format typecheck build clean

help: ## Display this help message
	@echo "==================================================================="
	@echo "  $(PROJECT_NAME)"
	@echo "==================================================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {{FS = ":.*?## "}}; {{printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}}'
	@echo ""
	@echo "==================================================================="

# ─── Validation ──────────────────────────────────────────────────────────────

validate: ## Validate all GitHub Actions definitions
	action-validator .

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

install-pre-commit: ## Install and configure git pre-commit hooks
	pip install --quiet pre-commit
	pre-commit install
	pre-commit autoupdate --bleeding-edge

# ── Standard chrysa targets ───────────────────────────────────────────────────

install: ## Install required tools (action-validator, pre-commit)
	pip install --quiet pre-commit
	which action-validator >/dev/null 2>&1 || pip install --quiet action-validator || true
	pre-commit install

dev: ## No-op for composite actions repo
	@echo "No dev server for composite actions — use validate to check actions"

test: validate ## Run action validation (alias → validate)

test-cov: validate ## Run action validation (no coverage for actions repo)

lint: validate ## Lint composite actions (alias → validate)

format: ## Format YAML files via pre-commit
	pre-commit run prettier --all-files 2>/dev/null || true

typecheck: validate ## Validate action schemas (alias → validate)

build: ## No-op — composite actions are deployed as YAML
	@echo "No build step — composite actions are deployed as-is"

clean: ## Remove pre-commit caches
	pre-commit clean 2>/dev/null || true
