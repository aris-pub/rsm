"""Interactive tests for the handrail Source menu item (rsm-jui).

Every handrail's menu carries a "Source" item. When the element has captured
source (both offsets and a .rsm-source div in the document) the item opens a
modal showing that source. When it does not, the item used to stay enabled and
only fail on click with an error toast reading "No source available for this
element." It must instead be disabled up front, with a reason, so the reader
sees that there is nothing to show before clicking.
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

# A labeled handrail that basic.html always renders with captured source.
HANDRAIL = ".theorem.hr"
STRIP_OFFSETS = (
    "el => { el.removeAttribute('data-source-start');"
    " el.removeAttribute('data-source-end'); }"
)


def _load(page: Page, server: str) -> None:
    page.goto(f"{server}/basic.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _open_menu(page: Page, selector: str):
    hr = page.locator(selector).first
    hr.scroll_into_view_if_needed()
    hr.hover()
    hr.locator(".hr-border-dots").first.click()
    return hr


def _code_item(page: Page):
    return page.locator('#hr-menu-singleton [data-role="code"]')


class TestSourceMenuItem:
    def test_enabled_and_opens_modal_when_source_present(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _open_menu(page, HANDRAIL)
        code = _code_item(page)
        expect(code).to_be_visible()
        expect(code).not_to_have_class(re.compile(r"\bdisabled\b"))
        code.click()
        expect(page.locator(".rsm-source-modal")).to_be_visible()
        expect(page.locator(".toast.error")).to_have_count(0)

    def test_disabled_with_tooltip_when_offsets_missing(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        # A handrailed element with no captured offsets (as happens for
        # synthesized nodes) has no source to show.
        page.locator(HANDRAIL).first.evaluate(STRIP_OFFSETS)
        _open_menu(page, HANDRAIL)
        code = _code_item(page)
        expect(code).to_be_visible()
        expect(code).to_have_class(re.compile(r"\bdisabled\b"))
        expect(code).to_have_attribute("aria-disabled", "true")
        # The reason rides our tooltip system (data-tooltip), not a title.
        expect(code).to_have_attribute("data-tooltip", "no source available")
        expect(code).not_to_have_attribute("title", re.compile(r".+"))

    def test_disabled_when_no_source_div_in_document(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        # No .rsm-source div means nothing to slice from, even with offsets.
        page.evaluate(
            "() => { const d = document.querySelector('.rsm-source');"
            " if (d) d.remove(); }"
        )
        _open_menu(page, HANDRAIL)
        code = _code_item(page)
        expect(code).to_have_class(re.compile(r"\bdisabled\b"))
        expect(code).to_have_attribute("data-tooltip", "no source available")

    def test_clicking_disabled_source_produces_no_toast(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        page.locator(HANDRAIL).first.evaluate(STRIP_OFFSETS)
        _open_menu(page, HANDRAIL)
        code = _code_item(page)
        expect(code).to_have_class(re.compile(r"\bdisabled\b"))
        # Dispatch the click on the item itself so it reaches the delegated
        # handler regardless of any pointer-events on the disabled state.
        code.evaluate("el => el.click()")
        expect(page.locator(".toast")).to_have_count(0)
        expect(page.locator(".rsm-source-modal")).to_have_count(0)
