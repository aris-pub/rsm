"""Interactive: the proof-rail becomes a 3-state bottom drawer at <=1100px.

Desktop (>1100px) keeps the fixed left rail. At <=1100px the SAME .proof-rail
re-skins as a bottom sheet driven by a `data-drawer` attribute with three states:

  closed - only a slim grip is visible
  peek   - a low bar showing the current proof's goal
  open   - the full sheet (scopes, map, state, reading)

A `.rail-handle` grip toggles peek<->open; the existing `.rail-collapse`
closes it; state persists in localStorage; focusing a step drops it to peek.

These assert the JS state machine (the data-drawer transitions, which are
CSS-independent) plus a light check that the sheet is bottom-anchored.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"
MOBILE = {"width": 800, "height": 1000}
DESKTOP = {"width": 1400, "height": 900}


def _load(page: Page, server: str, viewport=MOBILE) -> None:
    page.set_viewport_size(viewport)
    page.goto(f"{server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)
    # Clean slate so a persisted layout from another test can't leak in.
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)


def _state(page: Page):
    return page.evaluate(
        "() => document.querySelector('.proof-rail').getAttribute('data-drawer')"
    )


def _scroll_into_proof(page: Page):
    page.evaluate(
        "() => document.querySelector('.proof[data-nodeid]')"
        ".scrollIntoView({block:'center'})"
    )
    page.wait_for_timeout(400)


def test_rail_is_bottom_sheet_on_mobile(page: Page, interactive_server: str):
    _load(page, interactive_server)
    box = page.evaluate(
        """() => {const r=document.querySelector('.proof-rail');
        const b=r.getBoundingClientRect(); const cs=getComputedStyle(r);
        return {display:cs.display, position:cs.position,
                bottom:Math.round(b.bottom), vh:window.innerHeight};}"""
    )
    assert box["display"] != "none", "rail must not be hidden on mobile (it is a drawer)"
    assert box["position"] == "fixed"
    assert box["bottom"] >= box["vh"] - 2, f"drawer must sit at the viewport bottom: {box}"
    assert _state(page) in {"closed", "peek", "open"}, "rail needs a data-drawer state"
    expect(page.locator(".proof-rail .rail-handle")).to_be_attached()


def test_default_state_is_peek(page: Page, interactive_server: str):
    _load(page, interactive_server)
    assert _state(page) == "peek"


def test_handle_toggles_peek_and_open(page: Page, interactive_server: str):
    _load(page, interactive_server)
    handle = page.locator(".proof-rail .rail-handle")
    assert _state(page) == "peek"
    handle.click()
    assert _state(page) == "open"
    handle.click()
    assert _state(page) == "peek"


def test_drag_closes_and_tap_reopens(page: Page, interactive_server: str):
    """There is no close button: dragging the grip down lowers the sheet to
    closed, and a tap reopens it to peek."""
    _load(page, interactive_server)
    assert _state(page) == "peek"
    box = page.locator(".proof-rail .rail-handle").bounding_box()
    cx = box["x"] + box["width"] / 2
    cy = box["y"] + box["height"] / 2
    # Drag down ~40px -> step down a state (peek -> closed).
    page.mouse.move(cx, cy)
    page.mouse.down()
    page.mouse.move(cx, cy + 40, steps=6)
    page.mouse.up()
    assert _state(page) == "closed"
    # only the grip remains; the scope tabs are not shown
    assert not page.locator(".proof-rail .rail-scopes").is_visible()
    # A tap (no drag) reopens a closed sheet to peek.
    page.locator(".proof-rail .rail-handle").click()
    assert _state(page) == "peek"


def test_open_is_taller_than_peek(page: Page, interactive_server: str):
    _load(page, interactive_server)

    def h():
        return page.evaluate(
            "() => Math.round(document.querySelector('.proof-rail').getBoundingClientRect().height)"
        )

    peek_h = h()
    page.click(".proof-rail .rail-handle")  # -> open
    page.wait_for_timeout(300)
    assert h() > peek_h + 100, "open sheet must be substantially taller than peek"


def test_peek_shows_current_goal(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _scroll_into_proof(page)
    peek = page.locator(".proof-rail .rail-peek")
    expect(peek).to_be_visible()
    text = (peek.text_content() or "").strip()
    assert text, "peek bar must show the current proof's goal text"


def test_state_persists_across_reload(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.click(".proof-rail .rail-handle")  # -> open
    assert _state(page) == "open"
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)
    assert _state(page) == "open", "drawer state must survive a reload"


def test_desktop_keeps_left_rail(page: Page, interactive_server: str):
    _load(page, interactive_server, viewport=DESKTOP)
    box = page.evaluate(
        """() => {const r=document.querySelector('.proof-rail');
        const b=r.getBoundingClientRect(); const cs=getComputedStyle(r);
        return {position:cs.position, left:Math.round(b.left), bottom:Math.round(b.bottom),
                vh:window.innerHeight, drawer:r.getAttribute('data-drawer')};}"""
    )
    # On desktop it is the fixed LEFT rail, not bottom-anchored, and not in drawer mode.
    assert box["left"] < 200, f"desktop rail should hug the left gutter: {box}"
    assert box["bottom"] < box["vh"] - 50, "desktop rail must not be bottom-anchored"
    assert box["drawer"] in (None, ""), "desktop must not enter drawer mode"


def test_focusing_drops_to_peek(page: Page, interactive_server: str):
    """Entering focus mode must drop the drawer to peek so the focused cone is
    readable. focusmode.js signals this with a `rsm:focus-enter` event; here we
    verify the drawer's response to it (the map-node-click that fires the event
    is focus mode's own concern, covered by its tests)."""
    _load(page, interactive_server)
    page.click(".proof-rail .rail-handle")  # peek -> open
    assert _state(page) == "open"
    page.evaluate("() => document.dispatchEvent(new CustomEvent('rsm:focus-enter'))")
    assert _state(page) == "peek", "rsm:focus-enter should drop the drawer to peek"


def test_desktop_rail_pushes_content(page: Page, interactive_server: str):
    """At a width where the rail cannot fit in the centred margin, the content is
    pushed to the right of the rail (no overlap), not overlapped, not centred."""
    page.set_viewport_size({"width": 1450, "height": 900})
    page.goto(f"{interactive_server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)
    g = page.evaluate(
        """() => {
        const w = document.querySelector('.manuscriptwrapper').getBoundingClientRect();
        const r = document.querySelector('.proof-rail').getBoundingClientRect();
        return {railRight: Math.round(r.right), contentLeft: Math.round(w.left),
                contentW: Math.round(w.width), vw: window.innerWidth};
    }"""
    )
    assert g["contentLeft"] >= g["railRight"], f"content overlaps the rail: {g}"
    centred = (g["vw"] - g["contentW"]) / 2
    assert g["contentLeft"] > centred + 10, f"content not pushed right of centre: {g}"


def test_desktop_rail_centered_when_wide(page: Page, interactive_server: str):
    """When the margin is wide enough for the rail, the content stays centred and
    the rail does not overlap it."""
    page.set_viewport_size({"width": 1920, "height": 900})
    page.goto(f"{interactive_server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)
    g = page.evaluate(
        """() => {
        const w = document.querySelector('.manuscriptwrapper').getBoundingClientRect();
        const r = document.querySelector('.proof-rail').getBoundingClientRect();
        return {railRight: Math.round(r.right), contentLeft: Math.round(w.left),
                contentRight: Math.round(w.right), vw: window.innerWidth};
    }"""
    )
    assert g["contentLeft"] >= g["railRight"], f"rail overlaps content: {g}"
    left, right = g["contentLeft"], g["vw"] - g["contentRight"]
    assert abs(left - right) < 12, f"content not centred when wide: left={left} right={right}"
