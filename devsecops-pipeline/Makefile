# Optional shortcuts; all Python commands also work directly on Windows.
PYTHON ?= python3
.DEFAULT_GOAL := help
WORKLOAD ?= workloads/01-flask-api/vulnerable
.PHONY: help setup prepare scan demo test report tooling-up tooling-down
help:
	@echo "setup | prepare | scan WORKLOAD=... | demo | test | report"
setup:
	$(PYTHON) -m pip install -r requirements-dev.txt
	cd .. && $(PYTHON) -m pre_commit install
prepare:
	$(PYTHON) scripts/prepare.py
scan:
	$(PYTHON) scripts/pipeline.py $(WORKLOAD)
demo:
	$(PYTHON) scripts/demo.py
test:
	$(PYTHON) -m pytest tests -q
report:
	$(PYTHON) scripts/report.py
tooling-up:
	docker compose -f infra/docker-compose.tooling.yml up -d
tooling-down:
	docker compose -f infra/docker-compose.tooling.yml down
