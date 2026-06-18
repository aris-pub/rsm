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
