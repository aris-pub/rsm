"""Tests for collapsed author display mode (>5 authors)."""

from conftest import compare_have_want


def test_five_authors_no_collapse():
    """With exactly 5 authors, show all (no collapse)."""
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
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author" data-nodeid="1">

        <div class="paragraph">

        <p>Author 1<sup>1</sup></p>

        <p><sup>1</sup>MIT</p>
        </div>
        </div>

        <div class="author" data-nodeid="2">

        <div class="paragraph">

        <p>Author 2<sup>2</sup></p>

        <p><sup>2</sup>Harvard</p>
        </div>
        </div>

        <div class="author" data-nodeid="3">

        <div class="paragraph">

        <p>Author 3<sup>3</sup></p>

        <p><sup>3</sup>Stanford</p>
        </div>
        </div>

        <div class="author" data-nodeid="4">

        <div class="paragraph">

        <p>Author 4<sup>4</sup></p>

        <p><sup>4</sup>Berkeley</p>
        </div>
        </div>

        <div class="author" data-nodeid="5">

        <div class="paragraph">

        <p>Author 5<sup>5</sup></p>

        <p><sup>5</sup>Yale</p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_six_authors_collapsed():
    """With 6 authors, show first 3 and last 2, with expand button."""
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
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="authors-container">

        <div class="author" data-nodeid="1">

        <div class="paragraph">

        <p>Author 1<sup>1</sup></p>

        <p><sup>1</sup>MIT</p>
        </div>
        </div>

        <div class="author" data-nodeid="2">

        <div class="paragraph">

        <p>Author 2<sup>2</sup></p>

        <p><sup>2</sup>Harvard</p>
        </div>
        </div>

        <div class="author" data-nodeid="3">

        <div class="paragraph">

        <p>Author 3<sup>3</sup></p>

        <p><sup>3</sup>Stanford</p>
        </div>
        </div>

        <div class="author author-hidden author-toggleable" data-nodeid="4">

        <div class="paragraph">

        <p>Author 4<sup>4</sup></p>

        <p><sup>4</sup>Berkeley</p>
        </div>
        </div>

        <button class="toggle-authors">Show/hide full author information</button>

        <div class="author" data-nodeid="5">

        <div class="paragraph">

        <p>Author 5<sup>5</sup></p>

        <p><sup>5</sup>Yale</p>
        </div>
        </div>

        <div class="author" data-nodeid="6">

        <div class="paragraph">

        <p>Author 6<sup>6</sup></p>

        <p><sup>6</sup>Princeton</p>
        </div>
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_ten_authors_collapsed():
    """With 10 authors, show first 3 and last 2, hide middle 5."""
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
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="authors-container">

        <div class="author" data-nodeid="1">

        <div class="paragraph">

        <p>Author 1</p>
        </div>
        </div>

        <div class="author" data-nodeid="2">

        <div class="paragraph">

        <p>Author 2</p>
        </div>
        </div>

        <div class="author" data-nodeid="3">

        <div class="paragraph">

        <p>Author 3</p>
        </div>
        </div>

        <div class="author author-hidden author-toggleable" data-nodeid="4">

        <div class="paragraph">

        <p>Author 4</p>
        </div>
        </div>

        <div class="author author-hidden author-toggleable" data-nodeid="5">

        <div class="paragraph">

        <p>Author 5</p>
        </div>
        </div>

        <div class="author author-hidden author-toggleable" data-nodeid="6">

        <div class="paragraph">

        <p>Author 6</p>
        </div>
        </div>

        <div class="author author-hidden author-toggleable" data-nodeid="7">

        <div class="paragraph">

        <p>Author 7</p>
        </div>
        </div>

        <div class="author author-hidden author-toggleable" data-nodeid="8">

        <div class="paragraph">

        <p>Author 8</p>
        </div>
        </div>

        <button class="toggle-authors">Show/hide full author information</button>

        <div class="author" data-nodeid="9">

        <div class="paragraph">

        <p>Author 9</p>
        </div>
        </div>

        <div class="author" data-nodeid="10">

        <div class="paragraph">

        <p>Author 10</p>
        </div>
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
