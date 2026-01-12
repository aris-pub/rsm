from conftest import compare_have_want


def test_simple():
    compare_have_want(
        have="""\
        ## Section

        Lorem ipsum.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. Section</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Lorem ipsum.</p>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_subsections():
    compare_have_want(
        have="""\
        ## Section

        Lorem ipsum.

        ### Sub section

        Foo

        #### Sub sub section

        Bar

        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. Section</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Lorem ipsum.</p>

        </div>

        <section class="subsection level-3" data-nodeid="4">

        <h3>1.1. Sub section</h3>

        <div class="paragraph" data-nodeid="5">

        <p>Foo</p>

        </div>

        <section class="subsubsection level-4" data-nodeid="7">

        <h4>1.1.1. Sub sub section</h4>

        <div class="paragraph" data-nodeid="8">

        <p>Bar</p>

        </div>

        </section>

        </section>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )
