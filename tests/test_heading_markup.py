"""Headings hold inline markup up to the end of their line (rsm-abg).

The grammar side is covered by tree-sitter-rsm/test/corpus/headings.txt. These
tests check the built page: the heading shows the markup, the rest of the line
stays in the heading, and places that only take plain text get the title with
the math written as its TeX source."""

import logging
import re

import pytest

import rsm
from rsm import nodes

MATH_K = r'<span class="math">\(k=2\)</span>'


def _render(src: str, **kw) -> str:
    return rsm.render(src, handrails=False, **kw)


def _parse(src: str) -> nodes.Manuscript:
    return rsm.tsparser.TSParser().parse(src)


@pytest.mark.parametrize(
    "src",
    [
        "## The case $k=2$ here\n\nBar.\n",
        "## The case $k=2$ here",
        "## The case $k=2$ here   \n\nBar.\n",
        "## The case $k=2$ here\r\n\r\nBar.\r\n",
        "## The case $k=2$ here\nBar.\n",
        "## The case $k=2$ here % a comment\n\nBar.\n",
    ],
    ids=["blank-line", "eof", "trailing-spaces", "crlf", "next-line", "comment"],
)
def test_math_in_section_heading(src):
    html = _render(src)
    assert f"<h2>1. The case {MATH_K} here</h2>" in html
    assert "CST error" not in html


def test_heading_markup_does_not_leak_into_body():
    html = _render("## The case $k=2$ here\n\nBar.\n")
    body = html[html.index("</h2>") :]
    assert "k=2" not in body
    assert "<p>Bar.</p>" in body


@pytest.mark.parametrize(
    "src, inner",
    [
        ("## A *bold* word\n\nBar.\n", "A <span class=\"span\"><em>bold</em></span> word"),
        ("## A **strong** word\n\nBar.\n", "A <span class=\"span\"><strong>strong</strong></span> word"),
        ("## Uses `x` here\n\nBar.\n", 'Uses <span class="code"><code>x</code></span> here'),
        ("## Uses :code:x:: here\n\nBar.\n", 'Uses <span class="code"><code>x</code></span> here'),
        ("## $x$ first\n\nBar.\n", r'<span class="math">\(x\)</span> first'),
        ("## $x$ and $y$\n\nBar.\n", r'<span class="math">\(x\)</span> and <span class="math">\(y\)</span>'),
    ],
    ids=["emph", "strong", "backtick", "code-tag", "math-first", "two-math"],
)
def test_other_markup_in_section_heading(src, inner):
    html = _render(src)
    assert f"<h2>1. {inner}</h2>" in html


def test_math_in_subsection_and_subsubsection():
    html = _render("## A\n\n### Sub $x$ here\n\n#### Subsub $y$ here\n\nBar.\n")
    assert r'<h3>1.1. Sub <span class="math">\(x\)</span> here</h3>' in html
    assert r'<h4>1.1.1. Subsub <span class="math">\(y\)</span> here</h4>' in html


def test_math_in_document_title():
    html = _render("# Doc $x$ here\n\n## A\n\nBar.\n")
    assert r'<h1>Doc <span class="math">\(x\)</span> here</h1>' in html


def test_heading_with_markup_and_meta_on_next_line():
    html = _render("## The case $k=2$\n{\n  :label: sec-k\n}\n\nSee :ref:sec-k::.\n")
    assert f"<h2>1. The case {MATH_K}</h2>" in html
    assert 'href="#sec-k">Section 1</a>' in html


def test_heading_with_markup_and_meta_on_same_line():
    html = _render("## The case $k=2$ {:label: sec-k}\n\nSee :ref:sec-k::.\n")
    assert f"<h2>1. The case {MATH_K}</h2>" in html
    assert 'href="#sec-k">Section 1</a>' in html


def test_plain_title_copy_has_tex_source():
    tree = _parse("# Doc $x$ here\n\n## The case $k=2$ here\n\nBar.\n")
    assert tree.title == "Doc x here"
    sec = next(tree.traverse(nodeclass=nodes.Section))
    assert sec.title == "The case k=2 here"


def test_plain_heading_title_is_unchanged():
    tree = _parse("## Plain title\n\nBar.\n")
    sec = next(tree.traverse(nodeclass=nodes.Section))
    assert sec.title == "Plain title"
    assert sec.title_nodes == []


def test_toc_entry_shows_markup():
    html = _render(":toc: ::\n\n## The case $k=2$ here\n\nBar.\n")
    toc = html[html.index('<ul class="contents"') :]
    assert re.search(
        r'<a class="reference" href="#sec-1">1\. The case '
        + re.escape(MATH_K)
        + r" here</a>",
        toc,
    )


def test_sidebar_list_uses_plain_title():
    html = rsm.render(
        ":toc: ::\n\n## The case $k=2$ here\n\nBar.\n", handrails=True, sidebar=True
    )
    rail = html[html.index("rail-doc-map") :]
    assert '<a class="reference" href="#sec-1">1. The case k=2 here</a>' in rail


def test_markup_title_is_escaped():
    html = _render("## a<b $x$ & c\n\nBar.\n")
    assert r'<h2>1. a&lt;b <span class="math">\(x\)</span> &amp; c</h2>' in html


def test_unclosed_dollar_in_heading_is_still_an_error():
    html = _render("## Costs in $ and more\n\nBar.\n")
    assert "CST error" in html


def test_heading_and_toc_both_render_math_before_punctuation():
    # Handrail pages keep math and the punctuation after it together, and doing
    # so changes the title's nodes. The TOC entry must still come out whole.
    html = rsm.render(
        ":toc: ::\n\n## Case $x$. More\n\nBar.\n", handrails=True
    ).replace("\n", "")
    wrapped = (
        r'<span class="inline-wrapper"><span class="math">\(x\)</span>'
        r"<span>.</span></span> More"
    )
    assert html.count(wrapped) == 2
    assert html.count('<span class="inline-wrapper">') == html.count(
        "<span>.</span></span>"
    )


@pytest.mark.parametrize(
    "tag, src",
    [
        (":ref:", "## See :ref:lbl:: here\n\nText.\n"),
        (":cite:", "## See :cite:k:: here\n\nText.\n"),
        (":url:", "## See :url:https://a.org:: here\n\nText.\n"),
        (":note:", "## See :note:n:: here\n\nText.\n"),
        (":rawhtml:", "## See :rawhtml:{:alt: s} <b>s</b> :: here\n\nText.\n"),
    ],
)
def test_links_and_raw_html_are_left_out_of_a_heading(tag, src, caplog):
    with caplog.at_level(logging.WARNING):
        html = _render(src)
    assert "<h2>1. See here</h2>" in html
    assert "CST error" not in html
    assert "<b>s</b>" not in html
    assert "<p>Text.</p>" in html
    assert any(
        r.levelname == "ERROR" and tag in r.getMessage() and "heading" in r.getMessage()
        for r in caplog.records
    )


def test_heading_with_math_and_a_ref_keeps_the_math(caplog):
    with caplog.at_level(logging.WARNING):
        html = _render("## Case $x$ :ref:lbl:: here\n\nText.\n")
    assert r'<h2>1. Case <span class="math">\(x\)</span> here</h2>' in html


def test_plain_heading_with_crlf_line_endings():
    # The grammar's corpus files are stored with LF endings, so CRLF is
    # checked here.
    tree = _parse("## Foo\r\n\r\nBar.\r\n")
    sec = next(tree.traverse(nodeclass=nodes.Section))
    assert sec.title == "Foo"
    assert "CST error" not in _render("## Foo\r\n\r\nBar.\r\n")
