# justfile for rsm-lang development
# Install just: https://just.systems/man/en/

# Set shell for all recipes
set shell := ["bash", "-c"]

# List all available recipes
default:
    @just --list

# Install dependencies for development
install:
    uv sync

# Install with local tree-sitter-rsm for grammar development
install-local:
    uv sync
    uv pip install -e tree-sitter-rsm --no-build-isolation

# Run fast tests (skip slow, visual, and accessibility tests)
test-fast:
    uv run pytest -vv -m 'not visual and not accessibility' -k 'not slow'

# Run only slow tests
test-slow:
    uv run pytest -vv -k 'slow'

# Run visual regression tests (in parallel)
test-visual:
    uv run pytest -vv -m visual -n auto

# Run accessibility tests (WCAG compliance)
test-a11y:
    uv run pytest -vv -m accessibility -n auto

# Run interactive browser behavior tests (toasts, tooltips, clipboard, iframe contexts)
test-interactive:
    uv run pytest tests/interactive/ -vv --browser chromium

# Run tests with doctests in source and docs
test-docs:
    cd docs && uv run make doctest
    uv run pytest -vv --doctest-modules rsm/

# Run all tests (excluding visual and accessibility tests)
test: test-fast test-slow test-docs

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
    uv pip install -e tree-sitter-rsm --reinstall-package tree-sitter-rsm
    echo "Done! tree-sitter-rsm rebuilt successfully"

# Rebuild the standalone JS bundle (IIFE with window.RSM global)
js-bundle:
    npx esbuild rsm/static/onload.js --bundle --format=iife --global-name=RSM --outfile=rsm/static/rsm-standalone.js

# Rebuild all compiled artifacts (JS bundle + tree-sitter grammar)
build: js-bundle grammar
