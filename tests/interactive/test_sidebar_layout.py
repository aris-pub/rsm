"""Page layout around the reader sidebar.

Wide windows: the strip sits in the left margin; the column is centred in the
space right of it when that allows, and moves next to the panel (never under
it) when a view is open. Below 768px the strip is a bottom bar and a view opens
as a sheet.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"
DESKTOP = {"width": 1400, "height": 900}
PHONE = {"width": 375, "height": 812}

_GEOM = """() => {
    const w = document.querySelector('main.manuscriptwrapper').getBoundingClientRect();
    const s = document.querySelector('.rail-strip').getBoundingClientRect();
    const r = document.querySelector('.proof-rail').getBoundingClientRect();
    const d = document.documentElement;
    return {stripRight: Math.round(s.right), panelRight: Math.round(r.right),
            contentLeft: Math.round(w.left), contentRight: Math.round(w.right),
            vw: d.clientWidth, overflowX: d.scrollWidth - d.clientWidth};
}"""


def _load(page: Page, server: str, page_name: str = "sidebar", viewport=DESKTOP) -> None:
    page.set_viewport_size(viewport)
    page.goto(f"{server}/{page_name}.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)


def _open(page: Page, view: str) -> None:
    page.click(f'.rail-strip-btn[data-view="{view}"]')
    page.wait_for_selector(".proof-rail.open", timeout=5_000)
    page.wait_for_timeout(400)  # the column's transition


def test_closed_column_is_centred_when_wide(page: Page, interactive_server: str):
    _load(page, interactive_server, viewport={"width": 1920, "height": 900})
    g = page.evaluate(_GEOM)
    assert g["contentLeft"] >= g["stripRight"], g
    # Centred in the space right of the strip.
    left, right = g["contentLeft"] - g["stripRight"], g["vw"] - g["contentRight"]
    assert abs(left - right) < 12, f"column not centred when wide: {g}"


def test_closed_column_clears_strip_when_narrow(page: Page, interactive_server: str):
    _load(page, interactive_server, viewport={"width": 900, "height": 900})
    g = page.evaluate(_GEOM)
    assert g["contentLeft"] >= g["stripRight"], g
    assert g["overflowX"] <= 1, g


@pytest.mark.parametrize("width", [800, 1100, 1450])
def test_open_panel_pushes_column(page: Page, interactive_server: str, width):
    _load(page, interactive_server, viewport={"width": width, "height": 900})
    _open(page, "contents")
    g = page.evaluate(_GEOM)
    assert g["contentLeft"] >= g["panelRight"], f"the panel covers the text: {g}"
    assert g["overflowX"] <= 1, g


def test_crossing_the_phone_breakpoint(page: Page, interactive_server: str):
    """Narrowing a desktop window turns the strip into the bottom bar (and
    closes the panel rather than covering the page with a sheet); widening
    turns it back."""
    _load(page, interactive_server)
    _open(page, "contents")
    page.set_viewport_size(PHONE)
    page.wait_for_timeout(300)
    assert page.evaluate("() => document.documentElement.classList.contains('rail-phone')")
    assert not page.evaluate("() => document.documentElement.classList.contains('rail-open')")
    expect(page.locator('.rail-strip-btn[data-view="document"]')).to_be_visible()
    expect(page.locator('.rail-strip-btn[data-view="contents"]')).to_be_hidden()
    page.set_viewport_size(DESKTOP)
    page.wait_for_timeout(300)
    expect(page.locator('.rail-strip-btn[data-view="contents"]')).to_be_visible()
    expect(page.locator('.rail-strip-btn[data-view="document"]')).to_be_hidden()


def test_phone_sheet_sits_above_the_bar(page: Page, interactive_server: str):
    _load(page, interactive_server, viewport=PHONE)
    page.click('.rail-strip-btn[data-view="reading"]')
    page.wait_for_selector(".proof-rail.open", timeout=5_000)
    g = page.evaluate(
        "() => ({sheet: document.querySelector('.proof-rail').getBoundingClientRect().bottom,"
        " bar: document.querySelector('.rail-strip').getBoundingClientRect().top})"
    )
    assert g["sheet"] <= g["bar"], g


_GRAPH_FITS = """() => {
    const panel = document.querySelector('.proof-rail').getBoundingClientRect();
    const svg = document.querySelector('.proof-rail .rail-doc-map svg.toc-tree').getBoundingClientRect();
    return {panelTop: panel.top, panelBottom: panel.bottom, svgTop: svg.top, svgBottom: svg.bottom,
            svgLeft: svg.left, svgRight: svg.right, panelLeft: panel.left, panelRight: panel.right};
}"""


@pytest.mark.parametrize("viewport", [{"width": 1280, "height": 800}, PHONE], ids=["desktop", "phone"])
def test_contents_graph_fits_its_panel(page: Page, interactive_server: str, viewport):
    """A tall section graph scales down to fit the panel or sheet; it is never
    cut off at the top or bottom."""
    _load(page, interactive_server, page_name="sidebar_long", viewport=viewport)
    _open(page, "document" if viewport is PHONE else "contents")
    g = page.evaluate(_GRAPH_FITS)
    assert g["svgTop"] >= g["panelTop"] - 1 and g["svgBottom"] <= g["panelBottom"] + 1, g
    assert g["svgLeft"] >= g["panelLeft"] - 1 and g["svgRight"] <= g["panelRight"] + 1, g
