"""Math rendering via MathJax.

Covers the bug where typesetMath() failed silently when called without a math
renderer loaded. This happens in Studio when the initial render has no math
(so onload skips MathJax), then a subsequent compile introduces math and
onrender calls typesetMath. typesetMath now loads MathJax on demand when math
elements are present.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def wait_for_rsm(page):
    page.wait_for_function(RSM_READY, timeout=10_000)


def wait_for_math(page):
    """MathJax typesets after __rsmInitialized is set, so wait for its output."""
    page.wait_for_selector("span.math mjx-container", state="attached", timeout=15_000)


class TestMathRendering:
    """Math typesetting in a directly loaded RSM page."""

    def test_inline_math_renders(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/math-basic.html")
        wait_for_rsm(page)
        inline = page.locator("span.math").first
        expect(inline.locator("mjx-container")).to_have_count(1)
        content = inline.text_content()
        assert not content.startswith("\\("), (
            f"Inline math not rendered: {content[:80]}"
        )

    def test_display_math_renders(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/math-basic.html")
        wait_for_rsm(page)
        display = page.locator("div.mathblock").first
        expect(display.locator("mjx-container[display='true']")).to_have_count(1)
        content = display.text_content().strip()
        assert not content.startswith("$$"), (
            f"Display math not rendered: {content[:80]}"
        )

    def test_mathjax_loaded(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/math-basic.html")
        wait_for_rsm(page)
        wait_for_math(page)
        assert page.evaluate("() => window.MathJax.version") == "3.2.2"

    def test_typeset_math_returns_after_layout(
        self, page: Page, interactive_server: str
    ):
        """typesetMath resolves only once the math it was given is typeset, so
        code that measures the page can wait for it."""
        page.goto(f"{interactive_server}/math-basic.html")
        wait_for_rsm(page)
        rendered = page.evaluate("""async () => {
            const libs = await import('/static/libraries.js');
            const span = document.createElement('span');
            span.className = 'math';
            span.textContent = '\\\\(\\\\sqrt{n}\\\\)';
            document.querySelector('.manuscript').appendChild(span);
            await libs.typesetMath(span.parentElement);
            return !!span.querySelector('mjx-container') && span.getBoundingClientRect().width > 0;
        }""")
        assert rendered

    def test_assistive_mathml_present(self, page: Page, interactive_server: str):
        """Screen readers get MathML next to the visual rendering."""
        page.goto(f"{interactive_server}/math-basic.html")
        wait_for_rsm(page)
        wait_for_math(page)
        assert page.locator("span.math mjx-assistive-mml math").count() >= 1


class TestMathOnDemandLoading:
    """Regression: typesetMath must load MathJax on demand when none is loaded.

    Simulates the Studio bug: __rsmInitialized is set on a no-math page, then
    typesetMath is called on a DOM that now contains math elements.
    """

    def test_no_math_page_skips_mathjax(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/no-math.html")
        wait_for_rsm(page)
        assert not page.evaluate("() => !!window.MathJax")

    def test_typeset_math_loads_mathjax_on_demand(
        self, page: Page, interactive_server: str
    ):
        """After initializing on a no-math page, injecting math elements and
        calling typesetMath should load MathJax and render them."""
        page.goto(f"{interactive_server}/no-math.html")
        wait_for_rsm(page)
        assert not page.evaluate("() => !!window.MathJax")

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

        page.evaluate("""async () => {
            const libs = await import('/static/libraries.js');
            const container = document.querySelector('.manuscriptwrapper') || document.body;
            await libs.typesetMath(container);
        }""")

        assert page.evaluate("() => !!window.MathJax.typesetPromise")
        inline_content = page.locator("span.math").first.text_content()
        assert not inline_content.startswith("\\("), (
            f"Inline math not rendered after on-demand load: {inline_content[:80]}"
        )
        assert page.locator("div.mathblock mjx-container").count() == 1

    def test_typeset_math_silent_on_math_less_page(
        self, page: Page, interactive_server: str
    ):
        """Studio's editor recompiles the manuscript on every keystroke and runs
        onrender, then typesetMath, each time. On a math-less document that
        must neither load MathJax nor log anything."""
        messages: list[str] = []
        page.on(
            "console",
            lambda msg: messages.append(msg.text)
            if msg.type in ("warning", "error")
            else None,
        )

        page.goto(f"{interactive_server}/no-math.html")
        wait_for_rsm(page)

        page.evaluate(
            """async () => {
            const libs = await import('/static/libraries.js');
            const container = document.querySelector('.manuscriptwrapper') || document.body;
            await libs.typesetMath(container);
        }"""
        )

        assert not page.evaluate("() => !!window.MathJax")
        assert messages == [], f"typesetMath logged on a math-less page: {messages}"


class TestAnnotatedEquations:
    """MathJax must keep \\class in math so interactive figures can bind to
    parts of an equation. The other html extension commands (\\href, \\cssId,
    \\style) are removed, so they stay untrusted as they were under Temml.
    """

    def test_class_renders_carrying_the_class(
        self, page: Page, interactive_server: str
    ):
        """\\class{lk lk-a}{a} must render an element carrying classes lk lk-a,
        not a red parse error. (The hidden assistive MathML carries the class
        too, so the check looks inside the visual rendering only.)"""
        page.goto(f"{interactive_server}/math-class.html")
        wait_for_rsm(page)

        block = page.locator("#eqn-ann")
        expect(block).to_be_visible()

        expect(page.locator("#eqn-ann mjx-math .lk.lk-a")).to_have_count(1)
        # CHTML draws characters with CSS, so the text is read from the MathML.
        annotated = page.locator("#eqn-ann mjx-assistive-mml .lk.lk-a")
        assert annotated.text_content().strip() == "a"

        text = block.text_content()
        assert "\\class" not in text, f"raw \\class left unrendered: {text[:120]}"
        assert page.locator("#eqn-ann mjx-merror").count() == 0

    def test_class_equation_still_numbered_and_referenceable(
        self, page: Page, interactive_server: str
    ):
        """\\class must not touch numbering or :ref: resolution."""
        page.goto(f"{interactive_server}/math-class.html")
        wait_for_rsm(page)

        ref = page.locator("a.reference[href='#eqn-ann']")
        expect(ref).to_have_count(1)
        assert any(ch.isdigit() for ch in ref.text_content())

    def test_other_html_commands_stay_untrusted(
        self, page: Page, interactive_server: str
    ):
        """\\href must render as an undefined command, never as a link."""
        page.goto(f"{interactive_server}/math-class.html")
        wait_for_rsm(page)

        block = page.locator("#eqn-href")
        expect(block.locator("mjx-container")).to_have_count(1)
        assert "\\href" in block.text_content()
        assert page.locator("#eqn-href mjx-container a").count() == 0
        assert page.locator("#eqn-href mjx-container [href]").count() == 0

    def test_class_survives_notation_rerender(
        self, page: Page, interactive_server: str
    ):
        """Rebinding a notation macro re-renders every equation from its stored
        data-latex. The annotated atom must keep its classes on that path too."""
        page.goto(f"{interactive_server}/math-class.html")
        wait_for_rsm(page)
        expect(page.locator("#eqn-ann mjx-math .lk.lk-a")).to_have_count(1)

        page.evaluate(
            """async () => {
            const n = await import('/static/notation.js');
            await n.reRenderAll(document);
        }"""
        )

        expect(page.locator("#eqn-ann mjx-math .lk.lk-a")).to_have_count(1)
        # CHTML draws characters with CSS, so the text is read from the MathML.
        annotated = page.locator("#eqn-ann mjx-assistive-mml .lk.lk-a")
        assert annotated.text_content().strip() == "a"


class TestWidgetApi:
    """Widgets and figures render their own math through window.rsm."""

    def test_render_math_into_an_element(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/math-basic.html")
        wait_for_rsm(page)
        result = page.evaluate("""async () => {
            const el = document.createElement('span');
            document.querySelector('.manuscript').appendChild(el);
            await window.rsm.renderMath('\\\\class{w}{x}^2', el);
            const first = !!el.querySelector('mjx-math .w');
            await window.rsm.renderMath('\\\\sum_i y_i', el, { display: true });
            return [first, el.querySelectorAll('mjx-container').length,
                    el.querySelector('mjx-container').getAttribute('display')];
        }""")
        assert result == [True, 1, "true"]
