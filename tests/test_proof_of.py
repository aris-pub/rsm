"""Tests for the :proof: {:of: <label>} metakey.

A proof detached from its theorem (e.g. several proofs of one result, each under
its own section) declares the result it establishes with :of:. That wires the
proof to the theorem in the rendered lead ("Proof of Theorem 1.1", linked like a
:ref:), the proof-tree rail root, and the State pane's TO SHOW / hypotheses.
"""

import rsm
import rsm.nodes as nodes
from rsm import app

SRC = """\
# Doc

## One
  {:label: sec-one}

:theorem: {:label: thm-x}

  :let: $G$ be a graph ::. Then $G$ is nice.

::

## Two
  {:label: sec-two}

:proof: {:of: thm-x}

  :step:

    :qed:

    :p: Obvious. ::

  ::

::
"""


def _run(src):
    a = app.ProcessorApp(plain=src)
    a.run()
    return a.translator.tree


def _proof(tree):
    return next(iter(tree.traverse(nodeclass=nodes.Proof)))


def test_of_metakey_parses():
    proof = _proof(_run(SRC))
    assert proof.of == "thm-x"


def test_of_resolves_to_the_theorem_node():
    tree = _run(SRC)
    proof = _proof(tree)
    thm = next(iter(tree.traverse(nodeclass=nodes.Theorem)))
    assert proof.proves is thm


def test_of_sets_proof_tree_root_to_the_theorem():
    tree = _run(SRC)
    proof = _proof(tree)
    thm = next(iter(tree.traverse(nodeclass=nodes.Theorem)))
    assert proof.tree_root_title == thm.reftext


def test_of_seeds_state_with_theorem_hyps_and_goal():
    tree = _run(SRC)
    proof = _proof(tree)
    thm = next(iter(tree.traverse(nodeclass=nodes.Theorem)))
    let_c = next(
        c for c in thm.traverse(nodeclass=nodes.Construct) if c.kind == "let"
    )
    first = proof.step_state[0]
    assert any(h["id"] == let_c.nodeid for h in first["hyps"]), "theorem :let: not seeded"
    assert first["goal"]["id"] == thm.nodeid


def test_of_renders_linked_lead():
    html = rsm.render(SRC, handrails=True)
    assert "Proof of " in html
    assert 'href="#thm-x"' in html
    assert ">Theorem 1.1</a>" in html


def test_unknown_of_label_is_an_error():
    import pytest
    bad = SRC.replace(":of: thm-x", ":of: thm-nope")
    with pytest.raises(Exception):
        rsm.render(bad, handrails=True)
