# Responsiveness

**Mobile-first responsive design system using proportional scaling**

---

## Architecture

BRAIID uses a **mobile-first, proportional scaling** approach where all spacing scales automatically with viewport size by adjusting the root font-size.

### Key Principle: One Chunk = 3rem

All spacing derives from a single base unit:
```css
--chunk: 3rem;  /* Always 3× the root font-size */
```

At different viewports, the root font-size changes, and all rem-based spacing scales proportionally:

| Viewport | Root font-size | 1 chunk | Scale |
|----------|----------------|---------|-------|
| Mobile (< 640px) | 12px | 36px | 75% |
| Tablet (640px-1024px) | 14px | 42px | 87.5% |
| Desktop (≥ 1024px) | 16px | 48px | 100% |

---

## Breakpoints

Aligned with Tailwind CSS conventions, using **mobile-first** (`min-width`) media queries:

```css
/* Mobile: < 640px (default) */
:root {
  font-size: 12px;
}

/* sm: Small tablets and up (640px+) */
@media (min-width: 640px) {
  :root {
    font-size: 14px;
  }
}

/* lg: Desktop and up (1024px+) */
@media (min-width: 1024px) {
  :root {
    font-size: 16px;
  }
}
```

### Why These Breakpoints?

- **640px (sm)**: Captures landscape phones and small tablets
- **1024px (lg)**: Standard desktop/laptop threshold
- **Tailwind-inspired**: Aligns with industry conventions for consistency across Aris products

---

## Spacing Tokens

All spacing uses the chunk system, defined in rem units:

```css
--chunk-twelfth: 0.25rem;   /* chunk ÷ 12 */
--chunk-sixth: 0.5rem;       /* chunk ÷ 6 */
--chunk-quarter: 0.75rem;    /* chunk ÷ 4 */
--chunk-third: 1rem;         /* chunk ÷ 3 */
--chunk-half: 1.5rem;        /* chunk ÷ 2 */
--chunk: 3rem;               /* base unit */
--chunk-2: 6rem;             /* chunk × 2 */
--chunk-3: 9rem;             /* chunk × 3 */
--chunk-20: 60rem;           /* chunk × 20 - max width */
```

These scale automatically at each breakpoint:

| Token | Mobile | Tablet | Desktop |
|-------|--------|--------|---------|
| `--chunk-twelfth` | 3px | 3.5px | 4px |
| `--chunk-sixth` | 6px | 7px | 8px |
| `--chunk-third` | 12px | 14px | 16px |
| `--chunk-half` | 18px | 21px | 24px |
| `--chunk` | 36px | 42px | 48px |
| `--chunk-2` | 72px | 84px | 96px |

---

## Benefits

### ✅ Automatic Scaling
Change one value (root font-size) and everything scales proportionally:
- Spacing (padding, margins, gaps)
- Border radius
- Handrail zones
- Layout offsets

### ✅ Consistent Proportions
Relationships between elements remain constant across viewports. A gap that's "half a chunk" is always half a chunk, whether on mobile or desktop.

### ✅ Accessibility
Respects user font-size preferences set in browser settings.

### ✅ Simple Maintenance
No need to write media queries for every spacing value. Define it once in rem, it scales everywhere.

### ✅ Visual Testing
Test at three viewports to verify the entire responsive system:
- Mobile (375×667) - tests 12px base
- Tablet (768×1024) - tests 14px base
- Desktop (1280×720) - tests 16px base

---

## Migration Strategy

### Converting px to tokens

When replacing hardcoded pixel values:

1. **Identify the value at desktop (16px base)**
2. **Find the matching token** from the table above
3. **Replace with token or rem value**

Examples:
```css
/* Before */
padding: 8px;
margin: 16px;
gap: 24px;

/* After */
padding: var(--chunk-sixth);    /* or 0.5rem */
margin: var(--chunk-third);     /* or 1rem */
gap: var(--chunk-half);         /* or 1.5rem */
```

### Border radius tokens

Also converted to rem for scaling:
```css
--radius-sm: 0.125rem;  /* 2px at desktop */
--radius-md: 0.25rem;   /* 4px at desktop */
--radius-lg: 0.5rem;    /* 8px at desktop */
--radius-xl: 1rem;      /* 16px at desktop */
```

---

## Open Questions

### Handrails on Mobile

At 12px base font-size (mobile), handrails are 36px wide (--chunk). This is acceptable for touch targets but we should test:
- [ ] Are handrail controls still usable?
- [ ] Should we hide handrails on mobile entirely?
- [ ] Alternative interaction patterns (bottom sheet, swipe)?

### Typography Scaling

Currently only the base font-size scales. Should heading sizes also scale with viewport using `clamp()`?

```css
/* Potential enhancement */
--h1-size: clamp(1.5rem, 4vw, 2rem);
```

Or keep fixed rem values and let the root font-size handle all scaling?

### Content Width

`--chunk-20` (max manuscript width) scales:
- Mobile: 750px (60rem × 12px)
- Tablet: 840px (60rem × 14px)
- Desktop: 960px (60rem × 16px)

Should max-width be fixed at a certain viewport?

### Figures and Tables

Large content at narrow viewports:
- [ ] Scale down proportionally (current behavior)
- [ ] Horizontal scroll within container
- [ ] Tap to expand modal view

---

## Status

| Requirement | Status |
|-------------|--------|
| Mobile-first breakpoints | ✅ Implemented |
| Proportional scaling | ✅ Implemented |
| Spacing tokens in rem | ✅ Implemented |
| Radius tokens in rem | ✅ Implemented |
| Visual tests at 3 viewports | 🚧 In progress |
| Hardcoded px values migrated | 🚧 ~118 remain |
| Handrail mobile behavior | ❌ Not designed |
| Figure/table overflow | ❌ Not designed |

---

## References

- **Tailwind CSS breakpoints**: https://tailwindcss.com/docs/responsive-design
- **ARCH 3.1 requirements**: Document must be readable 320px-2560px
- **BRAIID tokens**: See `braiid/TOKENS.md` for complete token system
