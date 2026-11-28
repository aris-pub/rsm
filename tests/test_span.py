import logging
import re

import pytest

import rsm
from conftest import compare_have_want


def test_one_span():
    compare_have_want(
        have="""\
        This is a :span: {:strong:} boring :: paragraph.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a <span class="span" data-nodeid="3"><strong>boring</strong></span> paragraph.</p>

        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a <span class="span" data-nodeid="3"><strong>boring</strong></span> paragraph, though it has two <span class="span" data-nodeid="6"><em>spans</em></span> so it's less boring.</p>

        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a <span class="span" data-nodeid="3"><strong>paragraph with a <span class="span" data-nodeid="5"><em>span within a span</em></span></strong></span> so that makes it really cool.  BTW it also has a Halmos at the start of a line!</p>

        </div>

        </section>

        </div>

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a paragraph with <span id="lbl" class="span" data-nodeid="3"><strong>a span</strong></span> and it is multi line.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_span_with_label():
    compare_have_want(
        have="""\
        This is a :span: {:label: myspn, :strong:} boring :: paragraph.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a <span id="myspn" class="span" data-nodeid="3"><strong>boring</strong></span> paragraph.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_span_part_of_word():
    compare_have_want(
        have="""\
        This word is half bold :span: {:strong:} bo::ring.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This word is half bold <span class="span" data-nodeid="3"><strong>bo</strong></span>ring.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_span_part_of_word_with_shortcut():
    compare_have_want(
        have="""\
        This word is half bold **bo**ring.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This word is half bold <span class="span" data-nodeid="3"><strong>bo</strong></span>ring.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


@pytest.mark.parametrize(
    "key, tag", [("little", "small"), ("insert", "ins"), ("delete", "del")]
)
def test_span_key_renders_its_tag(caplog, key, tag):
    caplog.set_level(logging.WARNING)
    h = rsm.render(
        f"A :span: {{:{key}:}} few words :: here.",
        handrails=False,
        source_offsets=False,
    )
    assert f'<span class="span" data-nodeid="3"><{tag}>few words</{tag}></span>' in h, h
    assert not caplog.records, caplog.text


def _p(src):
    h = rsm.render(src, handrails=False, source_offsets=False)
    p = h[h.index("<p>") + 3 : h.index("</p>")]
    return re.sub(r'<span class="span" data-nodeid="\d+">(.*?)</span>', r"\1", p)


# A space just inside the markers of bold or italic moves outside the tag, so the
# reader still sees a space between the words (rsm-9iq).
@pytest.mark.parametrize(
    "src, want",
    [
        ("Some **graded **x here.", "Some <strong>graded</strong> x here."),
        ("Some and** lead**z here.", "Some and <strong>lead</strong>z here."),
        ("Some *it *y here.", "Some <em>it</em> y here."),
        ("Some and* lead*z here.", "Some and <em>lead</em>z here."),
        ("Some **graded ** x here.", "Some <strong>graded</strong> x here."),
        ("Some **graded**x here.", "Some <strong>graded</strong>x here."),
    ],
)
def test_space_inside_markers_moves_outside(caplog, src, want):
    caplog.set_level(logging.WARNING)
    assert _p(src) == want
    assert not caplog.records, caplog.text


def test_space_inside_span_tag_is_still_dropped():
    assert _p("A :span: {:strong:} graded :: x.") == "A <strong>graded</strong> x."
