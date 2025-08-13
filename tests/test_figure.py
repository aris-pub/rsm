from conftest import compare_have_want

SIMPLE_WANT = """\
<body>

<div class="manuscriptwrapper">

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

</div>

</body>
"""


def test_simple():
    compare_have_want(
        have="""\
        :rsm:

        :figure:
          :path: assets/example.png

          :caption: This is the figure caption.

        ::

        ::
        """,
        want=SIMPLE_WANT,
    )


def test_simple_with_extra_whitespace():
    compare_have_want(
        have="""\
        :rsm:

        :figure:
          :path: assets/example.png

          :caption:
            This is the figure caption.


        ::

        ::
        """,
        want=SIMPLE_WANT,
    )


def test_simple_with_multi_line_caption():
    compare_have_want(
        have="""\
        :rsm:

        :figure:
          :path: assets/example.png

          :caption:
            This is the figure caption.
            And it spans multiple lines.

        ::

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
        :rsm:

        :figure:
          :path: assets/example.png

          :caption: This is the *figure* caption.

        ::

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

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

        </div>

        </body>
        """,
    )


# Test video asset type
def test_video_mp4():
    compare_have_want(
        have="""\
        :rsm:

        :video:
          :path: assets/demo.mp4

          :caption: This is a video demonstration.

        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

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

        </div>

        </body>
        """,
    )


def test_video_youtube():
    compare_have_want(
        have="""\
        :rsm:

        :video:
          :path: https://www.youtube.com/watch?v=dQw4w9WgXcQ

          :caption: YouTube video example.

        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

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

        </div>

        </body>
        """,
    )


# Test HTML asset type
def test_html_asset():
    compare_have_want(
        have="""\
        :rsm:

        :html:
          :path: tests/assets/test.html

          :caption: Interactive visualization.

        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

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
        <span class="label">Html 1. </span>Interactive visualization.
        </figcaption>

        </figure>

        </section>

        </div>

        </div>

        </body>
        """,
    )


# Test mixed numbering
def test_mixed_asset_numbering():
    compare_have_want(
        have="""\
        :rsm:

        :figure:
          :path: assets/chart.png
          :caption: First figure.

        ::

        :video:
          :path: assets/demo.mp4
          :caption: First video.

        ::

        :figure:
          :path: assets/graph.jpg
          :caption: Second figure.

        ::

        :html:
          :path: tests/assets/viz.html
          :caption: First HTML.

        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

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
        <span class="label">Html 1. </span>First HTML.
        </figcaption>

        </figure>

        </section>

        </div>

        </div>

        </body>
        """,
    )
