"""The back pill: a transient, visible affordance over the native browser Back.

In-document jumps (following a :ref:/TOC link, a proof-rail node, or a keyboard
jump) ride native history (see test_backnav.py). That reversibility is invisible,
so a small "Back" pill appears after a jump and calls history.back() on click to
return the reader, then dismisses. It must NOT appear before any jump, and it is
a real, labelled button (it must not steal focus from the jumped-to block).
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"
PILL = ".rsm-back-pill"
PILL_VISIBLE = ".rsm-back-pill.is-visible"


def _load(page: Page, server: str):
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def test_back_pill_hidden_until_a_jump(page: Page, interactive_server: str):
    _load(page, interactive_server)
    # Built on load (so it can animate in) but not visible until a jump happens.
    assert page.locator(PILL).count() == 1
    assert not page.locator(PILL).is_visible()


def test_back_pill_is_a_labelled_button(page: Page, interactive_server: str):
    _load(page, interactive_server)
    pill = page.locator(PILL)
    assert pill.evaluate("el => el.tagName") == "BUTTON"
    assert pill.get_attribute("aria-label"), "pill needs an aria-label"


def test_jump_shows_pill_then_click_returns_and_dismisses(page: Page, interactive_server: str):
    _load(page, interactive_server)
    # Sit at an in-text reference near the bottom, note the position, then follow
    # it (a native hash jump up to the theorem).
    ref = page.locator('.manuscript a.reference[href="#thm-x"]').first
    ref.scroll_into_view_if_needed()
    page.wait_for_timeout(200)
    y_before = page.evaluate("() => Math.round(window.scrollY)")

    ref.click()
    # The jump moved the viewport; the pill offers a way back.
    page.wait_for_selector(PILL_VISIBLE, timeout=3000)
    # It does not steal focus: the jumped-to block keeps it (a11y).
    assert page.evaluate("() => document.activeElement.classList.contains('rsm-back-pill')") is False

    page.locator(PILL).click()
    # Clicking returns the reader to where they were (native Back restores scroll)
    page.wait_for_function(f"() => Math.abs(window.scrollY - {y_before}) < 150", timeout=3000)
    # ...and the pill dismisses once we are back.
    page.wait_for_function(
        "() => !document.querySelector('.rsm-back-pill').classList.contains('is-visible')",
        timeout=3000,
    )


def test_pill_dismisses_when_reader_scrolls_away(page: Page, interactive_server: str):
    _load(page, interactive_server)
    ref = page.locator('.manuscript a.reference[href="#thm-x"]').first
    ref.scroll_into_view_if_needed()
    page.wait_for_timeout(200)
    ref.click()
    page.wait_for_selector(PILL_VISIBLE, timeout=3000)
    # Resuming reading (scrolling well away from the landing) dismisses the pill,
    # so it never becomes pinned chrome.
    # This jump lands at the bottom of the (short) fixture, so "scrolling away"
    # means scrolling back up toward the start: a clear resumed-reading gesture.
    page.evaluate("() => window.scrollTo(0, 0)")
    page.wait_for_function(
        "() => !document.querySelector('.rsm-back-pill').classList.contains('is-visible')",
        timeout=3000,
    )
