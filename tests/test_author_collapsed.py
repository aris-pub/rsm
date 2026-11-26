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
        <p class="author-names"><span class="author-name"><span class="author-name-text" data-affiliation="MIT">Author 1</span><sup data-tooltip="MIT">1</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="Harvard">Author 2</span><sup data-tooltip="Harvard">2</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="Stanford">Author 3</span><sup data-tooltip="Stanford">3</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="Berkeley">Author 4</span><sup data-tooltip="Berkeley">4</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="Yale">Author 5</span><sup data-tooltip="Yale">5</sup></span></p>
        <button type="button" class="author-summary" aria-expanded="false" hidden>5 affiliations</button>
        <div class="author-details">
        <ol class="author-affiliations">
        <li value="1"><sup>1</sup>MIT</li>
        <li value="2"><sup>2</sup>Harvard</li>
        <li value="3"><sup>3</sup>Stanford</li>
        <li value="4"><sup>4</sup>Berkeley</li>
        <li value="5"><sup>5</sup>Yale</li>
        </ol>
        </div>
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
        <p class="author-names"><span class="author-name"><span class="author-name-text" data-affiliation="MIT">Author 1</span><sup data-tooltip="MIT">1</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="Harvard">Author 2</span><sup data-tooltip="Harvard">2</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="Stanford">Author 3</span><sup data-tooltip="Stanford">3</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="Berkeley">Author 4</span><sup data-tooltip="Berkeley">4</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="Yale">Author 5</span><sup data-tooltip="Yale">5</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="Princeton">Author 6</span><sup data-tooltip="Princeton">6</sup></span></p>
        <button type="button" class="author-summary" aria-expanded="false" hidden>6 affiliations</button>
        <div class="author-details">
        <ol class="author-affiliations">
        <li value="1"><sup>1</sup>MIT</li>
        <li value="2"><sup>2</sup>Harvard</li>
        <li value="3"><sup>3</sup>Stanford</li>
        <li value="4"><sup>4</sup>Berkeley</li>
        <li value="5"><sup>5</sup>Yale</li>
        <li value="6"><sup>6</sup>Princeton</li>
        </ol>
        </div>
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
        <p class="author-names"><span class="author-name"><span class="author-name-text">Author 1</span></span>, <span class="author-name"><span class="author-name-text">Author 2</span></span>, <span class="author-name"><span class="author-name-text">Author 3</span></span>, <span class="author-name"><span class="author-name-text">Author 4</span></span>, <span class="author-name"><span class="author-name-text">Author 5</span></span>, <span class="author-name"><span class="author-name-text">Author 6</span></span>, <span class="author-name"><span class="author-name-text">Author 7</span></span>, <span class="author-name"><span class="author-name-text">Author 8</span></span>, <span class="author-name"><span class="author-name-text">Author 9</span></span>, <span class="author-name"><span class="author-name-text">Author 10</span></span></p>
        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )
