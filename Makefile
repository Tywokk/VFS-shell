PYTHON ?= python3

.PHONY: run test lint

run:
	$(PYTHON) -m src.main

test:
	$(PYTHON) -m unittest discover -s tests -t .

lint:
	$(PYTHON) -m flake8 --max-line-length=80 src tests
