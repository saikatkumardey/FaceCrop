#!/usr/bin/env bash
# Fast test runner using uv
# Runs tests across all Python versions in seconds

set -e

echo "🚀 FaceCrop Fast Test Suite (powered by uv)"
echo "============================================"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Python versions to test
PYTHON_VERSIONS=("3.8" "3.9" "3.10" "3.11" "3.12")

for version in "${PYTHON_VERSIONS[@]}"; do
    echo ""
    echo "🐍 Testing with Python $version"
    echo "--------------------------------"

    # Create venv and install deps
    uv venv --python "$version" .venv-test-"$version" --quiet
    source .venv-test-"$version"/bin/activate

    # Install package and dev dependencies
    uv pip install -e ".[dev]" --quiet

    # Run tests
    if [ "$version" = "3.11" ]; then
        echo "  ✓ Running tests with coverage..."
        pytest --cov=facecrop --cov-report=term-missing -q

        echo "  ✓ Running linters..."
        ruff check src/ tests/ --quiet || true
        black --check src/ tests/ --quiet || echo "  ⚠ Format check failed"
        mypy src/ --no-error-summary || true
    else
        echo "  ✓ Running tests..."
        pytest -q
    fi

    # Cleanup
    deactivate
    rm -rf .venv-test-"$version"
done

echo ""
echo "✅ All tests complete!"
echo ""
echo "💡 Tip: Use 'uv run pytest' for even faster local testing"
