import rsm

from conftest import compare_have_want


def test_numbered_sections():
    compare_have_want(
        have="""\
        ## First

        Content of first.

        ## Second

        Content of second.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section id="sec-1" class="section level-2" data-nodeid="1">

        <h2>1. First</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Content of first.</p>

        </div>

        </section>

        <section id="sec-2" class="section level-2" data-nodeid="4">

        <h2>2. Second</h2>

        <div class="paragraph" data-nodeid="5">

        <p>Content of second.</p>

        </div>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_appendix_before_references():
    """Regression: appendix before references must not crash autonumbering.

    The appendix stamp resets section counters to A, B, C... but must not
    affect bibitem counters. Previously, the entire counts[Manuscript] dict
    was replaced, breaking numbering for bibitems that appear after the
    appendix.
    """
    source = """\
    ## Introduction
    {:label: sec-intro}

    Some text :cite:foo2020::.

    :appendix:

    ## Extra Details
    {:label: sec-extra}

    More content.

    :references:

    @article{foo2020,
      title={A test paper},
      author={Foo, B.},
      year={2020},
      journal={Journal of Testing},
      doi={10.1234/test}
    }

    ::
    """
    result = rsm.render(source, handrails=False, add_source=False)
    assert "A. Extra Details" in result
    assert "foo2020" in result


def test_nonum():
    compare_have_want(
        have="""\
        ## First

        Content of first.

        ## Second {
          :nonum:
        }

        Content of second.

        ## Third

        Content of third.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section id="sec-1" class="section level-2" data-nodeid="1">

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

        <section id="sec-2" class="section level-2" data-nodeid="7">

        <h2>2. Third</h2>

        <div class="paragraph" data-nodeid="8">

        <p>Content of third.</p>

        </div>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )
