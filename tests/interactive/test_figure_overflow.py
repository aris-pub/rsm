"""A figure must never grow a vertical scrollbar from a 1px overflow. CSS forces
overflow-y to 'auto' whenever overflow-x is 'auto', so the figure drops overflow-x
(wide content scrolls inside its child instead) and the table wrapper, which must
keep horizontal scroll, clips the vertical axis (rsm-0uy)."""

import pytest
from playwright.sync_api import Page

import rsm

pytestmark = pytest.mark.interactive

SRC = """# Overflow

:figure: {
  :path: assets/plot.svg
}
:caption: Caption with $\\tfrac12$ and $x_{j-1}^{2^j}$.
::

:table:

:tbody:

:tr: :td:one:: :td:two:: ::

::

::
"""


def _overflow(page: Page, selector: str, axis: str) -> str:
    return page.eval_on_selector(selector, f"e => getComputedStyle(e).overflow{axis}")


def test_figure_and_table_are_not_vertical_scroll_containers(page: Page, tmp_path):
    html = rsm.build(SRC, handrails=True, lint=False, standalone=True)
    out = tmp_path / "overflow.html"
    out.write_text(html)

    page.set_viewport_size({"width": 375, "height": 700})
    page.goto(out.as_uri(), wait_until="load")
    page.wait_for_timeout(300)

    # The figure clips its vertical axis, so a 1px vertical overflow (e.g. a tall
    # inline fraction in the caption) cannot show a scrollbar. overflow-x stays so
    # the figure keeps its block formatting context and horizontal scroll.
    assert _overflow(page, "figure", "Y") == "hidden"
    assert _overflow(page, "figure", "X") == "auto"
    assert _overflow(page, "figure > *:not(figcaption)", "X") == "auto"
    # The table wrapper keeps horizontal scroll for wide tables but clips Y
    # (clip downgrades to hidden alongside overflow-x:auto, as on the mathblock).
    assert _overflow(page, ".table-wrapper", "X") == "auto"
    assert _overflow(page, ".table-wrapper", "Y") == "hidden"


WIDE_TABLE = """# T

:table:

:tbody:

:tr: :td:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:: :td:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb:: :td:cccccccccccccccccccccccccccccccccc:: ::

::

::
"""


def test_wide_content_scrolls_horizontally_without_page_scroll(page: Page, tmp_path):
    """Clipping the vertical axis must not remove horizontal scroll: a table
    wider than the column still scrolls sideways inside its wrapper, and the page
    itself never scrolls horizontally (rsm-0uy)."""
    html = rsm.build(WIDE_TABLE, handrails=True, lint=False, standalone=True)
    out = tmp_path / "wide.html"
    out.write_text(html)

    page.set_viewport_size({"width": 375, "height": 700})
    page.goto(out.as_uri(), wait_until="load")
    page.wait_for_timeout(300)

    box = page.eval_on_selector(
        ".table-wrapper", "e => ({sw: e.scrollWidth, cw: e.clientWidth})"
    )
    assert box["sw"] > box["cw"], box  # content overflows, so it is scrollable
    page.eval_on_selector(".table-wrapper", "e => { e.scrollLeft = 9999; }")
    assert page.eval_on_selector(".table-wrapper", "e => e.scrollLeft") > 0

    # The page body never scrolls horizontally.
    assert page.evaluate(
        "() => document.documentElement.scrollWidth <= document.documentElement.clientWidth"
    )
