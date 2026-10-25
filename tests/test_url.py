import rsm
from conftest import compare_have_want
from rsm.transformer import Transformer


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


def test_url_reftext_inline_markup(caplog):
    """The display text of :url: accepts inline markup (emphasis, math), which
    renders as real HTML inside the link (rsm-z1e)."""
    src = "# T\n\nSee :url:https://x.org, *On* Lipschitz $\\ell_2$::.\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert "The CST contains errors." not in caplog.text, caplog.text
    assert "[CST error" not in h, h
    assert "<em>On</em>" in h, h
    assert r'<span class="math">\(\ell_2\)</span>' in h, h
    # The markup lives inside the anchor, not after it.
    assert '<a href="https://x.org"><span class="span"><em>On</em></span>' in h, h

    # The plain-text flattening stays available for string contexts.
    tree = rsm.tsparser.TSParser().parse(src)
    transformed = Transformer().transform(tree)
    url = next(n for n in transformed.traverse() if n.__class__.__name__ == "URL")
    assert url.overwrite_reftext == "On Lipschitz \\ell_2"
    assert [n.__class__.__name__ for n in url.reftext_nodes] == ["Span", "Text", "Math"]


def test_url_reftext_strong_and_code():
    src = "# T\n\n:url:https://x.org, **bold** and `grep`::.\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert "[CST error" not in h, h
    assert "<strong>bold</strong>" in h, h
    assert '<span class="code"><code>grep</code></span>' in h, h
