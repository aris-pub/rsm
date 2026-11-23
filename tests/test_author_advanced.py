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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author-block">
        <p class="author-names"><span class="author-name">Alice</span>, <span class="author-name">Bob</span></p>
        <details class="author-details">
        <summary><span class="author-count">1 affiliation</span><div class="icon chevron-down"><svg overflow="visible"><use href="#hr-icon-chevron-down" width="100%" height="100%"/></svg></div></summary>
        <ol class="author-affiliations">
        <li>MIT</li>
        </ol>
        </details>
        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author-block">
        <p class="author-names"><span class="author-name">Alice<sup data-tooltip="MIT">1</sup></span>, <span class="author-name">Bob<sup data-tooltip="Harvard">2</sup></span></p>
        <details class="author-details">
        <summary><span class="author-count">2 affiliations</span><div class="icon chevron-down"><svg overflow="visible"><use href="#hr-icon-chevron-down" width="100%" height="100%"/></svg></div></summary>
        <ol class="author-affiliations">
        <li value="1"><sup>1</sup>MIT</li>
        <li value="2"><sup>2</sup>Harvard</li>
        </ol>
        </details>
        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author-block">
        <p class="author-names"><span class="author-name">Alice<sup data-tooltip="MIT">1</sup></span>, <span class="author-name">Bob<sup data-tooltip="Harvard">2</sup></span>, <span class="author-name">Carol<sup data-tooltip="MIT">1</sup></span></p>
        <details class="author-details">
        <summary><span class="author-count">2 affiliations</span><div class="icon chevron-down"><svg overflow="visible"><use href="#hr-icon-chevron-down" width="100%" height="100%"/></svg></div></summary>
        <ol class="author-affiliations">
        <li value="1"><sup>1</sup>MIT</li>
        <li value="2"><sup>2</sup>Harvard</li>
        </ol>
        </details>
        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author-block">
        <p class="author-names"><span class="author-name">Alice</span></p>
        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author-block">
        <p class="author-names"><span class="author-name">Alice</span>, <span class="author-name">Bob</span></p>
        <details class="author-details">
        <summary><span class="author-count">1 note</span><div class="icon chevron-down"><svg overflow="visible"><use href="#hr-icon-chevron-down" width="100%" height="100%"/></svg></div></summary>
        <p class="author-note">Equal contribution</p>
        </details>
        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author-block">
        <p class="author-names"><span class="author-name">Alice<sup data-tooltip="Equal contribution">*</sup></span>, <span class="author-name">Bob<sup data-tooltip="Now at MIT">†</sup></span></p>
        <details class="author-details">
        <summary><span class="author-count">2 notes</span><div class="icon chevron-down"><svg overflow="visible"><use href="#hr-icon-chevron-down" width="100%" height="100%"/></svg></div></summary>
        <p class="author-note"><sup>*</sup>Equal contribution</p>
        <p class="author-note"><sup>†</sup>Now at MIT</p>
        </details>
        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author-block">
        <p class="author-names"><span class="author-name">Alice</span></p>
        <details class="author-details">
        <summary><span class="author-count">1 affiliation</span><span class="author-count">1 note</span><div class="icon chevron-down"><svg overflow="visible"><use href="#hr-icon-chevron-down" width="100%" height="100%"/></svg></div></summary>
        <ol class="author-affiliations">
        <li>MIT</li>
        </ol>
        <p class="author-note">Equal contribution</p>
        </details>
        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_many_notes_symbol_progression():
    """Test symbol progression: *, dagger, double-dagger, section, pilcrow, double-vertical, **, dagger-dagger."""
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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author-block">
        <p class="author-names"><span class="author-name">A1<sup data-tooltip="Note 1">*</sup></span>, <span class="author-name">A2<sup data-tooltip="Note 2">\u2020</sup></span>, <span class="author-name">A3<sup data-tooltip="Note 3">\u2021</sup></span>, <span class="author-name">A4<sup data-tooltip="Note 4">\xa7</sup></span>, <span class="author-name">A5<sup data-tooltip="Note 5">\xb6</sup></span>, <span class="author-name">A6<sup data-tooltip="Note 6">\u2016</sup></span>, <span class="author-name">A7<sup data-tooltip="Note 7">**</sup></span>, <span class="author-name">A8<sup data-tooltip="Note 8">\u2020\u2020</sup></span></p>
        <details class="author-details">
        <summary><span class="author-count">8 notes</span><div class="icon chevron-down"><svg overflow="visible"><use href="#hr-icon-chevron-down" width="100%" height="100%"/></svg></div></summary>
        <p class="author-note"><sup>*</sup>Note 1</p>
        <p class="author-note"><sup>\u2020</sup>Note 2</p>
        <p class="author-note"><sup>\u2021</sup>Note 3</p>
        <p class="author-note"><sup>\u00a7</sup>Note 4</p>
        <p class="author-note"><sup>\u00b6</sup>Note 5</p>
        <p class="author-note"><sup>\u2016</sup>Note 6</p>
        <p class="author-note"><sup>**</sup>Note 7</p>
        <p class="author-note"><sup>\u2020\u2020</sup>Note 8</p>
        </details>
        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div class="author-block">
        <p class="author-names"><span class="author-name">Alice<sup data-tooltip="MIT">1</sup><span class="icon orcid" aria-hidden="true"><svg overflow="visible"><use href="#hr-icon-orcid" width="100%" height="100%"/></svg></span></span>, <span class="author-name">Bob<sup data-tooltip="Harvard">2</sup></span>, <span class="author-name">Carol<sup data-tooltip="MIT">1</sup><span class="icon orcid" aria-hidden="true"><svg overflow="visible"><use href="#hr-icon-orcid" width="100%" height="100%"/></svg></span></span></p>
        <details class="author-details">
        <summary><span class="author-count">2 affiliations</span><span class="author-count">2 ORCIDs</span><span class="author-count">1 note</span><div class="icon chevron-down"><svg overflow="visible"><use href="#hr-icon-chevron-down" width="100%" height="100%"/></svg></div></summary>
        <ol class="author-affiliations">
        <li value="1"><sup>1</sup>MIT</li>
        <li value="2"><sup>2</sup>Harvard</li>
        </ol>
        <p class="author-note">Equal contribution</p>
        <p class="author-orcid">Alice: <span class="hyphenated">0000-0001-1111-1111</span></p>
        <p class="author-orcid">Carol: <span class="hyphenated">0000-0002-2222-2222</span></p>
        </details>
        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )
