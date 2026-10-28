"""Visual tests of the handrail dots pill in its four desktop states (rsm-wpv).

The colours and their contrast are asserted in
tests/interactive/test_pill_colours.py. These snapshots lock how each state
looks, in both themes:

- block hovered: pill on --surface-primary
- pill hovered: --surface-hint
- block active: the rail's colour, dark dots
- active and pill hovered: a lighter shade of the rail colour
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

FIXTURE = Path(__file__).parent / "fixtures" / "pill-states.rsm"
STATES = ["block-hover", "pill-hover", "active", "active-pill-hover"]


@pytest.mark.visual
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("state", STATES)
def test_pill_state(
    serve_rsm_html: callable,
    page: Page,
    assert_snapshot: callable,
    state: str,
    theme: str,
) -> None:
    page.set_viewport_size({"width": 1280, "height": 720})
    serve_rsm_html(FIXTURE.read_text(), dark_theme=theme == "dark")

    thm = page.locator(".theorem.hr").first
    dots = thm.locator(":scope > .hr-border-zone > .hr-border-dots")
    # A click on the content would focus the nested paragraph, not the theorem.
    if state.startswith("active"):
        thm.focus()
    if state.endswith("pill-hover"):
        dots.hover()
    else:
        thm.locator(":scope > .hr-content-zone").hover()
    page.wait_for_timeout(100)

    assert_snapshot(thm.screenshot())
