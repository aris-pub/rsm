"""Paragraphs with math stay inside the column.

A block's content zone is a flex item, and with min-width: auto it cannot
shrink below the widest thing inside it. In a paragraph with math that can be
MathJax's hidden assistive copy of the math (wider than the rendered math) or a
display equation nested in the paragraph. The zone then grew past the column at
narrow widths and when the sidebar panel narrows the column. #114 only gave the
mathblock's own content zone min-width: 0, and wide-math.rsm has the equation
as a block on its own, so neither case was covered. The fixture is a paragraph
from a real paper that showed the bug.
"""

import pytest
from playwright.sync_api import Playwright

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

# Every block's content zone must end at or before the column's right edge, and
# must be allowed to shrink (min-width 0): with min-width: auto a zone grows to
# its widest content. A real paper overflowed by up to 164px this way; this
# fixture does not visibly overflow, so the rule itself is checked too.
MEASURE = """() => {
  const man = document.querySelector('.manuscript').getBoundingClientRect();
  let worst = 0, what = '', rigid = 0;
  for (const z of document.querySelectorAll('.manuscript .hr > .hr-content-zone')) {
    const r = z.getBoundingClientRect();
    if (getComputedStyle(z).minWidth !== '0px') rigid++;
    if (r.width && r.right - man.right > worst) { worst = r.right - man.right; what = z.textContent.trim().slice(0, 40); }
  }
  return {pastColumn: worst, block: what, zonesThatCannotShrink: rigid, pageOverflow: document.documentElement.scrollWidth - innerWidth};
}"""


def _contexts(pw: Playwright, browser):
    iphone = pw.devices["iPhone 13"]
    return {
        "iphone-13": (browser.new_context(**iphone), False),
        "desktop-480": (browser.new_context(viewport={"width": 480, "height": 800}), False),
        "desktop-900-panel-open": (browser.new_context(viewport={"width": 900, "height": 800}), True),
    }


@pytest.mark.parametrize("setup", ["iphone-13", "desktop-480", "desktop-900-panel-open"])
def test_equation_in_paragraph_stays_in_the_column(playwright: Playwright, browser, interactive_server: str, setup):
    ctxs = _contexts(playwright, browser)
    ctx, open_panel = ctxs[setup]
    for name, (other, _) in ctxs.items():
        if name != setup:
            other.close()
    page = ctx.new_page()
    try:
        page.goto(f"{interactive_server}/wide-math-in-paragraph.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        page.locator(".manuscript mjx-container").first.wait_for(state="attached", timeout=15_000)
        if open_panel:
            page.click('.rail-strip-btn[data-view]')
            page.wait_for_function("() => document.documentElement.classList.contains('rail-open')")
            page.wait_for_timeout(600)
        m = page.evaluate(MEASURE)
        assert m["zonesThatCannotShrink"] == 0, f"content zones keep min-width: auto ({setup}): {m}"
        assert m["pastColumn"] <= 1, f"a block runs past the column ({setup}): {m}"
        assert m["pageOverflow"] <= 0, f"the page scrolls sideways ({setup}): {m}"
    finally:
        ctx.close()
