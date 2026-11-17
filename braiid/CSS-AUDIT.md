# Modern CSS audit of braiid.css

Checked on 2026-11-17 (rsm-fv2). This is a list of proposals, not changes. Line
numbers refer to braiid.css at that date. The browser floor is the one already
set by `light-dark()`: Chrome/Edge 123+, Safari 17.5+, Firefox 120+. Items that
need a newer browser say so.

Page layout is out of scope here. The author decided that page layout belongs
in CSS, not JavaScript; rsm-j51 covers moving `layout()` out of sidebar.js into
braiid.css with container queries, and the `--rail-ml` / `--rail-mw` rules
under `html.has-rail` (around line 3934) go with it.

## Already modern

- Colors are single `light-dark()` definitions, switched by `color-scheme`
  (see THEMING.md).
- Nesting (`&`), `:is()`, `:has()`, `@layer`, `color-mix()`, `:focus-visible`
  and logical properties (`margin-inline`, `padding-inline`, `inset-inline`)
  are in use already.

## Proposals

1. **Source modal as a `<dialog>`.**
   Location: `.rsm-source-modal` (line 3467) and `showSource()` in
   rsm/static/handrails.js.
   Today: a fixed `div` covers the page with `left/top: 0` and `width/height:
   100%`, a `z-index` of 2000 and a fixed `rgba(0, 0, 0, 0.4)` backdrop.
   JavaScript handles Escape and the click outside, and nothing keeps keyboard
   focus inside the modal.
   Proposed: build it as a `<dialog>` opened with `showModal()`, styled with
   `::backdrop`.
   Gain: the browser handles the top layer, Escape, the focus trap and inert
   page content, so the `z-index`, the key handler and most of the rule go
   away. This needs a change in handrails.js as well as the CSS.

2. **Hard-coded tint colors to `color-mix()` on tokens.**
   Location: `.deplens-down` and its keyframe (lines 2533 and 2552,
   `rgba(226, 136, 0, ...)`); `.deplens-kbd` (line 803, white at 22% and 50%);
   `.hr-border-dots:hover` (line 1374, mixes with a fixed `white`).
   Today: the tint is a fixed RGB value, so it does not follow the accent or
   the theme (the dots hover mixes with white in dark mode too).
   Proposed: `color-mix(in srgb, var(--yellow-600) 7%, transparent)` and
   similar, and mix the dots hover with `var(--surface-page)` or a token in
   place of `white`.
   Gain: one source for each color, and the tints adapt to dark mode.

3. **One theme flag for the `display` twins.**
   Location: `.dark-only` / `.light-only` (line 3398), the static fallbacks
   (line 3421) and `.widget-preview-still` (line 4097).
   Today: each `display` switch is written twice, once under `.dark-theme`
   and once under `@media (prefers-color-scheme: dark)` with
   `:root:not(.light-theme)`.
   Proposed: set a custom property such as `--theme: dark` once (on
   `.dark-theme` and in a single media twin), then switch each `display` with
   `@container style(--theme: dark)`.
   Gain: the media twin is written once instead of once per rule.
   Caveat: custom property style queries are newer than the current floor;
   check Firefox support before adopting.

4. **`100vh` to `100dvh`.**
   Location: the rail panel `max-height` (line 1884).
   Today: on phones `100vh` is the height with the browser toolbar hidden, so
   the bottom of the panel can sit under the toolbar.
   Proposed: `100dvh`.
   Gain: the panel fits the visible area on mobile browsers.

5. **Fluid root font size.**
   Location: `:root` `font-size` 12px (line 26), 14px from 640px (line 3453)
   and 16px from 1024px (line 3461).
   Today: the root font size jumps at two breakpoints, which is also why media
   query `rem` values do not match the page's `rem` (noted in rsm-j51).
   Proposed: `font-size: clamp(12px, <slope>, 16px)`.
   Gain: no jumps and one rule. This changes the type size between the
   breakpoints, so it is a design decision, not only a cleanup.

6. **`transition: all` on the theme toggle.**
   Location: `.rsm-theme-toggle` (line 3354 onward, `transition: all` at line
   3368).
   Today: no page has this button any more (the theme control moved to the
   sidebar's Reading tab), so the whole `.rsm-theme-toggle` block, its
   reduced-motion rule (around line 3441) and its print entry (around line
   3728) are unused.
   Proposed: delete the block.
   Gain: less dead CSS.

7. **Hand-placed popups to the popover API and anchor positioning.**
   Location: the many fixed or absolute popups with their own `z-index`
   (24 `z-index` values in the file: menus, tooltips, the rail panel).
   Today: JavaScript computes positions and the `z-index` values keep the
   popups in order.
   Proposed: `popover` plus CSS anchor positioning (`anchor-name`,
   `position-anchor`, `position-try`) where it fits.
   Gain: the browser places and stacks the popups. Caveat: anchor
   positioning is newer than the current floor; check Safari and Firefox
   support first.
