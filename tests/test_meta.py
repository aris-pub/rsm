import pytest

import rsm
from conftest import compare_have_want


def test_list_with_only_one_element():
    compare_have_want(
        have="""\
        # My Title

        :paragraph: {:class: mytype} This paragraph has only one type
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph mytype" data-nodeid="1">

        <p>This paragraph has only one type</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_list_with_one_element_before_key():
    compare_have_want(
        have="""\
        # My Title

        :paragraph: {:class: mytype, :label: lbl} This paragraph has only one type,
        that appears before another key.
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div id="lbl" class="paragraph mytype" data-nodeid="1">

        <p>This paragraph has only one type, that appears before another key.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_list_no_braces():
    compare_have_want(
        have="""\
        # My Title

        :paragraph: {:class: t1, t2} This paragraph has only one type
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph t1 t2" data-nodeid="1">

        <p>This paragraph has only one type</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_inline_no_meta_start_with_tag():
    compare_have_want(
        have="""\
        :paragraph: {:label: lbl} Foo bar.

        This span starts with a tag that is not a meta key, :span: :ref:lbl,some paragraph::, instead
        it starts with a ref::.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div id="lbl" class="paragraph" data-nodeid="1">

        <p>Foo bar.</p>

        </div>

        <div class="paragraph" data-nodeid="3">

        <p>This span starts with a tag that is not a meta key, <span class="span" data-nodeid="5"><span class="inline-wrapper"><a class="reference" href="#lbl">some paragraph</a><span>,</span></span> instead it starts with a ref</span>.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_list_within_inline():
    compare_have_want(
        have="""\
        Foo :span: {:class: t1, t2} bar :: baz.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Foo <span class="span t1 t2" data-nodeid="3">bar</span> baz.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_inline_start_with_brace():
    compare_have_want(
        have=r"""
        This span starts with a brace :span: \{ ::.
        """,
        want=r"""        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This span starts with a brace <span class="span" data-nodeid="3">{</span>.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_inline_meta_with_no_space():
    compare_have_want(
        have="""\
        Foo :span: {:strong:} bar ::.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Foo <span class="span" data-nodeid="3"><strong>bar</strong></span>.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_inline_meta_with_space_in_between_braces():
    compare_have_want(
        have="""\
        Foo :span: { :strong: } bar ::.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Foo <span class="span" data-nodeid="3"><strong>bar</strong></span>.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


META_ERROR_MSG = "Parse error in meta; the text at this position was ignored."


def _meta_error_records(caplog):
    return [r for r in caplog.records if r.getMessage() == META_ERROR_MSG]


@pytest.mark.parametrize(
    "lines, alt",
    [(["one", "two"], "one two"), (["one", "two", "three"], "one two three")],
)
def test_block_meta_value_over_several_lines(caplog, lines, alt):
    """A value may run over several lines, which are joined with single
    spaces (rsm-9kn)."""
    value = "\n    ".join(lines)
    src = f":figure: {{\n  :path: a.png\n  :alt: {value}\n}}\n\n:caption: C.\n\n::\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert not _meta_error_records(caplog), caplog.text
    assert "The CST contains errors." not in caplog.text, caplog.text
    assert f'alt="{alt}"' in h, h


def test_block_meta_without_errors_logs_nothing(caplog):
    src = ":figure: {\n  :path: a.png\n  :alt: one two\n}\n\n:caption: C.\n\n::\n"
    rsm.render(src, handrails=False, source_offsets=False)
    assert not _meta_error_records(caplog), caplog.text
    assert "The CST contains errors." not in caplog.text, caplog.text


def test_block_meta_multiline_list_logs_nothing(caplog):
    src = ":abstract: {\n  :keywords: a,\n    b\n}\n\nX.\n\n::\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert not _meta_error_records(caplog), caplog.text
    assert "The CST contains errors." not in caplog.text, caplog.text
    assert "Keywords: a, b" in h, h


def test_inline_meta_error_is_logged(caplog):
    """Inline meta goes through the same code as block meta, so a parse error
    inside it is logged too."""
    src = "A :span: {:title: :class: b} x:: b.\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    records = _meta_error_records(caplog)
    assert len(records) == 1, caplog.text
    assert records[0].start_row == 1, caplog.text
    assert "[CST error" not in h, h


def _unknown_key_records(caplog, key="colour"):
    return [r for r in caplog.records if r.getMessage() == f"Unknown meta key :{key}:"]


def _render(src):
    return rsm.render(src, handrails=False, source_offsets=False)


def _assert_one_unknown_key(caplog, h, start, key="colour"):
    """The unknown key is logged once, with its 1-based position, and nothing
    about it reaches the page (rsm-15f)."""
    records = _unknown_key_records(caplog, key)
    assert len(records) == 1, caplog.text
    assert records[0].levelname == "ERROR"
    assert records[0].name == "RSM.parse"
    assert (records[0].start_row, records[0].start_col) == start, caplog.text
    assert not _meta_error_records(caplog), caplog.text
    assert "The CST contains errors." not in caplog.text, caplog.text
    assert "[CST error" not in h, h
    assert key not in h, h


def _only_unknown_key(tag, body=""):
    return f":{tag}: {{\n  :colour: blue\n}}\n{body}::\n"


def test_config_with_only_unknown_key_is_logged(caplog):
    h = _render(":config: {\n  :minimap: false\n}\n::\n\nBody.\n")
    _assert_one_unknown_key(caplog, h, (2, 3), key="minimap")
    assert "Body." in h, h


def test_theorem_with_only_unknown_key_is_logged(caplog):
    h = _render(_only_unknown_key("theorem", "Body.\n"))
    _assert_one_unknown_key(caplog, h, (2, 3))
    rec = _unknown_key_records(caplog)[0]
    assert (rec.end_row, rec.end_col) == (2, 16), caplog.text
    assert "Body." in h, h


def test_figure_with_only_unknown_key_is_logged(caplog):
    h = _render(_only_unknown_key("figure"))
    _assert_one_unknown_key(caplog, h, (2, 3))


def test_section_with_only_unknown_key_is_logged(caplog):
    h = _render(":section: {\n  :colour: blue\n}\n\nBody.\n")
    _assert_one_unknown_key(caplog, h, (2, 3))
    assert "Body." in h, h


def test_one_line_meta_with_unknown_key_is_logged(caplog):
    h = _render(":theorem: {:colour: blue}\nBody.\n::\n")
    _assert_one_unknown_key(caplog, h, (1, 12))
    assert "Body." in h, h


def test_unknown_key_without_value_is_logged(caplog):
    h = _render(":theorem: {\n  :colour:\n  :label: thm\n}\nBody.\n::\n")
    _assert_one_unknown_key(caplog, h, (2, 3))
    assert 'id="thm"' in h, h
    assert "Body." in h, h


def test_unknown_key_next_to_known_keys_is_logged(caplog):
    h = _render(
        ":theorem: {\n  :label: thm\n  :colour: blue\n  :nonum:\n}\nBody.\n::\n"
    )
    _assert_one_unknown_key(caplog, h, (3, 3))
    assert 'id="thm"' in h, h
    assert "Body." in h, h


def test_inline_meta_with_unknown_key_is_logged(caplog):
    h = _render("A :span: {:colour: blue, :strong:} word :: b.\n")
    _assert_one_unknown_key(caplog, h, (1, 11))
    assert "<strong>word</strong>" in h, h


@pytest.mark.parametrize(
    "tag,body,content",
    [
        ("mathblock", "x = 1\n", "x = 1"),
        ("codeblock", "x = 1\n", "x = 1"),
        ("algorithm", "x = 1\n", "x = 1"),
        ("notation", "\\eig $\\lambda$ eigenvalue\n", "eigenvalue"),
    ],
)
def test_asis_block_with_only_unknown_key_is_logged(caplog, tag, body, content):
    h = _render(f"# T\n\n{_only_unknown_key(tag, body)}\nAfter.\n")
    _assert_one_unknown_key(caplog, h, (4, 3))
    assert content in h, h
    assert "After." in h, h


def test_table_with_only_unknown_key_is_logged(caplog):
    h = _render(":table: {\n  :colour: blue\n}\n:tbody:\n:tr: :td: a :: ::\n::\n::\n")
    _assert_one_unknown_key(caplog, h, (2, 3))
    assert ">a</td>" in h, h


def test_manuscript_meta_with_only_unknown_key_is_logged(caplog):
    h = _render("# Title\n{\n  :colour: blue\n}\n\nBody.\n")
    _assert_one_unknown_key(caplog, h, (3, 3))
    assert "Title" in h, h
    assert "Body." in h, h


def test_known_meta_key_logs_nothing(caplog):
    h = _render(":theorem: {\n  :label: thm\n}\nBody.\n::\n")
    assert not _meta_error_records(caplog), caplog.text
    assert not [r for r in caplog.records if "Unknown meta key" in r.getMessage()]
    assert "The CST contains errors." not in caplog.text, caplog.text
    assert "Body." in h, h


@pytest.mark.parametrize("key", [":Colour:", ":colour_x:"])
def test_key_of_another_shape_as_only_key_is_logged(caplog, key):
    """The unknown-key rule matches only lowercase letters, digits and hyphens,
    so this meta does not form. The ERROR after the tag is logged once as a
    meta error (rsm-15f)."""
    h = _render(f":theorem: {{\n  {key} blue\n}}\nBody.\n::\n")
    assert len(_meta_error_records(caplog)) == 1, caplog.text
    assert not [r for r in caplog.records if "Unknown meta key" in r.getMessage()]
    assert "The CST contains errors." not in caplog.text, caplog.text
    assert "[CST error" not in h, h
    assert "Body." in h, h


def test_empty_meta_logs_nothing(caplog):
    h = _render(":theorem: {}\nBody.\n::\n")
    assert not _meta_error_records(caplog), caplog.text
    assert not [r for r in caplog.records if "Unknown meta key" in r.getMessage()]
    assert "The CST contains errors." not in caplog.text, caplog.text
    assert "Body." in h, h


def test_content_error_after_unknown_key_is_still_reported(caplog):
    """The meta forms, so its unknown key is logged. The rows that fail to parse
    (a :tr: outside :tbody:) are still reported as a CST error."""
    h = _render(":table: {\n  :colour: blue\n}\n:tr: :td: a ::\n::\n::\n")
    assert len(_unknown_key_records(caplog)) == 1, caplog.text
    assert "The CST contains errors." in caplog.text, caplog.text
    assert "[CST error" in h, h
