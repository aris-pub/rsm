from conftest import compare_have_want


def test_simple():
    compare_have_want(
        have="""\
        # My Title {
          :label: mylbl
        }

        :config: {
          :override-date: 2022-03-29
        }
        ::

        :author: {
          :name: Leo Torres
          :affiliation: Max Planck Institute for Mathematics in the Sciences
          :email: leo@leotrs.com
        }
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div id="mylbl" class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <p class="manuscript-date">March 29, 2022</p>

        <div class="author-block">
        <p class="author-names">Leo Torres</p>
        <details class="author-details">
        <summary><div class="icon chevron-down"><svg width="16" height="16"><use href="#hr-icon-chevron-down" width="16" height="16"/></svg></div>Affiliations</summary>
        <ol class="author-affiliations">
        <li>Max Planck Institute for Mathematics in the Sciences</li>
        </ol>
        <p class="author-correspondence">Correspondence: <a href="mailto:leo@leotrs.com">leo@leotrs.com</a></p>
        </details>
        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_empty_author():
    compare_have_want(
        have="""\
        # The Perron non-backtracking eigenvalue after node addition {
          :label: mylbl
        }

        :config: {
          :override-date: 2022-03-29
        }
        ::

        :author: ::

        Lorem ipsum.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div id="mylbl" class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>The Perron non-backtracking eigenvalue after node addition</h1>

        <p class="manuscript-date">March 29, 2022</p>

        <div class="paragraph" data-nodeid="2">

        <p>Lorem ipsum.</p>

        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="author-block">
        <p class="author-names">Leo Torres</p>
        <details class="author-details">
        <summary><div class="icon chevron-down"><svg width="16" height="16"><use href="#hr-icon-chevron-down" width="16" height="16"/></svg></div>Affiliations</summary>
        <ol class="author-affiliations">
        <li>Some University</li>
        </ol>
        <p class="author-orcid">Leo Torres: 0000-0001-2345-6789</p>
        </details>
        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="author-block">
        <p class="author-names">Leo Torres</p>
        <details class="author-details">
        <summary><div class="icon chevron-down"><svg width="16" height="16"><use href="#hr-icon-chevron-down" width="16" height="16"/></svg></div>Affiliations</summary>
        <p class="author-note">Equal contribution</p>
        </details>
        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="author-block">
        <p class="author-names">Leo Torres</p>
        <details class="author-details">
        <summary><div class="icon chevron-down"><svg width="16" height="16"><use href="#hr-icon-chevron-down" width="16" height="16"/></svg></div>Affiliations</summary>
        <ol class="author-affiliations">
        <li>Department of Mathematics</li>
        </ol>
        </details>
        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )
