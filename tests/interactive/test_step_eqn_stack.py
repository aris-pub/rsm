"""A step whose first line is a display equation shows its step number and the
equation's number stacked in one info cell, instead of one on top of the other.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _open(page: Page, server: str, width: int) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{server}/step_eqn_stack.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_timeout(300)


def _overlap(a: dict, b: dict) -> bool:
    return not (
        a["x"] + a["width"] <= b["x"]
        or b["x"] + b["width"] <= a["x"]
        or a["y"] + a["height"] <= b["y"]
        or b["y"] + b["height"] <= a["y"]
    )


@pytest.mark.parametrize("width", [375, 1280])
def test_step_number_sits_above_the_equation_number(
    page: Page, interactive_server: str, width: int
):
    _open(page, interactive_server, width)
    cell = page.locator(".hr-info-stack")
    expect(cell).to_have_count(1)
    step_num = cell.locator(".step-number")
    eqn_num = cell.locator(".eqn-number")
    expect(step_num).to_have_text("⟨2⟩")
    expect(eqn_num).to_have_text("(1.2)")
    expect(eqn_num).to_be_visible()
    s, e = step_num.bounding_box(), eqn_num.bounding_box()
    assert not _overlap(s, e)
    assert s["y"] + s["height"] <= e["y"] + 1
    assert abs((s["x"] + s["width"] / 2) - (e["x"] + e["width"] / 2)) <= 2


@pytest.mark.parametrize(
    "width",
    [
        pytest.param(
            375,
            marks=pytest.mark.xfail(
                strict=True,
                reason="at 375 the equation after step 1's short text line sits "
                "close enough that (1.1) touches step 1's number, as on main",
            ),
        ),
        1280,
    ],
)
def test_no_number_in_the_info_column_overlaps_another(
    page: Page, interactive_server: str, width: int
):
    _open(page, interactive_server, width)
    boxes = page.eval_on_selector_all(
        ".proof .step-number p, .proof .eqn-number p",
        """els => els.map(e => { const r = e.getBoundingClientRect();
             return {x: r.x, y: r.y, width: r.width, height: r.height,
                     text: e.textContent}; })""",
    )
    assert len(boxes) == 5
    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            assert not _overlap(a, b), f"{a['text']} overlaps {b['text']}"
