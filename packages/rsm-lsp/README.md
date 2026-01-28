# RSM Language Server

Language Server Protocol (LSP) implementation for RSM (Rigorous Scientific Manuscripts).

## Features

The RSM LSP provides real-time linting and IDE features for scientific writing:

### Layer 1: Immediate Feedback (Tree-sitter CST)
- Syntax error detection
- Tag completion
- Basic navigation
- Updates on every keystroke (~10ms)

### Layer 2: Semantic Analysis (Python AST)
- Mathematical rigor checks (proofs, notation, constructs)
- Scientific writing quality (claims, terminology, evidence)
- Web-native best practices (accessibility, dark mode, links)
- Updates debounced (500-1000ms) or on-save

## Installation

```bash
npm install -g rsm-lsp
```

## Usage

### Emacs (eglot)

Add to your `.emacs` or `init.el`:

```elisp
(with-eval-after-load 'eglot
  (add-to-list 'eglot-server-programs
               '(rsm-mode . ("rsm-lsp" "--stdio"))))
```

### Emacs (lsp-mode)

```elisp
(with-eval-after-load 'lsp-mode
  (add-to-list 'lsp-language-id-configuration '(rsm-mode . "rsm"))
  (lsp-register-client
   (make-lsp-client :new-connection (lsp-stdio-connection "rsm-lsp")
                    :major-modes '(rsm-mode)
                    :server-id 'rsm-lsp)))
```

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Watch mode
npm run watch

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Lint
npm run lint

# Format
npm run format
```

## Architecture

The LSP uses a two-layer architecture:

1. **Layer 1 (Tree-sitter CST)**: Fast syntax checking and basic features
2. **Layer 2 (Python AST)**: Deep semantic analysis via `rsm parse --json`

This design provides immediate feedback while typing, with comprehensive analysis after a short delay.

## Configuration

Create `.rsm/config.yaml` in your project root to customize diagnostic rules:

```yaml
diagnostics:
  mode: debounced  # or "on-save"
  debounceMs: 500

  structure:
    missingTitle: warning
    missingLabels: warning

  references:
    undefinedLabel: error
    undefinedCitation: error

  mathematical:
    claimWithoutJustification: warning
    undefinedNotation: warning

  scientific:
    unsubstantiatedClaim: info
    undefinedAcronym: warning

  webNative:
    figureWithoutAltText: warning
    deadLink: error
```

See [Configuration Reference](docs/configuration.md) for all available options.

## License

MIT
