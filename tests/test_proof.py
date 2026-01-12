from conftest import compare_have_want


def test_simple():
    compare_have_want(
        have="""\
        :theorem:

        All $X$ are $Y$.

        ::

        :proof:

        :step: Axiom.::

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="theorem" data-nodeid="1">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.</span></p>

        </div>

        <div class="paragraph" data-nodeid="2">

        <p>All <span class="math" data-nodeid="4">\(X\)</span> are <span class="math" data-nodeid="7">\(Y\)</span>.</p>

        </div>

        </div>

        <div class="proof" data-nodeid="10">

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div class="step last" data-nodeid="11">

        <div class="statement" data-nodeid="12">

        <div class="paragraph" data-nodeid="13">

        <p>Axiom.</p>

        </div>

        </div>

        </div>

        <div class="halmos"></div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_empty_proof():
    compare_have_want(
        have="""\
        :theorem:

        Theorem contents.

        ::

        :proof:

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

        <div class="proof" data-nodeid="4">

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div class="halmos"></div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_sub_step():
    compare_have_want(
        have="""\
        :proof:

          :step: Top level step.

            :step: Sub-step.

              :p: Sub-proof.::

            ::
          ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="proof" data-nodeid="1">

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div class="step last" data-nodeid="2">

        <div class="statement" data-nodeid="3">

        <div class="paragraph" data-nodeid="4">

        <p>Top level step.</p>

        </div>

        </div>

        <div class="subproof" data-nodeid="6">

        <div class="step" data-nodeid="7">

        <div class="statement" data-nodeid="8">

        <div class="paragraph" data-nodeid="9">

        <p>Sub-step.</p>

        </div>

        </div>

        <div class="subproof" data-nodeid="11">

        <div class="paragraph" data-nodeid="12">

        <p>Sub-proof.</p>

        </div>

        </div>

        </div>

        </div>

        </div>

        <div class="halmos"></div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_two_steps():
    compare_have_want(
        have="""\
        :proof:

          :step: First step.::

          :step: Secon step.::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="proof" data-nodeid="1">

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div class="step" data-nodeid="2">

        <div class="statement" data-nodeid="3">

        <div class="paragraph" data-nodeid="4">

        <p>First step.</p>

        </div>

        </div>

        </div>

        <div class="step last" data-nodeid="6">

        <div class="statement" data-nodeid="7">

        <div class="paragraph" data-nodeid="8">

        <p>Secon step.</p>

        </div>

        </div>

        </div>

        <div class="halmos"></div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
