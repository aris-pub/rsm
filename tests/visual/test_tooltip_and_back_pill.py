"""Visual regression tests for reference tooltips and the back pill.

Two appearance guards for recently touched UI:

- An open reference tooltip. A tooltipster regression once let the tooltip box
  blow up into a full-width banner (the cloned block kept the document column's
  width:100% and sidebar-clearance margin); the fix lives in braiid/braiid.css
  and rsm/static/tooltips.js. This snapshot locks the capped, boxed tooltip.
- The back pill visible. After an in-document jump a transient
  <button class="rsm-back-pill"> fades in (created in rsm/static/onload.js,
  styled in braiid/braiid.css) and gains .is-visible. This snapshot locks its
  appearance.

Behavior (not appearance) is covered by tests/interactive/test_backpill.py.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

RSM_READY = "() => window.__rsmInitialized === true"

TOOLTIP_FIXTURE = Path(__file__).parent / "fixtures" / "reference-tooltip.rsm"
BACK_PILL_FIXTURE = Path(__file__).parent / "fixtures" / "back-pill.rsm"


@pytest.mark.visual
class TestReferenceTooltip:
    """Visual guard against the reference-tooltip overflow regression."""

    def test_reference_tooltip_open(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
    ) -> None:
        """Hover an in-text :ref: and capture the open tooltip.

        Guards the overflow regression: a correct tooltip is a compact, boxed
        card capped at maxWidth, not a full-width banner.
        """
        # Reference tooltips work at any width; a comfortable reading width makes
        # an overflow banner obvious against the capped box.
        page.set_viewport_size({"width": 1280, "height": 720})
        serve_rsm_html(TOOLTIP_FIXTURE.read_text())
        page.wait_for_function(RSM_READY, timeout=10_000)

        ref = page.locator('.manuscript a.reference[href="#thm-x"]').first
        ref.scroll_into_view_if_needed()
        ref.hover()

        # tooltipster appends the tooltip to <body> with a 200ms hover-intent
        # delay before it opens.
        page.wait_for_selector(".tooltipster-base", state="visible", timeout=3000)
        page.wait_for_timeout(300)

        assert_snapshot(page.screenshot())

    def test_reference_tooltip_open_dark(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
    ) -> None:
        """Dark-mode twin of test_reference_tooltip_open.

        In light mode the card's border and pointer are --border-primary, which
        is near-white, so pixelmatch's per-pixel threshold cannot see them: the
        light snapshot is blind to a missing or extra pointer. In dark mode the
        same tokens have real contrast against the page, so this snapshot is the
        one that actually guards the tooltip chrome, including that no pointer
        reappears (rsm-3y7).
        """
        page.set_viewport_size({"width": 1280, "height": 720})
        serve_rsm_html(TOOLTIP_FIXTURE.read_text())
        page.wait_for_function(RSM_READY, timeout=10_000)
        # The serve_rsm_html dark_theme flag string-replaces "<html>", which the
        # build does not emit (it is "<html lang=.. data-accent=..>"), so toggle
        # the class directly here.
        page.eval_on_selector("html", "h => h.classList.add('dark-theme')")

        ref = page.locator('.manuscript a.reference[href="#thm-x"]').first
        ref.scroll_into_view_if_needed()
        ref.hover()

        page.wait_for_selector(".tooltipster-base", state="visible", timeout=3000)
        page.wait_for_timeout(300)

        assert_snapshot(page.screenshot())


@pytest.mark.visual
class TestBackPill:
    """Visual guard for the transient back pill after an in-document jump."""

    def test_back_pill_visible(
        self,
        serve_rsm_html: callable,
        page: Page,
        assert_snapshot: callable,
    ) -> None:
        """Trigger an in-doc jump, wait for .is-visible, capture the pill.

        The interactive sidebar rail needs a desktop viewport (>=1400 wide).
        """
        page.set_viewport_size({"width": 1400, "height": 900})
        serve_rsm_html(BACK_PILL_FIXTURE.read_text())
        page.wait_for_function(RSM_READY, timeout=10_000)

        ref = page.locator('.manuscript a.reference[href="#thm-x"]').first
        ref.scroll_into_view_if_needed()
        page.wait_for_timeout(200)
        ref.click()

        page.wait_for_selector(".rsm-back-pill.is-visible", timeout=3000)
        # Let the fade-in transition settle before snapshotting.
        page.wait_for_timeout(300)

        # The pill is position:fixed, bottom-centre, so a viewport screenshot
        # (not full_page) reliably frames it.
        #
        # potf-4em: this fixture renders a :toc: tree (a DAG) plus a full column
        # of prose, so the frame is dense with text edges. Under CI CPU contention
        # those edges anti-alias slightly differently run-to-run (font hinting
        # drift), producing ~1480 borderline pixels at the default per-pixel
        # threshold while the layout, geometry, and JS-driven DAG label size
        # (--toc-label-px) are all bit-stable. Raising the per-pixel threshold to
        # 0.4 collapses that AA drift to zero; the small residual budget stays far
        # below the smallest real UI change to the pill or tree.
        assert_snapshot(page.screenshot(), threshold=0.4, max_diff_pixels=50)
