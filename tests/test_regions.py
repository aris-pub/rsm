from conftest import compare_have_want


def test_inline_cannot_contain_block():
    compare_have_want(
        have="""\
        # My Title

        This is a paragraph :span: with an inline :section: with a block. :: ::
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>
        <span class="error" data-nodeid="1">[CST error at (3, 1) - (3, 72)]</span>
        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_paragraph_ends_at_block():
    # A block tag in the middle of a paragraph's line ends the paragraph, and
    # is reported as an error at the tag (rsm-pn7).
    compare_have_want(
        have="""\
        # My Title

        This paragraph will terminate before the section starts :section: And this
        is inside the section. ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph will terminate before the section starts</p>

        </div>

        <section id="sec-1" class="section level-2" data-nodeid="3">

        <h2>1. </h2>

        <div class="paragraph" data-nodeid="4">

        <p>And this is inside the section.</p>

        </div>

        </section>
        <span class="error" data-nodeid="6">[CST error at (3, 57) - (3, 57)] </span><span class="error" data-nodeid="7">[CST error at (4, 24) - (4, 26)]</span>
        </section>

        </div>

        </main>

        </body>
        """,
    )
