import pytest
from conftest import EMPTY_WANT, compare_have_want

import rsm


def test_empty_manuscript():
    compare_have_want(have=":manuscript: ::\n", want=EMPTY_WANT)


def test_no_eof_newline():
    compare_have_want(have=":manuscript: ::", want=EMPTY_WANT)


def test_ignore_starting_space():
    compare_have_want(have="      :manuscript: ::\n", want=EMPTY_WANT)


def test_ignore_starting_newline():
    compare_have_want(have="\n:manuscript: ::\n", want=EMPTY_WANT)


def test_no_manuscript_title():
    compare_have_want(
        have="""\
        :manuscript:

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
        :manuscript:
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


def test_manuscript_meta():
    compare_have_want(
        have="""\
        :manuscript:
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


def test_no_halmos():
    with pytest.raises(rsm.tsparser.RSMParserError):
        compare_have_want(
            have=""":manuscript:\n\nFoo.\n""",
            want="XXX",
        )


def test_section_header():
    compare_have_want(
        have="""\
        :manuscript:

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
