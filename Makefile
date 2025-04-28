.PHONY: build check format

format:
	ruff format .

check:
	ruff check .
	mypy .

ifeq ($(OS),Windows_NT)
	PYTHON_CMD=cmd /C "set PYTHONPATH=src&& "
else
	PYTHON_CMD=PYTHONPATH=src
endif

test:
	$(PYTHON_CMD) pytest


build: format check test
