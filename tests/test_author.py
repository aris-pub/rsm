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
        <p class="author-names"><span class="author-name"><span class="author-name-text" data-affiliation="Max Planck Institute for Mathematics in the Sciences">Leo Torres</span><a class="author-contact" href="mailto:leo@leotrs.com" aria-label="Email Leo Torres" data-tip="Email Leo Torres"><span class="icon mail" aria-hidden="true"><svg overflow="visible"><use href="#hr-icon-mail" width="100%" height="100%"/></svg></span></a></span></p>
        <button type="button" class="author-summary" aria-expanded="false" hidden>1 affiliation<span aria-hidden="true"> · </span>1 email</button>
        <div class="author-details">
        <ol class="author-affiliations">
        <li>Max Planck Institute for Mathematics in the Sciences</li>
        </ol>
        <p class="author-correspondence">Correspondence: <a href="mailto:leo@leotrs.com">leo@leotrs.com</a></p>
        </div>
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

        <h1>The Perron <span class="hyphenated">non-backtracking</span> eigenvalue after node addition</h1>

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
        <p class="author-names"><span class="author-name"><span class="author-name-text" data-affiliation="Some University">Leo Torres</span><a class="author-contact" href="https://orcid.org/0000-0001-2345-6789" aria-label="ORCID record of Leo Torres" data-tip="ORCID record of Leo Torres"><span class="icon orcid" aria-hidden="true"><svg overflow="visible"><use href="#hr-icon-orcid" width="100%" height="100%"/></svg></span></a></span></p>
        <button type="button" class="author-summary" aria-expanded="false" hidden>1 affiliation<span aria-hidden="true"> · </span>1 ORCID</button>
        <div class="author-details">
        <ol class="author-affiliations">
        <li>Some University</li>
        </ol>
        <p class="author-orcid">Leo Torres: <span class="hyphenated">0000-0001-2345-6789</span></p>
        </div>
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
        <p class="author-names"><span class="author-name"><span class="author-name-text" data-note="Equal contribution">Leo Torres</span></span></p>
        <button type="button" class="author-summary" aria-expanded="false" hidden>1 note</button>
        <div class="author-details">
        <p class="author-note">Equal contribution</p>
        </div>
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
        <p class="author-names"><span class="author-name"><span class="author-name-text" data-affiliation="Department of Mathematics University of Somewhere Building 123">Leo Torres</span></span></p>
        <button type="button" class="author-summary" aria-expanded="false" hidden>1 affiliation</button>
        <div class="author-details">
        <ol class="author-affiliations">
        <li>Department of Mathematics University of Somewhere Building 123</li>
        </ol>
        </div>
        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )
