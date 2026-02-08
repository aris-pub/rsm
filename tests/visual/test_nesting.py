"""Visual regression tests for nesting behaviors."""

from pathlib import Path

import pytest
from playwright.sync_api import Page

from .conftest import VIEWPORTS


@pytest.mark.visual
class TestNestingStacking:
    """Tests for vertical alignment of borders at same nesting depth."""

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_aligned_borders(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures nested blocks with borders aligned at same depth.

        Tests: section → theorem → proof → paragraph nesting.
        Verifies borders align vertically when at same depth level.
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "nesting-stacking.rsm"
        content = serve_rsm_html(fixture.read_text())
        assert_snapshot(page.screenshot(full_page=True))


@pytest.mark.visual
class TestNestingShifting:
    """Tests for proof step depth width reduction (scales with viewport)."""

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_depth_0_1_2_3(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures proof steps at depths 0-3 with progressive width reduction.

        Tests: proof → step → substep → subsubstep nesting.
        Verifies proportional width reduction at each depth level (scales with viewport).
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "nesting-shifting.rsm"
        content = serve_rsm_html(fixture.read_text())
        assert_snapshot(page.screenshot(full_page=True))
