from conftest import compare_have_want


def test_succeeding_blankline():
    compare_have_want(
        have="""\
        :rsm:

        Foo.
        ::
        """,
        want="""\
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


def test_succeeding_blankline_with_tag():
    compare_have_want(
        have="""\
        :rsm:

        :paragraph: {:types: foo}This is a paragraph.
        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph foo" data-nodeid="1">

        <p>This is a paragraph.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_tag_no_meta():
    compare_have_want(
        have="""\
        :rsm:

        :paragraph: This is a paragraph.
        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">
        <span class="error" data-nodeid="1">[CST error at (2, 0) - (2, 11)]</span>
        <div class="paragraph" data-nodeid="2">

        <p>This is a paragraph.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_start_with_tag():
    compare_have_want(
        have="""\
        :rsm:

        :span: {:strong:} this tag :: starts the paragraph.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="span" data-nodeid="2"><strong>this tag</strong></span> starts the paragraph.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_start_with_shortcut():
    compare_have_want(
        have="""\
        :rsm:

        :|-: A claim::.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="construct claim" data-nodeid="2"><span class="keyword" data-nodeid="3">⊢</span> A claim</span>.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_simple():
    compare_have_want(
        have="""\
        :rsm:
          :label: mylbl
          :title: The Perron non-backtracking eigenvalue after node addition
          :date: 2022-03-29

        :section:
          :title: Introduction
          :label: sec-introduction
          :types: {t1, t2}

        Lorem ipsum.

        :paragraph: {:label: par1} This is a paragraph with meta data. It has several lines of text. It has several lines
        of text. It has several lines of text. It has several lines of text. It has several
        lines of text.

        :paragraph:
           {:label: par2}
        This is a paragraph with meta data. It has several lines of text. It has several lines
        of text. It has several lines of text. It has several lines of text. It has several
        lines of text.

        :paragraph: {:label: par3, :types: {a, b, c}} This is a paragraph with meta data. It
        has several lines of text. It has several lines of text. It has several lines of
        text. It has several lines of text. It has several lines of text.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div id="mylbl" class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>The Perron non-backtracking eigenvalue after node addition</h1>

        <section id="sec-introduction" class="section level-2 t1 t2" data-nodeid="1">

        <h2>1. Introduction</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Lorem ipsum.</p>

        </div>

        <div id="par1" class="paragraph" data-nodeid="4">

        <p>This is a paragraph with meta data. It has several lines of text. It has several lines of text. It has several lines of text. It has several lines of text. It has several lines of text.</p>

        </div>

        <div id="par2" class="paragraph" data-nodeid="6">

        <p>This is a paragraph with meta data. It has several lines of text. It has several lines of text. It has several lines of text. It has several lines of text. It has several lines of text.</p>

        </div>

        <div id="par3" class="paragraph a b c" data-nodeid="8">

        <p>This is a paragraph with meta data. It has several lines of text. It has several lines of text. It has several lines of text. It has several lines of text. It has several lines of text.</p>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_mathblock_inside_paragraph():
    compare_have_want(
        have="""\
        :rsm:
          :title: Mathblocks inside paragraphs

        This is a paragraph and the following equation
        $$
        2+2 = 4,
        $$
        should be part of the same paragraph still.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Mathblocks inside paragraphs</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This is a paragraph and the following equation </p>
        <div class="mathblock" data-nodeid="3">
        $$
        2+2 = 4,
        $$
        </div>
        <p> should be part of the same paragraph still.</p>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_mathblock_ending_paragraph():
    compare_have_want(
        have="""\
        :rsm:
          :title: Mathblocks inside paragraphs

        This is a paragraph that ends with an equation.
        $$
        2+2 = 4.
        $$

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Mathblocks inside paragraphs</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This is a paragraph that ends with an equation. </p>
        <div class="mathblock" data-nodeid="3">
        $$
        2+2 = 4.
        $$
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
