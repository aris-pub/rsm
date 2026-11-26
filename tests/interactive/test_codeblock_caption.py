"""The caption of a code block (rsm-hbhi).

A code block with a :caption: is laid out as a figure: the caption, which starts
with the label "Code Block 1.1.", sits under the code, flush with its left edge.
On a page wide enough for the margin column, the caption goes in that column,
level with its block, as the caption of a figure or table does.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

NAME = "codeblock_caption"

_GEOM = """() => {
    const box = (e) => { const b = e.getBoundingClientRect();
        return {l: b.left, t: b.top, r: b.right, b: b.bottom}; };
    const fig = document.querySelector('figure#code-sort');
    const cap = fig.querySelector(':scope > figcaption');
    const label = cap.querySelector('.label');
    return {
        fig: box(fig),
        pre: box(fig.querySelector('pre')),
        cap: box(cap),
        label: box(label),
        labelText: label.textContent,
        text: box(document.querySelector('.manuscript')),
        margin: getComputedStyle(document.documentElement)
            .getPropertyValue('--rsm-margin-on').trim() === '1',
        sw: document.documentElement.scrollWidth,
        cw: document.documentElement.clientWidth,
    };
}"""


def _geom(page: Page, server: str, width: int) -> dict:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{server}/{NAME}.html")
    page.wait_for_function("() => window.__rsmShown === true", timeout=10_000)
    page.evaluate("() => localStorage.clear()")
    page.goto(f"{server}/{NAME}.html", wait_until="load")
    page.wait_for_function("() => window.__rsmShown === true", timeout=10_000)
    page.evaluate("() => document.fonts.ready")
    page.wait_for_timeout(500)
    return page.evaluate(_GEOM)


def test_label_sits_under_the_code(page: Page, interactive_server: str):
    g = _geom(page, interactive_server, 1100)
    assert not g["margin"], g
    assert g["labelText"] == "Code Block 1.1. "
    gap = g["label"]["t"] - g["pre"]["b"]
    assert 0 <= gap <= 40, g
    assert abs(g["label"]["l"] - g["pre"]["l"]) <= 1, g


def test_caption_goes_in_the_margin_column_on_a_wide_page(
    page: Page, interactive_server: str
):
    g = _geom(page, interactive_server, 1440)
    assert g["margin"], g
    assert g["cap"]["l"] >= g["text"]["r"], g
    assert abs(g["cap"]["t"] - g["fig"]["t"]) <= 8, g
    assert g["sw"] <= g["cw"], g
