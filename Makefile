UV ?= $(if $(wildcard .tools/bin/uv),.tools/bin/uv,uv)

.PHONY: setup check test test-media help schemas doctor fixtures

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

FIXTURE_OUTPUT ?= .local/fixtures-v1
fixtures:
	$(UV) run --frozen tabi fixtures --output "$(FIXTURE_OUTPUT)"
