from conftest import compare_have_want_handrails


def test_codeblock_handrails():
    compare_have_want_handrails(
        have="""\
        ```
        comp = [abs(x) for x in range(10)]
        ```
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <pre>
        <code>comp = [abs(x) for x in range(10)]</code>
        </pre>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_codeblock_with_lang_handrails():
    compare_have_want_handrails(
        have="""\
        ```{:lang: python}

        def hello():
            print("world")
        ```
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <pre>
        <code class="highlight python"><span class="k">def</span><span class="w"> </span><span class="nf">hello</span><span class="p">():</span>
            <span class="nb">print</span><span class="p">(</span><span class="s2">&quot;world&quot;</span><span class="p">)</span>
        </code>
        </pre>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_manuscript():
    compare_have_want_handrails(
        have="""
        # Some Title

        Hello.

        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h1>Some Title</h1>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Hello.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_section():
    compare_have_want_handrails(
        have="""
        # Some Title

        ## Section
        Hello.

        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h1>Some Title</h1>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <section id="sec-1" class="section level-2" data-nodeid="1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h2>1. Section</h2>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="2">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Hello.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_abstract():
    compare_have_want_handrails(
        have="""
        # Some Title

        :abstract:
          The abstract.
        ::
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h1>Some Title</h1>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="abstract" data-nodeid="1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h2>Abstract</h2>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="2">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>The abstract.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_theorem():
    compare_have_want_handrails(
        have="""
        :theorem:

        Hello.

        ::
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="theorem hr hr-labeled" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.</span></p>

        </div>

        <div class="paragraph hr hr-offset hr-hidden" tabindex=0 data-nodeid="2">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Hello.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_author():
    compare_have_want_handrails(
        have=r"""
        # Indefinite Linear Algebra of the NBM

        :config: {
          :override-date: 2024-04-13
        }
        ::

        :author: {
          :name: Leo Torres
          :email: leo@leotrs.com
        }
        ::
        """,
        want=r"""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h1>Indefinite Linear Algebra of the NBM</h1>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <p class="manuscript-date">April 13, 2024</p>

        <div class="author-block">
        <div class="heading hr-hidden hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p class="author-names">Leo Torres</p>
        <details class="author-details">
        <summary><div class="icon chevron-down"><svg overflow="visible"><use href="#hr-icon-chevron-down" width="100%" height="100%"/></svg></div>Affiliations</summary>
        <p class="author-correspondence">Correspondence: <a href="mailto:leo@leotrs.com">leo@leotrs.com</a></p>
        </details>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>
        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_bibliography():
    compare_have_want_handrails(
        have="""
        This is a citation :cite:atiyah2018introduction::.

        :references:

        @book{atiyah2018introduction,
          title={Introduction to commutative algebra},
          author={Atiyah, M.F., & MacDonald, I.G.},
          year={2018},
          publisher={CRC Press},
          doi={https://doi.org/10.1201/9780429493638},
        }

        ::
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>This is a citation <span class="nowrap">[<a id="cite-0" class="reference cite" href="#atiyah2018introduction">1</a>]</span>.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <section class="level-2">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h2>References</h2>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="bibliography" data-nodeid="5">

        <div id="atiyah2018introduction" class="bibitem" data-nodeid="6">

        <div class="hr-hidden hr" tabindex=0>

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">
        <p>1. Atiyah, M.F., & MacDonald, I.G. "Introduction to commutative algebra". CRC Press. 2018. <br />[<a class="reference backlink" href="#cite-0">↖1</a>]</p>
        </div>

        <div class="hr-info-zone">
        <div class="hr-info">
        <a id="atiyah2018introduction-doi" class="bibitem-doi" href="https://doi.org/https://doi.org/10.1201/9780429493638" target="_blank" aria-label="DOI">
        <div class="icon ext"><svg overflow="visible"><use href="#hr-icon-ext" width="100%" height="100%"/></svg></div></a>
        </div>
        </div>

        </div>

        </div>

        </div>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_inline_math_followed_by_punctuation():
    compare_have_want_handrails(
        have="""
        # title

        one $2+2=4$.

        two $2+2=4$ baz.

        three $2+2=4$. Another sentence.

        four $H_k$, the maximal.

        five $x$; then.

        six $y$) end.
        """,
        want=r"""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h1>title</h1>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>one <span class="inline-wrapper">
        <span class="math" data-nodeid="3">\(2+2=4\)</span><span>.</span></span></p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="6">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>two <span class="math" data-nodeid="8">\(2+2=4\)</span> baz.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="11">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>three <span class="inline-wrapper">
        <span class="math" data-nodeid="13">\(2+2=4\)</span><span>.</span></span> Another sentence.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="16">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>four <span class="inline-wrapper">
        <span class="math" data-nodeid="18">\(H_k\)</span><span>,</span></span> the maximal.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="21">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>five <span class="inline-wrapper">
        <span class="math" data-nodeid="23">\(x\)</span><span>;</span></span> then.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="26">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>six <span class="inline-wrapper">
        <span class="math" data-nodeid="28">\(y\)</span><span>)</span></span> end.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_mathblock_nonum():
    compare_have_want_handrails(
        have="""
        This one has a number
        $$
        2+2=4
        $$

        And this one does not
        $$
        {:nonum:}
        2+2=4
        $$
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>This one has a number </p>
        <div class="mathblock hr hr-hidden hr-offset" tabindex=0 data-nodeid="3">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">
        $$
        2+2=4
        $$
        </div>

        <div class="hr-info-zone">
        <div class="hr-info"><div class="eqn-number"><p>(1)</p></div></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="5">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>And this one does not </p>
        <div class="mathblock hr hr-hidden hr-offset" tabindex=0 data-nodeid="7">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">
        $$
        2+2=4
        $$
        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_reference_followed_by_punctuation():
    """References followed by punctuation should be wrapped to prevent line breaks."""
    from conftest import compare_have_want
    compare_have_want(
        have="""
        # Test

        :theorem: {:label: thm-one}
          First.
        ::

        one :ref:thm-one::.

        two :ref:thm-one:: baz.

        three :ref:thm-one::. Another.

        four :ref:thm-one::, more.

        five (:ref:thm-one::).
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Test</h1>

        <div id="thm-one" class="theorem" data-nodeid="1">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.</span></p>

        </div>

        <div class="paragraph" data-nodeid="2">

        <p>First.</p>

        </div>

        </div>

        <div class="paragraph" data-nodeid="4">

        <p>one <span class="inline-wrapper"><a class="reference" href="#thm-one">Theorem 1</a><span>.</span></span></p>

        </div>

        <div class="paragraph" data-nodeid="8">

        <p>two <a class="reference" href="#thm-one">Theorem 1</a> baz.</p>

        </div>

        <div class="paragraph" data-nodeid="12">

        <p>three <span class="inline-wrapper"><a class="reference" href="#thm-one">Theorem 1</a><span>.</span></span> Another.</p>

        </div>

        <div class="paragraph" data-nodeid="16">

        <p>four <span class="inline-wrapper"><a class="reference" href="#thm-one">Theorem 1</a><span>,</span></span> more.</p>

        </div>

        <div class="paragraph" data-nodeid="20">

        <p>five <span class="inline-wrapper">(<a class="reference" href="#thm-one">Theorem 1</a><span>)</span></span>.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )
