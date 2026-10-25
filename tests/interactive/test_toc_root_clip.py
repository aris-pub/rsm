"""Interactive test for the body TOC tree root label on narrow screens (rsm-tj7).

The root node of the body TOC tree carries the whole manuscript title. The label
is drawn at a constant on-screen size, so a long title used to be wider than a
narrow screen and spilled out of the tree's box (clipped at the edges). The fix
collapses the root to the short "Top" marker when the title is too wide, keeping
the full title in the tooltip and accessible name. These checks confirm the
rendered result at the narrowest and a wide viewport, in both themes: the root
label sits inside the tree's box and the page does not scroll sideways.
"""

import pytest
from playwright.sync_api import Browser

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

LONG_TITLE = "A Very Long Manuscript Title That Overruns the Narrow Tree Drawing Area"

# Read the rendered geometry once the tree is laid out and labels are stabilized.
GEOMETRY = r"""
() => {
  const de = document.documentElement;
  const svg = document.querySelector('.toc.tree svg.toc-tree');
  const box = svg.getBoundingClientRect();
  const root = svg.querySelector('.toc-node.level-0');
  const text = root.querySelector('.toc-secnum').getBoundingClientRect();
  return {
    hscroll: de.scrollWidth > de.clientWidth,
    label: root.querySelector('.toc-secnum').textContent,
    aria: root.getAttribute('aria-label'),
    // A small tolerance absorbs sub-pixel rounding in the bounding boxes.
    overflow: (text.left < box.left - 0.5) || (text.right > box.right + 0.5),
  };
}
"""


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("width", [375, 1280])
def test_long_root_label_stays_inside_box(
    browser: Browser, interactive_server: str, width: int, theme: str
):
    ctx = browser.new_context(
        viewport={"width": width, "height": 800}, color_scheme=theme
    )
    try:
        page = ctx.new_page()
        page.goto(f"{interactive_server}/toc_root_clip.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        # tocarcs.js stabilizes label sizes after layout, so wait a frame first.
        page.wait_for_timeout(150)
        geo = page.evaluate(GEOMETRY)
        assert geo["label"] == "Top", geo
        assert geo["aria"] == LONG_TITLE, geo
        assert geo["overflow"] is False, geo
        assert geo["hscroll"] is False, geo
    finally:
        ctx.close()
