"""Interactive test for the TOC graph root dot (rsm-kay).

The TOC dependency-graph root stands in for the title/abstract. It used to be a
filled accent box carrying the title (or a "Top" marker on narrow screens). Now
it is a small muted dot: no box, no label, still a link to the top of the
manuscript with the title as its accessible name, and it takes the accent colour
on hover and keyboard focus. The same root appears in the body TOC tree and in
the sidebar Contents graph; both are checked here, at the narrowest and a wide
viewport, in both themes.
"""

import pytest
from playwright.sync_api import Browser, Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

# The accent colour (--primary-700) resolved in the page's current theme, read
# off a throwaway element so the test never hard-codes a theme's rgb.
ACCENT = """() => {
  const probe = document.createElement('span');
  probe.style.color = 'var(--primary-700)';
  document.body.appendChild(probe);
  const c = getComputedStyle(probe).color;
  probe.remove();
  return c;
}"""

# Shape, link target, accessible name, and resting fill of a root dot, given the
# SVG that holds it. Also whether the page scrolls sideways (a long title must
# not overflow now that the root is a dot).
ROOT = r"""(svgSel) => {
  const de = document.documentElement;
  const svg = document.querySelector(svgSel);
  const root = svg.querySelector('.toc-node.level-0');
  const dot = root.querySelector('circle');
  return {
    hasDot: !!dot,
    hasRect: !!root.querySelector('rect'),
    hasText: !!root.querySelector('text'),
    href: root.getAttribute('href'),
    aria: root.getAttribute('aria-label'),
    restFill: dot ? getComputedStyle(dot).fill : null,
    hscroll: de.scrollWidth > de.clientWidth,
  };
}"""


def _check_dot(page: Page, svg_sel: str, title: str) -> None:
    geo = page.evaluate(ROOT, svg_sel)
    assert geo["hasDot"], geo
    assert not geo["hasRect"], geo  # no box
    assert not geo["hasText"], geo  # no label
    assert geo["href"] == "#", geo  # links to the top of the manuscript
    assert geo["aria"] == title, geo  # title is the accessible name
    assert not geo["hscroll"], geo

    accent = page.evaluate(ACCENT)
    assert geo["restFill"] != accent, geo  # muted at rest, not the accent

    # Hover turns the dot the accent colour.
    page.hover(f"{svg_sel} .toc-node.level-0 circle")
    page.wait_for_function(
        "(a) => { const s = document.querySelector(a[0]);"
        " return getComputedStyle(s.querySelector("
        "'.toc-node.level-0 circle')).fill === a[1]; }",
        arg=[svg_sel, accent],
        timeout=2_000,
    )
    # Move away so the resting colour returns.
    page.mouse.move(5, 5)
    page.wait_for_function(
        "(a) => { const s = document.querySelector(a[0]);"
        " return getComputedStyle(s.querySelector("
        "'.toc-node.level-0 circle')).fill !== a[1]; }",
        arg=[svg_sel, accent],
        timeout=2_000,
    )

    # Keyboard focus also turns it the accent colour (focus-visible). Land on the
    # dot with a real Tab (a programmatic focus after a click would not count as
    # keyboard modality, so :focus-visible would not match): focus it, step off
    # with Shift+Tab, then Tab back onto it by keyboard.
    page.evaluate(
        "(s) => document.querySelector(s + ' .toc-node.level-0').focus()", svg_sel
    )
    page.keyboard.press("Shift+Tab")
    page.keyboard.press("Tab")
    assert page.evaluate(
        "(s) => document.activeElement === document.querySelector("
        "s + ' .toc-node.level-0')",
        svg_sel,
    )
    # The fill transitions (0.12s), so wait for it to settle on the accent.
    page.wait_for_function(
        "(a) => { const s = document.querySelector(a[0]);"
        " return getComputedStyle(s.querySelector("
        "'.toc-node.level-0 circle')).fill === a[1]; }",
        arg=[svg_sel, accent],
        timeout=2_000,
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("width", [375, 1280])
def test_body_toc_root_is_a_dot(
    browser: Browser, interactive_server: str, width: int, theme: str
):
    ctx = browser.new_context(
        viewport={"width": width, "height": 800}, color_scheme=theme
    )
    try:
        page = ctx.new_page()
        # A deliberately long title: the dot must not overflow the narrow screen.
        page.goto(f"{interactive_server}/toc_root_clip.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        page.wait_for_timeout(150)  # tocarcs.js settles label sizes after layout
        _check_dot(
            page,
            ".toc.tree svg.toc-tree",
            "A Very Long Manuscript Title That Overruns the Narrow Tree Drawing Area",
        )
    finally:
        ctx.close()


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("width", [375, 1280])
def test_sidebar_contents_root_is_a_dot(
    browser: Browser, interactive_server: str, width: int, theme: str
):
    # The strip is a left margin on desktop and a bottom bar on a phone; the
    # Contents button opens the graph in both.
    ctx = browser.new_context(
        viewport={"width": width, "height": 800}, color_scheme=theme
    )
    try:
        page = ctx.new_page()
        page.goto(f"{interactive_server}/sidebar.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        view = "contents" if width >= 768 else "document"
        page.click(f'.rail-strip-btn[data-view="{view}"]')
        page.wait_for_selector(".proof-rail.open .rail-doc-map", timeout=5_000)
        page.wait_for_timeout(150)
        _check_dot(page, ".rail-doc-map svg.toc-tree", "Sidebar Demo")
    finally:
        ctx.close()
