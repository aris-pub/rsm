# RSM Technical Reference

---

## What RSM Is

A markup language focused on meaning, not appearance.

| Tool | Philosophy |
|------|------------|
| LaTeX | Appearance (beautiful typesetting) |
| Markdown | Simplicity (readable source) |
| Word/Docs | What-you-see-is-what-you-get |
| Typst | Composability (programmable typesetting) |
| Quarto | Reproducibility (executable documents) |
| RSM | Meaning (semantic structure) |

Write `:theorem:` not `<div class="theorem-container">`. Write `:figure:` not a pile of HTML. The format handles the hard parts.

### RSM vs Quarto/Jupyter

Quarto and Jupyter produce executable documents. The document *is* the computation.

RSM produces static documents with optional embedded interactivity. The document is the *output* of scholarship, not the process.

| | Quarto/Jupyter | RSM |
|---|----------------|-----|
| Paradigm | Executable document | Static document with interactivity |
| Runtime | Required | Browser only |
| Archival | Fragile (dependency rot) | Robust (HTML is forever) |
| Hosting | Complex | Static files anywhere |
| Sharing | "Install these 47 packages" | A URL |

RSM says: the paper describes the research. The code lives in a repo. They're separate artifacts.

### Design Principles

- **Semantic-first**: Structure represents meaning, not formatting. RSM's explicit semantic markup serves both human readers (accessibility, clarity) and machine readers (AI retrieval, synthesis). Empirical studies show that RAG systems with semantic structure consistently outperform text-only approaches. See: [Semantic Enrichment research](/cross/market/research/2026-02-semantic-enrichment-ai.md)
- **Research-native**: Built for academic writing patterns
- **Plain text**: Git-friendly, version-controllable
- **Web-native**: Compiles to HTML, not PDF-first

### Competitive Context

**vs LaTeX**: Web-native output. No compilation errors. Collaboration built in.

**vs Typst**: Web-native from the start, not PDF with HTML as afterthought.

**vs Quarto**: Static and permanent. No runtime. No dependency rot.

**vs Markdown**: Research semantics built in (theorems, proofs, citations).

### Output

RSM compiles to BRAIID-compliant HTML. See [BRAIID Design System](#braiid-design-system) below.

For program-level positioning, see [/program/market/messaging.md](../../../program/market/messaging.md).

---

## Architecture Decisions

**Output Target:** RSM compiles to [ARCH 1.0-compliant HTML](/program/strategy/arch-1.0.md) with BRAIID styling.

### Document Configuration: Frontmatter vs CLI Flags

**Decision:** RSM supports per-document configuration via frontmatter. Settings are categorized by their nature:

| Category | Mechanism | Examples |
|----------|-----------|----------|
| **Per-document properties** | Frontmatter | TOC depth, numbering schemes, theme |
| **Per-build decisions** | CLI flags | Output path, standalone mode, CSS file |

**Per-Document (Frontmatter)**

Properties intrinsic to the document itself:

- **TOC depth**: How many heading levels appear in table of contents
- **Numbering schemes**: Theorem numbering (global, per-section, etc.)
- **Color theme** (future): Document aesthetic preset

These travel with the document. If you share the `.rsm` file, it renders the same way.

**Per-Build (CLI Flags)**

Build-time decisions that vary per invocation:

- `--output`: Where to write the output
- `--standalone`: Packaging format (single HTML vs separate assets)
- `--css`: Which CSS file to apply (overrides auto-detection)
- `--handrails`: Debug features for development
- `--menu-right`: UI preference for context menu position
- `--verbose`, `--log-*`: Logging and tooling behavior
- `--port`, `--no-browser`: Development server options

**The test:** "If I share this .rsm file with someone, should it render the same way?"
- **Yes** → Frontmatter (document property)
- **No** → CLI flag (build decision)

**Studio Implications**

This design makes RSM Studio straightforward: Studio reads frontmatter from the document and applies those settings when building. No separate metadata storage or build configuration needed.

CLI flags still work as overrides for one-off builds or custom workflows.

### No Frontmatter Variants

**Decision:** RSM uses a single frontmatter format, not multiple variants (YAML/TOML/JSON).

**Rationale:**
- Simpler parser implementation
- No ambiguity about which format to use
- Can design format specifically for RSM's needs

**Format TBD:** Likely custom RSM-style syntax to match document semantics, but YAML remains an option for familiarity.

### Opinionated Defaults

RSM is opinionated about many formatting choices that other systems make configurable:

**Not configurable (by design):**
- Bibliography style (one high-quality HTML style)
- Cross-reference format (standardized for web reading)
- Math macros (handled separately, not in document config)
- Custom layout (use CSS, not config)

**Why:** These are either:
1. Print-era conventions with no web benefit (bibliography styles)
2. Better handled by other mechanisms (CSS for layout)
3. Maintained separately for reusability (math macros)

Keeping the config surface small maintains RSM's "it just works" philosophy.

---

## BRAIID Design System

**Beautiful, Responsive, Accessible, Interactive, Inviting, Durable**

### What RSM Produces

Documents rendered with the BRAIID design system:

- **Beautiful** — typography, layout, visual design
- **Responsive** — works on any device
- **Accessible** — screen readers, WCAG compliance
- **Interactive** — embedded widgets, not bespoke apps
- **Inviting** — readable, respects reader time
- **Durable** — static files, no runtime rot, works in 50 years

### What BRAIID Is (For Now)

The design system RSM uses. Typography, layout, components, responsive behavior, accessibility defaults.

Concrete: a CSS framework, a component library, versioned (BRAIID 1.0).

Aspirational: the name captures what the output should be.

**Future possibility:** BRAIID becomes a standard. Aris grants certification. Other tools can produce BRAIID-compliant output. But that's earned through traction, not declared today.

### How Interactivity Works

RSM provides an "interactive-shaped hole."

You don't build interactives in RSM. You embed them:

- Plotly charts (exported as self-contained HTML)
- Observable notebook cells
- D3 visualizations
- 3D model viewers
- YouTube videos
- Whatever runs in an iframe or is self-contained JS

RSM handles sizing, captions, fallbacks, responsive behavior. The interactive is a black box that gets embedded.

Most papers won't have custom interactives. That's fine. The baseline — beautiful typography, responsive layout, accessible, permanent — is already better than PDF.

### Technical Requirements

**HTML Structure**
- Semantic HTML5 elements
- Accessible markup patterns
- Self-contained (single file or minimal dependencies)

**CSS**
- Responsive design (mobile-first)
- Accessibility (WCAG compliance)
- Typography optimization
- Print-friendly styles

**JavaScript**
- Optional (progressive enhancement)
- No runtime dependencies
- Graceful degradation

**Performance**
- Fast load times
- Works on slow connections
- Minimal resource usage

### Durability

BRAIID documents are:
- **Static files** — no server required
- **Self-contained** — no external dependencies that can break
- **Standards-based** — built on HTML/CSS/JS that will work forever
- **Archive-friendly** — can be preserved and accessed decades later

For program-level context, see [/program/market/messaging.md](../../../program/market/messaging.md) for how BRAIID fits into the Aris vision.
