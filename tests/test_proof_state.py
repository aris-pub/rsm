"""Tests for the per-step proof state (the floating sidebar's ASSUMING / TO SHOW).

Scope rule (Rule 1): an introduction (``:let:``/``:assume:``) stays in scope for
every later sibling step and any substeps therein, whether or not the
introducing step also states a claim. Splitting one step into two never changes
scope. A hypothesis meant to be local to a single sub-result belongs inside that
step's subproof, not as a sibling-level introduction.
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


# A step that introduces an assumption AND states its own claim. Under Rule 1
# the assumption still propagates to a later sibling (splitting is invariant);
# locality would require putting the assume inside the step's own subproof.
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


def test_assumption_in_a_claim_step_still_propagates_to_siblings():
    p = _proof(SRC_LOCAL)
    steps = list(p.traverse(nodeclass=nodes.Step))
    assume = next(
        c for c in p.traverse(nodeclass=nodes.Construct) if c.kind == "assume"
    )
    hyps = {s.label: [h["id"] for h in st["hyps"]] for s, st in zip(steps, p.step_state)}
    # In scope inside case one's own subproof...
    assert assume.nodeid in hyps["st-c1sub"]
    # ...and, under Rule 1, also in the later sibling case two (the claim in
    # case one does not confine the assumption to that step).
    assert assume.nodeid in hyps["st-case2"]
