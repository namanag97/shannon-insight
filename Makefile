.PHONY: help install test lint format type-check clean run all build-frontend package check-package publish-test publish

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package with dev dependencies
	pip install -e ".[dev]"

test:  ## Run tests with coverage
	pytest tests/ -v --cov=src/shannon_insight --cov-report=html --cov-report=term-missing

test-quick:  ## Run tests without coverage
	pytest tests/ -v

lint:  ## Run linting with ruff
	ruff check src/ tests/

format:  ## Format code with ruff
	ruff format src/ tests/
	ruff check --fix src/ tests/

type-check:  ## Run type checking with mypy
	mypy src/

check: lint type-check  ## Run all code quality checks

all: format check test  ## Format, check, and test

clean:  ## Clean up cache and build artifacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache .shannon-cache
	rm -rf htmlcov .coverage coverage.xml
	rm -rf build dist *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

run:  ## Run analyzer on test codebase
	shannon-insight test_codebase/complexity_demo --language python --top 10

build-frontend:  ## Build frontend for production
	@bash scripts/build-frontend.sh

package: build-frontend  ## Build distribution packages (includes frontend)
	rm -rf dist/
	python3 -m build

check-package:  ## Check package integrity
	twine check dist/*

publish-test:  ## Publish to Test PyPI
	twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
	twine upload dist/*

dev-setup: clean install  ## Complete development setup
	@echo "Development environment setup complete!"
	@echo "   Run 'make run' to test"
