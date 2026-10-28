"""WCAG 2.1 AA checks for asides (rsm-zvn.2, .3, .4): in the margin column,
closed and opened below their block, and lit by hover, in both themes."""

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
    (tmp_path / "output").mkdir(exist_ok=True)
    shutil.copy(FIXTURES / "figure-light.png", tmp_path / "output" / "figure-light.png")
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
    """A lit aside (deeper tint) and a filled marker still meet contrast."""
    page = _serve(serve_rsm_a11y, page, tmp_path, width)
    if width == 375:
        page.click("#call-a-two")
    _force_theme(page, theme)
    page.focus("#call-a-two")
    page.wait_for_timeout(250)
    v = _new_violations(page)
    assert not v, "\n" + _fmt(v)
