"""The "N more" pill in a shortened author list shows every author, and the
"Show fewer" pill shortens the list again."""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"

SHORT = "Ada Lovelace1, Bo Chen2, Cy Diaz3, 3 more, Gil Moreau3, Hana Sato4"
FULL = (
    "Ada Lovelace1, Bo Chen2, Cy Diaz3, Dana Patel4, Eli Novak1, Fay Okafor2, "
    "Gil Moreau3, Hana Sato4"
)

FULL_OPEN = (
    "Ada Lovelace1, Bo Chen2, Cy Diaz3, Dana Patel4, Eli Novak1, Fay Okafor2 "
    "Show fewer, Gil Moreau3, Hana Sato4"
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


def test_click_shows_every_author_and_the_show_fewer_pill(
    page: Page, interactive_server: str
):
    _load(page, interactive_server)
    page.get_by_role("button", name="Show 3 more authors").click()
    assert _shown_text(page) == FULL_OPEN
    expect(page.get_by_role("button", name="Show 3 more authors")).to_be_hidden()
    page.get_by_role("button", name="Show fewer authors").click()
    assert _shown_text(page) == SHORT


@pytest.mark.parametrize("key", ["Enter", "Space"])
def test_keyboard_shows_every_author(page: Page, interactive_server: str, key):
    _load(page, interactive_server)
    page.get_by_role("button", name="Show 3 more authors").focus()
    page.keyboard.press(key)
    assert _shown_text(page) == FULL_OPEN


def test_every_author_shows_without_javascript(browser, interactive_server: str):
    ctx = browser.new_context(java_script_enabled=False)
    page = ctx.new_page()
    page.goto(f"{interactive_server}/author_display.html")
    text = _shown_text(page)
    ctx.close()
    assert text == FULL
