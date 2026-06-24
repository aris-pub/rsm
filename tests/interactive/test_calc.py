"""The :calc: chain shows its relations at rest and discloses each justification
on demand, reusing the handrail collapse (a collapsed step shows its claim -- the
relation -- and hides its proof -- the justification)."""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def test_calc_relation_shown_justification_disclosed(page: Page, interactive_server: str):
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{interactive_server}/calc.html")
    page.wait_for_function(RSM_READY, timeout=10_000)

    row = page.locator(".calc > .step").first
    # At rest: the relation (math) is visible; its justification is hidden
    # (the step starts collapsed).
    expect(row.locator(".statement .math").first).to_be_visible()
    just = row.locator(".subproof").first
    expect(just).to_be_hidden()
    assert "hr-collapsed" in (row.get_attribute("class") or "")

    # Disclose via the because-mark in the info-zone (the right-margin per-row
    # slot): the native collapse control, reglyphed. It is shown at rest (the
    # calc's only affordance), so it is clickable without hovering first.
    marker = row.locator(":scope > .hr-info-zone .hr-collapse").first
    expect(marker).to_be_visible()
    marker.click()
    expect(just).to_be_visible()
    assert "hr-collapsed" not in (row.get_attribute("class") or "")
