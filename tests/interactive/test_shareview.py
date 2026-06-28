"""Interactive tests for the shareable presentation-state link (potf-44f).

A reader's constructed view (rail scope, folds, logic-preserving reorder order,
scroll anchor) is captured on demand by "Copy this view" in the document-scope
sidebar into a ?view= URL, and restored on load behind a "Shared view / Reset to
original" pill. The reorder.html fixture supplies folds, a reorderable proof, and
the rail scopes.
"""

from urllib.parse import urlparse, parse_qs

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _load(page: Page, server: str, query: str = "") -> None:
    if page.viewport_size["width"] < 1321:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/reorder.html{query}")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _copy_view_url(page: Page) -> str:
    page.locator(".proof-rail .rail-share-view").click()
    # Clipboard permissions are granted in conftest's browser_context_args.
    return page.evaluate("() => navigator.clipboard.readText()")


def _step_order(page: Page):
    return page.locator(".proof.hr").first.locator(".step").evaluate_all(
        "els => els.map(e => e.id)"
    )


def _collapsed(page: Page, block_id: str) -> bool:
    return page.locator(f"#{block_id}").evaluate(
        "el => el.classList.contains('hr-collapsed')"
    )


class TestCopyAction:
    def test_button_in_document_scope(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        expect(page.locator(".proof-rail .rail-share-view")).to_be_visible()

    def test_copy_writes_view_url(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        url = _copy_view_url(page)
        assert "view=" in url
        assert "view" in parse_qs(urlparse(url).query)

    def test_plain_copy_link_stays_anchor(self, page: Page, interactive_server: str):
        # The per-block "Copy link" must NOT become a view link.
        _load(page, interactive_server)
        step = page.locator("#stp-a")
        step.scroll_into_view_if_needed()
        step.hover()
        step.locator(".hr-border-dots").first.click()
        page.locator('#hr-menu-singleton [data-role="link"]').click()
        link = page.evaluate("() => navigator.clipboard.readText()")
        assert "#stp-a" in link and "view=" not in link


class TestRestore:
    def test_fold_roundtrips(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        # Collapse a step, then snapshot the view.
        page.evaluate(
            """async () => {
              const H = await import('/static/handrails.js');
              H.closeHandrail(document.getElementById('stp-setup'));
            }"""
        )
        assert _collapsed(page, "stp-setup") is True
        url = _copy_view_url(page)

        # Open the shared link as a FRESH recipient (clear localStorage so the
        # fold can only come from the token, not leaked persistence).
        page.evaluate("() => localStorage.clear()")
        page.goto(url)
        page.wait_for_function(RSM_READY, timeout=10_000)
        expect(page.locator(".rsm-shared-pill")).to_be_visible(timeout=5000)
        assert _collapsed(page, "stp-setup") is True

    def test_view_param_is_stripped(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        url = _copy_view_url(page)
        page.goto(url)
        page.wait_for_function(RSM_READY, timeout=10_000)
        expect(page.locator(".rsm-shared-pill")).to_be_visible(timeout=5000)
        # Once restored, the URL is clean so the #fragment/copyLink contract holds.
        assert "view=" not in page.evaluate("() => window.location.search")

    def test_notation_roundtrips(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        # Rebind \eig, then snapshot the view.
        page.evaluate(
            """async () => {
              const N = await import('/static/notation.js');
              N.setMacro('\\\\eig', '\\\\mu');
            }"""
        )
        url = _copy_view_url(page)

        # Fresh recipient: the rebinding must come from the token, not persistence.
        page.evaluate("() => localStorage.clear()")
        page.goto(url)
        page.wait_for_function(RSM_READY, timeout=10_000)
        expect(page.locator(".rsm-shared-pill")).to_be_visible(timeout=5000)
        in_force = page.evaluate(
            """async () => {
              const N = await import('/static/notation.js');
              return N.getNotationMacros()['\\\\eig'];
            }"""
        )
        assert in_force == "\\mu"

    def test_reorder_roundtrips(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        # Enter reorder mode and legally swap stp-b above stp-a.
        proof = page.locator(".proof.hr").first
        proof.scroll_into_view_if_needed()
        proof.hover()
        proof.locator(".hr-border-dots").first.click()
        page.locator('#hr-menu-singleton [data-role="reorder"]').click()
        handle = page.locator("#stp-b .reorder-handle").first.bounding_box()
        a = page.locator("#stp-a").bounding_box()
        page.mouse.move(handle["x"] + handle["width"] / 2, handle["y"] + handle["height"] / 2)
        page.mouse.down()
        page.mouse.move(a["x"] + 40, a["y"] + 5, steps=12)
        page.mouse.up()
        assert _step_order(page) == ["stp-setup", "stp-b", "stp-a", "stp-c"]
        url = _copy_view_url(page)

        page.evaluate("() => localStorage.clear()")
        page.goto(url)
        page.wait_for_function(RSM_READY, timeout=10_000)
        expect(page.locator(".rsm-shared-pill")).to_be_visible(timeout=5000)
        assert _step_order(page) == ["stp-setup", "stp-b", "stp-a", "stp-c"]


class TestResetPill:
    def test_reset_returns_to_pristine(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        page.evaluate(
            """async () => {
              const H = await import('/static/handrails.js');
              H.closeHandrail(document.getElementById('stp-setup'));
            }"""
        )
        url = _copy_view_url(page)
        page.evaluate("() => localStorage.clear()")
        page.goto(url)
        page.wait_for_function(RSM_READY, timeout=10_000)
        pill = page.locator(".rsm-shared-pill")
        expect(pill).to_be_visible(timeout=5000)
        assert _collapsed(page, "stp-setup") is True
        pill.locator(".rsm-shared-pill-reset").click()
        page.wait_for_function(RSM_READY, timeout=10_000)
        # Pristine paper: the fold is gone and no pill (the recipient never saved it).
        assert _collapsed(page, "stp-setup") is False
        expect(page.locator(".rsm-shared-pill")).to_have_count(0)


class TestAccessibility:
    def test_pill_is_polite_status(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        url = _copy_view_url(page)
        page.goto(url)
        page.wait_for_function(RSM_READY, timeout=10_000)
        pill = page.locator(".rsm-shared-pill")
        expect(pill).to_be_visible(timeout=5000)
        expect(pill).to_have_attribute("role", "status")
        expect(pill).to_have_attribute("aria-live", "polite")
