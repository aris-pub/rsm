from conftest import compare_have_want


def test_simple():
    compare_have_want(
        have="""\
        :rsm:

        :theorem:

        Theorem contents.

        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="theorem" data-nodeid="1">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.</span></p>

        </div>

        <div class="paragraph" data-nodeid="2">

        <p>Theorem contents.</p>

        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_multiple():
    compare_have_want(
        have="""\
        :rsm:

        :theorem:

        Theorem contents.

        ::

        :lemma:

        And a lemma.

        ::

        :theorem:

        Another theorem.

        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="theorem" data-nodeid="1">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.</span></p>

        </div>

        <div class="paragraph" data-nodeid="2">

        <p>Theorem contents.</p>

        </div>

        </div>

        <div class="lemma theorem" data-nodeid="4">

        <div class="paragraph hr-label">

        <p><span class="span label">Lemma 2.</span></p>

        </div>

        <div class="paragraph" data-nodeid="5">

        <p>And a lemma.</p>

        </div>

        </div>

        <div class="theorem" data-nodeid="7">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 3.</span></p>

        </div>

        <div class="paragraph" data-nodeid="8">

        <p>Another theorem.</p>

        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
