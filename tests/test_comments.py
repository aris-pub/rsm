from conftest import EMPTY_WANT, compare_have_want


def test_comment_one_line_comment():
    compare_have_want(
        have="""\
        :rsm:

        % comment

        ::
        """,
        want=EMPTY_WANT,
    )


def test_comment_multi_line_comment():
    compare_have_want(
        have="""\
        :rsm:

        % this is a
        % multi line comment

        ::
        """,
        want=EMPTY_WANT,
    )


def test_escape_comment_delimiter():
    compare_have_want(
        have=r"""        :rsm:

        \% This is not a comment.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>% This is not a comment.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_end_of_line_comment():
    compare_have_want(
        have="""\
        :rsm:

        Foo.% this is a comment at the end of a line

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Foo.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_percent_within_math_is_not_a_comment():
    compare_have_want(
        have=r"""        :rsm:

        $10\%$ this is not a comment

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="math" data-nodeid="2">\(10\%\)</span> this is not a comment</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_broken_paragraph():
    compare_have_want(
        have="""
        :rsm:

        This is a paragraph
        % with a comment
        in the middle

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a paragraph in the middle</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
