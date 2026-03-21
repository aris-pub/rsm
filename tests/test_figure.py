import base64
from textwrap import dedent

import rsm
from conftest import compare_have_want

SIMPLE_WANT = """\
<body data-accent="blue" data-lang="en" data-typography="sans-serif">

<main class="manuscriptwrapper">

<div class="manuscript" data-nodeid="0">

<section class="level-1">

<figure class="figure" data-nodeid="1">
<img src="assets/example.png" alt="Figure 1.">
<figcaption>
<span class="label">Figure 1. </span>This is the figure caption.
</figcaption>

</figure>

</section>

</div>

</main>

</body>
"""


def test_simple():
    compare_have_want(
        have="""\
        :figure: {
          :path: assets/example.png
        }
        :caption: This is the figure caption.
        ::
        """,
        want=SIMPLE_WANT,
    )


def test_simple_with_extra_whitespace():
    compare_have_want(
        have="""\
        :figure: {
          :path: assets/example.png
        }
        :caption:
          This is the figure caption.
        ::
        """,
        want=SIMPLE_WANT,
    )


def test_simple_with_multi_line_caption():
    compare_have_want(
        have="""\
        :figure: {
          :path: assets/example.png
        }

        :caption:
          This is the figure caption.
          And it spans multiple lines.

        ::
        """,
        want=SIMPLE_WANT.replace(
            "This is the figure caption.",
            "This is the figure caption. And it spans multiple lines.",
        ),
    )


def test_caption_with_inline_tags():
    compare_have_want(
        have="""\
        :figure: {
          :path: assets/example.png
        }

        :caption: This is the **figure** caption.
        ::
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <figure class="figure" data-nodeid="1">
        <img src="assets/example.png" alt="Figure 1.">
        <figcaption>
        <span class="label">Figure 1. </span>This is the <span class="span" data-nodeid="4"><strong>figure</strong></span> caption.
        </figcaption>

        </figure>

        </section>

        </div>

        </main>

        </body>
        """,
    )


# Test video asset type
def test_video_mp4():
    compare_have_want(
        have="""\
        :video:{
        :path: assets/demo.mp4
        }
        :caption: This is a video demonstration.
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <figure class="video" data-nodeid="1">
        <video controls src="assets/demo.mp4">Your browser does not support the video tag.</video>
        <figcaption>
        <span class="label">Video 1. </span>This is a video demonstration.
        </figcaption>

        </figure>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_video_youtube():
    compare_have_want(
        have="""\
        :video: {
          :path: https://www.youtube.com/watch?v=dQw4w9WgXcQ
        }
        :caption: YouTube video example.
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <figure class="video" data-nodeid="1">
        <video controls src="https://www.youtube.com/watch?v=dQw4w9WgXcQ">YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ</video>
        <figcaption>
        <span class="label">Video 1. </span>YouTube video example.
        </figcaption>

        </figure>

        </section>

        </div>

        </main>

        </body>
        """,
    )


# Test HTML asset type
def test_html_asset():
    compare_have_want(
        have="""\
        :html: {
          :path: tests/assets/test.html
        }
        :caption: Interactive visualization.
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <figure class="html" data-nodeid="1">
        <div class="interactive-chart">
          <h3>Sample Interactive Chart</h3>
          <canvas id="chart" width="400" height="300"></canvas>
          <script>
            // Chart rendering code would go here
            console.log('Chart initialized');
          </script>
        </div>
        <figcaption>
        <span class="label">Widget 1. </span>Interactive visualization.
        </figcaption>

        </figure>

        </section>

        </div>

        </main>

        </body>
        """,
    )


# Test mixed numbering
def test_mixed_asset_numbering():
    compare_have_want(
        have="""\
        :figure: {
          :path: assets/chart.png
        }
          :caption: First figure.
        ::

        :video: {
          :path: assets/demo.mp4
        }
          :caption: First video.
        ::

        :figure: {
          :path: assets/graph.jpg
        }
          :caption: Second figure.
        ::

        :html:{
          :path: tests/assets/viz.html
        }
          :caption: First HTML.
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <figure class="figure" data-nodeid="1">
        <img src="assets/chart.png" alt="Figure 1.">
        <figcaption>
        <span class="label">Figure 1. </span>First figure.
        </figcaption>

        </figure>

        <figure class="video" data-nodeid="4">
        <video controls src="assets/demo.mp4">Your browser does not support the video tag.</video>
        <figcaption>
        <span class="label">Video 1. </span>First video.
        </figcaption>

        </figure>

        <figure class="figure" data-nodeid="7">
        <img src="assets/graph.jpg" alt="Figure 2.">
        <figcaption>
        <span class="label">Figure 2. </span>Second figure.
        </figcaption>

        </figure>

        <figure class="html" data-nodeid="10">
        <div class="data-visualization">
          <p>Custom HTML visualization content</p>
        </div>
        <figcaption>
        <span class="label">Widget 1. </span>First HTML.
        </figcaption>

        </figure>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_figure_alt_text():
    compare_have_want(
        have="""\
        :figure: {
          :path: assets/example.png
          :alt: A scatter plot showing the correlation between X and Y.
        }
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <figure class="figure" data-nodeid="1">
        <img src="assets/example.png" alt="A scatter plot showing the correlation between X and Y.">
        </figure>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_figure_dark_mode():
    compare_have_want(
        have="""\
        :figure: {
          :path: assets/chart-light.png
          :dark: assets/chart-dark.png
        }
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <figure class="figure" data-nodeid="1">
        <picture>
        <source media="(prefers-color-scheme: dark)" srcset="assets/chart-dark.png">
        <img src="assets/chart-light.png" alt="Figure 1.">
        </picture>
        </figure>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_figure_static_path():
    """The :static: path is stored on the node for use by export formats; no HTML change."""
    compare_have_want(
        have="""\
        :figure: {
          :path: assets/interactive.svg
          :static: assets/interactive-static.png
        }
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <figure class="figure" data-nodeid="1">
        <img src="assets/interactive.svg" alt="Figure 1.">
        </figure>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_figure_all_new_options():
    compare_have_want(
        have="""\
        :figure: {
          :path: assets/plot-light.png
          :alt: A density plot.
          :dark: assets/plot-dark.png
          :static: assets/plot-static.png
        }
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <figure class="figure" data-nodeid="1">
        <picture>
        <source media="(prefers-color-scheme: dark)" srcset="assets/plot-dark.png">
        <img src="assets/plot-light.png" alt="A density plot.">
        </picture>
        </figure>

        </section>

        </div>

        </main>

        </body>
        """,
    )


class MockAssetResolver:
    """Asset resolver that returns predefined content for specific filenames."""

    def __init__(self, assets):
        self._assets = assets

    def resolve_asset(self, path):
        return self._assets.get(path)


def test_svg_image_resolved_as_data_uri():
    """SVG figures should be inlined as data URIs when the resolver provides content."""
    svg_content = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><circle cx="50" cy="50" r="40" fill="red"/></svg>'
    resolver = MockAssetResolver({"test.svg": svg_content})

    src = dedent("""\
        :figure: {
          :path: test.svg
        }
        :caption: A red circle.
        ::
    """)
    html = rsm.render(src, asset_resolver=resolver).lstrip()

    expected_b64 = base64.b64encode(svg_content.encode("utf-8")).decode("ascii")
    expected_src = f"data:image/svg+xml;base64,{expected_b64}"
    assert expected_src in html
    assert 'src="test.svg"' not in html


def test_png_image_resolved_as_data_uri():
    """PNG figures should be inlined as data URIs when the resolver provides content."""
    # Simulate binary content returned as string (as the Studio resolver does)
    fake_png = "fake-png-binary-content"
    resolver = MockAssetResolver({"photo.png": fake_png})

    src = dedent("""\
        :figure: {
          :path: photo.png
        }
        :caption: A photo.
        ::
    """)
    html = rsm.render(src, asset_resolver=resolver).lstrip()

    expected_b64 = base64.b64encode(fake_png.encode("utf-8")).decode("ascii")
    assert f"data:image/png;base64,{expected_b64}" in html


def test_image_falls_back_to_raw_path():
    """When the resolver returns None, the raw path should be used as src."""
    resolver = MockAssetResolver({})

    src = dedent("""\
        :figure: {
          :path: missing.png
        }
        :caption: Missing image.
        ::
    """)
    html = rsm.render(src, asset_resolver=resolver).lstrip()
    assert 'src="missing.png"' in html
