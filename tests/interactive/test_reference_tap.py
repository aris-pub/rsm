"""Interactive: references preview their target on touch, like footnote markers.

On touch, the first tap on a reference opens its preview without following the
link, a second tap on the same reference follows it, and a tap elsewhere closes
the preview. Mouse and keyboard are unchanged: a click and Enter follow the link
at once, and focus plus "i" toggles the preview.

Backlinks (in the notes list and the bibliography) also carry the `reference`
class and show a hover preview of the text they point back to, so they follow
the same touch rule.
"""

import pytest
from playwright.sync_api import Browser, Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"
PREVIEW = ".tooltipster-base"
REF = 'a.reference[href="#thm-x"]'
NOTE_BACKLINK = "#first .note-backlink"
BIB_BACKLINK = 'a.reference.backlink[href="#cite-0"]'


def _open(page: Page, server: str) -> None:
    page.goto(f"{server}/notes.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


@pytest.fixture
def touch_page(browser: Browser, interactive_server: str):
    ctx = browser.new_context(
        has_touch=True, is_mobile=True, viewport={"width": 390, "height": 844}
    )
    pg = ctx.new_page()
    _open(pg, interactive_server)
    yield pg
    ctx.close()


def _tap_elsewhere(page: Page) -> None:
    box = page.locator(".manuscript h1").first.bounding_box()
    page.touchscreen.tap(box["x"] + 5, box["y"] + box["height"] / 2)


class TestTapReference:

    def test_first_tap_opens_preview_without_following_the_link(
        self, touch_page: Page
    ):
        touch_page.locator(REF).tap()
        preview = touch_page.locator(PREVIEW)
        expect(preview).to_be_visible(timeout=3000)
        expect(preview).to_contain_text("For every graph")
        touch_page.wait_for_timeout(300)
        assert touch_page.evaluate("location.hash") == ""

    def test_second_tap_follows_the_link(self, touch_page: Page):
        touch_page.locator(REF).tap()
        expect(touch_page.locator(PREVIEW)).to_be_visible(timeout=3000)
        touch_page.locator(REF).tap()
        touch_page.wait_for_function("() => location.hash === '#thm-x'", timeout=3000)

    def test_tap_elsewhere_closes_the_preview(self, touch_page: Page):
        touch_page.locator(REF).tap()
        expect(touch_page.locator(PREVIEW)).to_be_visible(timeout=3000)
        _tap_elsewhere(touch_page)
        expect(touch_page.locator(PREVIEW)).to_have_count(0, timeout=3000)
        assert touch_page.evaluate("location.hash") == ""


class TestTapBacklink:

    @pytest.mark.parametrize(
        "link,target",
        [(NOTE_BACKLINK, "#call-first"), (BIB_BACKLINK, "#cite-0")],
        ids=["note", "bibliography"],
    )
    def test_first_tap_previews_and_second_follows(
        self, touch_page: Page, link: str, target: str
    ):
        touch_page.locator(link).scroll_into_view_if_needed()
        touch_page.locator(link).tap()
        expect(touch_page.locator(PREVIEW)).to_be_visible(timeout=3000)
        touch_page.wait_for_timeout(300)
        assert touch_page.evaluate("location.hash") == ""
        touch_page.locator(link).tap()
        touch_page.wait_for_function(
            f"() => location.hash === '{target}'", timeout=3000
        )


class TestPointerAndKeyboardUnchanged:

    def test_click_follows_the_link(self, page: Page, interactive_server: str):
        _open(page, interactive_server)
        page.locator(REF).click()
        page.wait_for_function("() => location.hash === '#thm-x'", timeout=3000)

    def test_enter_follows_the_link(self, page: Page, interactive_server: str):
        _open(page, interactive_server)
        page.locator(REF).focus()
        page.keyboard.press("Enter")
        page.wait_for_function("() => location.hash === '#thm-x'", timeout=3000)

    def test_i_toggles_the_preview(self, page: Page, interactive_server: str):
        _open(page, interactive_server)
        page.locator(REF).focus()
        page.keyboard.press("i")
        preview = page.locator(PREVIEW)
        expect(preview).to_be_visible(timeout=3000)
        expect(preview).to_contain_text("For every graph")
        page.keyboard.press("i")
        expect(preview).to_have_count(0, timeout=3000)
