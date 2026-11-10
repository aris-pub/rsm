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


CLICK_SRC = """# Doc

## Sec

Some text before the widget.

:html: {
  :label: w
  :as-paragraph:
}

<div id="widget" style="height: 120px; background: teal"><button id="widget-button">Go</button></div>

::
"""


def _load_click_doc(page: Page, tmp_path) -> None:
    html = rsm.build(CLICK_SRC, handrails=True, lint=False, standalone=True)
    out = tmp_path / "as-paragraph-click.html"
    out.write_text(html)
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(out.as_uri(), wait_until="load")
    page.wait_for_function("() => window.__rsmInitialized === true", timeout=10_000)


def test_click_in_as_paragraph_widget_does_not_select_it(page: Page, tmp_path):
    # A plain figure's body cannot take focus, so a click in it selects nothing.
    # An :as-paragraph: block is itself a focusable handrail, but a click on its
    # content (a widget being used) must not select it either.
    _load_click_doc(page, tmp_path)
    page.locator("#widget").click(position={"x": 400, "y": 80})
    assert page.evaluate("() => document.querySelector('figure.as-paragraph').matches(':focus')") is False


def test_focusable_element_in_as_paragraph_widget_still_takes_focus(page: Page, tmp_path):
    _load_click_doc(page, tmp_path)
    page.locator("#widget-button").click()
    assert page.evaluate("() => document.activeElement.id") == "widget-button"


def test_click_on_paragraph_still_selects_it(page: Page, tmp_path):
    _load_click_doc(page, tmp_path)
    para = page.locator(".paragraph.hr", has_text="Some text before").first
    para.locator("p").click()
    assert para.evaluate("el => el.matches(':focus')") is True


SELECT_SRC = """# Doc

## Sec

:html: {
  :label: w
  :as-paragraph:
}

<p id="widget-text">Text inside a widget that the reader can select.</p>

::
"""


def test_text_in_as_paragraph_widget_can_be_selected(page: Page, tmp_path):
    html = rsm.build(SELECT_SRC, handrails=True, lint=False, standalone=True)
    out = tmp_path / "as-paragraph-select.html"
    out.write_text(html)
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(out.as_uri(), wait_until="load")
    page.wait_for_function("() => window.__rsmInitialized === true", timeout=10_000)
    box = page.locator("#widget-text").bounding_box()
    page.mouse.move(box["x"] + 2, box["y"] + box["height"] / 2)
    page.mouse.down()
    page.mouse.move(box["x"] + box["width"] - 2, box["y"] + box["height"] / 2, steps=8)
    page.mouse.up()
    assert "the reader can select" in page.evaluate("() => String(window.getSelection())")
    assert page.evaluate("() => document.querySelector('figure.as-paragraph').matches(':focus')") is False


NESTED_SRC = """# Doc

## Sec

:remark: {
  :blockname: Hints
}

  :html: {
    :label: w
    :as-paragraph:
  }

  <div id="nested-widget" style="height: 120px; background: teal"></div>

  ::

::
"""


def test_click_in_nested_as_paragraph_widget_selects_no_block(page: Page, tmp_path):
    # With the widget's block unable to take focus, a press must not hand the
    # focus to the block around it either.
    html = rsm.build(NESTED_SRC, handrails=True, lint=False, standalone=True)
    out = tmp_path / "as-paragraph-nested.html"
    out.write_text(html)
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(out.as_uri(), wait_until="load")
    page.wait_for_function("() => window.__rsmInitialized === true", timeout=10_000)
    page.locator("#nested-widget").click(position={"x": 200, "y": 60})
    assert page.evaluate("() => document.activeElement.closest('.hr') === null"), page.evaluate(
        "() => document.activeElement.className"
    )
