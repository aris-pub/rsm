"""WCAG checks for footnote markers, the notes list and the note preview."""

from pathlib import Path

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page

FIXTURE = Path(__file__).parent.parent / "visual" / "fixtures" / "notes.rsm"

WIDTHS = [("mobile", 375, 667), ("desktop", 1280, 720)]

WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]


def _format(violations: list) -> str:
    return "\n".join(
        f"{v['id']}: {v['help']} ({len(v['nodes'])} nodes)\n"
        + "\n".join(f"    {n['html'][:200]}" for n in v["nodes"][:5])
        for v in violations
    )


@pytest.mark.accessibility
class TestNotesAccessibility:

    @pytest.mark.parametrize("theme", ["light", "dark"])
    @pytest.mark.parametrize("viewport_name,width,height", WIDTHS)
    def test_notes_list_page(
        self,
        serve_rsm_a11y: callable,
        page: Page,
        viewport_name: str,
        width: int,
        height: int,
        theme: str,
    ) -> None:
        page.set_viewport_size({"width": width, "height": height})
        page = serve_rsm_a11y(FIXTURE.read_text(), dark_theme=theme == "dark")
        violations = Axe().run(page).response["violations"]
        assert violations == [], _format(violations)

    @pytest.mark.parametrize("theme", ["light", "dark"])
    @pytest.mark.parametrize("viewport_name,width,height", WIDTHS)
    def test_open_preview(
        self,
        serve_rsm_a11y: callable,
        page: Page,
        viewport_name: str,
        width: int,
        height: int,
        theme: str,
    ) -> None:
        page.set_viewport_size({"width": width, "height": height})
        page = serve_rsm_a11y(FIXTURE.read_text(), dark_theme=theme == "dark")
        page.locator('a.note-marker[href="#first"]').hover()
        page.locator(".tooltipster-base").wait_for(state="visible", timeout=3000)
        page.wait_for_timeout(500)
        wcag = {"runOnly": {"type": "tag", "values": WCAG_TAGS}}
        violations = Axe().run(page, options=wcag).response["violations"]
        assert violations == [], _format(violations)

    def test_open_preview_adds_nothing_beyond_the_reference_preview(
        self,
        serve_rsm_a11y: callable,
        page: Page,
    ) -> None:
        # The preview is appended to <body>, outside the landmarks, so axe's
        # best-practice "region" rule flags it. The reference preview has the
        # same finding. The note preview must not add any other.
        page.set_viewport_size({"width": 1280, "height": 720})
        page = serve_rsm_a11y(FIXTURE.read_text())

        def violations_with_preview(selector: str) -> set[str]:
            page.mouse.move(0, 0)
            page.locator(".tooltipster-base").wait_for(state="detached", timeout=3000)
            page.locator(selector).hover()
            page.locator(".tooltipster-base").wait_for(state="visible", timeout=3000)
            page.wait_for_timeout(500)
            return {v["id"] for v in Axe().run(page).response["violations"]}

        note = violations_with_preview('a.note-marker[href="#first"]')
        reference = violations_with_preview('a.reference.cite[href="#knuth"]')
        assert note <= reference, note - reference
