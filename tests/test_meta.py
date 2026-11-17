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
        <span class="error" data-nodeid="1">[CST error at (3, 1) - (3, 29)]</span>
        <div class="paragraph" data-nodeid="2">

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
        Foo :span: {:class: {t1, t2}} bar :: baz.
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


def test_block_meta_continuation_line_is_logged(caplog):
    """A block meta value wrapped onto a second line is a parse error inside the
    meta. It is logged with its position, and the build goes on (rsm-sv0)."""
    src = (
        ":figure: {\n"
        "  :path: a.png\n"
        "  :alt: one\n"
        "    two\n"
        "}\n"
        "\n"
        ":caption: C.\n"
        "\n"
        "::\n"
    )
    h = rsm.render(src, handrails=False, source_offsets=False)
    records = _meta_error_records(caplog)
    assert len(records) == 1, caplog.text
    rec = records[0]
    assert rec.levelname == "ERROR"
    assert rec.name == "RSM.parse"
    assert (rec.start_row, rec.start_col, rec.end_row) == (4, 1, 4), caplog.text
    assert 'alt="one"' in h, h
    assert "[CST error" not in h, h
    assert "two" not in h, h


def test_block_meta_without_errors_logs_nothing(caplog):
    src = ":figure: {\n  :path: a.png\n  :alt: one two\n}\n\n:caption: C.\n\n::\n"
    rsm.render(src, handrails=False, source_offsets=False)
    assert not _meta_error_records(caplog), caplog.text
    assert "The CST contains errors." not in caplog.text, caplog.text


def test_block_meta_multiline_list_logs_nothing(caplog):
    src = ":abstract: {\n  :keywords: {a,\n    b}\n}\n\nX.\n\n::\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert not _meta_error_records(caplog), caplog.text
    assert "The CST contains errors." not in caplog.text, caplog.text
    assert "Keywords: a, b" in h, h


def test_block_meta_three_line_value(caplog):
    """With a third line, the parser ends the meta after the :alt: line (a
    MISSING "}" node, not an ERROR node), so nothing is reported inside the meta.
    The later lines and the caption become a paragraph inside the figure, and
    the existing warning points at the closing brace (line 6), not at "two"
    (line 4). This test records that behavior; see rsm-sv0."""
    src = (
        ":figure: {\n"
        "  :path: a.png\n"
        "  :alt: one\n"
        "    two\n"
        "    three\n"
        "}\n"
        "\n"
        ":caption: C.\n"
        "\n"
        "::\n"
    )
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert not _meta_error_records(caplog), caplog.text
    cst_warnings = [
        r for r in caplog.records if r.getMessage() == "The CST contains errors."
    ]
    assert len(cst_warnings) == 1, caplog.text
    assert cst_warnings[0].start_row == 6, caplog.text
    assert 'alt="one"' in h, h
    assert "two three" in h, h


def test_inline_meta_error_is_logged(caplog):
    """Inline meta goes through the same code as block meta, so a parse error
    inside it is logged too."""
    src = "A :span: {:title: a,, :class: b} x:: b.\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    records = _meta_error_records(caplog)
    assert len(records) == 1, caplog.text
    assert records[0].start_row == 1, caplog.text
    assert "[CST error" not in h, h
