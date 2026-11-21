"""The page's <title> holds the manuscript title as text, with each piece of math
as its TeX source between dollar signs, as arXiv does (rsm-39l)."""

import re

import pytest

import rsm


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
