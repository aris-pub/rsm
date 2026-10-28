"""Captions in the right-hand margin column (rsm-coj).

With room for a 15rem column beside the text (after the sidebar strip, any open
panel, at the current Reading width), every caption (figure, widget, video,
table) sits in that column, top-aligned with its block, unboxed. Without room
the same caption is stacked under its block. sidebar.js shows which by one
class on <html> (rsm-margin), and margin.js places the items, pushing one down
when it would overlap the one above.

The caption's handrail is never drawn in the margin: it stays in the left
gutter beside the block, spanning the block's height, hidden at rest and shown
on hover or focus of the block or the caption.
"""

import re
import shutil
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

import rsm

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"
FIXTURES = Path(__file__).parent / "fixtures"

# The four kinds of captioned block in the fixture, by the selector of the
# block that owns the caption, and the word its rail menu is labelled with.
KINDS = {
    "figure": ("figure#fig-a", "Figure"),
    "table": (".table-wrapper:has(> #tab-a)", "Table"),
    "widget": ("figure#wid-a", "Widget"),
    "video": ("figure#vid-a", "Video"),
}
ALL_BLOCKS = [
    "figure#fig-a",
    "figure#fig-b",
    "figure#fig-c",
    ".table-wrapper:has(> #tab-a)",
    "figure#wid-a",
    "figure#vid-a",
    ".table-wrapper:has(> #tab-wide)",
]

_GEOM = """(sel) => {
    const block = document.querySelector(sel);
    const cap = block.querySelector(':scope > figcaption');
    const box = (e) => { const b = e.getBoundingClientRect();
        return {l: b.left, t: b.top, r: b.right, b: b.bottom, w: b.width, h: b.height}; };
    // The block's own content: everything in it but the caption, without the
    // gutter zones of the figure's layout-only handrail.
    const parts = [...block.children].filter((c) => c.tagName !== 'FIGCAPTION')
        .map((c) => c.matches('.hr') ? c.querySelector(':scope > .hr-content-zone') : c)
        .map((c) => c.getBoundingClientRect()).filter((b) => b.height);
    const body = {l: Math.min(...parts.map((b) => b.left)), t: Math.min(...parts.map((b) => b.top)),
        r: Math.max(...parts.map((b) => b.right)), b: Math.max(...parts.map((b) => b.bottom))};
    body.w = body.r - body.l; body.h = body.b - body.t;
    const zone = cap.querySelector(':scope > .hr-border-zone');
    const para = document.querySelector('.manuscript .paragraph.hr > .hr-border-zone');
    return {
        block: box(block), cap: box(cap), body, rail: box(zone),
        railOpacity: +getComputedStyle(zone).opacity,
        paraRailLeft: para.getBoundingClientRect().left,
        text: box(block.closest('.manuscript')),
        margin: document.documentElement.classList.contains('rsm-margin'),
    };
}"""

_PAGE = """() => ({
    sw: document.documentElement.scrollWidth,
    cw: document.documentElement.clientWidth,
    iw: window.innerWidth,
    margin: document.documentElement.classList.contains('rsm-margin'),
})"""


def _load(
    page: Page,
    server: str,
    width: int,
    height: int = 900,
    name: str = "margin_captions",
):
    page.set_viewport_size({"width": width, "height": height})
    page.goto(f"{server}/{name}.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    _settle(page)


def _settle(page: Page, ms: int = 500):
    # Images, fonts and the column's slide (0.22s) settle, then the margin pass.
    page.evaluate("() => document.fonts.ready")
    page.wait_for_timeout(ms)


def _geom(page: Page, sel: str) -> dict:
    return page.evaluate(_GEOM, sel)


def _rest(page: Page):
    page.mouse.move(2, 2)
    page.evaluate("() => document.activeElement && document.activeElement.blur()")
    page.wait_for_timeout(150)


def _toggle_panel(page: Page, view: str = "contents"):
    page.click(f'.rail-strip-btn[data-view="{view}"]')
    _settle(page, 600)


def _force_theme(page: Page, theme: str):
    page.evaluate(
        "(t) => { const c = document.documentElement.classList;"
        " c.remove('light-theme', 'dark-theme'); c.add(t + '-theme'); }",
        theme,
    )
    page.wait_for_timeout(400)


def _assert_in_margin(g: dict, tol: float = 8):
    assert g["margin"], g
    assert g["cap"]["l"] >= g["text"]["r"], f"caption is not right of the text: {g}"
    assert abs(g["cap"]["t"] - g["block"]["t"]) <= tol, (
        f"caption not level with its block: {g}"
    )


def _assert_stacked(g: dict):
    assert not g["margin"], g
    assert (
        g["cap"]["l"] >= g["block"]["l"] - 1 and g["cap"]["r"] <= g["block"]["r"] + 1
    ), g
    gap = g["cap"]["t"] - g["body"]["b"]
    assert -1 <= gap <= 40, f"caption is not directly under its block: {g}"


# ---- with room ------------------------------------------------------------


@pytest.mark.parametrize("kind", list(KINDS))
def test_caption_in_margin_with_room(page: Page, interactive_server: str, kind):
    _load(page, interactive_server, 1440)
    _assert_in_margin(_geom(page, KINDS[kind][0]))


def test_page_never_scrolls_sideways_with_margin(page: Page, interactive_server: str):
    _load(page, interactive_server, 1440)
    p = page.evaluate(_PAGE)
    assert p["margin"], p
    assert p["sw"] == p["iw"], p


def test_wide_table_caption_in_margin_and_no_page_scroll(
    page: Page, interactive_server: str
):
    """A table wider than the text scrolls inside its own box. Its caption is
    still in the margin, level with the table's top, and the page does not
    scroll sideways."""
    _load(page, interactive_server, 1440)
    sel = ".table-wrapper:has(> #tab-wide)"
    _assert_in_margin(_geom(page, sel))
    box = page.eval_on_selector(sel, "e => ({sw: e.scrollWidth, cw: e.clientWidth})")
    assert box["sw"] > box["cw"], box
    page.eval_on_selector(sel, "e => { e.scrollLeft = 9999; }")
    page.wait_for_timeout(100)
    p = page.evaluate(_PAGE)
    assert p["sw"] == p["iw"], p
    _assert_in_margin(_geom(page, sel))


@pytest.mark.parametrize("width", [1440, 1920])
def test_margin_items_never_overlap(page: Page, interactive_server: str, width):
    _load(page, interactive_server, width)
    caps = [_geom(page, s)["cap"] for s in ALL_BLOCKS]
    caps.sort(key=lambda c: c["t"])
    for a, b in zip(caps, caps[1:], strict=False):
        assert b["t"] >= a["b"], f"margin captions overlap: {a} {b}"


def test_long_caption_pushes_the_next_one_down(page: Page, interactive_server: str):
    """fig-b's caption is far taller than fig-b, and fig-c follows right after,
    so fig-c's caption cannot sit level with fig-c: it is pushed below."""
    _load(page, interactive_server, 1440)
    b = _geom(page, "figure#fig-b")
    c = _geom(page, "figure#fig-c")
    _assert_in_margin(b)
    assert b["cap"]["b"] > c["block"]["t"], (
        "fixture: fig-b's caption should reach past fig-c's top"
    )
    assert c["cap"]["t"] >= b["cap"]["b"], (b, c)
    assert c["cap"]["t"] > c["block"]["t"] + 8, c
    # Pushed down, but not far: one small gap below the item above.
    assert c["cap"]["t"] - b["cap"]["b"] < 24, (b, c)


# ---- the live switch --------------------------------------------------------


def test_panel_open_switches_to_stacked_and_back(page: Page, interactive_server: str):
    _load(page, interactive_server, 1440)
    page.evaluate("() => { window.__noReload = true; }")
    _assert_in_margin(_geom(page, "figure#fig-a"))

    _toggle_panel(page)
    assert page.evaluate(
        "() => document.documentElement.classList.contains('rail-open')"
    )
    for sel in ALL_BLOCKS:
        _assert_stacked(_geom(page, sel))
    p = page.evaluate(_PAGE)
    assert p["sw"] <= p["cw"], p

    _toggle_panel(page)
    for kind in KINDS.values():
        _assert_in_margin(_geom(page, kind[0]))
    assert page.evaluate("() => window.__noReload === true"), "the page reloaded"


def test_panel_open_keeps_margin_when_there_is_room(
    page: Page, interactive_server: str
):
    """On a very wide window the column fits even beside the open panel."""
    _load(page, interactive_server, 1920)
    _toggle_panel(page)
    _assert_in_margin(_geom(page, "figure#fig-a"))
    p = page.evaluate(_PAGE)
    assert p["sw"] == p["iw"], p


def test_reading_width_switches_live(page: Page, interactive_server: str):
    """At 1700px with the Reading panel open the column fits at the normal
    width but not at the wide one. Choosing Wide stacks the captions, choosing
    Normal again puts them back, without a reload."""
    _load(page, interactive_server, 1700)
    page.evaluate("() => { window.__noReload = true; }")
    _toggle_panel(page, "reading")
    _assert_in_margin(_geom(page, "figure#fig-a"))

    page.click('.reading-row[data-control="measure"] .reading-opt[data-value="wide"]')
    _settle(page, 600)
    assert (
        page.evaluate("() => document.documentElement.dataset.readingMeasure") == "wide"
    )
    for sel in ALL_BLOCKS:
        _assert_stacked(_geom(page, sel))

    page.click('.reading-row[data-control="measure"] .reading-opt[data-value="normal"]')
    _settle(page, 600)
    _assert_in_margin(_geom(page, "figure#fig-a"))
    assert page.evaluate("() => window.__noReload === true"), "the page reloaded"


def test_window_resize_switches_live(page: Page, interactive_server: str):
    _load(page, interactive_server, 1440)
    _assert_in_margin(_geom(page, "figure#fig-a"))
    page.set_viewport_size({"width": 1200, "height": 900})
    _settle(page)
    _assert_stacked(_geom(page, "figure#fig-a"))
    page.set_viewport_size({"width": 1440, "height": 900})
    _settle(page)
    _assert_in_margin(_geom(page, "figure#fig-a"))


# ---- without room -----------------------------------------------------------


@pytest.mark.parametrize("width", [375, 1024])
@pytest.mark.parametrize("sel", ALL_BLOCKS)
def test_stacked_under_block_without_room(
    page: Page, interactive_server: str, width, sel
):
    _load(page, interactive_server, width)
    _assert_stacked(_geom(page, sel))


@pytest.mark.parametrize("width", [375, 1024, 1440])
def test_no_page_scroll_at_any_width(page: Page, interactive_server: str, width):
    _load(page, interactive_server, width)
    p = page.evaluate(_PAGE)
    assert p["sw"] <= p["cw"], p


_STYLE = """(sel) => {
    const cap = document.querySelector(sel).querySelector(':scope > figcaption');
    const text = cap.querySelector(':scope > .hr-content-zone');
    const label = cap.querySelector('.label');
    const para = document.querySelector('.manuscript .paragraph.hr p');
    const probe = (v) => { const s = document.createElement('span');
        s.style.color = `var(${v})`; document.querySelector('.manuscript').appendChild(s);
        const c = getComputedStyle(s).color; s.remove(); return c; };
    const t = getComputedStyle(text), l = getComputedStyle(label);
    return {
        sizeRatio: parseFloat(t.fontSize) / parseFloat(getComputedStyle(para).fontSize),
        lineRatio: parseFloat(t.lineHeight) / parseFloat(t.fontSize),
        color: t.color, labelColor: l.color, labelWeight: +l.fontWeight,
        labelDisplay: l.display,
        background: t.backgroundColor, border: t.borderTopWidth,
        subtle: probe('--text-subtle'), body: probe('--text-body'),
    };
}"""


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("kind", list(KINDS))
def test_same_caption_style_in_margin_and_stacked(
    page: Page, interactive_server: str, kind, theme
):
    """The caption looks the same in the margin and stacked: only the position
    changes. Small subtle text, bold label in the body colour on its own line,
    no box."""
    seen = []
    for width in (1440, 1024, 375):
        _load(page, interactive_server, width)
        _force_theme(page, theme)
        s = page.evaluate(_STYLE, KINDS[kind][0])
        assert abs(s["sizeRatio"] - 0.84) < 0.02, s
        assert abs(s["lineRatio"] - 1.5) < 0.05, s
        assert s["color"] == s["subtle"], s
        assert s["labelColor"] == s["body"], s
        assert s["labelWeight"] >= 600, s
        assert s["labelDisplay"] == "block", s
        assert s["background"] in ("rgba(0, 0, 0, 0)", "transparent"), s
        assert s["border"] == "0px", s
        seen.append((round(s["sizeRatio"], 3), s["color"], s["labelColor"]))
    assert len(set(seen)) == 1, seen


# ---- the handrail -------------------------------------------------------------


@pytest.mark.parametrize("width", [1440, 1024])
def test_rail_hidden_at_rest(page: Page, interactive_server: str, width):
    _load(page, interactive_server, width)
    _rest(page)
    for kind in KINDS.values():
        assert _geom(page, kind[0])["railOpacity"] == 0


def _assert_rail_in_gutter(g: dict):
    assert g["railOpacity"] == 1, g
    # Same x as every other handrail in the document.
    assert abs(g["rail"]["l"] - g["paraRailLeft"]) <= 1, g
    # Beside the block, never in the margin.
    assert g["rail"]["r"] <= g["body"]["l"], g
    assert g["rail"]["r"] < g["text"]["r"], g
    # Spanning the block's height.
    assert abs(g["rail"]["t"] - g["block"]["t"]) <= 1, g
    assert abs(g["rail"]["h"] - g["block"]["h"]) <= 1, g


@pytest.mark.parametrize("target", ["block", "caption"])
@pytest.mark.parametrize("width", [1440, 1024])
@pytest.mark.parametrize("kind", list(KINDS))
def test_rail_in_gutter_on_hover(
    page: Page, interactive_server: str, kind, width, target
):
    _load(page, interactive_server, width)
    sel = KINDS[kind][0]
    page.locator(sel).scroll_into_view_if_needed()
    _settle(page, 200)
    if target == "block":
        g = _geom(page, sel)
        page.mouse.move((g["body"]["l"] + g["body"]["r"]) / 2, g["body"]["t"] + 5)
    else:
        page.hover(f"{sel} > figcaption .label")
    page.wait_for_timeout(200)
    _assert_rail_in_gutter(_geom(page, sel))


@pytest.mark.parametrize("width", [1440, 1024])
def test_rail_on_keyboard_focus(page: Page, interactive_server: str, width):
    """Tab from the paragraph before the figure reaches the caption, which shows
    its rail in the gutter."""
    _load(page, interactive_server, width)
    _rest(page)
    page.locator(".manuscript .paragraph.hr", has_text="Captions sit in").focus()
    page.keyboard.press("Tab")
    page.wait_for_timeout(200)
    assert page.evaluate(
        "() => document.activeElement === document.querySelector('#fig-a > figcaption')"
    )
    _assert_rail_in_gutter(_geom(page, "figure#fig-a"))


@pytest.mark.parametrize("width", [1440, 1024])
@pytest.mark.parametrize("kind", list(KINDS))
def test_menu_opens_on_the_caption(page: Page, interactive_server: str, kind, width):
    """The rail's dots open the menu for the caption node, labelled with the
    block's kind, and the menu opens beside the gutter, not in the margin."""
    sel, label = KINDS[kind]
    _load(page, interactive_server, width)
    page.locator(sel).scroll_into_view_if_needed()
    page.hover(f"{sel} > figcaption .label")
    page.click(f"{sel} > figcaption > .hr-border-zone .hr-border-dots")
    menu = page.locator(".hr-menu-portaled .hr-menu")
    expect(menu).to_be_visible()
    expect(menu.locator('[data-role="label"]')).to_have_text(label)
    assert page.evaluate(
        "(s) => document.querySelector(s).querySelector(':scope > figcaption')"
        ".classList.contains('hr-menu-open')",
        sel,
    )
    g = _geom(page, sel)
    m = menu.bounding_box()
    assert m["x"] + m["width"] <= g["body"]["l"] + 1, (m, g)


def test_menu_pin_acts_on_the_figure(page: Page, interactive_server: str):
    _load(page, interactive_server, 1440)
    page.hover("#fig-a > figcaption .label")
    page.click("#fig-a > figcaption > .hr-border-zone .hr-border-dots")
    page.click('.hr-menu-portaled [data-role="pin"]')
    page.wait_for_selector(".proof-rail.open", timeout=5_000)
    expect(page.locator(".rail-pinned-title")).to_have_text("Figure 1.1")


# ---- the figure itself is untouched ---------------------------------------------


@pytest.mark.parametrize("width", [1440, 1024])
@pytest.mark.parametrize("kind", ["figure", "widget", "table"])
def test_nothing_drawn_inside_the_block(
    page: Page, interactive_server: str, kind, width
):
    """The block's own pixels are identical with the caption and its rail shown
    (hovered) and with the caption hidden: nothing new is drawn on the block."""
    _load(page, interactive_server, width)
    sel = KINDS[kind][0]
    page.locator(sel).scroll_into_view_if_needed()
    _settle(page, 200)
    g = _geom(page, sel)
    clip = {
        "x": g["body"]["l"],
        "y": g["body"]["t"],
        "width": g["body"]["w"],
        "height": g["body"]["h"],
    }
    page.mouse.move(g["body"]["l"] + 2, g["body"]["t"] + 2)
    page.wait_for_timeout(200)
    shown = page.screenshot(clip=clip, animations="disabled")
    page.eval_on_selector(
        f"{sel} > figcaption", "e => { e.style.visibility = 'hidden'; }"
    )
    page.wait_for_timeout(100)
    hidden = page.screenshot(clip=clip, animations="disabled")
    assert shown == hidden


def test_caption_stays_inside_its_figure(page: Page, interactive_server: str):
    """DOM order is unchanged: the caption is the figure's last child, so the
    figure is named by it and a screen reader reads the figure, then the
    caption."""
    _load(page, interactive_server, 1440)
    for sel in ("figure#fig-a", "figure#wid-a", "figure#vid-a"):
        assert (
            page.eval_on_selector(sel, "f => f.lastElementChild.tagName")
            == "FIGCAPTION"
        )
    expect(
        page.get_by_role("figure", name=re.compile(r"^Figure 1\.1\."))
    ).to_have_count(1)


# ---- print and no sidebar --------------------------------------------------------


def test_print_keeps_captions_under_their_block(page: Page, interactive_server: str):
    _load(page, interactive_server, 1440)
    page.emulate_media(media="print")
    page.wait_for_timeout(200)
    for sel in ALL_BLOCKS:
        pos = page.eval_on_selector(
            f"{sel} > figcaption", "e => getComputedStyle(e).position"
        )
        assert pos == "static", (sel, pos)
        g = _geom(page, sel)
        assert g["cap"]["t"] >= g["body"]["b"] - 1, g


@pytest.fixture
def plain_page(tmp_path: Path):
    """The fixture built without the sidebar, as one standalone file."""
    shutil.copy(FIXTURES / "margin_captions.rsm", tmp_path / "plain.rsm")
    shutil.copy(FIXTURES / "figure-light.png", tmp_path / "figure-light.png")
    rsm.build(
        path=str(tmp_path / "plain.rsm"),
        output_dir=str(tmp_path),
        output_filename="plain.html",
        write_output=True,
        handrails=True,
        standalone=True,
        sidebar=False,
    )
    return (tmp_path / "plain.html").as_uri()


def test_without_sidebar_captions_stack(page: Page, plain_page: str):
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(plain_page)
    page.wait_for_function(RSM_READY, timeout=10_000)
    _settle(page)
    for sel in ALL_BLOCKS:
        _assert_stacked(_geom(page, sel))
    p = page.evaluate(_PAGE)
    assert p["sw"] <= p["cw"], p
    page.hover("#fig-a > figcaption .label")
    page.wait_for_timeout(200)
    _assert_rail_in_gutter(_geom(page, "figure#fig-a"))
