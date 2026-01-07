from conftest import compare_have_want

from rsm.util import EscapedString


def test_ignore_single_char():
    esc = EscapedString(r"\:", ":")
    assert esc.find(":") == -1


def test_simple_not_escaped():
    compare_have_want(
        have="""
        :rsm:

        Warning: this is a warning.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Warning [CST error at (2, 7) - (2, 8)] this is a warning.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_simple():
    compare_have_want(
        have=r"""
        :rsm:

        Warning\: this is a warning.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Warning: this is a warning.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_colon_inside_bold():
    compare_have_want(
        have=r"""
        :rsm:

        :span: {:strong:} Warning\: :: this is a warning.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="span" data-nodeid="2"><strong>Warning:</strong></span> this is a warning.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_colon_inside_bold_no_space():
    compare_have_want(
        have=r"""
        :rsm:

        :span: {:strong:} Warning\::: this is a warning.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="span" data-nodeid="2"><strong>Warning:</strong></span> this is a warning.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_colon_inside_bold_with_shortcut():
    compare_have_want(
        have=r"""
        :rsm:

        *Warning\: *this is a warning.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="span" data-nodeid="2"><strong>Warning:</strong></span>this is a warning.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_backslash_brace_within_math():
    compare_have_want(
        have=r"""        :rsm:

        $[k]:= \{1,\ldots,k\}$

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="math" data-nodeid="2">\([k]:= \{1,\ldots,k\}\)</span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_colon_inside_manuscript_title():
    compare_have_want(
        have=r"""
        :rsm:
          :title: foo\:bar
        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>foo:bar</h1>

        </section>

        </div>

        </div>

        </body>
        """,
    )
