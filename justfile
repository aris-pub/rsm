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
    npx tree-sitter generate
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

# Generate a CHANGELOG entry for the given version and prepend to CHANGELOG.md.
# If no version is given, uses "Unreleased".
changelog version="Unreleased":
    #!/usr/bin/env bash
    set -euo pipefail
    VERSION="{{version}}"
    LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    if [ -z "$LAST_TAG" ]; then COMMITS=$(git log --oneline --no-merges); else COMMITS=$(git log --oneline --no-merges "${LAST_TAG}..HEAD"); fi
    DATE=$(date +%Y-%m-%d)
    PROMPT="Generate a CHANGELOG entry for version $VERSION (date: $DATE). Commits since last tag: $COMMITS. Rules: Skip ci/test/chore/docs commits and submodule updates. Group into Keep-a-Changelog sections: Added (feat:), Fixed (fix:), Changed (other). Rewrite as user-friendly prose. Omit empty sections. If no user-visible changes output: _No user-visible changes._ Output only raw markdown (no preamble, no code fences): ## [$VERSION] - $DATE, then ### Added, ### Fixed, ### Changed sections as needed."
    entry=$(claude --print "$PROMPT")
    if [ -f CHANGELOG.md ]; then { head -1 CHANGELOG.md; printf "\n%s\n" "$entry"; tail -n +2 CHANGELOG.md; } > CHANGELOG.tmp && mv CHANGELOG.tmp CHANGELOG.md; else printf "# Changelog\n\n%s\n" "$entry" > CHANGELOG.md; fi
    echo "==> CHANGELOG.md updated for $VERSION"

# Release rsm-lang, and tree-sitter-rsm first if it has unreleased commits.
# Bumps both packages by the same level following semantic versioning.
# Usage:   just release <major|minor|patch>
release level:
    #!/usr/bin/env bash
    set -euo pipefail

    LEVEL="{{level}}"
    if [[ "$LEVEL" != "major" && "$LEVEL" != "minor" && "$LEVEL" != "patch" ]]; then
        echo "Error: level must be 'major', 'minor', or 'patch', got '$LEVEL'"
        exit 1
    fi

    bump() {
        local version=$1
        local major minor patch
        IFS='.' read -r major minor patch <<< "$version"
        case "$LEVEL" in
            major) echo "$((major + 1)).0.0" ;;
            minor) echo "${major}.$((minor + 1)).0" ;;
            patch) echo "${major}.${minor}.$((patch + 1))" ;;
        esac
    }

    # Confirm major bumps to prevent accidental stable releases
    if [[ "$LEVEL" == "major" ]]; then
        RSM_CURRENT=$(grep '^version' pyproject.toml | head -1 | sed 's/version = "\(.*\)"/\1/')
        RSM_NEXT=$(bump "$RSM_CURRENT")
        echo "WARNING: major release will bump rsm-lang $RSM_CURRENT -> $RSM_NEXT"
        read -r -p "Are you sure? [y/N] " confirm
        if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
            echo "Aborted."
            exit 1
        fi
    fi

    # ── Step 1: Check whether tree-sitter-rsm needs a release ─────────────────
    GRAMMAR_LAST_TAG=$(cd tree-sitter-rsm && git describe --tags --abbrev=0 2>/dev/null || echo "none")
    if [[ "$GRAMMAR_LAST_TAG" == "none" ]]; then
        GRAMMAR_COMMITS=1
    else
        GRAMMAR_COMMITS=$(cd tree-sitter-rsm && git log --oneline "${GRAMMAR_LAST_TAG}..HEAD" | wc -l | tr -d ' ')
    fi

    if [[ "$GRAMMAR_COMMITS" -gt 0 ]]; then
        GRAMMAR_CURRENT=$(grep '^version' tree-sitter-rsm/pyproject.toml | head -1 | sed 's/version = "\(.*\)"/\1/')
        GRAMMAR_VERSION=$(bump "$GRAMMAR_CURRENT")

        echo "==> Releasing tree-sitter-rsm $GRAMMAR_CURRENT -> v$GRAMMAR_VERSION ($GRAMMAR_COMMITS new commits)"
        cd tree-sitter-rsm
        npx tree-sitter version "$GRAMMAR_VERSION"
        git commit -am "Release $GRAMMAR_VERSION"
        git tag -- "v$GRAMMAR_VERSION"
        git push origin main
        git push origin "v$GRAMMAR_VERSION"
        cd ..

        echo "==> Waiting for tree-sitter-rsm publish action to start..."
        sleep 15
        GRAMMAR_RUN_ID=$(gh run list \
            --repo aris-pub/tree-sitter-rsm \
            --workflow "Publish packages" \
            --limit 1 \
            --json databaseId \
            --jq '.[0].databaseId')
        echo "==> Watching run $GRAMMAR_RUN_ID (this takes ~10 minutes for all wheels)..."
        gh run watch "$GRAMMAR_RUN_ID" --repo aris-pub/tree-sitter-rsm --exit-status
        echo "==> tree-sitter-rsm v$GRAMMAR_VERSION published."

        # Update the submodule pointer to the newly tagged commit
        git submodule update --init --remote tree-sitter-rsm
        git add tree-sitter-rsm
    else
        echo "==> tree-sitter-rsm is up to date, skipping grammar release."
        GRAMMAR_VERSION=""
    fi

    # ── Step 2: Release rsm-lang ───────────────────────────────────────────────
    RSM_CURRENT=$(grep '^version' pyproject.toml | head -1 | sed 's/version = "\(.*\)"/\1/')
    RSM_VERSION=$(bump "$RSM_CURRENT")

    echo "==> Releasing rsm-lang $RSM_CURRENT -> v$RSM_VERSION"

    sed -i.bak "s/^version = \"[0-9.]*\"/version = \"$RSM_VERSION\"/" pyproject.toml
    rm -f pyproject.toml.bak

    # Update grammar dependency floor if we just released a new grammar version
    if [[ -n "$GRAMMAR_VERSION" ]]; then
        sed -i.bak "s/tree-sitter-rsm>=[0-9.]*/tree-sitter-rsm>=$GRAMMAR_VERSION/" pyproject.toml
        rm -f pyproject.toml.bak
    fi

    git add pyproject.toml
    just changelog "$RSM_VERSION"
    git add CHANGELOG.md
    git commit -m "Release v$RSM_VERSION"
    git tag "v$RSM_VERSION"
    git push origin main
    git push origin "v$RSM_VERSION"

    echo "==> Waiting for rsm-lang publish action to start..."
    sleep 15
    RSM_RUN_ID=$(gh run list \
        --repo aris-pub/rsm \
        --workflow "Publish to PyPI" \
        --limit 1 \
        --json databaseId \
        --jq '.[0].databaseId')
    echo "==> Watching run $RSM_RUN_ID..."
    gh run watch "$RSM_RUN_ID" --repo aris-pub/rsm --exit-status

    echo ""
    echo "Released:"
    if [[ -n "$GRAMMAR_VERSION" ]]; then
        echo "  tree-sitter-rsm v$GRAMMAR_VERSION"
    fi
    echo "  rsm-lang v$RSM_VERSION"
