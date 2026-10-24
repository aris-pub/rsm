import rsm
from conftest import compare_have_want


def test_no_reftext():
    compare_have_want(
        have="""\
        This paragraph has a hyperlink :url:https://www.apache.com::.

        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph has a hyperlink <a href="https://www.apache.com">https://www.apache.com</a>.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_custom_reftext():
    compare_have_want(
        have="""\
        This is a link to :url:https://www.apache.com, Apache::.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a link to <a href="https://www.apache.com">Apache</a>.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_no_target():
    compare_have_want(
        have="""\
        This is a malformed url :url:::.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a malformed url [CST error at (0, 24) - (0, 31)] .</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )

    compare_have_want(
        have="""\
        This is a malformed url with a space :url: ::.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a malformed url with a space [CST error at (0, 37) - (0, 45)] .</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_url_reftext_strips_surrounding_space():
    """The space after the comma must not end up inside the link text (rsm-bpe)."""
    h = rsm.render(
        "# T\n\nLink :url:https://x.org, click here  ::.\n",
        handrails=False,
        source_offsets=False,
    )
    assert '<a href="https://x.org">click here</a>' in h, h


def test_ref_reftext_strips_surrounding_space():
    h = rsm.render(
        "# T\n\n:theorem: {:label: thm-x}\n  A statement. ::\n\nSee :ref:thm-x, the theorem::.\n",
        handrails=False,
        source_offsets=False,
    )
    assert '<a class="reference" href="#thm-x">the theorem</a>' in h, h
