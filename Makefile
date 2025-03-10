.DEFAULT_GOAL := default

.PHONY: default install_deps lint test build clean gen_test_docs

default: install_deps lint test

install_deps:
	poetry install

lint:
	poetry run python devtools/lint.py

test:
	poetry run pytest

build:
	poetry build

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