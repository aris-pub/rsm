"""Interactive test: collapse menu item labels must reflect collapsed state.

Regression guard for the singleton-menu refactor (f2f499e), which removed the
"Collapse" <-> "Expand" label flip that openHandrail/closeHandrail used to do on
each handrail's own menu. With one shared menu, the flip has to happen when the
menu is opened (showMenuFor), or the item is stuck reading "Collapse" even on an
already-collapsed block.
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _load(page: Page, server: str) -> None:
    page.goto(f"{server}/collapse-menu.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _dots(step):
    return step.locator(":scope > .hr-border-zone .hr-border-dots")


def _collapse_text(page: Page):
    return page.locator("#hr-menu-singleton [data-role='collapse'] .hr-menu-item-text")


def _collapse_all_text(page: Page):
    return page.locator(
        "#hr-menu-singleton [data-role='collapse-all'] .hr-menu-item-text"
    )


def test_collapse_label_reads_collapse_when_expanded(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _dots(page.locator("#stp-outer")).click()
    expect(_collapse_text(page)).to_have_text("Collapse")


def test_collapse_label_flips_to_expand_when_collapsed(page: Page, interactive_server: str):
    _load(page, interactive_server)
    step = page.locator("#stp-outer")
    _dots(step).click()
    # Collapse the step through its menu item (steps have no left chevron).
    page.locator("#hr-menu-singleton [data-role='collapse']").click()
    expect(step).to_have_class(re.compile(r"\bhr-collapsed\b"))
    # Reopen the menu: the first dots click hides the still-open menu, the second
    # re-runs showMenuFor, which is where the label must be re-derived.
    _dots(step).click()
    _dots(step).click()
    expect(_collapse_text(page)).to_have_text("Expand")


def test_collapse_label_updates_in_place_on_click(page: Page, interactive_server: str):
    # Clicking the item collapses the block; the label must flip immediately,
    # while the menu stays open, not only on the next open.
    _load(page, interactive_server)
    step = page.locator("#stp-outer")
    _dots(step).click()
    page.locator("#hr-menu-singleton [data-role='collapse']").click()
    expect(step).to_have_class(re.compile(r"\bhr-collapsed\b"))
    expect(_collapse_text(page)).to_have_text("Expand")


def test_clicking_menu_item_does_not_select_block(page: Page, interactive_server: str):
    # Clicking a menu item runs its action but must not focus (and so highlight
    # in blue) the block, the same rule the collapse chevron already follows.
    _load(page, interactive_server)
    step = page.locator("#stp-outer")
    _dots(step).click()
    page.locator("#hr-menu-singleton [data-role='collapse-all']").click()
    assert step.evaluate("el => el.matches(':focus')") is False


def test_dot_shortcut_opens_focused_menu(page: Page, interactive_server: str):
    # The "." shortcut toggles the focused handrail's menu. It must drive the
    # shared singleton (move it into the focused handrail's zone), not the old
    # per-handrail menu-zone, which is empty until the singleton is moved in.
    _load(page, interactive_server)
    step = page.locator("#stp-outer")
    step.focus()
    page.keyboard.press(".")
    expect(step.locator(":scope > .hr-menu-zone #hr-menu-singleton")).to_be_visible()


def test_escape_closes_open_menu(page: Page, interactive_server: str):
    _load(page, interactive_server)
    step = page.locator("#stp-outer")
    step.focus()
    page.keyboard.press(".")
    expect(step.locator(":scope > .hr-menu-zone #hr-menu-singleton")).to_be_visible()
    page.keyboard.press("Escape")
    expect(page.locator("#hr-menu-singleton")).to_be_hidden()


def test_comma_collapses_focused_step(page: Page, interactive_server: str):
    _load(page, interactive_server)
    step = page.locator("#stp-outer")
    step.focus()
    page.keyboard.press(",")
    expect(step).to_have_class(re.compile(r"\bhr-collapsed\b"))


def test_semicolon_collapses_all_substeps(page: Page, interactive_server: str):
    _load(page, interactive_server)
    step = page.locator("#stp-outer")
    step.focus()
    page.keyboard.press(";")
    expect(page.locator("#stp-inner-a")).to_have_class(re.compile(r"\bhr-collapsed\b"))


def test_collapse_all_label_reflects_substep_state(page: Page, interactive_server: str):
    _load(page, interactive_server)
    # Collapse both inner steps via their own menus (not via "Collapse all", so the
    # singleton's label is not pre-set by that action).
    for sid in ("stp-inner-a", "stp-inner-b"):
        inner = page.locator(f"#{sid}")
        _dots(inner).click()
        page.locator("#hr-menu-singleton [data-role='collapse']").click()
        expect(inner).to_have_class(re.compile(r"\bhr-collapsed\b"))
    # Opening the outer step's menu must now show the all-collapsed label.
    _dots(page.locator("#stp-outer")).click()
    expect(_collapse_all_text(page)).to_have_text("Expand all")
