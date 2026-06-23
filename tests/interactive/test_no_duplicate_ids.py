"""Regression: cloning subtrees into the live DOM must never duplicate an id.

Two paths clone block subtrees into the page: reference/cite tooltips
(tooltips.js) and the proof-rail State panel (prooftree.js cloneClean). Once
every block carries an `id` (so rail/keyboard jumps can navigate by hash), any
clone that copies a subtree must strip ids first, or the document ends up with
duplicate ids -- invalid HTML that also breaks getElementById and hash nav.

This test pins the invariant across both clone paths.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _duplicate_ids(page: Page):
    # Scope to HTML block ids; ignore SVG-internal defs/markers (icon symbols,
    # TOC arc markers) which are a separate, pre-existing generated-id concern
    # and not what the block-clone paths touch.
    return page.evaluate(
        """() => {
        const els = [...document.querySelectorAll('[id]')].filter(
            (e) => e.tagName.toLowerCase() !== 'svg' && !e.closest('svg')
        );
        const seen = new Set();
        const dups = new Set();
        for (const e of els) {
            if (seen.has(e.id)) dups.add(e.id);
            else seen.add(e.id);
        }
        return [...dups];
    }"""
    )


def test_no_duplicate_ids_after_tooltip_and_state_panel(page: Page, interactive_server: str):
    # Desktop width so the proof-rail is the sidebar (its controls are hidden in
    # the bottom-drawer below the 1320px breakpoint).
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{interactive_server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)

    assert _duplicate_ids(page) == [], "duplicate ids on initial load"

    # Open a reference tooltip: this clones the target block into the popup.
    ref = page.wait_for_selector('.manuscript a.reference[href="#thm-x"]', timeout=5_000)
    ref.scroll_into_view_if_needed()
    ref.hover()
    page.wait_for_selector(".tooltipster-base", state="visible", timeout=5_000)
    assert _duplicate_ids(page) == [], "duplicate ids after opening a reference tooltip"

    # Switch to Proof scope: the State panel clones blocks via cloneClean.
    page.click('.rail-scope[data-scope="proof"]')
    page.wait_for_timeout(400)
    assert _duplicate_ids(page) == [], "duplicate ids after populating the proof State panel"
