from conftest import compare_have_want


def test_one_span():
    compare_have_want(
        have="""\
        This is a :span: {:strong:} boring :: paragraph.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a <span class="span" data-nodeid="3"><strong>boring</strong></span> paragraph.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_two_spans():
    compare_have_want(
        have="""\
        This is a :span: {:strong:} boring :: paragraph, though it has two :span:
        {:emphas:} spans :: so it's less boring.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a <span class="span" data-nodeid="3"><strong>boring</strong></span> paragraph, though it has two <span class="span" data-nodeid="6"><em>spans</em></span> so it's less boring.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_nested():
    compare_have_want(
        have="""\
        This is a :span: {:strong:} paragraph with a :span: {:emphas:} span within a span ::
        :: so that makes it really cool.  BTW it also has a Halmos at the start of a
        line!
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a <span class="span" data-nodeid="3"><strong>paragraph with a <span class="span" data-nodeid="5"><em>span within a span</em></span></strong></span> so that makes it really cool.  BTW it also has a Halmos at the start of a line!</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_span_with_multiline_meta():
    compare_have_want(
        have="""\
        This is a paragraph
        with :span: {:strong:,
        :label: lbl} a
        span :: and it is multi line.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a paragraph with <span id="lbl" class="span" data-nodeid="3"><strong>a span</strong></span> and it is multi line.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_span_with_label():
    compare_have_want(
        have="""\
        This is a :span: {:label: myspn, :strong:} boring :: paragraph.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a <span id="myspn" class="span" data-nodeid="3"><strong>boring</strong></span> paragraph.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_span_part_of_word():
    compare_have_want(
        have="""\
        This word is half bold :span: {:strong:} bo::ring.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This word is half bold <span class="span" data-nodeid="3"><strong>bo</strong></span>ring.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_span_part_of_word_with_shortcut():
    compare_have_want(
        have="""\
        This word is half bold **bo**ring.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This word is half bold <span class="span" data-nodeid="3"><strong>bo</strong></span>ring.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
