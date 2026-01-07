from conftest import compare_have_want


def test_simple_no_handrails():
    compare_have_want(
        have="""\
        :rsm:

        :sketch: Foo.::

        :proof:

          :step: Bar.::

        ::

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="sketch" data-nodeid="1">

        <div class="paragraph hr-label">

        <p><span class="span label">Proof sketch.</span></p>

        </div>

        <div class="paragraph" data-nodeid="2">

        <p>Foo.</p>

        </div>

        </div>

        <div class="proof" data-nodeid="4">

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div class="step last" data-nodeid="5">

        <div class="statement" data-nodeid="6">

        <div class="paragraph" data-nodeid="7">

        <p>Bar.</p>

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
