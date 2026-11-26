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
    assert s.reftext.strip() == "Step"
    m = rsm.nodes.MathBlock()
    assert m.reftext.strip() == "the equation"


def test_nonum():
    s = rsm.nodes.Step(nonum=True)
    assert s.reftext.strip() == "Step"
    m = rsm.nodes.MathBlock(nonum=True)
    assert m.reftext.strip() == "the equation"


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


@pytest.mark.parametrize(
    "title", ["", "\n  :title: Pappus chain"], ids=["untitled", "titled"]
)
@pytest.mark.parametrize("case", [NONUM, NUMBERING_OFF], ids=["nonum", "numbering-off"])
def test_an_unnumbered_theorem_is_named_without_a_number(case, title):
    html = _unnumbered_theorem_html(case, title, handrails=True, sidebar=True)
    assert "None" not in html

    # Every :ref: to it: the prose, the step that cites it, and the "Proof of" lead.
    assert html.count('<a class="reference" href="#thm-a">Theorem</a>') == 3
    assert '<span class="span label">Proof of <span class="inline-wrapper">' in html

    assert re.search(
        r'<div id="thm-a" class="theorem[^"]*" data-menu-label="Theorem"', html
    )

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
        {"config": "", "nonum": ""},
        "\n  :title: Pappus chain",
        handrails=True,
        sidebar=True,
    )
    assert html.count('<a class="reference" href="#thm-a">Theorem 1.1</a>') == 3
    assert re.search(
        r'<div id="thm-a" class="theorem[^"]*" data-menu-label="Theorem 1.1"', html
    )
    names = re.findall(r'<span class="rail-proof-name">([^<]*)</span>', html)
    assert names == [
        "Proof of Theorem 1.1",
        "Proof of Theorem 1.2",
        "Proof of Theorem 1.1",
    ]


def test_an_unnumbered_node_reftext_has_no_number():
    thm = rsm.nodes.Theorem(nonum=True)
    assert thm.full_number is None
    assert thm.reftext == "Theorem"
    sec = rsm.nodes.Section(nonum=True)
    assert sec.reftext == "Section"


# Custom link text that wraps onto more source lines (rsm-qmp). The scanner ends
# a text token at a newline, so each line is its own child of the reftext.
_WRAPPED_REF = "# T\n\n:span:{:label: x} target::\n\nSee :ref:x,TEXT::.\n"
_WRAPPED_URL = "# T\n\nSee :url:https://a.com,TEXT::.\n"


@pytest.mark.parametrize(
    "text, want, want_flat",
    [
        ("one\ntwo", "one two", "one two"),
        ("one\ntwo\nthree", "one two three", "one two three"),
        ("one\n*two*", 'one <span class="span"><em>two</em></span>', "one two"),
        (
            "one\n$x$\nthree",
            'one <span class="math">\\(x\\)</span> three',
            "one x three",
        ),
    ],
    ids=["two-lines", "three-lines", "emph-on-second-line", "math-on-second-line"],
)
@pytest.mark.parametrize(
    "src, opening",
    [
        (_WRAPPED_REF, '<a class="reference" href="#x">'),
        (_WRAPPED_URL, '<a href="https://a.com">'),
    ],
    ids=["ref", "url"],
)
def test_link_text_over_several_lines_keeps_every_line(
    src, opening, text, want, want_flat
):
    source = src.replace("TEXT", text)
    html = rsm.render(source, handrails=False, source_offsets=False)
    assert f"{opening}{want}</a>" in html
    tree = rsm.tsparser.TSParser().parse(source)
    (link,) = [n for n in tree.traverse() if isinstance(n, rsm.nodes.BaseReference)]
    assert link.overwrite_reftext == want_flat


# Link text of a reference to a paragraph, a list or a list item (rsm-5bda,
# Leo 2026-11-25). An item of a numbered list shows the marker that braiid.css
# draws for it: decimal, then lower-alpha, then lower-roman.


def _link_text(src, label):
    html = rsm.render(src, handrails=False)
    found = re.findall(rf'<a class="reference" href="#{label}">([^<]*)</a>', html)
    assert len(found) == 1, html
    return found[0]


def _list_doc(kind, items, label):
    body = "\n\n".join(f"  {item}" for item in items)
    return f"# T\n\n:{kind}: {{:label: lst}}\n\n{body}\n\n::\n\nSee :ref:{label}::.\n"


@pytest.mark.parametrize("kind", ["enumerate", "itemize"])
def test_a_reference_to_a_list_reads_list(kind):
    src = _list_doc(kind, [":-: one", ":-: two"], "lst")
    assert _link_text(src, "lst") == "List"


def test_a_reference_to_a_numbered_item_has_its_number():
    src = _list_doc("enumerate", [":-: one", ":-: {:label: x} two"], "x")
    assert _link_text(src, "x") == "Item 2"


def test_a_reference_to_a_nested_numbered_item_has_a_letter():
    items = [":-: one", ":-: two", ":--: two a", ":--: {:label: x} two b"]
    assert _link_text(_list_doc("enumerate", items, "x"), "x") == "Item 2.b"


def test_a_reference_to_a_third_level_numbered_item_has_a_roman_numeral():
    items = [
        ":-: one",
        ":-: two",
        ":--: two a",
        ":---: two a i",
        ":---: two a ii",
        ":---: two a iii",
        ":---: {:label: x} two a iv",
    ]
    assert _link_text(_list_doc("enumerate", items, "x"), "x") == "Item 2.a.iv"


def test_letters_after_z_follow_the_list_marker():
    items = [":-: one"] + [f":--: sub {n}" for n in range(27)]
    items.append(":--: {:label: x} sub 28")
    assert _link_text(_list_doc("enumerate", items, "x"), "x") == "Item 1.ab"


def test_a_reference_to_a_bulleted_item_reads_item():
    items = [":-: one", ":-: {:label: x} two", ":--: {:label: y} two a"]
    src = _list_doc("itemize", items, "x") + "And :ref:y::.\n"
    assert _link_text(src, "x") == "Item"
    assert _link_text(src, "y") == "Item"


def test_a_reference_to_a_paragraph_reads_paragraph():
    src = "# T\n\n:paragraph: {:label: x} Some text.\n\nSee :ref:x::.\n"
    assert _link_text(src, "x") == "Paragraph"


def test_the_table_of_contents_keeps_its_reftext():
    assert rsm.nodes.Contents().reftext == "Contents"


@pytest.mark.parametrize(
    "kind, items, label",
    [
        ("enumerate", [":-: one"], "lst"),
        ("itemize", [":-: one"], "lst"),
        ("enumerate", [":-: one", ":-: {:label: x :reftext: the second} two"], "x"),
        ("itemize", [":-: {:label: x :reftext: the second} two"], "x"),
    ],
    ids=["enumerate", "itemize", "numbered-item", "bulleted-item"],
)
def test_reftext_meta_key_wins_for_lists_and_items(kind, items, label):
    src = _list_doc(kind, items, label)
    if label == "lst":
        src = src.replace("{:label: lst}", "{:label: lst :reftext: the second}")
    assert _link_text(src, label) == "the second"


def test_a_ref_to_an_unnumbered_step_reads_step():
    src = """# T

:theorem: {:label: thm} A claim.::

:proof:
  :step: {:label: st-a, :nonum:} Foo.::
  :step: {:label: st-b} Bar.::
  :step: :qed: By :ref:st-a:: and :ref:st-b::.::
::
"""
    html = rsm.render(src)
    refs = re.findall(r'<a class="reference" href="#st-[ab]">([^<]*)</a>', html)
    assert refs[0] == "Step"
    assert re.fullmatch(r"Step ⟨\d⟩", refs[1])
