"""Visual regression tests for the author block.

The author block folds like other handrail blocks: closed, it shows the names
and, at the foot of its rail, a fold label that counts the details. Open, it
shows every name and the details. These snapshots lock how it looks closed and
open, at rest and under the mouse, wide and on a phone, light and dark, with
the hover on the mail icon and the tooltip on a name.

Behavior (the states, the controls, the tooltips) is covered by
tests/interactive/test_author_states.py and test_author_icons.py.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

FIXTURE = Path(__file__).parent / "fixtures" / "authors.rsm"
BLOCK = ".author-block"

SIZES = [("desktop", 1280, 720), ("phone", 375, 667)]


def _load(serve_rsm_html, page: Page, width: int, height: int, dark: bool = False):
    page.set_viewport_size({"width": width, "height": height})
    serve_rsm_html(FIXTURE.read_text(), dark_theme=dark)
    page.mouse.move(1, 1)
    page.wait_for_timeout(300)
    state = page.get_attribute(BLOCK, "data-authors")
    assert state == "closed", state


def _open(page: Page):
    page.click(f"{BLOCK} .author-summary")
    page.mouse.move(1, 1)
    page.wait_for_timeout(300)


@pytest.mark.visual
class TestAuthorBlock:
    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    @pytest.mark.parametrize(
        "viewport_name,width,height", SIZES, ids=[s[0] for s in SIZES]
    )
    def test_closed_at_rest(
        self, serve_rsm_html, page: Page, assert_snapshot, viewport_name, width, height, dark
    ):
        _load(serve_rsm_html, page, width, height, dark)
        assert_snapshot(page.screenshot())

    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    @pytest.mark.parametrize(
        "viewport_name,width,height", SIZES, ids=[s[0] for s in SIZES]
    )
    def test_open_at_rest(
        self, serve_rsm_html, page: Page, assert_snapshot, viewport_name, width, height, dark
    ):
        _load(serve_rsm_html, page, width, height, dark)
        _open(page)
        assert_snapshot(page.screenshot())

    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_closed_under_the_mouse(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _load(serve_rsm_html, page, 1280, 720, dark)
        page.hover(f"{BLOCK} .author-summary")
        page.wait_for_timeout(300)
        assert_snapshot(page.screenshot())

    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_open_under_the_mouse(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _load(serve_rsm_html, page, 1280, 720, dark)
        _open(page)
        page.hover(f"{BLOCK} .author-details")
        page.wait_for_timeout(300)
        assert_snapshot(page.screenshot())

    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_mail_icon_under_the_mouse(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _load(serve_rsm_html, page, 1280, 720, dark)
        page.hover('a.author-contact[href^="mailto:"]')
        page.wait_for_selector(".ui-tip.on", timeout=3_000)
        page.wait_for_timeout(300)
        assert_snapshot(page.screenshot())

    @pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
    def test_name_tooltip(self, serve_rsm_html, page: Page, assert_snapshot, dark):
        _load(serve_rsm_html, page, 1280, 720, dark)
        page.hover(".author-name-text >> text=Ada Lovelace")
        page.wait_for_selector(".tooltipster-base", state="visible", timeout=3_000)
        page.wait_for_timeout(300)
        assert_snapshot(page.screenshot())
