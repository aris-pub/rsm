"""The standalone build renders offline with braiid.css, jQuery and tooltipster
JS inlined, so it needs no network for those (rsm-nyg piece 1)."""

import pytest
from playwright.sync_api import Page

import rsm

pytestmark = pytest.mark.interactive

SRC = (
    ":rsm:\n\n# Hello\n\n"
    "A paragraph with a :ref:thm:: link.\n\n"
    ":theorem: {:label: thm}\n  A statement. ::\n\n::"
)


def test_standalone_renders_offline_with_inlined_assets(page: Page, tmp_path):
    html = rsm.build(SRC, handrails=True, lint=False, standalone=True)
    out = tmp_path / "standalone.html"
    out.write_text(html)

    blocked: list[str] = []

    def handle(route):
        url = route.request.url
        if url.startswith(("http://", "https://")):
            blocked.append(url)
            route.abort()
        else:
            route.continue_()

    page.route("**/*", handle)
    page.goto(out.as_uri(), wait_until="load")
    page.wait_for_timeout(500)

    # braiid.css applied from the inline <style>, with no network: a reference
    # link takes braiid's --link-default (blue-700), not the UA default blue.
    link_color = page.eval_on_selector("a.reference", "a => getComputedStyle(a).color")
    assert link_color == "rgb(3, 97, 161)", link_color
    assert (
        page.eval_on_selector(".manuscriptwrapper", "e => getComputedStyle(e).maxWidth")
        != "none"
    )

    # jQuery is inlined and live.
    assert page.evaluate("() => typeof window.jQuery") == "function"

    # None of the inlined libraries were fetched over the network.
    fetched = [
        u
        for u in blocked
        if any(k in u.lower() for k in ("jquery", "braiid", "tooltipster.bundle.js"))
    ]
    assert not fetched, fetched


MATH_SRC = """# Math

Inline $x + y$.

:algorithm:
\\begin{algorithm}
\\caption{Euclid}
\\begin{algorithmic}
\\PROCEDURE{Euclid}{$a, b$}
    \\RETURN $a$
\\ENDPROCEDURE
\\end{algorithmic}
\\end{algorithm}
::
"""


def test_standalone_math_and_pseudocode_use_inlined_libraries(page: Page, tmp_path):
    """MathJax, its fonts and pseudocode.js are inlined, so math and algorithms
    render with no request for them, and pseudocode's KaTeX css is not fetched
    (rsm-nyg.2)."""
    html = rsm.build(MATH_SRC, handrails=True, lint=False, standalone=True)
    out = tmp_path / "math.html"
    out.write_text(html)

    blocked: list[str] = []

    def handle(route):
        url = route.request.url
        if url.startswith(("http://", "https://")):
            blocked.append(url)
            route.abort()
        else:
            route.continue_()

    page.route("**/*", handle)
    page.goto(out.as_uri(), wait_until="load")
    page.wait_for_function(
        "() => document.querySelector('.ps-root') && document.querySelector('span.math mjx-container')",
        timeout=10_000,
    )

    fetched = [
        u
        for u in blocked
        if any(k in u.lower() for k in ("pseudocode", "katex", "mathjax", ".woff"))
    ]
    assert not fetched, fetched
    # MathJax's fonts load from their data URIs.
    page.evaluate("() => document.fonts.ready")
    assert page.evaluate(
        "() => [...document.fonts].some(f => f.family.replace(/\"/g, '') === 'MJXTEX-I' && f.status === 'loaded')"
    )


KEYS_SRC = "# T\n\n## A\n\nFirst paragraph.\n\nSecond paragraph.\n"


def test_standalone_page_has_the_keyboard_shortcuts(page: Page, tmp_path):
    # A standalone page, such as a paper on Press, is read like any other page,
    # so j moves to the next block as it does in a folder build.
    out = tmp_path / "keys.html"
    out.write_text(rsm.build(KEYS_SRC, handrails=True, lint=False, standalone=True))
    page.goto(out.as_uri(), wait_until="load")
    page.wait_for_function("() => window.__rsmShown === true", timeout=10_000)
    assert page.evaluate("() => document.activeElement === document.body")
    page.keyboard.press("j")
    assert page.evaluate("() => document.activeElement !== document.body")


SECTIONS_SRC = "# T\n\n## Alpha\n\nA.\n\n## Beta\n\nB.\n\n## Gamma\n\nC.\n"


def _focused_section(page: Page) -> str:
    return page.evaluate(
        "() => { const s = document.activeElement.closest('.section');"
        " return s ? s.querySelector('h2').textContent : ''; }"
    )


def test_l_goes_forward_and_h_goes_back_as_in_vim(page: Page, tmp_path):
    out = tmp_path / "sections.html"
    out.write_text(rsm.build(SECTIONS_SRC, handrails=True, lint=False, standalone=True))
    page.goto(out.as_uri(), wait_until="load")
    page.wait_for_function("() => window.__rsmShown === true", timeout=10_000)
    page.locator("h2", has_text="Beta").click()
    assert "Beta" in _focused_section(page)
    page.keyboard.press("l")
    assert "Gamma" in _focused_section(page)
    page.keyboard.press("h")
    page.keyboard.press("h")
    assert "Alpha" in _focused_section(page)
