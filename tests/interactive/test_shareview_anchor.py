"""Interactive tests for where a shared view lands, and the pins it carries (rsm-n4k).

"Copy this view" records the block at the top of the sender's window. The
recipient must land on that same block, at the same height, even when:

- a proof above the reader is folded (its hidden steps have a zero rect and
  used to win the "topmost block" search),
- the reader is inside an open proof,
- the layout shifts after the restore (math styles that change late, or
  content inserted late), and
- the sender had blocks pinned (the pins ride along for that visit only).

The shareview_long fixture is a long document with a lemma, a proof folded by
default, an open proof, and five sections of math-heavy labelled paragraphs.
"""

import base64
import json
import re
import time
from urllib.parse import parse_qs, urlparse

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"
# The page is shown (rsm-hc8): RSM is ready and the loading class is gone.
REVEALED = (
    "() => window.__rsmShown === true"
    " && !document.documentElement.classList.contains('rsm-loading')"
)
SENDER_TOP = 12
TOLERANCE = 50

# A late stylesheet that pushes everything below each display equation down.
# Added some time after RSM is ready, so the restore happens first.
SLOW_MATH_CSS = ".manuscript .mathblock { padding-top: 140px !important; }"
SLOW_DELAY_S = 1.5
def _slow_math_script(delay_s: float) -> str:
    return f"""
(() => {{
  const go = () => {{
    if (!window.__rsmInitialized) return setTimeout(go, 20);
    setTimeout(() => {{
      const style = document.createElement('style');
      style.textContent = {SLOW_MATH_CSS!r};
      document.head.appendChild(style);
    }}, {int(delay_s * 1000)});
  }};
  go();
}})();
"""


# A change that comes while the page is still loading: RSM waits for the page
# to keep its size for 0.5 s before showing it (rsm-hc8), so this lands first.
DURING_LOADING_S = 0.2

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
    }, 200);
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
          if (window.rsm && window.rsm.mathIdle) await window.rsm.mathIdle();
          await document.fonts.ready;
          await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
        }"""
    )


def _load(page: Page, server: str, query: str = "") -> None:
    if page.viewport_size["width"] < 1321:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/shareview_long.html{query}")
    page.wait_for_function(REVEALED, timeout=10_000)


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
    page.wait_for_function(REVEALED, timeout=10_000)
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
    top = _top(page, anchor)
    where = page.evaluate(
        "() => ({scrollY, height: document.documentElement.scrollHeight})"
    )
    assert abs(top - sender_top) <= TOLERANCE, (top, sender_top, where)
    assert anchor in _blocks_at(page, sender_top)


def _route_slow_math_css(page: Page, delay_s: float = SLOW_DELAY_S) -> None:
    page.add_init_script(_slow_math_script(delay_s))


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
        _route_slow_math_css(page, DURING_LOADING_S)
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
    def _pin(self, page: Page, block_id: str) -> None:
        block = page.locator(f"#{block_id}")
        block.scroll_into_view_if_needed()
        block.hover()
        block.locator(":scope > .hr-border-zone .hr-border-dots").click()
        page.locator('#hr-menu-singleton [data-role="pin"]').click()
        expect(
            page.locator(f'.rail-pinned-body > [data-pin-target="#{block_id}"]')
        ).to_have_count(1)
        # Pinning opens the panel, and the text column narrows over 0.22s. A
        # link copied before that ends records a scroll position from a
        # layout that the recipient never has.
        page.evaluate(
            """() => Promise.all(document.querySelector('main.manuscriptwrapper')
                 .getAnimations().map(a => a.finished))"""
        )

    def _pinned(self, page: Page) -> list[str]:
        return page.locator(".rail-pinned-body > [data-pin-target]").evaluate_all(
            "els => els.map(e => e.dataset.pinTarget)"
        )

    def test_pins_ride_along_and_are_not_saved(
        self, page: Page, interactive_server: str
    ):
        _fresh_sender(page, interactive_server)
        self._pin(page, "lem-main")
        self._pin(page, "par-1-1")
        assert self._pinned(page) == ["#par-1-1", "#lem-main"]
        _settle(page)
        _place(page, "par-1-6")
        sender_top = _top(page, "par-1-6")
        url = _copy_view_url(page)
        assert _token(url)["pins"] == ["par-1-1", "lem-main"]

        # The recipient has their own saved settings already.
        page.evaluate("() => localStorage.clear()")
        _load(page, interactive_server)
        saved_before = page.evaluate("() => JSON.stringify({...localStorage})")

        # The page is shown once its layout has settled (rsm-hc8), so the
        # anchor is in place at the reveal and stays there.
        page.goto(url)
        page.wait_for_function(REVEALED, timeout=10_000)
        _assert_lands_like_sender(page, "par-1-6", sender_top)
        expect(page.locator(".rsm-shared-pill")).to_be_visible(timeout=5000)
        rail = page.locator(".proof-rail")
        expect(rail).to_have_class(re.compile(r"\bhas-pin\b"))
        # Newest on top, as the sender had them.
        assert self._pinned(page) == ["#par-1-1", "#lem-main"]
        expect(page.locator(".rail-pinned-body")).to_contain_text("For every")
        assert "view=" not in page.evaluate("() => window.location.search")
        page.wait_for_timeout(600)
        _assert_lands_like_sender(page, "par-1-6", sender_top)

        assert page.evaluate("() => JSON.stringify({...localStorage})") == saved_before
        page.reload()
        page.wait_for_function(REVEALED, timeout=10_000)
        expect(rail).not_to_have_class(re.compile(r"\bhas-pin\b"))
        expect(page.locator(".rsm-shared-pill")).to_have_count(0)
        assert page.evaluate("() => JSON.stringify({...localStorage})") == saved_before

    def test_a_pinned_copy_fold_is_not_carried(self, page: Page, interactive_server: str):
        _fresh_sender(page, interactive_server)
        self._pin(page, "lem-main")
        copy = page.locator('.rail-pinned-body > [data-pin-target="#lem-main"]')
        copy.hover()
        copy.locator(":scope > .hr-collapse-zone .hr-collapse").click()
        expect(copy).to_have_class(re.compile(r"\bhr-collapsed\b"))
        url = _copy_view_url(page)
        assert "folds" not in _token(url)

    def test_no_pin_no_pins_field(self, page: Page, interactive_server: str):
        _fresh_sender(page, interactive_server)
        url = _copy_view_url(page)
        assert "pins" not in _token(url)


# Records where a block sits at the moment the page is shown. The observer is
# on the document because this runs before the <html> element exists.
REVEAL_PROBE_SCRIPT = """
window.__revealTop = null;
new MutationObserver(() => {
  const root = document.documentElement;
  if (!root || window.__revealTop !== null || !window.__probeId) return;
  if (!root.classList.contains('rsm-revealing')) return;
  const el = document.getElementById(window.__probeId);
  window.__revealTop = {top: el.getBoundingClientRect().top, at: performance.now()};
}).observe(document, {attributes: true, subtree: true, attributeFilter: ['class']});
"""
FONT_DELAY_S = 1.5


class TestSlowLoad:
    """Loading takes more than 3 s, so the pre-paint script shows the page before
    RSM has settled (rsm-y87). The reader must see the target when the page is
    shown, and see it in the right place once the layout has settled."""

    def _open_with_slow_fonts(self, page: Page, url: str, probe_id: str) -> None:
        # Each web font arrives FONT_DELAY_S after it was asked for. A route
        # handler that sleeps would hold the fonts one after the other, and the
        # test with them, so the requests are held and released here.
        held = []
        page.route("**/*.{woff,woff2}", lambda route: held.append((time.time(), route)))
        page.add_init_script(REVEAL_PROBE_SCRIPT)
        page.add_init_script(f"window.__probeId = {probe_id!r};")
        if page.viewport_size["width"] < 1321:
            page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(url, wait_until="commit")
        t0 = time.time()
        while not page.evaluate(REVEALED):
            assert time.time() - t0 < 20, "the page was never shown"
            now = time.time()
            for item in [h for h in held if now - h[0] >= FONT_DELAY_S]:
                held.remove(item)
                item[1].continue_()
            page.wait_for_timeout(50)
        for _, route in held:
            route.continue_()
        page.unroute("**/*.{woff,woff2}")
        _settle(page)
        # RSM waits for the layout to keep its size for 0.5 s, then places the
        # target again.
        page.wait_for_timeout(1200)

    def _shown(self, page: Page) -> dict:
        shown = page.evaluate("() => window.__revealTop")
        # The 3 s fallback showed the page, not the settled reveal.
        assert shown["at"] >= 2900, shown
        return shown

    def test_hash_target_is_in_view_when_the_page_is_shown(
        self, page: Page, interactive_server: str
    ):
        self._open_with_slow_fonts(
            page, f"{interactive_server}/shareview_long.html#par-4-2", "par-4-2"
        )
        shown = self._shown(page)
        assert 0 <= shown["top"] < 200, shown
        settled = _top(page, "par-4-2")
        assert 0 <= settled < 200, settled
        assert page.evaluate("() => document.activeElement.id") == "par-4-2"

    def test_shared_anchor_is_in_view_when_the_page_is_shown(
        self, page: Page, interactive_server: str
    ):
        token = _encode({"v": 1, "anchor": "par-4-2", "anchorTop": SENDER_TOP})
        self._open_with_slow_fonts(
            page, f"{interactive_server}/shareview_long.html?view={token}", "par-4-2"
        )
        shown = self._shown(page)
        assert abs(shown["top"] - SENDER_TOP) <= TOLERANCE, shown
        _assert_lands_like_sender(page, "par-4-2", SENDER_TOP)
