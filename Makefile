PYTHON ?= python3

.PHONY: run test test-os lint

run:
	$(PYTHON) -m src.main $(ARGS)

test:
	$(PYTHON) -m unittest discover -s tests -t .

test-os:
	sh scripts/test_params_basic.sh
	sh scripts/test_params_log.sh
	sh scripts/test_params_errors.sh
	sh scripts/test_vfs_variants.sh
	sh scripts/test_vfs_errors.sh

lint:
	$(PYTHON) -m flake8 --max-line-length=80 src tests
