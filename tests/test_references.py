import rsm
from conftest import compare_have_want
from rsm.transformer import Transformer


def test_reftext():
    compare_have_want(
        have="""\
        :section:{
          :title: First
          :label: sec-lbl}

        Content of first.

        This is a paragraph that refers to :ref:sec-lbl::.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section id="sec-lbl" class="section level-2" data-nodeid="1">

        <h2>1. First</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Content of first.</p>

        </div>

        <div class="paragraph" data-nodeid="4">

        <p>This is a paragraph that refers to <span class="inline-wrapper"><a class="reference" href="#sec-lbl">Section 1</a><span>.</span></span></p>

        </div>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_overwrite_reftext():
    compare_have_want(
        have="""\
        :section: {
          :title: First
          :label: sec-lbl
        }
        Content of first.

        This is a paragraph that refers to :ref:sec-lbl,The Section::.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section id="sec-lbl" class="section level-2" data-nodeid="1">

        <h2>1. First</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Content of first.</p>

        </div>

        <div class="paragraph" data-nodeid="4">

        <p>This is a paragraph that refers to <span class="inline-wrapper"><a class="reference" href="#sec-lbl">The Section</a><span>.</span></span></p>

        </div>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_ref_reftext_inline_markup(caplog):
    """The display text of :ref: accepts inline markup, which survives
    reference resolution and renders as real HTML (rsm-z1e)."""
    src = (
        "# T\n\n:theorem: {:label: thm-x}\n  A statement. ::\n\n"
        "See :ref:thm-x, the **main** result::.\n"
    )
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert "The CST contains errors." not in caplog.text, caplog.text
    assert "[CST error" not in h, h
    assert (
        '<a class="reference" href="#thm-x">the <span class="span">'
        "<strong>main</strong></span> result</a>" in h
    ), h

    tree = rsm.tsparser.TSParser().parse(src)
    transformed = Transformer().transform(tree)
    ref = next(
        n for n in transformed.traverse() if n.__class__.__name__ == "Reference"
    )
    assert ref.overwrite_reftext == "the main result"
    assert [n.__class__.__name__ for n in ref.reftext_nodes] == [
        "Text",
        "Span",
        "Text",
    ]


def test_ref_to_unknown_label(caplog):
    compare_have_want(
        have="""\
        this doesn't exist :ref:foo::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>this doesn't exist <span class="error" data-nodeid="3">[unknown label "foo"]</span></p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )
    assert "Reference to nonexistent label" in caplog.text


def test_cite_to_unknown_label(caplog):
    compare_have_want(
        have="""\
        This is an unknown cite :cite:foobar::.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is an unknown cite <span class="nowrap">[<a id="cite-0" class="reference cite unknown" href="#">[unknown label "foobar"]</a>]</span>.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )
    assert "Reference to nonexistent label" in caplog.text


def test_bibitem_without_doi(caplog):
    """Bibitem without DOI renders correctly"""
    compare_have_want(
        have="""\
        Text citing :cite: smith2024 ::.

        :references:
        @article{smith2024,
          title = {My Paper},
          author = {Jane Smith},
          year = {2024},
          journal = {Nature}
        }
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Text citing <span class="nowrap">[<a id="cite-0" class="reference cite" href="#smith2024">1</a>]</span>.</p>

        </div>

        <section class="level-2">

        <h2>References</h2>

        <ol class="bibliography" data-nodeid="5">

        <li id="smith2024" class="bibitem" data-nodeid="6">
        <div class="bib-card"><span class="bib-num">1</span><div class="bib-body"><div class="bib-who">Jane Smith (2024)</div><div class="bib-title">My Paper</div><div class="bib-venue">Nature</div><div class="bib-links"><span class="bib-cited">cited <a class="reference backlink" href="#cite-0" aria-label="Back to the citation">↖</a></span></div></div></div>
        </li>

        </ol>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )
    assert "Bibitem smith2024 has no DOI" in caplog.text


def test_ref_with_class_meta():
    """Ref with {:class: ...} meta parses into a PendingReference with classes."""
    src = "Text :ref:{:class: depends_on}some-slug:: end."
    parser = rsm.tsparser.TSParser()
    tree = parser.parse(src)

    refs = [n for n in tree.traverse() if isinstance(n, rsm.nodes.PendingReference)]
    assert len(refs) == 1
    ref = refs[0]
    assert ref.target == "some-slug"
    assert ref.classes == ["depends_on"]


def test_ref_with_class_meta_and_reftext():
    """Ref with {:class:} and display text."""
    src = "See :ref:{:class: generalizes}thm-42, Main Result:: for details."
    parser = rsm.tsparser.TSParser()
    tree = parser.parse(src)

    refs = [n for n in tree.traverse() if isinstance(n, rsm.nodes.PendingReference)]
    assert len(refs) == 1
    ref = refs[0]
    assert ref.target == "thm-42"
    assert ref.classes == ["generalizes"]
    assert ref.overwrite_reftext.strip() == "Main Result"


def test_ref_without_class_meta_still_works():
    """Plain :ref:slug:: without meta still works after grammar change."""
    src = "See :ref:some-ref:: here."
    parser = rsm.tsparser.TSParser()
    tree = parser.parse(src)

    refs = [n for n in tree.traverse() if isinstance(n, rsm.nodes.PendingReference)]
    assert len(refs) == 1
    assert refs[0].target == "some-ref"
    assert refs[0].classes == []


def test_bibitem_with_doi():
    """Bibitem with DOI renders correctly with link"""
    compare_have_want(
        have="""\
        Text citing :cite: smith2024 ::.

        :references:
        @article{smith2024,
          title = {My Paper},
          author = {Jane Smith},
          year = {2024},
          journal = {Nature},
          doi = {10.1234/example}
        }
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Text citing <span class="nowrap">[<a id="cite-0" class="reference cite" href="#smith2024">1</a>]</span>.</p>

        </div>

        <section class="level-2">

        <h2>References</h2>

        <ol class="bibliography" data-nodeid="5">

        <li id="smith2024" class="bibitem" data-nodeid="6">
        <div class="bib-card"><span class="bib-num">1</span><div class="bib-body"><div class="bib-who">Jane Smith (2024)</div><div class="bib-title">My Paper</div><div class="bib-venue">Nature</div><div class="bib-links"><a id="smith2024-doi" class="bibitem-doi" href="https://doi.org/10.1234/example" target="_blank">doi.org/10.1234/example</a><span class="bib-cited">cited <a class="reference backlink" href="#cite-0" aria-label="Back to the citation">↖</a></span></div></div></div>
        </li>

        </ol>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )
