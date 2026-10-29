"""Interactive tests for where a shared view lands, and the pin it carries (rsm-n4k).

"Copy this view" records the block at the top of the sender's window. The
recipient must land on that same block, at the same height, even when:

- a proof above the reader is folded (its hidden steps have a zero rect and
  used to win the "topmost block" search),
- the reader is inside an open proof,
- the layout shifts after the restore (math styles that change late, or
  content inserted late), and
- the sender had a block pinned (the pin rides along for that visit only).

The shareview_long fixture is a long document with a lemma, a proof folded by
default, an open proof, and five sections of math-heavy labelled paragraphs.
"""

import base64
import json
import re
from urllib.parse import parse_qs, urlparse

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"
SENDER_TOP = 12
TOLERANCE = 50

# A late stylesheet that pushes everything below each display equation down.
# Added some time after RSM is ready, so the restore happens first.
SLOW_MATH_CSS = ".manuscript .mathblock { padding-top: 140px !important; }"
SLOW_DELAY_S = 1.5
SLOW_MATH_SCRIPT = f"""
(() => {{
  const go = () => {{
    if (!window.__rsmInitialized) return setTimeout(go, 20);
    setTimeout(() => {{
      const style = document.createElement('style');
      style.textContent = {SLOW_MATH_CSS!r};
      document.head.appendChild(style);
    }}, {int(SLOW_DELAY_S * 1000)});
  }};
  go();
}})();
"""

# Chrome's scroll anchoring hides a late shift above the window by adjusting
# the scroll itself, and only in some cases. Safari has no scroll anchoring.
# Turn it off so the late-layout tests see the shift every time.
NO_SCROLL_ANCHORING_SCRIPT = """
document.addEventListener('DOMContentLoaded', () => {
  document.documentElement.style.overflowAnchor = 'none';
});
"""

# Inserts tall content at the top of the manuscript some time after load.
LATE_SHIFT_SCRIPT = """
(() => {
  const go = () => {
    if (!window.__rsmInitialized) return setTimeout(go, 20);
    setTimeout(() => {
      const m = document.querySelector('.manuscript');
      const d = document.createElement('div');
      d.className = 'late-shift';
      d.style.height = '600px';
      m.insertBefore(d, m.firstChild);
    }, 700);
  };
  go();
})();
"""


def _token(url: str) -> dict:
    tok = parse_qs(urlparse(url).query)["view"][0]
    tok += "=" * (-len(tok) % 4)
    return json.loads(base64.urlsafe_b64decode(tok).decode())


def _encode(state: dict) -> str:
    raw = base64.urlsafe_b64encode(json.dumps(state).encode()).decode()
    return raw.rstrip("=")


def _settle(page: Page) -> None:
    page.evaluate(
        """async () => {
          await document.fonts.ready;
          await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
        }"""
    )


def _load(page: Page, server: str, query: str = "") -> None:
    if page.viewport_size["width"] < 1321:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/shareview_long.html{query}")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _fresh_sender(page: Page, server: str) -> None:
    _load(page, server)
    page.evaluate("() => localStorage.clear()")
    _load(page, server)
    _settle(page)


def _top(page: Page, block_id: str) -> float:
    return page.evaluate(
        "id => document.getElementById(id).getBoundingClientRect().top", block_id
    )


def _place(page: Page, block_id: str, top: float = SENDER_TOP) -> None:
    page.evaluate(
        """([id, top]) => {
          const el = document.getElementById(id);
          window.scrollBy(0, el.getBoundingClientRect().top - top);
        }""",
        [block_id, top],
    )
    _settle(page)


def _blocks_at(page: Page, y: float) -> list[str]:
    # The blocks (innermost first) under a point in the text column, a little
    # below y. A step's first paragraph is a block of its own, so the step is
    # its parent here.
    return page.evaluate(
        """y => {
          const m = document.querySelector('.manuscript').getBoundingClientRect();
          let el = document.elementFromPoint(m.left + m.width / 2, y + 8);
          const ids = [];
          while (el && (el = el.closest('.hr[id]'))) {
            ids.push(el.id);
            el = el.parentElement;
          }
          return ids;
        }""",
        y,
    )


def _copy_view_url(page: Page) -> str:
    page.locator(".rail-strip .rail-share-view").click()
    return page.evaluate("() => navigator.clipboard.readText()")


def _open_as_recipient(page: Page, url: str, wait_until: str = "load") -> None:
    page.evaluate("() => localStorage.clear()")
    page.goto(url, wait_until=wait_until)
    page.wait_for_function(RSM_READY, timeout=10_000)
    expect(page.locator(".rsm-shared-pill")).to_be_visible(timeout=5000)


def _open_proof(page: Page, step_id: str) -> None:
    page.evaluate(
        """async (id) => {
          const H = await import('/static/handrails.js');
          H.openHandrail(document.getElementById(id).closest('.proof.hr'));
        }""",
        step_id,
    )
    _settle(page)


def _assert_lands_like_sender(page: Page, anchor: str, sender_top: float) -> None:
    assert abs(_top(page, anchor) - sender_top) <= TOLERANCE
    assert anchor in _blocks_at(page, sender_top)


def _route_slow_math_css(page: Page) -> None:
    page.add_init_script(SLOW_MATH_SCRIPT)


def _wait_slow_css(page: Page) -> None:
    page.wait_for_function(
        """() => {
          const mb = document.querySelector('.manuscript .mathblock');
          return mb && getComputedStyle(mb).paddingTop === '140px';
        }""",
        timeout=10_000,
    )
    _settle(page)
    # Leave the restore code a few frames to react to the shift.
    page.wait_for_timeout(300)


class TestAnchorChoice:
    def test_folded_proof_does_not_steal_the_anchor(
        self, page: Page, interactive_server: str
    ):
        _fresh_sender(page, interactive_server)
        assert page.locator("#stp-f1").evaluate("el => el.getClientRects().length") == 0
        _place(page, "par-3-4")
        sender_top = _top(page, "par-3-4")
        url = _copy_view_url(page)
        assert _token(url)["anchor"] == "par-3-4"

        _open_as_recipient(page, url)
        _settle(page)
        _assert_lands_like_sender(page, "par-3-4", sender_top)

    def test_reader_inside_an_unfolded_proof_step(
        self, page: Page, interactive_server: str
    ):
        _fresh_sender(page, interactive_server)
        _open_proof(page, "stp-f1")
        _place(page, "stp-f5")
        sender_top = _top(page, "stp-f5")
        url = _copy_view_url(page)
        assert _token(url)["anchor"] == "stp-f5"

        _open_as_recipient(page, url)
        _settle(page)
        # The fold state rode along, so the step is visible for the recipient.
        assert page.locator("#stp-f5").evaluate("el => el.getClientRects().length") > 0
        _assert_lands_like_sender(page, "stp-f5", sender_top)

    def test_block_partly_above_the_window_keeps_its_offset(
        self, page: Page, interactive_server: str
    ):
        # A reader halfway through a block: that block, at that offset.
        _fresh_sender(page, interactive_server)
        _place(page, "par-4-2", top=-30)
        url = _copy_view_url(page)
        assert _token(url)["anchor"] == "par-4-2"

        _open_as_recipient(page, url)
        _settle(page)
        assert abs(_top(page, "par-4-2") - (-30)) <= TOLERANCE


class TestLateLayout:
    @pytest.fixture(autouse=True)
    def _no_scroll_anchoring(self, page: Page):
        page.add_init_script(NO_SCROLL_ANCHORING_SCRIPT)

    def test_slow_math_stylesheet(self, page: Page, interactive_server: str):
        _route_slow_math_css(page)
        _fresh_sender(page, interactive_server)
        _wait_slow_css(page)
        _place(page, "par-3-4")
        sender_top = _top(page, "par-3-4")
        url = _copy_view_url(page)

        _open_as_recipient(page, url)
        _wait_slow_css(page)
        _assert_lands_like_sender(page, "par-3-4", sender_top)

    def test_content_inserted_after_load(self, page: Page, interactive_server: str):
        page.add_init_script(LATE_SHIFT_SCRIPT)
        _fresh_sender(page, interactive_server)
        page.wait_for_selector(".late-shift", state="attached")
        _settle(page)
        _place(page, "par-2-5")
        sender_top = _top(page, "par-2-5")
        url = _copy_view_url(page)

        _open_as_recipient(page, url)
        page.wait_for_selector(".late-shift", state="attached")
        _settle(page)
        page.wait_for_timeout(300)
        _assert_lands_like_sender(page, "par-2-5", sender_top)

    def test_recipient_scroll_wins_over_late_reanchor(
        self, page: Page, interactive_server: str
    ):
        _route_slow_math_css(page)
        _fresh_sender(page, interactive_server)
        _wait_slow_css(page)
        _place(page, "par-3-4")
        url = _copy_view_url(page)

        # The recipient must be able to scroll before the late styles arrive.
        _open_as_recipient(page, url, wait_until="commit")
        # The recipient starts reading before the stylesheet arrives.
        page.mouse.move(700, 400)
        page.mouse.wheel(0, 600)
        page.wait_for_timeout(200)
        assert page.evaluate(
            "() => getComputedStyle(document.querySelector('.manuscript .mathblock')).paddingTop"
        ) != "140px"
        read_at = page.evaluate("() => window.scrollY")
        assert abs(_top(page, "par-3-4") - (SENDER_TOP - 600)) <= TOLERANCE
        _wait_slow_css(page)
        # The page stays where the recipient scrolled it. It is not pulled
        # back to the shared anchor.
        assert abs(page.evaluate("() => window.scrollY") - read_at) <= 2


class TestOldTokens:
    def test_anchor_only_token(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        token = _encode({"v": 1, "anchor": "par-2-3"})
        _open_as_recipient(
            page, f"{interactive_server}/shareview_long.html?view={token}"
        )
        _settle(page)
        assert abs(_top(page, "par-2-3")) <= TOLERANCE
        assert "view=" not in page.evaluate("() => window.location.search")

    def test_folds_token_without_pins(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        key = page.evaluate(
            """async () => {
              const H = await import('/static/handrails.js');
              return H.collapseKey(document.getElementById('stp-f1').closest('.proof.hr'));
            }"""
        )
        token = _encode({"v": 1, "folds": {key: False}, "anchor": "stp-f3"})
        _open_as_recipient(
            page, f"{interactive_server}/shareview_long.html?view={token}"
        )
        _settle(page)
        assert abs(_top(page, "stp-f3")) <= TOLERANCE
        expect(page.locator(".proof-rail")).not_to_have_class(re.compile(r"\bhas-pin\b"))


class TestPins:
    def _pin_lemma(self, page: Page) -> None:
        lemma = page.locator("#lem-main")
        lemma.scroll_into_view_if_needed()
        lemma.hover()
        lemma.locator(":scope > .hr-border-zone .hr-border-dots").click()
        page.locator('#hr-menu-singleton [data-role="pin"]').click()
        expect(page.locator(".proof-rail")).to_have_class(re.compile(r"\bhas-pin\b"))

    def test_pin_rides_along_and_is_not_saved(
        self, page: Page, interactive_server: str
    ):
        _fresh_sender(page, interactive_server)
        self._pin_lemma(page)
        title = page.locator(".rail-pinned-title").inner_text()
        assert title.startswith("Lemma")
        _settle(page)
        _place(page, "par-1-6")
        sender_top = _top(page, "par-1-6")
        url = _copy_view_url(page)
        assert _token(url)["pins"][0]["id"] == "lem-main"

        # The recipient has their own saved settings already.
        page.evaluate("() => localStorage.clear()")
        _load(page, interactive_server)
        saved_before = page.evaluate("() => JSON.stringify({...localStorage})")

        page.goto(url)
        page.wait_for_function(RSM_READY, timeout=10_000)
        expect(page.locator(".rsm-shared-pill")).to_be_visible(timeout=5000)
        rail = page.locator(".proof-rail")
        expect(rail).to_have_class(re.compile(r"\bhas-pin\b"))
        expect(page.locator(".rail-pinned-title")).to_have_text(title)
        expect(page.locator(".rail-pinned-body")).to_contain_text("For every")
        assert "view=" not in page.evaluate("() => window.location.search")
        _settle(page)
        page.wait_for_timeout(600)
        _assert_lands_like_sender(page, "par-1-6", sender_top)

        assert page.evaluate("() => JSON.stringify({...localStorage})") == saved_before
        page.reload()
        page.wait_for_function(RSM_READY, timeout=10_000)
        expect(rail).not_to_have_class(re.compile(r"\bhas-pin\b"))
        expect(page.locator(".rsm-shared-pill")).to_have_count(0)
        assert page.evaluate("() => JSON.stringify({...localStorage})") == saved_before

    def test_no_pin_no_pins_field(self, page: Page, interactive_server: str):
        _fresh_sender(page, interactive_server)
        url = _copy_view_url(page)
        assert "pins" not in _token(url)
