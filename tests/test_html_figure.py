"""HTML in RSM (rsm-7yj): a :figure: takes HTML from a file or from an
:htmlblock: inside it, :html: is inline raw HTML, and :htmlblock: is a block of
raw HTML. The grammar side is in tree-sitter-rsm/test/corpus/htmlblock.txt and
rawhtml.txt."""

import logging
import re

import pytest

import rsm
from rsm import nodes
from rsm.app import ParserApp
from rsm.pandoc import PandocTranslator


def _render(src: str, handrails: bool = False) -> str:
    return rsm.render(src, handrails=handrails)


def _tree(src: str) -> nodes.Manuscript:
    return ParserApp(plain=src).run()


def _figure_tag(html: str) -> str:
    return re.search(r"<figure[^>]*>", html).group(0)


FIG_BLOCK = (
    "## S\n\n:figure: {:label: fig-a :alt: A canvas.}\n\n"
    '  :htmlblock:\n  <canvas id="c"></canvas>\n  ::\n\n'
    "  :caption: A canvas.\n\n::\n\nSee :ref:fig-a::.\n"
)


@pytest.mark.parametrize("handrails", [False, True])
def test_figure_with_an_html_block(handrails):
    html = _render(FIG_BLOCK, handrails)
    assert '<canvas id="c"></canvas>' in html
    assert "Figure 1.1" in html
    assert "Widget" not in html
    assert 'href="#fig-a"' in html and ">Figure 1.1</a>" in html
    assert "CST error" not in html


def test_figure_with_an_html_block_is_marked_as_holding_html():
    # Reference previews swap figures marked this way for a still or the alt
    # text (tooltips.js), and pages that are not HTML do the same.
    tag = _figure_tag(_render(FIG_BLOCK, handrails=True))
    assert re.search(r'class="[^"]*\bhtml\b', tag), tag
    assert 'data-alt="A canvas."' in tag


def test_figure_with_an_html_file_is_marked_as_holding_html():
    tag = _figure_tag(
        _render("## S\n\n:figure: {:path: widget.html :static: w.png}\n::\n", True)
    )
    assert re.search(r'class="[^"]*\bhtml\b', tag), tag
    assert "data-static=" in tag


def test_figure_with_an_image_is_not_marked_as_holding_html():
    tag = _figure_tag(_render("## S\n\n:figure: {:path: a.png}\n::\n", True))
    assert not re.search(r'class="[^"]*\bhtml\b', tag), tag


def test_html_block_body_is_not_escaped_or_wrapped():
    html = _render(FIG_BLOCK, handrails=True)
    body = html[html.index("<canvas") - 200 : html.index("</canvas>")]
    assert "<p>" not in body
    assert 'class="paragraph' not in body
    assert "&lt;canvas" not in html


@pytest.mark.parametrize("handrails", [False, True])
def test_html_block_on_its_own(handrails):
    src = (
        "## S\n\nBefore.\n\n:htmlblock: {:alt: A rule.}\n"
        '<div id="x" title="a: b">$x$ *y* &amp;</div>\n::\n\nAfter.\n'
    )
    html = _render(src, handrails)
    assert '<div id="x" title="a: b">$x$ *y* &amp;</div>' in html
    assert "<p>Before.</p>" in html and "<p>After.</p>" in html
    assert "Figure" not in html
    assert "CST error" not in html
    # The body is written as is, with no paragraph or handrail around it.
    i = html.index('<div id="x"')
    assert "hr-content-zone" not in html[i - 120 : i]
    assert 'class="paragraph' not in html[i - 120 : i]


def test_html_block_alt_is_a_hidden_fallback():
    src = ":htmlblock: {:alt: A diagram of $x$}\n<div>live</div>\n::\n"
    html = _render(src)
    alt = re.search(r'<div class="rawhtml-alt" hidden>(.*?)</div>', html, re.S)
    assert alt, html
    assert re.search(r'<span class="math"[^>]*>\\\(x\\\)</span>', alt.group(1))


def test_html_block_is_not_numbered():
    tree = _tree(":htmlblock:\n<div>x</div>\n::\n\n:figure: {:path: a.png :label: f}\n::\n")
    fig = next(tree.traverse(nodeclass=nodes.Figure))
    assert fig.full_number == "1"


def test_inline_html():
    html = _render("A :html:{:alt: bold} <b>bold</b> :: B.\n")
    assert "<b>bold</b>" in html
    assert '<span class="rawhtml-alt" hidden>bold</span>' in html


def test_rawhtml_is_no_longer_a_tag(caplog):
    with caplog.at_level(logging.WARNING):
        html = _render("A :rawhtml: <b>bold</b> :: B.\n")
    assert "<b>bold</b>" not in html


def test_html_is_no_longer_a_block(caplog):
    with caplog.at_level(logging.WARNING):
        html = _render("## S\n\n:html: {\n  :path: widget.html\n}\n::\n")
    assert "CST error" in html


def _pandoc_blocks(src: str) -> str:
    return str(PandocTranslator().translate(_tree(src))["blocks"])


def test_pandoc_figure_with_html_uses_its_static_image():
    out = _pandoc_blocks(
        "## S\n\n:figure: {:path: widget.html :static: w.png}\n  :caption: C.\n::\n"
    )
    assert "w.png" in out
    assert "widget.html" not in out


def test_pandoc_figure_with_html_and_no_static_says_see_online():
    out = _pandoc_blocks(FIG_BLOCK)
    assert "see online version" in out
    assert "canvas" not in out


def test_pandoc_html_block_uses_its_alt():
    out = _pandoc_blocks(":htmlblock: {:alt: A rule.}\n<hr>\n::\n")
    assert "'rule.'" in out
    assert "<hr>" not in out


def test_html_block_in_a_figure_sits_with_the_static_image():
    # The static view toggle (handrails.js) and print (braiid.css) swap every
    # sibling of the static image in the figure's content zone for the image.
    src = (
        "## S\n\n:figure: {:static: w.png}\n\n"
        '  :htmlblock:\n  <canvas id="c"></canvas>\n  ::\n\n  :caption: C.\n\n::\n'
    )
    html = _render(src, handrails=True)
    zone = html[html.index('<div class="hr-content-zone">') :]
    zone = zone[: zone.index("static-fallback")]
    assert '<canvas id="c"></canvas>' in zone
    assert html.count('<canvas id="c">') == 1
