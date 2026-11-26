"""BibTeX that is outside the subset RSM reads (bead rsm-4kju).

Each entry must build, keep its other fields and its citations, and give a
warning that names the entry key, and the field when there is one.
"""

import logging
from textwrap import dedent

import pytest

import rsm
from rsm import nodes
from rsm.tsparser import TSParser


def _src(entries: str, keys: str = "a") -> str:
    return (
        "# T\n\nSee :cite:"
        + keys
        + "::.\n\n:references:\n"
        + dedent(entries).strip()
        + "\n::\n"
    )


def _build(caplog, entries: str, keys: str = "a"):
    """Render strictly and parse the source. Return the bibitems by label, the
    HTML and the warnings."""
    src = _src(entries, keys)
    caplog.set_level(logging.WARNING, logger="RSM")
    html = rsm.render(src, handrails=False, source_offsets=False, strict=True)
    msgs = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    ast = TSParser().parse(src)
    items = {b.label: b for b in ast.traverse(nodeclass=nodes.Bibitem)}
    return items, html, msgs


def _assert_cited(html: str, *keys: str) -> None:
    assert "unknown label" not in html
    for key in keys:
        assert f'class="reference cite" href="#{key}"' in html
        assert f'<li id="{key}" class="bibitem"' in html


@pytest.mark.parametrize(
    "entry",
    [
        """
        @book{a,
          keywords = {sorting},
          title = {Sorting},
          year = {1998},
          doi = {10.5555/280635}
        }
        """,
        """
        @book{a,
          title = {Sorting},
          keywords = {sorting},
          year = {1998},
          doi = {10.5555/280635}
        }
        """,
        """
        @book{a,
          title = {Sorting},
          year = {1998},
          keywords = {sorting},
          doi = {10.5555/280635}
        }
        """,
        """
        @book{a,
          title = {Sorting},
          year = {1998},
          doi = {10.5555/280635},
          keywords = {sorting}
        }
        """,
    ],
    ids=["first", "middle", "before-doi", "last"],
)
def test_unknown_field_is_skipped_with_a_warning(caplog, entry):
    items, html, msgs = _build(caplog, entry + "\n@book{b, title = {B}, year = {2000}}")
    assert set(items) == {"a", "b"}
    assert items["a"].title == "Sorting"
    assert items["a"].year == "1998"
    assert items["a"].doi == "10.5555/280635"
    assert not hasattr(items["a"], "keywords")
    assert items["b"].title == "B"
    _assert_cited(html, "a")
    assert "entry a: field keywords is not used, skipped" in msgs


def test_several_unknown_fields_each_warn(caplog):
    items, html, msgs = _build(
        caplog,
        """
        @article{a,
          abstract = {Long text.},
          title = {T},
          isbn = {123},
          year = {2000}
        }
        """,
    )
    assert items["a"].title == "T"
    assert items["a"].year == "2000"
    _assert_cited(html, "a")
    assert "entry a: field abstract is not used, skipped" in msgs
    assert "entry a: field isbn is not used, skipped" in msgs


@pytest.mark.parametrize("where", ["first", "last", "only"])
def test_value_in_quotes_is_skipped_with_a_warning(caplog, where):
    entry = {
        "first": '@article{a, title = "Q", year = {2000}}',
        "last": '@article{a, year = {2000}, title = "Q"}',
        "only": '@article{a, title = "Q"}',
    }[where]
    items, html, msgs = _build(caplog, entry + "\n@book{b, title = {B}}")
    assert set(items) == {"a", "b"}
    assert items["a"].title == ""
    if where != "only":
        assert items["a"].year == "2000"
    _assert_cited(html, "a")
    assert any(
        m.startswith("entry a: field title is in quotes, skipped") and "braces" in m
        for m in msgs
    ), msgs


@pytest.mark.parametrize(
    "value, want",
    [
        ("{A {B} C}", "A B C"),
        ("{Erd\\H{o}s, Paul}", "Erd\\Hos, Paul"),
        ('{Erd{\\"o}s, Paul}', 'Erd\\"os, Paul'),
        ("{{A {deep {nest}}} end}", "A deep nest end"),
    ],
)
def test_braces_inside_a_value_are_ignored(caplog, value, want):
    items, html, msgs = _build(
        caplog, f"@article{{a, author = {value}, year = {{1959}}, title = {{T}}}}"
    )
    assert items["a"].author == want
    assert items["a"].year == "1959"
    assert items["a"].title == "T"
    _assert_cited(html, "a")
    warning = [m for m in msgs if m.startswith("entry a: field author")]
    assert len(warning) == 1, msgs
    assert "braces" in warning[0]
    assert "ö" in warning[0]


def test_value_without_inner_braces_gives_no_brace_warning(caplog):
    items, html, msgs = _build(caplog, "@article{a, title = {T}, year = {1959}}")
    assert items["a"].title == "T"
    assert not any("braces" in m for m in msgs), msgs


def test_string_definitions_are_skipped_with_a_warning(caplog):
    items, html, msgs = _build(
        caplog,
        """
        @string{jcp = {J. Chem. Phys.}}
        @article{a, title = {A}, year = {2000}}
        @String{pr = "Phys. Rev."}
        @book{b, title = {B}, year = {2001}}
        """,
        keys="a,b",
    )
    assert set(items) == {"a", "b"}
    assert items["a"].title == "A"
    assert items["b"].title == "B"
    _assert_cited(html, "a", "b")
    assert any(m.startswith("@string jcp is not used, skipped") for m in msgs), msgs
    assert any(m.startswith("@string pr is not used, skipped") for m in msgs), msgs


def test_bare_word_value_is_skipped_with_a_warning(caplog):
    items, html, msgs = _build(
        caplog, "@article{a, title = {A}, journal = jcp, year = 2000, volume = {3}}"
    )
    assert items["a"].title == "A"
    assert items["a"].journal == ""
    assert not items["a"].year
    assert items["a"].volume == "3"
    _assert_cited(html, "a")
    for field in ("journal", "year"):
        assert any(
            m.startswith(f"entry a: field {field} is not in braces, skipped")
            and "braces" in m
            for m in msgs
        ), msgs


@pytest.mark.parametrize("kind, want", [("Article", "article"), ("BOOK", "book")])
def test_kind_in_capitals_is_read(caplog, kind, want):
    items, html, msgs = _build(caplog, f"@{kind}{{a, title = {{A}}, year = {{2000}}}}")
    assert items["a"].kind == want
    assert items["a"].title == "A"
    _assert_cited(html, "a")
    assert not any("kind" in m for m in msgs), msgs


@pytest.mark.parametrize("kind", ["manual", "online", "thesis", "Manual"])
def test_unknown_kind_is_read_as_misc(caplog, kind):
    items, html, msgs = _build(caplog, f"@{kind}{{a, title = {{A}}, year = {{2000}}}}")
    assert items["a"].kind == "misc"
    assert items["a"].title == "A"
    assert items["a"].year == "2000"
    _assert_cited(html, "a")
    assert f"entry a: kind @{kind.lower()} is not known to RSM, read as @misc" in msgs


def test_field_name_in_capitals_is_read(caplog):
    items, html, msgs = _build(caplog, "@article{a, Title = {A}, YEAR = {2000}}")
    assert items["a"].title == "A"
    assert items["a"].year == "2000"
    assert not any("not used" in m for m in msgs), msgs


@pytest.mark.parametrize(
    "entry",
    ["@online{a, title = {A},}", "@online{a,\n  title = {A},\n}"],
    ids=["one-line", "lines"],
)
def test_one_field_with_a_trailing_comma_is_read(caplog, entry):
    items, html, msgs = _build(caplog, entry)
    assert items["a"].title == "A"
    _assert_cited(html, "a")
    assert not any("cannot read" in m for m in msgs), msgs


@pytest.mark.parametrize(
    "entries",
    [
        "@comment{x}\n@article{a, title = {A}}",
        "@article{a, title = {A}}\n@comment{x}",
        "@COMMENT{some {nested} text, with = signs}\n@article{a, title = {A}}",
    ],
    ids=["before", "after", "nested"],
)
def test_comment_entry_is_skipped_without_a_warning(caplog, entries):
    items, html, msgs = _build(caplog, entries)
    assert set(items) == {"a"}
    assert items["a"].title == "A"
    _assert_cited(html, "a")
    assert not any("comment" in m.lower() for m in msgs), msgs
    assert not any("cannot read" in m for m in msgs), msgs


def test_comment_entry_alone_builds(caplog):
    src = "# T\n\nText.\n\n:references:\n@comment{x}\n::\n"
    caplog.set_level(logging.WARNING, logger="RSM")
    rsm.render(src, handrails=False, source_offsets=False, strict=True)
    msgs = [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING]
    assert msgs == []


def _unreadable_entry_warnings(caplog, entries: str) -> list[str]:
    src = _src(entries)
    caplog.set_level(logging.WARNING, logger="RSM")
    TSParser().parse(src)
    msgs = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert not any("Point" in m for m in msgs), msgs
    return [m for m in msgs if "cannot read this entry" in m]


def test_unreadable_entry_warning_names_the_key_and_the_line(caplog):
    # The value of title has no closing quote, so the whole entry is an ERROR.
    warnings = _unreadable_entry_warnings(caplog, '@article{a,\n  title = "Q\n}')
    assert len(warnings) == 1, warnings
    assert warnings[0].startswith("entry a: ")
    # The entry starts on line 6 of the source made by _src.
    assert "line 6, column 1" in warnings[0]


def test_unreadable_entry_warning_without_a_key_names_the_line(caplog):
    # A stray closing brace makes an ERROR that holds no entry key.
    warnings = _unreadable_entry_warnings(caplog, "}\n@book{b, title = {B}}")
    assert len(warnings) == 1, warnings
    assert "line 6, column 1" in warnings[0]


@pytest.mark.parametrize(
    "value",
    ["{% off}", "{A {B}% off}"],
    ids=["after-opening-brace", "after-inner-brace"],
)
def test_value_cut_at_a_percent_sign_warns(caplog, value):
    src = _src(f"@article{{a,\n  title = {value},\n  year = {{2000}}\n}}")
    caplog.set_level(logging.WARNING, logger="RSM")
    TSParser().parse(src)
    msgs = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    warning = [m for m in msgs if m.startswith("entry a: field title")]
    assert len(warning) == 1, msgs
    assert "%" in warning[0]
    assert "\\%" in warning[0]


def test_value_with_a_percent_sign_in_the_text_gives_no_percent_warning(caplog):
    items, html, msgs = _build(caplog, "@article{a, title = {Sales up 50% in a year}}")
    assert items["a"].title == "Sales up 50% in a year"
    assert not any("%" in m for m in msgs), msgs


@pytest.mark.parametrize("field", ["title", "author", "journal"])
def test_escaped_percent_sign_in_a_value_is_a_percent_sign_in_the_page(caplog, field):
    entry = "@article{a, title = {T}, author = {A}, journal = {J}, year = {2000}}"
    entry = entry.replace(f"{field} = {{", f"{field} = {{50\\% off ")
    items, html, msgs = _build(caplog, entry)
    assert getattr(items["a"], field).startswith("50% off")
    assert "50% off" in html
    assert "\\%" not in html
