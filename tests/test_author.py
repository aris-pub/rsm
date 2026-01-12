from conftest import compare_have_want


def test_simple():
    compare_have_want(
        have="""\
        # My Title {
          :label: mylbl
          :date: 2022-03-29
        }

        :author: {
          :name: Leo Torres
          :affiliation: Max Planck Institute for Mathematics in the Sciences
          :email: leo@leotrs.com
        }
        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div id="mylbl" class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <p class="manuscript-date">March 29, 2022</p>

        <div class="author" data-nodeid="1">

        <div class="paragraph">

        <p>Leo Torres</p>

        <p>Max Planck Institute for Mathematics in the Sciences</p>

        <p><a href="mailto:leo@leotrs.com">leo@leotrs.com</a></p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_empty_author():
    compare_have_want(
        have="""\
        # The Perron non-backtracking eigenvalue after node addition {
          :label: mylbl
          :date: 2022-03-29
        }

        :author: ::

        Lorem ipsum.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div id="mylbl" class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>The Perron non-backtracking eigenvalue after node addition</h1>

        <p class="manuscript-date">March 29, 2022</p>

        <div class="author" data-nodeid="1">

        </div>

        <div class="paragraph" data-nodeid="2">

        <p>Lorem ipsum.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_author_with_orcid():
    compare_have_want(
        have="""\
        # My Title

        :author: {
          :name: Leo Torres
          :affiliation: Some University
          :orcid: 0000-0001-2345-6789
        }
        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="author" data-nodeid="1">

        <div class="paragraph">

        <p>Leo Torres</p>

        <p>Some University</p>

        <p>0000-0001-2345-6789</p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_author_with_note():
    compare_have_want(
        have="""\
        # My Title

        :author: {
          :name: Leo Torres
          :author-note: Equal contribution
        }
        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="author" data-nodeid="1">

        <div class="paragraph">

        <p>Leo Torres</p>

        <p>Equal contribution</p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_author_multiline_affiliation():
    compare_have_want(
        have="""\
        # My Title

        :author: {
          :name: Leo Torres
          :affiliation: Department of Mathematics
            University of Somewhere
            Building 123
        }
        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="author" data-nodeid="1">

        <div class="paragraph">

        <p>Leo Torres</p>

        <p>Department of Mathematics</p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
