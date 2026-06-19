# Changelog

## [1.4.0] - 2026-06-19

### Added
- A floating proof-tree rail that maps a proof's structure, highlights the step you're currently reading, and offers a focus mode that dims everything else. Switch between its Map and State tabs to follow the proof's outline or inspect the assumptions and claims in scope at each step.
- A two-scope floating sidebar with a built-in notation reader, redesigned as floating cards with a tooltip on every control. Proofs you've collapsed are now mirrored in its Proof tab.
- Reader-rebindable notation macros, so readers can change how a document's notation is rendered for them.
- A `:collapsed:` metakey that starts any block in its collapsed state.
- A `:of:` metakey for declaring which result a detached proof proves.
- Improved proof-scope analysis: introductions such as `let` and `assume` now carry past a co-located claim instead of being cut off by it.

### Fixed
- Assumptions introduced in an `ASSUME...PROVE` step now stay local to that step, while `let`/`assume` introductions correctly remain in scope for later sibling steps.
- Copying from handrails now re-focuses the window first, so clipboard writes no longer silently fail.
- Nested step text now clears the right-hand info zone, clicking a handrail's menu controls no longer selects the whole block, and the collapse-menu labels and figure static toggle have been restored.
- Figures and embeds get a chromeless alignment handrail.
- Keyboard shortcuts: menu shortcuts work again for the single shared menu (with Escape to dismiss), and shortcuts are ignored while a modifier is held or an editable field is focused.
- Unnumbered sections are excluded from the table of contents.
- Pathless `:html:` blocks no longer emit a spurious empty `<img>`.
- Accessibility: bibliography DOI and URL links now have accessible names, plus a broader accessibility pass over the floating sidebar.

## [1.3.1] - 2026-06-14

### Fixed

- Pointed the bundled tree-sitter-rsm grammar at the ABI-14 parser, restoring compatibility with the language server.

## [1.3.0] - 2026-06-14

### Added
- The table of contents now offers a dependency-graph tree view, letting you navigate your document by how its sections relate to one another.

### Fixed
- Binary image assets are now read correctly as raw bytes instead of UTF-8 text, so images no longer get corrupted during processing.
- Documents that contain no math are skipped during math typesetting rather than producing a spurious warning.

## [1.2.0] - 2026-04-07

### Added

- Static view toggle for figures and HTML widgets, allowing readers to switch between interactive and static renderings
- Complete LaTeX export with braiid styling matching Typst output, including theorem environments via Lua filter
- Braiid Typst template for PDF export with figure styling, numbering, and author extraction
- Clickable cross-references and citation links in PDF export
- Blue left border on theorem blocks and Halmos square on proofs in PDF
- Static fallback images for Html and Video assets in PDF export
- Shared figure counter between Figure and Html assets
- Tree-sitter syntax highlighting in documentation RSM examples
- Singleton handrail menu, reducing DOM complexity by 43%
- SVG icon deduplication via `<defs>`/`<symbol>`/`<use>`
- Images served by URL in non-standalone mode (base64 only in standalone)
- Source-only mode for the RSM directive
- LSP requests for source/preview navigation
- Support for `:preamble:` meta key on math and mathblock nodes
- External cross-references prefixed with manuscript title
- Responsive side padding for mobile viewports
- Source offset attributes on inline elements
- Batch math typesetting with `requestAnimationFrame` yields for better performance

### Fixed

- Handrail menu stays open when moving between items
- Icon clipping in handrail menu SVGs
- Inline math and cross-references wrapping to a new line separately from trailing punctuation
- Codeblock indentation and syntax highlighting in standalone mode
- Figure children overflowing their container
- iframe ResizeObserver for interactive content
- Strict mode now checks CST for errors instead of AST
- Equation numbers rendered as overlay instead of grid wrapper
- Image assets resolved through asset resolver as data URIs
- Bibliography items breaking across pages
- Orphaned theorem/proof titles and headings at page bottom
- Duplicate TOC emission removed — only one TOC rendered after abstract
- Handrail and heading colors unified to blue-700/blue-900
- Tighter spacing on first page, headings, and abstract
- LaTeX output compiles without setup (braiid.sty copied alongside output)
- LaTeX standalone output, section numbering, and align environments
- Pandoc translator missing handlers and caption format
- Semantic token spans use character length and split multi-line tokens correctly
- Invalid child positions handled in `rsm/nodePosition`
- Uniform text color before document load

### Changed

- Replaced pyfilesystem2 dependency with pathlib and shutil
- Unified inline-math-wrapper and inline-ref-wrapper into a single inline-wrapper

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
