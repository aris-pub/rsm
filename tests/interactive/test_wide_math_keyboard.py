"""Regression tests for rsm-dvb: keyboard users can scroll wide display math.

A display equation wider than its column scrolls inside its content zone. While
the zone overflows it is a Tab stop (tabindex=0, role=region, a label), so the
arrow keys scroll it. ArrowLeft and ArrowRight on the focused mathblock also
scroll it. Equations that fit get none of this, so they add no Tab stop.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

ZONES = "div.mathblock > .hr-content-zone"


def open_fixture(page: Page, server: str, width: int):
    page.set_viewport_size({"width": width, "height": 800})
    page.goto(f"{server}/wide-narrow-math.html")
    page.wait_for_function("() => window.__rsmInitialized === true", timeout=10_000)
    page.locator(f"{ZONES} mjx-container").first.wait_for(state="attached", timeout=15_000)
    page.evaluate(
        "async () => { await window.rsm.mathIdle(); await document.fonts.ready;"
        " await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); }"
    )
    return page.locator(ZONES)


def attrs(zone):
    return zone.evaluate(
        "el => ({tabindex: el.getAttribute('tabindex'), role: el.getAttribute('role'),"
        " label: el.getAttribute('aria-label'), overflow: el.scrollWidth - el.clientWidth})"
    )


def test_only_overflowing_zones_are_tab_stops_at_320(page: Page, interactive_server: str):
    zones = open_fixture(page, interactive_server, 320)
    assert zones.count() == 3
    wide, narrow, unnumbered = (attrs(zones.nth(i)) for i in range(3))

    assert wide["overflow"] > 0, "fixture: the first equation must overflow at 320px"
    assert wide["tabindex"] == "0"
    assert wide["role"] == "region"
    assert wide["label"] == "Equation (1), scrolls horizontally"

    assert narrow["overflow"] <= 0, "fixture: the second equation must fit at 320px"
    assert (narrow["tabindex"], narrow["role"], narrow["label"]) == (None, None, None)

    assert unnumbered["overflow"] > 0, "fixture: the third equation must overflow at 320px"
    assert unnumbered["tabindex"] == "0"
    assert unnumbered["role"] == "region"
    assert unnumbered["label"] == "Equation, scrolls horizontally"


def test_no_zone_is_a_tab_stop_at_1280(page: Page, interactive_server: str):
    zones = open_fixture(page, interactive_server, 1280)
    for i in range(zones.count()):
        a = attrs(zones.nth(i))
        assert a["overflow"] <= 0, f"fixture: equation {i} must fit at 1280px"
        assert (a["tabindex"], a["role"], a["label"]) == (None, None, None), a


def test_tab_reaches_wide_zone_and_arrow_scrolls_it(page: Page, interactive_server: str):
    zone = open_fixture(page, interactive_server, 320).nth(0)
    zone.locator("xpath=..").focus()
    page.keyboard.press("Tab")
    assert zone.evaluate("el => document.activeElement === el")
    page.keyboard.press("ArrowRight")
    page.wait_for_function("el => el.scrollLeft > 0", arg=zone.element_handle(), timeout=3_000)


def test_arrows_on_focused_wide_mathblock_scroll_its_zone(page: Page, interactive_server: str):
    zone = open_fixture(page, interactive_server, 320).nth(0)
    block = zone.locator("xpath=..")
    block.focus()
    page.keyboard.press("ArrowRight")
    page.wait_for_function("el => el.scrollLeft > 0", arg=zone.element_handle(), timeout=3_000)
    assert block.evaluate("el => document.activeElement === el")
    page.keyboard.press("ArrowLeft")
    page.wait_for_function("el => el.scrollLeft === 0", arg=zone.element_handle(), timeout=3_000)


def test_tab_stop_follows_resize(page: Page, interactive_server: str):
    zone = open_fixture(page, interactive_server, 1280).nth(0)
    assert attrs(zone)["tabindex"] is None

    page.set_viewport_size({"width": 320, "height": 800})
    page.wait_for_function(
        "el => el.getAttribute('tabindex') === '0'", arg=zone.element_handle(), timeout=3_000
    )

    page.set_viewport_size({"width": 1280, "height": 800})
    page.wait_for_function(
        "el => !el.hasAttribute('tabindex') && !el.hasAttribute('role')"
        " && !el.hasAttribute('aria-label')",
        arg=zone.element_handle(),
        timeout=3_000,
    )
