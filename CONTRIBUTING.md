# Contributing to RSM

Thank you for considering contributing to Readable Science Markup! This document provides guidelines for contributing to the project.

## Code of Conduct

RSM is a community-owned project. We expect all contributors to:
- Be respectful and constructive in discussions
- Focus on what's best for the community
- Welcome newcomers and help them get started

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- `just` command runner
- (Optional) `tree-sitter` CLI for grammar development

### Initial Setup

1. **Fork and clone the repository**
   ```bash
   git clone --recurse-submodules https://github.com/YOUR_USERNAME/rsm.git
   cd rsm
   ```

   **Important**: Use `--recurse-submodules` to include the `tree-sitter-rsm` grammar submodule.

2. **Install dependencies**
   ```bash
   just install
   ```

   This installs:
   - `rsm-lang` in editable mode
   - `tree-sitter-rsm` from PyPI (pre-built wheel)
   - All development and documentation dependencies

3. **Install pre-commit hooks (optional but recommended)**
   ```bash
   uv run pre-commit install
   ```

   The hooks will check YAML/TOML files and fix whitespace issues before commits.

## Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code patterns
   - Keep changes focused and minimal
   - Avoid over-engineering

3. **Run tests and linting**
   ```bash
   just check  # Runs linting, tests, and type checking
   ```

### Code Style

- **Linter**: ruff (configured for Python 3.10+)
- **Type Checker**: mypy with strict settings
- **Format**: Run `just lint` to format code
- **Comments**: Only add comments that explain *why*, not *what*
- **Simplicity**: Prefer simple solutions over abstractions

### Testing

All changes should include test coverage:

- **Unit tests**: Test individual functions and components
- **Slow tests**: Large-scale tests marked with `@pytest.mark.slow`
- **Doctests**: Examples in docstrings and documentation

```bash
# Run fast tests only (recommended during development)
just test

# Run all tests including slow ones
just test-all

# Run only slow tests
just test-slow

# Run doctests in source and docs
just test-docs

# Run type checking
just typecheck
```

### JavaScript Bundle

RSM includes a standalone JavaScript bundle (`rsm/static/rsm-standalone.js`) that must be regenerated when any JS files in `rsm/static/` are modified.

**When to rebuild**:
- After editing any `.js` file in `rsm/static/`

**How to rebuild**:
```bash
just rebuild-js-bundle
```

This bundles `onload.js` and dependencies into a single IIFE that exposes `RSM.onload()` and `RSM.onrender()`.

### Grammar Development (Advanced)

**Most contributors don't need this.** Only modify the grammar if you're changing RSM language syntax.

If you need to modify `tree-sitter-rsm/grammar.js`:

1. **Switch to local grammar development**
   ```bash
   just install-local
   ```

2. **Modify grammar**
   Edit `tree-sitter-rsm/grammar.js`

3. **Rebuild grammar**
   ```bash
   just grammar
   ```

   This regenerates the parser, rebuilds the C extension, and reinstalls the package.

### Documentation

- **User-facing docs**: Edit RST files in `docs/source/` directory
- **Build docs**: Run `just docs` to build HTML documentation
- **Serve docs with live reload**: Run `just docs-serve` (opens on port 7001)
- **Code docs**: Add docstrings with examples for public APIs
- **README**: Keep README focused on installation and quick start

## Submitting Changes

### Pull Request Process

1. **Ensure all checks pass**
   ```bash
   just check  # Linting + tests + type checking
   ```

2. **Commit your changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

   Pre-commit hooks will run automatically if installed.

3. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request**
   - Use a clear, descriptive title
   - Describe what changed and why
   - Reference any related issues
   - Ensure CI passes

### PR Guidelines

- **Keep PRs focused**: One feature or bug fix per PR
- **Write clear commit messages**: Describe *what* and *why*
- **Respond to feedback**: Address review comments promptly
- **Be patient**: Maintainers review PRs as time allows

## Project Structure

```
rsm/
├── rsm/               # Main package
│   ├── cli.py         # Command-line interface
│   ├── parser.py      # Tree-sitter integration
│   ├── builder.py     # HTML/CSS/JS generation
│   └── static/        # JavaScript and CSS assets
│
docs/
├── source/            # Sphinx documentation source (RST)
└── build/             # Generated documentation (HTML)

tests/                 # Comprehensive test suite
tree-sitter-rsm/       # Grammar submodule (tree-sitter)
```

## Common Commands

```bash
just                    # List all available commands
just install            # Install development dependencies
just install-local      # Install with local grammar (for grammar dev)
just test               # Run fast tests
just test-all           # Run all tests (including slow)
just lint               # Format and check code
just typecheck          # Run mypy type checking
just check              # Run lint + tests + typecheck
just docs               # Build documentation
just docs-serve         # Serve docs with live reload
just grammar            # Rebuild tree-sitter grammar (advanced)
just rebuild-js-bundle  # Rebuild standalone JS bundle
```

## Getting Help

- **Issues**: Check existing issues or open a new one
- **Questions**: Use GitHub Discussions
- **Bugs**: Include steps to reproduce and expected behavior

## Recognition

All contributors will be recognized in release notes and project documentation.

## License

By contributing to RSM, you agree that your contributions will be licensed under the MIT License.
