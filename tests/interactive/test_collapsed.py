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


# The Proof tab must mirror the body's collapse state: a collapsed proof shows a
# single-node card, not the step graph it is hiding.

def _band_in(page: Page) -> None:
    """Scroll the collapsed proof into the rail's reading band."""
    page.locator(".proof.hr[data-start-collapsed]").evaluate(
        "el => { const r = el.getBoundingClientRect();"
        " window.scrollBy(0, r.top - window.innerHeight * 0.18); }"
    )


def test_collapsed_proof_shows_card_not_dag(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)
    page.click('.rail-scope[data-scope="proof"]')
    _band_in(page)
    expect(page.locator(".proof-rail")).to_have_class(re.compile(r"\bproof-collapsed\b"))
    expect(page.locator(".proof-rail-item.shown .rail-collapsed-card")).to_be_visible()
    expect(page.locator(".proof-rail-item.shown .rail-map")).to_be_hidden()


def test_card_expands_proof_and_restores_map(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)
    page.click('.rail-scope[data-scope="proof"]')
    _band_in(page)
    card = page.locator(".proof-rail-item.shown .rail-collapsed-card")
    expect(card).to_be_visible()
    card.click()
    expect(page.locator("#stp-c1")).to_be_visible()  # body proof expanded
    expect(page.locator(".proof-rail")).not_to_have_class(
        re.compile(r"\bproof-collapsed\b")
    )
    expect(page.locator(".proof-rail-item.shown .rail-map")).to_be_visible()
