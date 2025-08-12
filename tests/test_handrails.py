from conftest import compare_have_want_handrails


def test_codeblock_handrails():
    compare_have_want_handrails(
        have="""\
        :rsm:

        ```
        comp = [abs(x) for x in range(10)]
        ```

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Code Block</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        </div>

        </body>
        """,
    )


def test_codeblock_with_lang_handrails():
    compare_have_want_handrails(
        have="""\
        :rsm:

        ```
        :lang: python

        def hello():
            print("world")
        ```

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Code Block</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        </div>

        </body>
        """,
    )


def test_manuscript():
    compare_have_want_handrails(
        have="""
        :rsm:
        :title: Some Title

        Hello.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Title</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        </div>

        </body>
        """,
    )


def test_section():
    compare_have_want_handrails(
        have="""
        :rsm:
        :title: Some Title

        ## Section
        Hello.

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Title</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        <section class="section level-2" data-nodeid="1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Section 1</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        </div>

        </body>
        """,
    )


def test_abstract():
    compare_have_want_handrails(
        have="""
        :rsm:
        :title: Some Title

        :abstract:
          The abstract.
        ::

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Title</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Abstract</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h3>Abstract</h3>

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

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        </div>

        </body>
        """,
    )


def test_theorem():
    compare_have_want_handrails(
        have="""
        :rsm:

        :theorem:

        Hello.

        ::

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="theorem hr hr-labeled" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Theorem 1</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        </div>

        </body>
        """,
    )


def test_author():
    compare_have_want_handrails(
        have=r"""
        :rsm:
          :title: Indefinite Linear Algebra of the NBM
          :date: 2024-04-13


        :author:
          :name: Leo Torres
          :email: leo@leotrs.com
        ::

        ::
        """,
        want=r"""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Title</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        <div class="author hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Author</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Leo Torres</p>

        <p><a href="mailto:leo@leotrs.com">leo@leotrs.com</a></p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_bibliography():
    compare_have_want_handrails(
        have="""
        :rsm:

        This is a citation :cite:atiyah2018introduction::.

        :bibliography: ::

        ::

        :bibtex:

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
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>This is a citation [<a id="cite-0" class="reference cite" href="#atiyah2018introduction">1</a>].</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <section class="level-2">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Bibliography</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        <div class="hr-menu">

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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
        <a id="atiyah2018introduction-doi" class="bibitem-doi" href="https://doi.org/https://doi.org/10.1201/9780429493638" target="_blank">
        <div class="icon ext">
                        </div></a>
        </div>
        </div>

        </div>

        </div>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_inline_math_followed_by_dot():
    compare_have_want_handrails(
        have="""
        :rsm:
          :title: title

        one $2+2=4$.

        two $2+2=4$ baz.

        three $2+2=4$. Another sentence.

        ::
        """,
        want=r"""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Title</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>one <span class="inline-math-wrapper">
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

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>three <span class="inline-math-wrapper">
        <span class="math" data-nodeid="13">\(2+2=4\)</span><span>.</span></span> Another sentence.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_mathblock_nonum():
    compare_have_want_handrails(
        have="""
        :rsm:

        This one has a number
        $$
        2+2=4
        $$

        And this one does not
        $$
        :nonum:
        2+2=4
        $$

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Equation (1)</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Equation</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        </div>

        </body>
        """,
    )


def test_toc_no_labels():
    compare_have_want_handrails(
        have="""
        :rsm:
                  :title: Foo

                :abstract:
                  Abs.
                ::

                :toc:

                ## Section

                ## Section

                ### Sub-section

                ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">
        <div class="float-minimap-wrapper">
        <div class="minimap">

                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 104" fill="#3C4952" preserveAspectRatio="xMinYMid meet" stroke-width="0">
                  <defs>

                    <linearGradient id="purple-green-scroll" x1="0%" x2="0%" y1="0%" y2="100%" gradientUnits="userSpaceOnUse">
                      <stop offset="0%" stop-color="#AD71F2" />
                      <stop id="stop-follow-scroll-1" offset="100%" stop-color="#1FB5A2" />
                      <stop id="stop-follow-scroll-2" offset="100%" stop-color="#DAE1E5" />
                      <stop offset="100%" stop-color="#DAE1E5" />
                    </linearGradient>

                    <mask id="gradient-mask">
                      <rect width="100%" height="100%" fill="url(#purple-green-scroll)" />
                    </mask>

                  </defs>

                  <g fill="url(#purple-green-scroll)">
                    <rect x="14" y="24" width="4" height="56" />
            <a href="#" class="reference" tabindex="-1"><circle id="mm-" cx="16" cy="20" r="8" data-pos="20" />
            <circle cx="16" cy="20" r="4" fill="#FCFEFF" data-pos="20" /></a>
            <a href="#" class="reference" tabindex="-1"><circle id="mm-" cx="16" cy="52" r="8" data-pos="52" />
            <circle cx="16" cy="52" r="4" fill="#FCFEFF" data-pos="52" /></a>
            <a href="#" class="reference" tabindex="-1"><circle id="mm-" cx="16" cy="84" r="6" data-pos="84" />
            <circle cx="16" cy="84" r="2" fill="#FCFEFF" data-pos="84" /></a></g>
        </svg>
        </div>
        </div>
        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Title</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h1>Foo</h1>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="abstract" data-nodeid="1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Abstract</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h3>Abstract</h3>

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

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Abs.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        <div class="toc">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Contents</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h3>Table of Contents</h3>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="toc-wrapper">

        <div class="minimap">

                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 104" fill="#3C4952" preserveAspectRatio="xMinYMid meet" stroke-width="0">
                  <defs>

                    <linearGradient id="purple-green-mouse" x1="0%" x2="0%" y1="0%" y2="100%" gradientUnits="userSpaceOnUse">
                      <stop offset="0%" stop-color="#AD71F2" />
                      <stop id="stop-follow-mouse-1" offset="100%" stop-color="#1FB5A2" />
                      <stop id="stop-follow-mouse-2" offset="100%" stop-color="#DAE1E5" />
                      <stop offset="100%" stop-color="#DAE1E5" />
                    </linearGradient>

                    <mask id="gradient-mask">
                      <rect width="100%" height="100%" fill="url(#purple-green-mouse)" />
                    </mask>

                  </defs>

                  <g fill="url(#purple-green-mouse)">
                    <rect x="14" y="24" width="4" height="56" />
            <circle cx="16" cy="20" r="8" data-pos="20" />
            <circle cx="16" cy="20" r="4" fill="#FCFEFF" data-pos="20" />
            <circle cx="16" cy="52" r="8" data-pos="52" />
            <circle cx="16" cy="52" r="4" fill="#FCFEFF" data-pos="52" />
            <circle cx="16" cy="84" r="6" data-pos="84" />
            <circle cx="16" cy="84" r="2" fill="#FCFEFF" data-pos="84" /></g>
        </svg>
        </div>

        <ul class="contents" data-nodeid="4">

        <li class="item" data-nodeid="5">
        <a class="reference" href="#">1. Section</a>
        </li>

        <li class="item" data-nodeid="7">
        <a class="reference" href="#">2. Section</a>
        <ul class="itemize" data-nodeid="9">

        <li class="item" data-nodeid="10">
        <a class="reference" href="#">2.1. Sub-section</a>
        </li>

        </ul>

        </li>

        </ul>

        </div>

        </div>

        <section class="section level-2" data-nodeid="12">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Section 1</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        </section>

        <section class="section level-2" data-nodeid="13">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Section 2</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h2>2. Section</h2>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <section class="subsection level-3" data-nodeid="14">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Section 2.1</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h3>2.1. Sub-section</h3>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
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


def test_toc_with_labels():
    compare_have_want_handrails(
        have="""
        :rsm:
                  :title: Foo

                :abstract:
                  Abs.
                ::

                :toc:

                ## Section
                  :label: sec-1

                ## Section
                  :label: sec-2

                ### Sub-section
                  :label: sub-sec

                ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">
        <div class="float-minimap-wrapper">
        <div class="minimap">

                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 104" fill="#3C4952" preserveAspectRatio="xMinYMid meet" stroke-width="0">
                  <defs>

                    <linearGradient id="purple-green-scroll" x1="0%" x2="0%" y1="0%" y2="100%" gradientUnits="userSpaceOnUse">
                      <stop offset="0%" stop-color="#AD71F2" />
                      <stop id="stop-follow-scroll-1" offset="100%" stop-color="#1FB5A2" />
                      <stop id="stop-follow-scroll-2" offset="100%" stop-color="#DAE1E5" />
                      <stop offset="100%" stop-color="#DAE1E5" />
                    </linearGradient>

                    <mask id="gradient-mask">
                      <rect width="100%" height="100%" fill="url(#purple-green-scroll)" />
                    </mask>

                  </defs>

                  <g fill="url(#purple-green-scroll)">
                    <rect x="14" y="24" width="4" height="56" />
            <a href="#sec-1" class="reference" tabindex="-1"><circle id="mm-sec-1" cx="16" cy="20" r="8" data-pos="20" />
            <circle cx="16" cy="20" r="4" fill="#FCFEFF" data-pos="20" /></a>
            <a href="#sec-2" class="reference" tabindex="-1"><circle id="mm-sec-2" cx="16" cy="52" r="8" data-pos="52" />
            <circle cx="16" cy="52" r="4" fill="#FCFEFF" data-pos="52" /></a>
            <a href="#sub-sec" class="reference" tabindex="-1"><circle id="mm-sub-sec" cx="16" cy="84" r="6" data-pos="84" />
            <circle cx="16" cy="84" r="2" fill="#FCFEFF" data-pos="84" /></a></g>
        </svg>
        </div>
        </div>
        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Title</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h1>Foo</h1>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="abstract" data-nodeid="1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Abstract</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h3>Abstract</h3>

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

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Abs.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        <div class="toc">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Contents</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h3>Table of Contents</h3>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="toc-wrapper">

        <div class="minimap">

                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 104" fill="#3C4952" preserveAspectRatio="xMinYMid meet" stroke-width="0">
                  <defs>

                    <linearGradient id="purple-green-mouse" x1="0%" x2="0%" y1="0%" y2="100%" gradientUnits="userSpaceOnUse">
                      <stop offset="0%" stop-color="#AD71F2" />
                      <stop id="stop-follow-mouse-1" offset="100%" stop-color="#1FB5A2" />
                      <stop id="stop-follow-mouse-2" offset="100%" stop-color="#DAE1E5" />
                      <stop offset="100%" stop-color="#DAE1E5" />
                    </linearGradient>

                    <mask id="gradient-mask">
                      <rect width="100%" height="100%" fill="url(#purple-green-mouse)" />
                    </mask>

                  </defs>

                  <g fill="url(#purple-green-mouse)">
                    <rect x="14" y="24" width="4" height="56" />
            <circle cx="16" cy="20" r="8" data-pos="20" />
            <circle cx="16" cy="20" r="4" fill="#FCFEFF" data-pos="20" />
            <circle cx="16" cy="52" r="8" data-pos="52" />
            <circle cx="16" cy="52" r="4" fill="#FCFEFF" data-pos="52" />
            <circle cx="16" cy="84" r="6" data-pos="84" />
            <circle cx="16" cy="84" r="2" fill="#FCFEFF" data-pos="84" /></g>
        </svg>
        </div>

        <ul class="contents" data-nodeid="4">

        <li class="item" data-nodeid="5">
        <a class="reference" href="#sec-1">1. Section</a>
        </li>

        <li class="item" data-nodeid="7">
        <a class="reference" href="#sec-2">2. Section</a>
        <ul class="itemize" data-nodeid="9">

        <li class="item" data-nodeid="10">
        <a class="reference" href="#sub-sec">2.1. Sub-section</a>
        </li>

        </ul>

        </li>

        </ul>

        </div>

        </div>

        <section id="sec-1" class="section level-2" data-nodeid="12">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Section 1</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
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

        </section>

        <section id="sec-2" class="section level-2" data-nodeid="13">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Section 2</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h2>2. Section</h2>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <section id="sub-sec" class="subsection level-3" data-nodeid="14">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse">
                      </div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Section 2.1</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h3>2.1. Sub-section</h3>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
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
