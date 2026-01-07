from conftest import EMPTY_WANT, compare_have_want


def test_empty_manuscript():
    compare_have_want(have=":rsm: ::\n", want=EMPTY_WANT)


def test_no_eof_newline():
    compare_have_want(have=":rsm: ::", want=EMPTY_WANT)


def test_ignore_starting_space():
    compare_have_want(have="      :rsm: ::\n", want=EMPTY_WANT)


def test_ignore_starting_newline():
    compare_have_want(have="\n:rsm: ::\n", want=EMPTY_WANT)


def test_no_manuscript_title():
    compare_have_want(
        have="""\
        :rsm:

        Lorem ipsum.

        ::
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
        :rsm:
          :title: My Title

        Lorem ipsum.

        ::
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
        :rsm:
        # Title
        ::
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
        :rsm:
          :label: mylbl
          :title: My Title
          :date: 2022-03-29
        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div id="mylbl" class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_section_header():
    compare_have_want(
        have="""\
        :rsm:

        Lorem ipsum.

        :section:
          :title: section title

        Lorem ipsum.

        ::
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
