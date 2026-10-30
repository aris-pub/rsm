"""Regression test for rsm-ctu: wide display math must scroll in its own box.

At a narrow viewport a long display equation used to run past the right edge and
overlap its equation number, with nothing scrollable. The fix gives the
mathblock content zone its own horizontal scroll, so wide math scrolls inside
the block while the number (in the sibling .hr-info-zone) stays put.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def wait_for_rsm(page):
    page.wait_for_function(RSM_READY, timeout=10_000)


def test_wide_math_scrolls_in_its_own_box(page: Page, interactive_server: str):
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(f"{interactive_server}/wide-math.html")
    wait_for_rsm(page)

    # Wait for MathJax to replace the raw $$...$$ with rendered math.
    zone = page.locator("div.mathblock > .hr-content-zone").first
    zone.locator("mjx-container").wait_for(state="attached", timeout=15_000)

    # The rendered equation really is wider than its box (otherwise this
    # fixture is not exercising the bug).
    overflow = zone.evaluate("el => el.scrollWidth - el.clientWidth")
    assert overflow > 0, f"fixture equation is not wider than its box ({overflow})"

    # The content zone is a real horizontal scroll container: it accepts a
    # scroll offset. With overflow:visible (the bug) scrollLeft stays 0.
    scroll_left = zone.evaluate(
        "el => { el.scrollLeft = 9999; return el.scrollLeft; }"
    )
    assert scroll_left > 0, (
        "mathblock content zone does not scroll horizontally; wide math "
        "overflows instead of scrolling in its own box"
    )

    # The page itself must not scroll horizontally.
    page_overflow = page.evaluate(
        "() => document.documentElement.scrollWidth - window.innerWidth"
    )
    assert page_overflow <= 1, f"page scrolls horizontally by {page_overflow}px"
