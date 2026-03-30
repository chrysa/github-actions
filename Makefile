#!make
ifneq (,)
	$(error This Makefile requires GNU Make)
endif

# ─── Variables ────────────────────────────────────────────────────────────────
PROJECT_NAME ?= github-actions

.DEFAULT_GOAL := help

.PHONY: $(shell grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | cut -d":" -f1 | tr "\n" " ")

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
