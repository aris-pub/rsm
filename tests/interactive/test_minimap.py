"""Interactive tests for the document minimap (rsm/static/minimap.js).

A strip at the right edge of the viewport replaces the native scrollbar: a mark
per section (line) and figure (dash), and a box over the part on screen. It
scrolls like a scrollbar (click, drag) and works as a map (hover a mark for its
label, click it to go there). On phones it shows only while the page scrolls.
The fixture (fixtures/minimap.rsm) has sections at two depths, two figures, an
:html: widget and a long foldable proof.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page

import rsm

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"
DESKTOP = {"width": 1280, "height": 800}
PHONE = {"width": 375, "height": 720}
LABELS = [
    "1. Introduction",
    "1.1. Background",
    "Figure 1.1",
    "2. Results",
    "Widget 2.1",
    "Widget 2.2",
    "3. Discussion",
    "Figure 3.1",
    "3.1. Outlook",
]
TYPES = [
    "section", "section", "figure", "section", "figure", "figure", "section", "figure", "section",
]


def _load(page: Page, server: str, size=DESKTOP, theme="light", reduced=False) -> None:
    page.set_viewport_size(size)
    page.emulate_media(color_scheme=theme, reduced_motion="reduce" if reduced else "no-preference")
    page.goto(f"{server}/minimap.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".rsm-minimap .rsm-minimap-mark", state="attached", timeout=10_000)
    # Let the debounced recompute after fonts and math settle.
    page.wait_for_timeout(400)


def _track(page: Page) -> dict:
    return page.locator(".rsm-minimap-track").bounding_box()


def _marks(page: Page) -> list[dict]:
    """Each mark's centre (px from the track top) and where it should be."""
    return page.evaluate(
        """() => {
        const track = document.querySelector('.rsm-minimap-track').getBoundingClientRect();
        const sh = document.documentElement.scrollHeight;
        const links = [...document.querySelectorAll('.rsm-minimap-links a')];
        return [...document.querySelectorAll('.rsm-minimap-mark')].map((m, i) => {
            const r = m.getBoundingClientRect();
            const el = document.getElementById(links[i].getAttribute('href').slice(1));
            const top = el.getBoundingClientRect().top + window.scrollY;
            return {
                label: links[i].textContent,
                type: m.classList.contains('mm-figure') ? 'figure' : 'section',
                top: m.classList.contains('mm-top'),
                y: r.top + r.height / 2 - track.top,
                expected: (top / sh) * track.height,
                id: el.id,
            };
        });
    }"""
    )


def _mark(page: Page, label: str) -> dict:
    return next(m for m in _marks(page) if m["label"] == label)


def _widest_gap_middle(marks: list[dict]) -> float:
    """The point (px from the track top) halfway across the widest gap between marks."""
    gaps = [
        (b["y"] - a["y"], (a["y"] + b["y"]) / 2)
        for a, b in zip(marks, marks[1:], strict=False)
    ]
    return max(gaps)[1]


def _settle_scroll(page: Page) -> float:
    """Wait for a (possibly smooth) scroll to stop and return scrollY."""
    return page.evaluate(
        """() => new Promise((resolve) => {
        let last = -1, same = 0;
        const tick = () => {
            const y = window.scrollY;
            same = Math.abs(y - last) < 0.5 ? same + 1 : 0;
            last = y;
            if (same >= 8) resolve(y); else requestAnimationFrame(tick);
        };
        tick();
    })"""
    )


def _top_in_viewport(page: Page, el_id: str) -> float:
    return page.evaluate(
        "(id) => document.getElementById(id).getBoundingClientRect().top", el_id
    )


def _strip_x(page: Page) -> float:
    box = _track(page)
    return box["x"] + box["width"] / 2


# ---------------------------------------------------------------------------
# Mounting and the native scrollbar


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_strip_replaces_the_native_scrollbar(page: Page, interactive_server: str, theme):
    _load(page, interactive_server, theme=theme)
    nav = page.locator(".rsm-minimap")
    assert nav.is_visible()
    box = nav.bounding_box()
    assert box["width"] == 24
    assert box["x"] + box["width"] == DESKTOP["width"], "the strip sits at the viewport edge"
    assert box["y"] == 0 and box["height"] == DESKTOP["height"]
    info = page.evaluate(
        """() => ({
        on: document.documentElement.classList.contains('rsm-minimap-on'),
        sw: document.documentElement.scrollWidth,
        cw: document.documentElement.clientWidth,
        iw: window.innerWidth,
        bar: getComputedStyle(document.documentElement).scrollbarWidth,
    })"""
    )
    assert info["on"]
    assert info["bar"] == "none"
    assert info["cw"] == info["iw"], "no native scrollbar"
    assert info["sw"] == info["iw"], "no horizontal overflow"


def test_strip_is_above_content_and_below_the_sidebar(page: Page, interactive_server: str):
    _load(page, interactive_server)
    z = page.evaluate(
        """() => ({
        mm: +getComputedStyle(document.querySelector('.rsm-minimap')).zIndex,
        strip: +getComputedStyle(document.querySelector('.rail-strip')).zIndex,
    })"""
    )
    assert 0 < z["mm"] < z["strip"]


def test_no_strip_without_javascript(browser: Browser, interactive_server: str):
    ctx = browser.new_context(java_script_enabled=False, viewport=DESKTOP)
    page = ctx.new_page()
    page.goto(f"{interactive_server}/minimap.html")
    page.wait_for_load_state("load")
    assert page.locator(".rsm-minimap").count() == 0
    assert "rsm-minimap-on" not in (page.locator("html").get_attribute("class") or "")
    ctx.close()


def test_native_scrollbar_present_without_javascript(browser: Browser, interactive_server: str):
    # Headless Chromium draws no scrollbars at all (Playwright passes
    # --hide-scrollbars), so check the style that would hide one instead of
    # measuring widths. Playwright's evaluate still runs with page scripts off.
    ctx = browser.new_context(java_script_enabled=False, viewport=DESKTOP)
    page = ctx.new_page()
    page.goto(f"{interactive_server}/minimap.html")
    page.wait_for_load_state("load")
    bar = page.evaluate("() => getComputedStyle(document.documentElement).scrollbarWidth")
    ctx.close()
    assert bar == "auto"


def test_marks_list(page: Page, interactive_server: str):
    _load(page, interactive_server)
    marks = _marks(page)
    assert [m["label"] for m in marks] == LABELS
    assert [m["type"] for m in marks] == TYPES
    # Top-level sections (##) are full width, deeper ones (###) shorter.
    tops = {m["label"]: m["top"] for m in marks if m["type"] == "section"}
    assert tops == {
        "1. Introduction": True,
        "1.1. Background": False,
        "2. Results": True,
        "3. Discussion": True,
        "3.1. Outlook": False,
    }


def test_unnumbered_widgets_and_figures_inside_widgets_get_no_mark(
    page: Page, interactive_server: str
):
    _load(page, interactive_server)
    # The fixture has a :nonum: widget with no caption (an ornament), and the
    # widget HTML holds a <figure> of its own.
    assert page.locator("#wid-ornament").count() == 1
    assert page.locator("figure.mm-inner-figure").count() == 3
    ids = [m["id"] for m in _marks(page)]
    assert "wid-ornament" not in ids
    assert len(ids) == len(LABELS)


def test_numbered_widget_without_a_caption_gets_a_mark_named_by_its_number(
    page: Page, interactive_server: str
):
    _load(page, interactive_server)
    assert page.locator("#wid-bare > figcaption").count() == 0
    m = next(m for m in _marks(page) if m["id"] == "wid-bare")
    assert m["type"] == "figure"
    assert m["label"] == "Widget 2.2"
    page.mouse.move(_strip_x(page), _track(page)["y"] + m["y"])
    assert page.locator(".rsm-minimap-tip").inner_text() == "Widget 2.2"


@pytest.mark.parametrize("size", [DESKTOP, PHONE], ids=["1280", "375"])
def test_marks_sit_at_their_fraction_of_the_strip(page: Page, interactive_server: str, size):
    _load(page, interactive_server, size=size)
    for m in _marks(page):
        assert abs(m["y"] - m["expected"]) <= 2, m


def test_mark_shapes(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.mouse.move(_strip_x(page), 2)  # hover the strip: marks at full width
    page.wait_for_timeout(400)
    shapes = page.evaluate(
        """() => [...document.querySelectorAll('.rsm-minimap-mark')].map((m) => {
        const cs = getComputedStyle(m, '::after');
        return { cls: m.className, h: parseFloat(cs.height), w: parseFloat(cs.width),
                 bg: cs.backgroundColor };
    })"""
    )
    top = next(s for s in shapes if "mm-top" in s["cls"])
    deep = next(s for s in shapes if "mm-section" in s["cls"] and "mm-top" not in s["cls"])
    fig = next(s for s in shapes if "mm-figure" in s["cls"])
    assert (top["h"], top["w"]) == (4, 20)  # 2px inset each side
    assert (deep["h"], deep["w"]) == (3, 16)  # 4px inset each side
    assert fig["h"] == 3 and abs(fig["w"] - 24 * 0.6) < 0.5
    # Figures use the accent, sections a neutral tone.
    assert fig["bg"] != top["bg"]


def test_figure_marks_follow_the_accent(page: Page, interactive_server: str):
    _load(page, interactive_server)
    fig = "() => getComputedStyle(document.querySelector('.mm-figure'), '::after').backgroundColor"
    blue = page.evaluate(fig)
    page.evaluate(
        "() => { document.documentElement.setAttribute('data-accent', 'red');"
        " document.body.setAttribute('data-accent', 'red'); }"
    )
    page.wait_for_timeout(400)  # the colour transition
    assert page.evaluate(fig) != blue


def test_marks_rest_faint_and_grow_on_hover(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.mouse.move(400, 400)
    page.wait_for_timeout(400)
    rest = page.evaluate(
        "() => { const cs = getComputedStyle(document.querySelector('.mm-section'), '::after');"
        " return [cs.opacity, cs.transform]; }"
    )
    assert rest[0] == "0.3"
    assert rest[1].startswith("matrix(0.75")
    page.mouse.move(_strip_x(page), 2)
    page.wait_for_timeout(400)
    hover = page.evaluate(
        "() => { const cs = getComputedStyle(document.querySelector('.mm-section'), '::after');"
        " return [cs.opacity, cs.transform]; }"
    )
    assert hover[0] == "1"
    assert hover[1] in ("none", "matrix(1, 0, 0, 1, 0, 0)")


# ---------------------------------------------------------------------------
# Hover, click, drag


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_hover_near_a_section_mark_shows_its_heading(page: Page, interactive_server: str, theme):
    _load(page, interactive_server, theme=theme)
    m = _mark(page, "2. Results")
    track = _track(page)
    page.mouse.move(_strip_x(page), track["y"] + m["y"] + 8)  # within 12px
    tip = page.locator(".rsm-minimap-tip")
    assert tip.is_visible()
    assert tip.inner_text() == "2. Results"
    # The label sits to the left of the strip, at the mark.
    tb = tip.bounding_box()
    assert tb["x"] + tb["width"] <= track["x"]
    assert abs(tb["y"] + tb["height"] / 2 - (track["y"] + m["y"])) <= 2
    assert "has-hovered" in page.locator(".rsm-minimap").get_attribute("class")
    page.wait_for_timeout(400)
    opacities = page.evaluate(
        """() => [...document.querySelectorAll('.rsm-minimap-mark')].map((m) =>
        [m.classList.contains('is-hovered'), getComputedStyle(m, '::after').opacity])"""
    )
    hovered = [o for h, o in opacities if h]
    others = [o for h, o in opacities if not h]
    assert hovered == ["1"]
    assert set(others) == {"0.35"}


def test_hover_shows_figure_labels(page: Page, interactive_server: str):
    _load(page, interactive_server)
    track = _track(page)
    for label in ("Figure 1.1", "Widget 2.1"):
        m = _mark(page, label)
        page.mouse.move(_strip_x(page), track["y"] + m["y"] - 4)
        assert page.locator(".rsm-minimap-tip").inner_text() == label


def test_marks_close_to_the_hovered_one_dim_further(page: Page, interactive_server: str):
    _load(page, interactive_server)
    # Squeeze two marks together: move the Background section's mark to within
    # 8px of the Introduction one by scaling the strip down.
    page.set_viewport_size({"width": 1280, "height": 60})
    page.wait_for_timeout(400)
    marks = _marks(page)
    a, b = marks[0], marks[1]
    assert abs(a["y"] - b["y"]) < 8, (a, b)
    track = _track(page)
    page.mouse.move(_strip_x(page), track["y"] + a["y"])
    page.wait_for_timeout(400)
    state = page.evaluate(
        """() => [...document.querySelectorAll('.rsm-minimap-mark')].slice(0, 2).map((m) =>
        [m.className, getComputedStyle(m, '::after').opacity])"""
    )
    hovered = [s for s in state if "is-hovered" in s[0]]
    near = [s for s in state if "is-near" in s[0]]
    assert len(hovered) == 1 and len(near) == 1
    assert near[0][1] == "0.1"


def test_hover_away_from_marks_shows_no_label(page: Page, interactive_server: str):
    _load(page, interactive_server)
    track = _track(page)
    mid = _widest_gap_middle(_marks(page))
    page.mouse.move(_strip_x(page), track["y"] + mid)
    assert not page.locator(".rsm-minimap-tip").is_visible()
    page.mouse.move(400, 400)
    assert not page.locator(".rsm-minimap-tip").is_visible()


@pytest.mark.parametrize("reduced", [True, False], ids=["reduced-motion", "smooth"])
def test_click_a_mark_scrolls_it_to_the_centre(page: Page, interactive_server: str, reduced):
    _load(page, interactive_server, reduced=reduced)
    m = _mark(page, "2. Results")
    track = _track(page)
    page.mouse.click(_strip_x(page), track["y"] + m["y"] + 6)
    if reduced:
        # Instant: already there on the next frame.
        page.evaluate("() => new Promise((r) => requestAnimationFrame(() => r()))")
    _settle_scroll(page)
    assert abs(_top_in_viewport(page, "sec-results") - DESKTOP["height"] / 2) <= 2


def test_click_a_figure_mark_scrolls_it_to_the_centre(page: Page, interactive_server: str):
    _load(page, interactive_server, reduced=True)
    m = _mark(page, "Widget 2.1")
    page.mouse.click(_strip_x(page), _track(page)["y"] + m["y"])
    _settle_scroll(page)
    assert abs(_top_in_viewport(page, "wid-a") - DESKTOP["height"] / 2) <= 2


def test_click_empty_strip_jumps_there(page: Page, interactive_server: str):
    _load(page, interactive_server)
    track = _track(page)
    mid = _widest_gap_middle(_marks(page))
    page.mouse.click(_strip_x(page), track["y"] + mid)
    y = _settle_scroll(page)
    sh, ih = page.evaluate("() => [document.documentElement.scrollHeight, innerHeight]")
    assert abs(y - (mid / track["height"] * sh - ih / 2)) <= 2


def test_drag_scrolls_top_to_bottom(page: Page, interactive_server: str):
    _load(page, interactive_server)
    track = _track(page)
    x = _strip_x(page)
    page.mouse.move(x, track["y"] + 1)
    page.mouse.down()
    seen = []
    for i in range(1, 21):
        page.mouse.move(x, track["y"] + 1 + (track["height"] - 2) * i / 20)
        seen.append(page.evaluate("() => window.scrollY"))
    page.mouse.up()
    max_y = page.evaluate("() => document.documentElement.scrollHeight - innerHeight")
    assert seen == sorted(seen), "dragging down only ever scrolls down"
    assert seen[0] < max_y * 0.1
    assert abs(seen[-1] - max_y) <= 2
    # A drag does not count as a click on the mark under the release point.
    assert abs(_settle_scroll(page) - max_y) <= 2


def test_drag_keeps_scrolling_outside_the_strip(page: Page, interactive_server: str):
    _load(page, interactive_server)
    track = _track(page)
    x = _strip_x(page)
    page.mouse.move(x, track["y"] + 10)
    page.mouse.down()
    page.mouse.move(x - 300, track["y"] + track["height"] / 2)  # pointer capture
    mid = page.evaluate("() => window.scrollY")
    page.mouse.up()
    assert mid > 0


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_viewport_box_tracks_scroll(page: Page, interactive_server: str, theme):
    _load(page, interactive_server, theme=theme)
    sh, ih = page.evaluate("() => [document.documentElement.scrollHeight, innerHeight]")
    track = _track(page)
    for y in (0, 1000, 2500, sh - ih):
        page.evaluate("(y) => window.scrollTo({ top: y, behavior: 'instant' })", y)
        page.evaluate("() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))")
        sy = page.evaluate("() => window.scrollY")
        box = page.locator(".rsm-minimap-box").bounding_box()
        assert abs(box["y"] - track["y"] - sy / sh * track["height"]) <= 1
        assert abs(box["height"] - ih / sh * track["height"]) <= 1
    # Inset 8px from both sides of the strip.
    assert abs(box["x"] - track["x"] - 8) <= 0.5
    assert abs(box["width"] - (track["width"] - 16)) <= 0.5
    # Its bottom edge reaches the bottom of the strip at the end of the page.
    assert abs(box["y"] + box["height"] - (track["y"] + track["height"])) <= 1


# ---------------------------------------------------------------------------
# Recomputing


def test_folding_a_proof_moves_the_marks_below_it_up(page: Page, interactive_server: str):
    _load(page, interactive_server)
    before = {m["label"]: m["y"] for m in _marks(page)}
    page.evaluate(
        "() => document.querySelector('#prf-long > .hr-collapse-zone > .hr-collapse').click()"
    )
    page.wait_for_timeout(50)
    page.wait_for_timeout(300)  # past the debounce
    after = {m["label"]: m["y"] for m in _marks(page)}
    for label in ("Widget 2.1", "3. Discussion", "Figure 3.1", "3.1. Outlook"):
        assert after[label] < before[label] - 5, label
    for m in _marks(page):
        assert abs(m["y"] - m["expected"]) <= 2, m


def test_folding_a_section_drops_the_marks_inside_it(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.evaluate(
        "() => document.querySelector('#sec-intro > .heading > .hr-collapse-zone > .hr-collapse').click()"
    )
    page.wait_for_timeout(350)
    labels = [m["label"] for m in _marks(page)]
    assert "1. Introduction" in labels
    assert "1.1. Background" not in labels
    assert "Figure 1.1" not in labels


def test_resize_recomputes(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.set_viewport_size({"width": 900, "height": 700})
    page.wait_for_timeout(400)
    for m in _marks(page):
        assert abs(m["y"] - m["expected"]) <= 2, m


# ---------------------------------------------------------------------------
# Keyboard and screen readers


def _tab_to_strip(page: Page) -> None:
    page.locator("body").focus()
    page.evaluate("() => document.activeElement && document.activeElement.blur()")
    for _ in range(40):
        page.keyboard.press("Tab")
        if page.evaluate("() => !!document.activeElement.closest('.rsm-minimap')"):
            return
    raise AssertionError("Tab never reached the minimap")


def _active_label(page: Page) -> str:
    return page.evaluate("() => document.activeElement.textContent")


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_tab_reaches_the_strip_and_arrows_walk_every_mark(page: Page, interactive_server: str, theme):
    _load(page, interactive_server, theme=theme)
    _tab_to_strip(page)
    seen = [_active_label(page)]
    for _ in range(len(LABELS) - 1):
        page.keyboard.press("ArrowDown")
        seen.append(_active_label(page))
        # The focused mark is ringed and its label shows.
        state = page.evaluate(
            """() => {
            const m = document.querySelector('.rsm-minimap-mark.is-focused');
            return { ring: m && getComputedStyle(m).outlineStyle,
                     tip: document.querySelector('.rsm-minimap-tip').textContent,
                     tipVisible: getComputedStyle(document.querySelector('.rsm-minimap-tip')).visibility };
        }"""
        )
        assert state["ring"] == "solid"
        assert state["tip"] == seen[-1]
        assert state["tipVisible"] == "visible"
    assert seen == LABELS
    # Past the end stays on the last mark; Up and Left go back.
    page.keyboard.press("ArrowDown")
    assert _active_label(page) == LABELS[-1]
    page.keyboard.press("ArrowUp")
    assert _active_label(page) == LABELS[-2]
    page.keyboard.press("ArrowLeft")
    assert _active_label(page) == LABELS[-3]
    page.keyboard.press("ArrowRight")
    assert _active_label(page) == LABELS[-2]
    page.keyboard.press("Home")
    assert _active_label(page) == LABELS[0]
    page.keyboard.press("End")
    assert _active_label(page) == LABELS[-1]


def test_strip_is_one_tab_stop(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _tab_to_strip(page)
    page.keyboard.press("Tab")
    assert not page.evaluate("() => !!document.activeElement.closest('.rsm-minimap')")
    page.keyboard.press("Shift+Tab")
    assert page.evaluate("() => !!document.activeElement.closest('.rsm-minimap')")


@pytest.mark.parametrize("key", ["Enter", " "], ids=["enter", "space"])
def test_enter_or_space_jumps_and_keeps_focus(page: Page, interactive_server: str, key):
    _load(page, interactive_server, reduced=True)
    url = page.url
    _tab_to_strip(page)
    for _ in range(LABELS.index("2. Results")):
        page.keyboard.press("ArrowDown")
    page.keyboard.press(key)
    _settle_scroll(page)
    assert abs(_top_in_viewport(page, "sec-results") - DESKTOP["height"] / 2) <= 2
    assert _active_label(page) == "2. Results"
    assert page.url == url, "a jump from the map does not change the address"


def test_escape_leaves_the_strip_for_the_text(page: Page, interactive_server: str):
    _load(page, interactive_server, reduced=True)
    _tab_to_strip(page)
    for _ in range(LABELS.index("3. Discussion")):
        page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")
    page.keyboard.press("Escape")
    assert page.evaluate("() => document.activeElement.id") == "sec-disc"
    assert not page.evaluate("() => !!document.activeElement.closest('.rsm-minimap')")
    assert page.locator(".rsm-minimap-mark.is-focused").count() == 0


def test_marks_are_exposed_as_a_list_of_links(page: Page, interactive_server: str):
    _load(page, interactive_server)
    nav = page.get_by_role("navigation", name="Document map")
    assert nav.count() == 1
    links = nav.get_by_role("link")
    assert links.all_text_contents() == LABELS
    hrefs = [links.nth(i).get_attribute("href") for i in range(links.count())]
    assert hrefs[0] == "#sec-intro" and hrefs[4] == "#wid-a"
    assert page.locator(".rsm-minimap-track").get_attribute("aria-hidden") == "true"


def test_keyboard_scrolling_still_works(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.mouse.click(600, 400)  # focus the page, not a control
    page.evaluate("() => document.activeElement && document.activeElement.blur()")
    start = page.evaluate("() => window.scrollY")
    for key in ("PageDown", "Space", "ArrowDown"):
        page.keyboard.press(key)
        y = _settle_scroll(page)
        assert y > start, key
        start = y
    page.keyboard.press("PageUp")
    assert _settle_scroll(page) < start


# ---------------------------------------------------------------------------
# Phones


def _phone_state(page: Page) -> dict:
    return page.evaluate(
        """() => {
        const cs = getComputedStyle(document.querySelector('.rsm-minimap'));
        return { opacity: parseFloat(cs.opacity), events: cs.pointerEvents,
                 cls: document.querySelector('.rsm-minimap').className };
    }"""
    )


def test_phone_strip_hidden_at_rest_and_lets_taps_through(page: Page, interactive_server: str):
    _load(page, interactive_server, size=PHONE)
    s = _phone_state(page)
    assert s["opacity"] == 0 and s["events"] == "none"
    hit = page.evaluate(
        "() => !!document.elementFromPoint(370, 300).closest('.rsm-minimap')"
    )
    assert not hit, "a tap at the edge reaches the text"


def test_phone_strip_shows_on_scroll_and_fades_after(page: Page, interactive_server: str):
    _load(page, interactive_server, size=PHONE)
    elapsed = page.evaluate(
        """() => new Promise((resolve) => {
        const nav = document.querySelector('.rsm-minimap');
        const t0 = performance.now();
        window.scrollBy(0, 200);
        const tick = () => {
            const cs = getComputedStyle(nav);
            if (parseFloat(cs.opacity) > 0 && cs.pointerEvents === 'auto') resolve(performance.now() - t0);
            else if (performance.now() - t0 > 1000) resolve(9999);
            else requestAnimationFrame(tick);
        };
        tick();
    })"""
    )
    assert elapsed < 100
    page.wait_for_timeout(700)
    assert "is-awake" in _phone_state(page)["cls"], "still showing soon after the scroll"
    page.wait_for_timeout(900)  # past 1.2s since the scroll, plus the fade
    s = _phone_state(page)
    assert "is-awake" not in s["cls"]
    assert s["opacity"] == 0 and s["events"] == "none"


def test_phone_strip_is_drawn_16px_with_a_24px_hit_area(page: Page, interactive_server: str):
    _load(page, interactive_server, size=PHONE)
    page.evaluate("() => window.scrollBy(0, 50)")
    page.wait_for_timeout(150)
    nav = page.locator(".rsm-minimap").bounding_box()
    track = _track(page)
    assert nav["width"] == 24 and nav["x"] + nav["width"] == PHONE["width"]
    assert track["width"] == 16 and track["x"] + track["width"] == PHONE["width"]
    hit = page.evaluate(
        "() => !!document.elementFromPoint(window.innerWidth - 23, 300).closest('.rsm-minimap')"
    )
    assert hit, "the 8px left of the drawn strip still belongs to it"


def test_phone_strip_stops_above_the_bottom_bar(page: Page, interactive_server: str):
    _load(page, interactive_server, size=PHONE)
    nav = page.locator(".rsm-minimap").bounding_box()
    bar = page.locator(".rail-strip").bounding_box()
    assert nav["y"] + nav["height"] <= bar["y"] + 1


def _touch(cdp, kind: str, x: float, y: float) -> None:
    points = [] if kind == "touchEnd" else [{"x": x, "y": y}]
    cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": points})


@pytest.fixture
def touch_page(browser: Browser):
    ctx = browser.new_context(viewport=PHONE, has_touch=True, is_mobile=True)
    page = ctx.new_page()
    yield page
    ctx.close()


def _load_touch(page: Page, server: str) -> None:
    page.goto(f"{server}/minimap.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".rsm-minimap .rsm-minimap-mark", state="attached")
    page.wait_for_timeout(400)


def test_phone_touch_drag_scrolls_the_page(touch_page: Page, interactive_server: str):
    page = touch_page
    _load_touch(page, interactive_server)
    cdp = page.context.new_cdp_session(page)
    page.evaluate("() => window.scrollBy(0, 1)")  # wake the strip
    page.wait_for_timeout(150)
    track = _track(page)
    x = PHONE["width"] - 6
    _touch(cdp, "touchStart", x, track["y"] + 4)
    seen = []
    for i in range(1, 11):
        _touch(cdp, "touchMove", x, track["y"] + 4 + (track["height"] - 8) * i / 10)
        seen.append(page.evaluate("() => window.scrollY"))
    # Still showing while the finger is down, past the fade delay.
    page.wait_for_timeout(1400)
    assert "is-awake" in _phone_state(page)["cls"] or "is-touching" in _phone_state(page)["cls"]
    assert _phone_state(page)["opacity"] == 1
    _touch(cdp, "touchEnd", x, 0)
    max_y = page.evaluate("() => document.documentElement.scrollHeight - innerHeight")
    assert seen == sorted(seen)
    assert seen[-1] > max_y * 0.9


def test_phone_tap_near_a_mark_shows_its_label(touch_page: Page, interactive_server: str):
    page = touch_page
    _load_touch(page, interactive_server)
    cdp = page.context.new_cdp_session(page)
    page.evaluate("() => window.scrollBy(0, 1)")
    page.wait_for_timeout(150)
    m = _mark(page, "2. Results")
    track = _track(page)
    y = track["y"] + m["y"] + 20  # within the 24px touch reach, not the 12px mouse one
    _touch(cdp, "touchStart", PHONE["width"] - 6, y)
    assert page.locator(".rsm-minimap-tip").inner_text() == "2. Results"
    assert page.locator(".rsm-minimap-tip").is_visible()
    _touch(cdp, "touchEnd", 0, 0)
    _settle_scroll(page)
    assert abs(_top_in_viewport(page, "sec-results") - PHONE["height"] / 2) <= 2


def test_phone_reduced_motion_has_no_fade(page: Page, interactive_server: str):
    _load(page, interactive_server, size=PHONE, reduced=True)
    durations = page.evaluate(
        "() => getComputedStyle(document.querySelector('.rsm-minimap')).transitionDuration"
    )
    # The global reduced-motion rule sets 0.00001s rather than 0s.
    assert all(float(d.strip().rstrip("s")) < 0.001 for d in durations.split(","))


# ---------------------------------------------------------------------------
# Switches


def _reading_opt(page: Page, value: str):
    return page.locator(f'.reading-row[data-control="minimap"] .reading-opt[data-value="{value}"]')


def _scrollbar_hidden(page: Page) -> bool:
    return page.evaluate(
        "() => document.documentElement.classList.contains('rsm-minimap-on')"
        " && getComputedStyle(document.documentElement).scrollbarWidth === 'none'"
    )


def _native_scrollbar(page: Page) -> bool:
    # Headless Chromium draws no scrollbars (--hide-scrollbars), so widths
    # cannot show one: check that nothing hides it.
    return page.evaluate(
        "() => !document.documentElement.classList.contains('rsm-minimap-on')"
        " && getComputedStyle(document.documentElement).scrollbarWidth === 'auto'"
    )


def test_reading_toggle_turns_the_strip_off_live_and_persists(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.click('.rail-strip-btn[data-view="reading"]')
    page.wait_for_selector(".proof-rail.open")
    assert _reading_opt(page, "on").get_attribute("aria-pressed") == "true"
    _reading_opt(page, "off").click()
    assert page.locator(".rsm-minimap").count() == 0
    assert _native_scrollbar(page), "the native scrollbar is back"
    assert _reading_opt(page, "off").get_attribute("aria-pressed") == "true"

    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_timeout(300)
    assert page.locator(".rsm-minimap").count() == 0
    assert _native_scrollbar(page)

    page.click('.rail-strip-btn[data-view="reading"]')
    _reading_opt(page, "on").click()
    page.wait_for_selector(".rsm-minimap .rsm-minimap-mark", state="attached")
    assert _scrollbar_hidden(page)
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".rsm-minimap .rsm-minimap-mark", state="attached")


def test_reading_toggle_keeps_the_sidebar_column_in_place(page: Page, interactive_server: str):
    # Showing or hiding the scrollbar changes the viewport width; the column the
    # sidebar places must follow so the page never scrolls sideways.
    _load(page, interactive_server)
    page.click('.rail-strip-btn[data-view="reading"]')
    page.wait_for_selector(".proof-rail.open")
    _reading_opt(page, "off").click()
    page.wait_for_timeout(400)
    assert page.evaluate(
        "() => document.documentElement.scrollWidth <= document.documentElement.clientWidth"
    )
    _reading_opt(page, "on").click()
    page.wait_for_timeout(400)
    assert page.evaluate("() => document.documentElement.scrollWidth === window.innerWidth")


def test_print_hides_the_strip(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.emulate_media(media="print")
    assert page.evaluate(
        "() => getComputedStyle(document.querySelector('.rsm-minimap')).display"
    ) == "none"


def test_body_flag_keeps_the_strip_off(page: Page, interactive_server: str):
    # What :config: { :minimap: false } emits (body[data-minimap="false"]).
    page.set_viewport_size(DESKTOP)
    page.route(
        "**/minimap.html",
        lambda route: route.fulfill(
            body=route.fetch().text().replace("<body ", '<body data-minimap="false" ', 1),
            content_type="text/html",
        ),
    )
    page.goto(f"{interactive_server}/minimap.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_timeout(300)
    assert page.locator(".rsm-minimap").count() == 0
    assert _native_scrollbar(page)


def test_minimap_works_without_the_sidebar(page: Page, interactive_server: str):
    page.set_viewport_size(DESKTOP)
    page.goto(f"{interactive_server}/basic.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_timeout(300)
    assert page.locator(".rsm-minimap").count() == 1
    labels = page.locator(".rsm-minimap-links a").all_text_contents()
    assert labels[:2] == ["1. Section One", "2. Section Two"]


@pytest.mark.skip(
    reason="rsm-3am: :minimap: is not yet a meta key in the tree-sitter-rsm grammar "
    "(metakey_any). Enable once the grammar change lands."
)
def test_config_flag_removes_the_strip(page: Page, tmp_path: Path):
    src = ":config: { :minimap: false }\n\n# Off\n\n## One\n\nText.\n"
    (tmp_path / "off.rsm").write_text(src)
    rsm.build(
        path=str(tmp_path / "off.rsm"),
        output_dir=str(tmp_path),
        output_filename="off.html",
        write_output=True,
        handrails=True,
        standalone=True,
        strict=True,
        sidebar=True,
    )
    page.goto((tmp_path / "off.html").as_uri())
    page.wait_for_function(RSM_READY, timeout=10_000)
    assert page.locator(".rsm-minimap").count() == 0
    assert page.locator('.reading-row[data-control="minimap"]').count() == 0
    assert _native_scrollbar(page), "the native scrollbar stays"
