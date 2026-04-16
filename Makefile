.PHONY: install install-dev test lint format check

install:
	python3 -m pip install -e .

install-dev:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest -q

lint:
	python3 -m ruff check .

format:
	python3 -m ruff format .

check: lint test

