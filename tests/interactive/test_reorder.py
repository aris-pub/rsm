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
            """() => [...document.querySelectorAll('.proof.hr .step')]
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
                     [...document.querySelectorAll('.proof.hr .step')]
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
