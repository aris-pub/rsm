# BRAIID

**Design System for RSM Documents**

---

## Purpose

RSM documents occupy a middle ground between two paradigms:

- **Static documents** (PDF, traditional HTML) — readable, archivable, but inert
- **Executable notebooks** (Jupyter, Observable) — interactive, but fragile and environment-dependent

BRAIID is the presentation layer that makes this middle ground tangible. It renders semantic structure visibly, makes every block addressable and navigable, and adds interaction without sacrificing durability. The result is a document you can read like a paper but navigate like a notebook — without requiring execution, servers, or specific runtime environments.

---

## What BRAIID Means

BRAIID is an acronym defining the core qualities of RSM document presentation:

| Letter | Quality | Meaning |
|--------|---------|---------|
| **B** | Beautiful | Considered typography, spacing, and visual rhythm that make reading a pleasure. Form follows function. |
| **R** | Responsive | Works on any viewport from 320px to 2560px. No horizontal scrolling, no broken layouts. |
| **A** | Accessible | WCAG 2.1 AA compliant. Semantic markup, sufficient contrast, keyboard navigable, screen reader friendly. |
| **I** | Interactive | Progressive enhancement. Collapsible sections, navigable structure, block-level affordances — all built on a baseline that works without JavaScript. |
| **I** | Inviting | Reading feels effortless. Progressive disclosure — chrome appears when needed, disappears when not. Respects reader attention. |
| **D** | Durable | Built on stable web standards. Works offline. Archivable. Will render correctly in 20 years. |

---

## Relationship to ARCH

[ARCH](../arch-1.0.md) defines the structural and behavioral floor for web-native research manuscripts. BRAIID builds the aesthetic layer on top of this floor.

| BRAIID Quality | ARCH Requirement |
|----------------|------------------|
| Beautiful | Not required by ARCH — BRAIID's contribution |
| Responsive | ARCH 3.1 — viewport range, relative units, no overflow |
| Accessible | ARCH 1.2, 3.3 — semantic HTML, contrast ratios |
| Interactive | ARCH 4.x — progressive enhancement, static fallbacks |
| Inviting | ARCH 3.2, 3.5 — theming, motion preferences |
| Durable | ARCH 5.x — archivable, offline, standards-based |

**Every BRAIID-styled document must be ARCH-compliant.** BRAIID adds aesthetics and interaction patterns; it cannot subtract from ARCH requirements.

---

## Relationship to Aris Foundations

BRAIID inherits from the Aris Program's Four Foundational Pillars:

- **Universal** → Responsive + Accessible
- **Transparent** → Durable (complete, exportable artifacts)
- **Interactive** → Interactive (obvious)
- **Humane** → Beautiful + Inviting

**Note on "Inviting" in BRAIID:** The fourth pillar is now "Humane" (respect researcher time and humanity). BRAIID uses "Inviting" as the reader-focused reification of this pillar—making manuscripts inviting to read, not dry or adversarial. The broader Humane pillar also encompasses other stakeholder experiences (authors, reviewers) in ways beyond BRAIID's scope as a document design system.

---

## For Theme Creators and Extenders

BRAIID is designed to be customizable. If you're creating a theme, template, or plugin:

### Token Reference

**[TOKENS.md](TOKENS.md)** — The design tokens you can override. Colors, typography, spacing scales. This is your primary customization surface.

### Patterns

**[HANDRAILS.md](HANDRAILS.md)** — The interactive navigation pattern. Understand this before modifying block-level styles.

### Cross-Cutting Behaviors

**[RESPONSIVENESS.md](RESPONSIVENESS.md)** — Viewport behavior, breakpoints. (Stub — needs design decisions)

**[THEMING.md](THEMING.md)** — Dark mode, token cascade, custom themes. (Stub)

**[PROGRESSIVE-ENHANCEMENT.md](PROGRESSIVE-ENHANCEMENT.md)** — What works without JavaScript. (Stub)

### Implementation

**braiid.css** — The reference implementation. Annotated with structure and ARCH compliance notes.

### What's Stable

- Token names and semantic meaning
- Handrail zone structure (HTML contract)
- Block type classes (`.paragraph`, `.theorem`, `.proof`, etc.)

### What May Change

- Specific token values
- Internal zone positioning (implementation detail)
- Animation timing

---

## Current Status

BRAIID 1.0 is in development. The current implementation has known ARCH compliance gaps:

- [ ] External font imports (should bundle or use system fonts)
- [ ] Fixed pixel units in layout (should use relative units)
- [ ] Missing `prefers-color-scheme` media query
- [ ] Missing `prefers-reduced-motion` support
- [ ] Missing print stylesheet
- [ ] Unverified contrast ratios in dark mode

See the annotated `braiid.css` for inline compliance notes.

---

## Files

| File | Purpose | Status |
|------|---------|--------|
| `README.md` | This document. Entry point. | ✅ |
| `TOKENS.md` | Abstract design token definitions | ✅ |
| `HANDRAILS.md` | Handrail pattern specification | ✅ |
| `RESPONSIVENESS.md` | Viewport behavior and breakpoints | Stub |
| `THEMING.md` | Dark mode, custom themes | Stub |
| `PROGRESSIVE-ENHANCEMENT.md` | What works without JavaScript | Stub |
| `braiid.css` | CSS implementation (annotated) | ✅ |

---

## Related Work

BRAIID draws inspiration from:

- **[Distill](https://distill.pub/)** — Pioneered web-native research publishing with interactive explanations, margin notes, and careful typography. BRAIID shares Distill's commitment to reading experience but adds navigable semantic structure.
- **[Tufte CSS](https://edwardtufte.github.io/tufte-css/)** — Demonstrated that web documents can achieve print-quality typography. Influenced BRAIID's approach to margins and sidenotes.
- **[Jupyter](https://jupyter.org/) / [Observable](https://observablehq.com/)** — Established the cell-based interaction paradigm that BRAIID adapts for static documents through the handrail system.
