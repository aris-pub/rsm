"""rsm-944: with JavaScript on, the theme has three states. A stored choice
forces light or dark regardless of the OS setting; no stored choice follows the
OS. The boot script sets .light-theme / .dark-theme / neither, and CSS
color-scheme + light-dark() resolve the colors.
"""

import pytest
from playwright.sync_api import Browser

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _luminance(rgb: str) -> float:
    import re

    r, g, b = (float(x) for x in re.findall(r"[\d.]+", rgb)[:3])
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255


def _state(browser: Browser, server: str, os_scheme: str, stored_theme):
    ctx = browser.new_context(color_scheme=os_scheme)
    if stored_theme is not None:
        ctx.add_init_script(
            "try { localStorage.setItem('rsm-reading', JSON.stringify({theme: '"
            + stored_theme
            + "'})); } catch (e) {}"
        )
    try:
        page = ctx.new_page()
        page.goto(f"{server}/basic.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        return page.evaluate(
            "() => ({"
            " dark: document.documentElement.classList.contains('dark-theme'),"
            " light: document.documentElement.classList.contains('light-theme'),"
            " bg: getComputedStyle(document.body).backgroundColor })"
        )
    finally:
        ctx.close()


def test_stored_light_overrides_dark_os(browser: Browser, interactive_server: str):
    s = _state(browser, interactive_server, "dark", "light")
    assert s["light"] and not s["dark"], s
    assert _luminance(s["bg"]) > 0.5, f"stored-light on dark OS is not light: {s}"


def test_stored_dark_overrides_light_os(browser: Browser, interactive_server: str):
    s = _state(browser, interactive_server, "light", "dark")
    assert s["dark"] and not s["light"], s
    assert _luminance(s["bg"]) < 0.2, f"stored-dark on light OS is not dark: {s}"


def test_no_preference_follows_dark_os(browser: Browser, interactive_server: str):
    s = _state(browser, interactive_server, "dark", None)
    assert not s["dark"] and not s["light"], f"expected no theme class: {s}"
    assert _luminance(s["bg"]) < 0.2, f"no-pref on dark OS did not follow OS: {s}"
