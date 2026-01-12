"""Tests for advanced author features: affiliation numbering and note symbols."""

from conftest import compare_have_want


def test_two_authors_same_affiliation():
    """Two authors with same affiliation: no superscripts (only 1 unique)."""
    compare_have_want(
        have="""\
        # Test

        :author: {
          :name: Alice
          :affiliation: MIT
        }
        ::

        :author:{
          :name: Bob
          :affiliation: MIT
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

        <p>Alice</p>

        <p>MIT</p>
        </div>
        </div>

        <div class="author" data-nodeid="2">

        <div class="paragraph">

        <p>Bob</p>

        <p>MIT</p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_two_authors_different_affiliations():
    """Two authors with different affiliations should get different numbers."""
    compare_have_want(
        have="""\
        # Test

        :author: {
          :name: Alice
          :affiliation: MIT
        }
        ::

        :author: {
          :name: Bob
          :affiliation: Harvard
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

        <p>Alice<sup>1</sup></p>

        <p><sup>1</sup>MIT</p>
        </div>
        </div>

        <div class="author" data-nodeid="2">

        <div class="paragraph">

        <p>Bob<sup>2</sup></p>

        <p><sup>2</sup>Harvard</p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_three_authors_mixed_affiliations():
    """Three authors: two share affiliation, one different."""
    compare_have_want(
        have="""\
        # Test

        :author: {
          :name: Alice
          :affiliation: MIT
        }
        ::

        :author:{
          :name: Bob
          :affiliation: Harvard
        }
        ::

        :author:{
          :name: Carol
          :affiliation: MIT
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

        <p>Alice<sup>1</sup></p>

        <p><sup>1</sup>MIT</p>
        </div>
        </div>

        <div class="author" data-nodeid="2">

        <div class="paragraph">

        <p>Bob<sup>2</sup></p>

        <p><sup>2</sup>Harvard</p>
        </div>
        </div>

        <div class="author" data-nodeid="3">

        <div class="paragraph">

        <p>Carol<sup>1</sup></p>

        <p><sup>1</sup>MIT</p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_author_with_no_affiliation():
    """Author without affiliation should not get a number."""
    compare_have_want(
        have="""\
        # Test

        :author:{
          :name: Alice
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

        <p>Alice</p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_two_authors_same_note():
    """Two authors with same note: no superscripts (only 1 unique)."""
    compare_have_want(
        have="""\
        # Test

        :author: {
          :name: Alice
          :author-note: Equal contribution
        }
        ::

        :author: {
          :name: Bob
          :author-note: Equal contribution
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

        <p>Alice</p>

        <p>Equal contribution</p>
        </div>
        </div>

        <div class="author" data-nodeid="2">

        <div class="paragraph">

        <p>Bob</p>

        <p>Equal contribution</p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_two_authors_different_notes():
    """Two authors with different notes should get different symbols."""
    compare_have_want(
        have="""\
        # Test

        :author: {
          :name: Alice
          :author-note: Equal contribution
        }
        ::

        :author: {
          :name: Bob
          :author-note: Now at MIT
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

        <p>Alice<sup>*</sup></p>

        <p><sup>*</sup>Equal contribution</p>
        </div>
        </div>

        <div class="author" data-nodeid="2">

        <div class="paragraph">

        <p>Bob<sup>†</sup></p>

        <p><sup>†</sup>Now at MIT</p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_author_with_affiliation_and_note():
    """Single author: no superscripts (only 1 unique affiliation and note)."""
    compare_have_want(
        have="""\
        # Test

        :author: {
          :name: Alice
          :affiliation: MIT
          :author-note: Equal contribution
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

        <p>Alice</p>

        <p>MIT</p>

        <p>Equal contribution</p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_many_notes_symbol_progression():
    """Test symbol progression: *, †, ‡, §, ¶, ‖, **, †† (with >5 authors collapsed)."""
    compare_have_want(
        have="""\
        # Test

        :author:{
          :name: A1
          :author-note: Note 1
        }
        ::

        :author:{
          :name: A2
          :author-note: Note 2
        }
        ::

        :author:{
          :name: A3
          :author-note: Note 3
        }
        ::

        :author:{
          :name: A4
          :author-note: Note 4
        }
        ::

        :author:{
          :name: A5
          :author-note: Note 5
        }
        ::

        :author:{
          :name: A6
          :author-note: Note 6
        }
        ::

        :author:{
          :name: A7
          :author-note: Note 7
        }
        ::

        :author:{
          :name: A8
          :author-note: Note 8
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

        <p>A1<sup>*</sup></p>

        <p><sup>*</sup>Note 1</p>
        </div>
        </div>

        <div class="author" data-nodeid="2">

        <div class="paragraph">

        <p>A2<sup>†</sup></p>

        <p><sup>†</sup>Note 2</p>
        </div>
        </div>

        <div class="author" data-nodeid="3">

        <div class="paragraph">

        <p>A3<sup>‡</sup></p>

        <p><sup>‡</sup>Note 3</p>
        </div>
        </div>

        <div class="author author-hidden author-toggleable" data-nodeid="4">

        <div class="paragraph">

        <p>A4<sup>§</sup></p>

        <p><sup>§</sup>Note 4</p>
        </div>
        </div>

        <div class="author author-hidden author-toggleable" data-nodeid="5">

        <div class="paragraph">

        <p>A5<sup>¶</sup></p>

        <p><sup>¶</sup>Note 5</p>
        </div>
        </div>

        <div class="author author-hidden author-toggleable" data-nodeid="6">

        <div class="paragraph">

        <p>A6<sup>‖</sup></p>

        <p><sup>‖</sup>Note 6</p>
        </div>
        </div>

        <button class="toggle-authors">Show/hide full author information</button>

        <div class="author" data-nodeid="7">

        <div class="paragraph">

        <p>A7<sup>**</sup></p>

        <p><sup>**</sup>Note 7</p>
        </div>
        </div>

        <div class="author" data-nodeid="8">

        <div class="paragraph">

        <p>A8<sup>††</sup></p>

        <p><sup>††</sup>Note 8</p>
        </div>
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_complex_author_combination():
    """Complex: 2 affiliations (show labels), 1 note (no labels)."""
    compare_have_want(
        have="""\
        # Test

        :author:{
          :name: Alice
          :affiliation: MIT
          :orcid: 0000-0001-1111-1111
          :author-note: Equal contribution
        }
        ::

        :author:{
          :name: Bob
          :affiliation: Harvard
          :author-note: Equal contribution
        }
        ::

        :author:{
          :name: Carol
          :affiliation: MIT
          :orcid: 0000-0002-2222-2222
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

        <p>Alice<sup>1</sup></p>

        <p><sup>1</sup>MIT</p>

        <p>0000-0001-1111-1111</p>

        <p>Equal contribution</p>
        </div>
        </div>

        <div class="author" data-nodeid="2">

        <div class="paragraph">

        <p>Bob<sup>2</sup></p>

        <p><sup>2</sup>Harvard</p>

        <p>Equal contribution</p>
        </div>
        </div>

        <div class="author" data-nodeid="3">

        <div class="paragraph">

        <p>Carol<sup>1</sup></p>

        <p><sup>1</sup>MIT</p>

        <p>0000-0002-2222-2222</p>
        </div>
        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
