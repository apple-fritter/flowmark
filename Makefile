# Makefile for easy development workflows.
# See development.md for docs.
# Note GitHub Actions call uv directly, not this Makefile.

.DEFAULT_GOAL := default

.PHONY: default install lint test upgrade build clean gen_test_docs

default: install lint test

install:
	uv sync --all-extras --dev

lint:
	uv run python devtools/lint.py

test:
	uv run pytest

upgrade:
	uv sync --upgrade

build:
	uv build

clean:
	-rm -rf dist/
	-rm -rf *.egg-info/
	-rm -rf .pytest_cache/
	-rm -rf .mypy_cache/
	-rm -rf .venv/
	-find . -type d -name "__pycache__" -exec rm -rf {} +

gen_test_docs:
	poetry run flowmark tests/testdocs/testdoc.orig.md -o tests/testdocs/testdoc.out.plain.md
	poetry run flowmark --semantic tests/testdocs/testdoc.orig.md -o tests/testdocs/testdoc.out.semantic.md