# justfile for rsm-markup development
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

# Run all tests including slow ones
test-all:
    uv run pytest -vv

# Run tests with doctests in source and docs
test-docs:
    cd docs && uv run make doctest
    uv run pytest -vv --doctest-modules rsm/

# Format code and run linter
lint:
    uv run ruff format rsm/ tests/
    uv run ruff check --fix rsm/ tests/

# Run quality checks then tests
check: lint test

# Run type checking
typecheck:
    uv run mypy rsm/

# Build documentation
docs:
    uv run sphinx-build docs/source/ docs/build/

# Clean documentation build artifacts
docs-clean:
    cd docs && make clean

# Serve documentation with live reload
docs-serve:
    uv run sphinx-autobuild docs/source/ docs/build/ --port 7001 --watch rsm/

# Build the tree-sitter grammar (for grammar development)
build-grammar:
    #!/usr/bin/env bash
    set -euo pipefail
    cd tree-sitter-rsm
    echo "Installing npm dependencies..."
    npm install
    echo "Generating parser..."
    node ./node_modules/.bin/tree-sitter generate
    echo "Building shared library..."
    if [[ "$OSTYPE" == "win32" || "$OSTYPE" == "msys" ]]; then
        node ./node_modules/.bin/tree-sitter build -o build/rsm.dll
        cp build/rsm.dll ../rsm/
    else
        node ./node_modules/.bin/tree-sitter build -o build/rsm.so
        cp build/rsm.so ../rsm/
    fi
    echo "Grammar built successfully!"

# Rebuild and reinstall tree-sitter-rsm after C code changes
rebuild-grammar:
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
    echo "Ensuring dev dependencies are still installed..."
    uv sync --extra dev
    echo "Done! tree-sitter-rsm rebuilt and dev dependencies preserved"

# Build distribution packages
build:
    uv build

# Publish to PyPI
publish:
    uv publish

# Publish to TestPyPI
publish-test:
    uv publish --publish-url https://test.pypi.org/legacy/

# Clean build artifacts
clean:
    rm -rf build/ dist/ *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name '*.pyc' -delete
    find . -type f -name '*.pyo' -delete

# Update dependencies
update:
    uv lock --upgrade

# Show dependency tree
deps:
    uv tree

# Rebuild the standalone JS bundle for RSM
rebuild-js-bundle:
    npx esbuild rsm/static/onload.js --bundle --format=iife --global-name=RSM --outfile=rsm/static/rsm-standalone.js
