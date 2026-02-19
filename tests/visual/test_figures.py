"""Visual regression tests for :figure: directive options."""

from pathlib import Path

import pytest
from playwright.sync_api import Page

from .conftest import VIEWPORTS

FIXTURE = Path(__file__).parent / "fixtures" / "figures.rsm"
IMAGE_DIR = Path(__file__).parent / "fixtures"


@pytest.mark.visual
class TestFigures:
    """Tests for :figure: with :alt: and :dark: options."""

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_light_color_scheme(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures figures under light color scheme.

        Tests: basic figure, figure with alt text, figure with :dark: variant (light image shown).
        """
        page.set_viewport_size({"width": width, "height": height})
        page.emulate_media(color_scheme="light")
        serve_rsm_html(FIXTURE.read_text(), image_dir=IMAGE_DIR)
        assert_snapshot(page.screenshot(full_page=True))

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_dark_color_scheme(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures figures with prefers-color-scheme: dark emulated.

        Tests: the :dark: variant image is selected by the <picture> element for the
        third figure; the other two figures are unaffected.
        """
        page.set_viewport_size({"width": width, "height": height})
        page.emulate_media(color_scheme="dark")
        serve_rsm_html(FIXTURE.read_text(), image_dir=IMAGE_DIR)
        assert_snapshot(page.screenshot(full_page=True))
