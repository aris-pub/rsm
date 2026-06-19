"""Characterization tests that pin the proof-model passes before they move.

These lock in current behavior of the transformer's proof passes (step
numbering at depth, hypothesis propagation into nested substeps, subproof
synthesis, the intra-proof dependency DAG, and the emitted ``rail-state-data``
contract) so the upcoming extraction into ``rsm/proof.py`` and the later
collapse into a single ``analyze_proofs`` call stay behavior-preserving.

They deliberately avoid the assume-paired-with-a-claim case, whose scope the
Rule 1 change is meant to alter; that case is exercised (and flipped) by
``test_proof_state.py`` instead, so this file stays green across that change.
"""

import json
import re

import rsm
import rsm.nodes as nodes
from rsm import app

# A bare :assume: step, then a step carrying its own claim plus two substeps,
# then a final qed step. Enough structure to exercise depth-2 numbering,
# forward + downward scope propagation, subproof synthesis, and one intra-proof
# reference. The tree-view :toc: makes the floating rail (and its state JSON)
# render.
SRC = """\
:toc: {
  :view: tree
}
::

# S

:theorem: {:label: thm-x} A claim.::

:proof:

  :step: {:label: st-1}

    :assume: $P$ ::.

  ::

  :step: {:label: st-2}

    :claim: Middle. ::

    :step: {:label: st-2a} Inner A. ::

    :step: {:label: st-2b} Inner B by :ref:st-2a::. ::

  ::

  :step: {:label: st-3}

    :qed:

    :p: Done. ::

  ::

::
"""


def _proof(src=SRC):
    a = app.ProcessorApp(plain=src)
    a.run()
    tree = a.translator.tree
    return tree, next(iter(tree.traverse(nodeclass=nodes.Proof)))


def _state_by_label(proof):
    return {
        s.label: st
        for s, st in zip(proof.traverse(nodeclass=nodes.Step), proof.step_state)
    }


def test_nested_step_numbering():
    _, p = _proof()
    assert [(n["num"], n["depth"], n["label"]) for n in p.tree_nodes] == [
        ("1", 1, "st-1"),
        ("2", 1, "st-2"),
        ("2.1", 2, "st-2a"),
        ("2.2", 2, "st-2b"),
        ("3", 1, "st-3"),
    ]
    assert [s.full_number for s in p.traverse(nodeclass=nodes.Step)] == [
        "1",
        "2",
        "2.1",
        "2.2",
        "3",
    ]


def test_bare_assumption_propagates_through_depth():
    # The bare :assume: in step 1 must reach every later sibling (2, 3) and the
    # substeps nested under them (2.1, 2.2). Stable under both scope rules,
    # since the assume shares no step with a claim.
    _, p = _proof()
    by_label = _state_by_label(p)
    assume = next(
        c for c in p.traverse(nodeclass=nodes.Construct) if c.kind == "assume"
    )
    for lbl in ("st-2", "st-2a", "st-2b", "st-3"):
        assert assume.nodeid in [h["id"] for h in by_label[lbl]["hyps"]], lbl


def test_goal_resolves_to_own_claim_then_parent_then_theorem():
    _, p = _proof()
    by_label = _state_by_label(p)
    # A step with its own claim shows it; a substep shows the parent's claim.
    assert by_label["st-2"]["goal"]["num"] == "2"
    assert by_label["st-2a"]["goal"]["num"] == "2"
    # A step with no claim of its own falls back to the theorem.
    assert by_label["st-1"]["goal"].get("thm")
    assert by_label["st-3"]["goal"].get("thm")


def test_nested_steps_synthesize_a_subproof():
    _, p = _proof()
    inner = next(s for s in p.traverse(nodeclass=nodes.Step) if s.label == "st-2a")
    sub = inner.parent
    assert isinstance(sub, nodes.Subproof)
    assert isinstance(sub.parent, nodes.Step) and sub.parent.label == "st-2"


def test_intra_proof_dependency_edge():
    _, p = _proof()
    # st-2b (:ref: st-2a) is the only intra-proof reference, so exactly one edge.
    assert [(e["src"], e["dst"], e["kind"]) for e in p.tree_edges] == [(3, 2, "dep")]


def test_rail_state_data_matches_model_and_resolves_in_dom():
    html = rsm.render(SRC, handrails=True)
    m = re.search(
        r'<script[^>]*class="rail-state-data"[^>]*>(.*?)</script>', html, re.S
    )
    assert m, "rail-state-data script not emitted"
    data = json.loads(m.group(1))
    # The emitted JSON is exactly the computed model...
    _, p = _proof()
    assert data == p.step_state
    # ...and every id it references resolves to a data-nodeid in the DOM, the
    # contract prooftree.js relies on (it does querySelector by that id).
    ids = {h["id"] for st in data for h in st["hyps"]}
    ids |= {st["goal"]["id"] for st in data if st["goal"]}
    for i in ids:
        assert f'data-nodeid="{i}"' in html, f"state id {i} has no DOM node"
