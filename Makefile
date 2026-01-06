.PHONY: help install test test-all lint format clean build publish

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install package with uv
	uv venv
	uv pip install -e ".[dev]"
	@echo "✅ Installed! Activate with: source .venv/bin/activate"

test: ## Run tests with current Python
	uv run pytest --cov=facecrop --cov-report=term-missing

test-all: ## Run tests on all Python versions (fast with uv)
	@bash scripts/test-all.sh

lint: ## Run linters
	uv run ruff check src/ tests/
	uv run black --check src/ tests/
	uv run mypy src/

format: ## Format code
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

clean: ## Remove build artifacts and cache
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov
	rm -rf .venv .venv-test-*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build: clean ## Build package
	uv build

publish-test: build ## Publish to Test PyPI
	uv publish --publish-url https://test.pypi.org/legacy/

publish: build ## Publish to PyPI
	uv publish

dev: ## Quick development setup
	@echo "🚀 Setting up FaceCrop development environment..."
	@command -v uv >/dev/null 2>&1 || (echo "Installing uv..." && curl -LsSf https://astral.sh/uv/install.sh | sh)
	@make install
	@echo ""
	@echo "✅ Development environment ready!"
	@echo ""
	@echo "Quick commands:"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Check code quality"
	@echo "  make format     - Format code"
	@echo "  make test-all   - Test all Python versions"

.DEFAULT_GOAL := help
