# Progressive Enhancement

**What works without JavaScript**

---

## Status: Stub

Current implementation is mostly correct but undocumented.

---

## ARCH Requirements

Per ARCH 4.1:

- Document MUST be fully readable with JavaScript disabled
- All text, figures, tables, equations, citations MUST render without JS
- Interactive figures MUST provide static fallback
- JavaScript MUST be used only for enhancement, not core content

---

## The Principle

> If the JavaScript fails, the science must survive.

BRAIID treats JavaScript as a layer that adds interactivity on top of a complete, readable document. Nothing in the LEFT or RIGHT regions of the handrail system is required to read the document — they enhance navigation and interaction.

---

## Current Behavior: JS Disabled

### What Works

| Feature | Status | Notes |
|---------|--------|-------|
| Body text | ✅ | Full content readable |
| Headings | ✅ | — |
| Figures | ✅ | Images render |
| Tables | ✅ | — |
| Math | ✅ | Source notation in HTML; may not render visually without MathJax |
| Citations | ✅ | Links work |
| Bibliography | ✅ | — |
| Code blocks | ✅ | Syntax highlighting is CSS-only (Pygments) |

### What Degrades

| Feature | Status | Notes |
|---------|--------|-------|
| Handrail controls | ❌ Hidden | Collapse, menu not functional |
| Collapsible sections | ❌ All expanded | Content visible but not collapsible |
| Theme toggle | ❌ Hidden | Falls back to system preference (once implemented) |
| Tooltips | ❌ Hidden | — |
| Toasts | ❌ Hidden | — |
| Context menus | ❌ Hidden | — |
| Source modal | ❌ Hidden | — |

### What's Broken

| Feature | Status | Notes |
|---------|--------|-------|
| Dark mode | ⚠️ | No `prefers-color-scheme` fallback — always light |
| Math rendering | ⚠️ | MathJax requires JS; source notation visible but not formatted |

---

## CSS Strategy

Progressive enhancement in CSS:

1. **Core styles** — work without JS, target static document
2. **Enhancement styles** — improve experience when JS available

Currently these are mixed in the same file. Could be separated:

```
braiid-core.css      — ARCH-compliant static document
braiid-interactive.css — JS-dependent enhancements
```

Or use a `.js` class on `<html>` to scope enhancements:

```css
/* Only when JS is available */
.js .hr-collapse-zone { display: block; }

/* Without JS, these are hidden */
.hr-collapse-zone { display: none; }
```

---

## Open Questions

### Math Fallback

MathJax requires JS. Options:
1. Accept degraded experience (source notation visible)
2. Pre-render to MathML (works in some browsers)
3. Pre-render to images (accessibility concerns)

### Handrails Without JS

Should handrails be completely hidden, or should the visual border remain?

Options:
1. **Hide everything** — clean reading experience, no non-functional UI
2. **Show border only** — structure visible, controls hidden
3. **Show all, disable interaction** — visual parity, controls don't work

---

## To Define

- [ ] Document expected behavior for each component without JS
- [ ] Add `prefers-color-scheme` for theme fallback
- [ ] Decide on math fallback strategy
- [ ] Decide on handrail fallback strategy
- [ ] Consider separating core vs enhancement CSS
