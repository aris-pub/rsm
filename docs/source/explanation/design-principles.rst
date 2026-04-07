.. _design-principles:

Design Principles
=================

These principles guide every decision in RSM's design.

- `The primary output is a web page <#web-first>`_
- `Capture what something means, not how it looks <#semantic-markup>`_
- `One language, purpose-built <#a-custom-grammar>`_
- `Beautiful output by default <#the-braiid-design-system>`_
- `If the JavaScript fails, the science must survive <#progressive-enhancement>`_
- `A manuscript is not an app <#static-documents-not-executable-notebooks>`_
- `Smart defaults over configuration <#humane-design>`_


.. _web-first:

Web-first
---------

**The primary output is a web page. PDF is a compatibility export.**

PDF is a frozen page image designed for print. It has fixed geometry, fixed
layout, and fixed typography. On a phone, a tablet, or with a screen reader,
PDFs break.

RSM targets HTML as the primary output. HTML is maintained by global standards
bodies, supported by every browser, and has proven backward-compatible across
decades. A well-structured HTML document from 2005 still renders correctly
today.

PDF export exists (via Pandoc/Typst) for fields that require it. But the
primary artifact is a web page.


.. _semantic-markup:

Semantic markup
---------------

**Capture what something means, not how it looks.**

Tags like ``:theorem:``, ``:cite:``, and ``:ref:`` describe what something
*is*, and the toolchain decides how to present it: numbering, tooltips,
cross-reference links, and navigation are all generated from the semantic
structure.

This matters because:

- **Accessibility**: screen readers can announce "Theorem 1" instead of
  guessing from visual styling.
- **Tooltips and navigation**: the toolchain generates interactive features
  automatically from the semantic tree.
- **Durability**: structure survives redesigns. Appearance changes; meaning
  doesn't.
- **Machine readability**: AI retrieval systems and search engines can parse
  the document's logical structure.


A custom grammar
-----------------

**One language, purpose-built for scientific writing.**

RSM is not an extension of Markdown, ReStructuredText, or LaTeX.

**Why not extend Markdown?**
Markdown's strength is minimal syntax. Adding research primitives (citations,
theorems, cross-references with tooltips, structured proofs) would require so
many extensions that the result would no longer feel like Markdown.

**Why not extend ReST?**
RSM started as a Sphinx extension. It became unsustainable: testing was
painful, the extension API couldn't support RSM's core features, and
development slowed to a crawl.


The BRAIID design system
-------------------------

**Beautiful output by default, not by configuration.**

RSM manuscripts are styled by BRAIID (Beautiful, Responsive, Accessible,
Interactive, Inviting, Durable). BRAIID is not optional: it is the default
output of ``rsm build``.

BRAIID exists because research manuscripts have specific design needs that
generic CSS frameworks don't address:

- **Typography for math and prose**: carefully tuned font scales, weights, and
  line heights for mixed mathematical and natural-language content.
- **Handrails**: a navigation system that makes the document's semantic
  structure visible and interactive without cluttering the reading experience.
- **Responsive without breakpoints**: a proportional scaling system based on a
  single "chunk" unit (3rem) that adapts to any viewport by changing the root
  font size.
- **Dark mode**: semantic color tokens that invert cleanly, with all accent
  colors meeting WCAG 2.1 AA contrast requirements in both themes.

BRAIID enforces a strict structural and behavioral floor: semantic HTML,
sufficient contrast, keyboard navigation, and offline readability.


Progressive enhancement
-----------------------

**If the JavaScript fails, the science must survive.**

RSM treats JavaScript as a layer that enhances a complete, readable document,
not a prerequisite for reading it.

What works without JavaScript:

- All text, headings, figures, tables, math, citations, bibliography, code
  blocks

What degrades gracefully:

- Handrail controls (collapse, menus)
- Tooltips on cross-references
- Dark mode toggle
- Collapsible proof sections

This ensures that RSM documents remain readable when archived, printed, or
viewed in restricted environments.


Static documents, not executable notebooks
------------------------------------------

**A manuscript describes research. The code lives elsewhere.**

RSM is not Jupyter. A manuscript and its code are separate artifacts.

RSM provides an "interactive-shaped hole": you embed pre-generated
visualizations (Bokeh, Plotly, D3) as self-contained HTML widgets. RSM
handles sizing, captions, accessibility metadata, and responsive behavior.
The widget is a black box.

This avoids runtime rot (broken dependencies after six months), complex
hosting requirements, and the "install these 47 packages" problem. An RSM
manuscript is static files served from anywhere.


Humane design
-------------

**Smart defaults over configuration. No accounts, no telemetry, no lock-in.**

RSM is designed to feel like a precision instrument, not a productivity app.

- **Progressive disclosure**: chrome appears when needed, disappears when not.
  Handrails are invisible until you hover.
- **Smart defaults**: ``rsm build`` produces a complete, styled manuscript
  with no configuration. Accent colors, typography, numbering, and dark mode
  just work.
- **Respect for time**: RSM is a CLI tool that reads text files and writes
  HTML. Nothing else.
