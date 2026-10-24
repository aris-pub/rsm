"""Regression for rsm-944: the dark theme must apply from the OS setting with
no JavaScript.

Dark colors used to live only under a .dark-theme class added by an inline
script, so with scripting off a reader on a dark system got a light page. After
the light-dark() migration the page follows prefers-color-scheme through CSS
alone. JavaScript is disabled here (so page.evaluate is unavailable), and the
page background is sampled from a screenshot corner: body sets
`background: var(--surface-page)`, so the corners show the themed surface.
"""

from io import BytesIO

import pytest
from PIL import Image
from playwright.sync_api import Browser

pytestmark = pytest.mark.interactive


def _corner_luminance(png: bytes) -> float:
    img = Image.open(BytesIO(png)).convert("RGB")
    r, g, b = img.getpixel((6, 6))
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255


def _shot(browser: Browser, server: str, scheme: str) -> bytes:
    ctx = browser.new_context(java_script_enabled=False, color_scheme=scheme)
    try:
        page = ctx.new_page()
        page.goto(f"{server}/basic.html")
        page.wait_for_load_state("load")
        return page.screenshot()
    finally:
        ctx.close()


def test_dark_os_without_js_renders_dark(browser: Browser, interactive_server: str):
    light = _corner_luminance(_shot(browser, interactive_server, "light"))
    dark = _corner_luminance(_shot(browser, interactive_server, "dark"))
    assert dark < light - 0.2, (
        f"page background did not darken from the OS setting without JS "
        f"(light corner {light:.3f}, dark corner {dark:.3f})"
    )
