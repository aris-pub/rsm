"""WCAG 2.1 AA checks for captions in the margin column and stacked under
their block (rsm-coj), in both themes."""

import shutil
from pathlib import Path

import pytest
from axe_playwright_python.sync_playwright import Axe

pytestmark = pytest.mark.accessibility

FIXTURES = Path(__file__).parents[1] / "interactive" / "fixtures"
SRC = (FIXTURES / "margin_captions.rsm").read_text()


def _fmt(violations):
    lines = []
    for v in violations:
        targets = ", ".join(
            (n["target"][0] if n.get("target") else "?") for n in v["nodes"][:6]
        )
        lines.append(f"[{v['impact']}] {v['id']}: {v['help']}  ->  {targets}")
    return "\n".join(lines)


def _new_violations(page):
    """Axe violations, less one that main already has: at 375px the first
    figure's image is wider than its box, so the box scrolls sideways and axe
    asks for it to be focusable. That is not caused by captions."""
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


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("width", [375, 1440])
def test_margin_captions_wcag(serve_rsm_a11y, page, tmp_path, width, theme):
    (tmp_path / "output" / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURES / "figure-light.png", tmp_path / "figure-light.png")
    shutil.copy(FIXTURES / "figure-light.png", tmp_path / "output" / "assets" / "figure-light.png")
    page.set_viewport_size({"width": width, "height": 900})
    page = serve_rsm_a11y(SRC, sidebar=True)
    margin = page.evaluate(
        "() => document.documentElement.classList.contains('rsm-margin')"
    )
    assert margin == (width == 1440)
    _force_theme(page, theme)
    v = _new_violations(page)
    assert not v, "\n" + _fmt(v)


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_focused_margin_caption_wcag(serve_rsm_a11y, page, tmp_path, theme):
    """With a caption focused (its rail and highlight shown) nothing fails."""
    (tmp_path / "output" / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURES / "figure-light.png", tmp_path / "output" / "assets" / "figure-light.png")
    page.set_viewport_size({"width": 1440, "height": 900})
    page = serve_rsm_a11y(SRC, sidebar=True)
    _force_theme(page, theme)
    page.focus("#fig-a > figcaption")
    page.wait_for_timeout(200)
    v = _new_violations(page)
    assert not v, "\n" + _fmt(v)
