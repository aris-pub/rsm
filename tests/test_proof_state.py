"""Tests for the per-step proof state (the floating sidebar's ASSUMING / TO SHOW).

An assumption introduced by a bare ``:assume:`` step stays in scope, per
Lamport's paradigm, for every later sibling step and any substeps therein, not
only for the step that introduces it.
"""

import rsm
import rsm.nodes as nodes
from rsm import app

# A bare assume step followed by later sibling steps.
SRC = """\
# S

:lemma: {:label: lem-x}

  The claim.

::

:proof:

  :step: {:label: st-assume}

    :assume: $P$ ::.

  ::

  :step: {:label: st-next}

    :claim: $Q$ ::.

    :p: Because. ::

  ::

  :step:

    :qed:

    :p: Done. ::

  ::

::
"""


def _proof(src):
    a = app.ProcessorApp(plain=src)
    a.run()
    return next(iter(a.translator.tree.traverse(nodeclass=nodes.Proof)))


def test_assumption_scopes_to_later_siblings_and_substeps():
    p = _proof(SRC)
    steps = list(p.traverse(nodeclass=nodes.Step))
    assume = next(
        c for c in p.traverse(nodeclass=nodes.Construct) if c.kind == "assume"
    )
    # Every step at or after the assume (siblings st-next and the final qed)
    # must carry the assumption in its hyps.
    for s, st in zip(steps, p.step_state):
        assert assume.nodeid in [h["id"] for h in st["hyps"]], (
            f"step {s.full_number} is missing the assumption introduced by an "
            "earlier sibling"
        )


# A step whose statement is ASSUME...PROVE (assume paired with its own claim):
# the assumption is local to proving that step, so it must not leak to a sibling.
SRC_LOCAL = """\
# S

:lemma: {:label: lem-y}

  The claim.

::

:proof:

  :step: {:label: st-case1}

    :assume: $P$ ::. :claim: case one. ::

    :p:

      :step: {:label: st-c1sub} It uses $P$. ::

    ::

  ::

  :step: {:label: st-case2}

    :claim: case two. ::

    :p: Trivial. ::

  ::

::
"""


def test_assume_prove_assumption_is_local_to_its_step():
    p = _proof(SRC_LOCAL)
    steps = list(p.traverse(nodeclass=nodes.Step))
    assume = next(
        c for c in p.traverse(nodeclass=nodes.Construct) if c.kind == "assume"
    )
    hyps = {s.label: [h["id"] for h in st["hyps"]] for s, st in zip(steps, p.step_state)}
    # In scope inside case one's own subproof...
    assert assume.nodeid in hyps["st-c1sub"]
    # ...but discharged by case one's claim, so absent from the sibling case two.
    assert assume.nodeid not in hyps["st-case2"]
