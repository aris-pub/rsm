"""The :calc: construct: an equational/calculational proof -- a chain of relation
steps, each carrying a justification.

This file covers parsing + node mapping; rendering is exercised separately.
"""

import re

import pytest

from rsm import nodes, tsparser
from rsm.app import ProcessorApp
from rsm.transformer import RSMTransformerError

CALC_SRC = """\
:calc:

  :step: $f(x) = a$

    :p: Because the first reason. ::

  ::

  :step: $= b$

    :p: Because the second reason. ::

  ::

::
"""


def _parse(src):
    return tsparser.TSParser().parse(src)


def test_calc_parses_to_a_calc_node():
    tree = _parse(CALC_SRC)
    calcs = list(tree.traverse(nodeclass=nodes.Calc))
    assert len(calcs) == 1


def test_calc_holds_its_relation_steps():
    tree = _parse(CALC_SRC)
    calc = next(iter(tree.traverse(nodeclass=nodes.Calc)))
    steps = [c for c in calc.children if isinstance(c, nodes.Step)]
    assert len(steps) == 2


def test_calc_steps_carry_their_justification():
    tree = _parse(CALC_SRC)
    calc = next(iter(tree.traverse(nodeclass=nodes.Calc)))
    first_step = next(c for c in calc.children if isinstance(c, nodes.Step))
    assert any(isinstance(c, nodes.Subproof) for c in first_step.children)


PROOF_WITH_CALC = """\
:theorem: {:label: thm-c} A claim. ::

:proof: {:of: thm-c}

  :step: First real step. ::

  :calc:

    :step: $f(x) = a$

      :p: First reason. ::

    ::

    :step: $= b$

      :p: Second reason. ::

    ::

  ::

  :step: Second real step. ::

::
"""


def _transform(src):
    # Run the pipeline up to (not including) the translator, so we can inspect
    # the transformed tree (the proof model is built by the transformer).
    app = ProcessorApp(plain=src, handrails=True)
    app.pop_task()  # drop the translator
    return app.run()


def test_calc_steps_stay_out_of_the_proof_dag():
    # The proof has exactly two real steps; the calc's relation steps must not
    # leak into the proof's step DAG as phantom nodes.
    tree = _transform(PROOF_WITH_CALC)
    proof = next(iter(tree.traverse(nodeclass=nodes.Proof)))
    assert len(proof.tree_nodes) == 2


def _render(src, handrails=False):
    return ProcessorApp(plain=src, handrails=handrails).run()


def test_calc_renders_as_a_chain():
    html = _render(CALC_SRC)
    assert 'class="calc"' in html
    # one step per relation, math emitted for native typesetting.
    assert html.count('class="step') == 2
    assert r"\(" in html


def test_calc_in_a_proof_renders_one_halmos_for_the_chain():
    html = _render(PROOF_WITH_CALC)
    # one tombstone for the proof and one for the whole chain.
    assert html.count('class="halmos"') == 2


def test_calc_justifications_start_collapsed():
    # Each relation's justification is collapsed at rest (disclosed on demand);
    # subtractive marker, so JS-off renders the full written proof.
    html = _render(CALC_SRC, handrails=True)
    assert html.count('data-start-collapsed="true"') == 2


# --- :calc: anywhere a display equation can go ------------------------------


def _chain(label: str = "", indent: str = "") -> str:
    """A two-row calc, optionally labelled, indented by `indent`."""
    meta = f" {{:label: {label}}}" if label else ""
    body = f"""\
:calc:{meta}

  :step: $\\sum_{{j=1}}^k a_j = b$

    :p: Because $\\frac{{1}}{{2}} \\le 1$. ::

  ::

  :step: $\\le \\frac{{c}}{{4L}}$

    :p: Because the second reason. ::

  ::

::
"""
    return "".join(
        indent + line if line.strip() else line for line in body.splitlines(True)
    )


TOP_LEVEL = "## Sec\n\nSome text.\n\n" + _chain("eq-c")

IN_PROOF = (
    """\
## Sec

:theorem: {:label: thm-c} A claim. ::

:proof: {:of: thm-c}

  :step: First step. ::

"""
    + _chain("eq-c", "  ")
    + """
  :step: Last step. ::

::
"""
)

IN_STEP_P = (
    """\
## Sec

:theorem: {:label: thm-c} A claim. ::

:proof: {:of: thm-c}

  :step: First step. ::

  :step: {:label: stp-host}

    :claim: The calculation below gives the bound. ::

    :p:

"""
    + _chain("eq-c", "      ")
    + """
    :: ::

::
"""
)

IN_STEP = (
    """\
## Sec

:theorem: {:label: thm-c} A claim. ::

:proof: {:of: thm-c}

  :step: A step that holds a chain.

"""
    + _chain("eq-c", "    ")
    + """
  ::

::
"""
)

IN_THEOREM = (
    """\
## Sec

:theorem: {:label: thm-c}

  A claim with a chain in it.

"""
    + _chain("eq-c", "  ")
    + """
::
"""
)


def _build(src):
    return ProcessorApp(plain=src, handrails=True, strict=True).run()


@pytest.mark.parametrize(
    "src",
    [TOP_LEVEL, IN_PROOF, IN_STEP, IN_STEP_P, IN_THEOREM],
    ids=["top-level", "in-proof", "in-step", "in-step-p", "in-theorem"],
)
def test_calc_builds_anywhere(src):
    tree = _transform(src)
    calc = next(iter(tree.traverse(nodeclass=nodes.Calc)))
    assert [type(c) for c in calc.children] == [nodes.Step, nodes.Step]
    assert 'class="calc' in _build(src)


def test_calc_rejects_a_non_step_child_in_source():
    src = "## Sec\n\n:calc:\n\n  :p: Not a relation. ::\n\n::\n"
    with pytest.raises(nodes.RSMNodeError, match="Calc"):
        _parse(src)


def test_calc_rejects_a_paragraph_child_in_source():
    src = "## Sec\n\n:calc:\n\n  Just some text.\n\n::\n"
    with pytest.raises(nodes.RSMNodeError, match="Calc"):
        _parse(src)


def test_calc_rejects_a_non_step_child_via_the_node_api():
    with pytest.raises(nodes.RSMNodeError):
        nodes.Calc().append(nodes.Paragraph())
    with pytest.raises(nodes.RSMNodeError):
        nodes.Calc().prepend(nodes.MathBlock())
    nodes.Calc().append(nodes.Step())


def test_calc_row_cannot_be_labelled():
    src = """\
## Sec

:calc:

  :step: {:label: stp-row} $a = b$

    :p: Reason. ::

  ::

::
"""
    with pytest.raises(RSMTransformerError, match="calc"):
        _transform(src)


@pytest.mark.parametrize("src", [TOP_LEVEL, IN_STEP_P], ids=["top", "step-p"])
def test_calc_rows_have_no_number(src):
    tree = _transform(src)
    calc = next(iter(tree.traverse(nodeclass=nodes.Calc)))
    for row in calc.children:
        assert row.full_number is None
        assert row.reftext == "Relation"


def _eqn_numbers(html):
    return re.findall(r'<div class="eqn-number"><p>\(([^)]*)\)</p></div>', html)


def test_labelled_calc_takes_an_equation_number():
    assert _eqn_numbers(_build(TOP_LEVEL)) == ["1.1"]


def test_unlabelled_calc_has_no_equation_number():
    src = "## Sec\n\n$$\na\n$$\n\n" + _chain() + "\n$$ {:label: eq-b}\nb\n$$\n"
    # The unlabelled chain does not use up a number.
    assert _eqn_numbers(_build(src)) == ["1.1", "1.2"]


def test_calc_shares_the_display_math_counter():
    src = (
        "## Sec\n\n$$ {:label: eq-a}\na\n$$\n\n"
        + _chain("eq-c")
        + "\n$$ {:label: eq-b}\nb\n$$\n\nSee :ref:eq-a::, :ref:eq-c:: and :ref:eq-b::.\n"
    )
    html = _build(src)
    assert _eqn_numbers(html) == ["1.1", "1.2", "1.3"]
    assert '<a class="reference" href="#eq-c">(1.2)</a>' in html


def test_ref_to_calc_prints_its_number():
    html = _build(TOP_LEVEL + "\nBy :ref:eq-c::, done.\n")
    assert '<a class="reference" href="#eq-c">(1.1)</a>' in html


def test_labelled_calc_inside_a_proof_is_numbered():
    html = _build(IN_STEP_P + "\nBy :ref:eq-c::, done.\n")
    assert _eqn_numbers(html) == ["1.1"]
    assert '<a class="reference" href="#eq-c">(1.1)</a>' in html


def test_calc_menu_label_names_the_equation():
    html = _build(TOP_LEVEL)
    assert re.search(
        r'id="eq-c" class="calc[^"]*" data-menu-label="Equation \(1\.1\)"', html
    )


@pytest.mark.parametrize(
    "src", [TOP_LEVEL, IN_PROOF, IN_STEP_P], ids=["top", "proof", "step-p"]
)
def test_calc_rows_never_read_step(src):
    html = _build(src)
    assert "Step ⟨⟩" not in html
    assert "None⟩" not in html
    labels = re.findall(r'class="step hr[^"]*" data-menu-label="([^"]*)"', html)
    assert labels.count("Relation") == 2


def test_calc_relation_math_is_display_size():
    html = _build(TOP_LEVEL)
    assert r"\(\displaystyle \sum_{j=1}^k a_j = b\)" in html
    assert r"\(\displaystyle \le \frac{c}{4L}\)" in html
    # The justification is prose, so its math stays text-size.
    assert r"\(\frac{1}{2} \le 1\)" in html


def test_calc_relation_math_is_display_size_inside_a_proof():
    assert _build(IN_STEP_P).count(r"\(\displaystyle ") == 2


def test_calc_relation_math_is_display_size_without_handrails():
    assert ProcessorApp(plain=TOP_LEVEL).run().count(r"\(\displaystyle ") == 2


def test_top_level_calc_lays_out_on_the_text_column():
    # Outside a proof the chain is a top-level block, like a display equation:
    # its handrail zones take the gutter instead of hanging left of the text.
    html = _build(TOP_LEVEL)
    classes = re.search(r'id="eq-c" class="([^"]*)"', html).group(1).split()
    assert "calc" in classes and "hr" in classes
    assert "hr-offset" not in classes


def test_calc_in_a_proof_keeps_its_offset_placement():
    html = _build(IN_STEP_P)
    classes = re.search(r'id="eq-c" class="([^"]*)"', html).group(1).split()
    assert "hr-offset" in classes


def test_calc_outside_a_proof_has_no_tombstone():
    # The tombstone ends a proof. Outside a proof the chain is a display
    # equation, so it does not get one.
    assert 'class="halmos"' not in _build(TOP_LEVEL)


def test_calc_without_handrails_keeps_its_label_as_id():
    assert 'id="eq-c" class="calc"' in ProcessorApp(plain=TOP_LEVEL).run()


@pytest.mark.parametrize("src", [TOP_LEVEL, IN_STEP_P], ids=["top", "step-p"])
def test_calc_number_stacks_above_the_first_rows_mark(src):
    html = _build(src)
    # The first row's cell holds the number, then the mark, in one stack.
    stack = re.search(
        r'<div class="hr-info hr-info-stack">'
        r'<div class="eqn-number"><p>\(1\.1\)</p></div>'
        r'\s*<div class="hr-collapse-zone">',
        html,
    )
    assert stack, "the number is not stacked above the first row's mark"
    assert html.count("hr-info-stack") == 1
    assert html.count('class="eqn-number"') == 1


def test_unnumbered_calc_has_no_stack():
    assert "hr-info-stack" not in _build("## Sec\n\n" + _chain())


STEP_STARTS_WITH_EQN = """\
## Sec

:theorem: {:label: thm-s} A claim. ::

:proof: {:of: thm-s}

  :step: A step with text before its equation:

  $$ {:label: eq-after-text}
  a = b
  $$

  ::

  :step:

  $$ {:label: eq-first-line}
  c = d
  $$

  ::

  :step:

  $$ {:nonum:}
  e = f
  $$

  ::

::

See :ref:eq-first-line::.
"""


def test_step_number_stacks_above_its_leading_equation_number():
    html = _build(STEP_STARTS_WITH_EQN)
    stack = re.search(
        r'<div class="hr-info hr-info-stack">'
        r'<div class="step-number"><p>⟨2⟩</p></div>'
        r'<div class="eqn-number"><p>\(1\.2\)</p></div></div>',
        html,
    )
    assert stack, "step 2 and its equation number are not stacked in one cell"
    # The equation number is shown once, in the step's cell, not twice.
    assert html.count("<p>(1.2)</p>") == 1
    assert html.count("hr-info-stack") == 1
    assert '<a class="reference" href="#eq-first-line">(1.2)</a>' in html


def test_step_with_text_before_its_equation_is_not_stacked():
    html = _build(STEP_STARTS_WITH_EQN)
    # Step 1 starts with text, so its number and the equation's stay apart.
    assert '<div class="hr-info"><div class="step-number"><p>⟨1⟩</p></div></div>' in html
    assert '<div class="hr-info"><div class="eqn-number"><p>(1.1)</p></div></div>' in html


def test_step_with_unnumbered_leading_equation_is_not_stacked():
    html = _build(STEP_STARTS_WITH_EQN)
    assert '<div class="hr-info"><div class="step-number"><p>⟨3⟩</p></div></div>' in html
