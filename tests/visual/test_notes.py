"""Visual guard for note and aside markers.

The marker is a small tinted chip with the number (braiid/braiid.css, the
note-marker rules). It is the same for notes and asides. On hover or focus the
chip fills with the primary color and the number takes the page color.
Definitions are shown in place for now, starting with the same chip at rest.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

RSM_READY = "() => window.__rsmInitialized === true"
FIXTURE = Path(__file__).parent / "fixtures" / "notes.rsm"

WIDTHS = [("mobile", 375, 667), ("desktop", 1280, 720)]


@pytest.mark.visual
class TestNoteMarkers:

    @pytest.mark.parametrize("theme", ["light", "dark"])
    @pytest.mark.parametrize("viewport_name,width,height", WIDTHS)
    def test_markers_at_rest(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
        theme: str,
    ) -> None:
        page.set_viewport_size({"width": width, "height": height})
        serve_rsm_html(FIXTURE.read_text(), dark_theme=theme == "dark")
        page.wait_for_function(RSM_READY, timeout=10_000)
        page.mouse.move(0, 0)
        assert_snapshot(page.locator(".manuscript").screenshot())

    @pytest.mark.parametrize("theme", ["light", "dark"])
    def test_marker_focused(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        theme: str,
    ) -> None:
        page.set_viewport_size({"width": 1280, "height": 720})
        serve_rsm_html(FIXTURE.read_text(), dark_theme=theme == "dark")
        page.wait_for_function(RSM_READY, timeout=10_000)
        page.locator('a.note-marker[href="#second"]').focus()
        paragraph = page.locator(".manuscript .paragraph").first
        assert_snapshot(paragraph.screenshot())
