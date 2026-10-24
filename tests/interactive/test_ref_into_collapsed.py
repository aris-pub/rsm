"""Regression test for rsm-r2c: following a reference into a collapsed block
must open the block, not land the reader on hidden content.

Clicking a :ref: (or loading a URL hash) whose target sits inside a collapsed
handrail used to set the hash and focus the target while it stayed hidden. The
fix opens every collapsed .hr ancestor of the target (outermost first) before
focusing it, for both hashchange and an initial load with a hash, without
writing the reader's persisted collapse state.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def wait_for_rsm(page):
    page.wait_for_function(RSM_READY, timeout=10_000)


def _is_revealed(page: Page, node_id: str) -> bool:
    """True when the element is rendered (has an offset parent)."""
    return page.evaluate(
        "(id) => { const e = document.getElementById(id);"
        " return !!e && e.offsetParent !== null; }",
        node_id,
    )


def _in_viewport(page: Page, node_id: str) -> bool:
    return page.evaluate(
        "(id) => { const e = document.getElementById(id); if (!e) return false;"
        " const r = e.getBoundingClientRect();"
        " return r.bottom > 0 && r.top < window.innerHeight; }",
        node_id,
    )


def _active_id(page: Page) -> str:
    return page.evaluate("() => document.activeElement && document.activeElement.id")


def test_clicking_ref_opens_all_collapsed_ancestors(
    page: Page, interactive_server: str
):
    page.goto(f"{interactive_server}/ref-into-collapsed.html")
    wait_for_rsm(page)

    # Precondition: the inner step is hidden inside the collapsed proof + step.
    assert not _is_revealed(page, "st-inner")

    page.click('a.reference[href="#st-inner"]')
    page.wait_for_function(
        "() => { const e = document.getElementById('st-inner');"
        " return e && e.offsetParent !== null; }",
        timeout=5_000,
    )

    assert _is_revealed(page, "st-inner"), "inner step still hidden after ref click"
    assert _in_viewport(page, "st-inner"), "inner step not scrolled into view"
    assert _active_id(page) == "st-inner", "inner step did not receive focus"


def test_clicking_ref_to_substep_reveals_it(page: Page, interactive_server: str):
    page.goto(f"{interactive_server}/ref-into-collapsed.html")
    wait_for_rsm(page)
    assert not _is_revealed(page, "st-outer")

    page.click('a.reference[href="#st-outer"]')
    page.wait_for_function(
        "() => { const e = document.getElementById('st-outer');"
        " return e && e.offsetParent !== null; }",
        timeout=5_000,
    )
    assert _is_revealed(page, "st-outer")
    assert _active_id(page) == "st-outer"


def test_direct_hash_load_shows_target_expanded(
    page: Page, interactive_server: str
):
    page.goto(f"{interactive_server}/ref-into-collapsed.html#st-inner")
    wait_for_rsm(page)
    page.wait_for_function(
        "() => { const e = document.getElementById('st-inner');"
        " return e && e.offsetParent !== null; }",
        timeout=5_000,
    )
    assert _is_revealed(page, "st-inner"), "direct #hash load left the target hidden"


def test_no_hash_load_stays_collapsed(page: Page, interactive_server: str):
    """Control: without a hash the author's collapsed default is honored."""
    page.goto(f"{interactive_server}/ref-into-collapsed.html")
    wait_for_rsm(page)
    assert not _is_revealed(page, "st-inner"), (
        "proof should stay collapsed when nothing navigates into it"
    )


def test_ref_expansion_does_not_persist(page: Page, interactive_server: str):
    page.goto(f"{interactive_server}/ref-into-collapsed.html")
    wait_for_rsm(page)

    key_and_before = page.evaluate(
        "() => { const k = 'rsm-collapse:' + location.pathname;"
        " return [k, localStorage.getItem(k)]; }"
    )
    before = key_and_before[1]

    page.click('a.reference[href="#st-inner"]')
    page.wait_for_function(
        "() => { const e = document.getElementById('st-inner');"
        " return e && e.offsetParent !== null; }",
        timeout=5_000,
    )

    after = page.evaluate(
        "(k) => localStorage.getItem(k)", key_and_before[0]
    )
    assert after == before, (
        f"reference-driven expansion wrote collapse state: {before!r} -> {after!r}"
    )
