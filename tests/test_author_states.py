"""The HTML of the author block, which has two states: closed and open.

The page script sets data-authors="closed" or "open" on .author-block. The
HTML holds every name and all the details, so readers without JavaScript see
everything. The controls (the "N more" and "Show fewer" pills and the summary
label) carry the hidden attribute and only show once the script sets a state.
Leo approved this design (design 4) on 2026-11-26.
"""

from bs4 import BeautifulSoup

import rsm

AUTHORS = [
    ("Ada Lovelace", "University of London", "ada@example.org", "0000-0002-1825-0097", "Equal contribution"),
    ("Bo Chen", "ETH Zurich", "", "", "Equal contribution"),
    ("Cy Diaz", "Universidad de Chile", "", "", ""),
    ("Dana Patel", "IIT Delhi", "", "", ""),
    ("Eli Novak", "University of London", "", "", ""),
    ("Fay Okafor", "ETH Zurich", "", "", ""),
    ("Gil Moreau", "Universidad de Chile", "", "", ""),
    ("Hana Sato", "IIT Delhi", "", "", ""),
]

SHORTEN = "  :author-display-first: 3\n  :author-display-last: 2\n"


def _source(config="", authors=AUTHORS):
    src = "# Title\n\n"
    if config:
        src += f":config: {{\n{config}}}\n::\n\n"
    for name, aff, email, orcid, note in authors:
        src += f":author: {{\n  :name: {name}\n"
        if aff:
            src += f"  :affiliation: {aff}\n"
        if email:
            src += f"  :email: {email}\n"
        if orcid:
            src += f"  :orcid: {orcid}\n"
        if note:
            src += f"  :author-note: {note}\n"
        src += "}\n::\n\n"
    return src + "Text.\n"


def _block(config="", authors=AUTHORS, handrails=False):
    html = rsm.render(_source(config, authors), handrails=handrails)
    return BeautifulSoup(html, "html.parser").select_one(".author-block")


class TestShortened:
    def test_more_pill_sits_after_the_first_names(self):
        p = _block(SHORTEN).select_one("p.author-names")
        more = p.select_one(".author-more")
        assert more.has_attr("hidden")
        button = more.select_one("button")
        assert button["type"] == "button"
        assert button.get_text() == "3 more"
        assert button["aria-label"] == "Show 3 more authors"
        assert button["aria-expanded"] == "false"
        before = [s.get_text() for s in more.find_all_previous("span", class_="author-name-text")]
        assert sorted(before) == ["Ada Lovelace", "Bo Chen", "Cy Diaz"]

    def test_fewer_pill_sits_where_the_hidden_names_end(self):
        hidden = _block(SHORTEN).select_one(".author-hidden-names")
        names = [s.get_text() for s in hidden.select(".author-name-text")]
        assert names == ["Dana Patel", "Eli Novak", "Fay Okafor"]
        fewer = hidden.contents[-1]
        assert "author-fewer" in fewer["class"]
        assert fewer.has_attr("hidden")
        button = fewer.select_one("button")
        assert button["type"] == "button"
        assert button.get_text() == "Show fewer"
        assert button["aria-label"] == "Show fewer authors"
        assert button["aria-expanded"] == "true"
        assert fewer.get_text() == " Show fewer"

    def test_full_text_without_the_controls(self):
        p = _block(SHORTEN).select_one("p.author-names")
        for c in p.select(".author-more, .author-fewer"):
            c.decompose()
        assert p.get_text() == (
            "Ada Lovelace1, Bo Chen2, Cy Diaz3, Dana Patel4, Eli Novak1, "
            "Fay Okafor2, Gil Moreau3, Hana Sato4"
        )

    def test_closed_text(self):
        p = _block(SHORTEN).select_one("p.author-names")
        for c in p.select(".author-hidden-names"):
            c.decompose()
        names = [s.get_text() for s in p.select(".author-name-text")]
        assert names == ["Ada Lovelace", "Bo Chen", "Cy Diaz", "Gil Moreau", "Hana Sato"]
        assert ", 3 more, " in p.get_text()

    def test_open_text(self):
        p = _block(SHORTEN).select_one("p.author-names")
        p.select_one(".author-more").decompose()
        text = p.get_text()
        assert "Fay Okafor2 Show fewer, Gil Moreau3" in text

    def test_summary_label(self):
        summary = _block(SHORTEN).select_one("button.author-summary")
        assert summary["type"] == "button"
        assert summary.has_attr("hidden")
        assert summary["aria-expanded"] == "false"
        assert summary.get_text() == "4 affiliations · 1 email · 1 ORCID · 1 note"

    def test_summary_label_sits_between_the_names_and_the_details(self):
        block = _block(SHORTEN)
        kids = [c for c in block.children if getattr(c, "name", None)]
        assert [k.name for k in kids] == ["p", "button", "div"]
        assert "author-summary" in kids[1]["class"]
        assert "author-details" in kids[2]["class"]

    def test_details_are_a_plain_block_without_a_summary(self):
        block = _block(SHORTEN)
        assert block.select_one("details") is None
        assert block.select_one("summary") is None
        details = block.select_one("div.author-details")
        affs = [li.get_text() for li in details.select("ol.author-affiliations li")]
        assert affs == [
            "1University of London",
            "2ETH Zurich",
            "3Universidad de Chile",
            "4IIT Delhi",
        ]
        assert details.select_one(".author-note").get_text() == "Equal contribution"
        assert details.select_one(".author-correspondence").get_text() == (
            "Correspondence: ada@example.org"
        )
        assert details.select_one(".author-orcid").get_text() == (
            "Ada Lovelace: 0000-0002-1825-0097"
        )

    def test_handrails_wrap_the_same_content(self):
        block = _block(SHORTEN, handrails=True)
        zone = block.select_one(".hr > .hr-content-zone")
        kids = [c for c in zone.children if getattr(c, "name", None)]
        assert [k.name for k in kids] == ["p", "button", "div"]
        assert block.select_one(".hr > .hr-collapse-zone button.hr-collapse")


class TestNotShortened:
    def test_no_pills(self):
        block = _block()
        assert block.select_one(".author-more") is None
        assert block.select_one(".author-fewer") is None
        assert block.select_one(".author-hidden-names") is None
        names = [s.get_text() for s in block.select(".author-name-text")]
        assert names == [a[0] for a in AUTHORS]

    def test_keys_that_cover_every_author_add_no_pills(self):
        block = _block("  :author-display-first: 5\n  :author-display-last: 3\n")
        assert block.select_one(".author-more") is None
        assert block.select_one(".author-fewer") is None

    def test_summary_label_and_details(self):
        block = _block()
        summary = block.select_one("button.author-summary")
        assert summary.has_attr("hidden")
        assert summary.get_text() == "4 affiliations · 1 email · 1 ORCID · 1 note"
        assert block.select_one("div.author-details ol.author-affiliations")

    def test_summary_label_lists_only_what_exists(self):
        block = _block(authors=[("A", "U", "", "", "")])
        assert block.select_one(".author-summary").get_text() == "1 affiliation"

    def test_no_details_no_summary_label(self):
        block = _block(authors=[("A", "", "", "", ""), ("B", "", "", "", "")])
        assert block.select_one(".author-summary") is None
        assert block.select_one(".author-details") is None


class TestNameTooltip:
    def test_name_points_at_its_own_affiliation_and_note(self):
        block = _block(SHORTEN)
        ada = block.select(".author-name-text")[0]
        assert ada["data-affiliation"] == "1"
        assert ada["data-note"] == "*"
        cy = block.select(".author-name-text")[2]
        assert cy["data-affiliation"] == "3"
        assert not cy.has_attr("data-note")

    def test_details_carry_the_numbers_and_symbols(self):
        block = _block(SHORTEN)
        items = block.select(".author-affiliations li")
        assert [li["data-affiliation"] for li in items] == ["1", "2", "3", "4"]
        assert items[2].get_text() == "3Universidad de Chile"
        assert block.select_one("p.author-note")["data-note"] == "*"

    def test_name_without_affiliation_or_note_has_no_tooltip_data(self):
        block = _block(authors=[("A", "", "", "", ""), ("B", "", "a@b.org", "", "")])
        for name in block.select(".author-name-text"):
            assert not name.has_attr("data-affiliation")
            assert not name.has_attr("data-note")

    def test_superscripts_stay_after_the_name(self):
        block = _block(SHORTEN)
        ada = block.select(".author-name")[0]
        assert ada.select_one(".author-name-text").find_next_sibling("sup").get_text() == "1"



ESCAPE_AUTHORS = [
    ("A", 'Lab "X" <b>bold</b>', 'a"b@x.org', "", 'Note "one" <i>it</i>'),
    ("B", "Other & Co", "", "", "Plain"),
]


class TestEscaping:
    """Affiliations, notes and emails are text: RSM accepts HTML only in :html:
    and :htmlblock: (rsm-8ckc)."""

    def test_affiliation_list_is_escaped(self):
        block = _block(authors=ESCAPE_AUTHORS)
        items = block.select(".author-affiliations li")
        assert items[0].get_text() == '1Lab "X" <b>bold</b>'
        assert items[1].get_text() == "2Other & Co"
        assert block.select(".author-affiliations b") == []

    def test_notes_are_escaped(self):
        block = _block(authors=ESCAPE_AUTHORS)
        note = block.select("p.author-note")[0]
        assert note.get_text() == '*Note "one" <i>it</i>'
        assert block.select("p.author-note i") == []

    def test_superscripts_hold_no_text_of_the_value(self):
        block = _block(authors=ESCAPE_AUTHORS)
        aff, note = block.select(".author-name")[0].select("sup")
        assert aff.attrs == {"data-affiliation": "1"}
        assert note.attrs == {"data-note": "*"}
        assert aff.get_text() == "1"
        assert note.get_text() == "*"

    def test_correspondence_link_is_escaped(self):
        block = _block(authors=ESCAPE_AUTHORS)
        link = block.select_one(".author-correspondence a")
        assert link["href"] == 'mailto:a"b@x.org'
        assert link.get_text() == 'a"b@x.org'

    def test_name_points_at_its_affiliation_and_note(self):
        block = _block(authors=ESCAPE_AUTHORS)
        name = block.select(".author-name-text")[0]
        assert name["data-affiliation"] == "1"
        assert name["data-note"] == "*"

    def test_orcid_line_is_escaped(self):
        block = _block(authors=[("A", "", "", '0000-<b>x</b>"', "")])
        line = block.select_one(".author-orcid")
        assert line.get_text() == 'A: 0000-<b>x</b>"'
        assert line.select("b") == []
        link = block.select_one("a.author-contact")
        assert link["href"] == 'https://orcid.org/0000-<b>x</b>"'


class TestChevron:
    """The handrail chevron is left out when the block has nothing to open."""

    def _chevron(self, config="", authors=AUTHORS):
        block = _block(config, authors, handrails=True)
        return block.select_one(".hr > .hr-collapse-zone button.hr-collapse")

    def test_no_chevron_when_there_is_nothing_to_open(self):
        assert self._chevron(authors=[("A", "", "", "", ""), ("B", "", "", "", "")]) is None

    def test_chevron_when_there_are_details(self):
        assert self._chevron(authors=[("A", "U", "", "", ""), ("B", "", "", "", "")])

    def test_chevron_when_the_list_is_shortened(self):
        bare = [(name, "", "", "", "") for name, *_ in AUTHORS]
        assert self._chevron(SHORTEN, bare)

    def test_chevron_with_shortened_list_and_details(self):
        assert self._chevron(SHORTEN)
