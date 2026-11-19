""":title: values hold inline markup (rsm-abg).

The grammar side is covered by tree-sitter-rsm/test/corpus/titles.txt. These
tests check the built page and the plain-text copy of each title."""

import logging
import re

import pytest

import rsm
from rsm import nodes
from rsm.app import ParserApp

MATH_X2 = r'<span class="math">\(x^2\)</span>'


def _render(src: str, handrails: bool = False) -> str:
    return rsm.render(src, handrails=handrails)


def _flat(html: str) -> str:
    return re.sub(r"\s+", " ", html)


def _tree(src: str) -> nodes.Manuscript:
    return ParserApp(plain=src).run()


@pytest.mark.parametrize(
    "src",
    [
        ":theorem: {:title: Uses $x^2$ here}\n  B.\n::\n",
        ":theorem: {:title: Uses $x^2$ here, :label: t}\n  B.\n::\n",
        ":theorem:\n  {\n  :title: Uses $x^2$ here\n  :label: t\n  }\n  B.\n::\n",
        ":theorem:\n  {\n  :title: Uses $x^2$ here   \n  :label: t\n  }\n  B.\n::\n",
    ],
    ids=["one-line", "one-line-then-key", "multi-line", "trailing-spaces"],
)
@pytest.mark.parametrize("handrails", [False, True])
def test_math_in_theorem_title(src, handrails):
    html = _flat(_render(src, handrails))
    assert f'<span class="span desc">Uses {MATH_X2} here</span>' in html
    assert "CST error" not in html
    assert "<p>B.</p>" in html


def test_theorem_title_with_math_keeps_its_label():
    html = _render(
        ":theorem:\n  {\n  :title: Uses $x^2$ here\n  :label: t\n  }\n  B.\n::\n\n"
        "See :ref:t::.\n"
    )
    assert 'href="#t">Theorem 1</a>' in html


@pytest.mark.parametrize(
    "title, inner",
    [
        ("A *b* c", 'A <span class="span"><em>b</em></span> c'),
        ("Uses :code:x:: here", 'Uses <span class="code"><code>x</code></span> here'),
        ("A :span:{:strong:}b:: c", 'A <span class="span"><strong>b</strong></span> c'),
    ],
    ids=["emph", "code-tag", "span"],
)
def test_other_markup_in_theorem_title(title, inner):
    html = _flat(_render(f":theorem: {{:title: {title}}}\n  B.\n::\n"))
    assert f'<span class="span desc">{inner}</span>' in html


def test_plain_theorem_title_is_unchanged():
    html = _flat(_render(":theorem: {:title: Plain words}\n  B.\n::\n"))
    assert '<span class="span desc">Plain words</span>' in html
    thm = _tree(":theorem: {:title: Plain words}\n  B.\n::\n").first_of_type(nodes.Theorem)
    assert thm.title == "Plain words"
    assert thm.title_nodes == []


def test_comma_in_one_line_block_meta_title_is_kept():
    thm = _tree(":theorem: {:title: A, b, :label: t}\n  B.\n::\n").first_of_type(
        nodes.Theorem
    )
    assert thm.title == "A, b"
    assert thm.label == "t"


def test_plain_copy_of_a_theorem_title():
    thm = _tree(":theorem: {:title: Uses $x^2$ here}\n  B.\n::\n").first_of_type(
        nodes.Theorem
    )
    assert thm.title == "Uses x^2 here"


@pytest.mark.parametrize(
    "src",
    [
        ":paragraph: {:title: Uses $x^2$ here} Body.\n",
        ":paragraph: {:title: Uses $x^2$ here, :label: p} Body.\n",
        ":paragraph: {:label: p, :title: Uses $x^2$ here} Body.\n",
    ],
    ids=["alone", "then-key", "after-key"],
)
def test_math_in_paragraph_title(src):
    html = _flat(_render(src))
    assert f'<span class="pg-label"> Uses {MATH_X2} here. </span>' in html
    assert "Body.</p>" in html
    assert "CST error" not in html


def test_colon_in_paragraph_title():
    html = _flat(_render(":paragraph: {:title: Ratio 3:1} Body.\n"))
    assert '<span class="pg-label"> Ratio 3:1. </span>' in html


def test_comma_ends_a_paragraph_title(caplog):
    with caplog.at_level(logging.WARNING):
        _render(":paragraph: {:title: A, b, :label: p} Body.\n")
    assert any(r.levelname in ("WARNING", "ERROR") for r in caplog.records)


def test_math_in_section_tag_title():
    html = _render(
        ":section:\n  {\n  :title: The case $k=2$\n  :label: s\n  }\n\nB.\n"
    )
    assert r'<h2>1. The case <span class="math">\(k=2\)</span></h2>' in html


@pytest.mark.parametrize(
    "tag, title",
    [
        (":ref:", "See :ref:lbl:: here"),
        (":rawhtml:", "See :rawhtml:{:alt: s} <b>s</b> :: here"),
    ],
)
def test_links_and_raw_html_are_left_out_of_a_title(tag, title, caplog):
    with caplog.at_level(logging.WARNING):
        html = _flat(_render(f":theorem: {{:title: {title}}}\n  B.\n::\n"))
    assert '<span class="span desc">See here</span>' in html
    assert "<b>s</b>" not in html
    assert any(
        r.levelname == "ERROR" and tag in r.getMessage() and "title" in r.getMessage()
        for r in caplog.records
    )


def test_markup_title_is_escaped():
    html = _flat(_render(":theorem: {:title: a<b $x$ & c}\n  B.\n::\n"))
    assert (
        r'<span class="span desc">a&lt;b <span class="math">\(x\)</span> &amp; c</span>'
        in html
    )


def test_other_text_keys_stay_plain():
    html = _render(":paragraph: {:title: T} Body.\n\n:author: {:name: A $x$ B} ::\n")
    assert '<span class="math">' not in html
