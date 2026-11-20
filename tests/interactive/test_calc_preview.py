"""Reference previews of a labelled :calc: (rsm-80l).

The preview shows the calc as it appears in the page: its rows, typeset, and
its number, with no handrail controls. A pinned calc is a copy of the block
with its handrail."""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"
HREF = "#eq-chain"
CHROME = (
    ".hr-collapse, .hr-collapse-zone, .hr-menu-zone, .hr-border-zone, "
    ".hr-spacer-zone, .hr-border-dots, [data-menu-label], [tabindex]"
)


def _load(page: Page, server: str) -> None:
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/calc_preview.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)


def _preview(page: Page):
    ref = page.locator(f'.manuscript a.reference[href="{HREF}"]').first
    ref.scroll_into_view_if_needed()
    ref.hover()
    tip = page.locator(f'.tooltipster-base:has(.ref-pin[data-pin-target="{HREF}"])').last
    expect(tip).to_be_visible(timeout=3000)
    return tip


def _assert_calc_excerpt(scope) -> None:
    calc = scope.locator(".calc-preview")
    expect(calc).to_have_count(1)
    rows = calc.locator(".step")
    expect(rows).to_have_count(3)
    # Each row's relation is typeset, not left as raw TeX.
    for i in range(3):
        expect(rows.nth(i).locator(".statement math").first).to_be_visible()
    assert "\\(" not in calc.inner_text()
    expect(calc.locator(".eqn-number")).to_have_text("(1.1)")
    expect(calc.locator(".eqn-number")).to_be_visible()
    expect(calc.locator(CHROME)).to_have_count(0)


def test_preview_shows_rows_and_number(page: Page, interactive_server: str):
    _load(page, interactive_server)
    tip = _preview(page)
    _assert_calc_excerpt(tip)
    # The number sits inside the preview and clear of the pin control.
    box = tip.locator(".tooltipster-content").bounding_box()
    num = tip.locator(".eqn-number").bounding_box()
    pin = tip.locator(".ref-pin").bounding_box()
    assert num["x"] + num["width"] <= box["x"] + box["width"]
    assert num["x"] + num["width"] <= pin["x"]


def test_pinned_calc_is_a_copy_with_its_handrail(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _preview(page).locator(".ref-pin").click()
    copy = page.locator(f'.rail-pinned-body > [data-pin-target="{HREF}"]')
    expect(copy).to_have_class(re.compile(r"\bcalc\b"))
    rows = copy.locator(":scope > .hr-content-zone > .step")
    expect(rows).to_have_count(3)
    for i in range(3):
        expect(rows.nth(i).locator(".statement math").first).to_be_visible()
    assert "\\(" not in copy.inner_text()
    expect(copy.locator(".eqn-number")).to_have_text("(1.1)")
    expect(copy.locator(":scope > .hr-border-zone .hr-border-dots")).to_have_count(1)
    expect(copy.locator(":scope > .hr-info-zone .pin-unpin")).to_have_count(1)


def test_preview_leaves_out_reasons_even_when_open(page: Page, interactive_server: str):
    # Previews are built at load, so the preview shows the page's default look
    # (no reasons) whatever the reader opened since.
    _load(page, interactive_server)
    row = page.locator(".manuscript #eq-chain .step").nth(1)
    row.locator(":scope > .hr-info-zone .hr-collapse").click()
    expect(row.locator(".subproof")).to_be_visible()
    tip = _preview(page)
    expect(tip.locator(".calc-preview .subproof")).to_have_count(0)
