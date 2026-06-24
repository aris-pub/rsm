"""Regression: an open handrail menu must paint ABOVE the floating proof-rail.

The menu pops into the left gutter where the fixed `.proof-rail` (z-index 40)
sits. An ancestor of the handrail establishes a stacking context that paints
below that rail, so a z-index on the menu (or the handrail) is trapped beneath
it and the rail occludes the open menu. handrails.js portals the open menu to
<body> (absolutely positioned in page coordinates) to escape every such ancestor
context. This test asserts the rail no longer wins the paint order at the menu.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _load_sidebar(page: Page, server: str) -> None:
    # The proof-rail is a fixed sidebar only above the 1320px drawer breakpoint.
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)


def test_open_menu_paints_above_proof_rail(page: Page, interactive_server: str):
    _load_sidebar(page, interactive_server)

    # Bring the proof into view so its steps (whose menus pop into the rail's
    # gutter) are on screen, and the rail is live.
    page.evaluate(
        """() => {
            const el = document.querySelector('.proof[data-nodeid]');
            const y = el.getBoundingClientRect().top + window.scrollY
                      - window.innerHeight * 0.25;
            window.scrollTo(0, y);
        }"""
    )
    page.wait_for_selector(".proof-rail.active", timeout=5_000)

    # Open the menu on a proof step (its dots sit in the left gutter, so the
    # menu opens leftward, over the rail region).
    step = page.locator(".proof .step").first
    step.scroll_into_view_if_needed()
    dots = step.locator(".hr-border-dots").first
    dots.hover()
    dots.click()

    menu = page.locator("#hr-menu-singleton .hr-menu")
    expect(menu).to_be_visible()

    # At the menu's center, the topmost painted element is the menu (or a
    # descendant), NOT the proof-rail: i.e. the rail no longer occludes it.
    hit_is_menu = page.evaluate(
        """() => {
            const menu = document.querySelector('#hr-menu-singleton .hr-menu');
            const r = menu.getBoundingClientRect();
            const x = r.left + r.width / 2;
            const y = r.top + r.height / 2;
            const hit = document.elementFromPoint(x, y);
            if (!hit) return { ok: false, reason: 'no element at point' };
            const inMenu = hit.closest('#hr-menu-singleton') !== null;
            const inRail = hit.closest('.proof-rail') !== null;
            return { ok: inMenu && !inRail,
                     hitClass: hit.className && hit.className.toString(),
                     inMenu, inRail };
        }"""
    )
    assert hit_is_menu["ok"], f"rail occludes the open menu: {hit_is_menu}"

    # The singleton is portaled out to <body> to escape the trapping context.
    assert page.evaluate(
        "() => document.getElementById('hr-menu-singleton').parentElement === document.body"
    ), "open menu should be portaled to <body>"

    # And the menu sits above the rail's stacking level: a point shared by the
    # menu and the rail resolves to the menu, confirming z-order, not just that
    # the menu happens to extend past the rail's right edge.
    overlap_hit = page.evaluate(
        """() => {
            const menu = document.querySelector('#hr-menu-singleton .hr-menu');
            const rail = document.querySelector('.proof-rail.active');
            const m = menu.getBoundingClientRect();
            const rr = rail.getBoundingClientRect();
            const x1 = Math.max(m.left, rr.left), x2 = Math.min(m.right, rr.right);
            const y1 = Math.max(m.top, rr.top), y2 = Math.min(m.bottom, rr.bottom);
            if (x2 <= x1 || y2 <= y1) return { overlap: false };
            const hit = document.elementFromPoint((x1 + x2) / 2, (y1 + y2) / 2);
            return { overlap: true,
                     hitIsMenu: !!hit && hit.closest('#hr-menu-singleton') !== null,
                     hitIsRail: !!hit && hit.closest('.proof-rail') !== null };
        }"""
    )
    if overlap_hit["overlap"]:
        assert overlap_hit["hitIsMenu"] and not overlap_hit["hitIsRail"], (
            f"in the menu/rail overlap region the rail still wins: {overlap_hit}"
        )


def test_menu_tracks_page_on_scroll(page: Page, interactive_server: str):
    """The portaled menu is absolutely positioned in PAGE coordinates, so it stays
    open and scrolls with its handrail (as the in-flow menu did), rather than
    pinning to the viewport and detaching."""
    _load_sidebar(page, interactive_server)

    dots = page.locator(".hr:not(.hr-hidden) .hr-border-dots").first
    dots.scroll_into_view_if_needed()
    dots.hover()
    dots.click()
    menu = page.locator("#hr-menu-singleton .hr-menu")
    expect(menu).to_be_visible()

    top_before = menu.bounding_box()["y"]
    page.evaluate("() => window.scrollBy(0, 120)")
    # Still open, and moved up by the scroll amount (tracks the page, not the
    # viewport): a fixed menu would have kept the same viewport y.
    expect(menu).to_be_visible()
    top_after = menu.bounding_box()["y"]
    assert top_before - top_after == pytest.approx(120, abs=4), (
        f"menu should scroll with the page: {top_before} -> {top_after}"
    )


def test_portaled_menu_keeps_document_font(page: Page, interactive_server: str):
    """Portaling the menu to <body> takes it out of .manuscriptwrapper, so it no
    longer inherits the document font and would fall back to the browser serif
    default. Its computed font-family must match the manuscript's (the restated
    --font-body), not a serif fallback -- a visual regression guard."""
    _load_sidebar(page, interactive_server)

    dots = page.locator(".hr:not(.hr-hidden) .hr-border-dots").first
    dots.scroll_into_view_if_needed()
    dots.hover()
    dots.click()
    expect(page.locator("#hr-menu-singleton .hr-menu")).to_be_visible()

    fonts = page.evaluate(
        """() => {
            const item = document.querySelector('#hr-menu-singleton .hr-menu-item-text')
                      || document.querySelector('#hr-menu-singleton .hr-menu-item');
            const ms = document.querySelector('.manuscriptwrapper');
            return {
                menu: getComputedStyle(item).fontFamily,
                manuscript: getComputedStyle(ms).fontFamily,
            };
        }"""
    )
    assert fonts["menu"] == fonts["manuscript"], (
        f"portaled menu font {fonts['menu']!r} != manuscript {fonts['manuscript']!r}"
    )
