"""Visual guard for :toc: {:orientation: horizontal} (rsm-bjv).

From 768px the text TOC graph runs left to right with the root dot at the left,
where the edges meet. On a phone it falls back to the vertical graph.
Behaviour is covered by tests/interactive/test_toc_orientation.py.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

RSM_READY = "() => window.__rsmInitialized === true"
FIXTURE = Path(__file__).parent / "fixtures" / "toc-horizontal.rsm"

WIDTHS = [("mobile", 375, 667), ("desktop", 1280, 720)]


@pytest.mark.visual
class TestTocOrientation:

    @pytest.mark.parametrize("theme", ["light", "dark"])
    @pytest.mark.parametrize("viewport_name,width,height", WIDTHS)
    def test_toc_graph(
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
        page.wait_for_timeout(150)  # tocarcs.js settles label sizes after layout
        assert_snapshot(page.locator("nav.toc").screenshot())
