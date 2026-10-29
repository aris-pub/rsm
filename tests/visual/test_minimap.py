"""Visual regression tests for the document minimap (rsm/static/minimap.js).

Appearance guards for the strip at the right edge: marks at rest, the strip
hovered with a label showing, a focused mark, and the phone strip while it
shows. Behaviour is covered by tests/interactive/test_minimap.py and
accessibility by tests/accessibility/test_minimap_a11y.py.

Baselines are generated on the Linux CI runner (see tests/visual/README.md).
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

FIXTURE = Path(__file__).parent / "fixtures" / "minimap.rsm"
IMAGES = Path(__file__).parent / "fixtures"
DESKTOP = {"width": 1280, "height": 800}
PHONE = {"width": 375, "height": 720}


def _serve(serve_rsm_html, page: Page, viewport: dict, dark: bool) -> None:
    page.set_viewport_size(viewport)
    page.emulate_media(reduced_motion="reduce")
    serve_rsm_html(FIXTURE.read_text(), dark_theme=dark, image_dir=IMAGES, sidebar=True)
    page.wait_for_selector(".rsm-minimap .rsm-minimap-mark", state="attached")


def _strip(page: Page):
    # Just the right edge, with room on the left for the label.
    return {"x": DESKTOP["width"] - 220, "y": 0, "width": 220, "height": DESKTOP["height"]}


def _hover_mark(page: Page, label: str) -> None:
    idx = page.locator(".rsm-minimap-links a").all_text_contents().index(label)
    box = page.locator(".rsm-minimap-mark").nth(idx).bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.wait_for_timeout(300)


@pytest.mark.visual
class TestMinimapDesktop:
    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_at_rest(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _serve(serve_rsm_html, page, DESKTOP, dark)
        page.mouse.move(600, 400)
        page.wait_for_timeout(300)
        assert_snapshot(page.screenshot(clip=_strip(page)))

    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_hover_section(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _serve(serve_rsm_html, page, DESKTOP, dark)
        _hover_mark(page, "2. Results")
        assert_snapshot(page.screenshot(clip=_strip(page)))

    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_hover_figure(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _serve(serve_rsm_html, page, DESKTOP, dark)
        _hover_mark(page, "Figure 1.1")
        assert_snapshot(page.screenshot(clip=_strip(page)))

    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_scrolled_to_the_middle(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _serve(serve_rsm_html, page, DESKTOP, dark)
        page.evaluate(
            "() => window.scrollTo(0, (document.documentElement.scrollHeight - innerHeight) / 2)"
        )
        page.mouse.move(600, 400)
        page.wait_for_timeout(300)
        assert_snapshot(page.screenshot(clip=_strip(page)))

    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_keyboard_focus(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _serve(serve_rsm_html, page, DESKTOP, dark)
        page.mouse.move(600, 400)
        page.locator(".rsm-minimap-links a").nth(3).focus()
        page.wait_for_timeout(300)
        assert_snapshot(page.screenshot(clip=_strip(page)))


@pytest.mark.visual
class TestMinimapPhone:
    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_showing_while_scrolling(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _serve(serve_rsm_html, page, PHONE, dark)
        page.evaluate("() => window.scrollTo(0, 1500)")
        page.wait_for_timeout(200)
        assert_snapshot(page.screenshot())

    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_hidden_at_rest(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _serve(serve_rsm_html, page, PHONE, dark)
        assert_snapshot(page.screenshot())
