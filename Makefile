.PHONY: build check format test docs

format:
	ruff format .

check:
	ruff check .
	mypy .

test:
	PYTHONPATH=./ pytest

docs:
	sphinx-apidoc -o docs/source src
	make -C docs html

build: format check test docs
