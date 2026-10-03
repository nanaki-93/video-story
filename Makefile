UV ?= $(if $(wildcard .tools/bin/uv),.tools/bin/uv,uv)

.PHONY: setup check test help

setup:
	$(UV) sync --frozen --group audit

check:
	$(UV) run --frozen ruff check src tests scripts
	$(UV) run --frozen ruff format --check src tests scripts
	$(UV) run --frozen pytest

test:
	$(UV) run --frozen pytest

help:
	$(UV) run --frozen tabi --help
