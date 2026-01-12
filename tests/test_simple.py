from conftest import EMPTY_WANT, compare_have_want


def test_no_manuscript_title():
    compare_have_want(
        have="""\
        Lorem ipsum.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Lorem ipsum.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_manuscript_title():
    compare_have_want(
        have="""\
        # My Title

        Lorem ipsum.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>Lorem ipsum.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_manuscript_with_shortcut_title():
    compare_have_want(
        have="""\
        # Title
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Title</h1>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_manuscript_meta():
    compare_have_want(
        have="""\
        # My Title {
          :label: mylbl
          :title: My Title
          :date: 2022-03-29
        }
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div id="mylbl" class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <p class="manuscript-date">March 29, 2022</p>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_section_header():
    compare_have_want(
        have="""\
        Lorem ipsum.

        ## section title

        Lorem ipsum.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Lorem ipsum.</p>

        </div>

        <section class="section level-2" data-nodeid="3">

        <h2>1. section title</h2>

        <div class="paragraph" data-nodeid="4">

        <p>Lorem ipsum.</p>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )
