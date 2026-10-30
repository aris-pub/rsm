"""Interactive tests for reader-rebindable :notation: macros.

The author declares ``\\eig $\\lambda$ ...`` in a :notation: block; the default
must render (lambda), and a reader rebinding (\\eig -> \\mu) must re-render the
math, persist across reloads, and reject invalid LaTeX.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


# MathJax typesets after __rsmInitialized is set. Text checks read the hidden
# assistive MathML, since CHTML draws its characters with CSS.
def _wait_for_math(page: Page) -> None:
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_function(
        "() => [...document.querySelectorAll('span.math, div.mathblock')]"
        ".every((el) => el.querySelector('mjx-container'))",
        timeout=15_000,
    )


def _load(page: Page, server: str) -> None:
    page.goto(f"{server}/notation.html")
    _wait_for_math(page)


def _set_macro(page: Page, macro: str, latex: str):
    return page.evaluate(
        """async ([m, l]) => {
            const n = await import('/static/notation.js');
            const libs = await import('/static/libraries.js');
            const ok = n.setMacro(m, l);
            await libs.mathIdle();
            return ok;
        }""",
        [macro, latex],
    )


def _inline(page: Page) -> str:
    return page.locator("span.math").first.text_content()


def _display(page: Page) -> str:
    return page.locator("div.mathblock").first.text_content()


# The fixture's second inline/display math use the parameterized macro \edges{G}.
def _param_inline(page: Page) -> str:
    return page.locator("span.math").nth(1).text_content()


def _param_display(page: Page) -> str:
    return page.locator("div.mathblock").nth(1).text_content()


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
    _wait_for_math(page)
    assert "μ" in _inline(page), "rebinding should persist via localStorage"


def test_invalid_input_rejected(page: Page, interactive_server: str):
    _load(page, interactive_server)
    assert _set_macro(page, "\\eig", "\\nonexistentcommand") is False
    assert "λ" in _inline(page), "invalid rebind must keep the previous rendering"


def test_parameterized_default_renders(page: Page, interactive_server: str):
    # A parameterized macro \edges $e(#1)$ called as \edges{G} must render e(G),
    # not leak the macro source, in both inline and display math.
    _load(page, interactive_server)
    assert "G" in _param_inline(page) and "edges" not in _param_inline(page)
    assert "G" in _param_display(page) and "edges" not in _param_display(page)


def test_parameterized_rebind_accepted_and_updates(page: Page, interactive_server: str):
    # Regression (the validator rendered the value standalone, so any value with
    # #1 was rejected): rebinding a parameterized macro to another parameterized
    # value must validate, be accepted, and re-render every call site.
    _load(page, interactive_server)
    assert _set_macro(page, "\\edges", "\\lvert E(#1)\\rvert") is True
    out = _param_inline(page)
    assert "E" in out and "G" in out, "rebound \\edges{G} should render |E(G)|"
    assert "e(G)" not in _param_inline(page).replace(" ", "")


def test_parameterized_default_is_valid(page: Page, interactive_server: str):
    # The parameterized default itself must pass validation (it previously failed
    # because #1 cannot render outside a macro call), so re-applying it is a no-op
    # accepted, not a rejection.
    _load(page, interactive_server)
    assert _set_macro(page, "\\edges", "e(#1)") is True


def test_parameterized_invalid_still_rejected(page: Page, interactive_server: str):
    # The fix must not blanket-accept: a genuinely broken parameterized body is
    # still rejected and the previous rendering is kept.
    _load(page, interactive_server)
    assert _set_macro(page, "\\edges", "\\nope{#1}") is False
    assert "G" in _param_inline(page)


def test_locate_skips_hidden_uses(page: Page, interactive_server: str):
    # Regression: the "locate" bullseye scrolls to the nearest occurrence, but a
    # display:none use (collapsed proofs, hidden source/static copies) reports a
    # zero box at top 0, which could beat a real but off-screen use and make
    # locate scroll to nothing ("works only sometimes"). It must flash a visible
    # use. sidebar.html carries the rail + notation panel (the \eig macro).
    if page.viewport_size["width"] < 768:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{interactive_server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_timeout(800)
    page.click('.rail-strip-btn[data-view="notation"]')
    # Deterministic bug setup: hide every real \eig use (so the only non-zero-box
    # candidate is one we append far down the page). Pre-fix, a hidden use (zero
    # box, distance == half the viewport) beats the far real one and locate flashes
    # nothing; post-fix the zero-box ones are skipped and the real one wins.
    page.evaluate(
        """() => {
            const re = /\\\\eig(?![a-zA-Z])/;
            document.querySelectorAll('span.math[data-latex], div.mathblock[data-latex]')
                .forEach((el) => { if (re.test(el.dataset.latex)) el.style.display = 'none'; });
            const v = document.createElement('span');
            v.className = 'math';
            v.dataset.latex = '\\\\eig';
            v.textContent = 'lambda';
            v.style.display = 'inline-block';
            document.querySelector('.manuscript').appendChild(v);
            window.scrollTo(0, 0);
        }"""
    )
    page.locator('.proof-rail .rail-notation-locate').first.click()
    page.wait_for_timeout(700)
    box = page.evaluate(
        """() => {
            const el = document.querySelector('.notation-located');
            if (!el) return null;
            const r = el.getBoundingClientRect();
            return { w: r.width, h: r.height };
        }"""
    )
    assert box is not None, "locate should flash a use"
    assert box["w"] > 0 and box["h"] > 0, "locate must flash a visible use, not a hidden one"


def test_notation_renders_without_errors(page: Page, interactive_server: str):
    """The author's :notation: reaches MathJax: no TeX error and no undefined
    command (MathJax draws those as red text) anywhere in the math."""
    _load(page, interactive_server)
    assert page.locator("mjx-container mjx-merror").count() == 0
    assert page.locator("mjx-container mjx-mtext[style*='color: red']").count() == 0

