# RSM Strategy

**Product:** RSM (Readable Science Markup) + BRAIID (Design System)
**Status:** Core foundation of Aris Program

---

## Strategic Context

**RSM is the foundational idea that started the Aris Program.**

Everything else — Studio, Press, BRAIID — exists to support web-native scientific manuscripts written in RSM.

---

## What is RSM?

RSM (Readable Science Markup) is a semantic markup language for scientific manuscripts.

**Design principles:**
- **Semantic-first:** Structure over appearance (meaning, not formatting)
- **Research-native:** Built for academic papers (citations, math, figures, cross-references)
- **Web-native:** HTML is primary output, PDF is export target
- **Readable:** Natural syntax (not LaTeX complexity, not Markdown limitations)

**Key differentiator:** RSM is about **meaning** (semantic structure), not appearance, composability, or reproducibility.

---

## What is BRAIID?

BRAIID is the design system RSM uses to render beautiful web-native manuscripts.

**BRAIID = Beautiful, Responsive, Accessible, Interactive, Inviting, Durable**

- **Beautiful** — Distill-level typography and layout
- **Responsive** — Works on any device (mobile-first)
- **Accessible** — WCAG compliance, screen readers
- **Interactive** — Embedded widgets (not bespoke apps)
- **Inviting** — Readable, respects reader time
- **Durable** — Static files, no runtime rot, works in 50 years

**The pitch:** "Write RSM. Get BRAIID."

BRAIID quality output is default, not optional. This is the moat.

---

## Competitive Positioning

**vs LaTeX:**
- Web-native output (not PDF-first)
- No compilation errors
- Collaboration built in (via Studio)
- Readable syntax

**vs Typst:**
- Web-native from the start (not PDF with HTML as afterthought)
- BRAIID quality as default output
- Reading ecosystem (clone, annotate, own)

**vs Quarto:**
- Static + permanent (no runtime, no dependency rot)
- Not executable-first (documents with interactive embeds)
- Semantic structure preserved

**vs Curvenote:**
- Documents, not components
- Semantic structure, not just provenance
- Simpler (not full CMS/platform)

**For detailed competitive analysis:** See [/cross/market/competitive/competitive-curvenote.md](/cross/market/competitive/competitive-curvenote.md) (Curvenote uses MyST, relevant for RSM comparison)

---

## Adoption Strategy

**Not converts from LaTeX.** Researchers don't switch tools for fun.

**RSM adoption follows venues:**
1. Press becomes a meaningful preprint server
2. Authors publish to Press using RSM (via Studio or other tools)
3. RSM adoption grows because Press matters

**Target users:**
- People writing for web-native venues
- People who want their paper to work on mobile
- People who care about accessibility
- People starting fresh (no legacy LaTeX investment)
- One discipline that champions this (network science? computational biology?)

---

## The Full Stack

RSM doesn't exist in isolation. It's part of the full Aris stack:

| Layer | Product | What it does |
|-------|---------|--------------|
| Format | RSM | Semantic markup language |
| Design | BRAIID | Design system for rendering |
| Authoring | Studio | Collaborative editor |
| Publishing | Press | Preprint server |
| Reading | Studio | Clone, annotate, own |

**The workflow:** Write RSM → render with BRAIID → publish on Press → readers clone to Studio → annotate, own, keep.

---

## What Makes RSM Defensible?

**See also:** `/products/studio/strategy/roadmap.md` section "Competitive Moats and Defensibility"

**What is NOT a moat:**
- Semantic markup alone (AI can infer structure)
- Semantic slicing/reuse (nice but not compelling)

**What IS a moat:**
1. **Web-native from the start** (Typst is PDF-first, HTML is afterthought)
2. **Static + interactive** (Quarto is executable-first, RSM is static with embeds)
3. **BRAIID quality as default** (Distill-level output with 1% of the effort)
4. **The reading ecosystem** (clone, annotate, own — see Studio strategy)
5. **Press as permanent registry** (permanent URLs, DOIs for HTML-native research)

**The full stack is the moat.** No single piece is defensible. The combination is.

---

## Interactivity Model

RSM provides an "interactive-shaped hole."

**You don't build interactives in RSM. You embed them:**
- Plotly charts (exported as self-contained HTML)
- Observable notebook cells
- D3 visualizations
- 3D model viewers
- YouTube videos
- Whatever runs in an iframe or is self-contained JS

RSM handles sizing, captions, fallbacks, responsive behavior. The interactive is a black box that gets embedded.

**Key insight:** A manuscript is not an app. It's a document with some interactive bits.

Most papers won't have custom interactives. That's fine. The baseline — beautiful typography, responsive layout, accessible, permanent — is already better than PDF.

---

## BRAIID Evolution Path

**Current state (2026):** BRAIID is the design system RSM uses.

**Future possibility:** BRAIID becomes a standard. Aris grants certification. Other tools can produce BRAIID-compliant output.

**But that's earned through traction, not declared today.**

For now: BRAIID is what you get when you write RSM and render with Aris tools.

---

## Success Metrics

**By 2027:**
- Press hosts 1,000+ RSM papers that look as good as Distill
- Researchers say "I can't go back to PDF"
- RSM tooling works with multiple editors (not just Studio)

**By 2030:**
- A discipline adopts RSM as their default format
- "Web-native manuscript" means BRAIID quality
- The tooling becomes invisible — so good it feels inevitable

---

## Key Messages

**For people who remember Distill:**
> "RSM is what Distill needed to survive."

**For people who don't:**
> "Beautiful web-native research documents. As easy to write as LaTeX. No web dev required."

**The value proposition:**
- "Write RSM. Get BRAIID."
- "RSM is what Distill needed to survive: same output quality, 1% of the effort"
- "A manuscript is not an app. It's a document with some interactive bits."

---

## Related Documentation

**Specifications:**
- [spec.md](../technical/spec.md) — RSM technical reference (language spec, architecture, BRAIID design system)

**Program-level positioning:**
- `/program/market/messaging.md` — RSM in context of full Aris Program

**Product strategies:**
- `/products/studio/strategy/roadmap.md` — RSM authoring and reading ecosystem
- `/products/press/strategy/roadmap.md` — RSM publishing and archival

**Competitive analysis:**
- [competitive/competitive-rsm-vs-myst.md](../market/competitive/competitive-rsm-vs-myst.md)

---

