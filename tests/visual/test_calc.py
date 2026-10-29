"""Visual guard for :calc: chains, outside a proof and inside one.

Outside a proof a numbered chain sits on the text column like a display
equation, with its number in the equation-number column. Inside a proof it keeps
its place among the steps. Relation math is at display size. In a numbered
chain the because-marks sit at the right end of each row.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

RSM_READY = "() => window.__rsmInitialized === true"
FIXTURE = Path(__file__).parent / "fixtures" / "calc.rsm"

WIDTHS = [("mobile", 375, 667), ("desktop", 1280, 720)]
PLACES = [("top-level", 0), ("in-proof", 1)]


def _load(serve_rsm_html, page: Page, width: int, height: int, theme: str) -> None:
    page.set_viewport_size({"width": width, "height": height})
    serve_rsm_html(FIXTURE.read_text(), dark_theme=theme == "dark")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.mouse.move(0, 0)


@pytest.mark.visual
class TestCalc:

    @pytest.mark.parametrize("place,section", PLACES)
    @pytest.mark.parametrize("theme", ["light", "dark"])
    @pytest.mark.parametrize("viewport_name,width,height", WIDTHS)
    def test_at_rest(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
        theme: str,
        place: str,
        section: int,
    ) -> None:
        _load(serve_rsm_html, page, width, height, theme)
        assert_snapshot(page.locator("section.level-2").nth(section).screenshot())

    @pytest.mark.parametrize("theme", ["light", "dark"])
    def test_reason_open(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        theme: str,
    ) -> None:
        _load(serve_rsm_html, page, 1280, 720, theme)
        mark = page.locator(
            "#eq-top > .hr-content-zone > .step > .hr-info-zone .hr-collapse"
        ).nth(1)
        mark.click()
        page.mouse.move(0, 0)
        page.wait_for_timeout(200)
        assert_snapshot(page.locator("section.level-2").first.screenshot())
