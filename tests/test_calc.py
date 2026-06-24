"""The :calc: construct: an equational/calculational proof -- a chain of relation
steps, each carrying a justification.

This file covers parsing + node mapping; rendering is exercised separately.
"""

from rsm import nodes, tsparser
from rsm.app import ProcessorApp

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


def test_calc_renders_as_a_chain_with_one_halmos():
    html = _render(CALC_SRC)
    assert 'class="calc"' in html
    # one step per relation; math emitted untouched for native typesetting;
    # one closing tombstone for the whole chain.
    assert html.count('class="step') == 2
    assert r"\(" in html
    assert html.count('class="halmos"') == 1


def test_calc_justifications_start_collapsed():
    # Each relation's justification is collapsed at rest (disclosed on demand);
    # subtractive marker, so JS-off renders the full written proof.
    html = _render(CALC_SRC, handrails=True)
    assert html.count('data-start-collapsed="true"') == 2
