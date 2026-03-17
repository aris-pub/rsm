# Changelog

## [1.1.0] - 2026-03-17

### Added

- Auto-generate `id` attributes on unlabeled sections for deep linking
- Handrails support for algorithm blocks
- Temml-KaTeX alias for algorithm rendering
- Meta keys to `:ref:` role
- New BibTeX entry types, fields, and URL fallback in the BibTeX parser

### Fixed

- Tooltip handrails, bibitem URL icons, and appendix appearing before references
- Tooltip whitelist, equation centering, and citation spacing
- Caption styling, asset resolver, and mathblock handrail visibility
- BibTeX keywords leaking into body text as global tokens
- `rsm serve` CSS auto-detect and file watching
- Slash character breaking text parsing
- Missing tooltipster shadow theme in CSS bundle
- Stray `</p>` tag for mathblocks with non-paragraph parents
- Duplicate `</div>` in caption translator breaking section collapse
- Mathblock rendering under Section nodes
- Orphan brackets in inline citations
- Table caption centering by moving caption outside `<table>`
- On-demand Temml loading when no math renderer exists
- Handrail focus highlight appearing during text selection
- Duplicate `<script>` tags increasing page load time

### Changed

- Selected handrail background now uses `--blue-100`
- Pseudocode.js fonts now inherit from document body font and design tokens
- Html asset display label renamed to Widget in captions
- Author rendering redesigned to compact inline format with AuthorBlock/AuthorNotes nodes
- External reference syntax updated

## [1.0.5] - 2026-02-21

### Fixed

- Include braiid directory in rsm-lang package distribution. Previously braiid assets (CSS, MD files) were missing from PyPI package, causing production deployments to fail.

## [1.0.4] - 2026-02-21

### Fixed

- Require tree-sitter-rsm>=1.0.3 to pick up fix for version-specific wheel tagging (resolves Python 3.13 compatibility in production).

## [1.0.3] - 2026-02-21

_No user-visible changes._

## [1.0.2] - 2026-02-21

### Fixed

- Replace `npx tree-sitter` version detection with `sed` in the release recipe, fixing releases in environments without `npx` available.

## [1.0.2] - 2026-02-21

_No user-visible changes._

## [1.0.1] - 2026-02-21

### Added

- Semantic tokens and document symbols support in the LSP server.
- Automated CHANGELOG generation and GitHub release notes.

### Fixed

- LSP runtime error caused by outdated tree-sitter dependency (upgraded to 0.25.0).
- Support for patch-level version bumps in the release recipe.
- Tree-sitter-rsm now builds before LSP tests run in CI.

## [1.0.0] - 2026-02-19

### Added

- Switch to temml for math rendering, with MathJax as fallback
- Pandoc bridge: export RSM documents to other formats and import from them (`rsm export` / `rsm import`)
- Code blocks can now appear inline within paragraphs
- `:figure:` directive supports new `:alt:`, `:dark:`, and `:static:` options
- New `--no-theme-toggle` CLI flag to disable the dark mode toggle in rendered output

### Fixed

- Restore standalone JS bundle as IIFE (with `window.RSM` global)
- Math renders with consistent CDN fonts instead of system fonts
- temml stylesheet no longer loads on pages without math
- Math block spacing regression and undefined citation detection
- LSP navigation used incorrect grammar node type names
