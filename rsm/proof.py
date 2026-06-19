"""Structured-proof analysis: the single home for the proof model.

RSM proofs are hierarchies of ``:step:`` nodes carrying ``:let:``/``:assume:``
hypotheses and ``:claim:`` goals. The transformer used to compute everything
about them inline; this module gathers that work so the model has one owner and
the views (the floating rail, the State pane, the proof-DAG SVG, an eventual
LSP) are pure consumers of what is computed here.

The passes, in the order the transformer runs them:

- ``resolve_of``            resolve ``:proof: {:of: <label>}`` to the result it
                            proves (sets ``proof.proves``).
- ``add_necessary_subproofs``  wrap a step's sub-steps in a synthesized
                            ``Subproof`` so the hierarchy is well formed.
- ``number_steps``          assign the per-proof ``1.1`` step numbering.
- ``make_trees``            derive each proof's step-dependency DAG
                            (``tree_nodes`` / ``tree_edges`` / ``tree_root_title``).
- ``make_state``            derive each step's ``hypotheses |- goal`` scope
                            (``step_state``), the data the State pane renders.

These mutate nodes in place, matching the transformer's whole-tree contract.
They depend on shared passes that still live in the transformer (label
collection before ``resolve_of``; numbering before ``make_trees``; node-id
assignment before ``make_state``), so the transformer keeps the call-sites and
their ordering for now.
"""

import logging

from . import nodes

logger = logging.getLogger("RSM").getChild("proof")


class ProofError(Exception):
    pass


# Construct kinds that introduce a hypothesis vs state a goal. Used by the scope
# computation in make_state.
HYP_KINDS = ("let", "assume")
GOAL_KINDS = ("claim", "claimblock")


def resolve_of(tree, labels_to_nodes) -> None:
    """Resolve each :proof: {:of: <label>} to the result it establishes.

    A proof detached from its theorem names the result with :of:; the resolved
    node is later used as the proof tree's root and the State pane's
    goal/hypotheses, and is rendered as a link in the proof's lead.
    """
    provable = (
        nodes.Theorem, nodes.Lemma, nodes.Corollary,
        nodes.Proposition, nodes.Statement,
    )
    for proof in tree.traverse(nodeclass=nodes.Proof):
        label = getattr(proof, "of", None)
        if not label:
            continue
        target = labels_to_nodes.get(label)
        if target is None:
            raise ProofError(
                f':proof: {{:of: {label}}} references an unknown label "{label}"'
            )
        if not isinstance(target, provable):
            raise ProofError(
                f":proof: {{:of: {label}}} must name a theorem-like block, not "
                f"{type(target).__name__}"
            )
        proof.proves = target


def add_necessary_subproofs(tree) -> None:
    for step in tree.traverse(nodeclass=nodes.Step):
        if not step.children:
            continue

        _, split_at_idx = step.first_of_type(
            (nodes.Step, nodes.Subproof), return_idx=True
        )
        if split_at_idx is None:
            split_at_idx = len(step.children)

        children = step.children[::]
        step.clear()

        statement = nodes.Statement()
        statement.append(children[:split_at_idx])
        statement.handrail_depth += 1

        if split_at_idx == len(children):
            step.append(statement)
            continue

        if isinstance(children[split_at_idx], nodes.Step):
            subproof = nodes.Subproof()
            subproof.append(children[split_at_idx:])
        elif isinstance(children[split_at_idx], nodes.Subproof):
            assert split_at_idx == len(children) - 1
            subproof = children[split_at_idx]
        else:
            raise ProofError("How did we get here?")
        step.append([statement, subproof])


def number_steps(proof) -> None:
    """Assign per-proof step numbers (the ``1.1`` scheme). Accepts a Proof or a
    Subproof, numbering its direct Step children."""
    step_gen = (s for s in proof.children if isinstance(s, nodes.Step))
    for idx, step in enumerate(step_gen, start=1):
        step.number = idx


def make_trees(tree) -> None:
    for proof in tree.traverse(nodeclass=nodes.Proof):
        _compute_tree(proof)


def _compute_tree(proof) -> None:
    """Per-proof step DAG for the floating proof-tree, mirroring the TOC.

    Nodes are the proof's steps in document order; edges are references from one
    step to another step OF THE SAME PROOF (containment edges and the root are
    added by the renderer, as for the TOC). Cross-proof and external references
    are dropped: the tree is scoped to one proof.
    """
    steps = list(proof.traverse(nodeclass=nodes.Step))
    if not steps:
        return
    row_of = {id(s): i for i, s in enumerate(steps)}

    def step_depth(step: nodes.Step) -> int:
        d = 1
        anc = step.parent
        while anc is not None and anc is not proof:
            if isinstance(anc, nodes.Step):
                d += 1
            anc = anc.parent
        return d

    def nearest_step(node: nodes.Node) -> nodes.Step | None:
        anc = node.parent
        while anc is not None and anc is not proof:
            if isinstance(anc, nodes.Step):
                return anc
            anc = anc.parent
        return None

    proof.tree_nodes = [
        {
            "num": str(s.full_number),
            "title": _step_title(s),
            "label": s.label or "",
            "depth": step_depth(s),
        }
        for s in steps
    ]
    proof.tree_root_title = _proof_root_title(proof)

    counts: dict[tuple[int, int], int] = {}
    for ref in proof.traverse(nodeclass=nodes.Reference):
        target = ref.target
        if not isinstance(target, nodes.Step) or id(target) not in row_of:
            continue
        src = nearest_step(ref)
        if src is None or src is target:
            continue
        key = (row_of[id(src)], row_of[id(target)])
        counts[key] = counts.get(key, 0) + 1

    proof.tree_edges = [
        {"src": s, "dst": d, "count": c, "kind": "dep" if d < s else "fwd"}
        for (s, d), c in sorted(counts.items())
    ]


def _step_title(step: nodes.Step) -> str:
    """Short text of a step's own claim, excluding nested sub-steps."""
    parts: list[str] = []

    def walk(node: nodes.Node) -> None:
        for child in node.children:
            if isinstance(child, nodes.Step):
                continue
            if isinstance(child, nodes.Text):
                parts.append(child.text)
            elif isinstance(child, nodes.NodeWithChildren):
                walk(child)

    walk(step)
    text = " ".join(" ".join(parts).split())
    return text[:90]


def _proof_root_title(proof) -> str:
    """The result a proof establishes, used as its tree's root label."""
    declared = getattr(proof, "proves", None)
    if declared is not None:
        return declared.reftext or "Statement"
    sib = proof.prev_sibling()
    theorem_types = (
        nodes.Theorem,
        nodes.Lemma,
        nodes.Corollary,
        nodes.Proposition,
        nodes.Definition,
        nodes.Remark,
        nodes.Statement,
    )
    while sib is not None:
        if isinstance(sib, theorem_types):
            return sib.reftext or "Statement"
        sib = sib.prev_sibling()
    # No theorem precedes this proof (e.g. several proofs of one result, each
    # under its own subsection): fall back to the enclosing heading's title.
    anc = proof.parent
    while anc is not None and not isinstance(anc, nodes.Section):
        anc = anc.parent
    if anc is not None and getattr(anc, "title", ""):
        return anc.title
    return "Statement"


def make_state(tree) -> None:
    """Per-step ``hypotheses |- goal`` for the rail's State view (runs after node
    ids are assigned, since it records construct node ids to clone)."""
    for proof in tree.traverse(nodeclass=nodes.Proof):
        _compute_state(proof)


def _compute_state(proof) -> None:
    steps = list(proof.traverse(nodeclass=nodes.Step))
    if not steps:
        return

    def nearest_step(node: nodes.Node) -> nodes.Step | None:
        anc = node.parent
        while anc is not None and anc is not proof:
            if isinstance(anc, nodes.Step):
                return anc
            anc = anc.parent
        return None

    def own_constructs(container: nodes.Node, kinds: tuple) -> list:
        # constructs of the given kinds belonging directly to `container`
        # (not to a nested step); for the theorem container, all of them.
        out = []
        is_step = isinstance(container, nodes.Step)
        for c in container.traverse(nodeclass=nodes.Construct):
            if c.kind not in kinds:
                continue
            if not is_step or nearest_step(c) is container:
                out.append(c)
        return out

    def ancestors(step: nodes.Step) -> list:  # outermost first
        chain = [step]
        anc = step.parent
        while anc is not None and anc is not proof:
            if isinstance(anc, nodes.Step):
                chain.append(anc)
            anc = anc.parent
        chain.reverse()
        return chain

    def preceding_step_siblings(step: nodes.Step) -> list:  # document order
        # A let/assume introduced by a step stays in scope for every later
        # step at the same level (Lamport), so a later step's hypotheses
        # include those of all its preceding step siblings.
        out = []
        sib = step.prev_sibling(nodes.Step)
        while sib is not None:
            out.append(sib)
            sib = sib.prev_sibling(nodes.Step)
        out.reverse()
        return out

    thm_types = (
        nodes.Theorem, nodes.Lemma, nodes.Corollary,
        nodes.Proposition, nodes.Statement,
    )
    # A :of:-declared result takes precedence over the preceding sibling.
    theorem = getattr(proof, "proves", None) or proof.prev_sibling()
    while theorem is not None and not isinstance(theorem, thm_types):
        theorem = theorem.prev_sibling()
    # Theorem hypotheses have no step number (they precede the proof).
    base_hyps = (
        [{"id": c.nodeid, "num": None} for c in own_constructs(theorem, HYP_KINDS)]
        if theorem is not None else []
    )

    state = []
    for s in steps:
        chain = ancestors(s)
        hyps = list(base_hyps)
        for anc in chain:
            # Preceding siblings at this level are in scope, then the
            # ancestor's own let/assume.
            for sib in preceding_step_siblings(anc):
                # A sibling that states its own claim is an ASSUME...PROVE:
                # its assumptions are discharged by that claim and do not
                # propagate to later siblings (only within its own subproof).
                if own_constructs(sib, GOAL_KINDS):
                    continue
                snum = str(sib.full_number)
                hyps += [
                    {"id": c.nodeid, "num": snum}
                    for c in own_constructs(sib, HYP_KINDS)
                ]
            num = str(anc.full_number)
            hyps += [
                {"id": c.nodeid, "num": num}
                for c in own_constructs(anc, HYP_KINDS)
            ]
        goal = None
        for anc in reversed(chain):  # innermost first
            claims = own_constructs(anc, GOAL_KINDS)
            if claims:
                goal = {"id": claims[0].nodeid, "num": str(anc.full_number)}
                break
        # A setup step with no claim of its own is working toward the
        # theorem; show its conclusion as the goal.
        if goal is None and theorem is not None:
            goal = {"id": theorem.nodeid, "num": theorem.reftext or None, "thm": True}
        state.append({"goal": goal, "hyps": hyps})
    proof.step_state = state
