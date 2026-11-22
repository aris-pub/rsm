"""Switching a TOC between list and tree from its handrail menu (rsm-1tj).

toggleTocView used to call tocarcs.draw, which tocarcs.js does not export, so
every switch to tree threw and the rest of the handler (the menu text flip)
never ran. A TOC that starts as a list was also never wired for hover, because
tocarcs only wires trees present at load.
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"


def _open_menu(page: Page) -> None:
    hr = page.locator("nav.toc > .hr").first
    hr.hover()
    hr.locator(".hr-border-dots").click()
    expect(page.locator("#hr-menu-singleton [data-role='toc-view']")).to_be_visible()


def _toc_view_item(page: Page):
    return page.locator("#hr-menu-singleton [data-role='toc-view']")


def test_toc_toggles_list_and_tree_without_errors(page: Page, interactive_server: str):
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"{interactive_server}/toc-view.html")
    page.wait_for_function(RSM_READY, timeout=10_000)

    toc = page.locator("nav.toc")
    svg = toc.locator("svg.toc-tree")
    text = _toc_view_item(page).locator(".hr-menu-item-text")

    expect(toc).not_to_have_class("toc tree")
    expect(svg).to_be_hidden()

    for want_tree in (True, False, True):
        _open_menu(page)
        expect(text).to_have_text("View as tree" if want_tree else "View as list")
        _toc_view_item(page).click()
        if want_tree:
            expect(toc).to_have_class("toc tree")
            expect(svg).to_be_visible()
        else:
            expect(toc).to_have_class("toc")
            expect(svg).to_be_hidden()
        # The label flips in place, without reopening the menu.
        expect(text).to_have_text("View as list" if want_tree else "View as tree")
        page.keyboard.press("Escape")

    assert errors == [], f"page errors while toggling the TOC view: {errors}"

    # The tree shows its arcs, and since this TOC started as a list it must
    # have been wired on the switch: hovering a node fades the unrelated ones.
    edges = svg.locator(".toc-edge")
    assert edges.count() > 0
    assert edges.first.bounding_box()["width"] > 0
    assert svg.get_attribute("data-wired") == "1"
    svg.locator(".toc-node[data-idx='0']").hover()
    expect(svg.locator(".toc-node.toc-faded").first).to_be_attached()


def test_tree_toc_in_the_text_previews_like_the_sidebar(
    page: Page, interactive_server: str
):
    """A node of the TOC graph in the text shows the section preview on hover,
    as the same graph in the sidebar does."""
    page.goto(f"{interactive_server}/toc-view.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    _open_menu(page)
    _toc_view_item(page).click()
    page.keyboard.press("Escape")
    node = page.locator("nav.toc svg.toc-tree .toc-node[data-idx='0']")
    expect(node).to_have_class(re.compile(r"\btooltipstered\b"))
    node.hover()
    tip = page.locator(".tooltipster-base").last
    expect(tip).to_be_visible(timeout=3000)
    expect(tip).to_contain_text("First section")


# ---- the list/graph icons on the heading line (rsm-ucv) ----


def _icon(page: Page, view: str):
    return page.locator(f"nav.toc .toc-switch button[data-toc-view='{view}']")


def test_icons_switch_the_view(page: Page, interactive_server: str):
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"{interactive_server}/toc-view.html")
    page.wait_for_function(RSM_READY, timeout=10_000)

    toc = page.locator("nav.toc")
    svg = toc.locator("svg.toc-tree")
    list_btn, tree_btn = _icon(page, "list"), _icon(page, "tree")
    expect(list_btn).to_be_visible()
    expect(tree_btn).to_be_visible()
    expect(list_btn).to_have_attribute("aria-pressed", "true")
    expect(tree_btn).to_have_attribute("aria-pressed", "false")

    tree_btn.click()
    expect(toc).to_have_class("toc tree")
    expect(svg).to_be_visible()
    expect(list_btn).to_have_attribute("aria-pressed", "false")
    expect(tree_btn).to_have_attribute("aria-pressed", "true")
    assert svg.get_attribute("data-wired") == "1"

    # Clicking the icon of the view on screen keeps that view.
    tree_btn.click()
    expect(toc).to_have_class("toc tree")

    list_btn.click()
    expect(toc).to_have_class("toc")
    expect(svg).to_be_hidden()
    expect(list_btn).to_have_attribute("aria-pressed", "true")
    expect(tree_btn).to_have_attribute("aria-pressed", "false")
    assert errors == [], errors


def test_icons_and_menu_item_stay_in_step(page: Page, interactive_server: str):
    page.goto(f"{interactive_server}/toc-view.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    text = _toc_view_item(page).locator(".hr-menu-item-text")

    # Menu item first: the icons follow.
    _open_menu(page)
    _toc_view_item(page).click()
    page.keyboard.press("Escape")
    expect(_icon(page, "tree")).to_have_attribute("aria-pressed", "true")
    expect(_icon(page, "list")).to_have_attribute("aria-pressed", "false")

    # Icon first: the menu item follows.
    _icon(page, "list").click()
    _open_menu(page)
    expect(text).to_have_text("View as tree")
    page.keyboard.press("Escape")
    _icon(page, "tree").click()
    _open_menu(page)
    expect(text).to_have_text("View as list")


def test_icons_are_hidden_without_scripting(browser, interactive_server: str):
    ctx = browser.new_context(java_script_enabled=False)
    try:
        page = ctx.new_page()
        page.goto(f"{interactive_server}/toc-view.html")
        page.wait_for_load_state("load")
        expect(page.locator("nav.toc .toc-switch")).to_be_attached()
        expect(page.locator("nav.toc .toc-switch")).to_be_hidden()
    finally:
        ctx.close()
