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

check-build:  ## Check built packages
	twine check dist/*

# ===== Release Management =====

release-check:  ## Check if ready for release (run all checks)
	@echo "🔍 Running quality checks..."
	@make quality
	@echo "🧪 Running tests..."
	@make test-cov
	@echo "🏗️  Building package..."
	@make clean build
	@echo "✅ All checks passed! Ready for release."

release-patch:  ## Create a patch release (0.1.0 -> 0.1.1)
	@echo "Creating patch release..."
	@make release-check
	@python -c "import re; \
		content = open('pyproject.toml').read(); \
		version = re.search(r'version = \"(.+)\"', content).group(1); \
		major, minor, patch = version.split('.'); \
		new_version = f'{major}.{minor}.{int(patch)+1}'; \
		print(f'Current: {version} -> New: {new_version}'); \
		open('pyproject.toml', 'w').write(content.replace(f'version = \"{version}\"', f'version = \"{new_version}\"'))"
	@echo "✅ Version bumped. Don't forget to update CHANGELOG.md!"
	@echo "Next steps:"
	@echo "  1. Update CHANGELOG.md with new version"
	@echo "  2. git add pyproject.toml CHANGELOG.md"
	@echo "  3. make release-tag"

release-minor:  ## Create a minor release (0.1.0 -> 0.2.0)
	@echo "Creating minor release..."
	@make release-check
	@python -c "import re; \
		content = open('pyproject.toml').read(); \
		version = re.search(r'version = \"(.+)\"', content).group(1); \
		major, minor, patch = version.split('.'); \
		new_version = f'{major}.{int(minor)+1}.0'; \
		print(f'Current: {version} -> New: {new_version}'); \
		open('pyproject.toml', 'w').write(content.replace(f'version = \"{version}\"', f'version = \"{new_version}\"'))"
	@echo "✅ Version bumped. Don't forget to update CHANGELOG.md!"
	@echo "Next steps:"
	@echo "  1. Update CHANGELOG.md with new version"
	@echo "  2. git add pyproject.toml CHANGELOG.md"
	@echo "  3. make release-tag"

release-major:  ## Create a major release (0.1.0 -> 1.0.0)
	@echo "Creating major release..."
	@make release-check
	@python -c "import re; \
		content = open('pyproject.toml').read(); \
		version = re.search(r'version = \"(.+)\"', content).group(1); \
		major, minor, patch = version.split('.'); \
		new_version = f'{int(major)+1}.0.0'; \
		print(f'Current: {version} -> New: {new_version}'); \
		open('pyproject.toml', 'w').write(content.replace(f'version = \"{version}\"', f'version = \"{new_version}\"'))"
	@echo "✅ Version bumped. Don't forget to update CHANGELOG.md!"
	@echo "Next steps:"
	@echo "  1. Update CHANGELOG.md with new version"
	@echo "  2. git add pyproject.toml CHANGELOG.md"
	@echo "  3. make release-tag"

release-tag:  ## Create and push release tag
	@VERSION=$$(grep -E '^version = ' pyproject.toml | cut -d'"' -f2); \
	echo "Creating release tag v$$VERSION..."; \
	git commit -m "Release v$$VERSION" || true; \
	git tag -a "v$$VERSION" -m "Release v$$VERSION"; \
	echo "✅ Tag created: v$$VERSION"; \
	echo ""; \
	echo "To push and trigger release:"; \
	echo "  git push origin main"; \
	echo "  git push origin v$$VERSION"

publish-test:  ## Publish to Test PyPI (manual)
	python -m twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI (manual - use GitHub Actions for releases)
	@echo "⚠️  WARNING: Use 'git push origin v*.*.*' to trigger automatic release"
	@echo "This command is for manual publishing only."
	@read -p "Continue with manual publish? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	python -m twine upload dist/*

docs:  ## Build documentation
	cd docs && make html

docs-serve:  ## Serve documentation locally
	cd docs && make html && python -m http.server --directory _build/html

example:  ## Run example computation
	optiride compute \
		--gpx examples/Auxonne.gpx \
		--mass 65 --height 1.86 --age 28 \
		--ftp 200 --intensity-factor 0.95 \
		--bike-mass 7.0 --auto-weather \
		--export-gpx --export-map

.DEFAULT_GOAL := help
