"""Author-year citations render as links and navigate to the bibliography like
numeric ones, and the a/b year suffix assigned during transform shows in the
rendered citation text (rsm-3ez)."""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def test_author_year_cite_renders_suffix_and_links(page: Page, interactive_server: str):
    page.goto(f"{interactive_server}/citations-author-year.html")
    page.wait_for_function(RSM_READY, timeout=10_000)

    # The first citation is Bourgain's 1985a work (the suffix follows the
    # sorted bibliography order, and bourgainA sorts before bourgainB by title).
    first = page.locator("a.cite").first
    expect(first).to_contain_text("Bourgain")
    expect(first).to_contain_text("1985a")
    assert first.get_attribute("href") == "#bourgainA"

    # Clicking the citation jumps to its bibliography entry (a native anchor).
    first.click()
    page.wait_for_function("() => location.hash === '#bourgainA'", timeout=3000)
    expect(page.locator("#bourgainA")).to_contain_text("Aaa embedding")


def test_multi_author_cite_uses_spelled_out_names(page: Page, interactive_server: str):
    page.goto(f"{interactive_server}/citations-author-year.html")
    page.wait_for_function(RSM_READY, timeout=10_000)

    arora = page.locator('a.cite[href="#arora"]')
    expect(arora).to_contain_text("Arora, Lee and Naor")
    expect(arora).to_contain_text("2008")
