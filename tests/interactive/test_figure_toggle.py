"""Test the static/interactive figure toggle via the handrail menu."""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


class TestFigureToggle:

    def test_static_toggle_swaps_content(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/figure-static.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        figure = page.locator("figure").first
        fallback = figure.locator(".static-fallback")

        # Fallback is hidden by default
        expect(fallback).to_be_hidden()

        # Open the caption handrail menu
        caption_dots = figure.locator("figcaption .hr-border-dots")
        caption_dots.click()

        # Click "Static"
        toggle = page.locator('#hr-menu-singleton [data-role="static-toggle"]')
        expect(toggle).to_be_visible()
        toggle.click()

        # Fallback should now be visible
        expect(fallback).to_be_visible()

        # Figure should have showing-static class
        expect(figure).to_have_class(re.compile("showing-static"))

    def test_toggle_back_to_interactive(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/figure-static.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        figure = page.locator("figure").first
        fallback = figure.locator(".static-fallback")
        caption_dots = figure.locator("figcaption .hr-border-dots")

        # Toggle to static
        caption_dots.click()
        page.locator('#hr-menu-singleton [data-role="static-toggle"]').click()
        expect(fallback).to_be_visible()

        # Toggle back to interactive
        caption_dots.click()
        toggle = page.locator('#hr-menu-singleton [data-role="static-toggle"]')
        toggle.click()
        expect(fallback).to_be_hidden()
        expect(figure).not_to_have_class(re.compile("showing-static"))

    def test_menu_text_changes_on_toggle(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/figure-static.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        figure = page.locator("figure").first
        caption_dots = figure.locator("figcaption .hr-border-dots")

        # Default state: "Static"
        caption_dots.click()
        toggle = page.locator('#hr-menu-singleton [data-role="static-toggle"]')
        expect(toggle.locator(".hr-menu-item-text")).to_have_text("Static")

        # After toggle: "Interactive"
        toggle.click()
        caption_dots.click()
        toggle = page.locator('#hr-menu-singleton [data-role="static-toggle"]')
        expect(toggle.locator(".hr-menu-item-text")).to_have_text("Interactive")

    def test_disabled_without_static(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/figure-static.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        # Second figure has no :static:
        figure = page.locator("figure").nth(1)
        caption_dots = figure.locator("figcaption .hr-border-dots")
        caption_dots.click()

        toggle = page.locator('#hr-menu-singleton [data-role="static-toggle"]')
        expect(toggle).to_have_class(re.compile("disabled"))

    def test_static_fallback_nested_in_handrail_is_revealed(
        self, page: Page, interactive_server: str
    ):
        """Regression: the static fallback lives inside the chromeless asset
        handrail (.hr-bare > .hr-content-zone). Toggling to static must reveal
        the fallback itself, not hide the wrapper that contains it (which would
        bury it). Guards the asset-handrail structure and the toggle against
        drifting apart again."""
        page.goto(f"{interactive_server}/figure-static.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        figure = page.locator("figure").first
        # Precondition: the fallback really is nested inside the asset handrail.
        expect(
            figure.locator(".hr-bare .hr-content-zone > .static-fallback")
        ).to_have_count(1)

        fallback = figure.locator(".static-fallback")
        interactive = figure.locator(
            ".hr-bare .hr-content-zone > :not(.static-fallback)"
        ).first

        figure.locator("figcaption .hr-border-dots").click()
        page.locator('#hr-menu-singleton [data-role="static-toggle"]').click()

        # The fallback is genuinely visible (no ancestor is display:none) and the
        # interactive content beside it is hidden.
        expect(fallback).to_be_visible()
        expect(interactive).to_be_hidden()

    def test_icon_changes_on_toggle(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/figure-static.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        figure = page.locator("figure").first
        caption_dots = figure.locator("figcaption .hr-border-dots")

        # Default: image icon
        caption_dots.click()
        toggle = page.locator('#hr-menu-singleton [data-role="static-toggle"]')
        use_el = toggle.locator("svg use")
        expect(use_el).to_have_attribute("href", "#hr-icon-image")

        # After toggle: play icon
        toggle.click()
        caption_dots.click()
        toggle = page.locator('#hr-menu-singleton [data-role="static-toggle"]')
        use_el = toggle.locator("svg use")
        expect(use_el).to_have_attribute("href", "#hr-icon-play")
