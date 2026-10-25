"""Interactive tests for the interface tooltip (uitip.js).

The sidebar's strip controls show a small label after a short hover-intent
delay. Moving the pointer off a control before the delay fires must cancel the
pending label, so it never pops up beside a control the cursor already left.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

# uitip.js shows the label after this delay (the `show` hover-intent timer).
HOVER_DELAY_MS = 350


def _load(page: Page, server: str) -> None:
    # Desktop width: the strip is in the left margin, clear of the manuscript.
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto(f"{server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    # uitip.setup() runs after the first render, so wait for its element.
    page.wait_for_selector("#rsm-ui-tip", state="attached", timeout=10_000)


def _strip_control(page: Page):
    return page.locator('.rail-strip-btn[data-view="contents"]')


def test_tip_shows_after_hover_delay(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _strip_control(page).hover()
    tip = page.locator("#rsm-ui-tip")
    expect(tip).to_be_visible(timeout=2000)
    expect(tip).to_have_text("Contents")


def test_tip_cancelled_when_pointer_leaves_before_delay(
    page: Page, interactive_server: str
):
    _load(page, interactive_server)
    _strip_control(page).hover()
    # Leave the control for plain page well within the hover-intent delay, then
    # wait past it. The pending timer must be cancelled, so the tip never shows.
    page.mouse.move(700, 450)
    page.wait_for_timeout(HOVER_DELAY_MS + 250)
    expect(page.locator("#rsm-ui-tip")).to_be_hidden()
