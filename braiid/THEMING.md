# Theming

**Dark mode, custom themes, token overrides**

---

## Status: Stub

Current implementation works but has ARCH compliance gaps.

---

## ARCH Requirements

Per ARCH 3.2:

- MUST define CSS custom properties for: foreground, background, accent, font family
- MUST support dark mode via `prefers-color-scheme: dark`
- SHOULD provide manual theme toggle

---

## Current State

| Requirement | Status |
|-------------|--------|
| CSS custom properties | ✅ Full token system |
| `prefers-color-scheme` | ❌ Missing — only class toggle |
| Manual toggle | ✅ `.rsm-theme-toggle` button |

### How It Works Now

Dark mode is triggered by adding `.dark-theme` class to the document. This requires JavaScript.

```javascript
document.documentElement.classList.add('dark-theme');
```

The `.dark-theme` class redefines primitive color tokens. Semantic tokens cascade automatically.

---

## Token Cascade

```
Primitives (gray-500, blue-700)
    ↓
Aliases (--dark, --primary-600)
    ↓
Semantic (--text-body, --surface-page)
    ↓
Components use semantic tokens
```

Dark mode inverts primitives. Aliases and semantic tokens stay the same names but resolve to inverted values.

---

## Open Questions

### System Preference Detection

Need to add:

```css
@media (prefers-color-scheme: dark) {
  :root {
    /* dark primitive overrides */
  }
}
```

But how does this interact with the manual toggle? If user manually selects light mode, system preference shouldn't override.

### Custom Themes

What's the theming API for third parties?

Options:
1. **Override semantic tokens only** — safest, limits customization
2. **Override any token** — more flexible, easier to break
3. **Provide theme presets** — curated alternative palettes

### Contrast Verification

✅ **Complete** — All color combinations meet WCAG 2.1 Level AA requirements.

Comprehensive accessibility testing infrastructure validates:
- 8 accent colors × 2 themes × 2 states = 32 combinations
- All meet 4.5:1 minimum contrast ratio for normal text
- Automated tests in `tests/accessibility/test_wcag.py` using axe-core

### Accent Colors

Eight accent colors are available via the `:accent:` config key:

- `blue` (default)
- `purple`
- `red`
- `green`
- `orange`
- `yellow`
- `pink`
- `gray`

All accent colors use the CSS custom property system with `--primary-*` tokens that cascade through semantic tokens for links, handrails, and interactive elements.

### Typography

Two typography modes via the `:typography:` config key:

- `sans-serif` (default) — Montserrat for headings, Source Sans 3 for body
- `serif` — Source Serif 4 for both headings and body

Implemented using `--font-heading` and `--font-body` CSS custom properties.

---

## To Define

- [ ] Define manual override precedence for system dark mode preference
- [ ] Document theming API for third-party theme creators
- [ ] Consider high contrast mode support
