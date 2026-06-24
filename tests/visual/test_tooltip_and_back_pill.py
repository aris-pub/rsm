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
        assert_snapshot(page.screenshot())
