# Changelog

## [2.0.0] - 2026-11-22

### Added

- New `:tabs:` and `:tab:` environment. LSP completion offers both tags.
- New `:plain-title:` key, which sets the plain text for the page's `<title>`.
- New `:as-paragraph:` option, which places a figure, widget or video at the level of a paragraph.
- New `:blockname:` key, which sets the name used for a theorem-like block, figure, widget, video or table.
- An eyebrow: a short label above the manuscript title.
- Raw HTML in documents: `:html:` for inline HTML, `:htmlblock:` for block HTML, and `:rawhtml:` with an `:alt:` fallback. Figures can hold HTML. The pandoc import turns raw HTML into these tags and drops HTML comments.
- Readers can pin several blocks at once. The panel stays open while any pins remain.
- Asides now appear in the margin. On narrow screens, readers tap a phrase to open its aside, and asides also open without JavaScript.
- Notes and asides are written as a call and a definition, and are numbered in the order of their calls. Footnotes are collected in one Notes list, and readers can hover or tap a note to preview it.
- Captions move to a right-hand margin column when the page has room.
- A document minimap replaces the browser's scrollbar.
- Readers can tap a reference to preview its target.
- A calc can go anywhere that a display equation can go.
- `:toc: :orientation: horizontal` lays out the table of contents graph from left to right.
- List and graph buttons on the table of contents heading line and in the sidebar's Contents view.
- A redesigned sidebar with an icon strip, a panel that pushes the page aside, and a bar for phones. The new `--sidebar` build option controls it.
- Author-year citations, set with the `:citation-style:` config key.
- Nested lists.
- A collapsed proof header shows the number of top-level steps.
- When no proof is selected, the proof panel lists the document's proofs.
- A fold label names the content that a folded block hides.
- Headings, `:title:` values, and the link text of `:url:` and `:ref:` can contain inline markup.
- Macros defined in a `:mathblock:` `{:preamble:}` also apply to inline math. A preamble does not get an equation number.
- Keyboard users can scroll a display equation that is wider than its column.
- On load, the page lists every notation macro that differs from its default. Figures are told when a symbol changes.
- Built pages show a spinner while they load, and the page appears once it is ready.
- The pandoc import now handles tables, preamble `\newcommand` macros, bibliographies, cross-references, abstracts, dates, author blocks, nested lists, figure and table labels, and the `:problem:`, `:exercise:` and `:porism:` blocks.
- The pandoc export includes a video's still image.
- A warning for a cite of a label that is not a bibliography entry.
- Meta values are checked, and bad values are logged. Unknown meta keys are logged by name and ignored.
- Parse errors that the parser repairs with a missing node are now reported.
- Lint messages include end positions, and JSON log records include positions.
- rsmify, a host service that converts arXiv papers to RSM.

### Changed

- RSM now requires tree-sitter 0.26 (below 0.27) and uses an ABI 15 grammar.
- Python 3.10 is no longer supported.
- MathJax is once again RSM's math renderer. Math is set in Latin Modern, and the font is served from `static/`.
- Builds use relative `static/` and `assets/` folders, and the math libraries are pinned copies in `static/`.
- Standalone builds include braiid.css, jQuery and the tooltipster JavaScript in the file and no longer load them from a CDN.
- The page `<title>` is written as plain text, with math written as `$TeX$`.
- Block titles are translated with the document's notation.
- Hyphenated words are kept on one line, including across markup, links and front matter.
- Bibliography entries are shown as cards. On narrow screens, the DOI and back links sit on one row.
- A figure image that is wider than the text column shrinks to fit.
- On touch screens, handrails sit on one line and the text gets 12px more width on each side.
- The back pill hides after 8 seconds without use.
- An unknown tag in body text produces one parse error, and that error covers the whole tag.
- Positions in parse error logs and in error text on the page start at 1.
- Node positions are stored as plain tuples.
- An app returns `None` when the source cannot be parsed, and the parser error is raised again.
- The dark theme works without JavaScript.
- The unused `:theme:` option and the theme toggle styles have been removed.

### Fixed

- A reference to a file that cannot be parsed shows an error.
- An HTML file that is not UTF-8 shows the HTML asset error box.
- Text content is HTML-escaped, so math source cannot open tags. Titles and reference text are escaped too.
- Lines of text that start with a number parse again.
- A list written inside a paragraph stays in that paragraph.
- A comma before a closing brace is dropped in both block and inline meta.
- A parse error inside a meta is logged instead of dropped.
- The space between a note or aside call and the next inline node is kept.
- Blocks with no number get no "None" in captions or reference text. For example, a reference reads "Theorem", not "Theorem None".
- Raw HTML and inline math keep the punctuation that follows them on the same line.
- Long links wrap with the text, and link text keeps every line when it wraps.
- Math in link text renders on pages with handrails.
- Wide display math scrolls in its own box. Figures and table wrappers no longer show a vertical scrollbar, and figure content that is too tall is clipped.
- Every content zone of a block shrinks to fit the column.
- A reference to content inside a collapsed fold opens the fold.
- A shared view lands on the right block, keeps the pin, and applies its notation before the first typeset.
- A link's target is placed before the 3-second fallback shows the page, and the reader's place is kept if they act before the page finishes loading.
- Pinned and previewed blocks show widgets as their still images. Previews of a calc show the calc instead of an empty box.
- Text in an `:as-paragraph:` block can be selected, and a click on its content does not select the block around it.
- Closing the pinned block also closes the sidebar panel on desktop.
- The `:accent:` color applies to links, keywords, action colors and the active handrail.
- Handrail pill colors follow the rail and the page. The Source menu item is disabled for an element that has no source.
- Dark mode: chevron color and a stronger aside line and tint. The source window is dark under the dark theme.
- Sidebar colors follow the document's colors, and faded sidebar map labels are easier to read.
- The table of contents graph has the same layout on every build and closer spacing when it is tall. Its root is a muted dot, a long root collapses to "Top" on narrow screens, every listed section is a link, and switching the table of contents view no longer throws an error.
- Videos fit their figure.
- A labeled image figure no longer has its id twice.
- Bibliography entries show the volume and issue, and DOIs are normalized.
- Proof state section markers read "§n" instead of "(n)".
- Folder builds copy figure media, so the folder works on its own. A `src="#id"` is no longer copied as a file.
- The pandoc export keeps a widget `:blockname:` that starts with "Widget", and keeps hand-written `:ref:` text that points to a static widget.
- LSP tag completions match the tags and meta keys in the grammar, and completion continues after a hyphen or digit.
- Removing a display equation no longer leaves it watched by the math scrolling code.
- Text next to an error in the parse tree keeps its red error style.
- Tooltip CSS no longer overrides document styles.
- Space is kept for the drawer bar at the end of the document.

## [2.0.0] - 2026-11-22

### Added

- Lists can be nested.
- A collapsed proof header shows how many top-level steps the proof has.
- Equations can carry CSS classes through `\class`.

### Fixed

- A labelled image figure no longer writes its id twice.
- A long table of contents tree root is shortened to "Top" so that it fits on a narrow screen.
- The Source item in the handrail menu is disabled for an element that has no source.
- Every section listed in the table of contents is a link, and a broken reference keeps its error style.
- Inline links stay inline, so a long link wraps with the text around it.
- Bibliography entries show the volume and issue, and DOIs are normalized.
- Proof-state section markers read "§n" instead of "(n)".
- Sidebar colours follow the document's colour tokens, and faded labels in the sidebar map stay readable.
- The page leaves room at the end for the resting drawer bar.
- The active handrail background and the handrail pills follow `:accent:` and the page colours instead of a fixed blue.
- `:accent:` changes link, keyword and action colours in body-only output too.
- Tooltip CSS no longer overrides the document's own styles.
- Figures and table wrappers never show a vertical scrollbar.
- Standalone output includes braiid.css, jQuery and the tooltip script in the file, so it no longer loads them from a CDN.
- A folder build copies figure media, so the folder works on its own.
- Caption links have better contrast, the static fallback image has alt text, and spacing around link text is correct.
- The dark theme applies without JavaScript.
- Collapsed folds open when a reference points to content inside them.
- Wide display math scrolls inside its own box.
- Text content is HTML-escaped, so math source can no longer open HTML tags.

### Changed

- Python 3.10 is no longer supported.
- RSM now requires tree-sitter 0.26 and uses a rebuilt ABI 15 grammar.
- New `:tabs:` and `:tab:` environments, with LSP completion.
- New `:plain-title:` sets the plain text for the page's `<title>`. Without it, the title is written as text, with math as `$TeX$`.
- `:html:` holds inline raw HTML and `:htmlblock:` holds block raw HTML. Both can go inside figures. Raw HTML keeps its trailing punctuation on the same line.
- New `:blockname:` sets the name for theorem-like blocks, figures, widgets, videos and tables.
- New `:as-paragraph:` places a figure, widget or video at the level of a paragraph.
- New eyebrow: a short label above the manuscript title.
- Headings, `:title:` values and the link text of `:url:` and `:ref:` can contain inline markup. Math in link text renders on handrail pages.
- Notes and asides are written as a call and a definition, and are numbered in the order of their calls. Footnotes are collected in one Notes list, with previews on hover and tap. Asides attach to a phrase and appear in the margin, open with a tap on narrow screens, and open without JavaScript.
- Author-year citations are available through the `:citation-style:` setting.
- `:toc: :orientation: horizontal` lays out the table of contents graph from left to right.
- A calc can go anywhere that a display equation can go, and a reference to a calc previews the calc.
- Macros in a `:mathblock:` `{:preamble:}` also apply to inline math, and a preamble gets no equation number.
- Block meta and inline meta follow the same rule, and a comma before the closing brace is dropped.
- A list written inside a paragraph stays in that paragraph.
- Lines of text that start with a number parse again.
- Redesigned sidebar with an icon strip, a panel that pushes the page aside, and a bar on phones. The new `--sidebar` build option controls it. The Contents view and the table of contents heading have list and graph buttons.
- Readers can pin several blocks. Pinned and previewed blocks show widgets as their still images.
- A shared view opens at the right block, keeps the pin, and applies its notation before the first typeset. On load, the page announces every macro that differs from its default, and the no-JavaScript math source uses the notation defaults.
- Built pages load behind a spinner and appear once the layout is settled. If the reader acts after the early reveal, the page keeps their place.
- A document minimap replaces the browser's scrollbar.
- Captions go in a right-hand margin column when there is room.
- Tapping a reference previews it.
- A fold label names what the folded block hides.
- The back pill hides after 8 seconds without use.
- MathJax is RSM's math renderer again. Math uses Latin Modern, served from `static/`.
- Bibliography entries appear as cards. On narrow screens, the DOI and back links share one row.
- The table of contents graph has the same layout on every build and closer spacing when it is tall. Its root is a muted dot, and the main graph previews blocks the way the sidebar graph does.
- Hyphenated words stay on one line.
- A figure image that is wider than the text column shrinks to fit, a video fits its figure, and content in a figure clips instead of scrolling.
- Keyboard users can scroll a display equation that is wider than its column.
- The proof panel lists the document's proofs when no proof is selected.
- Accessibility: the sidebar has keyboard folding and a skip link, and the Notation panel has better contrast.
- Dark mode: chevron colour, a stronger aside line and tint, and a dark source window.
- On touch screens, handrails fit on one line and the text column is 12px wider on each side.
- Parse errors in logs and in the page use 1-based positions. Lint messages include end positions, and JSON log records include positions.
- An unknown meta key is logged by name and ignored, and meta values are checked. Parse errors inside a meta are logged instead of dropped, an unknown tag in body text is reported as one parse error, and invalid input that the parser repairs is reported.
- Citing a label that is not a bibliography entry gives a warning.
- A reference to a file that cannot be parsed shows an error. The parser error for such a file is raised again, and the app returns None.
- An HTML file that is not UTF-8 shows the HTML asset error box.
- Block titles use the document's notation.
- Titles and reference text are HTML-escaped.
- Pandoc import handles bibliographies, cross-references, tables, `\newcommand` macros from the preamble, abstract, date, the author block, nested lists, escaped colons, and `:problem:`, `:exercise:` and `:porism:` blocks. Raw HTML is imported as `:htmlblock:` or `:html:`, and HTML comments are dropped.
- Pandoc export includes a video's still image, keeps hand-written `:ref:` text that points to a static widget, and keeps a widget's `:blockname:` when it starts with "Widget".
- New rsmify service converts arXiv papers to RSM, at the `/r` URL.
- Built output uses relative `static/` and `assets/` folders, with fixed versions of the math libraries in `static/`. `src="#id"` is left as it is.
- LSP tag completion matches the grammar's tags and meta keys, and keeps working after a hyphen or digit.

## [1.5.2] - 2026-10-08

### Changed

- `rsm.render` and the build apps no longer take `add_source`. That one flag bundled two unrelated behaviors, so it is now two independent flags. `source_offsets` stamps `data-source-start` and `data-source-end` on blocks and inline spans. `copy_source` emits the hidden full-source div that the copy-source modal reads. `render()` defaults both to False. The interactive build apps default both to True. Callers that passed `add_source=True` should pass `source_offsets=True, copy_source=True`, or just the one they need.

## [1.5.1] - 2026-07-13

### Added

- The language server now emits an `rsm/indexReady` notification once the document index is built, and navigation requests are guarded against a stale syntax tree so features like go-to-definition no longer act on outdated parse results.

### Fixed

- Brand assets are now fetched from the `aris-pub/brand` source, with support for overriding the location.
- Syntax highlighting now resolves `highlights.scm` from the `tree-sitter-rsm` package root, so highlighting works reliably regardless of where the language server is installed.

## [1.5.0] - 2026-06-29

### Added
- Drag-to-reorder proof steps: logic-preserving reordering with scoped dependencies, a handle that replaces the step dots, and Esc to cancel. When a reorder would break the proof, the rejection now names the blocking dependency. Disabled on touch devices (labeled "desktop only"), with screen-reader and reduced-motion support.
- New `:calc:` construct for calculational proofs.
- Dependency lens: a sticky upstream/downstream cone projected from any step or result.
- Reader-rewritable parameterized notation.
- Shareable links that capture the current presentation state.
- Reversible in-document jumps using the browser's native Back button, plus a "back pill" affordance over native Back.
- Reworked focus mode (prose trigger, accessibility, native collapse), off by default.
- Reader type controls in a new Reading sidebar tab.
- Proof rail upgrades: a document-wide State panel with uniform jump rows and provenance markers, a more legible proof DAG with goal previews, external named-result dependencies surfaced in the DAG, and the ability to pin a referenced block into the rail.
- Mobile bottom-drawer for the proof rail on narrow screens (1100px and below).
- Reader collapse state now persists across visits for all blocks, including section headings.
- Print/PDF stylesheet for clean paper export.
- Math is now typeset in reference tooltips.

### Fixed
- DAG labels keep a constant on-screen size at any zoom.
- Collapsed handrail shows a short curved tick instead of a misaligned rule, and proof tombstones align to a single content-edge column.
- Static-fallback (`:static:`) sizing, no-JS reveal, and dark variant.
- Sidebar tooltips no longer overflow into full-width banners.
- Reference tooltips now appear on cloned State-panel entries.
- The space between a construct keyword and a leading reference is preserved.
- Pandoc export emits tables and figure references in a portable encoding.
- Renamed the proof-structure sub-tab to "Steps".

### Changed
- Responsive proof rail that shrinks, then pushes content aside, then collapses to a drawer; the collapsed rail now shrinks to just the toggle handle, with handrail controls and touch-device collapse.
- Accessibility pass: front-matter headings, a TOC navigation landmark with named links, focus-visible styles, a 54rem default measure, and WCAG-AA contrast on quiet text, keyword tags, and step chips.
- Sidebar TOC-DAG readability, with a selection-driven (rather than scroll-driven) proof rail.
- Step numbers stay in a single column under nesting.

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
