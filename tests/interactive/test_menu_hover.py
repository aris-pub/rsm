"""Test that the handrail menu stays open while the mouse is inside it."""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


class TestMenuStaysOpenOnHover:

    def test_menu_stays_open_when_moving_between_items(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/basic.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

        # Open the menu
        dots = page.locator(".hr:not(.hr-hidden) .hr-border-dots").first
        dots.click()

        menu = page.locator("#hr-menu-singleton .hr-menu")
        expect(menu).to_be_visible()

        # Get bounding boxes of two different menu items
        items = page.locator("#hr-menu-singleton .hr-menu-item:visible")
        assert items.count() >= 2, "Need at least two visible menu items"

        box0 = items.nth(0).bounding_box()
        box1 = items.nth(1).bounding_box()

        # Move mouse from center of first item to center of second item
        # using small steps so the browser fires real mouseleave/mouseenter
        page.mouse.move(
            box0["x"] + box0["width"] / 2,
            box0["y"] + box0["height"] / 2,
        )
        page.mouse.move(
            box1["x"] + box1["width"] / 2,
            box1["y"] + box1["height"] / 2,
            steps=10,
        )

        # Menu must still be visible
        expect(menu).to_be_visible()
