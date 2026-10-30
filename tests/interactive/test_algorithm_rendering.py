"""Algorithm rendering via pseudocode.js.

pseudocode.js typesets the math in an algorithm with MathJax (MathJax.tex2chtml)
when no KaTeX is on the page, so RSM gives it no alias of its own.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

# Every character MathJax drew inside the algorithm has its CSS: CHTML draws a
# character as the ::before content of an mjx-c, which is empty without it.
ALGORITHM_MATH_STYLED = """() => {
    const cs = [...document.querySelectorAll('.ps-root mjx-container mjx-c')];
    return cs.length > 0 && cs.every((c) => {
        const content = getComputedStyle(c, '::before').content;
        return content && content !== 'none' && content !== 'normal';
    });
}"""


def wait_for_rsm(page):
    page.wait_for_function(RSM_READY, timeout=10_000)


class TestAlgorithmRendering:
    """pseudocode.js renders the algorithm block, math included."""

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

    def test_no_katex_alias(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/algorithm.html")
        wait_for_rsm(page)
        expect(page.locator(".ps-root")).to_be_visible(timeout=10_000)
        assert page.evaluate("() => typeof window.katex") == "undefined"

    def test_algorithm_math_is_typeset_and_styled(
        self, page: Page, interactive_server: str
    ):
        page.goto(f"{interactive_server}/algorithm.html")
        wait_for_rsm(page)
        expect(page.locator(".ps-root mjx-container").first).to_be_attached(timeout=10_000)
        page.wait_for_function(ALGORITHM_MATH_STYLED, timeout=10_000)

    def test_algorithm_without_other_math(self, page: Page, interactive_server: str):
        """MathJax loads for an algorithm even when the page has no other math."""
        page.goto(f"{interactive_server}/algorithm-only.html")
        wait_for_rsm(page)
        expect(page.locator(".ps-root mjx-container").first).to_be_attached(timeout=10_000)
        page.wait_for_function(ALGORITHM_MATH_STYLED, timeout=10_000)
