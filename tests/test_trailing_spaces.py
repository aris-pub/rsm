"""Spaces and tabs at the end of a line do not change how the next line parses (rsm-ryha).

Before the fix, spaces after a closing :: or $$ made the first word of the next
paragraph a parse error, even with a blank line in between.
"""

import pytest

import rsm
from rsm import nodes


def _manuscript(src):
    return rsm.transformer.Transformer().transform(rsm.tsparser.TSParser().parse(src))


def _of_type(manuscript, cls):
    return [n for n in manuscript.traverse() if isinstance(n, cls)]


def _paragraph_text(manuscript):
    return [
        "".join(t.text for t in p.traverse() if type(t) is nodes.Text).strip()
        for p in _of_type(manuscript, nodes.Paragraph)
        if not isinstance(p, (nodes.Caption, nodes.Item))
    ]


def _check(src, paragraphs):
    rsm.render(src, handrails=False, source_offsets=False, strict=True)
    m = _manuscript(src)
    assert not _of_type(m, nodes.Error)
    assert _paragraph_text(m)[-len(paragraphs) :] == paragraphs


@pytest.mark.parametrize("trail", ["  ", "\t", " \t "])
def test_theorem_closed_with_trailing_spaces(trail):
    src = f":theorem:\n\nfoo\n\n::{trail}\n\nNext paragraph here.\n"
    _check(src, ["foo", "Next paragraph here."])
    (thm,) = _of_type(_manuscript(src), nodes.Theorem)
    assert "Next" not in "".join(t.text for t in thm.traverse() if type(t) is nodes.Text)


@pytest.mark.parametrize("trail", ["  ", "\t"])
def test_display_math_closed_with_trailing_spaces(trail):
    src = f"$$\nx\n$${trail}\n\nNext paragraph here.\n"
    _check(src, ["Next paragraph here."])
    assert len(_of_type(_manuscript(src), nodes.MathBlock)) == 1


def test_mathblock_closed_with_trailing_spaces():
    src = ":mathblock:\nx\n::  \n\nNext paragraph here.\n"
    _check(src, ["Next paragraph here."])
    assert len(_of_type(_manuscript(src), nodes.MathBlock)) == 1


@pytest.mark.parametrize("trail", ["  ", "\t"])
def test_codeblock_closed_with_trailing_spaces(trail):
    src = f":codeblock:\nx = 1\n::{trail}\n\nNext paragraph here.\n"
    _check(src, ["Next paragraph here."])
    assert len(_of_type(_manuscript(src), nodes.CodeBlock)) == 1


def test_backtick_codeblock_closed_with_trailing_spaces():
    src = "```\nx = 1\n```  \n\nNext paragraph here.\n"
    _check(src, ["Next paragraph here."])
    assert len(_of_type(_manuscript(src), nodes.CodeBlock)) == 1


def test_table_closed_with_trailing_spaces():
    src = ":table:\n  :tbody:\n    :tr: a : b ::  \n  ::  \n::  \n\nNext paragraph here.\n"
    _check(src, ["Next paragraph here."])


def test_section_meta_followed_by_trailing_spaces():
    src = ":section: {:title: A}  \n\nNext paragraph here.\n"
    _check(src, ["Next paragraph here."])


def test_inline_math_then_trailing_spaces_at_paragraph_end():
    src = "Some $x$  \n\nNext paragraph here.\n"
    _check(src, ["Some x", "Next paragraph here."])


def test_inline_math_then_trailing_spaces_then_more_lines():
    src = "Some $x$  \nmore text.\n"
    _check(src, ["Some x more text."])
    assert len(_of_type(_manuscript(src), nodes.Paragraph)) == 1


def test_inline_math_then_trailing_spaces_at_end_of_file():
    _check("Some $x$  ", ["Some x"])


def test_inline_math_then_trailing_spaces_before_halmos():
    src = ":theorem:\n\nfoo $x$  \n::\n\nNext paragraph here.\n"
    _check(src, ["foo x", "Next paragraph here."])


def test_list_items_with_trailing_spaces():
    src = ":itemize:\n\n  :-: one  \n\n  :-: two $x$  \n\n::\n\nNext paragraph here.\n"
    _check(src, ["Next paragraph here."])
    assert len(_of_type(_manuscript(src), nodes.Item)) == 2


def test_blank_line_with_only_spaces_ends_a_paragraph():
    src = "Some text.\n   \nNext paragraph here.\n"
    _check(src, ["Some text.", "Next paragraph here."])


@pytest.mark.parametrize("heading", ["# Title  ", "## Section $x$  "])
def test_heading_with_trailing_spaces(heading):
    src = f"{heading}\n\nNext paragraph here.\n"
    _check(src, ["Next paragraph here."])
