# Testing targets

src_folder ?= src

.PHONY: black
black: ## Run black check in the src folder provided
black: files ?= ${src_folder} tests
black:
	${DC} run --rm --no-deps black --check --line-length 120 ${files}

.PHONY: flake8
flake8: ## Run flake8 in the src folder provided
flake8: files ?= ${src_folder} tests
flake8:
	${DC} run --rm --no-deps flake8 --config setup.cfg ${files}

.PHONY: isort
isort: ## Run isort verification.
isort: args?= --line-length 120 --diff --check-only --quiet .
isort:
	${DC} run --rm --no-deps isort ${args}

.PHONY: lint
lint: ## Run black, flake8, isort and mypy tests
lint: black flake8 isort mypy

.PHONY: mypy
mypy: ## Run mypy verification.
mypy: args?= -p ${src_folder}
mypy:
	${DC} run --rm --no-deps mypy ${args}

.PHONY: unit-test
unit-test: ## Run unit tests for file=<file> provided.
	${DC} run --rm unit_test

.PHONY: unit-test-shell
unit-test-shell: ## Run unit tests shell.
unit-test-shell:
	${DC} run -v $(PWD):/srv/app --rm --entrypoint=/bin/bash unit_test
