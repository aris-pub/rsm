""":author-display-first: and :author-display-last: shorten the author list.

Every name stays in the HTML. The names between the first and the last ones
are wrapped so that the page script can hide them behind a "N more" pill.
"""

import logging

import pytest
from bs4 import BeautifulSoup

import rsm

NAMES = [
    "Ada Lovelace",
    "Bo Chen",
    "Cy Diaz",
    "Dana Patel",
    "Eli Novak",
    "Fay Okafor",
    "Gil Moreau",
    "Hana Sato",
]


def _source(config="", names=NAMES):
    src = "# Title\n\n"
    if config:
        src += f":config: {{\n{config}}}\n::\n\n"
    for name in names:
        src += f":author: {{\n  :name: {name}\n}}\n::\n\n"
    return src + "Text.\n"


def _names_p(config="", names=NAMES):
    html = rsm.render(_source(config, names), handrails=False)
    return BeautifulSoup(html, "html.parser").select_one("p.author-names")


def _visible_text(p):
    """The text of the list as shown after the script shortens it."""
    p = BeautifulSoup(str(p), "html.parser").select_one("p.author-names")
    for hidden in p.select(".author-hidden-names"):
        hidden.decompose()
    return p.get_text()


def _remove_pills(p):
    for pill in p.select(".author-more, .author-fewer"):
        pill.decompose()


def _assert_full_list(p, names=NAMES):
    assert p.select_one(".author-more") is None
    assert p.select_one(".author-hidden-names") is None
    assert p.get_text() == ", ".join(names)


def test_both_keys_shorten_the_list():
    p = _names_p("  :author-display-first: 3\n  :author-display-last: 2\n")
    assert [s.get_text() for s in p.select(".author-name")] == NAMES
    button = p.select_one(".author-more button")
    assert button.get_text() == "3 more"
    assert button["type"] == "button"
    assert button["aria-label"] == "Show 3 more authors"
    hidden = [s.get_text() for s in p.select(".author-hidden-names .author-name")]
    assert hidden == ["Dana Patel", "Eli Novak", "Fay Okafor"]
    assert _visible_text(p) == (
        "Ada Lovelace, Bo Chen, Cy Diaz, 3 more, Gil Moreau, Hana Sato"
    )


def test_full_list_text_without_the_pills():
    p = _names_p("  :author-display-first: 3\n  :author-display-last: 2\n")
    _remove_pills(p)
    assert p.get_text() == ", ".join(NAMES)


def test_the_button_is_hidden_without_the_script():
    p = _names_p("  :author-display-first: 3\n  :author-display-last: 2\n")
    assert p.select_one(".author-more").has_attr("hidden")


def test_first_alone_counts_last_as_zero():
    p = _names_p("  :author-display-first: 3\n")
    assert p.select_one(".author-more button").get_text() == "5 more"
    assert _visible_text(p) == "Ada Lovelace, Bo Chen, Cy Diaz, 5 more"


def test_last_alone_counts_first_as_zero():
    p = _names_p("  :author-display-last: 2\n")
    assert p.select_one(".author-more button").get_text() == "6 more"
    assert _visible_text(p) == "6 more, Gil Moreau, Hana Sato"
    _remove_pills(p)
    assert p.get_text() == ", ".join(NAMES)


def test_no_keys_lists_every_author():
    _assert_full_list(_names_p())


@pytest.mark.parametrize(
    "config",
    [
        "  :author-display-first: 5\n  :author-display-last: 3\n",
        "  :author-display-first: 6\n  :author-display-last: 4\n",
        "  :author-display-first: 8\n",
        "  :author-display-last: 10\n",
    ],
)
def test_keys_that_cover_every_author_list_every_author(config):
    _assert_full_list(_names_p(config))


@pytest.mark.parametrize("bad", ["2.5", "two"])
@pytest.mark.parametrize("key", ["author-display-first", "author-display-last"])
def test_bad_value_is_logged_and_every_author_listed(caplog, key, bad):
    p = _names_p(f"  :{key}: {bad}\n")
    _assert_full_list(p)
    errors = [
        r
        for r in caplog.records
        if r.levelno == logging.ERROR
        and f"Invalid value for :{key}:" in r.getMessage()
    ]
    assert len(errors) == 1, caplog.text
    assert bad in errors[0].getMessage()
    assert "whole number" in errors[0].getMessage()


@pytest.mark.parametrize(
    "config",
    [
        "  :author-display-first: two\n  :author-display-last: 2\n",
        "  :author-display-first: 3\n  :author-display-last: 2.5\n",
        "  :author-display-first: -1\n  :author-display-last: 2\n",
        "  :author-display-first: {3}\n  :author-display-last: 2\n",
    ],
)
def test_one_bad_value_lists_every_author_even_when_the_other_is_good(
    caplog, config
):
    _assert_full_list(_names_p(config))
    assert "Invalid value for :author-display-" in caplog.text, caplog.text


def test_affiliation_superscripts_stay_with_the_names():
    src = (
        "# Title\n\n:config: {\n  :author-display-first: 1\n"
        "  :author-display-last: 1\n}\n::\n\n"
    )
    for i, name in enumerate(NAMES):
        src += f":author: {{\n  :name: {name}\n  :affiliation: Uni {i % 2}\n}}\n::\n\n"
    html = rsm.render(src + "Text.\n", handrails=False)
    soup = BeautifulSoup(html, "html.parser")
    p = soup.select_one("p.author-names")
    sups = [s.select_one("sup").get_text() for s in p.select(".author-name")]
    assert sups == ["1", "2"] * 4
    assert soup.select_one(".author-summary").get_text() == "2 affiliations"
