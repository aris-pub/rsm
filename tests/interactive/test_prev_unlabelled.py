"""The tooltip of a :prev: that points at a step without a label (rsm-c37x)."""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"


def test_hovering_prev_shows_the_step(page: Page, interactive_server: str):
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{interactive_server}/prev_unlabelled.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    ref = page.locator(".manuscript a.reference").first
    href = ref.get_attribute("href")
    assert href != "#"
    expect(page.locator(f".manuscript div.step{href}")).to_have_count(1)
    ref.hover()
    tip = page.locator(".tooltipster-base").last
    expect(tip).to_be_visible(timeout=3000)
    expect(tip).to_contain_text("The first number is fine")
    expect(tip.locator(".error")).to_have_count(0)
