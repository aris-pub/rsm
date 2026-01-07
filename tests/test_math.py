from conftest import compare_have_want


def test_display_alone():
    compare_have_want(
        have="""\
        :rsm:

        Some math
        :mathblock:
          :label: eqn-plus
          :types: smallequation

          2 + 2 = 4
        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Some math </p>
        <div id="eqn-plus" class="mathblock smallequation" data-nodeid="3">
        $$
        2 + 2 = 4
        $$
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_inline_no_meta():
    compare_have_want(
        have="""\
        :rsm:

        This paragraph contains inline math :math: 2 + 2 = 4::.

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph contains inline math <span class="math" data-nodeid="3">\(2 + 2 = 4\)</span>.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_inline_with_meta():
    compare_have_want(
        have="""\
        :rsm:

        This paragraph contains inline math :math: {:label: bar, :types: smallequation} 2 + 2
        = 4::.

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph contains inline math <span id="bar" class="math smallequation" data-nodeid="3">\(2 + 2
        = 4\)</span>.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_math_with_shortcuts():
    compare_have_want(
        have=r"""        :rsm:

        ## My Section

        When $a \ne 0$, there are two solutions to $ax^2 + bx + c = 0$ and they are
        $$x = {-b \pm \sqrt{b^2-4ac} \over 2a}.$$

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. My Section</h2>

        <div class="paragraph" data-nodeid="2">

        <p>When <span class="math" data-nodeid="4">\(a \ne 0\)</span>, there are two solutions to <span class="math" data-nodeid="7">\(ax^2 + bx + c = 0\)</span> and they are </p>
        <div class="mathblock" data-nodeid="10">
        $$
        x = {-b \pm \sqrt{b^2-4ac} \over 2a}.
        $$
        </div>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_math_ref():
    compare_have_want(
        have=r"""        :rsm:

        ## My Section

        This is some inline $2+2=4$ math.  And then some display math.
        :mathblock:
          :label: eqn-foo
          2+2=4
        ::
        And now we refer to :ref:eqn-foo::.

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. My Section</h2>

        <div class="paragraph" data-nodeid="2">

        <p>This is some inline <span class="math" data-nodeid="4">\(2+2=4\)</span> math.  And then some display math. </p>
        <div id="eqn-foo" class="mathblock" data-nodeid="7">
        $$
        2+2=4
        $$
        </div>
        <p> And now we refer to <a class="reference" href="#eqn-foo">(1.1)</a>.</p>
        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_mathblock_nonum():
    compare_have_want(
        have=r"""        :rsm:

        Some math
        :mathblock:
          :nonum:
          2+2=4
        ::

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Some math </p>
        <div class="mathblock" data-nodeid="3">
        $$
        2+2=4
        $$
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_mathblock_nonum_with_shortcut():
    compare_have_want(
        have=r"""        :rsm:

        Some math
        $$
          :nonum:
          2+2=4
        $$

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Some math </p>
        <div class="mathblock" data-nodeid="3">
        $$
        2+2=4
        $$
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_unclosed_dollar_sign():
    compare_have_want(
        have=r"""        :rsm:

        There are three dollar signs here $2+2 $= 0$.

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>There are three dollar signs here <span class="math" data-nodeid="3">\(2+2\)</span>= 0 [CST error at (2, 43) - (2, 44)] .</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
