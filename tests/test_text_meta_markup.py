"""The text meta values that the reader sees hold inline markup, as :title:
does (rsm-ugg): :affiliation:, :author-note:, :eyebrow:, :name:, :blockname:
and :reftext:.

The grammar side is covered by tree-sitter-rsm/test/corpus/titles.txt."""

import logging
import re

import pytest
import tree_sitter_rsm
from bs4 import BeautifulSoup
from tree_sitter import Language, Parser

import rsm
from rsm import nodes
from rsm.app import ParserApp, ProcessorApp
from rsm.pandoc import PandocTranslator

MATH_K = r'<span class="math">\(K\)</span>'


def _flat(html: str) -> str:
    return re.sub(r"\s+", " ", html)


def _render(src: str, handrails: bool = False) -> str:
    return _flat(rsm.render(src, handrails=handrails))


def _tree(src: str) -> nodes.Manuscript:
    return ParserApp(plain=src).run()


def _first(tree: nodes.Node, cls: type) -> nodes.Node:
    return next(tree.traverse(nodeclass=cls))


def _processed(src: str) -> nodes.Manuscript:
    a = ProcessorApp(plain=src)
    a.run()
    return a.translator.tree


EYEBROW = "# Title\n  {{:eyebrow: {}}}\n\nHello.\n"


class TestEyebrow:
    @pytest.mark.parametrize("value", ["The :math:K:: case", "The $K$ case"])
    def test_math_in_eyebrow(self, value, caplog):
        with caplog.at_level(logging.WARNING):
            html = _render(EYEBROW.format(value))
        assert f'<p class="manuscript-eyebrow">The {MATH_K} case</p>' in html
        assert not [r for r in caplog.records if r.levelname == "ERROR"]

    def test_plain_copy_of_the_eyebrow(self):
        assert _tree(EYEBROW.format("The $K$ case")).eyebrow == "The K case"

    def test_emphasis_in_eyebrow(self):
        html = _render(EYEBROW.format("A **bold** word"))
        assert (
            '<p class="manuscript-eyebrow">A <span class="span"><strong>bold'
            "</strong></span> word</p>"
        ) in html

    def test_escaped_tag_is_text_without_the_backslash(self):
        html = _render(EYEBROW.format(r"The \:math:K:: case"))
        assert '<p class="manuscript-eyebrow">The :math:K:: case</p>' in html

    def test_plain_eyebrow_is_unchanged(self):
        html = _render(EYEBROW.format("Note"))
        assert '<p class="manuscript-eyebrow">Note</p>' in html
        assert _tree(EYEBROW.format("Note")).eyebrow_nodes == []

    def test_html_in_eyebrow_is_text(self):
        html = _render(EYEBROW.format("a <b>c</b> $K$"))
        assert f"a &lt;b&gt;c&lt;/b&gt; {MATH_K}" in html


AUTHORS = (
    "# Title\n\n"
    ":author: {{\n  :name: {name}\n  :affiliation: {aff}\n"
    "  :author-note: {note}\n  :email: a@x.org\n  :orcid: 0000-0002-1825-0097\n}}\n::\n\n"
    ":author: {{\n  :name: Bo\n  :affiliation: Other\n  :author-note: Plain\n}}\n::\n\n"
    "Text.\n"
)


def _authors(name="Ada **B** Lovelace", aff="Lab of $K$ graphs", note="Note *one*"):
    return AUTHORS.format(name=name, aff=aff, note=note)


def _block(src: str) -> BeautifulSoup:
    return BeautifulSoup(rsm.render(src), "html.parser").select_one(".author-block")


class TestAuthor:
    def test_markup_in_name(self):
        name = _block(_authors()).select_one(".author-name-text")
        assert name.decode_contents() == (
            'Ada <span class="span"><strong>B</strong></span> Lovelace'
        )

    def test_plain_name_in_attributes(self):
        link = _block(_authors()).select_one("a.author-contact")
        assert link["aria-label"] == "Email Ada B Lovelace"

    def test_markup_in_orcid_line(self):
        line = _block(_authors()).select_one(".author-orcid")
        assert line.select_one("strong").get_text() == "B"
        assert line.get_text() == "Ada B Lovelace: 0000-0002-1825-0097"

    def test_math_in_affiliation(self):
        li = _block(_authors()).select(".author-affiliations li")[0]
        assert _flat(li.decode_contents()) == f"<sup>1</sup>Lab of {MATH_K} graphs"

    def test_emphasis_in_note(self):
        note = _block(_authors()).select("p.author-note")[0]
        assert note.decode_contents() == (
            '<sup>*</sup>Note <span class="span"><em>one</em></span>'
        )

    def test_plain_copies(self):
        author = _first(_tree(_authors()), nodes.Author)
        assert author.name == "Ada B Lovelace"
        assert author.affiliation == "Lab of K graphs"
        assert author.author_note == "Note one"

    def test_same_affiliation_with_markup_is_one_entry(self):
        src = AUTHORS.replace(":affiliation: Other", ":affiliation: {aff}").format(
            name="A", aff="Lab of $K$ graphs", note="N"
        )
        assert len(_block(src).select(".author-affiliations li")) == 1

    def test_html_in_values_is_text(self):
        block = _block(_authors(name="A <b>x</b> $K$", aff="L <b>y</b> $K$"))
        assert block.select("b") == []
        assert "A <b>x</b> " in block.select_one(".author-name-text").get_text()


BLOCKNAME = (
    "# Doc\n\n## Sec\n\n"
    ":remark: {{:label: r, :blockname: {name}}}\n  Body.\n::\n\n"
    "See :ref:r::.\n"
)


class TestBlockname:
    def test_math_in_theorem_label(self):
        html = _render(BLOCKNAME.format(name="$K$ hint"))
        assert f'<span class="span label">{MATH_K} hint 1.1.</span>' in html

    def test_math_in_reference(self):
        html = _render(BLOCKNAME.format(name="$K$ hint"))
        assert f'href="#r">{MATH_K} hint 1.1</a>' in html

    def test_plain_copy_in_menu_label(self):
        html = _render(BLOCKNAME.format(name="$K$ hint"), handrails=True)
        assert 'data-menu-label="K hint 1.1"' in html

    def test_plain_copies(self):
        tree = _processed(BLOCKNAME.format(name="$K$ hint"))
        remark = _first(tree, nodes.Remark)
        assert remark.blockname == "K hint"
        assert remark.reftext == "K hint 1.1"

    def test_math_in_caption_label(self):
        src = (
            "# Doc\n\n## Sec\n\n:figure: {\n  :label: x\n  :path: assets/a.png\n"
            "  :blockname: $K$ plot\n}\n\n:caption: A caption.\n\n::\n\nSee :ref:x::.\n"
        )
        html = _render(src)
        assert f'<span class="label">{MATH_K} plot 1.1. </span>' in html
        assert f'href="#x">{MATH_K} plot 1.1</a>' in html

    def test_plain_blockname_is_unchanged(self):
        html = _render(BLOCKNAME.format(name="Hint"))
        assert '<span class="span label">Hint 1.1.</span>' in html
        assert 'href="#r">Hint 1.1</a>' in html


REFTEXT = (
    "# Doc\n\n:lemma: {{:label: l, :reftext: {text}}}\n  Body.\n::\n\nSee :ref:l::.\n"
)


class TestReftext:
    def test_math_in_reference(self):
        html = _render(REFTEXT.format(text="the $K$ lemma"))
        assert f'href="#l">the {MATH_K} lemma</a>' in html

    def test_plain_copy(self):
        lemma = _first(_processed(REFTEXT.format(text="the $K$ lemma")), nodes.Lemma)
        assert lemma.reftext == "the K lemma"

    def test_reference_with_its_own_text_wins(self):
        src = REFTEXT.format(text="the $K$ lemma").replace(":ref:l::", ":ref:l, mine::")
        assert 'href="#l">mine</a>' in _render(src)

    def test_proof_of_reads_the_markup(self):
        src = (
            REFTEXT.format(text="the $K$ lemma").replace("See :ref:l::.\n", "")
            + "\n:proof: {:of: l}\n  P.\n::\n"
        )
        assert f'href="#l">the {MATH_K} lemma</a>' in (_render(src))

    def test_plain_reftext_is_unchanged(self):
        html = _render(REFTEXT.format(text="the main lemma"))
        assert 'href="#l">the main lemma</a>' in html


def test_link_in_a_text_value_is_left_out(caplog):
    with caplog.at_level(logging.WARNING):
        html = _render(EYEBROW.format("See :ref:lbl:: here"))
    assert '<p class="manuscript-eyebrow">See here</p>' in html
    assert any(
        r.levelname == "ERROR"
        and ":ref:" in r.getMessage()
        and "eyebrow" in r.getMessage()
        for r in caplog.records
    )


@pytest.mark.parametrize("key", ["email", "goal", "of", "icon", "label"])
def test_plain_keys_stay_plain(key):
    """These keys do not take markup, so a $ in them is not math."""
    parser = Parser(Language(tree_sitter_rsm.language()))
    cst = parser.parse(f":theorem: {{:{key}: a $x$ b}}\n  B.\n::\n".encode())
    text = str(cst.root_node)
    assert "metakey_text" in text
    assert "(math)" not in text


def _inline_types(inlines: list) -> list[str]:
    return [i["t"] for i in inlines]


class TestPandocExport:
    def test_markup_in_author_meta(self):
        meta = PandocTranslator().translate(_tree(_authors()))["meta"]
        inlines = meta["author"]["c"][0]["c"]
        assert {"t": "Strong", "c": [{"t": "Str", "c": "B"}]} in inlines
        assert "Math" in _inline_types(inlines)

    def test_math_in_reference(self):
        tree = _processed(REFTEXT.format(text="the $K$ lemma"))
        blocks = PandocTranslator().translate(tree)["blocks"]
        link = next(i for i in blocks[-1]["c"] if i["t"] == "Link")
        assert "Math" in _inline_types(link["c"][1])
