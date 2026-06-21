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


def test_proof_state_refs_get_body_tooltips(page: Page, interactive_server: str):
    """A reference cloned into the live Proof > State panel must get the same
    tooltipster tooltip as in the body.

    Regression: cloneClean() deep-cloned the body link, copying its
    ``tooltipstered`` class but not the tooltipster instance, so the sidebar
    link looked initialized yet had no working tooltip, and createTooltips()'s
    ``:not(.tooltipstered)`` filter then skipped it on re-init.
    """
    page.set_viewport_size({"width": 1280, "height": 460})
    _load(page, interactive_server)
    # Go live: Proof scope, State sub-tab.
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    # Scroll a late step into the reading band so its accumulated hypotheses
    # (which include the :assume: that references thm-x) render in the panel.
    page.evaluate(
        """() => {
            const steps = document.querySelectorAll('.proof .step');
            const el = steps[steps.length - 1];
            const y = el.getBoundingClientRect().top + window.scrollY
                      - window.innerHeight * 0.4;
            window.scrollTo(0, y);
        }"""
    )
    link = page.wait_for_selector(".rail-state a.reference", timeout=5_000)
    # The same hover-triggered tooltipster tooltip as in the body must appear.
    link.hover()
    tip = page.wait_for_selector(".tooltipster-base", state="visible", timeout=3_000)
    assert tip.is_visible()


def test_proof_state_shows_document_context(page: Page, interactive_server: str):
    """The Proof > State panel shows a "Context" group carrying the symbols and
    assumptions introduced in prose before the proof (here, the `:write:` that
    defines the spectral radius), distinct from the proof's own hypotheses."""
    page.set_viewport_size({"width": 1280, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    # Scroll the proof into the reading band so the State panel renders live.
    page.evaluate(
        """() => {
            const el = document.querySelector('.proof[data-nodeid]');
            const y = el.getBoundingClientRect().top + window.scrollY
                      - window.innerHeight * 0.2;
            window.scrollTo(0, y);
        }"""
    )
    block = page.wait_for_selector(".rail-state .rail-context", timeout=5_000)
    text = block.inner_text()
    assert "in scope" in text.lower()  # the document-context group, label uppercased by CSS
    assert "spectral radius" in text
    # the cloned introduction keeps its construct keyword (WRITE)
    assert block.query_selector(".keyword") is not None


def test_proof_state_math_is_typeset(page: Page, interactive_server: str):
    """Regression: cloned proof-step fragments came into the State panel as raw
    LaTeX (\\(...\\)); the panel must re-typeset them so no raw delimiters remain
    and real MathML is present (also an a11y requirement)."""
    page.set_viewport_size({"width": 1280, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    page.evaluate(
        """() => {
            const steps = document.querySelectorAll('.proof .step');
            const el = steps[steps.length - 1];
            const y = el.getBoundingClientRect().top + window.scrollY
                      - window.innerHeight * 0.4;
            window.scrollTo(0, y);
        }"""
    )
    panel = page.wait_for_selector(".rail-state .rail-state-block", timeout=5_000)
    state = page.locator(".rail-state")
    # no raw inline-math delimiters survive anywhere in the panel
    assert "\\(" not in state.inner_text()
    # and the math is real MathML, in the ASSUME group specifically
    assert page.locator(".rail-state .rail-hyps math").count() > 0


def test_proof_state_group_keyboard_operable(page: Page, interactive_server: str):
    """WCAG 2.1 AA: the State-panel group headers must be reachable and operable
    by keyboard alone. Each header is a native <button> with aria-expanded, so
    Tab can focus it and Enter toggles its band collapsed/expanded."""
    page.set_viewport_size({"width": 1280, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    page.evaluate(
        """() => {
            const el = document.querySelector('.proof[data-nodeid]');
            const y = el.getBoundingClientRect().top + window.scrollY
                      - window.innerHeight * 0.2;
            window.scrollTo(0, y);
        }"""
    )
    head = page.wait_for_selector(".rail-state .rail-goal .rail-state-head", timeout=5_000)
    # The PROVE band renders expanded.
    assert head.get_attribute("aria-expanded") == "true"
    # Keyboard-focusable: focus lands on the native button (not skipped/disabled).
    head.focus()
    assert page.evaluate(
        "() => document.activeElement.classList.contains('rail-state-head')"
    )
    # Enter on the focused header collapses the band...
    head.press("Enter")
    assert head.get_attribute("aria-expanded") == "false"
    assert page.locator(".rail-state .rail-goal.collapsed").count() == 1
    # ...and Enter again re-expands it.
    head.press("Enter")
    assert head.get_attribute("aria-expanded") == "true"
    assert page.locator(".rail-state .rail-goal.collapsed").count() == 0


# The intro :write: that defines the spectral radius sits near the viewport center.
_WRITE_CENTERED = """() => {
    const el = [...document.querySelectorAll('.write')]
        .find(e => !e.closest('.proof-rail') && e.textContent.includes('spectral radius'));
    if (!el) return false;
    const c = window.innerHeight / 2;
    const r = el.getBoundingClientRect();
    return Math.abs(r.top + r.height / 2 - c) < window.innerHeight * 0.35;
}"""


def _scroll_proof_into_band(page: Page) -> None:
    page.evaluate(
        """() => {
            const el = document.querySelector('.proof[data-nodeid]');
            const y = el.getBoundingClientRect().top + window.scrollY
                      - window.innerHeight * 0.2;
            window.scrollTo(0, y);
        }"""
    )


def test_proof_state_rows_are_uniform_jump_rows(page: Page, interactive_server: str):
    """No ⟨n⟩ step chips and no reserved chip gutter: every row in every band is
    a uniform jump-to-source row, including the In-scope (document-context)
    rows, which previously had no jump action at all."""
    page.set_viewport_size({"width": 1280, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    _scroll_proof_into_band(page)
    page.wait_for_selector(".rail-state .rail-context", timeout=5_000)
    assert page.locator(".rail-state .rail-step-badge").count() == 0
    assert page.locator(".rail-state .rail-hyps .rail-jump-row").count() > 0
    assert page.locator(".rail-state .rail-context .rail-jump-row").count() > 0
    # The provenance number is back, in the left gutter: a ⟨n⟩ step number in
    # ASSUME, a (n) section number in IN SCOPE.
    hyp_nums = page.locator(".rail-state .rail-hyps .rail-state-num")
    hyp_texts = [hyp_nums.nth(i).inner_text().strip() for i in range(hyp_nums.count())]
    assert any(t.startswith("⟨") and t.endswith("⟩") for t in hyp_texts)
    ctx_num = page.locator(".rail-state .rail-context .rail-state-num").first.inner_text()
    assert ctx_num.startswith("(") and ctx_num.endswith(")")


def test_proof_state_context_row_jumps_to_source(page: Page, interactive_server: str):
    """Clicking an In-scope row scrolls the body to where that item was
    introduced in prose: here the :write: defining the spectral radius, up in
    the Introduction well above the proof."""
    page.set_viewport_size({"width": 1280, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    _scroll_proof_into_band(page)
    row = page.wait_for_selector(
        ".rail-state .rail-context li:has-text('spectral radius')", timeout=5_000
    )
    # The intro write starts off-screen (above the proof in view)...
    assert page.evaluate(_WRITE_CENTERED) is False
    # ...and clicking the row scrolls it to the reading band.
    row.click()
    page.wait_for_function(_WRITE_CENTERED, timeout=5_000)


def test_proof_state_setup_goal_is_a_gutter_row(page: Page, interactive_server: str):
    """When the current step is a setup step (no own claim), PROVE shows a
    clamped preview of the theorem statement (so the collapsed state still
    carries information), as a gutter row: the .rail-jump-row treatment (rule +
    hover), a (section) marker, and a "show more" toggle."""
    page.set_viewport_size({"width": 1280, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    # Center the proof's first step, an :assume: working toward the theorem.
    page.evaluate(
        """() => {
            const step = document.querySelector('.proof .step');
            const y = step.getBoundingClientRect().top + window.scrollY
                      - window.innerHeight * 0.5;
            window.scrollTo(0, y);
        }"""
    )
    summary = page.wait_for_selector(
        ".rail-state .rail-goal .rail-goal-summary", timeout=5_000
    )
    assert "rail-jump-row" in (summary.get_attribute("class") or "")
    # the preview shows the statement text, not a blank disclosure
    preview = page.locator(".rail-state .rail-goal .rail-goal-text").inner_text()
    assert preview.strip()
    assert page.locator(".rail-state .rail-goal .rail-goal-toggle").count() == 1
    num = page.locator(".rail-state .rail-goal .rail-state-num").first.inner_text()
    assert num.startswith("(") and num.endswith(")")
