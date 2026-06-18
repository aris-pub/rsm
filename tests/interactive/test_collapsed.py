"""Interactive test for the :collapsed: metakey.

A proof marked :collapsed: must be collapsed by JS on load (its steps hidden, its
sketch sibling still visible), while an unmarked proof stays expanded. The
collapse is applied by JS, never baked into the HTML, so JS-off shows everything.
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _load(page: Page, server: str) -> None:
    page.goto(f"{server}/collapsed.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def test_marked_proof_collapses_on_load(page: Page, interactive_server: str):
    _load(page, interactive_server)
    marked = page.locator(".proof.hr[data-start-collapsed]")
    expect(marked).to_have_count(1)
    # JS added hr-collapsed on load (it is not in the static markup).
    expect(marked).to_have_class(re.compile(r"\bhr-collapsed\b"))
    # The collapsed proof's step is hidden, but its sketch sibling stays visible.
    expect(page.locator("#stp-c1")).to_be_hidden()
    expect(page.locator(".sketch.hr")).to_be_visible()


def test_unmarked_proof_stays_expanded(page: Page, interactive_server: str):
    _load(page, interactive_server)
    plain = page.locator(".proof.hr:not([data-start-collapsed])")
    expect(plain).to_have_count(1)
    expect(plain).not_to_have_class(re.compile(r"\bhr-collapsed\b"))
    expect(page.locator("#stp-e1")).to_be_visible()


def test_expanding_does_not_select_the_block(page: Page, interactive_server: str):
    # Clicking the collapse control expands the proof but must not focus (and so
    # visually select) the handrail.
    _load(page, interactive_server)
    marked = page.locator(".proof.hr[data-start-collapsed]")
    marked.locator(".hr-collapse-zone .hr-collapse").click()
    expect(page.locator("#stp-c1")).to_be_visible()  # it expanded
    assert marked.evaluate("el => el.matches(':focus')") is False
