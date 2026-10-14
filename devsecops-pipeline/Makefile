# Convenience targets. Everything the pipeline does is reachable from here.
SHELL := /bin/bash
.DEFAULT_GOAL := help

WORKLOAD ?= workloads/01-flask-api/vulnerable

.PHONY: help setup tooling-up tooling-down scan demo demo-vulnerable demo-fixed report clean test lint

help: ## Show the available targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[1;36m%-18s\033[0m %s\n", $$1, $$2}'

setup: ## Install developer tools and pre-commit hooks (stage 0, shift left)
	python3 -m pip install --user -r requirements-dev.txt
	pre-commit install
	@echo "developer tools and pre-commit hooks installed"

tooling-up: ## Start the tooling zone (Gitea, Vault dev, DefectDojo)
	docker compose -f infra/docker-compose.tooling.yml up -d
	@echo "Gitea http://localhost:3000 | Vault http://localhost:8200 | DefectDojo http://localhost:8081"

tooling-down: ## Stop the tooling zone
	docker compose -f infra/docker-compose.tooling.yml down -v

scan: ## Run the full pipeline for WORKLOAD=<path>
	scripts/run-pipeline.sh $(WORKLOAD)

demo-vulnerable: ## Run all three vulnerable workloads (gate must fail)
	-scripts/run-pipeline.sh workloads/01-flask-api/vulnerable
	-scripts/run-pipeline.sh workloads/02-cli-deps/vulnerable
	-scripts/run-pipeline.sh workloads/03-container-service/vulnerable

demo-fixed: ## Run all three fixed workloads (gate must pass)
	scripts/run-pipeline.sh workloads/01-flask-api/fixed
	scripts/run-pipeline.sh workloads/02-cli-deps/fixed
	scripts/run-pipeline.sh workloads/03-container-service/fixed

demo: demo-vulnerable demo-fixed report ## Full demo: 6 runs, then the report

report: ## Regenerate the findings report and the metrics file
	python3 scripts/report.py
	@echo "reports/FINDINGS_REPORT.md"

test: ## Run the unit tests of the pipeline logic (no containers needed)
	python3 -m pytest tests -q

clean: ## Remove run artefacts
	rm -rf reports/*/ reports/FINDINGS_REPORT.md reports/metrics.csv
