"""Visual regression tests for block types rendering."""

from pathlib import Path

import pytest
from playwright.sync_api import Page

from .conftest import VIEWPORTS


@pytest.mark.visual
class TestBlockTypes:
    """Tests for all major RSM block types."""

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_light_theme(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures baseline rendering of all block types in light theme.

        Tests: paragraphs, theorem-like blocks, proofs, code, math, lists.
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "block-types.rsm"
        content = serve_rsm_html(fixture.read_text())
        assert_snapshot(page.screenshot(full_page=True))

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_dark_theme(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures baseline rendering of all block types in dark theme.

        Tests: same blocks as light theme but with dark mode colors.
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "block-types.rsm"
        content = serve_rsm_html(fixture.read_text(), dark_theme=True)
        assert_snapshot(page.screenshot(full_page=True))
