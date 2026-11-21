"""The page's <title> holds the manuscript title as text, with each piece of math
as its TeX source between dollar signs, as arXiv does (rsm-39l)."""

import re
from textwrap import dedent

import pytest

import rsm
from rsm.tsparser import RSMParserError, TSParser


def _page_title(src: str, **kwargs) -> str:
    html = rsm.build(src, lint=False, **kwargs)
    return re.search(r"<title>(.*?)</title>", html, re.S).group(1)


@pytest.mark.parametrize("standalone", [False, True])
@pytest.mark.parametrize("handrails", [False, True])
def test_math_and_bold_in_title(handrails, standalone):
    src = "# The $\\mathbb{R}^n$ case of **Turán**\n\nText.\n"
    title = _page_title(src, handrails=handrails, standalone=standalone)
    assert title == "The $\\mathbb{R}^n$ case of Turán"


def test_math_at_the_end_of_a_title():
    src = "# Floor, ceiling, slopes, and $K$-theory\n\nText.\n"
    assert _page_title(src) == "Floor, ceiling, slopes, and $K$-theory"


def test_title_text_and_math_stay_escaped():
    src = "# With $a < b$ & `x<y`\n\nText.\n"
    assert _page_title(src) == "With $a &lt; b$ &amp; x&lt;y"


def test_emphasis_and_span_in_title():
    src = "# An *easy* :span:{:strong:} bound :: here\n\nText.\n"
    assert _page_title(src) == "An easy bound here"


def test_plain_title_is_unchanged():
    assert _page_title("# Plain title\n\nText.\n") == "Plain title"


# :plain-title:


@pytest.mark.parametrize("standalone", [False, True])
def test_plain_title_goes_in_title(standalone):
    src = dedent(
        """\
        # Floor, ceiling, slopes, and $K$-theory {
          :plain-title: Floor, ceiling, slopes, and K-theory
        }

        Text.
        """
    )
    title = _page_title(src, standalone=standalone)
    assert title == "Floor, ceiling, slopes, and K-theory"


def test_plain_title_keeps_its_commas():
    src = "# T {:plain-title: Floor, ceiling, slopes, and K-theory}\n\nText.\n"
    assert TSParser().parse(src).plain_title == "Floor, ceiling, slopes, and K-theory"


def test_plain_title_is_escaped():
    src = "# T {:plain-title: A < B & C}\n\nText.\n"
    assert _page_title(src) == "A &lt; B &amp; C"


def test_plain_title_is_only_in_title():
    src = "# The $K$ case {:plain-title: Distinct tab words}\n\nText.\n"
    html = rsm.build(src, lint=False)
    # The page keeps a copy of the whole source, which holds the meta as written.
    html = re.sub(r'<div class="rsm-source hide">.*?</div>', "", html, flags=re.S)
    assert html.count("Distinct tab words") == 1
    assert "<title>Distinct tab words</title>" in html


def test_no_plain_title():
    assert TSParser().parse("# The $K$ case\n\nText.\n").plain_title == ""


@pytest.mark.parametrize(
    "src, line",
    [
        ("# T {\n  :plain-title: The $K$ case\n}\n\nText.\n", 2),
        ("# T {\n  :eyebrow: N\n  :plain-title: A(:span: B\n}\n\nText.\n", 3),
        ("# T {:plain-title: The :math:K:: case}\n\nText.\n", 1),
        ("# T {:plain-title: A :label: b}\n\nText.\n", 1),
        ("# T {\n  :plain-title: A :strong: B\n}\n\nText.\n", 2),
        ("# T {:plain-title: A, :nonum:}\n\nText.\n", 1),
    ],
)
def test_plain_title_with_syntax_is_an_error(src, line):
    message = f"plain-title takes plain text only (line {line})"
    with pytest.raises(RSMParserError, match=re.escape(message)):
        TSParser().parse(src)


def test_key_on_the_next_line_is_fine():
    src = "# T {\n  :plain-title: A, B\n  :eyebrow: N\n}\n\nText.\n"
    tree = TSParser().parse(src)
    assert tree.plain_title == "A, B"
    assert tree.eyebrow == "N"
