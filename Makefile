.PHONY: help install install-dev test test-cov lint format type-check clean docs

help:  ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev,docs,jupyter]"
	pre-commit install

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=optiride --cov-report=html --cov-report=term-missing

test-watch:  ## Run tests in watch mode
	pytest-watch

lint:  ## Run linter
	ruff check .

lint-fix:  ## Run linter and fix issues
	ruff check . --fix

format:  ## Format code
	ruff format .

format-check:  ## Check code formatting
	ruff format --check .

type-check:  ## Run type checker
	mypy optiride

quality:  ## Run all quality checks (lint, format, type)
	@echo "Running ruff lint..."
	@ruff check .
	@echo "Running ruff format check..."
	@ruff format --check .
	@echo "Running mypy..."
	@mypy optiride --ignore-missing-imports
	@echo "All quality checks passed!"

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

clean:  ## Clean build artifacts and caches
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build distribution packages
	python -m build

publish-test:  ## Publish to Test PyPI
	python -m twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
	python -m twine upload dist/*

docs:  ## Build documentation
	cd docs && make html

docs-serve:  ## Serve documentation locally
	cd docs && make html && python -m http.server --directory _build/html

example:  ## Run example computation
	optiride compute \
		--gpx examples/CingléVentoux.gpx \
		--mass 65 --height 1.86 --age 28 \
		--ftp 250 --power-flat 200 \
		--bike-mass 7.0 --auto-weather \
		--export-gpx

.DEFAULT_GOAL := help
