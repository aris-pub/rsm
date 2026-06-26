"""Interactive tests for pinning a referenced block into the rail (potf-bio).

Hovering a reference shows an inert preview (tooltips.js). A "pin" button in
that preview keeps the same excerpt open in a Pinned tab of the rail, so the
reader can read a proof with the result it depends on beside it. One pin at a
time: pinning replaces, and [x] unpins.
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _load(page: Page, server: str) -> None:
    if page.viewport_size["width"] < 1321:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)


def _hover_ref(page: Page, href: str):
    ref = page.locator(f'a.reference[href="{href}"]').first
    ref.scroll_into_view_if_needed()
    ref.hover()
    return ref


def _pin(page: Page, href: str) -> None:
    # Target the pin button for THIS reference: tooltipster leaves closed
    # tooltips in the DOM, so a bare .first can match a stale one.
    _hover_ref(page, href)
    pin = page.locator(f'.ref-pin[data-pin-target="{href}"]')
    expect(pin).to_be_visible(timeout=3000)
    pin.click()


class TestPinToRail:
    def test_reference_tooltip_has_pin_button(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _hover_ref(page, "#thm-x")
        expect(page.locator(".ref-pin").first).to_be_visible(timeout=3000)

    def test_pin_populates_rail_and_switches_scope(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        rail = page.locator(".proof-rail")
        expect(rail).to_have_class(re.compile(r"\bhas-pin\b"))
        expect(rail).to_have_class(re.compile(r"\bscope-pinned\b"))
        expect(page.locator('.rail-scope[data-scope="pinned"]')).to_be_visible()
        expect(page.locator(".rail-pinned")).to_contain_text("A claim about")

    def test_pin_replaces_previous(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        expect(page.locator(".rail-pinned")).to_contain_text("A claim about")
        _pin(page, "#st-1")
        expect(page.locator(".rail-pinned")).to_contain_text("First")
        expect(page.locator(".rail-pinned")).not_to_contain_text("A claim about")

    def test_pinned_tab_always_present_with_empty_state(
        self, page: Page, interactive_server: str
    ):
        # Like the Proof tab, the Pinned tab is always there; with nothing pinned
        # it shows an empty state, not a hidden/absent tab.
        _load(page, interactive_server)
        tab = page.locator('.rail-scope[data-scope="pinned"]')
        expect(tab).to_be_visible()
        tab.click()
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
        # Tab stays (always present); the section falls back to its empty state.
        expect(page.locator('.rail-scope[data-scope="pinned"]')).to_be_visible()
        page.click('.rail-scope[data-scope="pinned"]')
        expect(rail).to_have_class(re.compile(r"\bscope-pinned\b"))
        expect(page.locator(".rail-pinned-empty")).to_be_visible()
        expect(page.locator(".rail-pinned-body")).to_be_hidden()
