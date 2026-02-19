# Changelog

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
