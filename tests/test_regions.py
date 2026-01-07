from conftest import compare_have_want


def test_inline_cannot_contain_block():
    compare_have_want(
        have="""\
        :rsm:
          :title: My Title

        This is a paragraph :span: with an inline :section: with a block. :: ::

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>
        <span class="error" data-nodeid="1">[CST error at (3, 0) - (3, 71)]</span>
        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_paragraph_ends_at_block():
    compare_have_want(
        have="""\
        :rsm:
          :title: My Title

        This paragraph will terminate before the section starts :section: And this
        is inside the section. ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph will terminate before the section starts [CST error at (3, 56) - (3, 65)] And this is inside the section.</p>

        </div>
        <span class="error" data-nodeid="3">[CST error at (6, 0) - (6, 2)]</span>
        </section>

        </div>

        </div>

        </body>
        """,
    )
