from conftest import compare_have_want
import pytest


def test_config_simple():
    """Test basic config block."""
    compare_have_want(
        have="""\
        # My Document

        :config: {
          :toc-depth: 3
          :numbering: section
          :theme: blue
        }
        ::

        This is content.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Document</h1>

        <div class="paragraph" data-nodeid="2">

        <p>This is content.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_config_toc_depth_only():
    """Test config with only toc-depth specified."""
    compare_have_want(
        have="""\
        # Title

        :config: {
          :toc-depth: 2
        }
        ::

        Content here.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Title</h1>

        <div class="paragraph" data-nodeid="2">

        <p>Content here.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_config_numbering_document():
    """Test numbering: document mode."""
    compare_have_want(
        have="""\
        # Title

        :config: {
          :numbering: document
        }
        ::

        ## Section One

        :theorem: Theorem content.

        ## Section Two

        :theorem: Another theorem.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Section One</h1>

        <div class="theorem" data-nodeid="2">

        <div class="paragraph">

        <p><span class="label">Theorem 1. </span>Theorem content.</p>

        </div>

        </div>

        </section>

        <section class="level-2">

        <h2>Section Two</h2>

        <div class="theorem" data-nodeid="4">

        <div class="paragraph">

        <p><span class="label">Theorem 2. </span>Another theorem.</p>

        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_config_numbering_section():
    """Test numbering: section mode."""
    compare_have_want(
        have="""\
        # Title

        :config: {
          :numbering: section
        }
        ::

        ## Section One

        :theorem: Theorem content.

        ## Section Two

        :theorem: Another theorem.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Section One</h1>

        <div class="theorem" data-nodeid="2">

        <div class="paragraph">

        <p><span class="label">Theorem 1.1. </span>Theorem content.</p>

        </div>

        </div>

        </section>

        <section class="level-1">

        <h1>Section Two</h1>

        <div class="theorem" data-nodeid="4">

        <div class="paragraph">

        <p><span class="label">Theorem 2.1. </span>Another theorem.</p>

        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_config_numbering_none():
    """Test numbering: none mode."""
    compare_have_want(
        have="""\
        # Title

        :config: {
          :numbering: none
        }
        ::

        ## Section

        :theorem: Theorem content.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Section</h1>

        <div class="theorem" data-nodeid="2">

        <div class="paragraph">

        <p><span class="label">Theorem. </span>Theorem content.</p>

        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_config_anywhere_in_document():
    """Test that config can appear anywhere in document."""
    compare_have_want(
        have="""\
        # Title

        Some content.

        :config: {
          :numbering: none
        }
        ::

        More content.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>Some content.</p>

        </div>

        <div class="paragraph" data-nodeid="3">

        <p>More content.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_config_multiple_blocks_error():
    """Test that multiple config blocks raise an error."""
    # This test expects an exception to be raised
    # We'll need to adjust based on how RSM handles errors
    with pytest.raises(Exception):  # Replace with specific exception type
        from rsm import app

        app.render(
            source="""\
        # Title

        :config: {
          :numbering: section
        }
        ::

        # Content

        :config: {
          :numbering: document
        }
        ::
        """
        )


def test_config_invalid_numbering_value():
    """Test that invalid numbering value raises an error."""
    with pytest.raises(Exception):  # Replace with specific exception type
        from rsm import app

        app.render(
            source="""\
        # Title

        :config: {
          :numbering: invalid
        }
        ::

        ## Content
        """
        )
