.PHONY: build check format

format:
	ruff format .

check:
	ruff check .
	mypy .

build: format check
