"""Visual regression tests for interactive handrail states."""

from pathlib import Path

import pytest
from playwright.sync_api import Page

from .conftest import VIEWPORTS


@pytest.mark.visual
class TestHandrailStates:
    """Tests for handrail visibility, hover, focus, and collapse states."""

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_hidden_handrail_default(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures paragraphs with hidden handrails in default state.

        Tests: .hr-hidden class with opacity 0% (invisible by default).
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "interactive-states.rsm"
        content = serve_rsm_html(fixture.read_text())
        assert_snapshot(page.screenshot(full_page=True))

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_hidden_handrail_hovered(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures paragraph handrail on hover (controls become visible).

        Tests: .hr-hidden handrail with opacity 100% on hover.
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "interactive-states.rsm"
        content = serve_rsm_html(fixture.read_text())

        # Hover over the first paragraph (should have hr-hidden class)
        paragraph = page.locator(".paragraph.hr.hr-hidden").first
        paragraph.hover()
        assert_snapshot(paragraph.screenshot())

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_visible_handrail_focused(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures theorem handrail in focused state.

        Tests: blue background, active border color, visible controls.
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "interactive-states.rsm"
        content = serve_rsm_html(fixture.read_text())

        # Focus the first theorem using click (more reliable than .focus())
        theorem = page.locator(".theorem.hr").first
        theorem.click()
        assert_snapshot(theorem.screenshot())

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_proof_collapsed(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures proof in collapsed state.

        Tests: .hr-collapsed class, hidden content, collapse indicator.
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "interactive-states.rsm"
        content = serve_rsm_html(fixture.read_text())

        # Click collapse button (force=True bypasses visibility checks)
        proof = page.locator(".proof.hr").first
        collapse_btn = proof.locator(".hr-collapse").first
        collapse_btn.click(force=True)

        # Wait for collapse animation/class to apply
        page.wait_for_selector(".proof.hr.hr-collapsed", timeout=1000)

        # Capture the collapsed proof
        collapsed_proof = page.locator(".proof.hr.hr-collapsed").first
        assert_snapshot(collapsed_proof.screenshot())

    @pytest.mark.parametrize("viewport_name,width,height", VIEWPORTS)
    def test_handrail_menu_visible(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
        viewport_name: str,
        width: int,
        height: int,
    ) -> None:
        """
        Captures handrail with visible three-dot menu.

        Tests: menu visibility on hover, menu items, menu styling.
        """
        page.set_viewport_size({"width": width, "height": height})
        fixture = Path(__file__).parent / "fixtures" / "interactive-states.rsm"
        content = serve_rsm_html(fixture.read_text())

        # Hover over theorem to show handrail controls
        theorem = page.locator(".theorem.hr").first
        theorem.hover()

        # Hover over the three-dot menu button to show menu
        menu_dots = theorem.locator(".hr-border-dots").first
        menu_dots.hover()

        # Wait a bit for menu to appear
        page.wait_for_timeout(100)

        # Capture the theorem with visible menu
        assert_snapshot(theorem.screenshot())
