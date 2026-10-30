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


def test_bibliography_entry_is_a_card_with_links_on_hover(page: Page, interactive_server: str):
    """Each entry shows authors and year, title and venue. Its DOI (top right,
    on the authors line) and the way back to the citation (flush right on the
    venue line) show on hover, so the card has no extra row."""
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto(f"{interactive_server}/citations-author-year.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    entry = page.locator("#bourgainA")
    expect(entry.locator(".bib-who")).to_contain_text("Bourgain")
    expect(entry.locator(".bib-title")).not_to_be_empty()
    expect(entry.locator(".bib-num")).to_have_count(0)
    cited = entry.locator(".bib-cited")
    expect(cited.locator("a.backlink")).to_have_count(1)
    who_top = entry.locator(".bib-who").bounding_box()["y"]
    venue_top = entry.locator(".bib-venue").bounding_box()["y"]
    assert abs(cited.bounding_box()["y"] - venue_top) < 6
    doi = entry.locator(".bibitem-doi")
    if doi.count():
        assert abs(doi.bounding_box()["y"] - who_top) < 6
    page.mouse.move(1, 1)
    expect(cited).to_have_css("opacity", "0")
    entry.locator(".bib-title").hover()
    expect(cited).to_have_css("opacity", "1")
    bg = entry.locator(".bib-card").evaluate("e => getComputedStyle(e).backgroundColor")
    assert bg != "rgba(0, 0, 0, 0)"


def test_bibliography_links_share_a_row_on_a_phone(playwright, browser, interactive_server: str):
    """On a phone the DOI and the back links sit together on one row after the
    venue, instead of at the right of the authors and venue lines."""
    ctx = browser.new_context(**playwright.devices["iPhone 13"])
    page = ctx.new_page()
    try:
        page.goto(f"{interactive_server}/citations-author-year.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        entry = page.locator("#bourgainA")
        venue = entry.locator(".bib-venue").bounding_box()
        cited = entry.locator(".bib-cited").bounding_box()
        assert cited["y"] >= venue["y"] + venue["height"] - 2, (venue, cited)
        doi = entry.locator(".bibitem-doi, .bibitem-url")
        if doi.count():
            d = doi.first.bounding_box()
            assert abs(d["y"] - cited["y"]) < 6, (d, cited)
            assert d["x"] < cited["x"]
    finally:
        ctx.close()
