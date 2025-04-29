.PHONY: build check format test

format:
	ruff format .

check:
	ruff check .
	mypy .

test:
	PYTHONPATH=./ pytest

build: format check test