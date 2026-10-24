# Theming

**Dark mode, custom themes, token overrides**

---

## How it works

Every color is a single CSS custom property defined once with both values, using
`light-dark()`:

```css
:root {
  color-scheme: light dark;
  --gray-0: light-dark(#FFFFFF, #13181B);
  --surface-page: light-dark(var(--white), var(--gray-0));
}
```

The browser picks which half resolves from the element's `color-scheme`. On
`:root` that is `light dark`, so by default the page follows the operating
system setting with no JavaScript.

An explicit reader choice forces one side by setting `color-scheme` through a
class on the root element:

```css
.dark-theme  { color-scheme: dark; }
.light-theme { color-scheme: light; }
```

So there are three states:

| State | Root class | Resolves to |
|-------|-----------|-------------|
| Follow the OS (default) | none | OS setting, via `color-scheme: light dark` |
| Force dark | `.dark-theme` | dark |
| Force light | `.light-theme` | light |

The reading controls (the sidebar's Reading tab) add or clear these classes and
persist the choice in the `rsm-reading` localStorage object. A boot script in
the page head re-applies the stored choice before first paint. With no stored
choice no class is set, so the page follows the OS. None of this is needed to
get the right colors: with scripting off the CSS alone follows the OS.

`color-scheme` drives colors only. For the few things that switch on `display`
rather than color (the `.dark-only` / `.light-only` asset variants, the static
fallback images), the OS path needs an explicit `@media (prefers-color-scheme:
dark)` twin of the `.dark-theme` rule, guarded by `:root:not(.light-theme)` so
an explicit light choice still wins.

---

## Token cascade

```
Primitives (--gray-500, --blue-700)   <- light-dark() pairs
    down
Aliases (--dark, --primary-600)
    down
Semantic (--text-body, --surface-page)
    down
Components use semantic tokens
```

Primitives carry the light and dark values. Most semantic tokens just reference
a primitive and resolve correctly in both themes without their own pair. A
semantic token needs its own `light-dark()` only when it points at a different
primitive per theme (for example `--surface-page` is `var(--white)` in light but
`var(--gray-0)` in dark).

`tests/test_theme_tokens.py` guards every token's light and dark value against a
recorded baseline, and fails if a `.dark-theme` block ever redefines a token
again (the old duplicated model).

---

## Open questions

### Custom themes

What is the theming API for third parties?

Options:
1. **Override semantic tokens only** - safest, limits customization
2. **Override any token** - more flexible, easier to break
3. **Provide theme presets** - curated alternative palettes

### Contrast verification

**Complete.** All color combinations meet WCAG 2.1 Level AA.

Comprehensive accessibility testing validates:
- 8 accent colors x 2 themes x 2 states = 32 combinations
- All meet the 4.5:1 minimum contrast ratio for normal text
- Automated tests in `tests/accessibility/test_wcag.py` using axe-core

### Accent colors

Eight accent colors are available via the `:accent:` config key:

- `blue` (default)
- `purple`
- `red`
- `green`
- `orange`
- `yellow`
- `pink`
- `gray`

All accent colors use the custom property system with `--primary-*` tokens that
cascade through semantic tokens for links, handrails, and interactive elements.

### Typography

Two typography modes via the `:typography:` config key:

- `sans-serif` (default): Montserrat for headings, Source Sans 3 for body
- `serif`: Source Serif 4 for both headings and body

Implemented using the `--font-heading` and `--font-body` custom properties.

---

## To define

- [ ] Document the theming API for third-party theme creators
- [ ] Consider high contrast mode support
