"""Hyphenated words never break across lines (rsm-69h).

Chromium and Firefox may break a line right after a hyphen. RSM wraps each
hyphenated word in a span that braiid.css styles with white-space: nowrap. A
hyphenated word is any stretch of text without spaces that contains a hyphen,
including math joined to the hyphen. Text that is not prose (math source, code,
URLs, the page title) is left as it is."""

import re
from html.parser import HTMLParser

import pytest

import rsm

OPEN = '<span class="hyphenated">'
MATH_K = r'<span class="math">\(K\)</span>'


def _no_nodeids(html: str) -> str:
    return re.sub(r' data-nodeid="\d+"', "", html)


def _render(src: str, **kw) -> str:
    return rsm.render(src, handrails=False, **kw)


def _body(src: str) -> str:
    return _render(f"# T\n\n{src}\n")


class _TextOf(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data):
        self.parts.append(data)


def _text(html: str) -> str:
    parser = _TextOf()
    parser.feed(html)
    return "".join(parser.parts)


@pytest.mark.parametrize(
    "word", ["K-theory", "1-2", "x-axis", "Cohen-Macaulay-type"]
)
def test_hyphenated_word_in_paragraph(word):
    html = _body(f"The {word} here.")
    assert f"The {OPEN}{word}</span> here." in html


def test_punctuation_joined_to_the_word_stays_inside():
    html = _body("See Cohen-Macaulay, and (x-axis).")
    assert f"See {OPEN}Cohen-Macaulay,</span> and {OPEN}(x-axis).</span>" in html


def test_words_without_hyphen_are_not_wrapped():
    html = _body("No hyphen in this sentence.")
    assert OPEN not in html


def test_math_joined_to_hyphen_is_one_word():
    html = _no_nodeids(_body("The $K$-theory here."))
    assert f"The {OPEN}{MATH_K}-theory</span> here." in html


def test_math_after_hyphen_is_one_word():
    html = _no_nodeids(_body("Rank 1-$K$ here."))
    assert f"Rank {OPEN}1-{MATH_K}</span> here." in html


def test_math_between_hyphens_is_one_word():
    html = _no_nodeids(_body("A x-$K$-y here."))
    assert f"A {OPEN}x-{MATH_K}-y</span> here." in html


def test_math_without_hyphen_is_not_wrapped():
    html = _body("The $K$th power and $K$ alone.")
    assert OPEN not in html


def test_hyphen_inside_math_does_not_count():
    html = _body("The $a-b$ difference.")
    assert OPEN not in html
    assert r"\(a-b\)" in html


def test_plain_heading():
    html = _render("# T\n\n## Floor, ceiling, slopes, and K-theory\n\nBar.\n")
    assert f"<h2>1. Floor, ceiling, slopes, and {OPEN}K-theory</span></h2>" in html


def test_heading_with_math():
    html = _render("# T\n\n## Floor, ceiling, slopes, and $K$-theory\n\nBar.\n")
    assert f"<h2>1. Floor, ceiling, slopes, and {OPEN}{MATH_K}-theory</span></h2>" in html


def test_manuscript_title():
    html = _render("# Notes on K-theory\n\nBar.\n")
    assert f"<h1>Notes on {OPEN}K-theory</span></h1>" in html


def test_page_title_element_is_not_touched():
    html = rsm.build("# Notes on K-theory\n\nBar.\n", handrails=True, standalone=True)
    assert "<title>Notes on K-theory</title>" in html
    html = rsm.build("# Notes on $K$-theory\n\nBar.\n", handrails=True, standalone=True)
    title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
    assert "hyphenated" not in title
    assert title.endswith("</span>-theory")


def test_caption():
    html = _body(":figure:\n  :path: x.png\n\n  :caption: The x-axis.\n\n::")
    assert f"The {OPEN}x-axis.</span>" in html


def test_inside_bold():
    html = _body("A **Cohen-Macaulay** ring.")
    assert f"<strong>{OPEN}Cohen-Macaulay</span></strong>" in html


@pytest.mark.parametrize(
    "src, kept",
    [
        ("Run `a-b` now.", "<code>a-b</code>"),
        (":url:https://a-b.example.com::", 'href="https://a-b.example.com"'),
        ("$$\na-b\n$$", "a-b\n$$"),
    ],
    ids=["code", "url", "mathblock"],
)
def test_non_prose_is_not_touched(src, kept):
    html = _body(src)
    assert kept in html
    assert OPEN not in html


def test_codeblock_is_not_touched():
    html = _body(":codeblock:\n  x-y = 1\n::")
    assert OPEN not in html


def test_text_content_is_unchanged():
    src = "The $K$-theory of x-axis, 1-2 and Cohen-Macaulay-type rings."
    html = _body(src)
    assert html.count(OPEN) == 4
    # Copying the page copies its text, which must be the source text with
    # plain hyphens and no hidden characters.
    assert "The \\(K\\)-theory of x-axis, 1-2 and Cohen-Macaulay-type rings." in _text(html)


def test_handrails_math_with_trailing_punctuation():
    # The handrails translator moves punctuation after math into a wrapper span
    # with the math, so the hyphenated word must still close after it.
    html = rsm.render("# T\n\nRank 1-$K$. Next.\n", handrails=True)
    start = html.index(OPEN)
    inner = html[start:]
    depth, i = 0, 0
    for m in re.finditer(r"<span\b|</span>", inner):
        depth += 1 if m.group() == "<span" else -1
        if depth == 0:
            i = m.end()
            break
    # The inline wrapper writes a newline after its opening tag.
    assert _text(inner[:i]) == "1-\n\\(K\\)."
    assert inner[i:].startswith(" Next.")
