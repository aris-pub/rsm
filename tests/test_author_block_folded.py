"""While the author details are folded, the author block shows a mail icon after
each author who has an email, the ORCID mark after each author who has an
ORCID, and labels that count what the fold holds (Leo chose this from
mockups on 2026-11-23)."""

import re

import rsm

SRC = """\
# Title

:author: {
  :name: Ada Lovelace
  :affiliation: University of London
  :email: ada@example.org
  :orcid: 0000-0002-1825-0097
  :author-note: Equal contribution
} ::

:author: {
  :name: Charles Babbage
  :affiliation: University of Cambridge
  :email: charles@example.org
  :author-note: Equal contribution
} ::

:author: {
  :name: Mary Somerville
  :affiliation: University of London
} ::

Text.
"""


def _names(html: str) -> str:
    return re.search(r'<p class="author-names">(.*?)</p>', html, re.S).group(1)


def _summary(html: str) -> str:
    return re.search(r"<summary>(.*?)</summary>", html, re.S).group(1)


def _author(html: str, name: str) -> str:
    for part in re.findall(r'<span class="author-name">(.*?)</span>(?:, |$)', _names(html)):
        if part.startswith(name):
            return part
    raise AssertionError(f"no author entry for {name}")


def test_each_author_is_one_entry():
    names = _names(rsm.render(SRC))
    assert names.count('<span class="author-name">') == 3


def test_mail_icon_after_authors_with_an_email():
    html = rsm.render(SRC)
    assert "hr-icon-mail" in _author(html, "Ada Lovelace")
    assert "hr-icon-mail" in _author(html, "Charles Babbage")
    assert "hr-icon-mail" not in _author(html, "Mary Somerville")


def test_orcid_mark_after_authors_with_an_orcid():
    html = rsm.render(SRC)
    assert "hr-icon-orcid" in _author(html, "Ada Lovelace")
    assert "hr-icon-orcid" not in _author(html, "Charles Babbage")


def test_summary_counts_what_the_fold_holds():
    text = re.sub(r"<[^>]+>", " ", _summary(rsm.render(SRC)))
    labels = text.split()
    assert " ".join(labels) == "2 affiliations 2 emails 1 ORCID 1 note"


def test_summary_has_no_label_for_what_is_missing():
    src = "# T\n\n:author: {\n  :name: A\n  :affiliation: U\n} ::\n\nText.\n"
    text = " ".join(re.sub(r"<[^>]+>", " ", _summary(rsm.render(src))).split())
    assert text == "1 affiliation"
