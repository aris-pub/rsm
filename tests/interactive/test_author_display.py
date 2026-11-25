"""The "N more" button in a shortened author list shows every author."""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"

SHORT = "Ada Lovelace1, Bo Chen2, Cy Diaz3, 3 more, Gil Moreau3, Hana Sato4"
FULL = (
    "Ada Lovelace1, Bo Chen2, Cy Diaz3, Dana Patel4, Eli Novak1, Fay Okafor2, "
    "Gil Moreau3, Hana Sato4"
)


def _load(page: Page, server: str):
    page.goto(f"{server}/author_display.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _shown_text(page: Page) -> str:
    return page.locator("p.author-names").inner_text()


def test_list_is_shortened_on_load(page: Page, interactive_server: str):
    _load(page, interactive_server)
    assert _shown_text(page) == SHORT
    button = page.get_by_role("button", name="Show 3 more authors")
    expect(button).to_be_visible()
    expect(button).to_have_text("3 more")


def test_click_shows_every_author_and_removes_the_button(
    page: Page, interactive_server: str
):
    _load(page, interactive_server)
    page.get_by_role("button", name="Show 3 more authors").click()
    assert _shown_text(page) == FULL
    expect(page.locator("p.author-names button")).to_have_count(0)
    expect(page.locator(".author-count").first).to_have_text("4 affiliations")


@pytest.mark.parametrize("key", ["Enter", "Space"])
def test_keyboard_shows_every_author(page: Page, interactive_server: str, key):
    _load(page, interactive_server)
    page.get_by_role("button", name="Show 3 more authors").focus()
    page.keyboard.press(key)
    assert _shown_text(page) == FULL
    expect(page.locator("p.author-names button")).to_have_count(0)


def test_every_author_shows_without_javascript(browser, interactive_server: str):
    ctx = browser.new_context(java_script_enabled=False)
    page = ctx.new_page()
    page.goto(f"{interactive_server}/author_display.html")
    text = _shown_text(page)
    ctx.close()
    assert text == FULL
