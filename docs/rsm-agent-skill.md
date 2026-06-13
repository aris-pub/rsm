---
name: rsm-authoring
description: >
  Write correct RSM (Readable Science Markup) files. Covers the full RSM syntax:
  block/inline/construct tags, meta regions, proof structure, cross-references,
  math, code, tables, and bibliography. Use when working with .rsm files or
  authoring scientific manuscripts in RSM format.
---

# RSM — Readable Science Markup

RSM is a web-first markup language for scientific manuscripts. It uses colon-delimited tags
(`:tag:`) and Halmos closers (`::`) to express document structure, mathematical proofs,
cross-references, and metadata.

Every `.rsm` file is a valid RSM manuscript.


## Two Tag Types

RSM has two kinds of tags:

**Block tags** — structural containers (theorems, proofs, sections, lists, etc.)

```
:theorem: {
  :title: Main Result
  :label: thm-main
}

  Content paragraphs, nested blocks, inlines...

::
```

**Inline tags** — annotations within a paragraph (spans, refs, math, proof constructs)

```
:let: $x \in A$ ::
:claim:{:label: my-claim} some statement ::
:span:{:strong:, :emphas:} important text ::
:ref:label, display text::
```

Both open with `:tagname:` and close with `::` (the Halmos). Sections are the sole
exception — they close implicitly when a sibling or parent section begins, or at document
end.


## Document Structure

A manuscript starts with an optional title line using `#`, followed by optional top-level
meta, then body content:

```
# Manuscript Title {
  :label: my-manuscript
}

:config: {
  :theme: default
  :accent: blue
  :typography: sans-serif
  :numbering: section
  :override-date: 2025-01-15
}
::

:author: {
  :name: Jane Doe
  :email: jane@example.edu
  :affiliation: Some University
} ::

:abstract:
  Summary of the manuscript.
::

:toc:

## First Section
  Content...

### Subsection
  Content...

#### Subsubsection
  Content...
```

**Manuscript meta** goes in `{...}` right after the `#` title. It accepts keys like
`:label:` and `:title:`.

**`:config:`** is a block tag for document-wide settings: `:theme:`, `:accent:`,
`:typography:`, `:numbering:`, `:override-date:`, `:toc-depth:`, `:author-display-first:`,
`:author-display-last:`. It appears as a top-level block, closed with `::`.

**Section shortcuts:** `##`, `###`, `####` work like Markdown headings. They can also be
written as `:section:`, `:subsection:`, `:subsubsection:` with a `{:title: ...}` meta
key. Section-form tags do not need a Halmos — they close implicitly.

**Sections can carry meta** on the line after the heading:

```
## My Section {
  :label: sec-intro
  :icon: star
}
```

`:appendix:` is a stamp (no content, no Halmos) that marks where appendix sections begin.


## Complete Tag Reference

### Block Tags

| Tag | Description |
|-----|-------------|
| `:abstract:` | Manuscript abstract |
| `:algorithm:` | Algorithm listing (as-is content, not recursive) |
| `:author:` | Author information block |
| `:codeblock:` | Code listing (as-is content) |
| `:config:` | Document configuration |
| `:corollary:` | Corollary |
| `:definition:` | Definition |
| `:enumerate:` | Numbered list |
| `:example:` | Example |
| `:exercise:` | Exercise |
| `:figure:` | Figure float |
| `:html:` | HTML asset |
| `:itemize:` | Unnumbered list |
| `:lemma:` | Lemma |
| `:mathblock:` | Display math (as-is content) |
| `:p:` | Subproof (used inside steps) |
| `:porism:` | Porism (corollary of a proof) |
| `:problem:` | Problem |
| `:proof:` | Proof |
| `:proposition:` | Proposition |
| `:remark:` | Remark |
| `:sketch:` | Proof sketch |
| `:step:` | Proof step (inside proofs) |
| `:theorem:` | Theorem |
| `:toc:` | Table of contents (standard block; takes meta such as `:view:`, but no content) |
| `:video:` | Video asset |

All block tags open with `:tag:`, take optional `{meta}`, contain paragraphs/blocks, and
close with `::`.

### Inline Tags — General

| Tag | Description |
|-----|-------------|
| `:span:` | Text span — for styling via meta or attaching a `:label:` to specific text |
| `:note:` | Footnote |
| `:draft:` | Visible comment / draft note |

`:span:` is particularly useful for labeling a piece of text so it can be cross-referenced.
The reference targets only the span, not the enclosing paragraph:

```
Some :span:{:label: key-insight} remarkable observation:: that we revisit later.
...
As noted in :ref:key-insight::, ...
```

### Inline Tags — Special Syntax

| Tag | Shortcut | Description |
|-----|----------|-------------|
| `:math:` | `$...$` | Inline math (as-is content) |
| `:code:` | `` `...` `` | Inline code (as-is content) |
| `:ref:` | — | Internal cross-reference |
| `:cite:` | — | Bibliography citation |
| `:url:` | — | External hyperlink |
| `:previous:` | — | Reference a step by number |
| `:prev:` | — | Reference the previous step (stamp) |
| `:prev2:` | — | Reference step before last (stamp) |
| `:prev3:` | — | Reference two steps before (stamp) |

**Stamps** (`:prev:`, `:prev2:`, `:prev3:`) have no content and no Halmos — they stand alone.

**Emphasis shortcuts:** `**bold**` = `:span:{:strong:}bold::`, `*italic*` = `:span:{:emphas:}italic::`.

### Inline Tags — Proof Constructs

These appear inside theorem statements and proof steps:

| Tag | Description |
|-----|-------------|
| `:assume:` | Introduce an assumption |
| `:case:` | Prove a special case of the goal |
| `:claim:` (or `:⊢:` or `:\|-:`) | State a mathematical claim |
| `:define:` | Introduce a variable and assumption |
| `:let:` | Introduce a variable and assumption |
| `:new:` | Introduce a variable and assumption |
| `:pick:` | Introduce a variable with a property (pair with `:st:`) |
| `:prove:` | Set the goal |
| `:st:` | "Such that" — follows `:pick:` |
| `:suffices:` | Change the goal |
| `:suppose:` | Introduce an assumption |
| `:then:` | State a claim under an assumption |
| `:wlog:` | Without loss of generality |
| `:write:` | Introduce notation / a symbol |
| `:qed:` | State that the goal is proven (stamp — no Halmos) |

All constructs except `:qed:` open with `:tag:`, take optional `{meta}`, contain inline
content, and close with `::`.  `:qed:` is a stamp.


## Meta Regions

Meta appears in `{...}` immediately after a tag. Block meta uses newline-separated
key-value pairs; inline meta uses comma-separated pairs inside `{...}`.

**Block meta** (one pair per line):

```
:theorem: {
  :title: Main Result
  :label: thm-main
  :icon: star
}
```

**Inline meta** (comma-separated, on one line):

```
:span:{:strong:, :emphas:} text ::
:claim:{:label: my-claim} statement ::
:paragraph:{:icon: bookmark} Text here.
```

### Meta Keys by Type

**Text keys** (value is a string on the same line or rest of line):

| Key | Description |
|-----|-------------|
| `:affiliation:` | Author institutional affiliation |
| `:alt:` | Alt text for figure images |
| `:author-note:` | Author note (e.g. "Equal contribution") |
| `:email:` | Author email |
| `:goal:` | Theorem goal |
| `:icon:` | Icon assigned to the block |
| `:label:` | Cross-reference label |
| `:lang:` | Language code (e.g. `en`, `es`) |
| `:name:` | Author name |
| `:orcid:` | Author ORCID identifier |
| `:reftext:` | Label display text for references |
| `:title:` | Block or manuscript title |

**Boolean keys** (presence = true, no value needed):

| Key | Description |
|-----|-------------|
| `:emphas:` | Emphasized span |
| `:isclaim:` | Math block is a claim |
| `:nonum:` | Suppress numbering |
| `:strong:` | Bold span |

**List keys** (value in `{item1, item2, ...}` or a single item):

| Key | Description |
|-----|-------------|
| `:class:` | CSS classes |
| `:keywords:` | Abstract keywords |
| `:msc:` | Mathematics Subject Classification |

**Any-value keys** (parsed as-is):

| Key | Description |
|-----|-------------|
| `:accent:` | Accent color (blue, red, green, orange, yellow, purple, pink, gray) |
| `:author-display-first:` | Authors shown at start when >5 |
| `:author-display-last:` | Authors shown at end when >5 |
| `:dark:` | Dark-mode figure path |
| `:numbering:` | Numbering mode (document, section, none) |
| `:override-date:` | Override manuscript date |
| `:path:` | Figure path |
| `:scale:` | Figure scale |
| `:static:` | Static/PDF export figure path |
| `:theme:` | Manuscript theme |
| `:toc-depth:` | Table of contents depth |
| `:typography:` | Typography style (sans-serif, serif) |


## Proof Architecture

RSM's structured proof system is inspired by Leslie Lamport's "How to Write a 21st Century
Proof" and resembles the hierarchical proof style used in TLA+. Unlike TLA+ (which targets
formal verification), RSM proofs are written in natural language for human readers — the
structure provides navigability and rigor without requiring machine-checkable logic.

Proofs follow a rigid nesting: **proof → steps → substeps/subproofs**.

```
:proof:

  :step: {:label: step-1}
    Statement of what this step establishes.

    :p: Justification for this step. :: ::

  :step:
    :claim: Some intermediate result. ::

    :p:

      :step: Substep inside the justification. ::

      :step: Another substep. ::

    :: ::

  :step: :qed:

    :p: By :ref:step-1::. :: ::

::
```

**Key rules:**
- `:step:` can only appear directly inside `:proof:`, `:sketch:`, or inside a `:p:` (subproof)
- `:p:` provides the justification for its parent step — it can contain nested steps
- `:p:` closes with `:: ::` (its own Halmos, then the step's Halmos)
- Proof constructs (`:let:`, `:assume:`, `:prove:`, `:claim:`, `:pick:` / `:st:`, `:qed:`) appear inline within steps
- `:qed:` is a stamp — it has no content and no Halmos

### Proof vs Sketch

`:proof:` contains the full structured proof with steps. `:sketch:` is a lighter variant —
it has the same nesting rules but is intended for informal proof outlines. A common pattern
is to place a `:sketch:` before the `:proof:` to give the reader a high-level overview:

```
:theorem: {:label: thm-main}
  :claim: All $X$ are $Y$. ::
::

:sketch:
  The idea is to use induction on $n$, applying Lemma 2 at each step.
::

:proof:
  :step: ...
  ...
::
```

### Referencing Previous Steps

Inside a proof, you can reference earlier steps without explicit labels using stamps:

| Stamp | Meaning |
|-------|---------|
| `:prev:` | The immediately preceding step |
| `:prev2:` | The step before last |
| `:prev3:` | Two steps before the current one |

These are stamps — they stand alone with no content and no Halmos:

```
:step: {:label: stp-main}
  :claim: $a_n^{m+1} b_0 = 0$ ::

  :p: By :ref:first-substep::. :: ::

:step:
  :claim: $1 + u^{-1}x$ is a unit. ::

  :p: By :prev:. :: ::

:step:
  Multiplying :prev2: by $\lambda$ and subtracting :prev:.
::
```

For steps further back or across subproofs, use explicit `:label:` / `:ref:` pairs instead.
`:previous:` is the non-stamp variant that takes a step number: `:previous:3, Step 3::`.

### Common Proof Construct Patterns

```
% Introduce a variable
:let: $x \in A$ ::

% Introduce a variable with a property
:pick: $n \in \mathbb{N}$ :: :st: $x^n = 0$ ::

% Set the goal
:prove: that $1 + x$ is a unit ::

% State a claim
:claim: $f$ is nilpotent ::

% Alternative claim syntax
:⊢: $u^{-1} x$ is nilpotent.::

% Change the goal
:suffices: to show that $g$ is a unit ::

% Introduce an assumption
:assume: $f$ is a unit in $A[x]$ ::

% Introduce notation
:write: $A[x]$ for the ring of polynomials ::

% Mark goal as proven
:qed:
```

### Extended Proof Example

A multi-level proof showing nested subproofs and step references:

```
:proof:

  :step: {:label: x-is-nilp}

    :pick: $n \in \mathbb{N}$ :: :st: $x^n = 0$ ::.

    :p: Such an $n$ exists by definition of nilpotent. :: ::

  :step:

    We have
    $$ {:label: eqn-main}
    (1 + x)(1 - x + x^2 - \ldots + (-1)^n x^n) = 1.
    $$

    :p: Multiplying the left-hand side directly yields the middle expression.
    The term $(-1)^n x^{n+1}$ equals $0$, by :ref:x-is-nilp::. :: ::

  :step: :ref:goal-1, Goal 1:: is :qed:.

    :p: By :ref:eqn-main::. :: ::

  :step: {:label: sufficiency}

    To prove :ref:goal-2, Goal 2::, it :suffices: to :assume: $u \in A$ ::
    where $u$ is a unit ::, and :prove: that $u + x$ is a unit. :: ::

  :step: :⊢: $u^{-1} x$ is nilpotent.::

    :p: Immediately from $(u^{-1} x)^n = u^{-n} x^n = 0$. :: ::

  :step: :⊢: $1 + u^{-1} x$ is a unit.::

    :p: By :ref:goal-1, Goal 1::. :: ::

  :step: :⊢: $u + x$ is a unit.::

    :p: Because both $u$ and $1 + u^{-1} x$ are units, and the units are
    closed under multiplication. :: ::

  :step:

    :ref:goal-2, Goal 2:: is :qed:.

    :p: By :ref:sufficiency::. :: ::

::
```


## Cross-References

`:ref:` links to a `:label:` elsewhere in the document:

```
:ref:label::              % renders the auto-generated number
:ref:label, display text:: % renders "display text" as the link
```

`:cite:` references a bibliography entry:

```
:cite:atiyah2018::
:cite:key1 key2, see also::  % multiple keys, optional display text
```

`:url:` links to an external address:

```
:url:https://example.com::
:url:https://example.com, click here::
```

`:previous:` references a step by number:

```
:previous:3, Step 3::
```


## Shortcuts

| Shortcut | Equivalent |
|----------|------------|
| `$...$` | `:math:...::` |
| `$$...$$` | `:mathblock:...::` (display math) |
| `` `...` `` | `:code:...::` |
| ```` ```...``` ```` | `:codeblock:...::` |
| `**...**` | `:span:{:strong:}...::` |
| `*...*` | `:span:{:emphas:}...::` |
| `:-:` | List item (inside `:enumerate:` or `:itemize:`) |
| `:caption:` | Figure/table caption (paragraph-level) |
| `%` | Line comment |
| `\:` | Escaped colon (literal `:` in text) |


## Tables

```
:table: {:label: my-table}

  :thead:
    :tr: Header 1 : Header 2 : Header 3 ::
  ::

  :tbody:
    :tr: Cell 1 : Cell 2 : Cell 3 ::
    :tr:
      :td: Long cell content ::
      :td: More content ::
    ::
  ::

  :caption: A sample table.

::
```

Short rows use `:` as cell separator: `:tr: A : B : C ::`.
Long rows use explicit `:td:...::` for each cell.


## Bibliography

A `:references:` block at document end contains BibTeX-style entries. The syntax is
essentially a subset of BibTeX — `@type{label, key={value}, ...}` — so existing `.bib`
entries can often be pasted in with minimal adjustment:

```
:references:

@book{knuth1997,
  title={The Art of Computer Programming},
  author={Knuth, Donald E.},
  year={1997},
  publisher={Addison-Wesley},
}

@article{smith2020,
  title={On Something},
  author={Smith, J.},
  year={2020},
  journal={Journal of Things},
  volume={42},
  number={3},
  doi={https://doi.org/10.1234/example},
}

@software{numpy2024,
  title={NumPy},
  author={Harris, C.R., et al.},
  year={2024},
  url={https://numpy.org},
}

::
```

Supported entry types: `book`, `article`, `software`.
Supported fields: `title`, `author`, `year`, `publisher`, `journal`, `volume`, `number`, `doi`, `url`, `edition`.


## Common Mistakes

1. **Missing Halmos** — every block and inline tag (except sections, stamps, and items) must
   close with `::`. A missing `::` causes parse errors downstream.

2. **`:qed:` with Halmos** — `:qed:` is a stamp. Write `:qed:`, never `:qed:::`.

3. **`:step:` outside proof** — `:step:` is only valid inside `:proof:`, `:sketch:`, or `:p:`.

4. **Wrong meta separator** — block meta uses newlines between pairs; inline meta uses
   commas. Mixing them up causes parse failures.
   ```
   % WRONG — comma in block meta
   :theorem: {:title: Foo, :label: bar}

   % CORRECT — newlines in block meta
   :theorem: {
     :title: Foo
     :label: bar
   }

   % CORRECT — commas in inline meta
   :span:{:strong:, :emphas:} text ::
   ```

5. **Subproof closing** — `:p:` needs `:: ::` (its own Halmos then the parent step's).
   Forgetting the step's `::` is a frequent error.

6. **`:prev:` stamps don't take content** — write `:prev:`, not `:prev: something ::`.

7. **`:toc:` is a block with no content** — close it with `::` like any block. It accepts a
   meta region (e.g. `:view: tree` to default the table of contents to the dependency
   tree view), but content written inside it is discarded with a warning; the table of
   contents is generated automatically.

8. **Bare text outside paragraphs** — all text must live inside a paragraph context. Top-level
   text after a section heading is fine (implicit paragraph), but text floating outside any
   container is not.

9. **`:ref:` format** — the target comes right after the tag with no space before content:
   `:ref:label::` or `:ref:label, text::`. Do not write `:ref: label::` (space after tag).

10. **`:cite:` format** — same as ref: `:cite:key::`, not `:cite: key::`.


## Working Examples

### Example 1: Minimal Document

```rsm
# Hello World

## Introduction

This is a simple RSM manuscript with inline $2+2=4$ math and a display equation:
$$
E = mc^2.
$$

A **bold** and *italic* example.
```

### Example 2: Theorem and Proof

```rsm
# A Short Note

:author: {
  :name: Jane Doe
  :email: jane@example.edu
} ::

:abstract:
  We prove a basic fact about nilpotent elements.
::

## Main Result

:let: $A$ be a ring ::.

:theorem: {
  :title: Nilpotent Plus Unit
  :label: thm-main
}

  :let: $x \in A$ :: and :assume: $x$ is nilpotent ::.  :prove: that $1 + x$ is a
  unit of $A$. ::

::

:proof:

  :step: {:label: x-nilp}

    :pick: $n \in \mathbb{N}$ :: :st: $x^n = 0$ ::.

    :p: By definition of nilpotent. :: ::

  :step:

    We have
    $$ {:label: eqn-main}
    (1 + x)(1 - x + x^2 - \ldots + (-1)^n x^n) = 1.
    $$

    :p: Direct computation, using :ref:x-nilp::. :: ::

  :step: :qed:

    :p: By :ref:eqn-main::. :: ::

::
```

### Example 3: Lists, Figures, Tables, and Bibliography

```rsm
# A Survey

:author: {
  :name: Alice
  :email: alice@univ.edu
  :affiliation: State University
} ::

:abstract: {
  :keywords: {networks, algebra}
  :msc: {05C50, 15A18}
}
  A survey of recent results.
::

:toc:

## Background

Key properties of the operator:

:enumerate:

  :-: :claim: The operator is self-adjoint. ::

  :-: :claim: The spectrum is real. ::

::

:figure: {
  :path: img/spectrum.png
  :alt: Spectral plot
  :label: fig-spectrum
  :scale: 0.8
}

  :caption: The spectrum of the operator, see :ref:fig-spectrum::.

::

:html: {
  :path: interactive_chart.html
  :label: widget-chart
}

  :caption: Interactive visualization of the data.

::

:table: {:label: tbl-results}

  :thead:
    :tr: Method : Accuracy : Runtime ::
  ::

  :tbody:
    :tr: Baseline : 0.85 : 1.2s ::
    :tr: Ours : 0.93 : 0.8s ::
  ::

  :caption: Comparison of methods.

::

We follow :cite:knuth1997:: throughout.

:references:

@book{knuth1997,
  title={The Art of Computer Programming},
  author={Knuth, Donald E.},
  year={1997},
  publisher={Addison-Wesley},
}

::
```
