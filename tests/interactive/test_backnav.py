"""Chrome jumps (proof-rail nodes, keyboard "jump to top") navigate by URL hash
so they ride the native browser Back button: the jump pushes a history entry and
sets the hash, and Back restores the prior scroll position. (In-text :ref:/TOC
clicks are native anchors and already behave this way; this covers the JS jumps
that previously used scrollIntoView and left no history entry.)
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def test_keyboard_jump_to_top_pushes_history_and_back_returns(page: Page, interactive_server: str):
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{interactive_server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)

    # Move well down the document and focus a content block so keyboard.js
    # handles the "H" (jump to top) shortcut.
    page.locator(".manuscript .hr").last.scroll_into_view_if_needed()
    page.wait_for_timeout(200)
    y_before = page.evaluate("() => Math.round(window.scrollY)")
    h_before = page.evaluate("() => history.length")
    assert y_before > 200, f"expected to be scrolled down, got scrollY={y_before}"

    page.evaluate("() => document.querySelector('.manuscript .hr[id]').focus()")
    page.keyboard.press("H")

    # The jump pushes a history entry, sets the hash, and (smooth-)scrolls up.
    # Use event-based waits: scroll-behavior:smooth makes the scroll async.
    page.wait_for_function(f"() => history.length > {h_before}", timeout=3000)
    assert page.evaluate("() => location.hash") != "", "jump did not set a URL hash"
    page.wait_for_function(f"() => window.scrollY < {y_before} - 50", timeout=3000)

    # Native browser Back returns to where the reader was.
    page.go_back()
    page.wait_for_function(f"() => Math.abs(window.scrollY - {y_before}) < 100", timeout=3000)
