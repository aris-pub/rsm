"""Handrails of the blocks in a section share one vertical line.

On touch screens the fold chevron is hidden, and its column used to collapse
only in foldable blocks (headings, theorems, proofs), so their rails sat 12px
left of the paragraphs' rails. Screenshot tests did not catch it: their phone
runs used a narrow desktop window, where the touch rules never apply. This test
measures the rails directly, with and without touch.
"""

import pytest
from playwright.sync_api import Browser

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

FIXTURES = ["basic", "asides", "shareview_long", "citations-author-year", "pill", "notes", "calc"]

MODES = [
    ("phone-touch", {"viewport": {"width": 375, "height": 800}, "is_mobile": True, "has_touch": True}),
    ("phone-mouse", {"viewport": {"width": 375, "height": 800}}),
    ("desktop", {"viewport": {"width": 1280, "height": 900}}),
]

# For each section, the left edge of the rail of every block directly in it
# (not blocks nested inside another block, which are indented on purpose).
RAILS = """() => {
  const out = [];
  for (const sec of document.querySelectorAll('.manuscript section')) {
    const xs = [];
    for (const hr of sec.querySelectorAll('.hr')) {
      if (hr.closest('section') !== sec) continue;
      const outer = hr.parentElement.closest('.hr');
      if (outer && sec.contains(outer)) continue;
      const rail = hr.querySelector(':scope > .hr-border-zone > .hr-border-rect');
      if (!rail) continue;
      const r = rail.getBoundingClientRect();
      if (!r.height) continue;
      xs.push({x: r.left, what: hr.className.split(' ').filter(c => !c.startsWith('hr')).join('.')});
    }
    if (xs.length > 1) out.push({section: sec.querySelector('h2, h3, h4') ? sec.querySelector('h2, h3, h4').textContent.trim().slice(0, 40) : '', xs});
  }
  return out;
}"""

# Equation numbers and other info-zone content must fit their column.
OVERFLOW = """() => {
  const bad = [];
  for (const z of document.querySelectorAll('.manuscript .hr > .hr-info-zone')) {
    const zr = z.getBoundingClientRect();
    if (!zr.width) continue;
    const r = document.createRange();
    r.selectNodeContents(z);
    for (const q of r.getClientRects()) {
      if (q.width && q.right > zr.right + 0.5) bad.push(z.textContent.trim().slice(0, 12));
    }
  }
  return bad;
}"""


@pytest.mark.parametrize("mode,ctx_args", MODES, ids=[m for m, _ in MODES])
@pytest.mark.parametrize("fixture", FIXTURES)
def test_rails_in_a_section_line_up(browser: Browser, interactive_server: str, fixture, mode, ctx_args):
    ctx = browser.new_context(**ctx_args)
    page = ctx.new_page()
    try:
        page.goto(f"{interactive_server}/{fixture}.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        page.wait_for_timeout(300)
        sections = page.evaluate(RAILS)
        assert sections, "no section with two or more blocks to compare"
        off = []
        for s in sections:
            xs = [p["x"] for p in s["xs"]]
            # A heading's rail is 1px thicker, so allow 1.5px.
            if max(xs) - min(xs) > 1.5:
                off.append((s["section"], [(p["what"], round(p["x"], 1)) for p in s["xs"]]))
        assert not off, f"rails out of line ({mode}): {off}"
        assert page.evaluate(OVERFLOW) == []
    finally:
        ctx.close()
