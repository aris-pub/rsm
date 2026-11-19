"""The list/graph switch in the sidebar's Contents view (rsm-ucv).

The fixture has a :toc: shown as a list, so both the page and the sidebar start
as a list. The two switches keep separate settings, and the sidebar's choice is
saved with the other sidebar views.
"""

import pytest
from playwright.sync_api import Browser, Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"
URL = "/toc_switch_sidebar.html"


def _load(page: Page, server: str, clear: bool = True) -> None:
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(server + URL)
    page.wait_for_function(RSM_READY, timeout=10_000)
    if clear:
        page.evaluate("() => localStorage.clear()")
        page.reload()
        page.wait_for_function(RSM_READY, timeout=10_000)


def _show(page: Page, view: str) -> None:
    btn = page.locator(f'.rail-strip-btn[data-view="{view}"]')
    if btn.get_attribute("aria-pressed") != "true":
        btn.click()
    page.wait_for_selector(".proof-rail.open", timeout=5_000)


def _rail_btn(page: Page, view: str):
    return page.locator(f".rail-head .rail-toc-switch button[data-toc-view='{view}']")


def _page_btn(page: Page, view: str):
    return page.locator(f"nav.toc .toc-switch button[data-toc-view='{view}']")


def test_sidebar_switch_shows_list_and_graph(page: Page, interactive_server: str):
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    _load(page, interactive_server)
    _show(page, "contents")
    panel = page.locator(".rail-doc-map")
    rail_list = panel.locator("ul.contents")
    rail_svg = panel.locator("svg.toc-tree")

    expect(_rail_btn(page, "list")).to_be_visible()
    expect(_rail_btn(page, "list")).to_have_attribute("aria-pressed", "true")
    expect(rail_list).to_be_visible()
    expect(rail_svg).to_be_hidden()

    _rail_btn(page, "tree").click()
    expect(_rail_btn(page, "tree")).to_have_attribute("aria-pressed", "true")
    expect(_rail_btn(page, "list")).to_have_attribute("aria-pressed", "false")
    expect(rail_svg).to_be_visible()
    expect(rail_list).to_be_hidden()

    _rail_btn(page, "list").click()
    expect(rail_list).to_be_visible()
    expect(rail_svg).to_be_hidden()
    assert errors == [], errors


def test_sidebar_switch_shown_only_in_contents_view(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _show(page, "contents")
    expect(page.locator(".rail-toc-switch")).to_be_visible()
    _show(page, "notation")
    expect(page.locator(".rail-toc-switch")).to_be_hidden()
    _show(page, "reading")
    expect(page.locator(".rail-toc-switch")).to_be_hidden()


def test_page_and_sidebar_switches_are_separate(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _show(page, "contents")
    toc = page.locator("nav.toc")

    _rail_btn(page, "tree").click()
    expect(page.locator(".rail-doc-map")).to_have_class("rail-panel rail-doc-map tree")
    expect(toc).to_have_class("toc")
    expect(_page_btn(page, "list")).to_have_attribute("aria-pressed", "true")

    _page_btn(page, "tree").click()
    expect(toc).to_have_class("toc tree")
    _page_btn(page, "list").click()
    expect(toc).to_have_class("toc")
    expect(page.locator(".rail-doc-map")).to_have_class("rail-panel rail-doc-map tree")
    expect(_rail_btn(page, "tree")).to_have_attribute("aria-pressed", "true")


def test_sidebar_choice_is_saved_and_page_choice_is_not(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _show(page, "contents")
    _rail_btn(page, "tree").click()
    _page_btn(page, "tree").click()
    expect(page.locator("nav.toc")).to_have_class("toc tree")

    _load(page, interactive_server, clear=False)
    _show(page, "contents")
    expect(page.locator(".rail-doc-map")).to_have_class("rail-panel rail-doc-map tree")
    expect(_rail_btn(page, "tree")).to_have_attribute("aria-pressed", "true")
    # The page switch is not saved: the author's list view is back.
    expect(page.locator("nav.toc")).to_have_class("toc")
    expect(_page_btn(page, "list")).to_have_attribute("aria-pressed", "true")


def test_long_entries_end_in_an_ellipsis(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _show(page, "contents")
    panel = page.locator(".rail-doc-map")
    link = panel.locator("ul.contents a[href='#sec-long']")
    expect(link).to_be_visible()
    style = link.evaluate(
        "el => { const s = getComputedStyle(el);"
        " return [s.textOverflow, s.whiteSpace, s.overflowX]; }"
    )
    assert style == ["ellipsis", "nowrap", "hidden"], style
    assert link.evaluate("el => el.scrollWidth > el.clientWidth"), "the long title was not cut"
    assert panel.evaluate("el => el.scrollWidth <= el.clientWidth"), "the list scrolls sideways"
    box = link.bounding_box()
    assert box["height"] < 30, "the entry wraps onto more than one line"


def test_sidebar_switch_hidden_without_scripting(browser: Browser, interactive_server: str):
    ctx = browser.new_context(java_script_enabled=False, viewport={"width": 1400, "height": 900})
    try:
        page = ctx.new_page()
        page.goto(interactive_server + URL)
        page.wait_for_load_state("load")
        expect(page.locator(".rail-toc-switch")).to_be_attached()
        expect(page.locator(".rail-toc-switch")).to_be_hidden()
        expect(page.locator("nav.toc .toc-switch")).to_be_hidden()
    finally:
        ctx.close()
