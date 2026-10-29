"""A labelled :calc: is numbered like a display equation, at the top level and
inside a proof.

The chain's number sits in the info column, stacked directly above the first
row's because-mark, and the marks stay in one vertical line. Outside a proof
the rows start on the text column. Relation math is set at display size.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"
ROW = ":scope > .hr-content-zone > .step"
MARK = ":scope > .hr-info-zone .hr-collapse"


def _open(page: Page, server: str, width: int) -> None:
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{server}/calc_numbered.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_timeout(300)


def _boxes_overlap(a: dict, b: dict) -> bool:
    return not (
        a["x"] + a["width"] <= b["x"]
        or b["x"] + b["width"] <= a["x"]
        or a["y"] + a["height"] <= b["y"]
        or b["y"] + b["height"] <= a["y"]
    )


@pytest.mark.parametrize("calc_id", ["eq-top", "eq-inproof"])
@pytest.mark.parametrize("width", [375, 1280])
def test_number_stacks_above_the_first_mark(
    page: Page, interactive_server: str, calc_id: str, width: int
):
    _open(page, interactive_server, width)
    calc = page.locator(f"#{calc_id}")
    calc.scroll_into_view_if_needed()
    number = calc.locator(".eqn-number")
    expect(number).to_have_count(1)
    expect(number).to_be_visible()
    expected = "(1.2)" if calc_id == "eq-top" else "(2.1)"
    expect(number).to_have_text(expected)
    num_box = number.bounding_box()
    marks = calc.locator(f"{ROW} > .hr-info-zone .hr-collapse")
    assert marks.count() >= 2
    boxes = [marks.nth(i).bounding_box() for i in range(marks.count())]
    for i, box in enumerate(boxes):
        assert not _boxes_overlap(num_box, box), f"mark {i} overlaps the number"
    first = boxes[0]
    # Directly above the first mark, centred on the same x.
    assert num_box["y"] + num_box["height"] <= first["y"] + 1
    num_cx = num_box["x"] + num_box["width"] / 2
    assert abs(num_cx - (first["x"] + first["width"] / 2)) <= 2
    # The marks stay in one vertical line.
    centres = [b["x"] + b["width"] / 2 for b in boxes]
    assert max(centres) - min(centres) <= 1
    # Nothing runs past the right edge of the page.
    overflow = page.evaluate(
        "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    assert overflow <= 0


@pytest.mark.parametrize("width", [375, 1280])
def test_top_level_rows_start_on_the_text_column(
    page: Page, interactive_server: str, width: int
):
    _open(page, interactive_server, width)
    text_left = page.evaluate(
        """() => document.querySelector('.paragraph > .hr-content-zone p')
                 .getBoundingClientRect().left"""
    )
    row_left = page.evaluate(
        """() => document.querySelector(
                   '#eq-top > .hr-content-zone > .step .statement .math')
                 .getBoundingClientRect().left"""
    )
    assert abs(row_left - text_left) <= 2, (text_left, row_left)


@pytest.mark.parametrize("calc_id", ["eq-top", "eq-inproof"])
@pytest.mark.parametrize("width", [375, 1280])
def test_pixel_click_on_mark_discloses_reason(
    page: Page, interactive_server: str, calc_id: str, width: int
):
    _open(page, interactive_server, width)
    row = page.locator(f"#{calc_id}").locator(ROW).last
    reason = row.locator(".subproof").first
    expect(reason).to_be_hidden()
    mark = row.locator(MARK)
    mark.scroll_into_view_if_needed()
    box = mark.bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    # The mark must be the top element at its own centre, then a real click
    # there opens the reason.
    hit = page.evaluate(
        "([x, y]) => { const el = document.elementFromPoint(x, y);"
        " return !!el && !!el.closest('.hr-collapse'); }",
        [cx, cy],
    )
    assert hit, "something covers the because-mark"
    page.mouse.click(cx, cy)
    expect(reason).to_be_visible()


def test_relation_math_is_display_style(page: Page, interactive_server: str):
    _open(page, interactive_server, 1280)
    row_math = page.locator("#eq-top .statement .math").first
    assert row_math.locator('mstyle[displaystyle="true"]').count() >= 1
    reason_math = page.locator("#eq-top .subproof .math").first
    assert reason_math.locator("math").count() == 1
    assert reason_math.locator('mstyle[displaystyle="true"]').count() == 0


def test_rows_have_relation_menu_label(page: Page, interactive_server: str):
    _open(page, interactive_server, 1280)
    labels = page.eval_on_selector_all(
        ".calc .step", "els => els.map(e => e.dataset.menuLabel)"
    )
    assert labels and all(label == "Relation" for label in labels)
    assert "Step ⟨" not in page.locator(".manuscript").inner_text()
