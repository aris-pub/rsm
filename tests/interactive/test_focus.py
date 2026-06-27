"""Interactive tests for focus mode (potf-i4g).

Focusing a step folds the proof to that step and its prerequisite cone: every
off-cone step collapses (via the same handrail collapse the chevron uses), the
rail dims to the cone, and a "Show full proof" exit bar appears. The reorder
fixture's first proof has a deterministic cone: stp-setup is a prerequisite of
both stp-a and stp-b, and stp-c uses both, so focusing stp-a keeps stp-setup and
stp-a expanded and collapses stp-b and stp-c.
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _load(page: Page, server: str) -> None:
    # The rail (and so focus mode) is desktop-only; use a wide viewport.
    if page.viewport_size["width"] < 1321:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/reorder.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    # Focus mode is opt-in (potf-i4g): enable it for the tests. The triggers and
    # the menu item check this flag live, so setting it after load suffices.
    page.evaluate("() => document.documentElement.setAttribute('data-focus-mode', 'on')")


def _open_step_menu(page: Page, step_id: str):
    step = page.locator(f"#{step_id}")
    step.scroll_into_view_if_needed()
    step.hover()
    step.locator(".hr-border-dots").first.click()
    return step


def _open_proof_menu(page: Page):
    proof = page.locator(".proof.hr").first
    proof.scroll_into_view_if_needed()
    proof.hover()
    proof.locator(".hr-border-dots").first.click()
    return proof


def _focus_step(page: Page, step_id: str):
    _open_step_menu(page, step_id)
    page.locator('#hr-menu-singleton [data-role="focus"]').click()


def _collapsed(page: Page, step_id: str) -> bool:
    return page.locator(f"#{step_id}").evaluate(
        "el => el.classList.contains('hr-collapsed')"
    )


class TestFocusMenu:
    def test_step_menu_has_focus_item(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _open_step_menu(page, "stp-a")
        expect(page.locator('#hr-menu-singleton [data-role="focus"]')).to_be_visible()

    def test_proof_menu_has_no_focus_item(self, page: Page, interactive_server: str):
        # Focus is a per-step affordance; the proof handrail must not offer it.
        _load(page, interactive_server)
        _open_proof_menu(page)
        expect(page.locator('#hr-menu-singleton [data-role="focus"]')).to_be_hidden()


class TestFocusEnter:
    def test_entering_focus_marks_proof_rail_and_scope(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _focus_step(page, "stp-a")
        proof = page.locator(".proof.hr").first
        expect(proof).to_have_class(re.compile(r"\bproof-focused\b"))
        expect(page.locator(".proof-rail")).to_have_class(re.compile(r"\bfocusing\b"))
        expect(page.locator(".proof-focus-exit")).to_be_visible()
        # The rail flips to the Proof scope so the dimmed cone is visible.
        expect(
            page.locator('.proof-rail .rail-scope[data-scope="proof"]')
        ).to_have_class(re.compile(r"\bactive\b"))

    def test_noncone_steps_collapse_cone_steps_stay_open(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _focus_step(page, "stp-a")
        # stp-a depends on stp-setup; both are the cone and stay expanded.
        assert _collapsed(page, "stp-setup") is False
        assert _collapsed(page, "stp-a") is False
        # stp-b and stp-c are off the cone of stp-a, so they fold.
        assert _collapsed(page, "stp-b") is True
        assert _collapsed(page, "stp-c") is True


class TestFocusExit:
    def test_escape_exits_and_restores(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _focus_step(page, "stp-a")
        proof = page.locator(".proof.hr").first
        expect(proof).to_have_class(re.compile(r"\bproof-focused\b"))
        page.keyboard.press("Escape")
        expect(proof).not_to_have_class(re.compile(r"\bproof-focused\b"))
        expect(page.locator(".proof-focus-exit")).to_have_count(0)
        # Steps focus had folded are open again.
        assert _collapsed(page, "stp-b") is False
        assert _collapsed(page, "stp-c") is False

    def test_exit_button_exits_and_restores(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _focus_step(page, "stp-a")
        proof = page.locator(".proof.hr").first
        page.locator(".proof-focus-exit").click()
        expect(proof).not_to_have_class(re.compile(r"\bproof-focused\b"))
        expect(page.locator(".proof-rail")).not_to_have_class(
            re.compile(r"\bfocusing\b")
        )
        assert _collapsed(page, "stp-b") is False
        assert _collapsed(page, "stp-c") is False


class TestFocusAccessibility:
    def test_live_region_announces_on_enter(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _focus_step(page, "stp-a")
        status = page.locator(".focus-sr-status")
        expect(status).to_have_attribute("role", "status")
        expect(status).to_have_attribute("aria-live", "polite")
        expect(status).to_contain_text("Focused step", timeout=2000)


class TestFocusNonDestructive:
    """Entering and leaving focus must not disturb the reader's own collapses."""

    def test_manual_collapse_survives_focus_round_trip(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        # The reader collapses stp-setup themselves before focusing.
        page.evaluate(
            """async () => {
              const H = await import('/static/handrails.js');
              H.closeHandrail(document.getElementById('stp-setup'));
            }"""
        )
        assert _collapsed(page, "stp-setup") is True
        # stp-setup is in stp-a's cone, so focus opens it...
        _focus_step(page, "stp-a")
        assert _collapsed(page, "stp-setup") is False
        # ...but on exit it returns to the reader's collapsed state, not blindly open.
        page.locator(".proof-focus-exit").click()
        assert _collapsed(page, "stp-setup") is True
