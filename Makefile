.PHONY: build check format

format:
	ruff format .

check:
	ruff check .
	mypy .

test:
	PYTHONPATH=src pytest

build: format check test
