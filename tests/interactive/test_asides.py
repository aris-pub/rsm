"""Asides on the page (rsm-zvn.2, rsm-zvn.3, rsm-zvn.4, rsm-aul).

An aside is called on the phrase it is about. The HTML puts each aside at the
end of the block that calls it. With room for the right-hand column
(html.rsm-margin, set by sidebar.js), asides.js hands each aside to margin.js,
which places it level with its phrase and pushes it down past whatever is above
it, captions included. Without room the aside is hidden and its phrase opens
and closes it below its block. Without scripts every aside is shown, open,
below its block.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

# __rsmInitialized is set before the first render pass, which is where
# asides.js runs (after math), so also wait for the phrases to be wired.
RSM_READY = (
    "() => window.__rsmInitialized === true && !!document.querySelector("
    "'a.aside-phrase[aria-controls]')"
)
NAME = "asides"
CLOSE = ["a-one", "a-two", "a-three"]
ALL = ["a-one", "a-two", "a-three", "a-fig", "a-item", "a-step", "a-pair-1", "a-pair-2"]

_GEOM = """(id) => {
    const box = (e) => { const b = e.getBoundingClientRect();
        return {l: b.left, t: b.top, r: b.right, b: b.bottom, w: b.width, h: b.height}; };
    const aside = document.getElementById(id);
    const marker = document.getElementById('call-' + id);
    // The text of the block that calls the aside: everything in the aside's
    // container before the first aside.
    const holder = aside.parentElement;
    const first = holder.querySelector(':scope > .aside');
    const range = document.createRange();
    range.setStart(holder, 0);
    range.setEndBefore(first);
    const p = range;
    const rail = aside.closest('.hr').querySelector(':scope > .hr-border-zone');
    return {
        aside: box(aside), marker: box(marker), p: box(p), rail: box(rail),
        holder: box(holder),
        shown: getComputedStyle(aside).display !== 'none',
        expanded: marker.getAttribute('aria-expanded'),
        controls: marker.getAttribute('aria-controls'),
        text: box(aside.closest('.manuscript')),
        margin: document.documentElement.classList.contains('rsm-margin'),
    };
}"""

_PAGE = """() => ({
    sw: document.documentElement.scrollWidth,
    cw: document.documentElement.clientWidth,
    margin: document.documentElement.classList.contains('rsm-margin'),
})"""


def _load(page: Page, server: str, width: int, height: int = 900, hash: str = ""):
    page.set_viewport_size({"width": width, "height": height})
    page.goto(f"{server}/{NAME}.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.evaluate("() => localStorage.clear()")
    if hash:
        page.goto(f"{server}/{NAME}.html#{hash}")
    else:
        page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    _settle(page)


def _settle(page: Page, ms: int = 500):
    page.evaluate("() => document.fonts.ready")
    page.wait_for_timeout(ms)


def _geom(page: Page, id_: str) -> dict:
    return page.evaluate(_GEOM, id_)


def _overlap(a: dict, b: dict) -> bool:
    return a["l"] < b["r"] and b["l"] < a["r"] and a["t"] < b["b"] and b["t"] < a["b"]


def _toggle_panel(page: Page, view: str = "contents"):
    page.click(f'.rail-strip-btn[data-view="{view}"]')
    _settle(page, 600)


def _assert_in_margin(g: dict):
    assert g["margin"], g
    assert g["shown"], g
    assert g["aside"]["l"] >= g["text"]["r"], f"aside is not right of the text: {g}"
    assert g["aside"]["t"] >= g["marker"]["t"] - 1, f"aside starts above its phrase: {g}"
    assert g["expanded"] is None, g


def _assert_closed(g: dict):
    assert not g["margin"], g
    assert not g["shown"], g
    assert g["expanded"] == "false", g


def _assert_open_below(g: dict):
    assert not g["margin"], g
    assert g["shown"], g
    assert g["expanded"] == "true", g
    assert g["aside"]["t"] >= g["p"]["b"] - 1, f"aside is not below its text: {g}"
    h = g["holder"]
    assert g["aside"]["l"] >= h["l"] - 1 and g["aside"]["r"] <= h["r"] + 1, g


# ---- wide: the right-hand column (zvn.2) -----------------------------------


def test_close_asides_in_margin_without_overlap(page: Page, interactive_server: str):
    _load(page, interactive_server, 1280)
    gs = [_geom(page, i) for i in CLOSE]
    for g in gs:
        _assert_in_margin(g)
    # The three phrases are within a few lines of each other.
    assert gs[-1]["marker"]["t"] - gs[0]["marker"]["t"] < 5 * gs[0]["marker"]["h"] * 3
    for a, b in zip(gs, gs[1:], strict=False):
        assert b["aside"]["t"] >= a["aside"]["b"], (a, b)
    # The first aside is long enough to reach past the second marker, so the
    # second one was pushed down.
    assert gs[0]["aside"]["b"] > gs[1]["marker"]["t"]
    assert gs[1]["aside"]["t"] > gs[1]["marker"]["t"] + 4


@pytest.mark.parametrize("width", [1280, 1440, 1920])
def test_no_margin_items_overlap(page: Page, interactive_server: str, width):
    _load(page, interactive_server, width)
    boxes = [_geom(page, i)["aside"] for i in ALL]
    boxes += page.evaluate(
        "() => [...document.querySelectorAll('figcaption')].map(e => {"
        " const b = e.getBoundingClientRect();"
        " return {l: b.left, t: b.top, r: b.right, b: b.bottom}; })"
    )
    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            assert not _overlap(a, b), (a, b)


def test_aside_and_caption_share_the_column(page: Page, interactive_server: str):
    _load(page, interactive_server, 1280)
    g = _geom(page, "a-fig")
    _assert_in_margin(g)
    cap = page.eval_on_selector(
        "figure#fig-a > figcaption",
        "e => { const b = e.getBoundingClientRect(); return {l: b.left, t: b.top}; }",
    )
    assert abs(cap["l"] - g["aside"]["l"]) < 1, (cap, g)
    assert cap["t"] >= g["aside"]["b"], (cap, g)


@pytest.mark.parametrize("id_", ["a-item", "a-step", "a-pair-1", "a-pair-2"])
def test_every_kind_of_block_puts_its_aside_in_margin(
    page: Page, interactive_server: str, id_
):
    _load(page, interactive_server, 1280)
    _assert_in_margin(_geom(page, id_))


def test_phrase_click_in_margin_does_not_jump(page: Page, interactive_server: str):
    _load(page, interactive_server, 1280)
    before = page.evaluate("() => [scrollY, location.hash]")
    page.click("#call-a-one")
    page.wait_for_timeout(200)
    assert page.evaluate("() => [scrollY, location.hash]") == before
    _assert_in_margin(_geom(page, "a-one"))


def test_panel_open_moves_asides_below_and_back(page: Page, interactive_server: str):
    _load(page, interactive_server, 1280)
    _assert_in_margin(_geom(page, "a-one"))
    _toggle_panel(page)
    for i in CLOSE:
        _assert_closed(_geom(page, i))
    _toggle_panel(page)
    for i in CLOSE:
        _assert_in_margin(_geom(page, i))


def test_reading_width_wide_moves_asides_below_and_back(
    page: Page, interactive_server: str
):
    _load(page, interactive_server, 1280)
    page.evaluate(
        "() => { const v = JSON.stringify({measure: 'wide'});"
        " localStorage.setItem('rsm-reading', v); }"
    )
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    _settle(page)
    assert page.evaluate("() => document.documentElement.dataset.readingMeasure") == "wide"
    _assert_closed(_geom(page, "a-one"))
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    _settle(page)
    _assert_in_margin(_geom(page, "a-one"))


def test_reading_width_switches_live(page: Page, interactive_server: str):
    _load(page, interactive_server, 1700)
    page.evaluate("() => { window.__noReload = true; }")
    _toggle_panel(page, "reading")
    _assert_in_margin(_geom(page, "a-one"))
    page.click('.reading-row[data-control="measure"] .reading-opt[data-value="wide"]')
    _settle(page, 600)
    _assert_closed(_geom(page, "a-one"))
    page.click('.reading-row[data-control="measure"] .reading-opt[data-value="normal"]')
    _settle(page, 600)
    _assert_in_margin(_geom(page, "a-one"))
    assert page.evaluate("() => window.__noReload === true"), "the page reloaded"


def test_window_resize_switches_live(page: Page, interactive_server: str):
    _load(page, interactive_server, 1280)
    _assert_in_margin(_geom(page, "a-one"))
    page.set_viewport_size({"width": 1000, "height": 900})
    _settle(page)
    _assert_closed(_geom(page, "a-one"))
    page.set_viewport_size({"width": 1280, "height": 900})
    _settle(page)
    _assert_in_margin(_geom(page, "a-one"))


def test_opened_aside_stays_open_across_a_margin_round_trip(
    page: Page, interactive_server: str
):
    _load(page, interactive_server, 1000)
    page.click("#call-a-two")
    _assert_open_below(_geom(page, "a-two"))
    page.set_viewport_size({"width": 1280, "height": 900})
    _settle(page)
    _assert_in_margin(_geom(page, "a-two"))
    page.set_viewport_size({"width": 1000, "height": 900})
    _settle(page)
    _assert_open_below(_geom(page, "a-two"))
    _assert_closed(_geom(page, "a-one"))


@pytest.mark.parametrize("width", [375, 768, 1024, 1280, 1440])
@pytest.mark.parametrize("js", [True, False])
def test_no_page_scroll_at_any_width(browser, interactive_server: str, width, js):
    ctx = browser.new_context(
        java_script_enabled=js, viewport={"width": width, "height": 900}
    )
    page = ctx.new_page()
    page.goto(f"{interactive_server}/{NAME}.html")
    if js:
        page.wait_for_function(RSM_READY, timeout=10_000)
        for i in ALL:
            if not _geom(page, i)["margin"]:
                page.click(f"#call-{i}")
    page.wait_for_timeout(500)
    p = page.evaluate(_PAGE)
    ctx.close()
    assert p["sw"] <= p["cw"], p


# ---- linked hover ------------------------------------------------------------

_LIT = """(id) => {
    const a = document.getElementById(id), m = document.getElementById('call-' + id);
    return {aside: a.classList.contains('rsm-aside-lit'),
            marker: m.classList.contains('rsm-aside-lit'),
            asideBg: getComputedStyle(a).backgroundColor,
            markerBg: getComputedStyle(m).backgroundColor,
            markerColor: getComputedStyle(m).color,
            textColor: getComputedStyle(m.parentElement).color};
}"""


def _rest(page: Page):
    page.mouse.move(2, 2)
    page.evaluate("() => document.activeElement && document.activeElement.blur()")
    page.wait_for_timeout(250)


@pytest.mark.parametrize("width", [1280, 375])
def test_hovering_the_phrase_lights_both(page: Page, interactive_server: str, width):
    _load(page, interactive_server, width)
    if width < 1000:
        page.click("#call-a-one")
    _rest(page)
    rest = page.evaluate(_LIT, "a-one")
    assert not rest["aside"] and not rest["marker"]
    page.hover("#call-a-one")
    page.wait_for_timeout(250)
    lit = page.evaluate(_LIT, "a-one")
    assert lit["aside"] and lit["marker"], lit
    assert lit["asideBg"] != rest["asideBg"], (rest, lit)
    assert lit["markerBg"] != rest["markerBg"], (rest, lit)
    _rest(page)
    assert not page.evaluate(_LIT, "a-one")["aside"]


def test_hovering_the_aside_lights_the_phrase_and_the_rail(
    page: Page, interactive_server: str
):
    _load(page, interactive_server, 1280)
    _rest(page)
    rail = "() => +getComputedStyle(document.getElementById('a-one').closest('.hr')" \
        ".querySelector(':scope > .hr-border-zone')).opacity"
    assert page.evaluate(rail) == 0
    page.hover("#a-one")
    page.wait_for_timeout(250)
    lit = page.evaluate(_LIT, "a-one")
    assert lit["aside"] and lit["marker"], lit
    assert page.evaluate(rail) == 1
    others = page.evaluate(_LIT, "a-two")
    assert not others["aside"] and not others["marker"]


def test_focusing_the_phrase_lights_both(page: Page, interactive_server: str):
    _load(page, interactive_server, 1280)
    _rest(page)
    page.focus("#call-a-two")
    page.wait_for_timeout(150)
    lit = page.evaluate(_LIT, "a-two")
    assert lit["aside"] and lit["marker"], lit
    page.focus("#call-a-three")
    page.wait_for_timeout(150)
    assert not page.evaluate(_LIT, "a-two")["aside"]
    assert page.evaluate(_LIT, "a-three")["aside"]


def test_lit_phrase_has_the_tint_of_the_lit_aside(page: Page, interactive_server: str):
    _load(page, interactive_server, 1280)
    page.hover("#a-one")
    page.wait_for_timeout(250)
    lit = page.evaluate(_LIT, "a-one")
    assert lit["markerBg"] == lit["asideBg"], lit
    # Still body text, not link colour or a filled chip.
    assert lit["markerColor"] == lit["textColor"], lit


# ---- narrow: tap to open below the block (zvn.3) ----------------------------


def test_asides_closed_on_a_phone(page: Page, interactive_server: str):
    _load(page, interactive_server, 375)
    for i in ALL:
        g = _geom(page, i)
        _assert_closed(g)
        assert g["controls"] == i


def test_tap_opens_below_the_paragraph_and_again_closes(
    page: Page, interactive_server: str
):
    _load(page, interactive_server, 375)
    page.click("#call-a-two")
    g = _geom(page, "a-two")
    _assert_open_below(g)
    # Never mid-sentence: the paragraph's text is all above the aside.
    assert g["aside"]["t"] >= g["p"]["b"]
    page.click("#call-a-two")
    _assert_closed(_geom(page, "a-two"))
    assert page.evaluate("() => location.hash") == ""


def test_opened_asides_stack_in_phrase_order(page: Page, interactive_server: str):
    _load(page, interactive_server, 375)
    page.click("#call-a-pair-2")
    page.click("#call-a-pair-1")
    one, two = _geom(page, "a-pair-1"), _geom(page, "a-pair-2")
    _assert_open_below(one)
    _assert_open_below(two)
    assert two["aside"]["t"] >= one["aside"]["b"], (one, two)


def test_opening_one_of_three_leaves_the_others_closed(
    page: Page, interactive_server: str
):
    _load(page, interactive_server, 375)
    page.click("#call-a-three")
    _assert_open_below(_geom(page, "a-three"))
    _assert_closed(_geom(page, "a-one"))
    _assert_closed(_geom(page, "a-two"))


@pytest.mark.parametrize("id_", ["a-item", "a-step"])
def test_list_item_and_step_open_below_their_text(
    page: Page, interactive_server: str, id_
):
    _load(page, interactive_server, 375)
    page.click(f"#call-{id_}")
    _assert_open_below(_geom(page, id_))


def test_rail_spans_the_opened_aside(page: Page, interactive_server: str):
    _load(page, interactive_server, 375)
    closed = _geom(page, "a-one")
    page.click("#call-a-one")
    page.click("#call-a-three")
    g = _geom(page, "a-three")
    assert g["rail"]["b"] >= g["aside"]["b"] - 1, g
    assert g["rail"]["h"] > closed["rail"]["h"], (closed, g)


def test_keyboard_toggles_with_enter_and_space(page: Page, interactive_server: str):
    _load(page, interactive_server, 375)
    page.focus("#call-a-one")
    page.keyboard.press("Enter")
    _assert_open_below(_geom(page, "a-one"))
    y = page.evaluate("() => scrollY")
    page.keyboard.press("Space")
    _assert_closed(_geom(page, "a-one"))
    assert page.evaluate("() => scrollY") == y, "Space scrolled the page"
    page.keyboard.press("Space")
    _assert_open_below(_geom(page, "a-one"))
    assert page.evaluate("() => document.activeElement.id") == "call-a-one"


def test_phrase_reachable_by_tab(page: Page, interactive_server: str):
    _load(page, interactive_server, 375)
    page.focus("#call-a-one")
    page.keyboard.press("Shift+Tab")
    page.keyboard.press("Tab")
    assert page.evaluate("() => document.activeElement.id") == "call-a-one"


def test_link_to_an_aside_opens_it(page: Page, interactive_server: str):
    _load(page, interactive_server, 375, hash="a-two")
    _assert_open_below(_geom(page, "a-two"))


def test_desktop_without_room_uses_tap_to_open(page: Page, interactive_server: str):
    """At 1000px a desktop window has no room for the column, so it behaves
    like a phone."""
    _load(page, interactive_server, 1000)
    assert not page.evaluate(_PAGE)["margin"]
    page.click("#call-a-one")
    _assert_open_below(_geom(page, "a-one"))


# ---- hover preview on pointer devices ---------------------------------------

_TIP = """() => [...document.querySelectorAll('.tooltipster-base')]
    .map(t => t.textContent.trim())"""


def test_hover_preview_of_a_closed_aside(page: Page, interactive_server: str):
    _load(page, interactive_server, 1000)
    page.hover("#call-a-three")
    page.wait_for_timeout(700)
    tips = page.evaluate(_TIP)
    assert any("The third aside, short." in t for t in tips), tips


def test_hover_preview_is_titled_as_an_aside(page: Page, interactive_server: str):
    """The preview is the shared reference preview, titled "Aside". Asides have
    no number, and the footnotes' "Note 3" would be wrong."""
    _load(page, interactive_server, 1000)
    page.hover("#call-a-three")
    page.wait_for_timeout(700)
    titles = page.evaluate(
        "() => [...document.querySelectorAll('.tooltipster-base .ref-pin')]"
        ".map(b => b.dataset.pinTitle)"
    )
    assert titles == ["Aside"], titles


def test_no_hover_preview_once_open(page: Page, interactive_server: str):
    _load(page, interactive_server, 1000)
    page.click("#call-a-three")
    _rest(page)
    page.hover("#call-a-three")
    page.wait_for_timeout(700)
    assert not any("third aside" in t for t in page.evaluate(_TIP))


def test_opening_closes_the_preview(page: Page, interactive_server: str):
    _load(page, interactive_server, 1000)
    page.hover("#call-a-three")
    page.wait_for_timeout(700)
    assert any("third aside" in t for t in page.evaluate(_TIP))
    page.click("#call-a-three")
    page.wait_for_timeout(700)
    assert not any("third aside" in t for t in page.evaluate(_TIP))


def test_no_hover_preview_in_margin(page: Page, interactive_server: str):
    _load(page, interactive_server, 1280)
    page.hover("#call-a-three")
    page.wait_for_timeout(700)
    assert not any("third aside" in t for t in page.evaluate(_TIP))


def test_reference_preview_leaves_the_aside_out(page: Page, interactive_server: str):
    """The step's statement holds its aside, but the preview of a reference to
    the step shows the statement only."""
    _load(page, interactive_server, 1280)
    assert page.evaluate("() => !!document.querySelector('#st-a .aside')")
    page.hover('a.reference[href="#st-a"]')
    page.wait_for_timeout(700)
    tips = page.evaluate(_TIP)
    assert any("A first step with an aside" in t for t in tips), tips
    assert not any("The aside of the proof step" in t for t in tips), tips


# ---- without scripts (zvn.4) --------------------------------------------------


@pytest.mark.parametrize("width", [375, 1280])
def test_without_js_every_aside_is_open_below_its_block(
    browser, interactive_server: str, width
):
    ctx = browser.new_context(
        java_script_enabled=False, viewport={"width": width, "height": 900}
    )
    page = ctx.new_page()
    page.goto(f"{interactive_server}/{NAME}.html")
    page.wait_for_timeout(300)
    assert not page.evaluate("() => document.documentElement.className.includes('has-asides')")
    gs = [_geom(page, i) for i in ALL]
    p = page.evaluate(_PAGE)
    ctx.close()
    for g in gs:
        assert g["shown"], g
        assert g["aside"]["t"] >= g["p"]["b"] - 1, g
        assert g["aside"]["r"] <= g["text"]["r"] + 1, g
    for i, a in enumerate(gs):
        for b in gs[i + 1 :]:
            assert not _overlap(a["aside"], b["aside"]), (a, b)
    assert p["sw"] <= p["cw"], p


@pytest.mark.parametrize("width", [375, 1280])
def test_first_paint_already_has_the_scripted_state(
    page: Page, interactive_server: str, width
):
    """The pre-paint script sets has-asides before any module runs, so the
    asides are hidden (narrow) from the first paint instead of showing and
    then vanishing. Shown by loading the page with the modules blocked."""
    page.route("**/static/onload.js", lambda route: route.abort())
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{interactive_server}/{NAME}.html")
    page.wait_for_timeout(300)
    assert page.evaluate("() => document.documentElement.classList.contains('has-asides')")
    for i in ALL:
        assert not _geom(page, i)["shown"]


# ---- look ------------------------------------------------------------------

_STYLE = """(id) => {
    const a = document.getElementById(id);
    const para = a.closest('.hr-content-zone').querySelector(':scope > p');
    const cap = document.querySelector('figure#fig-a > figcaption > .hr-content-zone');
    const probe = (prop, v) => { const s = document.createElement('span');
        s.style[prop] = v; document.querySelector('.manuscript').appendChild(s);
        const c = getComputedStyle(s)[prop]; s.remove(); return c; };
    const s = getComputedStyle(a);
    return {
        bg: s.backgroundColor,
        want: probe('backgroundColor',
            'color-mix(in srgb, var(--primary-700) 9%, var(--surface-page))'),
        radius: s.borderTopLeftRadius,
        borders: [s.borderLeftWidth, s.borderTopWidth, s.borderRightWidth, s.borderBottomWidth],
        sizeRatio: parseFloat(s.fontSize) / parseFloat(getComputedStyle(para).fontSize),
        lineRatio: parseFloat(s.lineHeight) / parseFloat(s.fontSize),
        padTop: parseFloat(s.paddingTop) / parseFloat(s.fontSize),
        padLeft: parseFloat(s.paddingLeft) / parseFloat(s.fontSize),
        capBg: getComputedStyle(cap).backgroundColor,
        numbers: a.querySelectorAll('.note__number').length,
    };
}"""


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("width", [375, 1280])
def test_aside_card_look(page: Page, interactive_server: str, width, theme):
    _load(page, interactive_server, width)
    page.evaluate(
        "(t) => { const c = document.documentElement.classList;"
        " c.remove('light-theme', 'dark-theme'); c.add(t + '-theme'); }",
        theme,
    )
    if width < 1000:
        page.click("#call-a-one")
    _rest(page)
    st = page.evaluate(_STYLE, "a-one")
    assert st["bg"] == st["want"], st
    assert st["radius"] == "8px", st
    assert st["borders"] == ["0px"] * 4, "no vertical bars on an aside"
    assert abs(st["sizeRatio"] - 0.84) < 0.01, st
    assert abs(st["lineRatio"] - 1.5) < 0.01, st
    assert abs(st["padTop"] - 0.65) < 0.02 and abs(st["padLeft"] - 0.85) < 0.02, st
    assert st["numbers"] == 0, "an aside card has no number"
    # Captions are unboxed, asides are cards.
    assert st["capBg"] == "rgba(0, 0, 0, 0)" and st["bg"] != st["capBg"], st


def test_aside_has_no_handrail_of_its_own(page: Page, interactive_server: str):
    _load(page, interactive_server, 1280)
    n = page.evaluate(
        "() => [...document.querySelectorAll('.aside')]"
        ".filter(a => a.matches('.hr') || a.querySelector('.hr, .hr-border-zone')).length"
    )
    assert n == 0


_PHRASE = """(id) => {
    const m = document.getElementById('call-' + id);
    const s = getComputedStyle(m), p = getComputedStyle(m.parentElement);
    const probe = (prop, v) => { const e = document.createElement('span');
        e.style[prop] = v; document.querySelector('.manuscript').appendChild(e);
        const c = getComputedStyle(e)[prop]; e.remove(); return c; };
    return {
        text: m.textContent, color: s.color, bodyColor: p.color,
        weight: s.fontWeight, bodyWeight: p.fontWeight, bg: s.backgroundColor,
        line: s.textDecorationLine, style: s.textDecorationStyle,
        decoColor: s.textDecorationColor,
        want: probe('color', 'color-mix(in srgb, var(--primary-700) 70%, transparent)'),
        thickness: s.textDecorationThickness, offset: s.textUnderlineOffset,
        fontSize: parseFloat(s.fontSize),
    };
}"""


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("width", [375, 1280])
def test_phrase_look(page: Page, interactive_server: str, width, theme):
    """Body text with a faint dotted accent underline, no chip and no number."""
    _load(page, interactive_server, width)
    page.evaluate(
        "(t) => { const c = document.documentElement.classList;"
        " c.remove('light-theme', 'dark-theme'); c.add(t + '-theme'); }",
        theme,
    )
    _rest(page)
    st = page.evaluate(_PHRASE, "a-one")
    assert st["text"] == "the next one (aside)", st
    assert st["color"] == st["bodyColor"], st
    assert st["weight"] == st["bodyWeight"], st
    assert st["bg"] == "rgba(0, 0, 0, 0)", st
    assert st["line"] == "underline" and st["style"] == "dotted", st
    assert st["decoColor"] == st["want"], st
    assert st["thickness"] == "1.5px", st
    assert abs(float(st["offset"][:-2]) - 0.2 * st["fontSize"]) < 0.5, st
    assert not page.evaluate("() => document.querySelector('a.note-marker[data-note-kind=aside]')")


def test_tap_target_is_44px_tall_on_touch(browser, interactive_server: str):
    ctx = browser.new_context(
        viewport={"width": 375, "height": 800}, has_touch=True, is_mobile=True
    )
    page = ctx.new_page()
    page.goto(f"{interactive_server}/{NAME}.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    _settle(page)
    coarse = page.evaluate("() => matchMedia('(hover: none) and (pointer: coarse)').matches")
    heights = page.evaluate(
        "() => [...document.querySelectorAll('a.aside-phrase')]"
        ".map(a => [...a.getClientRects()].map(r => r.height))"
    )
    page.tap("#call-a-two")
    page.wait_for_timeout(200)
    opened = page.evaluate("() => document.getElementById('a-two').classList.contains('rsm-aside-open')")
    ctx.close()
    assert coarse
    for rects in heights:
        assert rects and all(h >= 44 for h in rects), heights
    assert opened
