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
  :eyebrow: Preprint
}

:config: {
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

:toc: ::

## First Section
  Content...

### Subsection
  Content...

#### Subsubsection
  Content...
```

**Manuscript meta** goes in `{...}` right after the `#` title. It accepts keys like
`:label:` and `:title:`, and `:eyebrow:`: a short label set above the title, such as
`Preprint` or `Lecture notes`. `:plain-title:` sets the page's `<title>` (the browser
tab) as plain text, such as `:plain-title: Floor, ceiling, slopes, and K-theory`. It
must be the last key on its line, and a `$` or a tag in it is an error. Without it,
`<title>` holds the title's text with math as `$TeX$`.

**`:config:`** is a block tag for document-wide settings: `:accent:`,
`:typography:`, `:numbering:`, `:citation-style:`, `:override-date:`, `:toc-depth:`,
`:author-display-first:`, `:author-display-last:`, `:no-minimap:`. It appears as a top-level block, closed
with `::`.

**Section shortcuts:** `##`, `###`, `####` work like Markdown headings. They can also be
written as `:section:`, `:subsection:`, `:subsubsection:` with a `{:title: ...}` meta
key. Section-form tags do not need a Halmos — they close implicitly.

**A heading's title runs to the end of its line** and may hold inline markup: math
(`$...$`), `*italic*`, `**bold**`, code and `:span:`. Links (`:ref:`, `:url:`,
`:cite:`), note and aside calls and `:html:` are not allowed in a heading: RSM
leaves them out and logs an error. Where only plain text fits (the browser tab, the
sidebar's Contents list, the section graph), the title is shown without markup, with
math as its TeX source. A `:title:` meta value follows the same rules, as in
`:theorem: {:title: Bounds on $x$ :label: thm-x}`.

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
| `:calc:` | Calculation: a chain of relations, each a `:step:` with its reason (see Calculations) |
| `:codeblock:` | Code listing (as-is content) |
| `:config:` | Document configuration |
| `:corollary:` | Corollary |
| `:definition:` | Definition |
| `:enumerate:` | Numbered list |
| `:example:` | Example |
| `:exercise:` | Exercise |
| `:figure:` | Figure float |
| `:htmlblock:` | A block of raw HTML (as-is content, see below) |
| `:itemize:` | Unnumbered list |
| `:lemma:` | Lemma |
| `:mathblock:` | Display math (as-is content) |
| `:pf:` | Subproof (used inside steps) |
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

**Theorem-like blocks** are `:theorem:`, `:lemma:`, `:corollary:`, `:proposition:`,
`:definition:`, `:example:`, `:exercise:`, `:problem:`, `:porism:` and `:remark:`. They
accept `:title:` and `:blockname:`. `:blockname:` sets the name the block is called by,
in place of its type's name, written exactly as given:

```
:remark: {
  :blockname: Hint
  :label: hint-inversion
}

  Two circles are tangent at a point $T$. What does inversion at $T$ make of them?

::
```

In Section 1 the header reads "Hint 1.1." (or "Hint." with `:nonum:`), and
`:ref:hint-inversion::` reads "Hint 1.1". The block is still a remark: it is numbered with the other
theorem-like blocks and keeps the class `remark`.

`:figure:`, `:video:` and `:table:` also accept `:blockname:`. With `:blockname: Chart`,
a figure's caption label reads "Chart 1.1." and a `:ref:` to it reads "Chart 1.1", in
place of "Figure". It is still numbered with the figures. Other blocks ignore
`:blockname:`.

### Inline Tags — General

| Tag | Description |
|-----|-------------|
| `:span:` | Text span — for styling via meta or attaching a `:label:` to specific text |
| `:draft:` | Visible comment / draft note |

`:span:` is particularly useful for labeling a piece of text so it can be cross-referenced.
The reference targets only the span, not the enclosing paragraph:

```
Some :span:{:label: key-insight} remarkable observation:: that we revisit later.
...
As noted in :ref:key-insight::, ...
```

### Notes and Asides

`:note:` (a footnote) and `:aside:` each have two forms: a call and a definition.

| Form | Example | Where |
|------|---------|-------|
| Footnote call | `:note:my-note::` | Inline, where the number goes |
| Aside call | `:aside:my-aside,the words it is about::` | Inline, around the phrase the aside is about |
| Definition | `:note: {:label: my-note} contents ::` or `:aside: {:label: my-aside} contents ::` | A block of its own, anywhere in the document |

```
Some paragraph with a note at the end. :note:my-note::

:note: {:label: my-note} this is the note's contents ::

We look for a map into :aside:hilbert,some Euclidean space:: such that ...

:aside: {:label: hilbert} Bourgain writes Hilbert space instead. ::
```

- A footnote call takes only the label of its definition, like the target of `:ref:`.
  Text after the tag in a footnote call is a parse error.
- An aside call takes the label, a comma, and the phrase the aside is about, the same
  pattern as `:ref:label,text::`. The phrase may hold inline markup (`*emph*`,
  `**strong**`, `:span:`) and inline math, but not references or links. The phrase is
  shown in the text with a faint dotted underline, and it is what lights or opens the
  aside. An aside call without a phrase (`:aside:my-aside::`) is an error that asks
  for the phrase.
- A definition must have the `{:label: ...}` meta block. Without it, it is a parse error.
  Its content is one paragraph: inline content, display math (`$$...$$`) and code
  blocks. A blank line inside a definition is an error.
- The definition's tag decides whether the call is a footnote or an aside. A call to an
  aside must have a phrase and a call to a footnote must not.
- Footnotes are numbered 1, 2, 3 in the order their calls appear. Asides have no
  number.
- Footnotes are shown in one Notes list just before References (at the end of the
  document when there are no references), with their numbers and a link back to the
  call. Where a footnote definition is written does not change where it is shown.
- An aside is shown below the paragraph or list item that calls it. On wide screens
  it sits in the right-hand column level with its phrase. On narrow screens it is
  closed until the reader taps or clicks the phrase.
- Errors: a call with no definition, a definition called more than once, an aside call
  without a phrase, a footnote call with a phrase, and an aside (call or definition)
  inside a caption. A definition that is never called gives a warning and is not shown.
- The old form with the content inside the sentence (`:note: some text ::`) is gone.

### Inline Tags — Special Syntax

| Tag | Shortcut | Description |
|-----|----------|-------------|
| `:math:` | `$...$` | Inline math (as-is content) |
| `:code:` | `` `...` `` | Inline code (as-is content) |
| `:html:` | none | Inline raw HTML (as-is content, see below) |
| `:ref:` | — | Internal cross-reference |
| `:cite:` | — | Bibliography citation |
| `:url:` | — | External hyperlink |
| `:previous:` | — | Reference a step by number |
| `:prev:` | — | Reference the previous step (stamp) |
| `:prev2:` | — | Reference step before last (stamp) |
| `:prev3:` | — | Reference two steps before (stamp) |

**Stamps** (`:prev:`, `:prev2:`, `:prev3:`) have no content and no Halmos — they stand alone.

**Emphasis shortcuts:** `**bold**` = `:span:{:strong:}bold::`, `*italic*` = `:span:{:emphas:}italic::`.

### Raw HTML

`:html:` puts raw HTML inside a sentence, written into the HTML page exactly as
typed, with no escaping. It is built like the long form of `:code:`: the HTML runs up
to the first `::`, and `:alt:` in the optional meta block is the fallback.

```
Consider a chain of circles :html:{:alt: the circle $C_0$} <mtp-display model="pappus" name="c0"></mtp-display> ::, each tangent to the next.
```

- The HTML cannot contain `::`, cannot start with a colon, and cannot be empty.
- `:alt:` may hold text and inline math (`$...$`). It cannot hold a brace, as with any
  meta value.
- Where the HTML cannot be, the fallback stands in: output other than HTML (pandoc
  export), and the copies the page makes of its own content (reference previews, the
  pinned excerpt, the proof State view). Text read out of the document (a still
  image's alt text taken from a caption, the proof tree labels) uses the fallback too.
  Without `:alt:` nothing stands in, and RSM warns.
- Without JavaScript the page shows the HTML, as it does with JavaScript.
- Allowed wherever inline content is: paragraphs, spans, `**bold**`, `*italic*`,
  theorems, captions, list items and table cells. Not in a link's text (`:ref:` or
  `:url:` reftext, an aside's phrase): there the fallback is shown, with a warning.
  Not in a heading or a `:title:`: there it is left out, with an error.
- Write phrasing content (elements that may sit inside a `<p>`, such as `<span>`,
  `<svg>` or a custom element). A `<div>` or another block element ends the paragraph
  early in the browser.

`:htmlblock:` is the block form. Its body runs from the line after the tag to the
closing `::`, and is written into the page as is, with no paragraph or handrail
around it. It is not numbered. `:alt:` is its fallback, as for `:html:`.

```
:htmlblock: {:alt: A slider that sets $k$}
<input type="range" min="1" max="10" id="k-slider">
::
```

To number HTML and give it a caption, put it in a `:figure:`, either from a file
(`:path: chart.html`) or as an `:htmlblock:` inside the figure (see Figures).

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

Meta appears in `{...}` immediately after a tag. Block meta and inline meta are written
the same way. A value runs to the next key or to the closing `}`. Line breaks count as
spaces, so meta may be written on one line or on many, and a value may run over several
lines. A comma at the end of a pair, right before the next key or the closing `}`, is
dropped, so commas between pairs are optional. A comma anywhere else stays in the value.

```
:theorem: {:title: Main Result, :label: thm-main, :icon: star}

:theorem: {
  :title: Main Result
  :label: thm-main
  :icon: star
}

:theorem: {
  :title: A long title that runs
          onto a second line
  :label: thm-long
}

:span:{:strong:, :emphas:} text ::
:span:{:strong: :emphas:} text ::
:paragraph:{:title: Setup, part one :label: par-setup} Text here.
```

A value cannot hold a brace. It also cannot hold a word written like a key, a colon
after a space followed by letters and a colon (such as ` :label:`), because that word
starts the next pair. A colon anywhere else stays in the value, as in `Ratio 3:1`.

### Meta Keys by Type

**Text keys** (value is text):

| Key | Description |
|-----|-------------|
| `:affiliation:` | Author institutional affiliation |
| `:alt:` | Alt text for figure images; the fallback of `:html:` and `:htmlblock:` |
| `:author-note:` | Author note (e.g. "Equal contribution") |
| `:blockname:` | Name a theorem-like block, figure, video or table is called by, in place of its type's name |
| `:email:` | Author email |
| `:eyebrow:` | Short label above the manuscript title |
| `:goal:` | Theorem goal |
| `:icon:` | Icon assigned to the block |
| `:label:` | Cross-reference label |
| `:name:` | Author name |
| `:orcid:` | Author ORCID identifier |
| `:plain-title:` | Plain text for the browser tab, in place of the manuscript title |
| `:reftext:` | Label display text for references |
| `:title:` | Block or manuscript title; may hold inline markup, as a heading does |

**Boolean keys** (presence = true, no value needed):

| Key | Description |
|-----|-------------|
| `:as-paragraph:` | A figure or video sits at the level of a paragraph: no number, no caption |
| `:emphas:` | Emphasized span |
| `:isclaim:` | Math block is a claim |
| `:no-minimap:` | Turn the minimap off (in `:config:`) |
| `:nonum:` | Suppress numbering |
| `:strong:` | Bold span |

**List keys** (items separated by commas, such as `:keywords: graphs, cliques`):

| Key | Description |
|-----|-------------|
| `:class:` | CSS classes |
| `:keywords:` | Abstract keywords |
| `:msc:` | Mathematics Subject Classification |

A value of the wrong form, or a word that is not one of the allowed
values, is logged as an error with its line and the allowed values. The value is ignored,
the key keeps its default, and the build goes on.

**Path keys** (a file path, which may contain spaces):

| Key | Description |
|-----|-------------|
| `:dark:` | Dark-mode figure path |
| `:path:` | Figure path |
| `:static:` | Static/PDF export figure path |

**Number keys**:

| Key | Description |
|-----|-------------|
| `:author-display-first:` | Authors shown at start when >5 (whole number) |
| `:author-display-last:` | Authors shown at end when >5 (whole number) |
| `:scale:` | Figure scale (a number such as `0.5`) |
| `:toc-depth:` | Table of contents depth (whole number) |

**Word keys** (one word from a fixed list):

| Key | Description |
|-----|-------------|
| `:accent:` | Accent color (blue, red, green, orange, yellow, purple, pink, gray) |
| `:citation-style:` | Citation style (numeric, parens-author-year, author-parens-year) |
| `:lang:` | In `:config:`, a language code (e.g. `en`, `es`, `en-US`); in code, the code's language (e.g. `python`) |
| `:numbering:` | Numbering mode (document, section, none) |
| `:orientation:` | Table of contents tree orientation (horizontal, vertical) |
| `:typography:` | Typography style (sans-serif, serif) |
| `:view:` | Table of contents view (list, tree) |

**Date keys**:

| Key | Description |
|-----|-------------|
| `:override-date:` | Override manuscript date, written YYYY-MM-DD |


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

    :pf: Justification for this step. :: ::

  :step:
    :claim: Some intermediate result. ::

    :pf:

      :step: Substep inside the justification. ::

      :step: Another substep. ::

    :: ::

  :step: :qed:

    :pf: By :ref:step-1::. :: ::

::
```

**Key rules:**
- `:step:` can only appear directly inside `:proof:`, `:sketch:`, `:calc:`, or inside a `:pf:` (subproof)
- `:pf:` provides the justification for its parent step — it can contain nested steps
- `:pf:` closes with `:: ::` (its own Halmos, then the step's Halmos)
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

### Calculations

A `:calc:` is a chain of relations. Each row is a `:step:` that holds one relation in
`$...$`, followed by a `:pf:` with the reason it holds. It can go anywhere a display
equation (`$$...$$`) can go, inside or outside a proof.

Outside a proof:

```
:calc: {:label: eq-onepair}

  :step: $\|F(x)-F(y)\|^2 \ge c_0\sum_{j=1}^{k}a_j^2$

    :pf: By the bound for each scale. ::

  ::

  :step: $\ge \frac{c_0}{4L}\,d(x,y)^2$

    :pf: By Cauchy-Schwarz and $k \le L$. ::

  ::

::

By :ref:eq-onepair::, the map shrinks no distance by more than $2\sqrt{L/c_0}$.
```

Inside a proof, as the justification of a step:

```
:proof:

  :step: {:label: stp-bound}

    :claim: $(a+b)^2 \ge 4ab$. ::

    :pf:

      :calc:

        :step: $(a+b)^2 - 4ab = (a-b)^2$

          :pf: Expand and collect terms. ::

        ::

        :step: $\ge 0$

          :pf: A square is never negative. ::

        ::

      ::

    :: ::

::
```

**Rules:**
- A `:calc:` holds only `:step:` rows. Anything else is an error.
- A labelled `:calc:` takes the next equation number, from the same counter as `$$...$$`,
  and `:ref:` to it prints that number, e.g. (6.1). An unlabelled `:calc:` has no number.
- Only the whole chain is numbered. A row has no step number and cannot have a `:label:`.
- The relations render at display size. The reasons start folded: the reader opens one
  from the mark at the right of its row.
- Inside a proof the chain reads as one step: its rows are not steps of the proof.

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

  :pf: By :ref:first-substep::. :: ::

:step:
  :claim: $1 + u^{-1}x$ is a unit. ::

  :pf: By :prev:. :: ::

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

    :pf: Such an $n$ exists by definition of nilpotent. :: ::

  :step:

    We have
    $$ {:label: eqn-main}
    (1 + x)(1 - x + x^2 - \ldots + (-1)^n x^n) = 1.
    $$

    :pf: Multiplying the left-hand side directly yields the middle expression.
    The term $(-1)^n x^{n+1}$ equals $0$, by :ref:x-is-nilp::. :: ::

  :step: :ref:goal-1, Goal 1:: is :qed:.

    :pf: By :ref:eqn-main::. :: ::

  :step: {:label: sufficiency}

    To prove :ref:goal-2, Goal 2::, it :suffices: to :assume: $u \in A$ ::
    where $u$ is a unit ::, and :prove: that $u + x$ is a unit. :: ::

  :step: :⊢: $u^{-1} x$ is nilpotent.::

    :pf: Immediately from $(u^{-1} x)^n = u^{-n} x^n = 0$. :: ::

  :step: :⊢: $1 + u^{-1} x$ is a unit.::

    :pf: By :ref:goal-1, Goal 1::. :: ::

  :step: :⊢: $u + x$ is a unit.::

    :pf: Because both $u$ and $1 + u^{-1} x$ are units, and the units are
    closed under multiplication. :: ::

  :step:

    :ref:goal-2, Goal 2:: is :qed:.

    :pf: By :ref:sufficiency::. :: ::

::
```


## Cross-References

`:ref:` links to a `:label:` elsewhere in the document:

```
:ref:label::              % renders the auto-generated number
:ref:label, display text:: % renders "display text" as the link
```

`:cite:` references one or more bibliography entries, keys separated by commas. It has no
display text: every `:cite:` in a document renders the same way, set document-wide by
`:citation-style:` (numeric `[1]` by default, or author-year).

```
:cite:atiyah2018::
:cite:knuth,euler::  % multiple keys, comma-separated
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

A `:references:` block at the end of the document holds BibTeX entries, one after the
other, and closes with `::`. The key of an entry is the word after the opening brace, such
as `knuth1997` in `@book{knuth1997,`. Citations use this key.

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
  doi={10.1234/example},
}

@software{numpy2024,
  title={NumPy},
  author={Harris, C.R., et al.},
  year={2024},
  url={https://numpy.org},
}

::
```

RSM reads a subset of BibTeX. Entries outside this subset never stop the build. RSM keeps
each entry, and gives a warning that names the entry key and the field:

- The entry kinds are `@article`, `@book`, `@conference`, `@incollection`,
  `@inproceedings`, `@mastersthesis`, `@misc`, `@phdthesis`, `@software`, `@techreport`,
  `@unpublished` and `@webpage`. RSM reads them in capitals too, such as `@Article`. RSM
  reads any other kind, such as `@manual`, as `@misc` and gives a warning.
- The fields are `title`, `author`, `editor`, `year`, `month`, `journal`, `booktitle`,
  `series`, `volume`, `number`, `pages`, `edition`, `publisher`, `organization`,
  `institution`, `school`, `address`, `howpublished`, `note`, `doi` and `url`. RSM skips
  any other field, such as `keywords` or `abstract`, and gives a warning.
- Each value is written in braces. RSM skips a value in quotes, such as
  `title = "Sorting"`, or a value that is a bare word, such as `journal = jcp`, and gives
  a warning.
- RSM ignores braces inside a value and keeps the text inside them, so `{A {B} C}` reads
  "A B C", and gives a warning. RSM does not read LaTeX commands: `{Erd\H{o}s}` reads
  `Erd\Hos`. Write accented letters as they are, such as ö.
- RSM skips `@string` definitions and gives a warning that names each one.
- A `%` starts a comment everywhere in RSM, also inside a value. Write a percent sign in a
  value as `\%`, as in `title = {Sales up 50\% in a year}`. When a `%` cuts a value, RSM
  skips that field, reads the later fields, and gives a warning.

RSM warns about an entry without a `doi`, because the reader cannot follow it to the work.

An article renders as `Author. "Title". Journal Volume(Number) (Year).`. The issue
`number` prints in parentheses next to the volume, and any absent field is omitted. A
`pages` field is accepted but never rendered. A `doi` may be written bare (`10.1234/x`) or
as a resolver URL (`https://doi.org/10.1234/x`): either way it produces a single link.


## Common Mistakes

1. **Missing Halmos** — every block and inline tag (except sections, stamps, and items) must
   close with `::`. A missing `::` causes parse errors downstream.

2. **`:qed:` with Halmos** — `:qed:` is a stamp. Write `:qed:`, never `:qed:::`.

3. **`:step:` outside proof** — `:step:` is only valid inside `:proof:`, `:sketch:`, `:calc:`, or `:pf:`.

4. **Subproof closing** — `:pf:` needs `:: ::` (its own Halmos then the parent step's).
   Forgetting the step's `::` is a frequent error.

5. **`:prev:` stamps don't take content** — write `:prev:`, not `:prev: something ::`.

6. **`:toc:` is a block with no content** — close it with `::` like any block. It accepts a
   meta region (e.g. `:view: tree` to default the table of contents to the dependency
   tree view), but content written inside it is discarded with a warning; the table of
   contents is generated automatically.

7. **Bare text outside paragraphs** — all text must live inside a paragraph context. Top-level
   text after a section heading is fine (implicit paragraph), but text floating outside any
   container is not.

8. **`:ref:` format** — the target comes right after the tag with no space before content:
   `:ref:label::` or `:ref:label, text::`. Do not write `:ref: label::` (space after tag).

9. **`:cite:` format** — same as ref: `:cite:key::`, not `:cite: key::`.


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

    :pf: By definition of nilpotent. :: ::

  :step:

    We have
    $$ {:label: eqn-main}
    (1 + x)(1 - x + x^2 - \ldots + (-1)^n x^n) = 1.
    $$

    :pf: Direct computation, using :ref:x-nilp::. :: ::

  :step: :qed:

    :pf: By :ref:eqn-main::. :: ::

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
  :keywords: networks, algebra
  :msc: 05C50, 15A18
}
  A survey of recent results.
::

:toc: ::

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

:figure: {
  :path: interactive_chart.html
  :label: fig-chart
  :static: interactive_chart.png
}

  :caption: Interactive visualization of the data.

::

:figure: {:label: fig-canvas :alt: A canvas that draws the orbit.}

  :htmlblock:
  <canvas id="orbit"></canvas>
  ::

  :caption: The orbit, drawn live.

::

**Figures that hold HTML.** A `:figure:` holds HTML from a file named by `:path:` (an HTML fragment, for example a `fig.html` that contains `<svg>...</svg>`), or from an `:htmlblock:` inside it. The markup is written into the page, so it picks up the page CSS variables (dark mode, accent color). A raw image file (`.png`, `.jpg`, `.svg`) is embedded as an `<img>` and cannot see those variables. A copy of the page's own content (a reference preview, for example) shows the figure's `:static:` image, or else its `:alt:`, in place of the live HTML, and so does output other than HTML (pandoc export). Without either, pandoc export writes a note to see the online version.

**Notation in figures that hold HTML.** Readers can rename the symbols declared in a `:notation:` block (for example, change `\emb` from `F` to `\varphi`). Math in the page is typeset again with the new symbol, but a figure that draws a symbol itself (in SVG `<text>`, or on a canvas) must update the label in its own script. `window.rsm.notation.get("\\emb")` returns the current LaTeX of a macro (`"F"`, or `"\\varphi"` after the rename). After every rename, and after a reset to the author's default, RSM dispatches the event `rsm:notation-change` on `document`. Its `detail` has `macro` (the macro name, `"\\emb"`), `latex` (its new value) and `macros` (a copy of the current values of all macros). On load, the event is also dispatched once for each macro whose current value differs from its default: one that the reader renamed on an earlier visit, or one renamed by a shared view link (`?view=`). To typeset a symbol, rather than write its LaTeX as text, pass it to `window.rsm.renderMath(latex, el, {display})`, which renders into the element `el` with the document's current notation. A rename does not update math that was rendered this way, so the figure's script renders it again when the event arrives. `window.rsm` can be missing while the figure's own script first runs, so the script calls it from a `load` listener on `window`.

```html
<svg viewBox="0 0 100 40"><foreignObject x="0" y="0" width="100" height="40">
  <span id="emb-label"></span>
</foreignObject></svg>
<script>
  const label = document.getElementById("emb-label");
  const draw = () => window.rsm.renderMath("\\emb(x)", label);
  window.addEventListener("load", draw);
  document.addEventListener("rsm:notation-change", (ev) => {
    if (ev.detail.macro === "\\emb") draw();
  });
</script>
```

**Figures as paragraphs.** With `:as-paragraph:`, a `:figure:` or `:video:` sits at the level of a paragraph instead of being a block. Use it for a picture that belongs to the text around it, for example inside a theorem-like block:

```rsm
:remark: {
  :blockname: Hint
}

  Under inversion at $T$, the chain becomes a stack of congruent circles.

  :figure: {
    :as-paragraph:
    :path: figs/pappus-images.png
    :alt: The chain and its image, a stack of congruent circles.
    :scale: 0.2
  }
  ::

::
```

It takes no number, and the next figure is numbered as if it were not there. A `:caption:` given to it is ignored, with a warning. It has a handrail like a paragraph's, labeled with its kind ("Figure", "Video", or its `:blockname:`), and is never wider than the text column. Every other key still works (`:path:`, `:dark:`, `:static:`, `:alt:`, `:scale:`, `:label:`...). A `:ref:` to it reads its kind with no number, as for any unnumbered block. It is allowed anywhere a paragraph is.

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
