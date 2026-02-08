"""Visual regression tests for light/dark theming."""

from pathlib import Path

import pytest
from playwright.sync_api import Page

from .conftest import VIEWPORTS


@pytest.mark.visual
class TestTheming:
    """Tests for light and dark mode theme rendering."""

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_light_theme_comprehensive(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures comprehensive light theme rendering.

        Tests: all block types in default light mode colors.
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "block-types.rsm"
        content = serve_rsm_html(fixture.read_text(), dark_theme=False)
        assert_snapshot(page.screenshot(full_page=True))

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_dark_theme_comprehensive(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures comprehensive dark theme rendering.

        Tests: all block types with .dark-theme class applied to <html>.
        Verifies inverted color palette, surface colors, borders.
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "block-types.rsm"
        content = serve_rsm_html(fixture.read_text(), dark_theme=True)
        assert_snapshot(page.screenshot(full_page=True))

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_dark_theme_nesting(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures dark theme with nested blocks.

        Tests: border colors, backgrounds in dark mode with nesting.
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "nesting-stacking.rsm"
        content = serve_rsm_html(fixture.read_text(), dark_theme=True)
        assert_snapshot(page.screenshot(full_page=True))
