"""Interactive layout test for nested-handrail geometry.

A step nested inside a subproof has its info-zone (the number column) absolutely
positioned and pulled left over the content area. The content-zone must reserve
that width on its right, otherwise its text is drawn under the info-zone and gets
occluded when the block is painted on focus. This asserts the geometry directly
(no pixels), so it is deterministic.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def test_nested_step_content_zone_clears_info_zone(page: Page, interactive_server: str):
    page.goto(f"{interactive_server}/collapse-menu.html")
    page.wait_for_function(RSM_READY, timeout=10_000)

    step = page.locator("#stp-inner-a")  # a step one subproof deep (info-zone pulled left)
    content = step.locator(":scope > .hr-content-zone")
    info = step.locator(":scope > .hr-info-zone")

    cbox = content.bounding_box()
    ibox = info.bounding_box()
    assert cbox is not None and ibox is not None

    content_right = cbox["x"] + cbox["width"]
    info_left = ibox["x"]
    assert content_right <= info_left + 1, (
        f"content-zone (right={content_right:.1f}) overflows under the info-zone "
        f"(left={info_left:.1f}); its text would be occluded on focus"
    )
