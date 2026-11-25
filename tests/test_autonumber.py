import logging
import re
from pathlib import Path

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
    result = rsm.render(source, handrails=False, source_offsets=False)
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

        <section id="sec-n4" class="section level-2" data-nodeid="4">

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


def test_theorem_and_figure_without_sections_log_no_warning(caplog):
    asset = Path(__file__).parent / "assets" / "test.html"
    src = f"""\
# T

:theorem:

  Statement.

::

:figure: {{
  :path: {asset}
}}
:caption: A caption.
::
"""
    caplog.set_level(logging.WARNING, logger="RSM")
    html = rsm.render(src, handrails=True)
    assert [r.getMessage() for r in caplog.records] == []
    assert "Theorem 1." in html
    assert "Figure 1." in html


TABLES_AND_ALGORITHMS = r"""# T

{config}{section_one}:table: {{:label: tab1}}
:tbody:
:tr: :td:a:: ::
::
:caption: First.
::

:algorithm: {{:label: alg1}}
\begin{{algorithm}}
\begin{{algorithmic}}
\STATE $x = 1$
\end{{algorithmic}}
\end{{algorithm}}
::

{section_two}:table: {{:label: tab2}}
:tbody:
:tr: :td:b:: ::
::
:caption: Second.
::

:table: {{:label: tab3}}
:tbody:
:tr: :td:c:: ::
::
:caption: Third.
::

:algorithm: {{:label: alg2}}
\begin{{algorithm}}
\begin{{algorithmic}}
\STATE $x = 2$
\end{{algorithmic}}
\end{{algorithm}}
::

See :ref:tab1::, :ref:tab2::, :ref:tab3::, :ref:alg1:: and :ref:alg2::.
"""


def _numbers(config="", sections=True):
    src = TABLES_AND_ALGORITHMS.format(
        config=config,
        section_one="## One\n\n" if sections else "",
        section_two="## Two\n\n" if sections else "",
    )
    html = rsm.render(src, handrails=True)
    captions = re.findall(r'<span class="label">([^<]*)</span>', html)
    references = re.findall(r'<a class="reference"[^>]*>([^<]*)</a>', html)
    menus = [
        label
        for label in re.findall(r'data-menu-label="([^"]+)"', html)
        if label.startswith("Algorithm")
    ]
    return captions, references, menus


def test_tables_and_algorithms_are_numbered_within_their_section():
    captions, references, menus = _numbers()
    assert captions == ["Table 1.1. ", "Table 2.1. ", "Table 2.2. "]
    assert references == [
        "Table 1.1",
        "Table 2.1",
        "Table 2.2",
        "Algorithm 1.1",
        "Algorithm 2.1",
    ]
    assert menus == ["Algorithm 1.1", "Algorithm 2.1"]


def test_tables_and_algorithms_without_sections_are_numbered_through_the_document():
    captions, references, menus = _numbers(sections=False)
    assert captions == ["Table 1. ", "Table 2. ", "Table 3. "]
    assert references == [
        "Table 1",
        "Table 2",
        "Table 3",
        "Algorithm 1",
        "Algorithm 2",
    ]
    assert menus == ["Algorithm 1", "Algorithm 2"]


def test_numbering_document_numbers_tables_and_algorithms_through_the_document():
    captions, references, menus = _numbers(
        config=":config: {\n  :numbering: document\n}\n::\n\n"
    )
    assert captions == ["Table 1. ", "Table 2. ", "Table 3. "]
    assert references == [
        "Table 1",
        "Table 2",
        "Table 3",
        "Algorithm 1",
        "Algorithm 2",
    ]
    assert menus == ["Algorithm 1", "Algorithm 2"]


def test_numbering_none_leaves_tables_and_algorithms_without_numbers():
    captions, references, menus = _numbers(
        config=":config: {\n  :numbering: none\n}\n::\n\n"
    )
    assert captions == ["Table. ", "Table. ", "Table. "]
    assert references == ["Table", "Table", "Table", "Algorithm", "Algorithm"]


def _config(numbering):
    return ":config: {\n  :numbering: " + numbering + "\n}\n::\n\n"


SECTIONS = """# T

{config}## One

Text.

## Two

### Sub
{{:label: sub}}

#### Subsub
{{:label: subsub}}

:theorem: {{:label: thm}} A theorem.
::

See :ref:sub::, :ref:subsub:: and :ref:thm::.
"""


def test_numbering_document_numbers_subsections_within_their_section():
    html = rsm.render(SECTIONS.format(config=_config("document")), handrails=True)
    headings = re.findall(r"<h[34]>([^<]*)</h[34]>", html)
    references = re.findall(r'<a class="reference"[^>]*>([^<]*)</a>', html)
    assert headings == ["2.1. Sub", "2.1.1. Subsub"]
    assert references == ["Section 2.1", "Section 2.1.1", "Theorem 1"]


CITATION = """# T

{config}See :cite:knuth::.

:references:
  @book{{knuth,
    title={{Art of Computer Programming}},
    author={{Knuth, Donald E}},
    year={{2014}},
    publisher={{Addison-Wesley}}
  }}
::
"""


def _cite_text(html):
    m = re.search(r"<p>See (.*?)\.</p>", html, re.S)
    assert m
    return re.sub(r"<[^>]+>", "", m.group(1)).replace(" ", " ").strip()


def test_numbering_none_keeps_citation_numbers():
    html = rsm.render(CITATION.format(config=_config("none")), handrails=True)
    assert _cite_text(html) == "[1]"
    assert '<span class="bib-num">1</span>' in html


def test_numbering_none_keeps_author_year_citations():
    config = (
        ":config: {\n  :numbering: none\n  :citation-style: parens-author-year\n}"
        "\n::\n\n"
    )
    html = rsm.render(CITATION.format(config=config), handrails=True)
    assert _cite_text(html) == "(Knuth, 2014)"


EQUATIONS = """# T

{config}## One

$$ {{:label: eq}}
x
$$

$$ {{:label: eqr, :reftext: the key bound}}
y
$$

See :ref:eq:: and :ref:eqr::.
"""


def test_numbering_none_equation_reference_reads_the_equation():
    html = rsm.render(EQUATIONS.format(config=_config("none")), handrails=True)
    references = re.findall(r'<a class="reference"[^>]*>([^<]*)</a>', html)
    assert references == ["the equation", "the key bound"]


def test_reference_to_nonum_equation_reads_the_equation():
    src = "# T\n\n$$ {:label: eq, :nonum:}\nx\n$$\n\nSee :ref:eq::.\n"
    html = rsm.render(src, handrails=True)
    references = re.findall(r'<a class="reference"[^>]*>([^<]*)</a>', html)
    assert references == ["the equation"]
