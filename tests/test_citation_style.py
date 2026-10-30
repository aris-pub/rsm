"""Citation style is a paper-wide :config: option, not a per-citation choice.

:citation-style: controls how every :cite: renders:
  numeric              -> [5]              (default, unchanged)
  parens-author-year   -> (Bourgain, 1985) (all in parens)
  author-parens-year   -> Bourgain (1985)  (only the year in parens)

Author rules: 1/2/3 surnames spelled out, 4+ use "et al." (rsm-3ez).
"""

import re

import rsm

_BIB = """\

:references:
  @book{knuth,
    title={Art of Computer Programming},
    author={Knuth, Donald E},
    year={2014},
    publisher={Addison-Wesley}
  }
  @article{three,
    title={Expander flows},
    author={Arora, Sanjeev and Lee, James R and Naor, Assaf},
    year={2008},
    journal={J. ACM}
  }
  @article{four,
    title={A paper},
    author={Smith, A and Jones, B and Lee, C and Wang, D},
    year={2020},
    journal={J. X}
  }
::
"""


def _build(style, citekey):
    cfg = ""
    if style is not None:
        cfg = ":config: {\n  :citation-style: " + style + "\n}\n::\n\n"
    src = "# T\n\n" + cfg + "See :cite:" + citekey + "::.\n" + _BIB
    return rsm.build(src, handrails=False, lint=False)


def _cite_text(html):
    """The visible text of the citation in the "See ...." sentence, tags
    stripped and non-breaking spaces shown as ordinary spaces."""
    m = re.search(r"<p>See (.*?)\.</p>", html, re.S)
    if not m:
        return None
    text = re.sub(r"<[^>]+>", "", m.group(1))
    return text.replace(" ", " ").strip()


def test_numeric_is_the_default():
    assert _cite_text(_build(None, "knuth")) == "[1]"


def test_numeric_explicit():
    assert _cite_text(_build("numeric", "knuth")) == "[1]"


def test_parens_author_year_single_author():
    assert _cite_text(_build("parens-author-year", "knuth")) == "(Knuth, 2014)"


def test_author_parens_year_single_author():
    assert _cite_text(_build("author-parens-year", "knuth")) == "Knuth (2014)"


def test_three_authors_all_spelled_out():
    assert _cite_text(_build("parens-author-year", "three")) == "(Arora, Lee and Naor, 2008)"


def test_four_authors_use_et_al():
    assert _cite_text(_build("parens-author-year", "four")) == "(Smith et al., 2020)"


def test_author_parens_year_three_authors():
    assert _cite_text(_build("author-parens-year", "three")) == "Arora, Lee and Naor (2008)"


def test_parens_multiple_keys():
    # Separated by "; " inside one outer paren, each author-year together.
    assert (
        _cite_text(_build("parens-author-year", "knuth,three"))
        == "(Knuth, 2014; Arora, Lee and Naor, 2008)"
    )


def test_author_parens_multiple_keys():
    # Separated by ", ", each with its own parenthesised year.
    assert (
        _cite_text(_build("author-parens-year", "knuth,three"))
        == "Knuth (2014), Arora, Lee and Naor (2008)"
    )


def test_year_stays_with_author_via_nbsp():
    # The only space that must not break is the one before the year, so it is
    # a non-breaking space in the raw markup (rendered as an ordinary space).
    html = _build("parens-author-year", "knuth")
    assert "Knuth, 2014" in html
    assert "Knuth, 2014" not in html  # the breakable-space form must not appear


def test_invalid_citation_style_is_rejected():
    import pytest

    import rsm.tsparser

    with pytest.raises(rsm.tsparser.RSMParserError, match="citation-style"):
        _build("sideways", "knuth")


# Bibliography ordering and year-suffix disambiguation. bA and bB share an
# author and year, so author-year mode must tell them apart with a/b suffixes
# assigned in sorted order, and sort the whole list by author then year.
_BIB2 = """\

:references:
  @article{knuth14, title={TAOCP}, author={Knuth, Donald E}, year={2014}, journal={X} }
  @article{bA, title={Aaa first}, author={Bourgain, Jean}, year={1985}, journal={IJM} }
  @article{bB, title={Bbb second}, author={Bourgain, Jean}, year={1985}, journal={IJM} }
  @article{arora08, title={Expander flows}, author={Arora, Sanjeev and Lee, James R and Naor, Assaf}, year={2008}, journal={JACM} }
::
"""


def _build2(style, body="See :cite:bA::."):
    cfg = ":config: {\n  :citation-style: " + style + "\n}\n::\n\n" if style else ""
    return rsm.build("# T\n\n" + cfg + body + "\n" + _BIB2, handrails=False, lint=False)


def _bib_order(html):
    """The labels of the bibliography entries in document order."""
    return re.findall(r'<div id="([^"]+)" class="bibitem"', html)


def _bib_text(html, label):
    """The visible text of one bibliography entry, nbsp shown as a space."""
    m = re.search(
        r'<div id="' + re.escape(label) + r'" class="bibitem".*?'
        r'<div class="hr-content-zone">(.*?)</div>',
        html,
        re.S,
    )
    if not m:
        return None
    return re.sub(r"<[^>]+>", "", m.group(1)).replace(" ", " ").strip()


def test_bibliography_sorted_by_author_then_year():
    assert _bib_order(_build2("parens-author-year")) == ["arora08", "bA", "bB", "knuth14"]


def test_bibliography_keeps_source_order_in_numeric():
    assert _bib_order(_build2("numeric")) == ["knuth14", "bA", "bB", "arora08"]


def test_year_suffix_in_bibliography():
    h = _build2("parens-author-year")
    assert "(1985a)" in _bib_text(h, "bA")
    assert "(1985b)" in _bib_text(h, "bB")
    assert "(2008)" in _bib_text(h, "arora08")  # no collision, no suffix


def test_year_suffix_in_cite():
    assert _cite_text(_build2("parens-author-year", "See :cite:bA::.")) == "(Bourgain, 1985a)"
    assert _cite_text(_build2("parens-author-year", "See :cite:bB::.")) == "(Bourgain, 1985b)"


def test_bibliography_unnumbered_in_author_year():
    h = _build2("parens-author-year")
    for lbl in ["arora08", "bA", "bB", "knuth14"]:
        assert not re.match(r"\d+\.", _bib_text(h, lbl))


def test_bibliography_numbered_in_numeric():
    html = _build2("numeric")
    m = re.search(r'id="knuth14" class="bibitem".*?<span class="bib-num">(\d+)</span>', html, re.S)
    assert m, "numeric entry has no number pill"
