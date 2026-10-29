"""WCAG 2.1 AA checks for asides (rsm-zvn.2, .3, .4, rsm-aul): in the margin
column, closed and opened below their block, and lit by hover, in both themes.
The control is the phrase the aside is about."""

import shutil
from pathlib import Path

import pytest
from axe_playwright_python.sync_playwright import Axe

pytestmark = pytest.mark.accessibility

FIXTURES = Path(__file__).parents[1] / "interactive" / "fixtures"
SRC = (FIXTURES / "asides.rsm").read_text()
ALL = ["a-one", "a-two", "a-three", "a-fig", "a-item", "a-step", "a-pair-1", "a-pair-2"]


def _fmt(violations):
    lines = []
    for v in violations:
        targets = ", ".join(
            (n["target"][0] if n.get("target") else "?") for n in v["nodes"][:6]
        )
        lines.append(f"[{v['impact']}] {v['id']}: {v['help']}  ->  {targets}")
    return "\n".join(lines)


def _new_violations(page):
    """Axe violations, less one that main already has: at 375px a figure's
    image can be wider than its box, so the box scrolls sideways and axe asks
    for it to be focusable. That is not caused by asides."""
    out = []
    for v in Axe().run(page).response["violations"]:
        if v["id"] == "scrollable-region-focusable":
            v = dict(v)
            v["nodes"] = [
                n for n in v["nodes"] if not n["target"][0].endswith("> .hr-bare.hr")
            ]
            if not v["nodes"]:
                continue
        out.append(v)
    return out


def _force_theme(page, theme):
    page.evaluate(
        "(t) => { const c = document.documentElement.classList;"
        " c.remove('light-theme', 'dark-theme'); c.add(t + '-theme'); }",
        theme,
    )
    page.wait_for_timeout(400)


def _serve(serve_rsm_a11y, page, tmp_path, width):
    (tmp_path / "output" / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURES / "figure-light.png", tmp_path / "output" / "assets" / "figure-light.png")
    page.set_viewport_size({"width": width, "height": 900})
    return serve_rsm_a11y(SRC, sidebar=True)


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("width", [375, 1280])
def test_asides_at_rest_wcag(serve_rsm_a11y, page, tmp_path, width, theme):
    page = _serve(serve_rsm_a11y, page, tmp_path, width)
    margin = page.evaluate(
        "() => document.documentElement.classList.contains('rsm-margin')"
    )
    assert margin == (width == 1280)
    _force_theme(page, theme)
    v = _new_violations(page)
    assert not v, "\n" + _fmt(v)


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_opened_asides_wcag(serve_rsm_a11y, page, tmp_path, theme):
    page = _serve(serve_rsm_a11y, page, tmp_path, 375)
    for i in ALL:
        page.click(f"#call-{i}")
    _force_theme(page, theme)
    v = _new_violations(page)
    assert not v, "\n" + _fmt(v)


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("width", [375, 1280])
def test_lit_aside_wcag(serve_rsm_a11y, page, tmp_path, width, theme):
    """A lit aside and its lit phrase (deeper tint) still meet contrast."""
    page = _serve(serve_rsm_a11y, page, tmp_path, width)
    if width == 375:
        page.click("#call-a-two")
    _force_theme(page, theme)
    page.focus("#call-a-two")
    page.wait_for_timeout(250)
    v = _new_violations(page)
    assert not v, "\n" + _fmt(v)


# Contrast of the aside's text on its tint and of the phrase's text on its own
# background (the page at rest, the lit tint when lit), measured directly. The
# colours are drawn onto a canvas so color-mix() results come back as sRGB.
_CONTRAST = """(id) => {
    const cv = document.createElement('canvas'); cv.width = cv.height = 1;
    const cx = cv.getContext('2d', {willReadFrequently: true});
    const rgb = (c) => { cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000';
        cx.fillStyle = c; cx.fillRect(0, 0, 1, 1); return [...cx.getImageData(0, 0, 1, 1).data]; };
    const lum = ([r, g, b]) => [r, g, b].map((v) => { v /= 255;
        return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; })
        .reduce((s, v, i) => s + v * [0.2126, 0.7152, 0.0722][i], 0);
    const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);
        return (x + 0.05) / (y + 0.05); };
    const a = document.getElementById(id);
    const m = document.getElementById('call-' + id);
    const bg = rgb(getComputedStyle(a).backgroundColor);
    const mbg = getComputedStyle(m).backgroundColor;
    const page = rgb(getComputedStyle(document.body).backgroundColor);
    const phraseBg = mbg === 'rgba(0, 0, 0, 0)' ? page : rgb(mbg);
    return {
        text: ratio(rgb(getComputedStyle(a).color), bg),
        phrase: ratio(rgb(getComputedStyle(m).color), phraseBg),
        bgAlpha: bg[3],
    };
}"""


def _with_accent(src: str, accent: str) -> str:
    if not accent:
        return src
    title, rest = src.split("\n", 1)
    return f"{title}\n\n:config: {{\n  :accent: {accent}\n}}\n::\n{rest}"


def _contrast(serve_rsm_a11y, page, tmp_path, accent, theme, state) -> dict:
    (tmp_path / "output" / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURES / "figure-light.png", tmp_path / "output" / "assets" / "figure-light.png")
    page.set_viewport_size({"width": 1280, "height": 900})
    page = serve_rsm_a11y(_with_accent(SRC, accent), sidebar=True)
    if accent:
        assert page.evaluate("() => document.documentElement.dataset.accent") == accent
    _force_theme(page, theme)
    if state == "lit":
        page.hover("#a-one")
    else:
        page.mouse.move(1, 1)
    page.wait_for_timeout(300)
    lit = page.evaluate("() => document.getElementById('a-one').classList.contains('rsm-aside-lit')")
    assert lit == (state == "lit")
    c = page.evaluate(_CONTRAST, "a-one")
    assert c["bgAlpha"] == 255, c
    return c


CASES = [
    pytest.param(accent, theme, state, id=f"{state}-{theme}-{accent or 'default'}")
    for accent in ["", "green"]
    for theme in ["light", "dark"]
    for state in ["rest", "lit"]
]


@pytest.mark.parametrize("accent,theme,state", CASES)
def test_aside_text_contrast(serve_rsm_a11y, page, tmp_path, accent, theme, state):
    c = _contrast(serve_rsm_a11y, page, tmp_path, accent, theme, state)
    assert c["text"] >= 4.5, c


@pytest.mark.parametrize("accent,theme,state", CASES)
def test_phrase_text_contrast(serve_rsm_a11y, page, tmp_path, accent, theme, state):
    c = _contrast(serve_rsm_a11y, page, tmp_path, accent, theme, state)
    assert c["phrase"] >= 4.5, c


_CONTROL = """(id) => {
    const m = document.getElementById('call-' + id);
    return {
        tag: m.tagName, href: m.getAttribute('href'), tabIndex: m.tabIndex,
        name: m.textContent.replace(/\\s+/g, ' ').trim(),
        expanded: m.getAttribute('aria-expanded'),
        controls: m.getAttribute('aria-controls'),
        role: m.getAttribute('role'),
    };
}"""


@pytest.mark.parametrize("width", [375, 1280])
def test_phrase_is_a_named_control(serve_rsm_a11y, page, tmp_path, width):
    """The phrase is focusable, its accessible name says it is about an aside,
    and on narrow screens it says whether the aside is open."""
    page = _serve(serve_rsm_a11y, page, tmp_path, width)
    link = page.get_by_role("link", name="the next one (aside)", exact=True)
    assert link.count() == 1
    assert link.get_attribute("id") == "call-a-one"
    c = page.evaluate(_CONTROL, "a-one")
    assert c["tag"] == "A" and c["href"] == "#a-one" and c["tabIndex"] == 0, c
    assert c["controls"] == "a-one", c
    assert c["role"] is None, c
    if width == 375:
        assert c["expanded"] == "false", c
        page.focus("#call-a-one")
        page.keyboard.press("Enter")
        assert page.evaluate(_CONTROL, "a-one")["expanded"] == "true"
        page.keyboard.press("Space")
        assert page.evaluate(_CONTROL, "a-one")["expanded"] == "false"
    else:
        assert c["expanded"] is None, c
