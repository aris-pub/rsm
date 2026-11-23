from conftest import compare_have_want


def test_simple():
    compare_have_want(
        have="""\
        ## Section

          This paragraph contains a claim :claim: {:label: clm-lbl}all $X$ are $Y$ ::.
        """,
        want=r"""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section id="sec-1" class="section level-2" data-nodeid="1">

        <h2>1. Section</h2>

        <div class="paragraph" data-nodeid="2">

        <p>This paragraph contains a claim <span id="clm-lbl" class="construct claim" data-nodeid="4"><span class="keyword" data-nodeid="5">⊢</span> all <span class="math" data-nodeid="8">\(X\)</span> are <span class="math" data-nodeid="11">\(Y\)</span></span>.</p>

        </div>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_with_math():
    compare_have_want(
        have="""\
        This paragraph has math inside a claim :claim: :math:2+2=4:: ::.
        """,
        want=r"""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph has math inside a claim <span class="construct claim" data-nodeid="3"><span class="keyword" data-nodeid="4">⊢</span> <span class="math" data-nodeid="7">\(2+2=4\)</span></span>.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_claim_within_list():
    compare_have_want(
        have="""\
        We now make a bunch of claims.

        :enumerate:

        :-: {:label: one} :claim: :math:2+2=4:: ::.

        :-: {:label: two} :claim: :math:3+3=6:: ::.

        ::
        """,
        want=r"""        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>We now make a bunch of claims.</p>

        </div>

        <div class="paragraph" data-nodeid="3">

        <ol class="enumerate" data-nodeid="4">

        <li id="one" class="item" data-nodeid="5">
        <span class="construct claim" data-nodeid="6"><span class="keyword" data-nodeid="7">⊢</span> <span class="math" data-nodeid="10">\(2+2=4\)</span></span>.
        </li>

        <li id="two" class="item" data-nodeid="13">
        <span class="construct claim" data-nodeid="14"><span class="keyword" data-nodeid="15">⊢</span> <span class="math" data-nodeid="18">\(3+3=6\)</span></span>.
        </li>

        </ol>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )
