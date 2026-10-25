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

    def test_dark_theme_is_actually_applied(
        self,
        serve_rsm_html: callable,
        page: Page,
    ) -> None:
        """serve_rsm_html(dark_theme=True) must force dark mode.

        The dark snapshots above are only meaningful if the page really renders
        dark. Guards rsm-si1: the old <html> string replace never matched the
        built "<html lang=.. data-accent=..>" tag, so every dark_theme=True
        snapshot was silently rendering light.
        """
        fixture = Path(__file__).parent / "fixtures" / "block-types.rsm"
        serve_rsm_html(fixture.read_text(), dark_theme=True)

        has_class = page.evaluate(
            "() => document.documentElement.classList.contains('dark-theme')"
        )
        assert has_class, "dark_theme=True did not add .dark-theme to <html>"

        # Prove it rendered dark, not just that a class string is present: the
        # first opaque page background must be a dark color.
        rgb = page.evaluate(
            """() => {
                const els = [document.body, document.documentElement,
                             document.querySelector('.manuscriptwrapper')];
                for (const el of els) {
                    if (!el) continue;
                    const m = getComputedStyle(el).backgroundColor
                        .match(/^rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
                    if (!m) continue;
                    const a = m[4] === undefined ? 1 : parseFloat(m[4]);
                    if (a > 0) return [Number(m[1]), Number(m[2]), Number(m[3])];
                }
                return null;
            }"""
        )
        assert rgb is not None, "no opaque page background found"
        luminance = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
        assert luminance < 90, f"page background {rgb} is not dark (luminance {luminance:.0f})"
