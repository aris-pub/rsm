# BRAIID Tokens

**Abstract design token definitions**

Tokens are the foundational values that define BRAIID's visual language. This document describes the abstract scales and their intended use. For CSS implementation, see `braiid.css`.

---

## Spacing

### The Chunk

The foundational unit is **3rem** (48px at desktop, 42px at tablet, 36px at mobile), called a "chunk" in the design system. This value was chosen because:

- Large enough for comfortable touch targets on mobile (minimum 36×36px)
- Divides evenly into halves, thirds, sixths, twelfths
- Creates clear visual rhythm at document scale
- Scales proportionally with viewport via root font-size

Everything in BRAIID is a multiple or divisor of the chunk.

### Scale

| Token | rem | Mobile (12px) | Tablet (14px) | Desktop (16px) | Relation | Use |
|-------|-----|---------------|---------------|----------------|----------|-----|
| `chunk-twelfth` | 0.25rem | 3px | 3.5px | 4px | chunk ÷ 12 | Tight gaps |
| `chunk-sixth` | 0.5rem | 6px | 7px | 8px | chunk ÷ 6 | Small spacing |
| `chunk-quarter` | 0.75rem | 9px | 10.5px | 12px | chunk ÷ 4 | — |
| `chunk-third` | 1rem | 12px | 14px | 16px | chunk ÷ 3 | Zone width |
| `chunk-half` | 1.5rem | 18px | 21px | 24px | chunk ÷ 2 | Section gaps |
| `chunk` | 3rem | 36px | 42px | 48px | **base unit** | Handrail width |
| `chunk-2` | 6rem | 72px | 84px | 96px | chunk × 2 | Depth offset |
| `chunk-3` | 9rem | 108px | 126px | 144px | chunk × 3 | — |

### Handrail Spacing

The handrail left region is exactly one chunk, divided into three equal zones:

| Token | Value | Mobile | Tablet | Desktop | Purpose |
|-------|-------|--------|--------|---------|---------|
| `hr-zone-width` | `chunk-third` (1rem) | 12px | 14px | 16px | Width of each zone |
| `hr-left-total` | `chunk` (3rem) | 36px | 42px | 48px | Total left region |
| `hr-right-total` | `chunk` (3rem) | 36px | 42px | 48px | Info zone width |
| `hr-total-offset` | `chunk-2` (6rem) | 72px | 84px | 96px | Left + right combined |

Note: The menu zone and border zone overlap — they occupy the same `chunk-third` column, not two columns combined.

---

## Radius

Border radii follow the chunk scale and scale with viewport:

| Token | rem | Mobile | Tablet | Desktop | Relation | Use |
|-------|-----|--------|--------|---------|----------|-----|
| `radius-none` | 0 | 0 | 0 | 0 | — | Sharp corners |
| `radius-sm` | 0.125rem | 1.5px | 1.75px | 2px | chunk ÷ 24 | Halmos symbol |
| `radius-md` | 0.25rem | 3px | 3.5px | 4px | `chunk-twelfth` | Small elements |
| `radius-lg` | 0.5rem | 6px | 7px | 8px | `chunk-sixth` | Buttons, controls |
| `radius-xl` | 1rem | 12px | 14px | 16px | `chunk-third` | Cards, modals |
| `radius-full` | 50% | 50% | 50% | 50% | — | Circles |

The progression (0.125→0.25→0.5→1) doubles at each step, creating consistent visual relationships.

---

## Color

Colors are organized in three tiers.

### Why Seven Hues?

The palette includes seven hues, each with a distinct purpose:

| Hue | Role |
|-----|------|
| **Gray** | Neutral foundation — text, borders, surfaces |
| **Blue** | Primary brand, information status, links |
| **Purple** | Secondary brand, highlights |
| **Green** | Success status |
| **Red** | Error status |
| **Orange** | Warning status (reserved) |
| **Yellow** | Accent, stars, special indicators |
| **Pink** | Accent, quotes |

Blue and purple are brand colors. Green, red, and orange are semantic status colors. Yellow and pink are accent colors for specific UI elements. Gray is the workhorse.

### Tier 1: Primitives

Raw color values organized by hue. Each hue has a scale from 0 (lightest) to 1000 (darkest):

- **Gray**: 0, 50, 75, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950, 1000
- **Blue**: 50–950
- **Purple**: 50–950
- **Green**: 50–950
- **Red**: 50–950
- **Orange**: 50–950
- **Yellow**: 50–950
- **Pink**: 50–950

Primitives are not used directly in components. They feed into aliases.

### Tier 2: Aliases

Human-readable names with semantic weight:

**Neutrals:**
- `black`, `almost-black`, `extra-dark`, `dark`, `medium`, `light`, `extra-light`, `almost-white`, `white`

**Brand:**
- `--primary-50` through `--primary-950` (default: maps to blue, configurable via `:accent:` key)
- `--secondary-50` through `--secondary-950` (maps to purple)

**Status:**
- `information-*` (maps to blue)
- `success-*` (maps to green)
- `error-*` (maps to red)

### Tier 3: Semantic

Contextual meaning. These are what components use:

**Surfaces:**
- `surface-page` — document background
- `surface-primary` — card/block backgrounds
- `surface-hover` — hover state backgrounds
- `surface-information`, `surface-success`, `surface-error` — status backgrounds
- `surface-action` — button backgrounds
- `surface-hint` — highlighted areas

**Borders:**
- `border-primary` — default borders
- `border-information`, `border-success`, `border-error` — status borders
- `border-action` — focus/action borders
- `handrail-default`, `handrail-active` — handrail-specific

**Text:**
- `text-body` — main text
- `text-disabled` — disabled states
- `text-keyword` — RSM keywords
- `text-action` — interactive text
- `text-error` — error messages
- `text-hilite-bg` — highlight background

**Links:**
- `link-default`, `link-hover`

**Icons:**
- `icon-information`, `icon-error`, `icon-action`

### Accent Colors

The `--primary-*` scale can be changed via the `:accent:` config key to any of eight colors:

- `blue` (default)
- `purple`
- `red`
- `green`
- `orange`
- `yellow`
- `pink`
- `gray`

All accent colors meet WCAG 2.1 Level AA contrast requirements (4.5:1 minimum) against both light and dark backgrounds.

### Dark Mode

Dark mode inverts the primitive scales. Semantic tokens remain stable — `surface-page` is always "the page background," but its value changes from near-white to near-black.

---

## Typography

### Font Families

| Token | Default Value | Use |
|-------|---------------|-----|
| `--font-heading` | Montserrat, sans-serif | Headings (h1-h5) |
| `--font-body` | Source Sans 3, sans-serif | Body text, paragraphs |
| `--font-mono` | Source Code Pro, monospace | Code blocks |

**Typography modes via `:typography:` config key:**

- `sans-serif` (default) — Montserrat for headings, Source Sans 3 for body
- `serif` — Source Serif 4 for both headings and body

When `:typography: serif` is set, both `--font-heading` and `--font-body` are overridden to use Source Serif 4.

### Scale

The scale uses approximately 1.125 ratio (major second). This interval was chosen for:

- Subtle but perceptible hierarchy between levels
- Comfortable reading at all sizes
- Avoids dramatic jumps that waste vertical space

| Token | Size | Use |
|-------|------|-----|
| `text-h1` | 2.000rem (32px) | Document title |
| `text-h2` | 1.750rem (28px) | Section headings |
| `text-h3` | 1.500rem (24px) | Subsections |
| `text-h4` | 1.375rem (22px) | Subsubsections |
| `text-h5` | 1.250rem (20px) | — |
| `text-h6` | 1.000rem (16px) | Block labels (Theorem, Proof, Definition, etc.) |
| `text-body` | 1.000rem (16px) | Body text |
| `text-small` | 0.875rem (14px) | Captions, labels, equation numbers |

### Weights

| Token | Value | Use |
|-------|-------|-----|
| `weight-light` | 300 | — |
| `weight-regular` | 400 | Body text |
| `weight-medium` | 500 | H3, H4 |
| `weight-semi` | 600 | H2, labels, keywords |
| `weight-bold` | 700 | H1 |

### Line Heights

| Token | Value | Use |
|-------|-------|-----|
| `leading-tight` | 1.25 | Headings |
| `leading-normal` | 1.5 | Body text |

---

## Borders

| Token | Value | Use |
|-------|-------|-----|
| `border-extrathin` | 1px | Subtle dividers |
| `border-thin` | 2px | Default borders, handrail lines |
| `border-med` | 4px | Heading handrails |
| `border-thick` | 6px | — |

---

## Shadows

| Token | Value | Use |
|-------|-------|-----|
| `shadow-soft` | 0px 2px 6px rgba(0,0,0,15%) | Subtle elevation |
| `shadow-strong` | 0px 1px 2px rgba(0,0,0,30%) | Defined elevation |

---

## Units: rem vs em

### Principle: Use rem for layout, em for typography

BRAIID uses **rem** for almost all spacing, sizing, and layout to maintain consistent proportional scaling across the entire page. Use **em** sparingly, only when spacing should scale with an element's local font-size.

### Use `rem` (root em) for:

**✅ Layout spacing** - padding, margin, gap that should be consistent across the page
```css
.container {
  padding: var(--chunk);     /* 3rem - scales with root only */
  gap: var(--chunk-half);    /* 1.5rem - uniform spacing */
}
```

**✅ Component sizing** - predictable sizing that doesn't compound when nested
```css
.button {
  padding: 0.5rem 1rem;      /* Fixed size regardless of nesting */
  border-radius: var(--radius-lg);  /* 0.5rem */
}
```

**✅ All tokens** - chunk system, radius, handrail spacing
```css
--chunk: 3rem;
--radius-xl: 1rem;
--hr-zone-width: var(--chunk-third);
```

**✅ Borders and shadows**
```css
box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);
```

### Use `em` only for:

**⚠️ Typography-relative spacing** - margins/padding that should scale with text size
```css
p {
  margin-bottom: 1em;        /* Scales with paragraph font-size */
}

h1 {
  font-size: 2rem;           /* Fixed size */
  margin-bottom: 0.5em;      /* Scales with h1's font-size */
}
```

**⚠️ Line-height** (or better: unitless)
```css
body {
  line-height: 1.5;          /* Best: unitless (multiplier) */
}
```

**⚠️ Icon sizing relative to text**
```css
.icon {
  width: 1.2em;              /* Always 1.2× adjacent text */
  height: 1.2em;
}
```

**⚠️ Inline padding in small text elements**
```css
.badge {
  font-size: 0.875rem;       /* Fixed size */
  padding: 0.25em 0.5em;     /* Scales with badge text */
}
```

### Why rem is default

1. **Predictable** - 1rem is always 1× root font-size, regardless of nesting
2. **No compounding** - em compounds when nested (1.2em inside 1.2em = 1.44em)
3. **Consistent** - Layout spacing remains uniform across the page
4. **Responsive** - Changing root font-size scales everything proportionally

### Current em usage in BRAIID

These intentional em usages scale with typography:
- `--halmos--ellipsis-width: 1em` - scales with text
- `.hr {margin-block-end: 1em}` - paragraph spacing scales with text
- `padding-inline-start: 1.5em` - list indentation scales with text
- `.icon {width: 1.2em}` - icon sizing relative to text
- `padding-inline: 0.2em` - inline padding in small elements

All other spacing uses rem for consistency with the chunk system.

---

## Implementation Status

| Category | Defined | Implemented | Notes |
|----------|---------|-------------|-------|
| Colors | ✅ | ✅ | Full three-tier system |
| Typography | ✅ | ✅ | — |
| Spacing | ✅ | ✅ | Tokens in rem, ~118 hardcoded px remain |
| Radius | ✅ | ✅ | Tokens in rem |
| Borders | ✅ | ✅ | — |
| Shadows | ✅ | ✅ | — |
| Units | ✅ | ✅ | rem for layout, em for typography |

**In progress**: Converting remaining ~118 hardcoded px values to chunk tokens.
