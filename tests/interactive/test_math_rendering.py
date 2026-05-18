"""Regression tests for math rendering via Temml/MathJax.

Covers the bug where typesetMath() fails silently when called without a math
renderer loaded.  This happens in Studio when the initial render has no math
(so onload skips Temml), then a subsequent compile introduces math and
onrender calls typesetMath — which found neither Temml nor MathJax.

The fix: typesetMath() now loads Temml on-demand when math elements are present
but no renderer is available.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def wait_for_rsm(page):
    page.wait_for_function(RSM_READY, timeout=10_000)


class TestMathRendering:
    """Math typesetting in a directly loaded RSM page."""

    def test_inline_math_renders(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/math-basic.html")
        wait_for_rsm(page)
        # Temml replaces the raw \(...\) content with MathML markup
        inline = page.locator("span.math").first
        expect(inline).to_be_visible()
        content = inline.text_content()
        assert not content.startswith("\\("), (
            f"Inline math not rendered: {content[:80]}"
        )

    def test_display_math_renders(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/math-basic.html")
        wait_for_rsm(page)
        display = page.locator("div.mathblock").first
        expect(display).to_be_visible()
        content = display.text_content().strip()
        assert not content.startswith("$$"), (
            f"Display math not rendered: {content[:80]}"
        )

    def test_temml_loaded(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/math-basic.html")
        wait_for_rsm(page)
        has_temml = page.evaluate("() => !!window.temml")
        assert has_temml, "Temml should be loaded for a page with math"


class TestMathOnDemandLoading:
    """Regression: typesetMath must load Temml on-demand when no renderer exists.

    Simulates the Studio bug: __rsmInitialized is set on a no-math page, then
    typesetMath is called on a DOM that now contains math elements.
    """

    def test_no_math_page_skips_temml(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/no-math.html")
        wait_for_rsm(page)
        has_temml = page.evaluate("() => !!window.temml")
        assert not has_temml, "Temml should NOT be loaded for a page without math"

    def test_typeset_math_loads_temml_on_demand(
        self, page: Page, interactive_server: str
    ):
        """After initializing on a no-math page, injecting math elements and
        calling typesetMath should load Temml and render them."""
        page.goto(f"{interactive_server}/no-math.html")
        wait_for_rsm(page)

        # Confirm Temml is not loaded
        assert not page.evaluate("() => !!window.temml")

        # Inject math elements into the DOM
        page.evaluate("""() => {
            const container = document.querySelector('.manuscriptwrapper') || document.body;
            const span = document.createElement('span');
            span.className = 'math';
            span.textContent = '\\\\(2 + 2 = 4\\\\)';
            container.appendChild(span);

            const div = document.createElement('div');
            div.className = 'mathblock';
            div.textContent = '$$ x^2 $$';
            container.appendChild(div);
        }""")

        # Call typesetMath — this should load Temml on-demand and render
        page.evaluate("""async () => {
            const libs = await import('/static/libraries.js');
            const container = document.querySelector('.manuscriptwrapper') || document.body;
            await libs.typesetMath(container);
        }""")

        # Temml should now be loaded
        has_temml = page.evaluate("() => !!window.temml")
        assert has_temml, "typesetMath should have loaded Temml on-demand"

        # Math should be rendered (content replaced)
        inline_content = page.locator("span.math").first.text_content()
        assert not inline_content.startswith("\\("), (
            f"Inline math not rendered after on-demand load: {inline_content[:80]}"
        )

    def test_typeset_math_silent_on_math_less_page(
        self, page: Page, interactive_server: str
    ):
        """Regression: typesetMath must not emit 'Neither temml nor MathJax'
        warnings when there is no math in the document.

        Studio's editor recompiles the manuscript on every keystroke and runs
        onrender → typesetMath each time.  For a math-less document, the
        function previously fell through past the on-demand load (which is
        also gated on math presence) and into the MathJax fallback's
        availability check, logging a warning.  The warning is a false alarm
        — there is no math to typeset — but it spams the console on every
        edit, drowning out real diagnostics.
        """
        warnings: list[str] = []
        page.on(
            "console",
            lambda msg: warnings.append(msg.text)
            if msg.type == "warning" and "Neither temml nor MathJax" in msg.text
            else None,
        )

        page.goto(f"{interactive_server}/no-math.html")
        wait_for_rsm(page)

        # Sanity: no temml on a math-less page
        assert not page.evaluate("() => !!window.temml")

        # Call typesetMath the way onrender would after a recompile.  One
        # call is enough; the bug manifests on every invocation.
        page.evaluate(
            """async () => {
            const libs = await import('/static/libraries.js');
            const container = document.querySelector('.manuscriptwrapper') || document.body;
            await libs.typesetMath(container);
        }"""
        )

        # No "Neither temml nor MathJax ready for typesetting" warnings.
        assert warnings == [], (
            f"typesetMath emitted spurious 'Neither temml nor MathJax' "
            f"warnings on a math-less page: {warnings}"
        )
