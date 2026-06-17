"""Interactive tests for reader-rebindable :notation: macros.

The author declares ``\\eig $\\lambda$ ...`` in a :notation: block; the default
must render (lambda), and a reader rebinding (\\eig -> \\mu) must re-render the
math, persist across reloads, and reject invalid LaTeX.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _load(page: Page, server: str) -> None:
    page.goto(f"{server}/notation.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _set_macro(page: Page, macro: str, latex: str):
    return page.evaluate(
        """async ([m, l]) => {
            const n = await import('/static/notation.js');
            return n.setMacro(m, l);
        }""",
        [macro, latex],
    )


def _inline(page: Page) -> str:
    return page.locator("span.math").first.text_content()


def _display(page: Page) -> str:
    return page.locator("div.mathblock").first.text_content()


def test_default_notation_renders(page: Page, interactive_server: str):
    _load(page, interactive_server)
    assert "λ" in _inline(page), "default \\eig should render as lambda (inline)"
    assert "λ" in _display(page), "default \\eig should render as lambda (display)"


def test_rebind_updates_math(page: Page, interactive_server: str):
    _load(page, interactive_server)
    assert _set_macro(page, "\\eig", "\\mu") is True
    assert "μ" in _inline(page), "rebound \\eig should render as mu (inline)"
    assert "μ" in _display(page), "rebound \\eig should render as mu (display)"
    assert "λ" not in _inline(page)


def test_rebind_persists_across_reload(page: Page, interactive_server: str):
    _load(page, interactive_server)
    assert _set_macro(page, "\\eig", "\\mu") is True
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    assert "μ" in _inline(page), "rebinding should persist via localStorage"


def test_invalid_input_rejected(page: Page, interactive_server: str):
    _load(page, interactive_server)
    assert _set_macro(page, "\\eig", "\\nonexistentcommand") is False
    assert "λ" in _inline(page), "invalid rebind must keep the previous rendering"


def test_mathjax_fallback_honors_notation(page: Page, interactive_server: str):
    """When Temml is unavailable, the author's :notation: must still render via
    MathJax with no author-side change: the same macros reach tex.macros."""
    page.route("**/temml*", lambda route: route.abort())
    _load(page, interactive_server)

    # Temml failed; MathJax took over.
    assert page.evaluate("() => !window.temml && !!window.MathJax")
    # The author's notation reached MathJax's macro table unchanged.
    assert page.evaluate("() => window.MathJax.config.tex.macros.eig") == "\\lambda"
    # And the math rendered without an undefined-macro error.
    page.wait_for_selector("span.math mjx-container", timeout=15_000)
    assert page.locator("span.math mjx-container mjx-merror").count() == 0
