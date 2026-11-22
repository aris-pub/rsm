"""Meta values of the path, number, word and date kinds (rsm-92w).

The grammar checks the shape of each value. Python checks words against their
allowed values, whole numbers, and real dates. A value that fails a check is
logged as an error with its line and the allowed values, the key keeps its
default, and the build goes on.
"""

import logging

import pytest

import rsm
import rsm.nodes as nodes
from rsm.tsparser import TSParser


def _parse(src):
    return TSParser().parse(src)


def _first(tree, nodeclass):
    return next(iter(tree.traverse(nodeclass=nodeclass)))


def _value_errors(caplog, key):
    return [
        r
        for r in caplog.records
        if r.levelno == logging.ERROR and f"Invalid value for :{key}:" in r.getMessage()
    ]


def _config(body):
    return f"# T\n\n:config: {{\n{body}}}\n::\n\n## One\n\nText.\n"


def test_one_line_block_meta_path_stops_at_the_brace():
    tree = _parse(":figure: {:path: a.png}\n::\n")
    assert str(_first(tree, nodes.Figure).path) == "a.png"


def test_path_may_contain_spaces():
    tree = _parse(":figure: {\n  :path: my figs/a b.png\n  :label: f\n}\n::\n")
    fig = _first(tree, nodes.Figure)
    assert str(fig.path) == "my figs/a b.png"
    assert fig.label == "f"


def test_inline_meta_word_stops_at_the_comma():
    tree = _parse("A :span: {:lang: en, :label: x} hi :: b.\n")
    span = _first(tree, nodes.Span)
    assert span.lang == "en"
    assert span.label == "x"


def test_scale_and_dates_parse():
    tree = _parse(
        "# T\n\n:config: {\n  :override-date: 2024-01-15\n  :toc-depth: 2\n}\n::\n\n"
        ":figure: {\n  :path: a.png\n  :scale: 0.5\n}\n::\n"
    )
    assert tree.date == "2024-01-15"
    assert tree.toc_depth == "2"
    assert _first(tree, nodes.Figure).scale == "0.5"


def test_code_lang_is_not_checked_as_a_language_code(caplog):
    tree = _parse("A :code:{:lang: python} x = 1 :: b.\n")
    assert _first(tree, nodes.Code).lang == "python"
    assert not _value_errors(caplog, "lang"), caplog.text


@pytest.mark.parametrize(
    "key,bad,attr,default,allowed",
    [
        ("accent", "teal", "accent", "blue", "blue, red, green"),
        ("numbering", "chapter", "numbering", "section", "document, section, none"),
        ("typography", "mono", "typography", "sans-serif", "sans-serif, serif"),
        (
            "citation-style",
            "sideways",
            "citation_style",
            "numeric",
            "numeric, parens-author-year, author-parens-year",
        ),
        ("lang", "invalid123", "lang", "en", "a language code"),
    ],
)
def test_bad_config_word_is_logged_and_default_used(
    caplog, key, bad, attr, default, allowed
):
    src = _config(f"  :label: c\n  :{key}: {bad}\n")
    tree = _parse(src)
    assert getattr(tree, attr) == default
    records = _value_errors(caplog, key)
    assert len(records) == 1, caplog.text
    rec = records[0]
    msg = rec.getMessage()
    assert "line 5" in msg and bad in msg and allowed in msg, msg
    assert (rec.start_row, rec.start_col, rec.end_row) == (5, 3, 5), caplog.text


def test_bad_config_word_does_not_stop_the_build(caplog):
    html = rsm.render(_config("  :accent: teal\n"), handrails=False)
    assert "Text." in html
    assert 'data-accent="blue"' in html


@pytest.mark.parametrize(
    "key,bad,allowed",
    [
        ("view", "graph", "list, tree"),
        ("orientation", "sideways", "horizontal, vertical"),
    ],
)
def test_bad_toc_word_is_logged_and_default_used(caplog, key, bad, allowed):
    tree = _parse(f":toc: {{\n  :{key}: {bad}\n}}\n::\n\n## One\n\nText.\n")
    toc = _first(tree, nodes.Contents)
    assert (toc.view, toc.orientation) == ("list", "vertical")
    records = _value_errors(caplog, key)
    assert len(records) == 1, caplog.text
    msg = records[0].getMessage()
    assert "line 2" in msg and bad in msg and allowed in msg, msg


def test_word_with_a_space_is_logged(caplog):
    tree = _parse(_config("  :accent: dark blue\n  :numbering: none\n"))
    assert tree.accent == "blue"
    assert tree.numbering == "none"
    records = _value_errors(caplog, "accent")
    assert len(records) == 1, caplog.text
    assert "line 4" in records[0].getMessage(), caplog.text
    assert "dark blue" in records[0].getMessage(), caplog.text


@pytest.mark.parametrize(
    "src",
    [
        ":figure: {\n  :path: a.png\n  :scale: abc\n  :label: f\n}\n::\n",
        ":figure: {\n  :scale: abc\n  :path: a.png\n  :label: f\n}\n::\n",
    ],
    ids=["middle", "first"],
)
def test_bad_scale_is_logged_and_default_used(caplog, src):
    fig = _first(_parse(src), nodes.Figure)
    assert fig.scale == 1.0
    assert str(fig.path) == "a.png"
    assert fig.label == "f"
    records = _value_errors(caplog, "scale")
    assert len(records) == 1, caplog.text
    msg = records[0].getMessage()
    assert "abc" in msg and "a number" in msg, msg


def test_bad_scale_as_the_only_key_is_logged(caplog):
    html = rsm.render(":figure: {:scale: abc}\n::\n\nText.\n", handrails=False)
    records = _value_errors(caplog, "scale")
    assert len(records) == 1, caplog.text
    assert "line 1" in records[0].getMessage(), caplog.text
    assert "Text." in html
    assert "[CST error" not in html


@pytest.mark.parametrize("bad", ["2.5", "two"])
def test_bad_toc_depth_is_logged_and_default_used(caplog, bad):
    tree = _parse(_config(f"  :toc-depth: {bad}\n  :accent: red\n"))
    assert not hasattr(tree, "toc_depth")
    assert tree.accent == "red"
    records = _value_errors(caplog, "toc-depth")
    assert len(records) == 1, caplog.text
    msg = records[0].getMessage()
    assert bad in msg and "whole number" in msg, msg


@pytest.mark.parametrize("bad", ["2024-13-40", "2024/01/02"])
def test_bad_override_date_is_logged_and_default_used(caplog, bad):
    tree = _parse(_config(f"  :override-date: {bad}\n"))
    assert tree.date is None
    records = _value_errors(caplog, "override-date")
    assert len(records) == 1, caplog.text
    msg = records[0].getMessage()
    assert bad in msg and "YYYY-MM-DD" in msg, msg


def test_no_minimap_turns_the_minimap_off():
    html = rsm.render(_config("  :no-minimap:\n"), handrails=True, sidebar=True)
    assert 'data-minimap="false"' in html
    assert 'data-control="minimap"' not in html


@pytest.mark.parametrize("line", [":minimap: false", ":theme: dark"])
def test_removed_keys_are_unknown(caplog, line):
    src = _config(f"  :accent: red\n  {line}\n")
    html = rsm.render(src, handrails=True, sidebar=True)
    assert 'data-accent="red"' in html
    assert 'data-minimap="false"' not in html
    key = line.split(":")[1]
    assert f"Unknown meta key :{key}:" in caplog.text, caplog.text


@pytest.mark.parametrize(
    "src",
    [
        "Ordered list:\n1. First step\n2. Second step\n",
        "Some text\n2 apples and\n3 pears.\n",
        "Year\n2025 was long.\n",
    ],
)
def test_lines_that_start_with_a_number_parse(src):
    cst = TSParser().parse(src, abstractify=False)
    assert not cst.root_node.has_error


def test_date_with_one_digit_month_is_logged(caplog):
    with caplog.at_level(logging.ERROR):
        tree = _parse(_config(":override-date: 2025-1-05"))
    assert _value_errors(caplog, "override-date")
    assert not getattr(tree, "date", None)
