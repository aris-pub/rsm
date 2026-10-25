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
    # The proof-rail is a fixed sidebar only above the 1320px responsive drawer
    # breakpoint; below it the rail becomes a bottom drawer whose controls are
    # hidden in the default peek state (clicks then time out). These tests
    # exercise the desktop sidebar, so ensure a desktop-width viewport. Tests
    # that need a specific size set it before calling _load (width stays >=1321).
    if page.viewport_size["width"] < 1321:
        page.set_viewport_size({"width": 1400, "height": 900})
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


def test_proof_selection_follows_clicks_not_scroll(page: Page, interactive_server: str):
    # The Proof scope follows the selected (clicked / focused) proof, not the
    # scroll. Short (wide) viewport so the proof starts below the fold.
    page.set_viewport_size({"width": 1400, "height": 460})
    _load(page, interactive_server)
    page.evaluate("() => window.scrollTo(0, 0)")
    page.wait_for_function(
        "() => document.querySelector('.proof-rail').classList.contains('no-proof')",
        timeout=5_000,
    )
    # Scrolling the proof into view must NOT select it (no scroll-spy any more).
    page.evaluate(
        "() => document.querySelector('.proof[data-nodeid]').scrollIntoView({block: 'center'})"
    )
    page.wait_for_timeout(400)
    assert page.evaluate(
        "() => document.querySelector('.proof-rail').classList.contains('no-proof')"
    ), "scrolling a proof into view should not select it"
    # Clicking it selects it: its rail item becomes the shown one.
    page.evaluate("() => document.querySelector('.proof[data-nodeid]').click()")
    page.wait_for_function(
        "() => { const r = document.querySelector('.proof-rail');"
        " return !r.classList.contains('no-proof')"
        " && !!r.querySelector('.rail-proof .proof-rail-item.shown'); }",
        timeout=5_000,
    )
    # And the selection persists when scrolling away.
    page.evaluate("() => window.scrollTo(0, 0)")
    page.wait_for_timeout(300)
    assert not page.evaluate(
        "() => document.querySelector('.proof-rail').classList.contains('no-proof')"
    ), "selection should persist when scrolling away"


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
    page.set_viewport_size({"width": 1400, "height": 460})
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
    page.set_viewport_size({"width": 1400, "height": 460})
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
    page.set_viewport_size({"width": 1400, "height": 460})
    _load(page, interactive_server)
    # Go live: Proof scope, State sub-tab.
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    # Scroll a late step into the reading band so its accumulated hypotheses
    # (which include the :assume: that references thm-x) render in the panel.
    page.evaluate(
        """() => {
            const steps = [...document.querySelectorAll('.proof[data-nodeid] .step')]
                .filter((s) => !s.closest('.calc'));
            const el = steps[steps.length - 1];
            el.scrollIntoView({ block: 'center' });
            el.click();
        }"""
    )
    link = page.wait_for_selector(".rail-state a.reference", timeout=5_000)
    # The same hover-triggered tooltipster tooltip as in the body must appear.
    link.hover()
    tip = page.wait_for_selector(".tooltipster-base", state="visible", timeout=3_000)
    assert tip.is_visible()


def test_body_reference_tooltip_renders_math(page: Page, interactive_server: str):
    """A body reference tooltip must render its target's math, not show raw
    \\(...\\)/$$...$$: the tooltip content is a clone, so it is typeset on open
    (functionReady) like the sidebar and body do."""
    page.set_viewport_size({"width": 1400, "height": 720})
    _load(page, interactive_server)
    # A body reference whose target (thm-x, "A claim about λ") carries math.
    ref = page.wait_for_selector(
        '.manuscript a.reference[href="#thm-x"]', timeout=5_000
    )
    ref.scroll_into_view_if_needed()
    ref.hover()
    tip = page.wait_for_selector(".tooltipster-base", state="visible", timeout=3_000)
    assert "\\(" not in tip.inner_text()
    assert page.locator(".tooltipster-base math").count() > 0


def test_proof_state_shows_document_context(page: Page, interactive_server: str):
    """The Proof > State panel shows a "Context" group carrying the symbols and
    assumptions introduced in prose before the proof (here, the `:write:` that
    defines the spectral radius), distinct from the proof's own hypotheses."""
    page.set_viewport_size({"width": 1400, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    # Scroll the proof into the reading band so the State panel renders live.
    page.evaluate(
        """() => {
            const el = document.querySelector('.proof[data-nodeid]');
            el.scrollIntoView({ block: 'center' });
            el.click();
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
    page.set_viewport_size({"width": 1400, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    page.evaluate(
        """() => {
            const steps = [...document.querySelectorAll('.proof[data-nodeid] .step')]
                .filter((s) => !s.closest('.calc'));
            const el = steps[steps.length - 1];
            el.scrollIntoView({ block: 'center' });
            el.click();
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
    page.set_viewport_size({"width": 1400, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    page.evaluate(
        """() => {
            const el = document.querySelector('.proof[data-nodeid]');
            el.scrollIntoView({ block: 'center' });
            el.click();
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


def _select_proof(page: Page) -> None:
    # Selection is click/focus-driven now, not scroll: clicking the proof (as the
    # reader would) shows it in the rail and lights up the Proof scope.
    page.evaluate(
        """() => {
            const el = document.querySelector('.proof[data-nodeid]');
            el.scrollIntoView({ block: 'center' });
            el.click();
        }"""
    )


def test_proof_state_rows_are_uniform_jump_rows(page: Page, interactive_server: str):
    """No ⟨n⟩ step chips and no reserved chip gutter: every row in every band is
    a uniform jump-to-source row, including the In-scope (document-context)
    rows, which previously had no jump action at all."""
    page.set_viewport_size({"width": 1400, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    _select_proof(page)
    page.wait_for_selector(".rail-state .rail-context", timeout=5_000)
    assert page.locator(".rail-state .rail-step-badge").count() == 0
    assert page.locator(".rail-state .rail-hyps .rail-jump-row").count() > 0
    assert page.locator(".rail-state .rail-context .rail-jump-row").count() > 0
    # The provenance number is back, in the left gutter: a ⟨n⟩ step number in
    # ASSUME, a §n section number in IN SCOPE.
    hyp_nums = page.locator(".rail-state .rail-hyps .rail-state-num")
    hyp_texts = [hyp_nums.nth(i).inner_text().strip() for i in range(hyp_nums.count())]
    assert any(t.startswith("⟨") and t.endswith("⟩") for t in hyp_texts)
    ctx_num = page.locator(".rail-state .rail-context .rail-state-num").first.inner_text()
    assert ctx_num.strip().startswith("§")


def test_proof_state_context_row_jumps_to_source(page: Page, interactive_server: str):
    """Clicking an In-scope row scrolls the body to where that item was
    introduced in prose: here the :write: defining the spectral radius, up in
    the Introduction well above the proof."""
    page.set_viewport_size({"width": 1400, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    _select_proof(page)
    row = page.wait_for_selector(
        ".rail-state .rail-context li:has-text('spectral radius')", timeout=5_000
    )
    # The intro write starts off-screen (above the proof in view)...
    assert page.evaluate(_WRITE_CENTERED) is False
    # ...and clicking the row scrolls it to the reading band.
    row.click()
    page.wait_for_function(_WRITE_CENTERED, timeout=5_000)


def test_proof_dag_pins_current_step_path(page: Page, interactive_server: str):
    """The proof DAG (Steps view) rests highlighting the current step's
    prerequisite cone: the current node is marked, and off-path nodes fade, so
    the whole tree is not lit at once."""
    page.set_viewport_size({"width": 1400, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')  # Steps (map) is the default proof view
    # Make the proof's first step current: its cone is small, so later steps fade.
    page.evaluate(
        """() => {
            const step = [...document.querySelectorAll('.proof[data-nodeid] .step')]
                .find((s) => !s.closest('.calc'));
            step.scrollIntoView({ block: 'center' });
            step.click();
        }"""
    )
    cur = page.wait_for_selector(
        ".rail-map svg.toc-tree .toc-node.current-step", timeout=5_000
    )
    assert "toc-faded" not in (cur.get_attribute("class") or "")
    # at least one node is off the current path and faded (path pinned, not all lit)
    page.wait_for_function(
        "() => document.querySelectorAll('.rail-map svg.toc-tree .toc-node.toc-faded')"
        ".length > 0",
        timeout=5_000,
    )


def test_proof_state_setup_goal_is_a_gutter_row(page: Page, interactive_server: str):
    """When the current step is a setup step (no own claim), PROVE shows a
    clamped preview of the theorem statement (so the collapsed state still
    carries information), as a gutter row: the .rail-jump-row treatment (rule +
    hover), a (section) marker, and a "show more" toggle."""
    page.set_viewport_size({"width": 1400, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    # Center the proof's first step, an :assume: working toward the theorem.
    page.evaluate(
        """() => {
            const step = [...document.querySelectorAll('.proof[data-nodeid] .step')]
                .find((s) => !s.closest('.calc'));
            step.scrollIntoView({ block: 'center' });
            step.click();
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
    assert num.strip().startswith("§")


def test_proof_state_goal_section_marker_reads_as_section(
    page: Page, interactive_server: str
):
    """rsm-8u3: the PROVE row for a goal introduced in a section shows a small,
    muted section marker (here "§2"), not "(2)". Next to the ⟨n⟩ step glyphs,
    "(2)" read as a stray step number; "§" marks it as a section instead. Step
    rows keep their glyph."""
    page.set_viewport_size({"width": 1400, "height": 460})
    _load(page, interactive_server)
    page.click('.rail-scope[data-scope="proof"]')
    page.click('.rail-subtabs-proof .rail-tab[data-view="state"]')
    # The proof's first step is a setup :assume: with no own claim, so PROVE
    # renders the goal summary whose gutter marker is the goal's section
    # provenance (the theorem lives in section 2, "Results").
    page.evaluate(
        """() => {
            const step = [...document.querySelectorAll('.proof[data-nodeid] .step')]
                .find((s) => !s.closest('.calc'));
            step.scrollIntoView({ block: 'center' });
            step.click();
        }"""
    )
    goal_num = page.wait_for_selector(
        ".rail-state .rail-goal .rail-goal-summary .rail-state-num", timeout=5_000
    )
    text = goal_num.inner_text().strip()
    assert text.startswith("§"), f"section marker should lead with the section sign: {text!r}"
    assert "(" not in text and ")" not in text, f"no step-like brackets: {text!r}"
    # Tagged as a section marker so CSS renders it small and muted.
    assert "rail-state-num-section" in (goal_num.get_attribute("class") or "")
    # Step rows (ASSUME) keep the ⟨n⟩ glyph, visibly unlike the goal marker.
    hyp_num = (
        page.locator(".rail-state .rail-hyps .rail-state-num").first.inner_text().strip()
    )
    assert hyp_num.startswith("⟨") and hyp_num.endswith("⟩"), hyp_num
    # "Tiny": the section marker renders smaller than the step glyph. Both are
    # 0.78em of the same .rail-state base, so they match until the section rule
    # shrinks the marker.
    sizes = page.evaluate(
        """() => {
            const g = document.querySelector(
                '.rail-state .rail-goal .rail-goal-summary .rail-state-num');
            const h = document.querySelector('.rail-state .rail-hyps .rail-state-num');
            const px = (el) => parseFloat(getComputedStyle(el).fontSize);
            return { goal: px(g), hyp: px(h) };
        }"""
    )
    assert sizes["goal"] < sizes["hyp"], f"section marker must be smaller: {sizes}"


# ---- bottom-drawer clearance (rsm-3gp) ----
# Below 1320px the proof-rail rests as a fixed bottom bar (peek state). The page
# must reserve space for it so the end of the document is not stuck under the bar,
# and jumps to a near-bottom target must land above it.

_DRAWER_SIZES = [{"width": 375, "height": 844}, {"width": 1200, "height": 800}]


def _load_drawer(page: Page, server: str, size: dict) -> None:
    page.set_viewport_size(size)
    page.goto(f"{server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)
    # Clear any layout a sibling test persisted so the drawer starts at its
    # default resting (peek) state.
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", timeout=10_000)
    page.wait_for_function(
        "() => document.querySelector('.proof-rail').getAttribute('data-drawer') === 'peek'",
        timeout=5_000,
    )


_LAST_PARAGRAPH = (
    "[...document.querySelectorAll('.manuscriptwrapper p')]"
    ".filter(e => !e.closest('.proof-rail')).pop()"
)


@pytest.mark.parametrize("size", _DRAWER_SIZES, ids=["375", "1200"])
def test_drawer_rest_bar_clears_document_end(page: Page, interactive_server: str, size):
    """Scrolled to the very bottom, the last line of the document must end at
    least 8px above the resting drawer bar (the page reserves bottom padding)."""
    _load_drawer(page, interactive_server, size)
    page.evaluate("() => window.scrollTo(0, document.documentElement.scrollHeight)")
    page.wait_for_timeout(200)
    geom = page.evaluate(
        "() => {"
        " const bar = document.querySelector('.proof-rail.active').getBoundingClientRect();"
        f" const last = ({_LAST_PARAGRAPH}).getBoundingClientRect();"
        " const d = document.documentElement;"
        " return {barTop: bar.top, barHeight: bar.height, lastBottom: last.bottom,"
        " overflowX: d.scrollWidth - d.clientWidth}; }"
    )
    assert geom["lastBottom"] <= geom["barTop"] - 8, (
        f"last line must clear the resting drawer bar by >=8px: {geom}"
    )
    assert geom["overflowX"] <= 1, f"page must not scroll horizontally: {geom}"


@pytest.mark.parametrize("size", _DRAWER_SIZES, ids=["375", "1200"])
def test_drawer_jump_to_bottom_target_clears_bar(
    page: Page, interactive_server: str, size
):
    """Bringing a near-bottom target into view (scroll-padding-bottom) must land
    it above the resting bar, not under it."""
    _load_drawer(page, interactive_server, size)
    page.evaluate(f"() => ({_LAST_PARAGRAPH}).scrollIntoView({{block: 'end'}})")
    page.wait_for_timeout(200)
    geom = page.evaluate(
        "() => {"
        " const bar = document.querySelector('.proof-rail.active').getBoundingClientRect();"
        f" const last = ({_LAST_PARAGRAPH}).getBoundingClientRect();"
        " return {barTop: bar.top, lastBottom: last.bottom}; }"
    )
    assert geom["lastBottom"] <= geom["barTop"] - 8, (
        f"jumped-to target must clear the resting drawer bar by >=8px: {geom}"
    )
