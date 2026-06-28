"""Interactive tests for logic-preserving step reordering (potf-bzv).

A proof opts into reorder mode from its handrail menu; while active, the reader
drags a step among its siblings and the proof body reflows, but only into orders
that respect the step dependency graph. The fixture proof is shaped like the
Nikiforov bound: a setup step both later steps rest on, two independent steps,
and a conclusion that uses both, so exactly the middle pair is interchangeable.
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _load(page: Page, server: str) -> None:
    if page.viewport_size["width"] < 1321:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/reorder.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _open_proof_menu(page: Page):
    proof = page.locator(".proof.hr").first
    proof.hover()
    proof.locator(".hr-border-dots").first.click()
    return proof


class TestReorderMenu:
    def test_proof_menu_has_reorder_item(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _open_proof_menu(page)
        expect(page.locator('#hr-menu-singleton [data-role="reorder"]')).to_be_visible()

    def test_reorder_item_toggles_mode(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        proof = _open_proof_menu(page)
        page.locator('#hr-menu-singleton [data-role="reorder"]').click()
        expect(proof).to_have_class(re.compile(r"\breorder-active\b"))


class TestReorderModel:
    """The fixture's declared dependencies must pin the endpoints and free only
    the middle pair, so the core's legality matches the proof's logic."""

    def test_fixture_pins_endpoints_swaps_middle(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        lp = page.evaluate(
            """async () => {
              const R = await import('/static/reorder.js');
              const it = document.querySelector('.proof-rail-item');
              const m = R.extractModel(it);
              const out = {};
              for (const id of m.byId.keys())
                out[m.byId.get(id).bodyEl.id] = R.legalPositions(m, id);
              return out;
            }"""
        )
        assert lp["stp-setup"] == [0], lp
        assert lp["stp-a"] == [1, 2], lp
        assert lp["stp-b"] == [1, 2], lp
        assert lp["stp-c"] == [3], lp

    def test_scope_pins_introducer_without_explicit_ref(
        self, page: Page, interactive_server: str
    ):
        # A :let: step introduces a hypothesis in scope for its later siblings,
        # so it is a prerequisite even though the later step never :ref:s it.
        _load(page, interactive_server)
        lp = page.evaluate(
            """async () => {
              const R = await import('/static/reorder.js');
              for (const it of document.querySelectorAll('.proof-rail-item')) {
                const m = R.extractModel(it);
                if (!m || ![...m.byId.values()].some((s) => s.bodyEl.id === 'stp-let'))
                  continue;
                const out = {};
                for (const id of m.byId.keys())
                  out[m.byId.get(id).bodyEl.id] = R.legalPositions(m, id);
                return out;
              }
              return null;
            }"""
        )
        assert lp["stp-let"] == [0], lp
        assert lp["stp-uses-y"] == [1], lp


class TestReorderDrag:
    """Dragging a step's handle reorders the body, but only into legal orders."""

    def _enter_reorder(self, page: Page):
        proof = page.locator(".proof.hr").first
        proof.scroll_into_view_if_needed()
        proof.hover()
        proof.locator(".hr-border-dots").first.click()
        page.locator('#hr-menu-singleton [data-role="reorder"]').click()
        expect(proof).to_have_class(re.compile(r"\breorder-active\b"))
        return proof

    def _order(self, page: Page):
        return page.evaluate(
            """() => [...document.querySelector('.proof.hr').querySelectorAll('.step')]
                     .filter(s => !s.closest('.calc')).map(s => s.id)"""
        )

    def _drag(self, page: Page, handle_sel: str, tx: float, ty: float):
        box = page.locator(handle_sel).first.bounding_box()
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.mouse.down()
        page.mouse.move(tx, ty, steps=10)
        page.mouse.up()

    def test_legal_swap_reorders_body(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        self._enter_reorder(page)
        assert self._order(page) == ["stp-setup", "stp-a", "stp-b", "stp-c"]
        a = page.locator("#stp-a").bounding_box()
        # drag stp-b up to just inside stp-a's top -> lands before stp-a (legal)
        self._drag(page, "#stp-b .reorder-handle", a["x"] + 40, a["y"] + 5)
        assert self._order(page) == ["stp-setup", "stp-b", "stp-a", "stp-c"]

    def test_illegal_move_is_blocked(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        self._enter_reorder(page)
        c = page.locator("#stp-c").bounding_box()
        # stp-setup is pinned first (a and b depend on it); dragging it down must
        # not move it.
        self._drag(page, "#stp-setup .reorder-handle", c["x"] + 40, c["y"])
        assert self._order(page) == ["stp-setup", "stp-a", "stp-b", "stp-c"]

    def test_state_index_stays_bound_to_step_after_reorder(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        self._enter_reorder(page)

        def idxmap():
            return page.evaluate(
                """() => Object.fromEntries(
                     [...document.querySelector('.proof.hr').querySelectorAll('.step')]
                       .map((s) => [s.id, s.dataset.stateIdx]))"""
            )

        assert idxmap() == {
            "stp-setup": "0",
            "stp-a": "1",
            "stp-b": "2",
            "stp-c": "3",
        }
        a = page.locator("#stp-a").bounding_box()
        self._drag(page, "#stp-b .reorder-handle", a["x"] + 40, a["y"] + 5)
        # b moved to position 1, but its State index stays 2 (bound to the step,
        # not its place), so the panel still shows b's own state.
        m = idxmap()
        assert m["stp-b"] == "2" and m["stp-a"] == "1", m

    def test_escape_cancels_reorder_mode(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        proof = self._enter_reorder(page)
        expect(proof.locator(".reorder-handle").first).to_be_visible()
        page.keyboard.press("Escape")
        expect(proof).not_to_have_class(re.compile(r"\breorder-active\b"))
        assert proof.locator(".reorder-handle").count() == 0


class TestReorderAccessibility:
    """Screen readers must perceive reorder mode and the result of a reorder
    even though the gesture itself is pointer/touch driven."""

    def _enter_reorder(self, page: Page):
        proof = page.locator(".proof.hr").first
        proof.scroll_into_view_if_needed()
        proof.hover()
        proof.locator(".hr-border-dots").first.click()
        page.locator('#hr-menu-singleton [data-role="reorder"]').click()
        expect(proof).to_have_class(re.compile(r"\breorder-active\b"))
        return proof

    def test_menu_item_reflects_state_with_aria_pressed(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        proof = page.locator(".proof.hr").first
        proof.hover()
        proof.locator(".hr-border-dots").first.click()
        item = page.locator('#hr-menu-singleton [data-role="reorder"]')
        expect(item).to_have_attribute("aria-pressed", "false")
        item.click()
        # Reopen the menu; the proof is now in reorder mode, so the toggle reads on.
        proof.hover()
        proof.locator(".hr-border-dots").first.click()
        expect(
            page.locator('#hr-menu-singleton [data-role="reorder"]')
        ).to_have_attribute("aria-pressed", "true")

    def test_handles_named_per_step(self, page: Page, interactive_server: str):
        # Each gutter handle carries its step's label so a screen reader can tell
        # them apart instead of hearing the same name on every one.
        _load(page, interactive_server)
        self._enter_reorder(page)
        labels = page.locator(".proof.hr .reorder-handle").evaluate_all(
            "els => els.map((e) => e.getAttribute('aria-label'))"
        )
        assert len(set(labels)) == len(labels) and len(labels) == 4, labels
        assert all(l.startswith("Reorder Step") for l in labels), labels

    def test_live_region_announces_mode_and_reorder(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        self._enter_reorder(page)
        status = page.locator(".reorder-sr-status")
        expect(status).to_have_attribute("aria-live", "polite")
        expect(status).to_contain_text("Reorder mode on", timeout=2000)
        # A legal drag (stp-b before stp-a) is announced to the same region.
        a = page.locator("#stp-a").bounding_box()
        box = page.locator("#stp-b .reorder-handle").first.bounding_box()
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.mouse.down()
        page.mouse.move(a["x"] + 40, a["y"] + 5, steps=10)
        page.mouse.up()
        expect(status).to_contain_text("moved to position", timeout=2000)


class TestReorderTouch:
    """Reorder needs a pointer and the wide dependency rail, so on coarse-pointer
    touch devices the menu item is shown disabled and labeled, not offered."""

    # Playwright cannot emulate the pointer/hover media features, so stub
    # matchMedia to report a coarse pointer for that one query (leaving others,
    # e.g. prefers-reduced-motion, intact). showMenuFor reads it when the menu
    # opens, so installing the stub before the click exercises the real path.
    _STUB = """() => {
      const orig = window.matchMedia.bind(window);
      window.matchMedia = (q) => /pointer:\\s*coarse/.test(q)
        ? { matches: true, media: q, onchange: null,
            addListener() {}, removeListener() {},
            addEventListener() {}, removeEventListener() {},
            dispatchEvent() { return false; } }
        : orig(q);
    }"""

    def test_touch_disables_and_relabels_reorder(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        page.evaluate(self._STUB)
        proof = page.locator(".proof.hr").first
        proof.hover()
        proof.locator(".hr-border-dots").first.click()
        item = page.locator('#hr-menu-singleton [data-role="reorder"]')
        expect(item).to_be_visible()
        expect(item).to_have_class(re.compile(r"\bdisabled\b"))
        expect(item).to_have_attribute("aria-disabled", "true")
        expect(item).to_contain_text("desktop only")
        # force=True: a real user can tap a greyed item, so bypass Playwright's
        # actionability gate to prove the click handler still refuses it.
        item.click(force=True)
        expect(proof).not_to_have_class(re.compile(r"\breorder-active\b"))


class TestRejectionReason:
    """An illegal move names the dependency it would break, in the handrail
    gutter (and to screen readers on drop). potf-13p."""

    def _enter_reorder(self, page: Page):
        proof = page.locator(".proof.hr").first
        proof.scroll_into_view_if_needed()
        proof.hover()
        proof.locator(".hr-border-dots").first.click()
        page.locator('#hr-menu-singleton [data-role="reorder"]').click()

    def _press_handle(self, page: Page, handle_sel: str):
        box = page.locator(handle_sel).first.bounding_box()
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.mouse.down()

    def test_illegal_drag_names_blocking_dep(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        self._enter_reorder(page)
        # Drag stp-c (Step 4) up between stp-setup and stp-a: illegal, since
        # stp-c uses stp-a (Step 2). The reason rides the indicator.
        self._press_handle(page, "#stp-c .reorder-handle")
        a = page.locator("#stp-a").bounding_box()
        page.mouse.move(a["x"] + 40, a["y"] - 5, steps=12)
        reason = page.locator(".reorder-reason")
        expect(reason).to_be_visible()
        expect(reason).to_contain_text("Step 4 uses Step 2")
        page.mouse.up()

    def test_legal_drag_shows_no_reason(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        self._enter_reorder(page)
        # stp-b (Step 3) and stp-a (Step 2) are interchangeable: a legal slot
        # carries no reason.
        self._press_handle(page, "#stp-b .reorder-handle")
        a = page.locator("#stp-a").bounding_box()
        page.mouse.move(a["x"] + 40, a["y"] + 5, steps=12)
        expect(page.locator(".reorder-reason")).to_be_hidden()
        page.mouse.up()

    def test_illegal_drop_announces_reason(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        self._enter_reorder(page)
        self._press_handle(page, "#stp-c .reorder-handle")
        a = page.locator("#stp-a").bounding_box()
        page.mouse.move(a["x"] + 40, a["y"] - 5, steps=12)
        page.mouse.up()
        status = page.locator(".reorder-sr-status")
        expect(status).to_contain_text("Move blocked: Step 4 uses Step 2", timeout=2000)
