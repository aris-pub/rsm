"""Print / PDF media behavior.

Browsers export PDF with JavaScript ON, so the JS-off <noscript> fallback never
runs and the screen-only chrome would leak onto paper. The @media print rules in
braiid.css are the real print fallback. These tests emulate print media and
assert it: interactive widgets become their static image, the floating rail and
gutter chrome disappear, and content JS collapsed is unfolded so the full paper
prints.
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


class TestPrintStaticFallback:

    def test_widget_swapped_for_static_under_print(
        self, page: Page, interactive_server: str
    ):
        """For a :html: widget figure (data-static), print media reveals the
        static image and hides the live widget mount, even though the JS toggle
        was never used."""
        page.goto(f"{interactive_server}/static-fallback.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        figure = page.locator("figure.html[data-static]")
        fallback = figure.locator(".static-fallback")
        widget = figure.locator("#widget")

        # On screen, the live widget shows and the static stays hidden.
        expect(widget).to_be_visible()
        expect(fallback).to_be_hidden()

        page.emulate_media(media="print")

        # Under print, the static is revealed and the live widget is hidden.
        expect(fallback).to_be_visible()
        expect(widget).to_be_hidden()

    def test_image_figure_shows_light_static_under_print(
        self, page: Page, interactive_server: str
    ):
        """An image figure with light/dark statics prints the light variant (paper
        is light) and hides the dark one and the live <picture>."""
        page.goto(f"{interactive_server}/static-fallback.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        figure = page.locator("figure.figure[data-static]")
        light = figure.locator(".static-fallback .static-fallback-light")
        dark = figure.locator(".static-fallback .static-fallback-dark")

        page.emulate_media(media="print")

        expect(light).to_be_visible()
        expect(dark).to_be_hidden()
        expect(figure.locator("picture")).to_be_hidden()


class TestPrintChromeHidden:

    def test_proof_rail_hidden_under_print(self, page: Page, interactive_server: str):
        """The floating proof-rail is screen-only and must not appear in the PDF."""
        # Desktop width so the rail is the active side panel (see test_collapsed).
        if page.viewport_size["width"] < 1321:
            page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{interactive_server}/collapsed.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        page.wait_for_selector(".proof-rail.active", timeout=10_000)

        expect(page.locator(".proof-rail")).to_be_visible()

        page.emulate_media(media="print")

        expect(page.locator(".proof-rail")).to_be_hidden()


class TestPrintUnfoldsCollapsed:

    def test_collapsed_proof_steps_visible_under_print(
        self, page: Page, interactive_server: str
    ):
        """A :collapsed: proof folds its steps on load; print media must unfold it
        so every step prints."""
        if page.viewport_size["width"] < 1321:
            page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{interactive_server}/collapsed.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        marked = page.locator(".proof.hr[data-start-collapsed]")
        expect(marked).to_have_class(re.compile(r"\bhr-collapsed\b"))
        # On screen the first step is folded away.
        expect(page.locator("#stp-c1")).to_be_hidden()

        page.emulate_media(media="print")

        # Under print the folded step is revealed.
        expect(page.locator("#stp-c1")).to_be_visible()
