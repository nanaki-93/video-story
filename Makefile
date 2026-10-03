UV ?= $(if $(wildcard .tools/bin/uv),.tools/bin/uv,uv)

.PHONY: setup check test test-media help schemas doctor fixtures clean-cache web-check web-build run-web run-worker

setup:
	$(UV) sync --frozen --group audit

check:
	$(UV) run --frozen ruff check src tests scripts
	$(UV) run --frozen ruff format --check src tests scripts
	$(UV) run --frozen python scripts/export_schemas.py --check
	$(UV) run --frozen pytest

schemas:
	$(UV) run --frozen python scripts/export_schemas.py

test:
	$(UV) run --frozen pytest

help:
	$(UV) run --frozen tabi --help

doctor:
	$(UV) run --frozen tabi doctor --json

test-media:
	$(UV) run --frozen pytest --run-media tests/integration

web-check:
	cd web && npm run check && npm test

web-build:
	cd web && npm run build

run-web:
	$(UV) run --frozen tabi web

run-worker:
	$(UV) run --frozen tabi web --no-open

FIXTURE_OUTPUT ?= .local/fixtures-v1
fixtures:
	$(UV) run --frozen tabi fixtures --output "$(FIXTURE_OUTPUT)"

# Inspect by default. Actual removal needs the observed inventory and explicit --apply.
clean-cache:
	@test -n "$(PROJECT)" || (echo 'Set PROJECT to the project directory'; exit 2)
	$(UV) run --frozen tabi cache prune --project "$(PROJECT)" --all
