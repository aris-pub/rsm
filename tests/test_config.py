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

        <div class="paragraph" data-nodeid="1">

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

        <div class="paragraph" data-nodeid="1">

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
        ::

        ## Section Two

        :theorem: Another theorem.
        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Title</h1>

        <section class="section level-2" data-nodeid="1">

        <h2>1. Section One</h2>

        <div class="theorem" data-nodeid="2">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.</span></p>

        </div>

        <div class="paragraph" data-nodeid="3">

        <p>Theorem content.</p>

        </div>

        </div>

        </section>

        <section class="section level-2" data-nodeid="5">

        <h2>2. Section Two</h2>

        <div class="theorem" data-nodeid="6">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 2.</span></p>

        </div>

        <div class="paragraph" data-nodeid="7">

        <p>Another theorem.</p>

        </div>

        </div>

        </section>

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
        ::

        ## Section Two

        :theorem: Another theorem.
        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Title</h1>

        <section class="section level-2" data-nodeid="1">

        <h2>1. Section One</h2>

        <div class="theorem" data-nodeid="2">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.1.</span></p>

        </div>

        <div class="paragraph" data-nodeid="3">

        <p>Theorem content.</p>

        </div>

        </div>

        </section>

        <section class="section level-2" data-nodeid="5">

        <h2>2. Section Two</h2>

        <div class="theorem" data-nodeid="6">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 2.1.</span></p>

        </div>

        <div class="paragraph" data-nodeid="7">

        <p>Another theorem.</p>

        </div>

        </div>

        </section>

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
        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Title</h1>

        <section class="section level-2" data-nodeid="1">

        <h2>Section</h2>

        <div class="theorem" data-nodeid="2">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem.</span></p>

        </div>

        <div class="paragraph" data-nodeid="3">

        <p>Theorem content.</p>

        </div>

        </div>

        </section>

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
    from rsm.tsparser import TSParser, RSMParserError

    with pytest.raises(RSMParserError, match="Multiple config blocks"):
        TSParser().parse("""\
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
        """)


def test_config_invalid_numbering_value():
    """Test that invalid numbering value raises an error."""
    from rsm.tsparser import TSParser, RSMParserError

    with pytest.raises(RSMParserError, match="Invalid numbering value"):
        TSParser().parse("""\
        # Title

        :config: {
          :numbering: invalid
        }
        ::

        ## Content
        """)
