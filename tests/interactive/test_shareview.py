"""Interactive tests for the shareable presentation-state link (potf-44f).

A reader's constructed view (rail scope, folds, logic-preserving reorder order,
scroll anchor) is captured on demand by "Copy this view" in the document-scope
sidebar into a ?view= URL, and restored on load behind a "Shared view / Reset to
original" pill. The reorder.html fixture supplies folds, a reorderable proof, and
the rail scopes.
"""

import base64
import json
from urllib.parse import parse_qs, urlparse

import pytest
from playwright.sync_api import Page, expect

import rsm

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"


def _load(page: Page, server: str, query: str = "") -> None:
    if page.viewport_size["width"] < 1321:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/reorder.html{query}")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _copy_view_url(page: Page) -> str:
    page.locator(".rail-strip .rail-share-view").click()
    # Clipboard permissions are granted in conftest's browser_context_args.
    return page.evaluate("() => navigator.clipboard.readText()")


def _step_order(page: Page):
    return (
        page.locator(".proof.hr")
        .first.locator(".step")
        .evaluate_all("els => els.map(e => e.id)")
    )


def _collapsed(page: Page, block_id: str) -> bool:
    return page.locator(f"#{block_id}").evaluate(
        "el => el.classList.contains('hr-collapsed')"
    )


class TestCopyAction:
    def test_button_in_strip(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        expect(page.locator(".rail-strip .rail-share-view")).to_be_visible()

    def test_copy_writes_view_url(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        url = _copy_view_url(page)
        assert "view=" in url
        assert "view" in parse_qs(urlparse(url).query)

    def test_copy_confirms_in_manuscript_terms(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _copy_view_url(page)
        toast = page.locator(".toast").last
        expect(toast).to_contain_text("manuscript")
        expect(toast).not_to_contain_text("paper")

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
        # Collapse a proof, then snapshot the view.
        page.evaluate(
            """async () => {
              const H = await import('/static/handrails.js');
              H.closeHandrail(document.getElementById('stp-setup').closest('.proof.hr'));
            }"""
        )
        proof = page.evaluate(
            "() => document.getElementById('stp-setup').closest('.proof.hr').id"
        )
        assert _collapsed(page, proof) is True
        url = _copy_view_url(page)

        # Open the shared link as a FRESH recipient (clear localStorage so the
        # fold can only come from the token, not leaked persistence).
        page.evaluate("() => localStorage.clear()")
        page.goto(url)
        page.wait_for_function(RSM_READY, timeout=10_000)
        expect(page.locator(".rsm-shared-pill")).to_be_visible(timeout=5000)
        assert _collapsed(page, proof) is True

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
        page.mouse.move(
            handle["x"] + handle["width"] / 2, handle["y"] + handle["height"] / 2
        )
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


def _token(state: dict) -> str:
    raw = json.dumps(state).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


# Keeps every math render of the paragraph that uses \eig, from before any page
# script runs, so a render with the default symbol cannot slip by between two
# checks. The renders are read at the end because MathJax adds the text after it
# inserts the container.
RECORD_EIG_RENDERS = """
  window.__eigRenders = [];
  new MutationObserver((records) => {
    for (const r of records) {
      for (const n of r.addedNodes) {
        if (n.nodeName !== 'MJX-CONTAINER') continue;
        const math = n.closest('span.math');
        if (!math || math.dataset.latex !== '\\\\eig') continue;
        window.__eigRenders.push(n);
      }
    }
  }).observe(document, { childList: true, subtree: true });
"""


class TestNotationBeforeFirstTypeset:
    def test_math_is_typeset_once_with_senders_symbol(
        self, page: Page, interactive_server: str
    ):
        page.add_init_script(RECORD_EIG_RENDERS)
        token = _token({"v": 1, "notation": {"\\eig": "\\mu"}})
        _load(page, interactive_server, f"?view={token}")
        expect(page.locator(".rsm-shared-pill")).to_be_visible(timeout=5000)
        renders = page.evaluate("() => window.__eigRenders.map((n) => n.textContent)")
        assert len(renders) == 1, renders
        assert "μ" in renders[0] and "λ" not in renders[0], renders

    def test_shared_notation_is_not_saved(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        page.evaluate("() => localStorage.clear()")
        token = _token({"v": 1, "notation": {"\\eig": "\\mu"}})
        _load(page, interactive_server, f"?view={token}")
        saved = page.evaluate(
            "() => Object.keys(localStorage).filter((k) => k.startsWith('rsm-notation:'))"
        )
        assert saved == []

    def test_other_version_token_leaves_notation_alone(
        self, page: Page, interactive_server: str
    ):
        token = _token({"v": 999, "notation": {"\\eig": "\\mu"}})
        _load(page, interactive_server, f"?view={token}")
        in_force = page.evaluate(
            """async () => {
              const N = await import('/static/notation.js');
              return N.getNotationMacros()['\\\\eig'];
            }"""
        )
        assert in_force == "\\lambda"


class TestResetPill:
    def test_reset_returns_to_pristine(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        page.evaluate(
            """async () => {
              const H = await import('/static/handrails.js');
              H.closeHandrail(document.getElementById('stp-setup').closest('.proof.hr'));
            }"""
        )
        proof = page.evaluate(
            "() => document.getElementById('stp-setup').closest('.proof.hr').id"
        )
        url = _copy_view_url(page)
        page.evaluate("() => localStorage.clear()")
        page.goto(url)
        page.wait_for_function(RSM_READY, timeout=10_000)
        pill = page.locator(".rsm-shared-pill")
        expect(pill).to_be_visible(timeout=5000)
        assert _collapsed(page, proof) is True
        pill.locator(".rsm-shared-pill-reset").click()
        page.wait_for_function(RSM_READY, timeout=10_000)
        # Pristine paper: the fold is gone and no pill (the recipient never saved it).
        assert _collapsed(page, proof) is False
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


# Two builds of one document, served one after the other at the same URL. V2
# adds a paragraph before the theorem, which shifts every node id after it.
_V1 = """# Folds

:theorem:

  An unlabelled theorem.

::

The last paragraph.
"""
_V2 = _V1.replace(":theorem:", "A new first paragraph.\n\n:theorem:", 1)


def _serve(page: Page, server: str, source: str, query: str = "") -> None:
    html = rsm.build(source=source, handrails=True, standalone=False, sidebar=True)
    page.unroute("**/view-change.html*")
    page.route(
        "**/view-change.html*",
        lambda route: route.fulfill(body=html, content_type="text/html"),
    )
    page.evaluate("() => localStorage.clear()")
    page.goto(f"{server}/view-change.html{query}")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _collapsed_texts(page: Page):
    return page.evaluate(
        r"""() => [...document.querySelectorAll('.manuscript .hr-collapsed')]
             .map(h => (h.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 30))"""
    )


class TestChangedDocument:
    def test_unlabelled_fold_stays_on_its_block(
        self, page: Page, interactive_server: str
    ):
        page.goto(f"{interactive_server}/basic.html")
        _serve(page, interactive_server, _V1)
        page.locator(".theorem.hr > .hr-collapse-zone .hr-collapse").click()
        token = page.evaluate(
            """async () => {
              const S = await import('/static/shareview.js');
              return S.captureState();
            }"""
        )
        _serve(page, interactive_server, _V2, f"?view={_token(token)}")
        texts = _collapsed_texts(page)
        assert len(texts) == 1 and "unlabelled theor" in texts[0], texts

    def test_fold_that_matches_no_block_is_ignored(
        self, page: Page, interactive_server: str
    ):
        page.goto(f"{interactive_server}/basic.html")
        _serve(page, interactive_server, _V1)
        folds = page.evaluate(
            """() => {
              const p = [...document.querySelectorAll('.manuscript .paragraph.hr')]
                .find(el => el.textContent.includes('The last paragraph'));
              const folds = {'n:1': true, 'n:2': true, 'l:gone': true,
                             'h:00000000': true};
              if (p.dataset.hash) folds['h:' + p.dataset.hash] = true;
              return folds;
            }"""
        )
        _serve(
            page, interactive_server, _V1, f"?view={_token({'v': 1, 'folds': folds})}"
        )
        assert _collapsed_texts(page) == []
        hidden = page.evaluate(
            "() => document.querySelectorAll('.manuscript .hide').length"
        )
        assert hidden == 0


# An unlabelled theorem and an unlabelled proof, with filler after them so that
# the page scrolls. The steps have labels because reordering needs them. V4
# adds a paragraph before the theorem.
_V3 = (
    """# Parts

:theorem:

  An unlabelled theorem.

::

:proof:

  :step: {:label: s-1} First step. ::

  :step: {:label: s-2} Second step. ::

  :step: {:label: s-3} Third step. ::

::

"""
    + "\n\n".join(f"Filler paragraph {i}." for i in range(40))
    + "\n"
)
_V4 = _V3.replace(":theorem:", "A new first paragraph.\n\n:theorem:", 1)


def _step_texts(page: Page):
    return page.locator(".proof.hr .step").evaluate_all(
        "els => els.map(e => e.textContent.trim().split(' ')[0])"
    )


class TestChangedDocumentParts:
    """Pins, the step order and the block at the top of the window use the same
    keys as folds."""

    def test_pin_stays_on_its_block(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/basic.html")
        _serve(page, interactive_server, _V3)
        token = page.evaluate(
            """async () => {
              const T = await import('/static/tooltips.js');
              const S = await import('/static/shareview.js');
              T.pinTarget('#' + document.querySelector('.manuscript .theorem.hr').id);
              return S.captureState();
            }"""
        )
        _serve(page, interactive_server, _V4, f"?view={_token(token)}")
        expect(page.locator(".rail-pinned-body > [data-pin-target]")).to_have_count(1)
        assert page.evaluate(
            """() => document.querySelector('.rail-pinned-body > [data-pin-target]')
                 .dataset.pinTarget === '#' +
                 document.querySelector('.manuscript .theorem.hr').id"""
        )

    def test_step_order_stays_on_its_steps(self, page: Page, interactive_server: str):
        if page.viewport_size["width"] < 1321:
            page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{interactive_server}/basic.html")
        _serve(page, interactive_server, _V3)
        order = page.evaluate(
            """async () => {
              const H = await import('/static/handrails.js');
              const proof = document.querySelector('.manuscript .proof.hr');
              const s = [...proof.querySelectorAll('.step')].map(H.blockKey);
              return {[H.blockKey(proof)]: [s[2], s[0], s[1]]};
            }"""
        )
        _serve(
            page, interactive_server, _V4, f"?view={_token({'v': 1, 'order': order})}"
        )
        assert _step_texts(page) == ["Third", "First", "Second"]

    def test_anchor_stays_on_its_block(self, page: Page, interactive_server: str):
        page.goto(f"{interactive_server}/basic.html")
        _serve(page, interactive_server, _V3)
        token = page.evaluate(
            """async () => {
              const S = await import('/static/shareview.js');
              const t = document.querySelector('.manuscript .theorem.hr');
              window.scrollTo({top: window.scrollY + t.getBoundingClientRect().top - 20,
                               behavior: 'instant'});
              return S.captureState();
            }"""
        )
        assert token["anchor"].startswith("h:"), token
        _serve(page, interactive_server, _V4, f"?view={_token(token)}")
        page.wait_for_timeout(500)
        top = page.evaluate(
            """() => document.querySelector('.manuscript .theorem.hr')
                 .getBoundingClientRect().top"""
        )
        assert abs(top - token["anchorTop"]) <= 3, (top, token)
