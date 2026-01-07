from conftest import compare_have_want


def test_numbered_sections():
    compare_have_want(
        have="""\
        :rsm:

        :section:
          :title: First

        Content of first.

        :section:
          :title: Second

        Content of second.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. First</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Content of first.</p>

        </div>

        </section>

        <section class="section level-2" data-nodeid="4">

        <h2>2. Second</h2>

        <div class="paragraph" data-nodeid="5">

        <p>Content of second.</p>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_nonum():
    compare_have_want(
        have="""\
        :rsm:

        :section:
          :title: First

        Content of first.

        :section:
          :title: Second
          :nonum:

        Content of second.

        :section:
          :title: Third

        Content of third.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. First</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Content of first.</p>

        </div>

        </section>

        <section class="section level-2" data-nodeid="4">

        <h2>Second</h2>

        <div class="paragraph" data-nodeid="5">

        <p>Content of second.</p>

        </div>

        </section>

        <section class="section level-2" data-nodeid="7">

        <h2>2. Third</h2>

        <div class="paragraph" data-nodeid="8">

        <p>Content of third.</p>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )
