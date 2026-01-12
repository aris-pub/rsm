from conftest import compare_have_want


def test_simple():
    compare_have_want(
        have="""
        ## Foo

        :appendix:

        ## Bar
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. Foo</h2>

        </section>

        <section class="section level-2" data-nodeid="3">

        <h2>A. Bar</h2>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_subsection():
    compare_have_want(
        have="""
        ## Foo
        ### Sub Foo

        :appendix:

        ## Bar
        ### Sub Bar
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. Foo</h2>

        <section class="subsection level-3" data-nodeid="2">

        <h3>1.1. Sub Foo</h3>

        </section>

        </section>

        <section class="section level-2" data-nodeid="4">

        <h2>A. Bar</h2>

        <section class="subsection level-3" data-nodeid="5">

        <h3>A.1. Sub Bar</h3>

        </section>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_theorem():
    compare_have_want(
        have="""
        ## Foo
        ### Sub Foo

        :theorem: ::

        :appendix:

        ## Bar
        ### Sub Bar

        :theorem: ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. Foo</h2>

        <section class="subsection level-3" data-nodeid="2">

        <h3>1.1. Sub Foo</h3>

        <div class="theorem" data-nodeid="3">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.1.</span></p>

        </div>

        </div>

        </section>

        </section>

        <section class="section level-2" data-nodeid="5">

        <h2>A. Bar</h2>

        <section class="subsection level-3" data-nodeid="6">

        <h3>A.1. Sub Bar</h3>

        <div class="theorem" data-nodeid="7">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem A.1.</span></p>

        </div>

        </div>

        </section>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_section_reftext():
    compare_have_want(
        have="""
        :ref:app::

        :appendix:

        ## Foo bar {:label: app}
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><a class="reference" href="#app">Appendix A</a></p>

        </div>

        <section id="app" class="section level-2" data-nodeid="4">

        <h2>A. Foo bar</h2>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )
