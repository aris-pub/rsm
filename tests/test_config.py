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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Document</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This is content.</p>

        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>Content here.</p>

        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

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

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

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

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

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

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

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

        </main>

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


def test_config_accent_purple():
    """Test that accent color can be set to purple."""
    compare_have_want(
        have="""\
        # Test Document

        :config: {
          :accent: purple
        }
        ::

        Content here.
        """,
        want="""\
        <body data-accent="purple" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test Document</h1>

        <div class="paragraph" data-nodeid="1">

        <p>Content here.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_config_accent_default_blue():
    """Test that accent defaults to blue when not specified."""
    compare_have_want(
        have="""\
        # Test Document

        Content here.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test Document</h1>

        <div class="paragraph" data-nodeid="1">

        <p>Content here.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_config_accent_with_numbering():
    """Test accent works alongside other config keys."""
    compare_have_want(
        have="""\
        # Test Document

        :config: {
          :accent: red
          :numbering: document
        }
        ::

        ## Section

        :theorem: Theorem content.
        ::
        """,
        want="""\
        <body data-accent="red" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test Document</h1>

        <section class="section level-2" data-nodeid="1">

        <h2>1. Section</h2>

        <div class="theorem" data-nodeid="2">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.</span></p>

        </div>

        <div class="paragraph" data-nodeid="3">

        <p>Theorem content.</p>

        </div>

        </div>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_config_accent_all_colors():
    """Test all valid accent colors."""
    valid_colors = ["blue", "red", "green", "orange", "yellow", "purple", "pink", "gray"]
    for color in valid_colors:
        compare_have_want(
            have=f"""\
            # Test

            :config: {{
              :accent: {color}
            }}
            ::

            Content.
            """,
            want=f"""\
            <body data-accent="{color}" data-lang="en" data-typography="sans-serif">

            <main class="manuscriptwrapper">

            <div class="manuscript" data-nodeid="0">

            <section class="level-1">

            <h1>Test</h1>

            <div class="paragraph" data-nodeid="1">

            <p>Content.</p>

            </div>

            </section>

            </div>

            </main>

            </body>
            """,
        )


def test_config_invalid_accent_raises_error():
    """Test that invalid accent value raises an error."""
    from rsm.tsparser import TSParser, RSMParserError

    with pytest.raises(RSMParserError, match="Invalid accent value"):
        TSParser().parse("""\
        # Title

        :config: {
          :accent: hotpink
        }
        ::
        """)


def test_config_typography_serif():
    """Test that typography can be set to serif."""
    compare_have_want(
        have="""\
        # Test Document

        :config: {
          :typography: serif
        }
        ::

        Content here.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test Document</h1>

        <div class="paragraph" data-nodeid="1">

        <p>Content here.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_config_typography_default_sans_serif():
    """Test that typography defaults to sans-serif when not specified."""
    compare_have_want(
        have="""\
        # Test Document

        Content here.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test Document</h1>

        <div class="paragraph" data-nodeid="1">

        <p>Content here.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_config_typography_with_accent():
    """Test typography works alongside accent color."""
    compare_have_want(
        have="""\
        # Test Document

        :config: {
          :typography: serif
          :accent: purple
        }
        ::

        Content here.
        """,
        want="""\
        <body data-accent="purple" data-lang="en" data-typography="serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test Document</h1>

        <div class="paragraph" data-nodeid="1">

        <p>Content here.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_config_invalid_typography_raises_error():
    """Test that invalid typography value raises an error."""
    from rsm.tsparser import TSParser, RSMParserError

    with pytest.raises(RSMParserError, match="Invalid typography value"):
        TSParser().parse("""\
        # Title

        :config: {
          :typography: comic-sans
        }
        ::
        """)


def test_config_lang_spanish():
    """Test that lang can be set to Spanish."""
    compare_have_want(
        have="""\
        # Test Document

        :config: {
          :lang: es
        }
        ::

        Content here.
        """,
        want="""\
        <body data-accent="blue" data-lang="es" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test Document</h1>

        <div class="paragraph" data-nodeid="1">

        <p>Content here.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_config_lang_with_region():
    """Test that lang can be set with region code."""
    compare_have_want(
        have="""\
        # Test Document

        :config: {
          :lang: en-US
        }
        ::

        Content here.
        """,
        want="""\
        <body data-accent="blue" data-lang="en-US" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test Document</h1>

        <div class="paragraph" data-nodeid="1">

        <p>Content here.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_config_lang_default_en():
    """Test that lang defaults to en when not specified."""
    compare_have_want(
        have="""\
        # Test Document

        Content here.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test Document</h1>

        <div class="paragraph" data-nodeid="1">

        <p>Content here.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_config_invalid_lang_raises_error():
    """Test that invalid lang value raises an error."""
    from rsm.tsparser import TSParser, RSMParserError

    with pytest.raises(RSMParserError, match="Invalid lang value"):
        TSParser().parse("""\
        # Title

        :config: {
          :lang: invalid123
        }
        ::
        """)
