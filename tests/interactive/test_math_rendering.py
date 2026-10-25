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


class TestAnnotatedEquations:
    """Temml must keep \\class in math so interactive figures can bind to parts
    of an equation.  \\class is trust-gated in Temml, so without opting in it
    errors and renders a red temml-error node instead of carrying the class.
    Other trust-gated commands (\\href, \\cssId, ...) must stay untrusted.
    """

    def test_class_renders_carrying_the_class(
        self, page: Page, interactive_server: str
    ):
        """\\class{lk lk-a}{a} must render an element carrying classes lk lk-a,
        not a red parse error."""
        page.goto(f"{interactive_server}/math-class.html")
        wait_for_rsm(page)

        block = page.locator("#eqn-ann")
        expect(block).to_be_visible()

        # The annotated atom carries both classes from \class{lk lk-a}{a}.
        annotated = page.locator("#eqn-ann .lk.lk-a")
        expect(annotated).to_have_count(1)
        assert annotated.text_content().strip() == "a"

        # No leftover raw LaTeX and no trust error.
        text = block.text_content()
        assert "\\class" not in text, f"raw \\class left unrendered: {text[:120]}"
        assert "not trusted" not in text.lower(), (
            f"\\class rendered a trust error: {text[:120]}"
        )
        assert page.locator("#eqn-ann .temml-error").count() == 0

    def test_class_equation_still_numbered_and_referenceable(
        self, page: Page, interactive_server: str
    ):
        """Trusting \\class must not touch numbering or :ref: resolution."""
        page.goto(f"{interactive_server}/math-class.html")
        wait_for_rsm(page)

        ref = page.locator("a.reference[href='#eqn-ann']")
        expect(ref).to_have_count(1)
        # The reference resolved to a number like (1).
        assert any(ch.isdigit() for ch in ref.text_content())

    def test_other_trust_gated_commands_stay_untrusted(
        self, page: Page, interactive_server: str
    ):
        """\\href must not be trusted by the \\class-only predicate: it stays a
        red literal, never a rendered link."""
        page.goto(f"{interactive_server}/math-class.html")
        wait_for_rsm(page)

        block = page.locator("#eqn-href")
        expect(block).to_be_visible()
        # Untrusted \\href is echoed as a red literal, not consumed into a link.
        assert "\\href" in block.text_content()
        assert page.locator("#eqn-href a").count() == 0

    def test_class_survives_notation_rerender(
        self, page: Page, interactive_server: str
    ):
        """Rebinding a notation macro re-renders every equation from its stored
        data-latex. The annotated atom must keep its classes, not revert to a
        red error on that path too."""
        page.goto(f"{interactive_server}/math-class.html")
        wait_for_rsm(page)
        expect(page.locator("#eqn-ann .lk.lk-a")).to_have_count(1)

        page.evaluate(
            """async () => {
            const n = await import('/static/notation.js');
            n.reRenderAll(document);
        }"""
        )

        annotated = page.locator("#eqn-ann .lk.lk-a")
        expect(annotated).to_have_count(1)
        assert annotated.text_content().strip() == "a"

    def test_class_renders_via_mathjax_fallback(
        self, page: Page, interactive_server: str
    ):
        """With Temml blocked, the MathJax fallback (html extension enabled)
        must also carry the class, so both renderers agree."""
        page.route("**/temml*", lambda route: route.abort())
        page.goto(f"{interactive_server}/math-class.html")
        wait_for_rsm(page)

        assert page.evaluate("() => !window.temml && !!window.MathJax")
        # The html extension is in MathJax's active package list (resolved to a
        # flat array after startup).
        assert page.evaluate(
            "() => window.MathJax.config.tex.packages.includes('html')"
        )

        annotated = page.locator("#eqn-ann .lk.lk-a")
        expect(annotated.first).to_be_visible(timeout=15_000)
        assert annotated.count() >= 1
