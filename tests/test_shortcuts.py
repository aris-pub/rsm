from conftest import compare_have_want


def test_one_strong():
    compare_have_want(
        have="""\
        :rsm:
          :title: My Title

        This paragraph has a *shortcut* for strong span.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph has a <span class="span" data-nodeid="3"><strong>shortcut</strong></span> for strong span.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_two_strong():
    compare_have_want(
        have="""\
        :rsm:
          :title: My Title

        This paragraph has two *shortcuts* for strong *spans*.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph has two <span class="span" data-nodeid="3"><strong>shortcuts</strong></span> for strong <span class="span" data-nodeid="6"><strong>spans</strong></span>.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_one_emphas():
    compare_have_want(
        have="""\
        :rsm:
          :title: My Title

        This paragraph has a /shortcut/ for emphasis span.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph has a <span class="span" data-nodeid="3"><em>shortcut</em></span> for emphasis span.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_one_math():
    compare_have_want(
        have="""\
        :rsm:
          :title: My Title

        This paragraph has some $2+2=4$ awesome math.

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph has some <span class="math" data-nodeid="3">\(2+2=4\)</span> awesome math.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_two_math():
    compare_have_want(
        have="""\
        :rsm:
          :title: My Title

        This paragraph has some $2+2=4$ awesome math and also some math that $2 + 2 + 2
        + 2 + 2 = 10$ is broken down.

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph has some <span class="math" data-nodeid="3">\(2+2=4\)</span> awesome math and also some math that <span class="math" data-nodeid="6">\(2 + 2 + 2
        + 2 + 2 = 10\)</span> is broken down.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_mathblock():
    compare_have_want(
        have="""\
        :rsm:

        This paragraph is followed by display math
        $$2 + 2 = 4.$$

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph is followed by display math </p>
        <div class="mathblock" data-nodeid="3">
        $$
        2 + 2 = 4.
        $$
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_section_shortcut():
    compare_have_want(
        have="""\
        :rsm:

        ## My Section
          :label: my-sec

        This section contains a shortcut

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section id="my-sec" class="section level-2" data-nodeid="1">

        <h2>1. My Section</h2>

        <div class="paragraph" data-nodeid="2">

        <p>This section contains a shortcut</p>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_subsubsection_shortcut():
    compare_have_want(
        have="""\
        :rsm:

        ## My Section

        Foo.

        ### My Subsection

        Bar.

        #### My Subsubsection

        Baz.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. My Section</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Foo.</p>

        </div>

        <section class="subsection level-3" data-nodeid="4">

        <h3>1.1. My Subsection</h3>

        <div class="paragraph" data-nodeid="5">

        <p>Bar.</p>

        </div>

        <section class="subsubsection level-4" data-nodeid="7">

        <h4>1.1.1. My Subsubsection</h4>

        <div class="paragraph" data-nodeid="8">

        <p>Baz.</p>

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


def test_claim_shortcut():
    compare_have_want(
        have="""\
        :rsm:

        This paragraph contains a :|-: claim with a turnstile::. And also another one :⊢: but it takes
        multiple lines::.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph contains a <span class="construct claim" data-nodeid="3"><span class="keyword" data-nodeid="4">⊢</span> claim with a turnstile</span>. And also another one <span class="construct claim" data-nodeid="8"><span class="keyword" data-nodeid="9">⊢</span> but it takes multiple lines</span>.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_prev_shortcut():
    compare_have_want(
        have="""\
        :rsm:

        :theorem:

        All $X$ are $Y$.

        ::

        :proof:

        :step:
          :label: st1
          All $X$ are $Z$ and all $Z$ are $Y$.
        ::

        :step: :qed:.

           :p: Due to :prev:.::

        ::

        ::

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

        <div id="st1" class="step" data-nodeid="11">

        <div class="statement" data-nodeid="12">

        <div class="paragraph" data-nodeid="13">

        <p>All <span class="math" data-nodeid="15">\(X\)</span> are <span class="math" data-nodeid="18">\(Z\)</span> and all <span class="math" data-nodeid="21">\(Z\)</span> are <span class="math" data-nodeid="24">\(Y\)</span>.</p>

        </div>

        </div>

        </div>

        <div class="step last" data-nodeid="27">

        <div class="statement" data-nodeid="28">

        <div class="paragraph" data-nodeid="29">

        <p><span class="construct qed" data-nodeid="30"><span class="keyword" data-nodeid="31">QED</span></span>.</p>

        </div>

        </div>

        <div class="subproof" data-nodeid="34">

        <div class="paragraph" data-nodeid="35">

        <p>Due to <a class="reference" href="#st1">Step ⟨1⟩</a>.</p>

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


def test_prev2_shortcut():
    compare_have_want(
        have="""\
        :rsm:

        :theorem:

        All $X$ are $Y$.

        ::

        :proof:

        :step:
          :label: st1
          All $X$ are $Z$ and all $Z$ are $Y$.
        ::

        :step:
          :label: st2
          Something inconsequential here.
        ::

        :step: :qed:.

           :p: Due to :prev2:.::

        ::

        ::

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

        <div id="st1" class="step" data-nodeid="11">

        <div class="statement" data-nodeid="12">

        <div class="paragraph" data-nodeid="13">

        <p>All <span class="math" data-nodeid="15">\(X\)</span> are <span class="math" data-nodeid="18">\(Z\)</span> and all <span class="math" data-nodeid="21">\(Z\)</span> are <span class="math" data-nodeid="24">\(Y\)</span>.</p>

        </div>

        </div>

        </div>

        <div id="st2" class="step" data-nodeid="27">

        <div class="statement" data-nodeid="28">

        <div class="paragraph" data-nodeid="29">

        <p>Something inconsequential here.</p>

        </div>

        </div>

        </div>

        <div class="step last" data-nodeid="31">

        <div class="statement" data-nodeid="32">

        <div class="paragraph" data-nodeid="33">

        <p><span class="construct qed" data-nodeid="34"><span class="keyword" data-nodeid="35">QED</span></span>.</p>

        </div>

        </div>

        <div class="subproof" data-nodeid="38">

        <div class="paragraph" data-nodeid="39">

        <p>Due to <a class="reference" href="#st1">Step ⟨1⟩</a>.</p>

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


def test_prev_and_prev2_shortcut():
    compare_have_want(
        have="""\
        :rsm:

        :theorem:

        All $X$ are $Y$.

        ::

        :proof:

        :step:
          :label: st1
          All $X$ are $Z$.
        ::

        :step:
          :label: st2
          All $Z$ are $Y$.
        ::

        :step: :qed:.

           :p: Due to :prev: and :prev2:.::

        ::

        ::

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

        <div id="st1" class="step" data-nodeid="11">

        <div class="statement" data-nodeid="12">

        <div class="paragraph" data-nodeid="13">

        <p>All <span class="math" data-nodeid="15">\(X\)</span> are <span class="math" data-nodeid="18">\(Z\)</span>.</p>

        </div>

        </div>

        </div>

        <div id="st2" class="step" data-nodeid="21">

        <div class="statement" data-nodeid="22">

        <div class="paragraph" data-nodeid="23">

        <p>All <span class="math" data-nodeid="25">\(Z\)</span> are <span class="math" data-nodeid="28">\(Y\)</span>.</p>

        </div>

        </div>

        </div>

        <div class="step last" data-nodeid="31">

        <div class="statement" data-nodeid="32">

        <div class="paragraph" data-nodeid="33">

        <p><span class="construct qed" data-nodeid="34"><span class="keyword" data-nodeid="35">QED</span></span>.</p>

        </div>

        </div>

        <div class="subproof" data-nodeid="38">

        <div class="paragraph" data-nodeid="39">

        <p>Due to <a class="reference" href="#st2">Step ⟨2⟩</a> and <a class="reference" href="#st1">Step ⟨1⟩</a>.</p>

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


def test_code_shortcut():
    compare_have_want(
        have="""\
        :rsm:

        This is inline code`comp = [abs(x) for x in range(10)]`.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is inline code
        <span class="code" data-nodeid="3"><code>comp = [abs(x) for x in range(10)]</code></span>
        .</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_codeblock_shortcut():
    compare_have_want(
        have="""\
        :rsm:

        ```
        comp = [abs(x) for x in range(10)]
        ```

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock" data-nodeid="1">

        <pre>
        <code>comp = [abs(x) for x in range(10)]</code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_hashtag_not_at_the_start_of_line():
    compare_have_want(
        have=r"""        :rsm:

        ## This is a section title

        And \# this is not!

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. This is a section title</h2>

        <div class="paragraph" data-nodeid="2">

        <p>And # this is not!</p>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_escaped_colon_behind_halmos():
    compare_have_want(
        have=r"""        :rsm:

        Shortcut right beside an escaped colon :span: {:emphas:} foo\:::

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Shortcut right beside an escaped colon <span class="span" data-nodeid="3"><em>foo:</em></span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_escaped_colon_behind_halmos_after_shortcut():
    compare_have_want(
        have=r"""        :rsm:

        Shortcut right beside an escaped colon *foo\:*

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Shortcut right beside an escaped colon <span class="span" data-nodeid="3"><strong>foo:</strong></span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_math_after_turnstile():
    compare_have_want(
        have="""\
        :rsm:

        This paragraph has math inside a claim :⊢: $2+2=4$::.

        ::
        """,
        want=r"""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This paragraph has math inside a claim <span class="construct claim" data-nodeid="3"><span class="keyword" data-nodeid="4">⊢</span> <span class="math" data-nodeid="7">\(2+2=4\)</span></span>.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_turnstile_and_math_within_list():
    compare_have_want(
        have="""\
        :rsm:

        We now make a bunch of claims

        :enumerate:

        :item: {:label: one} :⊢: $2+2=4$::.

        :item: {:label: two} :⊢: $3+3=6$::.

        ::

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>We now make a bunch of claims</p>

        </div>

        <ol class="enumerate" data-nodeid="3">

        <li id="one" class="item" data-nodeid="4">
        <span class="construct claim" data-nodeid="5"><span class="keyword" data-nodeid="6">⊢</span> <span class="math" data-nodeid="9">\(2+2=4\)</span></span>.
        </li>

        <li id="two" class="item" data-nodeid="12">
        <span class="construct claim" data-nodeid="13"><span class="keyword" data-nodeid="14">⊢</span> <span class="math" data-nodeid="17">\(3+3=6\)</span></span>.
        </li>

        </ol>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_asterisk_inside_math():
    compare_have_want(
        have="""\
        :rsm:

        $2*2 = 4*1$

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="math" data-nodeid="2">\(2*2 = 4*1\)</span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_asterisk_inside_code():
    compare_have_want(
        have="""\
        :rsm:

        `[x**2 for x in range(10)]`

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>
        <span class="code" data-nodeid="2"><code>[x**2 for x in range(10)]</code></span>
        </p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_asterisk_inside_mathblock():
    compare_have_want(
        have=r"""
        :rsm:

        Here comes a mathblock with an asterisk\:
        $$
        2*2 = 4*1
        $$

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Here comes a mathblock with an asterisk: </p>
        <div class="mathblock" data-nodeid="3">
        $$
        2*2 = 4*1
        $$
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_asterisk_inside_codeblock():
    compare_have_want(
        have="""\
        :rsm:

        ```
        2*2 = 4*1
        ```

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock" data-nodeid="1">

        <pre>
        <code>2*2 = 4*1</code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
