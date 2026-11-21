"""Tabs (:tabs:): switching in CSS, links into a hidden tab, alignment with the
text, print, and scripting off."""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"


def _load(page: Page, url: str) -> None:
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto(url)
    page.wait_for_function(RSM_READY, timeout=10_000)


def _shown(page: Page, sel: str) -> bool:
    return page.evaluate(
        "(s) => { const e = document.querySelector(s); return !!e && e.getClientRects().length > 0; }",
        sel,
    )


def _wait_shown(page: Page, sel: str) -> None:
    # The URL changes before the hashchange handler selects the tab.
    page.wait_for_function(
        "(s) => { const e = document.querySelector(s); return !!e && e.getClientRects().length > 0; }",
        arg=sel,
        timeout=5_000,
    )


def _checked(page: Page, group: str) -> list[bool]:
    return page.evaluate(
        "(g) => [...document.querySelectorAll(g + ' > .tab-input')].map(i => i.checked)",
        group,
    )


def test_first_tab_shows_and_a_click_switches(page: Page, interactive_server: str):
    _load(page, f"{interactive_server}/tabs.html")
    assert _shown(page, "#fig-a") and not _shown(page, "#fig-b")
    page.locator("#tabs-fig > .tab-label").nth(1).click()
    assert _shown(page, "#fig-b") and not _shown(page, "#fig-a")
    assert _checked(page, "#tabs-fig") == [False, True]


def test_arrow_keys_move_between_tabs(page: Page, interactive_server: str):
    _load(page, f"{interactive_server}/tabs.html")
    page.locator("#tabs-fig > .tab-input").first.focus()
    page.keyboard.press("ArrowRight")
    assert _shown(page, "#fig-b")


def test_a_reference_into_a_hidden_tab_selects_it(page: Page, interactive_server: str):
    _load(page, f"{interactive_server}/tabs.html")
    page.locator('a.reference[href="#fig-b"]').first.click()
    _wait_shown(page, "#fig-b")
    assert _checked(page, "#tabs-fig") == [False, True]
    box = page.locator("#fig-b").bounding_box()
    assert box and 0 <= box["y"] < 900


def test_a_reference_to_a_tab_selects_it(page: Page, interactive_server: str):
    _load(page, f"{interactive_server}/tabs.html")
    page.locator('a.reference[href="#tab-proof"]').first.click()
    _wait_shown(page, "#tab-proof")


def test_loading_with_a_hash_in_a_hidden_tab_selects_it(
    page: Page, interactive_server: str
):
    _load(page, f"{interactive_server}/tabs.html#stp-one")
    assert _shown(page, "#stp-one")
    box = page.locator("#stp-one").bounding_box()
    assert box and 0 <= box["y"] < 900


def test_tab_row_and_panel_text_line_up_with_the_text(
    page: Page, interactive_server: str
):
    _load(page, f"{interactive_server}/tabs.html")
    lefts = page.evaluate(
        """() => {
          const text = document.querySelector('#sec .paragraph > .hr-content-zone').getBoundingClientRect();
          const label = document.querySelector('#tabs-fig > .tab-label').getBoundingClientRect();
          const thm = document.querySelector('#thm > .hr-content-zone').getBoundingClientRect();
          const panels = document.querySelectorAll('.tabs');
          const sketch = panels[1].querySelector('.sketch > .hr-content-zone').getBoundingClientRect();
          return {text: text.left, textRight: text.right, label: label.left, thm: thm.left, sketch: sketch.left, sketchRight: sketch.right};
        }"""
    )
    assert abs(lefts["label"] - lefts["text"]) < 1
    assert abs(lefts["sketch"] - lefts["thm"]) < 1
    assert abs(lefts["sketchRight"] - lefts["textRight"]) < 1


def test_tabs_inside_a_block_line_up_with_its_text(page: Page, interactive_server: str):
    _load(page, f"{interactive_server}/tabs.html")
    d = page.evaluate(
        """() => {
          const remark = document.querySelector('.remark > .hr-content-zone');
          const label = remark.querySelector('.tabs > .tab-label').getBoundingClientRect();
          const para = remark.querySelector('.tabs > .tab .paragraph > .hr-content-zone').getBoundingClientRect();
          return {remark: remark.getBoundingClientRect().left, label: label.left, para: para.left};
        }"""
    )
    assert abs(d["label"] - d["remark"]) < 1
    assert abs(d["para"] - d["remark"]) < 1


def test_print_shows_every_tab_and_no_row(page: Page, interactive_server: str):
    _load(page, f"{interactive_server}/tabs.html")
    page.emulate_media(media="print")
    assert _shown(page, "#fig-a") and _shown(page, "#fig-b")
    assert not _shown(page, "#tabs-fig > .tab-label")


def test_scripting_off_shows_every_tab_and_no_row(browser, interactive_server: str):
    ctx = browser.new_context(
        java_script_enabled=False, viewport={"width": 1280, "height": 900}
    )
    page = ctx.new_page()
    page.goto(f"{interactive_server}/tabs.html")
    page.wait_for_load_state("load")
    assert _shown(page, "#fig-a") and _shown(page, "#fig-b")
    assert not _shown(page, "#tabs-fig > .tab-label")
    ctx.close()
