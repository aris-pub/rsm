from conftest import compare_have_want


def test_reftext():
    compare_have_want(
        have="""\
        :rsm:

        :section:
          :title: First
          :label: sec-lbl

        Content of first.

        This is a paragraph that refers to :ref:sec-lbl::.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section id="sec-lbl" class="section level-2" data-nodeid="1">

        <h2>1. First</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Content of first.</p>

        </div>

        <div class="paragraph" data-nodeid="4">

        <p>This is a paragraph that refers to <a class="reference" href="#sec-lbl">Section 1</a>.</p>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_overwrite_reftext():
    compare_have_want(
        have="""\
        :rsm:

        :section:
          :title: First
          :label: sec-lbl

        Content of first.

        This is a paragraph that refers to :ref:sec-lbl,The Section::.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section id="sec-lbl" class="section level-2" data-nodeid="1">

        <h2>1. First</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Content of first.</p>

        </div>

        <div class="paragraph" data-nodeid="4">

        <p>This is a paragraph that refers to <a class="reference" href="#sec-lbl">The Section</a>.</p>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_ref_to_unknown_label(caplog):
    compare_have_want(
        have="""\
        :rsm:

        :ref:foo::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="error" data-nodeid="2">[unknown label "foo"]</span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
    assert "Reference to nonexistent label" in caplog.text


def test_cite_to_unknown_label(caplog):
    compare_have_want(
        have="""\
        :rsm:

        This is an unknown cite :cite:foobar::.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is an unknown cite [<a id="cite-0" class="reference cite unknown" href="#">[unknown label "foobar"]</a>].</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
    assert "Reference to nonexistent label" in caplog.text
