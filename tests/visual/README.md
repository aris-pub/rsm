# Visual Regression Tests for BRAIID Design System

This directory contains Playwright-based visual regression tests that lock in the current visual state of RSM-compiled documents styled with BRAIID CSS.

## Purpose

These tests capture baseline screenshots of rendered RSM documents and detect any visual changes to the design system. They help prevent unintended visual regressions when refactoring CSS or making design changes.

## Structure

```
tests/visual/
├── __init__.py
├── conftest.py              # Playwright fixtures, HTML generation, VIEWPORTS config
├── fixtures/                # RSM source documents for testing
│   ├── block-types.rsm
│   ├── nesting-stacking.rsm
│   ├── nesting-shifting.rsm
│   └── interactive-states.rsm
├── screenshots/             # Baseline screenshots (committed to Git)
│   ├── block-types-{light,dark}-{mobile,tablet,desktop}.png
│   ├── nesting-{aligned-borders,depth-shifting}-{mobile,tablet,desktop}.png
│   ├── states-*-{mobile,tablet,desktop}.png
│   └── theming-*-{mobile,tablet,desktop}.png
├── test_block_types.py      # Block rendering tests (all viewports)
├── test_nesting.py          # Nesting and depth tests (all viewports)
├── test_states.py           # Interactive state tests (all viewports)
└── test_theming.py          # Light/dark mode tests (all viewports)
```

## Running Tests

### Run all visual tests

```bash
uv run pytest tests/visual/ -m visual
```

### Run specific test categories

```bash
uv run pytest tests/visual/test_block_types.py -v
uv run pytest tests/visual/test_theming.py -v
```

### Update baselines after intentional changes

After making intentional CSS changes, regenerate the screenshots:

```bash
# Delete old screenshots
rm -rf tests/visual/screenshots/

# Re-run tests to generate new screenshots
uv run pytest tests/visual/ -m visual

# Review changes, then commit
git add tests/visual/screenshots/
git commit -m "Update visual baselines for <feature>"
```

## Test Coverage

### Block Types
- **Light/Dark theme**: All major block types (paragraphs, theorems, proofs, code, math, lists)
- **Theorem-like blocks**: theorem, lemma, corollary, definition, example, proposition, remark
- **Proofs**: standard proofs, proof sketches, nested steps
- **Code**: inline code and syntax-highlighted codeblocks
- **Math**: inline math, display math, numbered equations
- **Lists**: ordered, unordered, and nested lists

### Nesting Behaviors
- **Stacking**: vertical alignment of borders when blocks are nested at same depth
- **Shifting**: proof step depth reduction (96px width reduction per level, depths 0-3)

### Interactive States
- **Hidden handrails**: default invisible state (opacity 0%)
- **Hovered**: handrail controls become visible
- **Focused**: blue background, active border (skipped - needs RSM syntax fix)
- **Collapsed**: content hidden, collapse indicator (skipped - needs RSM syntax fix)

### Theming
- **Light mode**: default color scheme
- **Dark mode**: inverted color palette with `.dark-theme` class

### Responsive
**All tests run at 3 viewports** (defined in `conftest.VIEWPORTS`):
- **Mobile**: 375×667 (iPhone SE) - tests 12px base font-size
- **Tablet**: 768×1024 (iPad) - tests 14px base font-size (640px+ breakpoint)
- **Desktop**: 1280×720 - tests 16px base font-size (1024px+ breakpoint)

## Known Issues

- Two tests are currently skipped due to RSM syntax errors in `interactive-states.rsm`:
  - `test_visible_handrail_focused`
  - `test_proof_collapsed`
- TODO: Fix RSM syntax for theorem and proof blocks to enable these tests

## Implementation Notes

- **Viewport parameterization**: All tests use `@pytest.mark.parametrize` with `VIEWPORTS` from `conftest.py`
- **Mobile-first responsive**: Tests verify mobile (12px), tablet (14px), desktop (16px) font-size scaling
- Tests use `page.screenshot(path=...)` to capture baselines
- Screenshots are committed to Git (no LFS needed, ~36 images, ~2MB total)
- Browser: Chromium only for consistency
- Fonts: Google Fonts loaded and waited for with `document.fonts.ready`
- CSS/JS: Inline in generated HTML for self-contained testing

## Future Improvements

- Add Firefox/Safari browser testing
- Fix RSM syntax issues in interactive-states fixture
- Add tests for equation numbering modes
- Add tests for table rendering
- Add tests for figure captions
- Consider adding Percy or similar for visual diff viewing in CI
