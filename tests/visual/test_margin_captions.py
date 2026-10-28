"""Visual regression for captions in the margin column and stacked (rsm-coj).

Baselines are generated on Linux CI (run with --update-snapshots there). The
fixture is shared with tests/interactive/test_margin_captions.py.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

FIXTURES = Path(__file__).parents[1] / "interactive" / "fixtures"
SRC = (FIXTURES / "margin_captions.rsm").read_text()

# 1440: the column fits (captions in the margin). 1024 and 375: stacked.
WIDTHS = [("wide-1440", 1440), ("desktop-1024", 1024), ("mobile-375", 375)]


def _shot(page: Page, serve_rsm_html, width: int, scheme: str) -> bytes:
    page.set_viewport_size({"width": width, "height": 900})
    page.emulate_media(color_scheme=scheme)
    serve_rsm_html(SRC, image_dir=FIXTURES, sidebar=True)
    page.mouse.move(1, 1)
    return page.screenshot(full_page=True, animations="disabled")


@pytest.mark.visual
class TestMarginCaptions:
    @pytest.mark.parametrize("scheme", ["light", "dark"])
    @pytest.mark.parametrize("name,width", WIDTHS)
    def test_at_rest(
        self, serve_rsm_html, page: Page, assert_snapshot, name, width, scheme
    ) -> None:
        """Nothing beside the blocks at rest, captions in the margin or under
        their block."""
        assert_snapshot(_shot(page, serve_rsm_html, width, scheme))

    @pytest.mark.parametrize("scheme", ["light", "dark"])
    @pytest.mark.parametrize("name,width", WIDTHS[:2])
    def test_caption_focused(
        self, serve_rsm_html, page: Page, assert_snapshot, name, width, scheme
    ) -> None:
        """A focused caption: its rail in the left gutter, spanning the figure."""
        _shot(page, serve_rsm_html, width, scheme)
        page.focus("#fig-a > figcaption")
        page.wait_for_timeout(300)
        assert_snapshot(page.screenshot(animations="disabled"))
