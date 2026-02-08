# Handrails

**Pattern specification for RSM document navigation**

---

## Concept

RSM documents are semantic block structures. Unlike traditional documents (continuous prose) or notebooks (executable cells), RSM produces a **navigable semantic document** — rendered content where structure is visible and each block is addressable.

The **handrail** is the UI system that makes this possible. Every semantic block — section, paragraph, theorem, proof, equation — has a handrail that:

1. **Reveals structure** — Visual indication of block boundaries and nesting
2. **Enables interaction** — Collapse, copy link, view source, block-level actions
3. **Provides navigation** — Click-to-focus, keyboard navigation between blocks

Handrails follow **progressive disclosure**: invisible by default, appearing on hover or focus. Structure cues without visual clutter.

---

## Three-Region Model

Conceptually, each block has three regions:

```
┌──────────────┬─────────────────────────────────┬──────────────┐
│    LEFT      │            CENTER               │    RIGHT     │
│              │                                 │              │
│  Interaction │           Content               │   Metadata   │
│  affordances │                                 │   & status   │
│              │                                 │              │
│  - Collapse  │  The actual block content:      │  - Equation  │
│  - Menu      │  paragraph text, theorem        │    numbers   │
│  - Border    │  statement, proof steps, etc.   │  - Bookmarks │
│              │                                 │  - Comments  │
└──────────────┴─────────────────────────────────┴──────────────┘
```

**Critical constraint:** The CENTER region must be visually centered in the viewport. This means the LEFT region must be offset outside the content column, not pushing content rightward.

---

## Zone Architecture

The three regions are implemented as zones in the HTML/CSS:

```
LEFT REGION (1 chunk)              CENTER                RIGHT (1 chunk)
┌─────────┬────────────┬─────────┐┌──────────────────────┐┌─────────────┐
│ COLLAPSE│MENU/BORDER │ SPACER  ││       CONTENT        ││    INFO     │
│         │ (overlap)  │         ││                      ││             │
│  1 zone │   1 zone   │ 1 zone  ││ viewport - chunk-2   ││   1 chunk   │
│         │            │         ││                      ││             │
└─────────┴────────────┴─────────┘└──────────────────────┘└─────────────┘
          ↑
          Menu and border occupy the same column
```

**Key dimensions (using spacing tokens):**

- Each left zone: `chunk-third`
- Total left region: `chunk` = 3 × `chunk-third`
- Right region: `chunk`
- Content width: viewport width minus `chunk-2`

### Zone Responsibilities

| Zone | Width | Purpose |
|------|-------|---------|
| **Collapse** | `chunk-third` | Expand/collapse toggle button |
| **Menu/Border** | `chunk-third` | Context menu trigger AND vertical border line (overlapping) |
| **Spacer** | `chunk-third` | Gap between border and content |
| **Content** | remaining | The actual block content |
| **Info** | `chunk` | Equation numbers, step numbers, bookmark/comment icons |

### HTML Structure

The RSM compiler produces this structure for each block:

```html
<div class="hr hr-offset paragraph">
  <div class="hr-collapse-zone">...</div>
  <div class="hr-menu-zone">...</div>      <!-- overlaps with border-zone -->
  <div class="hr-border-zone">
    <div class="hr-border-dots">...</div>
    <div class="hr-border-rect"></div>     <!-- vertical line -->
  </div>
  <div class="hr-spacer-zone">...</div>
  <div class="hr-content-zone">
    <!-- actual content here -->
  </div>
  <div class="hr-info-zone">...</div>
</div>
```

The `.hr-offset` class triggers absolute positioning of the left zones, pulling them outside the content flow. Menu zone and border zone share the same position — one shows the context menu trigger, the other shows the vertical line.

---

## Positioning

### The Centering Problem

If left zones were in normal flow, content would be pushed right:

```
BAD: Content not centered
├─ LEFT ─┼──────── CONTENT ────────┼ RIGHT ┤
         ↑
         Not centered in viewport
```

The solution is absolute positioning:

```
GOOD: Content centered
         ├──────── CONTENT ────────┤
├─ LEFT ─┤                         ├ RIGHT ┤
    ↑                                  ↑
    Absolute, negative left        Absolute, left: 100%
```

Left zones are positioned with negative offsets (`-chunk-third`, `-chunk-third × 2`, `-chunk`). The info zone is positioned at `left: 100%`. Content remains in normal flow, centered.

---

## Nesting Behaviors

Blocks can be nested (theorem inside section, paragraph inside theorem). There are two nesting behaviors:

### Stacking (Default)

Nested blocks share the same visual column. Their handrails align vertically, occupying the same position. Content alignment is preserved.

Key behavior: A section's handrail covers **only the heading**, not the section content. Blocks inside the section have their own handrails that align with where the section's handrail would be — they stack, not shift.

```
│ 2. Methods                    ← Section heading (handrail visible)
│
  ┌─ Theorem 2.1 ────────────   ← Theorem handrail (always visible)
  │
  │  Let X be a topological     ← Content inside theorem
  │  space satisfying...
  │
  └──────────────────────────

  Paragraph of regular text.    ← Paragraph handrail (on hover)
  More explanation here...         aligns with theorem handrail above

  ┌─ Theorem 2.2 ────────────   ← Another theorem, same alignment
  │  ...
```

The theorem handrail and paragraph handrail (when revealed on hover) occupy the same vertical column. They stack on top of each other conceptually — the visual border appears in the same position for all blocks at the same level.

### Shifting (Proofs)

Proof steps indent progressively. Each nesting level shifts right, creating visual hierarchy.

```
┌─ Proof ────────────────────────────────────────
│
├─ Step 1 ───────────────────────────────────────
│  │
│  └─ Substep 1.1 ───────────────────────────────
│     │
│     └─ Substep 1.1.1 ──────────────────────────
│        │
│        └─ Content at depth 3
│
├─ Step 2 ───────────────────────────────────────
│  │
│  └─ Step 2 content
```

Each depth level reduces content width by one chunk:

| Depth | Content Width |
|-------|---------------|
| 0 | viewport - `chunk-2` |
| 1 | viewport - `chunk-2` - `chunk` |
| 2 | viewport - `chunk-2` - `chunk` × 2 |
| 3 | viewport - `chunk-2` - `chunk` × 3 |

The formula: `100% - chunk-2 - (chunk × depth)`

### How the CSS Knows

Class-based detection:

- `.proof`, `.step`, `.subproof` → shifting behavior
- Everything else → stacking behavior

---

## Extent Modes

The vertical line in the border zone can span different amounts of the block:

### Full Extent

The handrail spans the entire block height. Used for most content blocks: paragraphs, theorems, proofs.

```
┌─ Theorem 2.1 ──────────────
│
│  Let X be a topological
│  space satisfying...
│
│  This is the full statement
│  and the border extends all
│  the way down.
│
└────────────────────────────
```

### Heading Only

The handrail only spans the heading, not the full section content. Used for sections.

```
│ 2. Methods                    ← Handrail covers only this line
│

  This section content is NOT
  wrapped by the section's
  handrail. The border stops
  at the heading.

  Content continues without
  the section's border...
```

### Implementation

This is controlled by the RSM compiler, not CSS. The compiler decides what content gets wrapped inside the handrail's content zone:

- **Theorems, proofs**: Full content wrapped inside handrail
- **Sections**: Only the heading wrapped; body content is outside

---

## States

### Visibility Defaults

Not all handrails behave the same:

| Block Type | Default Visibility |
|------------|-------------------|
| Paragraphs | Hidden (appears on hover) |
| Theorems, Definitions, etc. | **Always visible** |
| Proofs | **Always visible** |
| Section headings | **Always visible** |

Blocks that carry semantic weight (named environments, structural elements) have visible handrails by default. Regular paragraphs reveal their handrails only on interaction.

### Default (Not Hovered, Hidden Handrail)

- Collapse zone: hidden (opacity 0)
- Border dots: hidden (opacity 0)
- Border line: hidden (opacity 0)
- Menu zone: hidden

### Default (Always-Visible Handrail)

- Collapse zone: hidden (opacity 0)
- Border dots: hidden (opacity 0)
- Border line: **visible**, default color (`handrail-default`)
- Menu zone: hidden

### Hovered

- Collapse zone: visible (opacity 100)
- Border dots: visible (opacity 100)
- Border line: visible, default color

### Focused / Active

- Border dots: primary color background
- Border line: active color (`handrail-active`)
- Content zone: information background (`surface-information`)
- All child handrails also highlighted

### Collapsed

- Content zone children: hidden
- Border line: bottom border added (indicates continuation)
- Collapse icon: expand state
- Optional "steps hidden" text for proof steps

### Mobile

**Undefined.** Hover interactions don't exist on touch devices. Options under consideration:

- Tap to reveal handrail controls
- Long-press for context menu
- Swipe gestures
- Bottom sheet UI

See [RESPONSIVENESS.md](RESPONSIVENESS.md) for open questions.

---

## Interactions

| Action | Result |
|--------|--------|
| Hover block | Handrail controls appear |
| Click border dots | Opens context menu |
| Click collapse toggle | Expand/collapse block content |
| Focus block | Handrail highlighted, keyboard navigation enabled |
| Tab | Move to next focusable block |
| Shift+Tab | Move to previous focusable block |

### Context Menu Actions

- Copy link to block
- View RSM source
- (Future: bookmark, comment, share)

---

## Halmos

Proofs display a Halmos (QED symbol) — a small filled square — on hover/focus. It appears at the bottom-right of the proof block.

Dimensions: `chunk-sixth` × `chunk-sixth`, with `radius-sm` corner rounding.

---

## Known Issues

### Depth Limit

Current CSS only handles depths 0–3. Depth 4+ will not shift correctly. The RSM compiler should enforce this limit, or the CSS needs to be extended.

### Magic Numbers

Zone widths and offsets are hardcoded pixels in the CSS, not tokens. See [TOKENS.md](TOKENS.md) for the spacing scale that should replace these.

### Selector Fragility

Depth selectors like `.hr .hr .hr .hr` break if any wrapper element is inserted. Consider using `data-depth` attributes instead.

### No Visual Tests

Changes to handrail CSS cannot be verified automatically. Visual regression tests are needed before any refactoring.

### Mobile Undefined

No touch interaction pattern defined. See States section above.

---

## Future Improvements

1. **Tokenize spacing** — Replace px with spacing tokens
2. **Data-driven depth** — Use `data-depth` attributes instead of nested selectors
3. **Simplify zones** — Collapse zone and menu zone could potentially merge
4. **Responsive behavior** — Handrails on mobile (currently undefined)
5. **Print behavior** — Handrails should be hidden in print
