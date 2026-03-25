"""Tests for author display with many authors (previously collapsed mode)."""

from conftest import compare_have_want


def test_five_authors_no_collapse():
    """With exactly 5 authors, all names shown inline."""
    compare_have_want(
        have="""\
        # Test

        :author: {
          :name: Author 1
          :affiliation: MIT
        }
        ::

        :author: {
          :name: Author 2
          :affiliation: Harvard
        }
        ::

        :author: {
          :name: Author 3
          :affiliation: Stanford
        }
        ::

        :author: {
          :name: Author 4
          :affiliation: Berkeley
        }
        ::

        :author: {
          :name: Author 5
          :affiliation: Yale
        }
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author-block">
        <p class="author-names">Author 1<sup data-tooltip="MIT">1</sup>, Author 2<sup data-tooltip="Harvard">2</sup>, Author 3<sup data-tooltip="Stanford">3</sup>, Author 4<sup data-tooltip="Berkeley">4</sup>, Author 5<sup data-tooltip="Yale">5</sup></p>
        <details class="author-details">
        <summary><div class="icon chevron-down"><svg width="16" height="16"><use href="#hr-icon-chevron-down" width="16" height="16"/></svg></div>Affiliations</summary>
        <ol class="author-affiliations">
        <li value="1"><sup>1</sup>MIT</li>
        <li value="2"><sup>2</sup>Harvard</li>
        <li value="3"><sup>3</sup>Stanford</li>
        <li value="4"><sup>4</sup>Berkeley</li>
        <li value="5"><sup>5</sup>Yale</li>
        </ol>
        </details>
        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_six_authors():
    """With 6 authors, all names shown inline with collapsible details."""
    compare_have_want(
        have="""\
        # Test

        :author: {
          :name: Author 1
          :affiliation: MIT
        }
        ::

        :author: {
          :name: Author 2
          :affiliation: Harvard
        }
        ::

        :author: {
          :name: Author 3
          :affiliation: Stanford
        }
        ::

        :author: {
          :name: Author 4
          :affiliation: Berkeley
        }
        ::

        :author: {
          :name: Author 5
          :affiliation: Yale
        }
        ::

        :author: {
          :name: Author 6
          :affiliation: Princeton
        }
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author-block">
        <p class="author-names">Author 1<sup data-tooltip="MIT">1</sup>, Author 2<sup data-tooltip="Harvard">2</sup>, Author 3<sup data-tooltip="Stanford">3</sup>, Author 4<sup data-tooltip="Berkeley">4</sup>, Author 5<sup data-tooltip="Yale">5</sup>, Author 6<sup data-tooltip="Princeton">6</sup></p>
        <details class="author-details">
        <summary><div class="icon chevron-down"><svg width="16" height="16"><use href="#hr-icon-chevron-down" width="16" height="16"/></svg></div>Affiliations</summary>
        <ol class="author-affiliations">
        <li value="1"><sup>1</sup>MIT</li>
        <li value="2"><sup>2</sup>Harvard</li>
        <li value="3"><sup>3</sup>Stanford</li>
        <li value="4"><sup>4</sup>Berkeley</li>
        <li value="5"><sup>5</sup>Yale</li>
        <li value="6"><sup>6</sup>Princeton</li>
        </ol>
        </details>
        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_ten_authors():
    """With 10 authors, all names shown inline."""
    compare_have_want(
        have="""\
        # Test

        :author:{:name: Author 1}
        ::

        :author:{:name: Author 2}
        ::

        :author:{:name: Author 3}
        ::

        :author:{:name: Author 4}
        ::

        :author:{:name: Author 5}
        ::

        :author:{:name: Author 6}
        ::

        :author:{:name: Author 7}
        ::

        :author:{:name: Author 8}
        ::

        :author:{:name: Author 9}
        ::

        :author:{:name: Author 10}
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author-block">
        <p class="author-names">Author 1, Author 2, Author 3, Author 4, Author 5, Author 6, Author 7, Author 8, Author 9, Author 10</p>
        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )
