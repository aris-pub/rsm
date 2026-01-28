# RSM Language Server

Language Server Protocol (LSP) implementation for RSM (Rigorous Scientific Manuscripts).

## Status: Phase 0 & 1 Complete (Under Review)

The LSP is currently in active development. Phase 0 (Foundation) and Phase 1 (Python AST Integration) are complete and undergoing thorough review before proceeding to Phase 2.

**What Works Now**:
- ✅ Syntax error detection (real-time, ~10ms)
- ✅ Tag completion (50+ RSM constructs)
- ✅ Python AST integration via `rsm parse --json`
- ✅ Structure diagnostics (missing titles, unlabeled theorems, empty sections)
- ✅ Basic reference checking (via Python transformer errors)
- ✅ 92 passing tests with high core coverage

**What's Next** (Phases 2-6):
- Mathematical rigor (proof validation, notation tracking)
- Scientific writing quality (claims, terminology, evidence)
- Web-native checks (accessibility, dark mode, links)
- Advanced LSP features (go-to-definition, hover, find references)
- Studio integration
- npm release

See [STATUS.md](STATUS.md) for detailed progress and [IMPLEMENTATION_PROGRESS.md](IMPLEMENTATION_PROGRESS.md) for the full development log.

## Features (Phase 0 & 1)

### Layer 1: Immediate Feedback (Tree-sitter CST)
- ✅ Syntax error detection (ERROR nodes, missing `::`)
- ✅ Tag completion (`:theorem:`, `:proof:`, `:claim:`, etc.)
- ✅ Incremental parsing with caching
- ✅ Updates on every keystroke (~10ms)

### Layer 2: Semantic Analysis (Python AST)
- ✅ Structure checks:
  - Missing manuscript title
  - Sections without labels
  - Theorems/lemmas/definitions without labels (recommended)
  - Empty sections
- ✅ Reference checks (limited):
  - Undefined references (via Error nodes from Python transformer)
- ✅ Updates debounced (500ms default)
- ⏳ Mathematical rigor (proofs, notation) - Phase 2
- ⏳ Scientific writing (claims, terminology) - Phase 2
- ⏳ Web-native (accessibility, dark mode) - Phase 3

## Quick Start

### Prerequisites
- Node.js ≥18.0.0
- Python with RSM package installed (`uv run rsm --version` works)
- RSM tree-sitter grammar built (`../../tree-sitter-rsm/`)

### Testing the Server

```bash
# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test                # 92 tests, all passing
npm run test:coverage   # Core coverage: 93-100%

# Test via terminal
node test-client.js     # Automated LSP protocol test
```

**Expected Output**:
- Server initializes with completion provider
- Syntax errors detected immediately
- Tag completion works (`:the` → `:theorem:`)
- Semantic diagnostics after 500ms (theorems without labels, etc.)

### Usage (Future - Phase 4)

Currently tested via `test-client.js`. Emacs/LSP-mode integration planned for Phase 4.

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Watch mode
npm run watch

# Run all tests (unit + integration)
npm test

# Run tests with coverage
npm run test:coverage

# Lint
npm run lint

# Format
npm run format
```

### Project Structure

```
packages/rsm-lsp/
├── src/
│   ├── server.ts              # LSP server entry point
│   ├── layer1/                # Tree-sitter CST (fast)
│   │   ├── parser.ts          # Tree-sitter wrapper
│   │   ├── completion.ts      # Tag completion (50+ tags)
│   │   └── navigation.ts      # Label extraction (not implemented)
│   ├── layer2/                # Python AST (semantic)
│   │   ├── python.ts          # Subprocess wrapper
│   │   ├── ast.ts             # AST types & helpers
│   │   ├── cache.ts           # AST caching
│   │   └── debounce.ts        # Debouncing
│   ├── diagnostics/
│   │   ├── engine.ts          # Diagnostic dispatcher
│   │   └── rules/
│   │       ├── structure.ts   # Structure checks
│   │       └── references.ts  # Reference checks
│   └── utils/
│       ├── location.ts        # Position/range helpers
│       └── logger.ts          # Logging
└── test/
    ├── unit/                  # 59 unit tests
    ├── integration/           # 6 integration tests
    └── fixtures/              # Test RSM files
```

## Architecture

The LSP uses a **two-layer architecture** to balance speed and depth:

### Layer 1: Tree-sitter CST (Fast - ~10ms)
- Incremental parsing on every keystroke
- Syntax error detection (ERROR nodes)
- Tag completion
- Simple pattern-based rules

### Layer 2: Python AST (Semantic - ~300ms)
- Debounced (500ms default) to avoid redundant parses
- Calls `uv run rsm parse <tempfile>` subprocess
- Full semantic AST with resolved references
- Structure and reference diagnostics
- Cached by document URI and version

**Data Flow**:
```
User types → Layer 1 (immediate syntax errors)
          ↓
    Wait 500ms (debounce)
          ↓
    Layer 2:
     1. Write document to temp file
     2. Call `rsm parse <file> --log-format json`
     3. Parse JSON → TypeScript AST
     4. Run semantic diagnostics
     5. Merge with Layer 1 diagnostics
     6. Send to editor
```

## Testing

### Test Coverage

**92 total tests** (all passing):
- 27 tests from Phase 0 (parser, completion)
- 65 tests from Phase 1 (Python integration, diagnostics)

**Core Logic Coverage**:
- `structure.ts`: **100%**
- `ast.ts`: **100%**
- `completion.ts`: **100%**
- `engine.ts`: **93.33%**
- `parser.ts`: **93.15%**
- `python.ts`: **74.54%**

**Not Yet Covered** (planned for Phase 4):
- `server.ts`: 0% (needs LSP protocol integration tests)
- `cache.ts`: 0% (tested via integration tests)
- `debounce.ts`: 0% (tested via integration tests)

### Running Tests

```bash
# All tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm run test:coverage

# Specific test file
npm test test/unit/layer2/python.test.ts
```

## Configuration (Planned - Phase 2)

Configuration system is designed but not yet implemented. Future usage:

```yaml
# .rsm/config.yaml
diagnostics:
  mode: debounced  # or "on-save"
  debounceMs: 500

  structure:
    missingTitle: warning
    emptySection: warning

  references:
    undefinedLabel: error
```

## Known Limitations

1. **Reference tracking is limited**: Python transformer pre-resolves references, so we can't easily track which labels are actually used (can't detect unused labels)

2. **Some errors have no position**: Error nodes with `[-1, -1]` positions can't be accurately positioned in the editor

3. **No configuration system yet**: All diagnostic rules are hardcoded (severity, enable/disable)

4. **No LSP advanced features yet**: Go-to-definition, hover, find references planned for Phase 4

## Development Status

See [IMPLEMENTATION_PROGRESS.md](IMPLEMENTATION_PROGRESS.md) for detailed commit-by-commit progress.

**Current Phase**: Review (before Phase 2)

**Branch**: `feat/rsm-lsp`

**Last Updated**: 2026-01-28

## License

MIT
