"""An :as-paragraph: figure is laid out as a paragraph: inside a remark its picture
starts where the remark's text starts and is never wider than the column, and no
element scrolls sideways, on a wide and on a phone screen."""

import pytest
from playwright.sync_api import Page

import rsm

pytestmark = pytest.mark.interactive

# Far wider than any column, so only the width cap keeps it inside.
WIDE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="3000" height="1500">'
    '<rect width="3000" height="1500" fill="teal"/></svg>'
)

SRC = """# Doc

## Sec

:remark: {
  :blockname: Hint
}

  Under inversion at $T$, the chain becomes a stack of congruent circles.

  :figure: {
    :as-paragraph:
    :path: wide.svg
    :alt: The chain and its image, a stack of congruent circles.
  }
  ::

::
"""

MEASURE = """() => {
  const rect = (e) => e.getBoundingClientRect();
  const para = document.querySelector(".remark .paragraph.hr:not(.hr-label) p");
  const fig = document.querySelector("figure.as-paragraph");
  const img = fig.querySelector("img");
  const column = fig.querySelector(":scope > .hr-content-zone");
  const scrollers = [...document.querySelectorAll("*")]
    .filter((e) => e.scrollWidth > e.clientWidth + 1)
    .filter((e) => ["auto", "scroll"].includes(getComputedStyle(e).overflowX))
    .map((e) => e.tagName + "." + e.className);
  const root = document.documentElement;
  return {
    paraLeft: rect(para).left,
    paraWidth: rect(para).width,
    imgLeft: rect(img).left,
    imgWidth: rect(img).width,
    columnWidth: rect(column).width,
    scrollers,
    pageScrolls: root.scrollWidth > root.clientWidth,
  };
}"""


@pytest.mark.parametrize("width", [1280, 375])
def test_as_paragraph_figure_fits_the_column(page: Page, tmp_path, monkeypatch, width):
    (tmp_path / "wide.svg").write_text(WIDE_SVG)
    monkeypatch.chdir(tmp_path)
    html = rsm.build(SRC, handrails=True, lint=False, standalone=True)
    out = tmp_path / "as-paragraph.html"
    out.write_text(html)

    page.set_viewport_size({"width": width, "height": 800})
    page.goto(out.as_uri(), wait_until="load")
    page.wait_for_timeout(300)
    m = page.evaluate(MEASURE)

    assert m["scrollers"] == [], m
    assert not m["pageScrolls"], m
    assert m["imgWidth"] > 0, m
    assert m["imgWidth"] <= m["columnWidth"] + 0.5, m
    assert m["imgWidth"] <= m["paraWidth"] + 0.5, m
    # The picture fills the column, so its left edge is the column's: the same as
    # the text of the paragraph above it.
    assert abs(m["imgLeft"] - m["paraLeft"]) <= 0.5, m
