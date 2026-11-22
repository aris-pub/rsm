"""One rule for meta blocks and inline meta (rsm-9kn).

A value runs to the next key or to the closing brace. Newlines count as spaces,
so a value may run over several lines. A comma after a pair is dropped, so
commas between pairs (and after the last one) are optional. The grammar side is covered by
tree-sitter-rsm/test/corpus/meta.txt."""

import logging

import pytest

import rsm
from rsm import nodes
from rsm.app import ParserApp


def _tree(src: str) -> nodes.Manuscript:
    return ParserApp(plain=src).run()


def _first(src: str, cls):
    return next(_tree(src).traverse(nodeclass=cls))


def _thm(meta: str) -> nodes.Theorem:
    return _first(f":theorem: {meta}\n  Body.\n::\n", nodes.Theorem)


@pytest.mark.parametrize(
    "meta",
    [
        "{:title: A, :label: t, :nonum:}",
        "{:title: A :label: t :nonum:}",
        "{\n  :title: A,\n  :label: t,\n  :nonum:\n  }",
        "{\n  :title: A\n  :label: t\n  :nonum:\n  }",
        "{:nonum:, :title: A, :label: t}",
        "{:nonum: :title: A :label: t}",
        "{:title: A, :label: t, :nonum:,}",
        "{:nonum:, :title: A, :label: t,}",
    ],
    ids=[
        "one-line-commas",
        "one-line-bare",
        "lines-commas",
        "lines-bare",
        "bool-first-comma",
        "bool-first-bare",
        "last-bool-comma",
        "last-value-comma",
    ],
)
def test_same_pairs_in_every_form(meta):
    thm = _thm(meta)
    assert thm.title == "A"
    assert thm.label == "t"
    assert thm.nonum is True


def test_ref_finds_a_label_followed_by_a_comma():
    html = rsm.render(
        ":theorem: {:label: t, :title: A}\n  Body.\n::\n\nSee :ref:t::.\n",
        handrails=False,
    )
    assert 'href="#t">Theorem 1</a>' in html


@pytest.mark.parametrize(
    "meta, title",
    [
        (
            "{\n  :title: A long title that runs\n          onto a second line\n"
            "          and a third\n  :label: t\n  }",
            "A long title that runs onto a second line and a third",
        ),
        (
            "{:title: A long title\n  that runs on, :label: t}",
            "A long title that runs on",
        ),
        (
            "{\n  :title: A long title % a note\n          onto a second line\n"
            "  :label: t\n  }",
            "A long title onto a second line",
        ),
    ],
    ids=["lines", "one-line-style", "comment"],
)
def test_value_over_several_lines(meta, title):
    thm = _thm(meta)
    assert thm.title == title
    assert thm.label == "t"


@pytest.mark.parametrize(
    "meta, title",
    [
        ("{:title: Lemma on a, b and c :label: t}", "Lemma on a, b and c"),
        ("{:title: Lemma on a, b, :label: t}", "Lemma on a, b"),
        (
            "{:title: Ratio 3:1, see http://a.org :label: t}",
            "Ratio 3:1, see http://a.org",
        ),
        ("{:title: Task #1\\: Masked LM, :label: t}", "Task #1: Masked LM"),
        ("{:title: Note :x and a:b: c :label: t}", "Note :x and a:b: c"),
        ("{:label: t :title: Ends in a comma,}", "Ends in a comma"),
    ],
    ids=[
        "mid-comma",
        "comma-before-key",
        "colons",
        "escape",
        "colon-words",
        "comma-before-brace",
    ],
)
def test_what_stays_in_a_value(meta, title):
    thm = _thm(meta)
    assert thm.title == title
    assert thm.label == "t"


def test_path_stops_at_the_next_key():
    # rsm-bmg: the path used to take in the keys after it.
    fig = _first(":figure: {:path: a.png, :scale: 0.5}\n::\n", nodes.Figure)
    assert str(fig.path) == "a.png"
    assert fig.scale == "0.5"


def test_path_with_spaces_stops_at_the_next_key():
    fig = _first(":figure: {:path: my figs/a b.png :label: f}\n::\n", nodes.Figure)
    assert str(fig.path) == "my figs/a b.png"
    assert fig.label == "f"


def test_two_words_for_a_word_key_is_reported(caplog):
    with caplog.at_level(logging.WARNING):
        _tree(":config: {:accent: dark blue :lang: en}\n::\n\nText.\n")
    assert any("dark blue" in r.getMessage() for r in caplog.records)


@pytest.mark.parametrize(
    "meta",
    [
        "{:keywords: a, b, c}",
        "{:keywords: a, b, c :label: x}",
        "{:keywords: a, b, c, :label: x}",
        "{\n  :keywords: a,\n             b, c\n  :label: x\n  }",
    ],
    ids=["alone", "then-key", "comma-before-key", "lines"],
)
def test_list_values(meta):
    abstract = _first(f":abstract: {meta}\n  Text.\n::\n", nodes.Abstract)
    assert abstract.keywords == ["a", "b", "c"]


def test_list_item_with_spaces():
    abstract = _first(
        ":abstract: {:keywords: spectral graph theory, interlacing}\n  Text.\n::\n",
        nodes.Abstract,
    )
    assert abstract.keywords == ["spectral graph theory", "interlacing"]


def test_unknown_key_is_reported_and_the_next_key_kept(caplog):
    with caplog.at_level(logging.WARNING):
        thm = _thm("{:colour: blue :label: t}")
    assert thm.label == "t"
    assert any(":colour:" in r.getMessage() for r in caplog.records)


def test_heading_meta_without_commas():
    sec = _first("## A title {:label: s :nonum:}\n\nBody.\n", nodes.Section)
    assert sec.title == "A title"
    assert sec.label == "s"
    assert sec.nonum is True


@pytest.mark.parametrize(
    "src",
    [
        ":paragraph: {:title: Setup, part one, :label: p} Body.\n",
        ":paragraph: {:title: Setup, part one :label: p} Body.\n",
        ":paragraph:\n  {\n  :title: Setup,\n          part one\n  :label: p\n  } Body.\n",
    ],
    ids=["commas", "bare", "lines"],
)
def test_inline_meta(src):
    par = _first(src, nodes.Paragraph)
    assert par.title == "Setup, part one"
    assert par.label == "p"


@pytest.mark.parametrize(
    "src",
    [
        "A :span:{:strong:, :label: x}b::.\n",
        "A :span:{:strong: :label: x}b::.\n",
        "A :span:{:label: x,\n  :strong:}b::.\n",
    ],
    ids=["comma", "bare", "lines"],
)
def test_inline_meta_on_a_span(src):
    span = _first(src, nodes.Span)
    assert span.label == "x"
    assert span.strong is True


def test_text_key_with_no_value_is_an_error(caplog):
    with caplog.at_level(logging.WARNING):
        thm = _thm("{:title: :label: t}")
    assert thm.label == "t"
    assert any("Parse error in meta" in r.getMessage() for r in caplog.records)
