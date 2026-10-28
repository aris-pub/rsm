"""Interactive test for :toc: {:orientation: horizontal} (rsm-bjv).

The page carries both layouts of the text TOC graph. From 768px the left to
right one shows, below that the vertical one, so a phone never scrolls sideways.
The shown graph must behave like the vertical one: hover lights up the
prerequisite cone, keyboard focus outlines the node, and the root dot sits
inside the drawing where the edges meet.
"""

import pytest
from playwright.sync_api import Browser, Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

SHOWN = r"""() => {
  const de = document.documentElement;
  const shown = [...document.querySelectorAll('.toc.tree svg.toc-tree')]
    .filter((s) => getComputedStyle(s).display !== 'none');
  const svg = shown[0];
  const box = (el) => el.getBoundingClientRect();
  const node = (i) => box(svg.querySelector(`.toc-node[data-idx="${i}"] rect`));
  const dot = box(svg.querySelector('circle.toc-root-dot'));
  const sb = box(svg);
  return {
    count: shown.length,
    cls: svg.getAttribute('class'),
    // Rows: Introduction=0, Preliminaries=1, Random subsets=2, The embedding=3.
    prelim: [node(1).x, node(1).y],
    random: [node(2).x, node(2).y],
    svgW: sb.width, svgH: sb.height,
    dotInside: dot.left >= sb.left && dot.right <= sb.right
      && dot.top >= sb.top && dot.bottom <= sb.bottom,
    dotInViewport: dot.left >= 0 && dot.right <= de.clientWidth,
    hscroll: de.scrollWidth > de.clientWidth,
  };
}"""


def _open(browser: Browser, server: str, width: int, theme: str):
    ctx = browser.new_context(viewport={"width": width, "height": 900}, color_scheme=theme)
    page = ctx.new_page()
    page.goto(f"{server}/toc_horizontal.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_timeout(150)  # tocarcs.js settles label sizes after layout
    return ctx, page


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("width", [375, 767, 768, 1280])
def test_direction_by_width(browser: Browser, interactive_server: str, width: int, theme: str):
    ctx, page = _open(browser, interactive_server, width, theme)
    try:
        geo = page.evaluate(SHOWN)
        assert geo["count"] == 1, geo
        if width >= 768:
            assert "toc-tree-h" in geo["cls"], geo
            # A subsection sits to the right of its section.
            assert geo["random"][0] > geo["prelim"][0] + 10, geo
            assert geo["svgW"] > geo["svgH"], geo
        else:
            assert "toc-tree-v" in geo["cls"], geo
            # A subsection sits below its section.
            assert geo["random"][1] > geo["prelim"][1] + 10, geo
        assert geo["dotInside"], geo
        assert geo["dotInViewport"], geo
        assert not geo["hscroll"], geo
    finally:
        ctx.close()


def _faded(page: Page, sel: str) -> list[str]:
    return page.evaluate(
        "(s) => [...document.querySelectorAll(s + ' .toc-node.toc-faded')]"
        ".map((n) => n.dataset.idx).sort()",
        sel,
    )


def test_hover_highlights_the_same_cone_in_both_layouts(
    browser: Browser, interactive_server: str
):
    results = {}
    for width, sel in [(1280, "svg.toc-tree-h"), (375, "svg.toc-tree-v")]:
        ctx, page = _open(browser, interactive_server, width, "light")
        try:
            assert _faded(page, sel) == []
            # Hover "Lower bound" (row 5): its cone is The embedding, the root,
            # and the sections thm-main depends on.
            page.hover(f'.toc.tree {sel} .toc-node[data-idx="5"] rect')
            page.wait_for_function(
                "(s) => document.querySelector(s + ' .toc-node.toc-faded')",
                arg=f".toc.tree {sel}",
                timeout=2_000,
            )
            results[width] = _faded(page, f".toc.tree {sel}")
            page.mouse.move(2, 2)
            page.wait_for_function(
                "(s) => !document.querySelector(s + ' .toc-faded')",
                arg=f".toc.tree {sel}",
                timeout=2_000,
            )
        finally:
            ctx.close()
    assert results[1280], results
    assert "5" not in results[1280], results
    assert results[1280] == results[375], results


def _focus_outline(page: Page, sel: str, idx: str) -> str:
    node = f'.toc.tree {sel} .toc-node[data-idx="{idx}"]'
    page.evaluate("(s) => document.querySelector(s).focus()", node)
    # Step off and back by keyboard so :focus-visible matches.
    page.keyboard.press("Shift+Tab")
    page.keyboard.press("Tab")
    assert page.evaluate("(s) => document.activeElement === document.querySelector(s)", node)
    return page.evaluate(
        "(s) => getComputedStyle(document.querySelector(s)).outlineStyle", node
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_focus_outlines_nodes_and_lights_root_dot(
    browser: Browser, interactive_server: str, theme: str
):
    ctx, page = _open(browser, interactive_server, 1280, theme)
    try:
        assert _focus_outline(page, "svg.toc-tree-h", "3") == "solid"
        accent = page.evaluate(
            "() => { const p = document.createElement('span');"
            " p.style.color = 'var(--primary-700)'; document.body.appendChild(p);"
            " const c = getComputedStyle(p).color; p.remove(); return c; }"
        )
        root = page.evaluate(
            "() => document.querySelector('.toc.tree svg.toc-tree-h .toc-node.level-0')"
            ".dataset.idx"
        )
        _focus_outline(page, "svg.toc-tree-h", root)
        page.wait_for_function(
            "(a) => getComputedStyle(document.querySelector("
            "'.toc.tree svg.toc-tree-h circle.toc-root-dot')).fill === a",
            arg=accent,
            timeout=2_000,
        )
    finally:
        ctx.close()


def test_hidden_layout_is_not_in_tab_order(browser: Browser, interactive_server: str):
    # Only the shown graph's links take focus, so a keyboard reader does not tab
    # through the same TOC twice.
    ctx, page = _open(browser, interactive_server, 1280, "light")
    try:
        page.evaluate(
            "() => document.querySelector('.toc.tree svg.toc-tree-h .toc-node').focus()"
        )
        seen = set()
        for _ in range(30):
            page.keyboard.press("Tab")
            seen.add(
                page.evaluate(
                    "() => { const s = document.activeElement.closest('svg');"
                    " return s ? s.getAttribute('class') : ''; }"
                )
            )
        assert not any("toc-tree-v" in c for c in seen), seen
    finally:
        ctx.close()
