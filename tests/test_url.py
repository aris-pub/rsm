from conftest import compare_have_want


def test_no_reftext():
    compare_have_want(
        have="""\
        :rsm:

        This paragraph has a hyperlink :url:https://www.apache.com::.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph has a hyperlink <a href="https://www.apache.com">https://www.apache.com</a>.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_custom_reftext():
    compare_have_want(
        have="""\
        :rsm:

        This is a link to :url:https://www.apache.com, Apache::.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a link to <a href="https://www.apache.com"> Apache</a>.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_no_target():
    compare_have_want(
        have="""\
        :rsm:

        This is a malformed url :url:::.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a malformed url [CST error at (2, 24) - (2, 31)] .</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )

    compare_have_want(
        have="""\
        :rsm:

        This is a malformed url with a space :url: ::.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a malformed url with a space [CST error at (2, 37) - (2, 45)] .</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
