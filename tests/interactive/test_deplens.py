"""Interactive tests for the dependency lens (potf-1d2).

From a proof step the reader lights its dependency cone in the prose: upstream
("What does this rest on?", the prerequisites) and/or downstream ("What rests on
this?", the dependents). The lens is sticky (it holds while the reader scrolls)
and the two directions compose. It reads the same per-proof step DAG as reorder
and focus.

The reorder.html fixture's first proof has a deterministic DAG:
  stp-setup  is a prerequisite of  stp-a  and  stp-b
  stp-c      depends on  stp-a  and  stp-b
so:
  upstream(stp-c)     = {stp-a, stp-b, stp-setup}   downstream(stp-c)   = {}
  upstream(stp-a)     = {stp-setup}                 downstream(stp-a)   = {stp-c}
  upstream(stp-setup) = {}                          downstream(stp-setup) = {stp-a, stp-b, stp-c}
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _load(page: Page, server: str) -> None:
    # The lens reads the floating rail, which is desktop-only; use a wide viewport.
    if page.viewport_size["width"] < 1321:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/reorder.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _open_step_menu(page: Page, step_id: str):
    step = page.locator(f"#{step_id}")
    step.scroll_into_view_if_needed()
    step.hover()
    step.locator(".hr-border-dots").first.click()
    return step


def _lens(page: Page, step_id: str, direction: str) -> None:
    _open_step_menu(page, step_id)
    page.locator(f'#hr-menu-singleton [data-role="deplens-{direction}"]').click()


def _classes(page: Page, step_id: str) -> str:
    return page.locator(f"#{step_id}").evaluate("el => el.className")


def _has(page: Page, step_id: str, cls: str) -> bool:
    return page.locator(f"#{step_id}").evaluate(
        f"el => el.classList.contains('{cls}')"
    )


class TestLensMenu:
    def test_step_offers_both_directions(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _open_step_menu(page, "stp-a")
        expect(page.locator('#hr-menu-singleton [data-role="deplens-up"]')).to_be_visible()
        expect(page.locator('#hr-menu-singleton [data-role="deplens-down"]')).to_be_visible()

    def test_upstream_disabled_when_nothing_upstream(
        self, page: Page, interactive_server: str
    ):
        # stp-setup depends on nothing: the item is shown but disabled, with a hint.
        _load(page, interactive_server)
        _open_step_menu(page, "stp-setup")
        up = page.locator('#hr-menu-singleton [data-role="deplens-up"]')
        expect(up).to_be_visible()
        expect(up).to_have_class(re.compile(r"\bdisabled\b"))
        expect(up).to_have_attribute("aria-disabled", "true")
        # The reason is carried via our tooltip system (data-tooltip), not a title.
        expect(up).to_have_attribute("data-tooltip", re.compile(r"depends on nothing"))
        expect(up).not_to_have_attribute("title", re.compile(r".+"))
        # downstream is real, so it stays enabled.
        down = page.locator('#hr-menu-singleton [data-role="deplens-down"]')
        expect(down).to_be_visible()
        expect(down).not_to_have_class(re.compile(r"\bdisabled\b"))

    def test_downstream_disabled_when_nothing_downstream(
        self, page: Page, interactive_server: str
    ):
        # nothing rests on stp-c (the conclusion): shown but disabled, with a hint.
        _load(page, interactive_server)
        _open_step_menu(page, "stp-c")
        expect(
            page.locator('#hr-menu-singleton [data-role="deplens-up"]')
        ).not_to_have_class(re.compile(r"\bdisabled\b"))
        down = page.locator('#hr-menu-singleton [data-role="deplens-down"]')
        expect(down).to_be_visible()
        expect(down).to_have_class(re.compile(r"\bdisabled\b"))
        expect(down).to_have_attribute("data-tooltip", re.compile(r"Nothing else"))

    def test_disabled_item_shows_our_tooltip_on_hover(
        self, page: Page, interactive_server: str
    ):
        # Hovering a disabled item shows one of OUR (tooltipster) tooltips, not a
        # native title: a .tooltipster-box appears carrying the reason.
        _load(page, interactive_server)
        _open_step_menu(page, "stp-setup")
        page.locator('#hr-menu-singleton [data-role="deplens-up"]').hover()
        tip = page.locator(".tooltipster-box .rail-tip")
        expect(tip).to_be_visible(timeout=2000)
        expect(tip).to_contain_text("depends on nothing")

    def test_proof_handrail_has_no_lens(self, page: Page, interactive_server: str):
        # The lens is a per-step affordance; the proof handrail must not offer it.
        _load(page, interactive_server)
        proof = page.locator(".proof.hr").first
        proof.scroll_into_view_if_needed()
        proof.hover()
        proof.locator(".hr-border-dots").first.click()
        expect(page.locator('#hr-menu-singleton [data-role="deplens-up"]')).to_be_hidden()
        expect(page.locator('#hr-menu-singleton [data-role="deplens-down"]')).to_be_hidden()


class TestUpstream:
    def test_upstream_lights_cone_and_fades_rest(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _lens(page, "stp-a", "up")
        # stp-a rests on stp-setup: cone is lit, stp-a is the anchor.
        assert _has(page, "stp-setup", "deplens-up")
        assert _has(page, "stp-a", "deplens-anchor")
        # stp-b and stp-c are off the upstream cone, so upstream recedes them.
        assert _has(page, "stp-b", "deplens-faded")
        assert _has(page, "stp-c", "deplens-faded")

    def test_entering_marks_rail_scope_and_bar(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _lens(page, "stp-a", "up")
        expect(page.locator(".proof-rail")).to_have_class(re.compile(r"\bdeplensing\b"))
        expect(page.locator(".deplens-bar")).to_be_visible()
        expect(
            page.locator('.proof-rail .rail-scope[data-scope="proof"]')
        ).to_have_class(re.compile(r"\bactive\b"))


class TestDownstream:
    def test_downstream_marks_dependents_without_fading_rest(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _lens(page, "stp-a", "down")
        # stp-c rests on stp-a: it is marked. stp-a is the anchor.
        assert _has(page, "stp-c", "deplens-down")
        assert _has(page, "stp-a", "deplens-anchor")
        # downstream does not dim the rest: stp-setup and stp-b stay legible.
        assert _has(page, "stp-setup", "deplens-faded") is False
        assert _has(page, "stp-b", "deplens-faded") is False


class TestCompose:
    def test_both_cones_light_at_once(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _lens(page, "stp-a", "up")
        # The bar offers the other direction; clicking it composes the two.
        page.locator(".deplens-bar .deplens-add").click()
        assert _has(page, "stp-setup", "deplens-up")  # what stp-a rests on
        assert _has(page, "stp-c", "deplens-down")  # what rests on stp-a
        assert _has(page, "stp-a", "deplens-anchor")
        # stp-b is in neither cone; with a direction composed it recedes.
        assert _has(page, "stp-b", "deplens-faded")


class TestActiveAffordance:
    def test_pill_names_lens_and_shows_esc_hint(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _lens(page, "stp-a", "up")
        bar = page.locator(".deplens-bar")
        expect(bar).to_be_visible()
        expect(bar.locator(".deplens-bar-badge")).to_contain_text("Dependency lens")
        # The reader is told Escape clears it.
        expect(bar.locator(".deplens-kbd")).to_contain_text("Esc")
        # The pill is anchored to the viewport so it survives scrolling.
        assert bar.evaluate("el => getComputedStyle(el).position") == "fixed"


class TestExit:
    def test_escape_clears(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _lens(page, "stp-a", "up")
        expect(page.locator(".deplens-bar")).to_be_visible()
        page.keyboard.press("Escape")
        expect(page.locator(".deplens-bar")).to_have_count(0)
        assert _has(page, "stp-setup", "deplens-up") is False
        assert _has(page, "stp-b", "deplens-faded") is False

    def test_clear_button_clears(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _lens(page, "stp-a", "up")
        page.locator(".deplens-bar .deplens-exit").click()
        expect(page.locator(".deplens-bar")).to_have_count(0)
        assert _has(page, "stp-setup", "deplens-up") is False

    def test_retrigger_same_direction_toggles_off(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _lens(page, "stp-a", "up")
        expect(page.locator(".deplens-bar")).to_be_visible()
        _lens(page, "stp-a", "up")
        expect(page.locator(".deplens-bar")).to_have_count(0)


class TestAccessibility:
    def test_live_region_announces(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _lens(page, "stp-c", "up")
        status = page.locator(".deplens-sr-status")
        expect(status).to_have_attribute("role", "status")
        expect(status).to_have_attribute("aria-live", "polite")
        expect(status).to_contain_text("rests on", timeout=2000)


# --- result-level lens (the deplens.html fixture) -------------------------
#
# Result dependency graph (derived from each proof's citations):
#   thm-mid's proof cites lem-base;  thm-top's proof cites thm-mid.
#   lem-other is independent. So:
#     upstream(thm-top) = {thm-mid, lem-base}   downstream(thm-top) = {}
#     upstream(thm-mid) = {lem-base}            downstream(thm-mid) = {thm-top}
#     upstream(lem-base) = {}                   downstream(lem-base) = {thm-mid, thm-top}
#     lem-other: isolated.

def _load_dep(page: Page, server: str) -> None:
    if page.viewport_size["width"] < 1321:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/deplens.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _lens_block(page: Page, block_id: str, direction: str) -> None:
    _open_step_menu(page, block_id)  # opens the ⋯ menu of any handrail block
    page.locator(f'#hr-menu-singleton [data-role="deplens-{direction}"]').click()


class TestResultMenu:
    def test_theorem_offers_both_directions(
        self, page: Page, interactive_server: str
    ):
        _load_dep(page, interactive_server)
        _open_step_menu(page, "thm-mid")
        expect(page.locator('#hr-menu-singleton [data-role="deplens-up"]')).to_be_visible()
        expect(page.locator('#hr-menu-singleton [data-role="deplens-down"]')).to_be_visible()

    def test_base_lemma_upstream_disabled(self, page: Page, interactive_server: str):
        _load_dep(page, interactive_server)
        _open_step_menu(page, "lem-base")
        up = page.locator('#hr-menu-singleton [data-role="deplens-up"]')
        expect(up).to_be_visible()
        expect(up).to_have_class(re.compile(r"\bdisabled\b"))
        expect(up).to_have_attribute("data-tooltip", re.compile(r"no other result"))
        expect(
            page.locator('#hr-menu-singleton [data-role="deplens-down"]')
        ).not_to_have_class(re.compile(r"\bdisabled\b"))

    def test_top_theorem_downstream_disabled(
        self, page: Page, interactive_server: str
    ):
        _load_dep(page, interactive_server)
        _open_step_menu(page, "thm-top")
        expect(
            page.locator('#hr-menu-singleton [data-role="deplens-up"]')
        ).not_to_have_class(re.compile(r"\bdisabled\b"))
        down = page.locator('#hr-menu-singleton [data-role="deplens-down"]')
        expect(down).to_be_visible()
        expect(down).to_have_class(re.compile(r"\bdisabled\b"))

    def test_isolated_lemma_both_disabled(self, page: Page, interactive_server: str):
        _load_dep(page, interactive_server)
        _open_step_menu(page, "lem-other")
        up = page.locator('#hr-menu-singleton [data-role="deplens-up"]')
        down = page.locator('#hr-menu-singleton [data-role="deplens-down"]')
        # Both shown, both disabled: an isolated result still surfaces the pair.
        expect(up).to_be_visible()
        expect(down).to_be_visible()
        expect(up).to_have_class(re.compile(r"\bdisabled\b"))
        expect(down).to_have_class(re.compile(r"\bdisabled\b"))


class TestResultUpstream:
    def test_upstream_lights_transitive_cone(
        self, page: Page, interactive_server: str
    ):
        _load_dep(page, interactive_server)
        _lens_block(page, "thm-top", "up")
        # thm-top rests on thm-mid, which rests on lem-base: both lit, transitively.
        assert _has(page, "thm-mid", "deplens-up")
        assert _has(page, "lem-base", "deplens-up")
        assert _has(page, "thm-top", "deplens-anchor")
        # the unrelated lemma is off the cone and recedes.
        assert _has(page, "lem-other", "deplens-faded")

    def test_switches_to_document_scope(self, page: Page, interactive_server: str):
        _load_dep(page, interactive_server)
        _lens_block(page, "thm-top", "up")
        expect(
            page.locator('.proof-rail .rail-scope[data-scope="document"]')
        ).to_have_class(re.compile(r"\bactive\b"))
        expect(page.locator(".deplens-bar")).to_be_visible()


class TestResultDownstream:
    def test_downstream_marks_dependents(self, page: Page, interactive_server: str):
        _load_dep(page, interactive_server)
        _lens_block(page, "lem-base", "down")
        # thm-mid rests on lem-base, and thm-top rests on thm-mid: both depend on it.
        assert _has(page, "thm-mid", "deplens-down")
        assert _has(page, "thm-top", "deplens-down")
        assert _has(page, "lem-base", "deplens-anchor")
        # downstream does not fade the rest.
        assert _has(page, "lem-other", "deplens-faded") is False


class TestResultCompose:
    def test_both_directions_on_a_theorem(self, page: Page, interactive_server: str):
        _load_dep(page, interactive_server)
        _lens_block(page, "thm-mid", "up")
        page.locator(".deplens-bar .deplens-add").click()
        assert _has(page, "lem-base", "deplens-up")  # what thm-mid rests on
        assert _has(page, "thm-top", "deplens-down")  # what rests on thm-mid
        assert _has(page, "thm-mid", "deplens-anchor")
        assert _has(page, "lem-other", "deplens-faded")
