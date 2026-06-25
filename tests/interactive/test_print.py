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


class TestPrintKeepsContent:
    """Two regressions the unfold and mount-hiding rules can cause on a real
    built paper but not on a bare fixture: rsm build embeds the raw source in
    <div class="rsm-source hide"> (so the .hide unfold must skip it), and a
    data-static figure's :caption: is its own handrail with its own content-zone
    (so the mount-hiding rule must skip it, or the caption prints as an empty
    box)."""

    def test_embedded_source_stays_hidden_under_print(
        self, page: Page, interactive_server: str
    ):
        page.goto(f"{interactive_server}/static-fallback.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        src = page.locator(".rsm-source")
        expect(src).to_have_count(1)

        page.emulate_media(media="print")

        expect(src).to_be_hidden()

    def test_figure_caption_prints_not_an_empty_box(
        self, page: Page, interactive_server: str
    ):
        page.goto(f"{interactive_server}/static-fallback.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        fig = page.locator("figure.figure[data-static]")

        page.emulate_media(media="print")

        # The static image prints, and its caption text prints with it.
        expect(fig.locator(".static-fallback")).to_be_visible()
        expect(fig.get_by_text("light and dark static fallbacks")).to_be_visible()


class TestPrintNoSpacerZoneMark:
    """A collapsed block caps its left gutter with a border-bottom on the
    spacer-zone. Print unfolds the body but keeps the .hr-collapsed class, so
    without the print override that cap prints as a stray ~16px dash at the
    block's bottom-left. These guard that the dash is gone and that the fix
    neither touches the on-screen cap nor shifts handrail content sideways."""

    def test_no_spacer_zone_bottom_border_under_print(
        self, page: Page, interactive_server: str
    ):
        if page.viewport_size["width"] < 1321:
            page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{interactive_server}/collapsed.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        # On screen the collapsed proof's spacer-zone still draws the cap.
        collapsed_spacer = page.locator(
            ".proof.hr.hr-collapsed > .hr-spacer-zone"
        ).first
        screen_width = collapsed_spacer.evaluate(
            "el => getComputedStyle(el).borderBottomWidth"
        )
        assert screen_width != "0px", (
            f"on screen the collapsed cap should still draw, got {screen_width}"
        )

        page.emulate_media(media="print")

        # Under print no spacer-zone may paint a bottom border (the stray dash).
        widths = page.evaluate(
            """() => Array.from(document.querySelectorAll('.hr-spacer-zone'),
                 el => getComputedStyle(el).borderBottomWidth)"""
        )
        assert widths, "fixture should contain at least one .hr-spacer-zone"
        assert all(w == "0px" for w in widths), (
            f"a spacer-zone still draws a bottom border under print: {widths}"
        )

    def test_handrail_content_stays_left_aligned_under_print(
        self, page: Page, interactive_server: str
    ):
        """The fix removes only the border, not the 16px spacer, so collapsed and
        non-collapsed handrails keep the same content-zone left edge."""
        if page.viewport_size["width"] < 1321:
            page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{interactive_server}/collapsed.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        page.emulate_media(media="print")

        lefts = page.evaluate(
            """() => {
              const left = sel => {
                const cz = document.querySelector(sel + ' > .hr-content-zone');
                return cz ? Math.round(cz.getBoundingClientRect().left) : null;
              };
              return {
                collapsed: left('.proof.hr.hr-collapsed'),
                plain: left('.proof.hr:not(.hr-collapsed)'),
              };
            }"""
        )
        assert lefts["collapsed"] is not None and lefts["plain"] is not None
        assert lefts["collapsed"] == lefts["plain"], (
            f"collapsed proof content shifted vs a plain proof: {lefts}"
        )


class TestPrintProofBracket:
    """Proofs carry the handrail's vertical rule as a print 'proof bracket'
    marking the proof's extent: just the rule (the rect), no dots or other
    chrome. Other handrail blocks drop their border-zone entirely in print."""

    def test_proof_shows_vertical_rule_without_dots_under_print(
        self, page: Page, interactive_server: str
    ):
        if page.viewport_size["width"] < 1321:
            page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{interactive_server}/collapsed.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        page.emulate_media(media="print")

        info = page.evaluate(
            """() => {
              const proof = document.querySelector('.proof.hr');
              const rect = proof.querySelector(':scope > .hr-border-zone > .hr-border-rect');
              const dots = proof.querySelector(':scope > .hr-border-zone > .hr-border-dots');
              const cs = e => getComputedStyle(e);
              return {
                rule_width: cs(rect).borderLeftWidth,
                rule_shown: cs(rect).display !== 'none' && cs(rect).visibility !== 'hidden',
                dots_hidden: cs(dots).display === 'none',
              };
            }"""
        )
        assert info["rule_width"] != "0px", f"proof bracket rule missing: {info}"
        assert info["rule_shown"], f"proof bracket rule not shown: {info}"
        assert info["dots_hidden"], f"proof dots should be hidden in print: {info}"

    def test_non_proof_border_zone_hidden_under_print(
        self, page: Page, interactive_server: str
    ):
        if page.viewport_size["width"] < 1321:
            page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{interactive_server}/collapsed.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        page.emulate_media(media="print")

        # The sketch is a handrail block but not a proof, so its border-zone goes.
        zone = page.locator(".sketch.hr > .hr-border-zone").first
        assert zone.evaluate("el => getComputedStyle(el).display") == "none"
