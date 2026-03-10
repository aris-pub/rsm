"""Tests for algorithm rendering via pseudocode.js with the Temml-KaTeX alias.

Covers the fix where pseudocode.js requires window.katex but RSM loads Temml.
The alias in libraries.js (window.katex = window.temml) bridges the gap.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def wait_for_rsm(page):
    page.wait_for_function(RSM_READY, timeout=10_000)


class TestTemmlKatexAlias:
    """Verify that loading Temml also sets window.katex for pseudocode.js."""

    def test_katex_alias_exists(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/algorithm.html")
        wait_for_rsm(page)
        page.wait_for_function("() => !!window.temml", timeout=10_000)
        has_katex = page.evaluate("() => !!window.katex")
        assert has_katex, "window.katex should be set as an alias for window.temml"

    def test_katex_alias_is_temml(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/algorithm.html")
        wait_for_rsm(page)
        page.wait_for_function("() => !!window.temml", timeout=10_000)
        same = page.evaluate("() => window.katex === window.temml")
        assert same, "window.katex should be the exact same object as window.temml"


class TestAlgorithmRendering:
    """Verify pseudocode.js renders the algorithm block."""

    def test_pseudocode_renders(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/algorithm.html")
        wait_for_rsm(page)
        # pseudocode.js replaces the <pre class="pseudocode"> content with
        # rendered output inside a div with class "ps-root"
        rendered = page.locator(".ps-root")
        expect(rendered).to_be_visible(timeout=10_000)

    def test_pseudocode_contains_procedure_name(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/algorithm.html")
        wait_for_rsm(page)
        rendered = page.locator(".ps-root")
        expect(rendered).to_be_visible(timeout=10_000)
        text = rendered.text_content()
        assert "Euclid" in text, f"Rendered algorithm should contain 'Euclid': {text[:200]}"
