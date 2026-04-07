"""Visual regression tests for the static/interactive figure toggle."""

from pathlib import Path

import pytest
from playwright.sync_api import Page

from .conftest import VIEWPORTS

FIXTURE = Path(__file__).parent / "fixtures" / "figures.rsm"
IMAGE_DIR = Path(__file__).parent / "fixtures"

RSM_READY = "() => window.__rsmInitialized === true"


@pytest.mark.visual
class TestFigureToggle:
    """Visual tests for the figure static toggle feature."""

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_figure_default_interactive(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """Captures figure with static fallback in default (interactive) state."""
        page.set_viewport_size({"width": width, "height": height})
        serve_rsm_html(FIXTURE.read_text(), image_dir=IMAGE_DIR)
        page.wait_for_function(RSM_READY, timeout=10_000)

        figure = page.locator("figure").last
        assert_snapshot(figure.screenshot())

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_figure_toggled_to_static(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """Captures figure after toggling to static view."""
        page.set_viewport_size({"width": width, "height": height})
        serve_rsm_html(FIXTURE.read_text(), image_dir=IMAGE_DIR)
        page.wait_for_function(RSM_READY, timeout=10_000)

        figure = page.locator("figure").last
        caption_dots = figure.locator("figcaption .hr-border-dots")
        caption_dots.click()
        page.locator('#hr-menu-singleton [data-role="static-toggle"]').click()

        assert_snapshot(figure.screenshot())
