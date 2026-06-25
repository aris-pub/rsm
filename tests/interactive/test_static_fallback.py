"""Interactive behavior of the :static: / :dark: figure fallback.

Covers the three gaps the plain JS static-toggle did not: sizing (the shown
static must not overflow), no-JS reveal (the static must appear with scripting
disabled, via <noscript>), and the dark variant (dark mode swaps the static)."""

import pytest
from playwright.sync_api import Browser, Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


class TestStaticFallbackSizing:

    def test_shown_static_does_not_overflow(self, page: Page, interactive_server: str):
        """The static image is generated at 1600px wide; once revealed it must
        scale down to the container, not render at its natural pixel size."""
        page.goto(f"{interactive_server}/static-fallback.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        figure = page.locator("figure").first
        fallback = figure.locator(".static-fallback")

        # Reveal the static via the handrail toggle.
        figure.locator("figcaption .hr-border-dots").click()
        page.locator('#hr-menu-singleton [data-role="static-toggle"]').click()
        expect(fallback).to_be_visible()

        shown_img = figure.locator(".static-fallback-light")
        img_box = shown_img.bounding_box()
        figure_box = figure.bounding_box()
        assert img_box is not None and figure_box is not None
        # The rendered image fits inside the figure (would be ~1600px otherwise).
        assert img_box["width"] <= figure_box["width"] + 1


class TestStaticFallbackNoJS:

    def test_static_visible_without_javascript(
        self, browser: Browser, interactive_server: str
    ):
        """With JS disabled, the <noscript> copy renders and the static is shown
        even though the interactive toggle never runs."""
        context = browser.new_context(java_script_enabled=False)
        try:
            page = context.new_page()
            page.goto(f"{interactive_server}/static-fallback.html")

            figure = page.locator("figure").first
            # The noscript copy holds the static images; one of them is visible.
            noscript_static = figure.locator("noscript .static-fallback-light")
            # Playwright surfaces <noscript> children as DOM when JS is disabled.
            expect(noscript_static).to_be_visible()
        finally:
            context.close()

    def test_noscript_inert_with_javascript(self, page: Page, interactive_server: str):
        """With JS on, the <noscript> content must not render (its static stays
        hidden); only the JS-toggleable .static-fallback path is used."""
        page.goto(f"{interactive_server}/static-fallback.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        figure = page.locator("figure").first
        noscript_static = figure.locator("noscript .static-fallback-light")
        expect(noscript_static).to_be_hidden()
        # And the toggleable fallback is hidden until the user opts in.
        expect(figure.locator(".static-fallback")).to_be_hidden()


class TestStaticFallbackDark:

    def test_dark_theme_swaps_static_to_dark_image(
        self, page: Page, interactive_server: str
    ):
        """Revealing the static and switching to .dark-theme shows the dark image
        and hides the light one."""
        page.goto(f"{interactive_server}/static-fallback.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        figure = page.locator("figure").first
        light = figure.locator(".static-fallback .static-fallback-light")
        dark = figure.locator(".static-fallback .static-fallback-dark")

        # Reveal the static.
        figure.locator("figcaption .hr-border-dots").click()
        page.locator('#hr-menu-singleton [data-role="static-toggle"]').click()

        # Light mode: light static shown, dark hidden.
        expect(light).to_be_visible()
        expect(dark).to_be_hidden()

        # Switch the document to dark mode the same way the reading controls do.
        page.evaluate(
            "() => document.documentElement.classList.add('dark-theme')"
        )
        expect(dark).to_be_visible()
        expect(light).to_be_hidden()
