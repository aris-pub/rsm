"""Regression: a :calc: nested inside a proof step must keep its because-mark
control clickable and hoverable.

In the real paper a :calc: lives inside a proof step's :p:, and that PARENT
step's info-zone (.hr-info, z-index:1) painted OVER the calc row's per-row
disclosure control (the because-mark in its own info-zone), swallowing clicks
and hover. braiid.css fixes this by lifting the calc row's info-zone above the
parent (z-index:5) and making the .hr-collapse a solid, top-most hit target.

The original calc test missed this because it used a TOP-LEVEL calc fixture (no
parent step to overlap) and clicked via Playwright element-click, which
hit-tests the control box directly rather than the visible pixel. This test
uses a NESTED fixture (calc_nested.rsm) and drives a real pixel click through
document.elementFromPoint / page.mouse, so the parent overlap can actually bite.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _bring_calc_control_into_view(page: Page) -> dict:
    """Scroll the nested calc's first because-mark into view and return its
    viewport-center coordinates plus a hit-target probe."""
    return page.evaluate(
        """() => {
            const row = document.querySelector('.calc > .step');
            const ctrl = row.querySelector(':scope > .hr-info-zone .hr-collapse');
            ctrl.scrollIntoView({block: 'center'});
            const r = ctrl.getBoundingClientRect();
            const cx = r.left + r.width / 2;
            const cy = r.top + r.height / 2;
            const at = document.elementFromPoint(cx, cy);
            return {
                cx: Math.round(cx),
                cy: Math.round(cy),
                // The topmost painted element at the mark's center is this very
                // control, NOT a parent step's info-zone occluding it.
                hitIsThisControl: !!at && at.closest('.hr-collapse') === ctrl,
                hitClass: at ? at.className.toString() : null,
                hitParentHrInfo:
                    at && at.closest('.hr-info')
                        ? at.closest('.hr-info').className.toString()
                        : null,
                rowCollapsed: row.classList.contains('hr-collapsed'),
            };
        }"""
    )


def test_nested_calc_control_is_top_hit_target(page: Page, interactive_server: str):
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{interactive_server}/calc_nested.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    # Let the handrail layout settle before measuring geometry.
    page.wait_for_timeout(400)

    probe = _bring_calc_control_into_view(page)
    assert probe["hitIsThisControl"], (
        "a parent step's info-zone occludes the calc because-mark: "
        f"elementFromPoint hit {probe['hitClass']!r} "
        f"(parent .hr-info {probe['hitParentHrInfo']!r}), not the .hr-collapse"
    )


def test_nested_calc_pixel_click_discloses_justification(
    page: Page, interactive_server: str
):
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{interactive_server}/calc_nested.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_timeout(400)

    row = page.locator(".calc > .step").first
    just = row.locator(".subproof").first
    # At rest the relation (math) shows and the justification is hidden.
    expect(row.locator(".statement .math").first).to_be_visible()
    expect(just).to_be_hidden()
    assert "hr-collapsed" in (row.get_attribute("class") or "")

    probe = _bring_calc_control_into_view(page)
    # Real pixel click at the visible mark (hit-tests the painted pixel, so a
    # parent overlap that swallows the click would make this fail).
    page.mouse.click(probe["cx"], probe["cy"])

    expect(just).to_be_visible()
    assert "hr-collapsed" not in (row.get_attribute("class") or "")


def test_nested_calc_hover_flips_glyph_color(page: Page, interactive_server: str):
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{interactive_server}/calc_nested.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_timeout(400)

    probe = _bring_calc_control_into_view(page)

    # The because-mark is drawn with a CSS mask on ::before, themed via
    # background-color (gray --medium at rest, primary on row hover). Read the
    # pseudo-element color directly.
    def glyph_color() -> str:
        return page.evaluate(
            """() => {
                const ctrl = document.querySelector(
                    '.calc > .step > .hr-info-zone .hr-collapse');
                return getComputedStyle(ctrl, '::before').backgroundColor;
            }"""
        )

    rest_color = glyph_color()
    # Move the mouse over the visible pixel so :hover applies (a parent overlap
    # would steal the hover and the color would not change).
    page.mouse.move(probe["cx"], probe["cy"])
    page.wait_for_timeout(200)
    hover_color = glyph_color()

    assert rest_color != hover_color, (
        f"because-mark color did not flip on hover (rest={rest_color!r}, "
        f"hover={hover_color!r}): the parent info-zone is stealing the hover"
    )
