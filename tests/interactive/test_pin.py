"""Interactive tests for pinning a block into the sidebar's Pinned view.

Hovering a reference shows an inert preview (tooltips.js). A pin control in the
preview's corner keeps the same excerpt open in the Pinned view, so the reader
can read a proof with the result it depends on beside it; a block's handrail
menu offers the same as "Pin". Pinning opens the Pinned view. One pin at a time:
pinning replaces, and the close button unpins.
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _load(page: Page, server: str) -> None:
    if page.viewport_size["width"] < 768:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)


def _hover_ref(page: Page, href: str):
    ref = page.locator(f'.manuscript a.reference[href="{href}"]').first
    ref.scroll_into_view_if_needed()
    ref.hover()
    return ref


def _pin_button(page: Page, href: str):
    # Target the pin control for THIS reference: tooltipster leaves closed
    # tooltips in the DOM, so a bare .first can match a stale one.
    _hover_ref(page, href)
    pin = page.locator(f'.tooltipster-base .ref-pin[data-pin-target="{href}"]').last
    expect(pin).to_be_visible(timeout=3000)
    return pin


def _pin(page: Page, href: str) -> None:
    _pin_button(page, href).click()


class TestPinToSidebar:
    def test_reference_preview_has_pin_control(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        pin = _pin_button(page, "#thm-x")
        assert pin.get_attribute("aria-label") == "Pin to the sidebar"
        assert pin.get_attribute("aria-pressed") == "false"

    def test_pin_opens_pinned_view(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        rail = page.locator(".proof-rail")
        expect(rail).to_have_class(re.compile(r"\bhas-pin\b"))
        expect(rail).to_have_class(re.compile(r"\bscope-pinned\b"))
        expect(rail).to_have_class(re.compile(r"\bopen\b"))
        expect(page.locator('.rail-strip-btn[data-view="pinned"]')).to_have_attribute(
            "aria-pressed", "true"
        )
        expect(page.locator(".rail-pinned")).to_contain_text("A claim about")

    def test_pinned_preview_shows_pinned_state(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        page.keyboard.press("Escape")
        pin = _pin_button(page, "#thm-x")
        expect(pin).to_have_attribute("aria-pressed", "true")
        assert pin.get_attribute("aria-label") == "Pinned in the sidebar"
        assert pin.get_attribute("data-pinned") is not None

    def test_pin_replaces_previous(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        expect(page.locator(".rail-pinned")).to_contain_text("A claim about")
        _pin(page, "#st-1")
        expect(page.locator(".rail-pinned")).to_contain_text("First")
        expect(page.locator(".rail-pinned")).not_to_contain_text("A claim about")

    def test_pinned_view_has_empty_state(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        page.click('.rail-strip-btn[data-view="pinned"]')
        rail = page.locator(".proof-rail")
        expect(rail).to_have_class(re.compile(r"\bscope-pinned\b"))
        expect(page.locator(".rail-pinned-empty")).to_be_visible()
        expect(page.locator(".rail-pinned-body")).to_be_hidden()

    def test_unpin_clears(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        page.locator(".rail-pin-close").click()
        rail = page.locator(".proof-rail")
        expect(rail).not_to_have_class(re.compile(r"\bhas-pin\b"))
        expect(page.locator(".rail-pinned-empty")).to_be_visible()
        expect(page.locator(".rail-pinned-body")).to_be_hidden()

    def test_handrail_menu_pins_block(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        theorem = page.locator(".manuscript .theorem").first
        theorem.scroll_into_view_if_needed()
        theorem.hover()
        theorem.locator(":scope > .hr-border-zone .hr-border-dots").click()
        item = page.locator('#hr-menu-singleton [data-role="pin"]')
        expect(item).to_be_visible()
        item.click()
        rail = page.locator(".proof-rail")
        expect(rail).to_have_class(re.compile(r"\bscope-pinned\b"))
        expect(page.locator(".rail-pinned")).to_contain_text("A claim about")
