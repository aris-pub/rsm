"""rsm-fv2: the handrail Source modal has dark colors in every dark state and
light colors in the light state, with readable text in each.

The modal is built by handrails.js, so it exists only with JavaScript on. The
three theme states are: no stored choice on a dark OS (no theme class, the
colors come from light-dark() and the OS), a stored dark choice on a light OS
(.dark-theme), and a stored light choice on a dark OS (.light-theme).
"""

import re

import pytest
from playwright.sync_api import Browser

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"

STATES = [
    pytest.param("dark", None, "dark", id="dark-os-no-class"),
    pytest.param("light", "dark", "dark", id="explicit-dark-theme"),
    pytest.param("dark", "light", "light", id="explicit-light-theme"),
]


def _channel(c: float) -> float:
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(rgb: str) -> float:
    r, g, b = (float(x) for x in re.findall(r"[\d.]+", rgb)[:3])
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def _contrast(a: str, b: str) -> float:
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _modal_colors(browser: Browser, server: str, os_scheme: str, stored):
    # reduced_motion makes the hover background apply with no transition.
    ctx = browser.new_context(color_scheme=os_scheme, reduced_motion="reduce")
    if stored is not None:
        ctx.add_init_script(
            "try { localStorage.setItem('rsm-reading', JSON.stringify({theme: '"
            + stored
            + "'})); } catch (e) {}"
        )
    try:
        page = ctx.new_page()
        page.goto(f"{server}/basic.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        hr = page.locator(".theorem.hr").first
        hr.scroll_into_view_if_needed()
        hr.hover()
        hr.locator(".hr-border-dots").first.click()
        page.locator('#hr-menu-singleton [data-role="code"]').click()
        page.locator(".rsm-source-modal").wait_for(state="visible")
        page.locator(".rsm-source-modal .copy-source").hover()
        # Even a reduced-motion transition finishes only on a later frame.
        page.evaluate(
            "() => new Promise(r => requestAnimationFrame(() =>"
            " requestAnimationFrame(r)))"
        )
        return page.evaluate(
            "() => { const cs = (s) => getComputedStyle(document.querySelector(s));"
            " return {"
            " cls: document.documentElement.className,"
            " body: cs('.rsm-source-modal-body').backgroundColor,"
            " pre: cs('.rsm-source-modal-body pre').color,"
            " btnBg: cs('.rsm-source-modal .copy-source').backgroundColor,"
            " btnFg: cs('.rsm-source-modal .copy-source').color }; }"
        )
    finally:
        ctx.close()


@pytest.mark.parametrize("os_scheme,stored,expected", STATES)
def test_source_modal_body_matches_theme(
    browser: Browser, interactive_server: str, os_scheme, stored, expected
):
    c = _modal_colors(browser, interactive_server, os_scheme, stored)
    lum = _luminance(c["body"])
    if expected == "dark":
        assert lum < 0.1, f"modal body is not dark: {c}"
    else:
        assert lum > 0.6, f"modal body is not light: {c}"
    assert _contrast(c["pre"], c["body"]) >= 4.5, f"source text contrast: {c}"


@pytest.mark.parametrize("os_scheme,stored,expected", STATES)
def test_source_modal_button_hover_matches_theme(
    browser: Browser, interactive_server: str, os_scheme, stored, expected
):
    c = _modal_colors(browser, interactive_server, os_scheme, stored)
    lum = _luminance(c["btnBg"])
    if expected == "dark":
        assert lum < 0.1, f"hovered button background is not dark: {c}"
    else:
        assert lum > 0.6, f"hovered button background is not light: {c}"
    assert _contrast(c["btnFg"], c["btnBg"]) >= 3, f"hovered icon contrast: {c}"
