"""Visual regression tests for the reader sidebar (`rsm build --sidebar`).

Appearance guards for the strip, each panel view, the phone bar and sheet, the
Reading tiles and the pin control. Behaviour is covered by
tests/interactive/test_sidebar*.py and tests/interactive/test_pin.py;
accessibility by tests/accessibility/test_sidebar_a11y.py.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

FIXTURE = Path(__file__).parent / "fixtures" / "sidebar.rsm"
DESKTOP = {"width": 1280, "height": 800}
PHONE = {"width": 390, "height": 844}


def _serve(serve_rsm_html, page: Page, viewport: dict, dark: bool = False) -> None:
    page.set_viewport_size(viewport)
    serve_rsm_html(FIXTURE.read_text(), dark_theme=dark, sidebar=True)


def _open(page: Page, view: str) -> None:
    page.click(f'.rail-strip-btn[data-view="{view}"]')
    page.wait_for_selector(".proof-rail.open")
    page.mouse.move(DESKTOP["width"] - 5, DESKTOP["height"] - 5)  # no hover, no tooltip
    page.wait_for_timeout(500)  # the column's transition


def _select_proof(page: Page) -> None:
    page.evaluate(
        """() => {
            const step = [...document.querySelectorAll('.proof[data-nodeid] .step')]
                .filter((s) => !s.closest('.calc'))[1];
            step.scrollIntoView({ block: 'center' });
            step.click();
        }"""
    )
    page.wait_for_timeout(300)


@pytest.mark.visual
class TestSidebarDesktop:
    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_strip_closed(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _serve(serve_rsm_html, page, DESKTOP, dark)
        assert_snapshot(page.screenshot())

    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    @pytest.mark.parametrize("view", ["contents", "notation", "reading", "pinned"])
    def test_view_open(self, serve_rsm_html, page: Page, assert_snapshot, view, dark):
        _serve(serve_rsm_html, page, DESKTOP, dark)
        _open(page, view)
        assert_snapshot(page.screenshot())

    @pytest.mark.parametrize("view", ["steps", "state"])
    def test_proof_view_open(self, serve_rsm_html, page: Page, assert_snapshot, view):
        _serve(serve_rsm_html, page, DESKTOP)
        _select_proof(page)
        _open(page, view)
        assert_snapshot(page.screenshot())

    def test_pinned_excerpt(self, serve_rsm_html, page: Page, assert_snapshot):
        _serve(serve_rsm_html, page, DESKTOP)
        ref = page.locator('.manuscript a.reference[href="#thm-x"]').last
        ref.scroll_into_view_if_needed()
        ref.hover()
        pin = page.locator('.tooltipster-base .ref-pin[data-pin-target="#thm-x"]').last
        pin.wait_for(state="visible")
        pin.click()
        page.mouse.move(DESKTOP["width"] - 5, DESKTOP["height"] - 5)
        page.wait_for_timeout(600)
        assert_snapshot(page.screenshot())


@pytest.mark.visual
class TestPinControl:
    @pytest.mark.parametrize("state", ["rest", "pinned"])
    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_pin_control(self, serve_rsm_html, page: Page, assert_snapshot, state, dark):
        _serve(serve_rsm_html, page, DESKTOP, dark)
        ref = page.locator('.manuscript a.reference[href="#thm-x"]').last
        ref.scroll_into_view_if_needed()
        if state == "pinned":
            ref.hover()
            page.locator('.tooltipster-base .ref-pin[data-pin-target="#thm-x"]').last.click()
            page.keyboard.press("Escape")
            page.mouse.move(5, 5)
            page.wait_for_timeout(600)
        ref.hover()
        tip = page.locator(".tooltipster-base").last
        tip.wait_for(state="visible")
        page.wait_for_timeout(400)
        assert_snapshot(tip.screenshot())


@pytest.mark.visual
class TestSidebarPhone:
    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_bar_closed(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _serve(serve_rsm_html, page, PHONE, dark)
        assert_snapshot(page.screenshot())

    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    @pytest.mark.parametrize("view", ["document", "reading"])
    def test_sheet_open(self, serve_rsm_html, page: Page, assert_snapshot, view, dark):
        _serve(serve_rsm_html, page, PHONE, dark)
        page.click(f'.rail-strip-btn[data-view="{view}"]')
        page.wait_for_selector(".proof-rail.open")
        page.wait_for_timeout(300)
        assert_snapshot(page.screenshot())

    def test_sheet_notation_tab(self, serve_rsm_html, page: Page, assert_snapshot):
        _serve(serve_rsm_html, page, PHONE)
        page.click('.rail-strip-btn[data-view="document"]')
        page.click('.rail-subtabs-document .rail-tab[data-view="notation"]')
        page.wait_for_timeout(300)
        page.locator(".rail-notation-input").first.evaluate("el => el.blur()")
        page.mouse.move(PHONE["width"] - 10, 10)  # off the text, so no handrail hover
        page.wait_for_timeout(200)
        assert_snapshot(page.screenshot())
