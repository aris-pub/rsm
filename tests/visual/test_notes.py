"""Visual guard for footnote markers, the notes list and the note preview.

A footnote marker is a small tinted chip with the number (braiid/braiid.css,
the note-marker rules). On hover or focus the chip fills with the primary color
and the number takes the page color. Footnotes count on their own, 1, 2, 3.
They are shown in one Notes list before References, each entry starting with
the same chip at rest. An aside has no marker: its phrase has a dotted
underline (tests/visual/test_asides.py covers asides). Hovering a footnote
marker shows the reference preview with the note's text.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

RSM_READY = "() => window.__rsmInitialized === true"
FIXTURE = Path(__file__).parent / "fixtures" / "notes.rsm"

WIDTHS = [("mobile", 375, 667), ("desktop", 1280, 720)]


def _notes_section(page: Page):
    # The list's parent is the section that holds the heading and the list.
    return page.locator(".manuscript ol.noteslist").locator("xpath=..")


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
        page.locator('a.note-marker[href="#third"]').focus()
        paragraph = page.locator(".manuscript .paragraph").first
        assert_snapshot(paragraph.screenshot())


@pytest.mark.visual
class TestNotesList:

    @pytest.mark.parametrize("theme", ["light", "dark"])
    @pytest.mark.parametrize("viewport_name,width,height", WIDTHS)
    def test_notes_list(
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
        assert_snapshot(_notes_section(page).screenshot())


@pytest.mark.visual
class TestNotePreview:

    @pytest.mark.parametrize("theme", ["light", "dark"])
    @pytest.mark.parametrize("viewport_name,width,height", WIDTHS)
    def test_preview_on_hover(
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
        page.locator('a.note-marker[href="#third"]').hover()
        box = page.locator(".tooltipster-base .tooltipster-box")
        box.wait_for(state="visible", timeout=3000)
        # The preview typesets its math after it opens.
        page.wait_for_function(
            "() => !document.querySelector('.tooltipster-content').textContent.includes('\\\\(')",
            timeout=5000,
        )
        page.wait_for_timeout(300)
        assert_snapshot(box.screenshot())
