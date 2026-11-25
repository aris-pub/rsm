"""The margin column on a page built without the sidebar (rsm-1rmd).

When the window is wide enough, asides and captions go in the margin column, as
they do on pages built with the sidebar. The text column keeps its width, and
the text column plus the margin column are centered together in the window. The
column turns on when the page fits with its usual side padding on each side,
that is when the window is at least the Reading measure plus the gap and the
column (17rem) wide. braiid.css decides this with media queries and shows the
result as --rsm-margin-on on <html>.
"""

import json

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

NAME = "margin_plain"
RSM_READY = (
    "() => window.__rsmShown === true && !!document.querySelector("
    "'a.aside-phrase[aria-controls]')"
)

# The narrowest window with the margin column, for each Reading measure:
# the measure (52, 54 or 68rem) plus the gap and the column (17rem), at 16px.
THRESHOLDS = {"narrow": 1104, "normal": 1136, "wide": 1360}

_GEOM = """() => {
    const box = (e) => { const b = e.getBoundingClientRect();
        return {l: b.left, t: b.top, r: b.right, b: b.bottom, w: b.width, h: b.height}; };
    const aside = document.getElementById('bip');
    const marker = document.getElementById('call-bip');
    const fig = document.querySelector('figure#fig-a');
    const tab = document.querySelector('.table-wrapper:has(> #tab-a)');
    const cap = (b) => b.querySelector(':scope > figcaption');
    const html = document.documentElement;
    return {
        vw: html.clientWidth,
        sw: html.scrollWidth,
        on: getComputedStyle(html).getPropertyValue('--rsm-margin-on').trim(),
        sidebar: html.classList.contains('rsm-margin'),
        text: box(document.querySelector('.manuscript')),
        aside: box(aside),
        shown: getComputedStyle(aside).display !== 'none',
        expanded: marker.getAttribute('aria-expanded'),
        marker: box(marker),
        fig: box(fig), figCap: box(cap(fig)),
        tab: box(tab), tabCap: box(cap(tab)),
    };
}"""


def _settle(page: Page, ms: int = 500):
    page.evaluate("() => document.fonts.ready")
    page.wait_for_timeout(ms)


def _load(page: Page, server: str, width: int, measure: str | None = None):
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{server}/{NAME}.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    prefs = json.dumps({"measure": measure} if measure else {})
    page.evaluate(
        "(p) => { localStorage.clear(); localStorage.setItem('rsm-reading', p); }",
        prefs,
    )
    page.goto(f"{server}/{NAME}.html", wait_until="load")
    page.wait_for_function(RSM_READY, timeout=10_000)
    _settle(page)


def _geom(page: Page) -> dict:
    return page.evaluate(_GEOM)


def _assert_on(g: dict):
    assert g["on"] == "1", g
    assert not g["sidebar"], g
    assert g["shown"], g
    assert g["expanded"] is None, g
    assert g["aside"]["l"] >= g["text"]["r"], f"aside is not right of the text: {g}"
    for cap, block in (("figCap", "fig"), ("tabCap", "tab")):
        assert g[cap]["l"] >= g["text"]["r"], f"{cap} is not in the margin: {g}"
        assert abs(g[cap]["t"] - g[block]["t"]) <= 2, (
            f"{cap} is not level with its block: {g}"
        )
    assert g["sw"] <= g["vw"], g


def _assert_off(g: dict):
    assert g["on"] != "1", g
    assert not g["shown"], g
    assert g["expanded"] == "false", g
    for cap, block in (("figCap", "fig"), ("tabCap", "tab")):
        assert g[cap]["t"] >= g[block]["t"] + 10, f"{cap} is not under its block: {g}"
        assert g[cap]["r"] <= g["text"]["r"] + 1, g
    assert g["sw"] <= g["vw"], g


def test_aside_in_margin_level_with_its_phrase(page: Page, interactive_server: str):
    _load(page, interactive_server, 1440)
    g = _geom(page)
    _assert_on(g)
    assert abs(g["aside"]["t"] - g["marker"]["t"]) <= 2, g


def test_text_and_margin_centered_together(page: Page, interactive_server: str):
    _load(page, interactive_server, 1440)
    g = _geom(page)
    _assert_on(g)
    rem = 16
    # The column starts one gap (2rem) right of the text and is 15rem wide.
    assert abs(g["aside"]["l"] - (g["text"]["r"] + 2 * rem)) <= 2, g
    assert abs(g["aside"]["w"] - 15 * rem) <= 2, g
    left = g["text"]["l"]
    right = g["vw"] - (g["text"]["r"] + 17 * rem)
    assert abs(left - right) <= 2, f"left {left}, right {right}: {g}"


def test_text_column_keeps_its_width(page: Page, interactive_server: str):
    # 1100px: below the threshold, but at the same root size (16px from 1024px).
    _load(page, interactive_server, 1100)
    narrow = _geom(page)
    _load(page, interactive_server, 1440)
    wide = _geom(page)
    _assert_off(narrow)
    _assert_on(wide)
    assert abs(narrow["text"]["w"] - wide["text"]["w"]) <= 1, (narrow, wide)


@pytest.mark.parametrize("measure", ["narrow", "normal", "wide"])
def test_threshold_per_measure(page: Page, interactive_server: str, measure):
    at = THRESHOLDS[measure]
    _load(page, interactive_server, at, measure)
    _assert_on(_geom(page))
    _load(page, interactive_server, at - 1, measure)
    _assert_off(_geom(page))


def test_default_measure_without_a_stored_choice(page: Page, interactive_server: str):
    _load(page, interactive_server, THRESHOLDS["normal"])
    _assert_on(_geom(page))
    _load(page, interactive_server, THRESHOLDS["normal"] - 1)
    _assert_off(_geom(page))


def test_measure_change_switches_the_column_live(page: Page, interactive_server: str):
    _load(page, interactive_server, 1200)
    _assert_on(_geom(page))
    page.evaluate(
        "() => document.documentElement.setAttribute('data-reading-measure', 'wide')"
    )
    _settle(page)
    _assert_off(_geom(page))
    page.evaluate(
        "() => document.documentElement.setAttribute('data-reading-measure', 'normal')"
    )
    _settle(page)
    _assert_on(_geom(page))


def test_window_resize_switches_the_column_live(page: Page, interactive_server: str):
    _load(page, interactive_server, 1440)
    _assert_on(_geom(page))
    page.set_viewport_size({"width": 1000, "height": 900})
    _settle(page)
    _assert_off(_geom(page))
    page.set_viewport_size({"width": 1440, "height": 900})
    _settle(page)
    _assert_on(_geom(page))


def test_phrase_opens_the_aside_below_the_threshold(
    page: Page, interactive_server: str
):
    _load(page, interactive_server, 1000)
    page.click("#call-bip")
    _settle(page, 200)
    g = _geom(page)
    assert g["shown"], g
    assert g["expanded"] == "true", g


def test_phone_has_no_margin(page: Page, interactive_server: str):
    _load(page, interactive_server, 375)
    _assert_off(_geom(page))


def test_print_has_no_margin(page: Page, interactive_server: str):
    _load(page, interactive_server, 1440)
    page.emulate_media(media="print")
    _settle(page, 300)
    g = _geom(page)
    assert g["on"] != "1", g
    for cap in ("figCap", "tabCap"):
        assert g[cap]["r"] <= g["text"]["r"] + 1, g


def test_without_js_the_page_is_as_before(browser, interactive_server: str):
    """Without scripts nothing places items in the column, so the text column
    stays centered and every aside and caption stays under its block."""
    ctx = browser.new_context(
        java_script_enabled=False, viewport={"width": 1440, "height": 900}
    )
    page = ctx.new_page()
    page.goto(f"{interactive_server}/{NAME}.html")
    page.wait_for_timeout(300)
    g = _geom(page)
    ctx.close()
    assert g["on"] != "1", g
    left = g["text"]["l"]
    right = g["vw"] - g["text"]["r"]
    assert abs(left - right) <= 2, f"text is not centered: left {left}, right {right}"
    assert g["shown"], g
    assert g["aside"]["t"] >= g["marker"]["b"], f"aside is not under its phrase: {g}"
    assert g["aside"]["r"] <= g["text"]["r"] + 1, g
    for cap, block in (("figCap", "fig"), ("tabCap", "tab")):
        assert g[cap]["t"] >= g[block]["t"] + 10, f"{cap} is not under its block: {g}"
        assert g[cap]["r"] <= g["text"]["r"] + 1, g


_SIMPLE = """() => {
    const html = document.documentElement;
    const b = document.querySelector('.manuscript').getBoundingClientRect();
    const cap = document.querySelector('.table-wrapper > figcaption');
    const tab = document.querySelector('.table-wrapper');
    return {
        vw: html.clientWidth,
        on: getComputedStyle(html).getPropertyValue('--rsm-margin-on').trim(),
        text: {l: b.left, r: b.right, w: b.width},
        cap: cap && cap.getBoundingClientRect().toJSON(),
        tab: tab.getBoundingClientRect().toJSON(),
    };
}"""


def _load_simple(page: Page, server: str, name: str, width: int) -> dict:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{server}/{name}.html")
    page.wait_for_function("() => window.__rsmShown === true", timeout=10_000)
    page.evaluate("() => localStorage.clear()")
    page.goto(f"{server}/{name}.html", wait_until="load")
    page.wait_for_function("() => window.__rsmShown === true", timeout=10_000)
    _settle(page)
    return page.evaluate(_SIMPLE)


def test_page_without_asides_or_captions_stays_centered(
    page: Page, interactive_server: str
):
    g = _load_simple(page, interactive_server, "margin_none", 1440)
    assert g["on"] != "1", g
    left = g["text"]["l"]
    right = g["vw"] - g["text"]["r"]
    assert abs(left - right) <= 2, f"text is not centered: left {left}, right {right}"


def test_page_with_only_a_caption_gets_the_column(page: Page, interactive_server: str):
    g = _load_simple(page, interactive_server, "margin_caption_only", 1440)
    assert g["on"] == "1", g
    assert g["cap"]["left"] >= g["text"]["r"], f"caption is not in the margin: {g}"
    assert abs(g["cap"]["top"] - g["tab"]["top"]) <= 2, g
    left = g["text"]["l"]
    right = g["vw"] - (g["text"]["r"] + 17 * 16)
    assert abs(left - right) <= 2, f"left {left}, right {right}: {g}"
