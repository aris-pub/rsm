"""CST error text keeps its error span when text sits next to it (rsm-d2v)."""

import re
from pathlib import Path

import pytest

import rsm

ERROR_SPAN = re.compile(r'<span class="error"[^>]*>\[CST error at [^\]]*\]</span>')


class MockAssetResolver:
    def resolve_asset(self, path: str) -> str | None:
        return {"widget.html": "<div>Widget content</div>"}.get(path)


PARAGRAPH = "Some text :bogus: more text.\n"

FIGURE = """\
:figure: {
  :path: a.png
}
:caption: Some text :bogus: more text.
::
"""

WIDGET = """\
:html: {
  :path: widget.html
}
:caption: Some text :bogus: more text.
::
"""


def _render(src: str, handrails: bool) -> str:
    return rsm.render(src, handrails=handrails, asset_resolver=MockAssetResolver())


def _figcaption(html: str) -> str:
    start = html.find("<figcaption")
    end = html.find("</figcaption>")
    assert start != -1 and end != -1, html
    return html[start:end]


@pytest.mark.parametrize("handrails", [False, True], ids=["plain", "handrails"])
def test_error_between_text_in_paragraph(handrails):
    html = _render(PARAGRAPH, handrails)
    paragraph = html[html.find("<p") : html.find("</p>")]
    assert ERROR_SPAN.search(paragraph), paragraph
    assert "Some text" in paragraph
    assert "more text." in paragraph


@pytest.mark.parametrize("handrails", [False, True], ids=["plain", "handrails"])
def test_error_in_figure_caption(handrails):
    caption = _figcaption(_render(FIGURE, handrails))
    assert ERROR_SPAN.search(caption), caption
    assert "Some text" in caption
    assert "more text." in caption


@pytest.mark.parametrize("handrails", [False, True], ids=["plain", "handrails"])
def test_error_in_widget_caption(handrails):
    caption = _figcaption(_render(WIDGET, handrails))
    assert ERROR_SPAN.search(caption), caption
    assert "Some text" in caption
    assert "more text." in caption


def test_error_text_keeps_spaces_around_it():
    html = _render(PARAGRAPH, False)
    paragraph = html[html.find("<p") : html.find("</p>")]
    text = re.sub(r"<[^>]+>", "", paragraph.split(">", 1)[1])
    assert re.search(r"Some text \[CST error at [^\]]*\] bogus: more text\.", text), text


def test_error_rule_sets_red_text():
    css = (Path(rsm.__file__).parent.parent / "braiid" / "braiid.css").read_text()
    block = css[css.find("/* General utilities */") :]
    block = block[: block.find("}\n}") + 3]
    rule = re.search(r"\.error\s*\{([^}]*)\}", block)
    assert rule, block
    assert re.search(r"(?<![-\w])color:\s*var\(--error-900\)", rule.group(1)), rule.group(1)
