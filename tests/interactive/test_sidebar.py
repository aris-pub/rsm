"""Interactive tests for the two-scope floating sidebar.

Document scope (TOC tree + Notation) and Proof scope (proof-DAG + State), with a
collapse control and localStorage-persisted layout. These assert the class/state
transitions, which are independent of the (separately built) CSS.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _load(page: Page, server: str) -> None:
    page.goto(f"{server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)


def _rail_class(page: Page) -> str:
    return page.locator(".proof-rail").get_attribute("class")


def test_scope_switch(page: Page, interactive_server: str):
    _load(page, interactive_server)
    assert "scope-document" in _rail_class(page)
    page.click('.rail-scope[data-scope="proof"]')
    assert "scope-proof" in _rail_class(page)
    assert "scope-document" not in _rail_class(page)
    page.click('.rail-scope[data-scope="document"]')
    assert "scope-document" in _rail_class(page)
    assert "scope-proof" not in _rail_class(page)


def test_document_notation_subtab(page: Page, interactive_server: str):
    _load(page, interactive_server)
    # Document scope is active by default; switch its sub-tab to Notation.
    assert "doc-view-map" in _rail_class(page)
    page.click('.rail-subtabs-document .rail-tab[data-view="notation"]')
    assert "doc-view-notation" in _rail_class(page)
    assert "doc-view-map" not in _rail_class(page)


def test_proof_state_subtab(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    assert "proof-view-state" in _rail_class(page)
    assert "proof-view-map" not in _rail_class(page)


def test_collapse_persists(page: Page, interactive_server: str):
    _load(page, interactive_server)
    assert "collapsed" not in _rail_class(page)
    page.click(".rail-collapse")
    assert "collapsed" in _rail_class(page)
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)
    assert "collapsed" in _rail_class(page), "collapse state should persist"


def test_scope_persists(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)
    assert "scope-proof" in _rail_class(page), "scope choice should persist"


def test_proof_autofollow(page: Page, interactive_server: str):
    # Short (but still wide: the floating sidebar has a min-width) viewport, so
    # the proof is reliably below the fold at the top.
    page.set_viewport_size({"width": 1280, "height": 460})
    _load(page, interactive_server)
    # At the top the proof is off-screen: no proof is "in view".
    page.evaluate("() => window.scrollTo(0, 0)")
    page.wait_for_function(
        "() => document.querySelector('.proof-rail').classList.contains('no-proof')",
        timeout=5_000,
    )
    # Scroll the proof so its top sits ~20% down, inside the observer's reading
    # band: its rail item becomes the shown one and the Proof scope goes live.
    page.evaluate(
        """() => {
            const el = document.querySelector('.proof[data-nodeid]');
            const y = el.getBoundingClientRect().top + window.scrollY
                      - window.innerHeight * 0.2;
            window.scrollTo(0, y);
        }"""
    )
    page.wait_for_function(
        "() => { const r = document.querySelector('.proof-rail');"
        " return !r.classList.contains('no-proof')"
        " && !!r.querySelector('.rail-proof .proof-rail-item.shown'); }",
        timeout=5_000,
    )


def test_sidebar_absent_without_js(browser, interactive_server: str):
    """Graceful degradation (O8): with JS disabled the sidebar enhancement is
    not shown, but the paper's content remains fully present and readable."""
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()
    try:
        page.goto(f"{interactive_server}/sidebar.html")
        assert not page.locator(".proof-rail").is_visible()
        body = page.locator("body").inner_text()
        assert "spectral radius" in body  # prose is present
        assert "Results" in body  # sections are present
    finally:
        context.close()


def _open_notation(page: Page) -> None:
    # Document scope is active by default; reveal its Notation sub-tab.
    page.click('.rail-subtabs-document .rail-tab[data-view="notation"]')
    page.wait_for_selector(".rail-notation-input", timeout=10_000)


def test_notation_pane_lists_symbol(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _open_notation(page)
    row = page.locator(".rail-notation-row").first
    assert row.locator(".rail-notation-label").text_content() == "eigenvalue"
    assert row.locator(".rail-notation-input").input_value() == "\\lambda"


def test_notation_rebind_rerenders_document(page: Page, interactive_server: str):
    _load(page, interactive_server)
    # The author default \eig renders lambda in the prose.
    assert "λ" in page.locator("span.math").first.text_content()
    _open_notation(page)
    inp = page.locator(".rail-notation-input").first
    inp.fill("\\mu")
    inp.press("Enter")
    assert "μ" in page.locator("span.math").first.text_content()


def test_notation_reset_restores_default(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _open_notation(page)
    inp = page.locator(".rail-notation-input").first
    inp.fill("\\mu")
    inp.press("Enter")
    assert "μ" in page.locator("span.math").first.text_content()
    page.click(".rail-notation-reset")
    assert inp.input_value() == "\\lambda"
    assert "λ" in page.locator("span.math").first.text_content()


# Some \eig instance sits near the viewport center.
_NEAREST_CENTERED = """() => {
    const els = [...document.querySelectorAll('span.math[data-latex]')]
        .filter(e => e.dataset.latex.includes('eig'));
    const c = window.innerHeight / 2;
    return els.some(e => {
        const r = e.getBoundingClientRect();
        return Math.abs(r.top + r.height / 2 - c) < window.innerHeight * 0.3;
    });
}"""


def _first_eig_top(page: Page) -> float:
    return page.evaluate(
        "() => [...document.querySelectorAll('span.math[data-latex]')]"
        ".filter(e=>e.dataset.latex.includes('eig'))[0].getBoundingClientRect().top"
    )


def test_notation_apply_button_commits(page: Page, interactive_server: str):
    _load(page, interactive_server)
    assert "λ" in page.locator("span.math").first.text_content()
    _open_notation(page)
    page.locator(".rail-notation-input").first.fill("\\mu")
    # The explicit Apply button effectuates the change (no Enter needed).
    page.click(".rail-notation-apply")
    assert "μ" in page.locator("span.math").first.text_content()


def test_notation_change_highlights_all_instances(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _open_notation(page)
    page.locator(".rail-notation-input").first.fill("\\mu")
    page.click(".rail-notation-apply")
    # Every instance of the changed macro is highlighted momentarily.
    page.wait_for_function(
        "() => { const els=[...document.querySelectorAll('span.math[data-latex]')]"
        ".filter(e=>e.dataset.latex.includes('eig'));"
        " return els.length>0 && els.every(e=>e.classList.contains('notation-located')); }",
        timeout=3_000,
    )


def test_notation_locate_scrolls_to_nearest(page: Page, interactive_server: str):
    page.set_viewport_size({"width": 1280, "height": 460})
    _load(page, interactive_server)
    _open_notation(page)
    # At the bottom, the nearest \eig is a lower instance, not the intro one.
    page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
    page.click(".rail-notation-locate")
    page.wait_for_function(_NEAREST_CENTERED, timeout=5_000)
    # Nearest, not first: the intro instance stays above the viewport.
    assert _first_eig_top(page) < 0
    # The located symbol is briefly highlighted.
    page.wait_for_function(
        "() => [...document.querySelectorAll('span.math[data-latex]')]"
        ".filter(e=>e.dataset.latex.includes('eig'))"
        ".some(e=>e.classList.contains('notation-located'))",
        timeout=3_000,
    )


def test_notation_apply_scrolls_to_nearest(page: Page, interactive_server: str):
    page.set_viewport_size({"width": 1280, "height": 460})
    _load(page, interactive_server)
    _open_notation(page)
    # Apply while no instance is on screen: it scrolls the nearest into view.
    page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
    page.locator(".rail-notation-input").first.fill("\\mu")
    page.click(".rail-notation-apply")
    page.wait_for_function(_NEAREST_CENTERED, timeout=5_000)
