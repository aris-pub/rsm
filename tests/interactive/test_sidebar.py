"""Interactive tests for the reader sidebar (`rsm build --sidebar`).

An icon strip opens one view at a time (Contents, Notation, Proof steps, Proof
state, Pinned, Reading) in a panel that pushes the column instead of covering
it; on phones the strip is a bottom bar with one button per scope and the views
open as a sheet. The open view persists in localStorage.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _load(page: Page, server: str) -> None:
    # Desktop width: the strip is in the left margin and each view has its own
    # icon. Tests that need a specific size set it before calling _load.
    if page.viewport_size["width"] < 768:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", state="attached", timeout=10_000)


def _rail_class(page: Page) -> str:
    return page.locator(".proof-rail").get_attribute("class")


def _is_open(page: Page) -> bool:
    return page.evaluate("() => document.documentElement.classList.contains('rail-open')")


def _show(page: Page, view: str) -> None:
    """Open a view from the strip (a no-op if it is already the open view)."""
    btn = page.locator(f'.rail-strip-btn[data-view="{view}"]')
    if btn.get_attribute("aria-pressed") != "true":
        btn.click()
    page.wait_for_selector(".proof-rail.open", timeout=5_000)


def test_panel_starts_closed(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    assert not _is_open(page)
    assert not page.locator(".proof-rail").is_visible()
    assert page.locator(".rail-strip").is_visible()


def test_strip_opens_switches_and_closes(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _show(page, "contents")
    assert _is_open(page)
    assert "scope-document" in _rail_class(page)
    assert "doc-view-map" in _rail_class(page)
    assert page.locator('.rail-strip-btn[data-view="contents"]').get_attribute("aria-pressed") == "true"
    page.click('.rail-strip-btn[data-view="steps"]')
    assert "scope-proof" in _rail_class(page)
    assert "proof-view-map" in _rail_class(page)
    assert page.locator('.rail-strip-btn[data-view="contents"]').get_attribute("aria-pressed") == "false"
    # The open view's own icon closes the panel.
    page.click('.rail-strip-btn[data-view="steps"]')
    assert not _is_open(page)
    assert not page.locator(".proof-rail").is_visible()


def test_escape_closes_panel(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _show(page, "reading")
    page.keyboard.press("Escape")
    assert not _is_open(page)


def test_phone_rail_show_for_absent_view_does_not_flip_subview(
    page: Page, interactive_server: str
):
    # The figure fixture has no proof, so no proof panel is built. On a phone a
    # rail:show for a proof sub-view (state) must not open a sheet or flip the
    # proof subview class toward the missing panel.
    page.set_viewport_size({"width": 375, "height": 720})
    page.goto(f"{interactive_server}/sidebar_figure.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", state="attached", timeout=10_000)
    assert "no-proofs" in _rail_class(page)
    assert "proof-view-map" in _rail_class(page)
    page.evaluate(
        "() => document.dispatchEvent(new CustomEvent('rail:show',"
        " { detail: { view: 'state', open: true } }))"
    )
    assert not _is_open(page)
    assert "proof-view-state" not in _rail_class(page)
    assert "proof-view-map" in _rail_class(page)


def test_panel_head_names_the_view(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _show(page, "contents")
    assert page.locator(".rail-title").inner_text() == "Contents"
    assert "dependency graph" in page.locator(".rail-hint").inner_text()
    _show(page, "notation")
    assert page.locator(".rail-title").inner_text() == "Notation"
    assert "Rename one" in page.locator(".rail-hint").inner_text()
    # Every view says what it shows.
    for view in ("steps", "state", "pinned", "reading"):
        _show(page, view)
        assert page.locator(".rail-hint").is_visible(), view
        assert page.locator(".rail-hint").inner_text().strip(), view


def test_document_notation_view(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _show(page, "notation")
    assert "scope-document" in _rail_class(page)
    assert "doc-view-notation" in _rail_class(page)
    assert "doc-view-map" not in _rail_class(page)


def test_proof_state_view(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _show(page, "state")
    assert "proof-view-state" in _rail_class(page)
    assert "proof-view-map" not in _rail_class(page)


def test_panel_starts_closed_but_remembers_the_view(page: Page, interactive_server: str):
    """The panel always starts closed; the reader's last view is remembered for
    the next time they open it."""
    _load(page, interactive_server)
    _show(page, "state")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    assert not _is_open(page), "the panel must start closed"
    assert "proof-view-state" in _rail_class(page), "the last view should persist"


@pytest.mark.xfail(
    reason="rsm-bou: with real web fonts the narrowed column reflows taller and "
    "lower blocks drift ~24px while only the topmost block is held",
    strict=False,
)
def test_panel_never_covers_the_text(page: Page, interactive_server: str):
    """Opening a view moves the column right of the panel instead of under it,
    and the block at the top of the window keeps its place."""
    page.set_viewport_size({"width": 1280, "height": 800})
    _load(page, interactive_server)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.evaluate("() => document.querySelector('#sec-results').scrollIntoView()")
    page.wait_for_timeout(200)
    top_before = page.evaluate(
        "() => document.querySelector('#sec-results').getBoundingClientRect().top"
    )
    _show(page, "contents")
    page.wait_for_timeout(600)  # the column's transition
    geom = page.evaluate(
        """() => {
            const panel = document.querySelector('.proof-rail').getBoundingClientRect();
            const text = document.querySelector('.manuscript p').getBoundingClientRect();
            const d = document.documentElement;
            return { panelRight: panel.right, textLeft: text.left,
                     overflowX: d.scrollWidth - d.clientWidth,
                     top: document.querySelector('#sec-results').getBoundingClientRect().top };
        }"""
    )
    assert geom["textLeft"] >= geom["panelRight"], geom
    assert geom["overflowX"] <= 1, geom
    assert abs(geom["top"] - top_before) <= 2, (top_before, geom)


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
    _show(page, "notation")
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
    # The explicit Rename button effectuates the change (no Enter needed).
    assert page.locator(".rail-notation-apply").first.inner_text() == "Rename"
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
    _show(page, "state")
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
    _show(page, "state")
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
    _show(page, "state")
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
    _show(page, "state")
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
    _show(page, "state")
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
    _show(page, "state")
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
    _show(page, "steps")
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
    _show(page, "state")
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
    _show(page, "state")
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


def test_symbol_opens_notation(page: Page, interactive_server: str):
    """A symbol declared in :notation: is marked in the math; clicking it opens
    Notation with that symbol's field selected."""
    _load(page, interactive_server)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    sym = page.locator(".manuscript .paragraph .nt-eig").first
    sym.click()
    page.wait_for_function(
        "() => document.activeElement && document.activeElement.classList.contains('rail-notation-input')",
        timeout=5_000,
    )
    assert _is_open(page)
    assert "doc-view-notation" in _rail_class(page)
    # The field is selected, ready to type the new symbol.
    assert page.evaluate(
        "() => { const i = document.activeElement; return i.selectionStart === 0 && i.selectionEnd === i.value.length; }"
    )


def test_symbols_are_marked(page: Page, interactive_server: str):
    """Every use of a declared symbol carries its mark (nt-<name>), in the
    body's inline and display math alike."""
    _load(page, interactive_server)
    uses = page.evaluate(
        "() => [...document.querySelectorAll('.manuscript span.math[data-latex]')]"
        ".filter(e => /\\\\eig(?![a-zA-Z])/.test(e.dataset.latex)).length"
    )
    marked = page.evaluate(
        "() => [...document.querySelectorAll('.manuscript span.math[data-latex]')]"
        ".filter(e => e.querySelector('.nt-eig')).length"
    )
    assert uses > 0 and marked == uses, (uses, marked)


def test_reading_theme_offers_system(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    _show(page, "reading")
    row = page.locator('.reading-row[data-control="theme"]')
    values = [row.locator(".reading-opt").nth(i).get_attribute("data-value") for i in range(3)]
    assert values == ["system", "light", "dark"]
    # With no stored choice, System is the active one.
    assert row.locator('.reading-opt[data-value="system"]').get_attribute("aria-pressed") == "true"
    row.locator('.reading-opt[data-value="dark"]').click()
    assert page.evaluate("() => document.documentElement.classList.contains('dark-theme')")
    row.locator('.reading-opt[data-value="system"]').click()
    assert page.evaluate(
        "() => !document.documentElement.classList.contains('dark-theme')"
        " && !document.documentElement.classList.contains('light-theme')"
    )


# ---- phones: the bottom bar ----
# Below 768px the strip is a bottom bar. The page must reserve space for it so
# the end of the document is not stuck under the bar, and jumps to a near-bottom
# target must land above it.

_PHONE = {"width": 375, "height": 844}


def _load_phone(page: Page, server: str) -> None:
    page.set_viewport_size(_PHONE)
    page.goto(f"{server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)


_LAST_PARAGRAPH = (
    "[...document.querySelectorAll('.manuscriptwrapper p')]"
    ".filter(e => !e.closest('.proof-rail')).pop()"
)


def test_phone_bar_has_one_button_per_scope(page: Page, interactive_server: str):
    _load_phone(page, interactive_server)
    views = page.evaluate(
        "() => [...document.querySelectorAll('.rail-strip-btn')]"
        ".filter(b => b.offsetParent).map(b => b.dataset.view || 'link')"
    )
    assert views == ["document", "proof", "pinned", "reading", "link"]
    # Labelled, and at least 48px.
    for b in page.locator(".rail-strip-btn").all():
        if not b.is_visible():
            continue
        box = b.bounding_box()
        assert box["width"] >= 48 and box["height"] >= 48, box
        assert b.locator(".rail-strip-label").is_visible()


def test_phone_sheet_switches_views_with_tabs(page: Page, interactive_server: str):
    _load_phone(page, interactive_server)
    page.click('.rail-strip-btn[data-view="document"]')
    page.wait_for_selector(".proof-rail.open", timeout=5_000)
    tabs = page.locator(".rail-subtabs-document [role=tab]")
    assert tabs.count() == 2
    assert not page.locator(".rail-title").is_visible()  # the tabs replace it
    tabs.nth(1).click()
    assert "doc-view-notation" in _rail_class(page)
    assert tabs.nth(1).get_attribute("aria-selected") == "true"
    assert "Rename one" in page.locator(".rail-hint").inner_text()
    # Arrow keys move between the tabs.
    tabs.nth(1).press("ArrowLeft")
    assert "doc-view-map" in _rail_class(page)
    # No Width setting on a phone.
    page.click('.rail-strip-btn[data-view="reading"]')
    assert not page.locator('.reading-row[data-control="measure"]').is_visible()


def test_phone_bar_clears_document_end(page: Page, interactive_server: str):
    """Scrolled to the very bottom, the last line of the document must end at
    least 8px above the bar (the page reserves bottom padding)."""
    _load_phone(page, interactive_server)
    page.evaluate("() => window.scrollTo(0, document.documentElement.scrollHeight)")
    page.wait_for_timeout(200)
    geom = page.evaluate(
        "() => {"
        " const bar = document.querySelector('.rail-strip').getBoundingClientRect();"
        f" const last = ({_LAST_PARAGRAPH}).getBoundingClientRect();"
        " const d = document.documentElement;"
        " return {barTop: bar.top, lastBottom: last.bottom,"
        " overflowX: d.scrollWidth - d.clientWidth}; }"
    )
    assert geom["lastBottom"] <= geom["barTop"] - 8, geom
    assert geom["overflowX"] <= 1, geom


def test_phone_jump_to_bottom_target_clears_bar(page: Page, interactive_server: str):
    """Bringing a near-bottom target into view (scroll-padding-bottom) must land
    it above the bar, not under it."""
    _load_phone(page, interactive_server)
    page.evaluate(f"() => ({_LAST_PARAGRAPH}).scrollIntoView({{block: 'end'}})")
    page.wait_for_timeout(200)
    geom = page.evaluate(
        "() => {"
        " const bar = document.querySelector('.rail-strip').getBoundingClientRect();"
        f" const last = ({_LAST_PARAGRAPH}).getBoundingClientRect();"
        " return {barTop: bar.top, lastBottom: last.bottom}; }"
    )
    assert geom["lastBottom"] <= geom["barTop"] - 8, geom


# ---- keyboard and interface tooltips ----


def test_keyboard_opens_and_escape_returns_focus(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    btn = page.locator('.rail-strip-btn[data-view="reading"]')
    btn.focus()
    page.keyboard.press("Enter")
    assert _is_open(page)
    assert btn.get_attribute("aria-pressed") == "true"
    # Tab moves into the panel's controls.
    page.keyboard.press("Tab")
    in_panel_or_strip = page.evaluate(
        "() => !!document.activeElement.closest('.proof-rail, .rail-strip')"
    )
    assert in_panel_or_strip
    page.locator('.reading-opt[data-value="serif"]').focus()
    page.keyboard.press("Escape")
    assert not _is_open(page)
    # Focus goes back to the strip button that opened the view.
    assert page.evaluate(
        "() => document.activeElement.matches('.rail-strip-btn[data-view=\"reading\"]')"
    )


def test_interface_tooltip_on_hover_and_keyboard_focus(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    tip = page.locator("#rsm-ui-tip")
    assert tip.is_hidden()
    page.hover('.rail-strip-btn[data-view="contents"]')
    expect_tip = page.wait_for_function(
        "() => { const t = document.getElementById('rsm-ui-tip');"
        " return !t.hidden && t.textContent === 'Contents'; }",
        timeout=3_000,
    )
    assert expect_tip
    assert (
        page.locator('.rail-strip-btn[data-view="contents"]').get_attribute("aria-describedby")
        == "rsm-ui-tip"
    )
    # Beside the strip, not over it.
    g = page.evaluate(
        "() => ({tip: document.getElementById('rsm-ui-tip').getBoundingClientRect().left,"
        " strip: document.querySelector('.rail-strip').getBoundingClientRect().right})"
    )
    assert g["tip"] >= g["strip"], g
    # Keyboard focus shows it at once.
    page.mouse.move(900, 600)
    page.locator('.rail-strip-btn[data-view="contents"]').focus()
    page.keyboard.press("Tab")
    page.wait_for_function(
        "() => { const t = document.getElementById('rsm-ui-tip');"
        " return !t.hidden && t.textContent === 'Notation'; }",
        timeout=1_000,
    )
    # The open view's own button needs no label.
    page.keyboard.press("Enter")
    page.mouse.move(900, 600)
    page.hover('.rail-strip-btn[data-view="notation"]')
    page.wait_for_timeout(600)
    assert tip.is_hidden()


def test_reading_settings_apply_and_persist(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    _show(page, "reading")
    width_before = page.evaluate(
        "() => document.querySelector('main.manuscriptwrapper').getBoundingClientRect().width"
    )
    for control, value in [("typeface", "serif"), ("size", "4"), ("leading", "loose"), ("measure", "narrow")]:
        page.click(f'.reading-row[data-control="{control}"] .reading-opt[data-value="{value}"]')
        assert page.evaluate(
            f"() => document.documentElement.getAttribute('data-reading-{control}')"
        ) == value
    page.wait_for_timeout(400)
    width_after = page.evaluate(
        "() => document.querySelector('main.manuscriptwrapper').getBoundingClientRect().width"
    )
    assert width_after < width_before, (width_before, width_after)
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    assert page.evaluate("() => document.documentElement.getAttribute('data-reading-size')") == "4"
    _show(page, "reading")
    assert (
        page.locator('.reading-row[data-control="size"] .reading-opt[data-value="4"]').get_attribute("aria-pressed")
        == "true"
    )


def test_phone_sheet_carries_over_to_desktop(page: Page, interactive_server: str):
    _load_phone(page, interactive_server)
    page.click('.rail-strip-btn[data-view="document"]')
    page.click('.rail-subtabs-document .rail-tab[data-view="notation"]')
    page.set_viewport_size({"width": 1400, "height": 900})
    page.wait_for_timeout(300)
    assert _is_open(page)
    assert page.locator('.rail-strip-btn[data-view="notation"]').get_attribute("aria-pressed") == "true"
    assert page.locator(".rail-title").inner_text() == "Notation"


def test_phone_symbol_opens_notation_tab(page: Page, interactive_server: str):
    _load_phone(page, interactive_server)
    page.locator(".manuscript .paragraph .nt-eig").first.click()
    page.wait_for_function(
        "() => document.activeElement && document.activeElement.classList.contains('rail-notation-input')",
        timeout=5_000,
    )
    assert page.locator('.rail-strip-btn[data-view="document"]').get_attribute("aria-pressed") == "true"
    assert (
        page.locator('.rail-subtabs-document .rail-tab[data-view="notation"]').get_attribute("aria-selected")
        == "true"
    )


def test_desktop_strip_is_icon_only(page: Page, interactive_server: str):
    """Regression (prototype): the strip's labels show only on the phone bar."""
    _load(page, interactive_server)
    assert page.locator(".rail-strip .rail-strip-label:visible").count() == 0
    for b in page.locator(".rail-strip-btn:visible").all():
        assert b.get_attribute("aria-label")
