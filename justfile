# justfile for rsm-lang development
# Install just: https://just.systems/man/en/

# Set shell for all recipes
set shell := ["bash", "-c"]

# List all available recipes
default:
    @just --list

# Install dependencies for development
install:
    uv sync --all-extras

# Install with local tree-sitter-rsm for grammar development
install-local:
    uv sync --all-extras
    uv pip install -e tree-sitter-rsm --no-build-isolation

# Run fast tests (skip slow tests)
test:
    uv run pytest -vv -k 'not slow'

# Run only slow tests
test-slow:
    uv run pytest -vv -k 'slow'

# Run all tests including slow ones
test-all: test test-slow test-docs

# Run tests with doctests in source and docs
test-docs:
    cd docs && uv run make doctest
    uv run pytest -vv --doctest-modules rsm/

# Format code and run linter
lint:
    uv run ruff format rsm/ tests/
    uv run ruff check --fix rsm/ tests/

# Run type checking
typecheck:
    uv run mypy rsm/

# Run quality checks then tests
check: lint test typecheck

# Build documentation
docs:
    uv run sphinx-build docs/source/ docs/build/

# Clean documentation build artifacts
docs-clean:
    cd docs && uv run make clean

# Serve documentation with live reload
docs-serve:
    uv run sphinx-autobuild docs/source/ docs/build/ --port 7001 --watch rsm/

# Rebuild and reinstall tree-sitter-rsm grammar
grammar:
    #!/usr/bin/env bash
    set -euo pipefail
    cd tree-sitter-rsm
    echo "Regenerating parser from grammar.js..."
    tree-sitter generate
    echo "Rebuilding C extension..."
    make
    echo "Reinstalling tree-sitter-rsm package..."
    cd ..
    uv pip install -e tree-sitter-rsm --force-reinstall --no-deps --no-build-isolation
    echo "Done! tree-sitter-rsm rebuilt successfully"

# Rebuild the standalone JS bundle for RSM
rebuild-js-bundle:
    npx esbuild rsm/static/onload.js --bundle --format=iife --global-name=RSM --outfile=rsm/static/rsm-standalone.js
