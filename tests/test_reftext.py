import re

import pytest

import rsm
from conftest import compare_have_want


def test_mechanism():
    cls = rsm.nodes.Section
    node = cls()
    assert node.classreftext == cls.classreftext
    assert node.reftext_template == cls.classreftext
    assert node.reftext == "Section"

    node.reftext_template = "foobar"
    assert node.classreftext == cls.classreftext
    assert node.reftext_template == "foobar"
    assert node.reftext == "foobar"
    node.reftext_template = "{number}"
    assert node.reftext == ""
    node.number = 1
    assert node.reftext == "1"

    node = cls(reftext_template="foobar")
    assert node.classreftext == cls.classreftext
    assert node.reftext_template == "foobar"
    node.reftext_template = "{number}"
    assert node.reftext == ""
    node.number = 1
    assert node.reftext == "1"


def test_defaults():
    t = rsm.nodes.Theorem()
    assert t.reftext.strip() == "Theorem"
    p = rsm.nodes.Proof()
    assert p.reftext.strip() == "Proof"
    s = rsm.nodes.Step()
    assert s.reftext.strip() == "Step ⟨⟩"
    m = rsm.nodes.MathBlock()
    assert m.reftext.strip() == "()"


def test_nonum():
    s = rsm.nodes.Step(nonum=True)
    assert s.reftext.strip() == "Step ⟨⟩"
    m = rsm.nodes.MathBlock(nonum=True)
    assert m.reftext.strip() == "()"


def test_simple():
    compare_have_want(
        have="""\
        Some math
        :mathblock: {
          :label: eqn
          :reftext: Important Equation
        }
          2+2=4
        ::

        Here we refer to the :ref:eqn::.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Some math </p>
        <div id="eqn" class="mathblock" data-nodeid="3">
        $$
        2+2=4
        $$
        </div>

        </div>

        <div class="paragraph" data-nodeid="5">

        <p>Here we refer to the <span class="inline-wrapper"><a class="reference" href="#eqn">Important Equation</a><span>.</span></span></p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


# A node with no number, because of :nonum: or because the manuscript turns numbering off, is
# named without the number: "Theorem", not "Theorem None". The name reaches the reader through
# :ref: links, the handrail menu header, the "Proof of" lead of a detached proof, and the
# sidebar's Proof panel (proof list, proof tree nodes and collapsed card).
UNNUMBERED_THEOREM = """\
# T

{config}## One

:theorem: {{
  :label: thm-a{nonum}{title}
}}
  A claim.
::

:proof:
  :step: {{:label: st-1}} Foo.::
  :step: :qed: Done.::
::

:theorem: {{:label: thm-b}} Another.::

:proof:
  :step: :qed: By :ref:thm-a::.::
::

## Two

:proof: {{:of: thm-a}}
  :step: :qed: Again.::
::

See :ref:thm-a::.
"""
NONUM = {"config": "", "nonum": "\n  :nonum:"}
NUMBERING_OFF = {"config": ":config: {\n  :numbering: none\n}\n::\n\n", "nonum": ""}


def _unnumbered_theorem_html(case, title, **kwargs):
    return rsm.render(UNNUMBERED_THEOREM.format(**case, title=title), **kwargs)


@pytest.mark.parametrize("title", ["", "\n  :title: Pappus chain"], ids=["untitled", "titled"])
@pytest.mark.parametrize("case", [NONUM, NUMBERING_OFF], ids=["nonum", "numbering-off"])
def test_an_unnumbered_theorem_is_named_without_a_number(case, title):
    html = _unnumbered_theorem_html(case, title, handrails=True, sidebar=True)
    assert "None" not in html

    # Every :ref: to it: the prose, the step that cites it, and the "Proof of" lead.
    assert html.count('<a class="reference" href="#thm-a">Theorem</a>') == 3
    assert '<span class="span label">Proof of <span class="inline-wrapper">' in html

    assert re.search(r'<div id="thm-a" class="theorem[^"]*" data-menu-label="Theorem"', html)

    # The Proof panel: the proof list, the collapsed card of each of its proofs, the root of
    # each of their trees, and the result node in the tree of the proof that cites it. The
    # second proof is of thm-b, which has no number either when numbering is off.
    names = re.findall(r'<span class="rail-proof-name">([^<]*)</span>', html)
    assert names[0] == names[2] == "Proof of Theorem"
    cards = re.findall(r'<span class="rail-collapsed-title">([^<]*)</span>', html)
    assert cards[0] == cards[2] == "Theorem"
    assert re.search(
        r'<a href="#thm-a" class="toc-node level-1 toc-node-result" [^>]*'
        r'data-tooltip="Theorem" aria-label="Theorem">',
        html,
    )


@pytest.mark.parametrize("case", [NONUM, NUMBERING_OFF], ids=["nonum", "numbering-off"])
def test_a_ref_to_an_unnumbered_theorem_without_handrails(case):
    html = _unnumbered_theorem_html(case, "")
    assert "None" not in html
    assert html.count('<a class="reference" href="#thm-a">Theorem</a>') == 3


def test_a_numbered_theorem_keeps_its_number():
    html = _unnumbered_theorem_html(
        {"config": "", "nonum": ""}, "\n  :title: Pappus chain", handrails=True, sidebar=True
    )
    assert html.count('<a class="reference" href="#thm-a">Theorem 1.1</a>') == 3
    assert re.search(r'<div id="thm-a" class="theorem[^"]*" data-menu-label="Theorem 1.1"', html)
    names = re.findall(r'<span class="rail-proof-name">([^<]*)</span>', html)
    assert names == ["Proof of Theorem 1.1", "Proof of Theorem 1.2", "Proof of Theorem 1.1"]


def test_an_unnumbered_node_reftext_has_no_number():
    thm = rsm.nodes.Theorem(nonum=True)
    assert thm.full_number is None
    assert thm.reftext == "Theorem"
    sec = rsm.nodes.Section(nonum=True)
    assert sec.reftext == "Section"
