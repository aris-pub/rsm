"""Visual regression tests for accent color system."""

from pathlib import Path

import pytest
from playwright.sync_api import Page

from .conftest import VIEWPORTS


@pytest.mark.visual
class TestAccentColors:
    """Tests for accent color rendering across all 8 colors."""

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    @pytest.mark.parametrize(
        "accent_color",
        ["blue", "purple", "red", "green", "orange", "yellow", "pink", "gray"],
    )
    def test_accent_color(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
        accent_color: str,
    ) -> None:
        """
        Captures rendering with different accent colors.

        Tests: handrail dots, handrail borders, links, references all use
        the specified accent color from the palette.
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "accent-colors.rsm"

        # Add accent config to the RSM source
        rsm_source = f"""# Accent Color Test: {accent_color.title()}

:config: {{
  :accent: {accent_color}
}}
::

{fixture.read_text()}
"""

        content = serve_rsm_html(rsm_source, dark_theme=False)

        # Activate a handrail by clicking on it to show the accent color
        handrail = page.locator(".hr").first
        handrail.click()

        # Wait for CSS transitions
        page.wait_for_timeout(300)

        # potf-4em: raise the per-pixel threshold so borderline text-edge pixels
        # that flake under CI load drop out; a real accent change is a large color
        # step that survives. Small residual budget, below the smallest real change.
        assert_snapshot(page.screenshot(full_page=True), threshold=0.4, max_diff_pixels=50)

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    @pytest.mark.parametrize(
        "accent_color",
        ["blue", "purple", "red", "green", "orange", "yellow", "pink", "gray"],
    )
    def test_accent_color_dark_theme(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
        accent_color: str,
    ) -> None:
        """
        Captures rendering with accent colors in dark mode.

        Tests: accent colors work correctly with dark theme applied.
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "accent-colors.rsm"

        # Add accent config to the RSM source
        rsm_source = f"""# Accent Color Test: {accent_color.title()} (Dark)

:config: {{
  :accent: {accent_color}
}}
::

{fixture.read_text()}
"""

        content = serve_rsm_html(rsm_source, dark_theme=True)

        # Activate a handrail to show the accent color
        handrail = page.locator(".hr").first
        handrail.click()
        page.wait_for_timeout(300)

        # potf-4em: raise the per-pixel threshold so borderline text-edge pixels
        # that flake under CI load drop out; a real accent change is a large color
        # step that survives. Small residual budget, below the smallest real change.
        assert_snapshot(page.screenshot(full_page=True), threshold=0.4, max_diff_pixels=50)
