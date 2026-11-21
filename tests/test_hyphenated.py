"""Hyphenated words never break across lines (rsm-69h).

Chromium and Firefox may break a line right after a hyphen. RSM wraps each
hyphenated word in a span that braiid.css styles with white-space: nowrap. A
hyphenated word is any stretch of text without spaces that contains a hyphen
(the keyboard hyphen, the Unicode hyphen or an en dash), including inline
markup, math, code, links, citations and footnote markers that touch it. Markup
that touches such a word is wrapped whole, even when it holds spaces. Text that
is not prose (math source, code, bare URLs, the page title) is left as it is."""

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
    assert title == "Notes on $K$-theory"


def test_caption():
    html = _body(":figure:\n  :path: x.png\n\n  :caption: The x-axis.\n\n::")
    assert f"The {OPEN}x-axis.</span>" in html


def test_inside_bold():
    html = _no_nodeids(_body("A **Cohen-Macaulay** ring."))
    word = '<span class="span"><strong>Cohen-Macaulay</strong></span>'
    assert f"A {OPEN}{word}</span> ring." in html


def test_inside_bold_with_spaces():
    html = _body("A **graded Cohen-Macaulay** ring.")
    assert f"<strong>graded {OPEN}Cohen-Macaulay</span></strong>" in html


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


@pytest.mark.parametrize("word", ["pre-", "--", "-"])
def test_hyphen_at_an_end_or_alone(word):
    html = _body(f"The {word} and post- here.")
    assert f"The {OPEN}{word}</span> and {OPEN}post-</span> here." in html


def _word_of(html: str, start: str) -> str:
    """The hyphenated span in *html* that starts with *start*, with its tags."""
    i = html.index(OPEN + start)
    depth = 0
    for m in re.finditer(r"<span\b|</span>", html[i:]):
        depth += 1 if m.group() == "<span" else -1
        if depth == 0:
            return html[i : i + m.end()]
    raise AssertionError("unbalanced")


def test_bold_touching_hyphen_is_one_word():
    html = _no_nodeids(_body("A **Cohen**-Macaulay ring."))
    word = '<span class="span"><strong>Cohen</strong></span>-Macaulay'
    assert f"A {OPEN}{word}</span> ring." in html


def test_italic_after_hyphen_is_one_word():
    html = _no_nodeids(_body("A Cohen-*Macaulay* ring."))
    word = 'Cohen-<span class="span"><em>Macaulay</em></span>'
    assert f"A {OPEN}{word}</span> ring." in html


def test_code_touching_hyphen_is_one_word():
    html = _no_nodeids(_body("The `foo`-style call."))
    assert f'The {OPEN}<span class="code"><code>foo</code></span>-style</span> call.' in html


def test_reference_touching_hyphen_is_one_word():
    html = _body(":theorem: {:label: thm} Foo. ::\n\nA :ref:thm,Lemma::-type result.")
    word = _word_of(html, "<a")
    assert _text(word) == "Lemma-type"
    assert '<a class="reference" href="#thm">Lemma</a>' in word


def test_link_touching_hyphen_is_one_word():
    html = _body("A :url:https://a.org,site::-wide rule.")
    word = _word_of(html, "<a")
    assert _text(word) == "site-wide"
    assert 'href="https://a.org"' in word


def test_citation_touching_hyphen_is_one_word():
    src = (
        "As in :cite:knuth::-style.\n\n:references:\n  @book{knuth,\n"
        "    title={Art},\n    author={Knuth, Donald E},\n    year={2014},\n"
        "    publisher={AW}\n  }\n::"
    )
    html = _body(src)
    word = _word_of(html, '<span class="nowrap">')
    assert _text(word) == "[1]-style."


def test_footnote_marker_touching_hyphen_is_one_word():
    html = _body("Some (self-test):note:n:: here.\n\n:note: {:label: n} The note. ::")
    word = _word_of(html, "(self-test)")
    assert _text(word) == "(self-test)1"
    assert 'class="note-marker"' in word


def test_raw_html_touching_hyphen_is_one_word():
    html = _body("A :html:{:alt: x} <b>x</b> ::-ray here.")
    word = _word_of(html, "<span")
    assert "<b>x</b>" in word
    assert word.endswith("-ray</span>")


def test_link_text_is_prose():
    html = _body("See :url:https://a.org, the K-theory page:: now.")
    assert f"the {OPEN}K-theory</span> page</a>" in html


def test_reference_text_is_prose():
    html = _body(":theorem: {:label: thm} Foo. ::\n\nSee :ref:thm, the x-axis result::.")
    assert f"the {OPEN}x-axis</span> result</a>" in html


def test_bare_url_text_is_not_touched():
    html = _body("See :url:https://a-b.example.com:: now.")
    assert ">https://a-b.example.com</a>" in html
    assert OPEN not in html


def test_table_of_contents():
    html = _render("# T\n\n:toc: ::\n\n## Plain K-theory\n\nBar.\n")
    assert f"1. Plain {OPEN}K-theory</span></a>" in html


def test_sidebar_table_of_contents():
    html = rsm.render(
        "# T\n\n:toc: ::\n\n## Plain K-theory\n\nBar.\n", handrails=True, sidebar=True
    )
    toc = html[html.index('<ul class="contents">') :]
    assert f"1. Plain {OPEN}K-theory</span></a>" in toc


def test_raw_html_fallback_is_prose():
    html = _body("Consider :html:{:alt: the x-axis} <b>x</b> :: here.")
    assert f'<span class="rawhtml-alt" hidden>the {OPEN}x-axis</span></span>' in html


def test_author_name_and_affiliation():
    src = (
        "# T\n\n:author: {\n  :name: Jean-Pierre Serre\n"
        "  :affiliation: Max-Planck-Institut\n}\n::\n\nBar.\n"
    )
    html = _render(src)
    assert f"Jean-{OPEN}" not in html
    assert f"{OPEN}Jean-Pierre</span> Serre" in html
    assert f"{OPEN}Max-Planck-Institut</span>" in html


def test_keywords():
    html = _render("# T\n\n:abstract: {:keywords: non-backtracking, graphs}\n\nFoo.\n::\n")
    assert f"Keywords: {OPEN}non-backtracking,</span> graphs</p>" in html


def test_eyebrow():
    html = _render("# T {\n  :eyebrow: Follow-up\n}\n\nBar.\n")
    assert f"{OPEN}Follow-up</span>" in html


def test_bibliography_entry():
    src = (
        "As in :cite:knuth::.\n\n:references:\n  @book{knuth,\n"
        "    title={Semi-numerical algorithms},\n    author={Knuth, Donald-E},\n"
        "    year={2014},\n    publisher={Addison-Wesley}\n  }\n::"
    )
    html = _body(src)
    assert f'<div class="bib-title">{OPEN}Semi-numerical</span> algorithms</div>' in html
    assert f"{OPEN}Donald-E</span>" in html
    assert f'<div class="bib-venue">{OPEN}Addison-Wesley</span>' in html


@pytest.mark.parametrize(
    "word", ["Cauchy–Schwarz", "3–5", "co‐op"], ids=["en-dash", "range", "hyphen"]
)
def test_other_hyphen_characters(word):
    html = _body(f"The {word} here.")
    assert f"The {OPEN}{word}</span> here." in html


def test_minus_sign_is_not_a_hyphen():
    html = _body("The a−b here.")
    assert OPEN not in html


def test_en_dash_in_heading_and_strings():
    html = _render("# T {\n  :eyebrow: Cauchy–Schwarz\n}\n\n## The 3–5 case\n\nBar.\n")
    assert f"{OPEN}Cauchy–Schwarz</span>" in html
    assert f"The {OPEN}3–5</span> case</h2>" in html


def test_bold_with_space_touching_hyphen_is_one_run():
    html = _no_nodeids(_body("A **graded Cohen**-Macaulay ring."))
    word = '<span class="span"><strong>graded Cohen</strong></span>-Macaulay'
    assert f"A {OPEN}{word}</span> ring." in html


def test_bold_with_space_after_hyphen_is_one_run():
    html = _no_nodeids(_body("A Cohen-*Macaulay ring* here."))
    word = 'Cohen-<span class="span"><em>Macaulay ring</em></span>'
    assert f"A {OPEN}{word}</span> here." in html


def test_hyphen_inside_bold_touching_text_is_one_run():
    html = _no_nodeids(_body("A **graded Cohen-**Macaulay ring."))
    word = '<span class="span"><strong>graded Cohen-</strong></span>Macaulay'
    assert f"A {OPEN}{word}</span> ring." in html


def test_bold_with_space_not_touching_a_hyphenated_word():
    html = _no_nodeids(_body("A **graded Cohen-Macaulay** ring and **a b**-free x-y."))
    inner = f'<span class="span"><strong>graded {OPEN}Cohen-Macaulay</span></strong></span>'
    assert f"A {inner} ring" in html
    run = f'{OPEN}<span class="span"><strong>a b</strong></span>-free</span>'
    assert f"and {run} {OPEN}x-y.</span>" in html


def test_reference_with_space_touching_hyphen_is_one_run():
    html = _body("## Intro {:label: intro}\n\nSee :ref:intro::-style text.")
    word = _word_of(html, "<a")
    assert _text(word) == "Section 1-style"


def test_author_year_citation_touching_hyphen_is_one_run():
    src = (
        ":config: {\n  :citation-style: parens-author-year\n}\n::\n\n"
        "As in :cite:knuth::-style text.\n\n:references:\n  @book{knuth,\n"
        "    title={Art},\n    author={Knuth, Donald E},\n    year={2014},\n"
        "    publisher={AW}\n  }\n::"
    )
    html = _body(src)
    word = _word_of(html, "(<a")
    assert _text(word).replace(" ", " ") == "(Knuth, 2014)-style"
