"""Interactive: footnote markers preview their note, and the notes list links back.

Footnotes render in one Notes list before References. Each marker is a link to
its list entry and shows the reference preview (tooltips.js) with the note's
text:

  - pointer: hovering the marker opens the preview, a click follows the link;
  - touch: the first tap opens the preview without following the link, a
    second tap on the same marker follows it, a tap elsewhere closes it;
  - keyboard: the marker is focusable, "i" toggles the preview as it does on a
    reference, Enter follows the link;
  - no JavaScript: the marker is a plain link to the list, with no preview;
  - print: the list prints, previews do not.

Each list entry has a backlink to its call. Aside markers have no preview.
"""

import re

import pytest
from playwright.sync_api import Browser, Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"
PREVIEW = ".tooltipster-base"
MARKER = 'a.note-marker[href="#first"]'


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


def _scroll_y(page: Page) -> float:
    return page.evaluate("window.scrollY")


class TestNotesListPage:

    def test_list_sits_before_references(self, page: Page, interactive_server: str):
        _open(page, interactive_server)
        headings = page.locator(".manuscript h2").all_inner_texts()
        notes = headings.index("Notes")
        assert headings[notes + 1] == "References"

    def test_entries_are_numbered_in_call_order(
        self, page: Page, interactive_server: str
    ):
        _open(page, interactive_server)
        entries = page.locator("ol.noteslist > li.note")
        expect(entries).to_have_count(3)
        assert entries.evaluate_all("els => els.map(e => e.id)") == [
            "first",
            "second",
            "third",
        ]
        numbers = page.locator("ol.noteslist .note__number").all_inner_texts()
        # number 2 is the aside, shown in place
        assert numbers == ["1", "3", "4"]

    def test_entry_numbers_are_visible(self, page: Page, interactive_server: str):
        _open(page, interactive_server)
        expect(page.locator("#third .note__number")).to_be_visible()
        expect(page.locator("#third .note__number")).to_have_text("4")


class TestHoverPreview:

    def test_hover_opens_preview_with_the_note_text(
        self, page: Page, interactive_server: str
    ):
        _open(page, interactive_server)
        page.locator(MARKER).hover()
        preview = page.locator(PREVIEW)
        expect(preview).to_be_visible(timeout=3000)
        expect(preview).to_contain_text("The first footnote")
        # the backlink is left out of the preview
        expect(preview.locator(".note-backlink")).to_have_count(0)

    def test_preview_uses_the_reference_preview_theme(
        self, page: Page, interactive_server: str
    ):
        _open(page, interactive_server)
        page.locator(MARKER).hover()
        expect(page.locator(PREVIEW)).to_be_visible(timeout=3000)
        assert "tooltipster-shadow-rsm" in page.locator(PREVIEW).get_attribute("class")
        note_box = page.locator(".tooltipster-box").evaluate(
            "e => { const s = getComputedStyle(e); return [s.backgroundColor, s.borderRadius, s.boxShadow]; }"
        )
        page.mouse.move(0, 0)
        expect(page.locator(PREVIEW)).to_have_count(0, timeout=3000)
        page.locator('a.reference[href="#thm-x"]').hover()
        expect(page.locator(PREVIEW)).to_be_visible(timeout=3000)
        ref_box = page.locator(".tooltipster-box").evaluate(
            "e => { const s = getComputedStyle(e); return [s.backgroundColor, s.borderRadius, s.boxShadow]; }"
        )
        assert note_box == ref_box

    def test_math_in_the_preview_is_typeset(self, page: Page, interactive_server: str):
        _open(page, interactive_server)
        page.locator('a.note-marker[href="#second"]').hover()
        preview = page.locator(PREVIEW)
        expect(preview).to_be_visible(timeout=3000)
        expect(preview.locator("math, .katex, mjx-container, .temml").first).to_be_attached(
            timeout=5000
        )
        assert "\\(" not in preview.inner_text()

    def test_leaving_the_marker_closes_the_preview(
        self, page: Page, interactive_server: str
    ):
        _open(page, interactive_server)
        page.locator(MARKER).hover()
        expect(page.locator(PREVIEW)).to_be_visible(timeout=3000)
        page.mouse.move(0, 0)
        expect(page.locator(PREVIEW)).to_have_count(0, timeout=3000)

    def test_click_follows_the_link(self, page: Page, interactive_server: str):
        _open(page, interactive_server)
        page.locator(MARKER).click()
        page.wait_for_function("() => location.hash === '#first'", timeout=3000)
        expect(page.locator("#first")).to_be_in_viewport()

    def test_closed_aside_marker_previews_the_aside(
        self, page: Page, interactive_server: str
    ):
        # Without the margin column an aside is closed below its paragraph, and
        # its marker previews the aside itself (tests/interactive/test_asides.py).
        _open(page, interactive_server)
        page.locator('a.note-marker[href="#side"]').hover()
        preview = page.locator(PREVIEW)
        expect(preview).to_be_visible(timeout=3000)
        expect(preview).to_contain_text("An aside")
        expect(preview).not_to_contain_text("footnote")


class TestTapPreview:

    def test_first_tap_opens_preview_without_following_the_link(
        self, touch_page: Page
    ):
        touch_page.locator(MARKER).tap()
        preview = touch_page.locator(PREVIEW)
        expect(preview).to_be_visible(timeout=3000)
        expect(preview).to_contain_text("The first footnote")
        touch_page.wait_for_timeout(300)
        assert touch_page.evaluate("location.hash") == ""
        assert _scroll_y(touch_page) == 0

    def test_second_tap_follows_the_link(self, touch_page: Page):
        touch_page.locator(MARKER).tap()
        expect(touch_page.locator(PREVIEW)).to_be_visible(timeout=3000)
        touch_page.locator(MARKER).tap()
        touch_page.wait_for_function("() => location.hash === '#first'", timeout=3000)
        expect(touch_page.locator("#first")).to_be_in_viewport()

    def test_tap_elsewhere_closes_the_preview(self, touch_page: Page):
        touch_page.locator(MARKER).tap()
        expect(touch_page.locator(PREVIEW)).to_be_visible(timeout=3000)
        touch_page.touchscreen.tap(200, 800)
        expect(touch_page.locator(PREVIEW)).to_have_count(0, timeout=3000)
        assert touch_page.evaluate("location.hash") == ""


class TestKeyboard:

    def test_marker_is_in_the_tab_order(self, page: Page, interactive_server: str):
        _open(page, interactive_server)
        marker = page.locator(MARKER)
        assert marker.evaluate("e => e.tabIndex") >= 0
        page.locator(".manuscript .paragraph p").first.click(position={"x": 1, "y": 1})
        for _ in range(30):
            page.keyboard.press("Tab")
            if marker.evaluate("e => e === document.activeElement"):
                break
        assert marker.evaluate("e => e === document.activeElement")

    def test_i_toggles_the_preview(self, page: Page, interactive_server: str):
        _open(page, interactive_server)
        page.locator(MARKER).focus()
        page.keyboard.press("i")
        preview = page.locator(PREVIEW)
        expect(preview).to_be_visible(timeout=3000)
        expect(preview).to_contain_text("The first footnote")
        page.keyboard.press("i")
        expect(preview).to_have_count(0, timeout=3000)

    def test_enter_follows_the_link(self, page: Page, interactive_server: str):
        _open(page, interactive_server)
        page.locator(MARKER).focus()
        page.keyboard.press("Enter")
        page.wait_for_function("() => location.hash === '#first'", timeout=3000)
        expect(page.locator("#first")).to_be_in_viewport()


class TestBacklink:

    def test_backlink_returns_to_the_call(self, page: Page, interactive_server: str):
        _open(page, interactive_server)
        page.locator(MARKER).click()
        page.wait_for_function("() => location.hash === '#first'", timeout=3000)
        page.locator("#first .note-backlink").click()
        page.wait_for_function("() => location.hash === '#call-first'", timeout=3000)
        expect(page.locator("#call-first")).to_be_in_viewport()

    def test_every_entry_links_back_to_its_marker(
        self, page: Page, interactive_server: str
    ):
        _open(page, interactive_server)
        pairs = page.locator("ol.noteslist .note-backlink").evaluate_all(
            "els => els.map(a => [a.closest('li').id, a.getAttribute('href')])"
        )
        assert pairs == [
            ["first", "#call-first"],
            ["second", "#call-second"],
            ["third", "#call-third"],
        ]
        for _, href in pairs:
            expect(page.locator(href)).to_have_class(re.compile(r"\bnote-marker\b"))


class TestNoJavaScript:

    @pytest.fixture
    def nojs_page(self, browser: Browser, interactive_server: str):
        ctx = browser.new_context(java_script_enabled=False)
        pg = ctx.new_page()
        pg.goto(f"{interactive_server}/notes.html")
        pg.wait_for_load_state("load")
        yield pg
        ctx.close()

    def test_list_is_there(self, nojs_page: Page):
        expect(nojs_page.locator("ol.noteslist > li.note")).to_have_count(3)
        expect(nojs_page.locator("#third")).to_contain_text("The third footnote")

    def test_marker_is_a_plain_link_to_the_list(self, nojs_page: Page):
        nojs_page.locator(MARKER).hover()
        nojs_page.wait_for_timeout(500)
        expect(nojs_page.locator(PREVIEW)).to_have_count(0)
        nojs_page.locator(MARKER).click()
        nojs_page.wait_for_url("**/notes.html#first", timeout=3000)
        expect(nojs_page.locator("#first")).to_be_in_viewport()


class TestPrint:

    def test_list_prints_and_preview_does_not(self, page: Page, interactive_server: str):
        _open(page, interactive_server)
        page.locator(MARKER).hover()
        expect(page.locator(PREVIEW)).to_be_visible(timeout=3000)
        page.emulate_media(media="print")
        expect(page.locator(PREVIEW)).to_be_hidden()
        expect(page.locator("ol.noteslist")).to_be_visible()
        expect(page.locator("#first")).to_be_visible()
