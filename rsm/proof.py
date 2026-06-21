"""Structured-proof analysis: the single home for the proof model.

RSM proofs are hierarchies of ``:step:`` nodes carrying ``:let:``/``:assume:``
hypotheses and ``:claim:`` goals. The transformer used to compute everything
about them inline; this module gathers that work so the model has one owner and
the views (the floating rail, the State pane, the proof-DAG SVG, an eventual
LSP) are pure consumers of what is computed here.

``analyze_proofs`` is the single entry the transformer calls; it runs these in
order:

- ``resolve_of``            resolve ``:proof: {:of: <label>}`` to the result it
                            proves (sets ``proof.proves``).
- ``add_necessary_subproofs``  wrap a step's sub-steps in a synthesized
                            ``Subproof`` so the hierarchy is well formed.
- ``_number_all_steps``     assign the per-proof ``1.1`` step numbering.
- ``make_trees``            derive each proof's step-dependency DAG
                            (``tree_nodes`` / ``tree_edges`` / ``tree_root_title``).
- ``make_state``            derive each step's ``hypotheses |- goal`` scope
                            (``step_state``) as node references.

These mutate nodes in place, matching the transformer's whole-tree contract.
The only external prerequisites are label collection and reference resolution
(both run earlier in the transformer). ``make_state`` records node references
rather than ids, so ``analyze_proofs`` runs before id assignment;
``serialize_state`` resolves those references to the id-keyed JSON the rail
emits, at translate time.
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

# Every construct introduces a symbol or assumption except these (assertions,
# goal restructurings, and the QED marker). Used to collect the document-wide
# context that prose and definitions contribute.
_NON_INTRO_KINDS = frozenset({"then", "suffices", "claim", "claimblock", "qed", "prove"})


def analyze_proofs(tree, labels_to_nodes) -> None:
    """Run the full proof model over the tree, in dependency order.

    This is the single entry point the transformer calls. Each pass mutates
    nodes in place. ``make_state`` records node *references* that
    ``serialize_state`` resolves to node ids at translate time, so the whole
    analysis can run before ids are assigned (which matters because
    ``add_necessary_subproofs`` creates nodes that still need ids).
    """
    resolve_of(tree, labels_to_nodes)
    add_necessary_subproofs(tree)
    _number_all_steps(tree)
    make_trees(tree)
    make_state(tree)


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


def _number_all_steps(tree) -> None:
    """Number the steps of every proof and subproof in the tree."""
    for node in tree.traverse():
        if isinstance(node, (nodes.Proof, nodes.Subproof)):
            number_steps(node)


def make_trees(tree) -> None:
    for proof in tree.traverse(nodeclass=nodes.Proof):
        _compute_tree(proof)


def _is_named_result(node) -> bool:
    """Whether a cited node counts as a proof dependency worth its own DAG node:
    the theorem family (theorem, lemma, proposition, corollary), but not
    definitions, remarks, or examples."""
    return isinstance(node, nodes.Theorem) and not isinstance(
        node, (nodes.Definition, nodes.Remark, nodes.Example)
    )


def _compute_tree(proof) -> None:
    """Per-proof step DAG for the floating proof-tree, mirroring the TOC.

    Nodes are the proof's steps in document order, plus one appended node per
    external named result (theorem/lemma/...) a step cites; edges are step->step
    references within the proof and step->result dependencies. Containment edges
    and the root are added by the renderer, as for the TOC. Definitions,
    equations, and cross-proof step references stay out.
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
            "type": "step",
        }
        for s in steps
    ]
    proof.tree_root_title = _proof_root_title(proof)

    n_steps = len(steps)
    # External named results (theorem/lemma/proposition/corollary) cited by a
    # step become their own nodes, deduped by target and appended after the
    # steps, so the DAG shows the proof's dependence on results proved
    # elsewhere. Definitions, remarks, examples, equations, and cross-proof step
    # references are not dependencies in this sense and stay out.
    result_row: dict[int, int] = {}
    counts: dict[tuple[int, int], int] = {}
    for ref in proof.traverse(nodeclass=nodes.Reference):
        src = nearest_step(ref)
        if src is None:
            continue
        target = ref.target
        if isinstance(target, nodes.Step) and id(target) in row_of:
            if src is target:
                continue
            dst = row_of[id(target)]
        elif _is_named_result(target):
            tid = id(target)
            if tid not in result_row:
                result_row[tid] = len(proof.tree_nodes)
                proof.tree_nodes.append(
                    {
                        "num": "",
                        "title": str(getattr(target, "reftext", "") or ""),
                        "label": target.label or "",
                        "depth": 1,
                        "type": "result",
                    }
                )
            dst = result_row[tid]
        else:
            continue
        key = (row_of[id(src)], dst)
        counts[key] = counts.get(key, 0) + 1

    proof.tree_edges = [
        {
            "src": s,
            "dst": d,
            "count": c,
            # result edges (to appended result nodes) read as dependencies;
            # intra-proof edges keep the backward/forward distinction.
            "kind": "dep" if d >= n_steps else ("dep" if d < s else "fwd"),
        }
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


def _is_prose_intro(node) -> bool:
    """A construct that introduces a symbol or assumption into document-wide
    context: one living in running prose or in a definition, but not inside a
    proof or a theorem-family statement (whose introductions are that result's
    local antecedents). Such an introduction is in scope to the end of the paper.
    """
    if not isinstance(node, nodes.Construct) or node.kind in _NON_INTRO_KINDS:
        return False
    anc = node.parent
    while anc is not None:
        if isinstance(anc, nodes.Definition):
            anc = anc.parent  # a definition is itself a document-wide intro
            continue
        if isinstance(anc, (nodes.Proof, nodes.Theorem, nodes.Statement)):
            return False
        anc = anc.parent
    return True


def make_state(tree) -> None:
    """Per-step ``hypotheses |- goal`` for the rail's State view, plus the
    document-wide ambient context each proof inherits.

    Records node *references* (not ids) so it can run before ids are assigned;
    ``serialize_state`` turns those refs into the id-keyed JSON the rail emits.
    """
    # Prose and definition introductions accumulate in document order and stay
    # in scope to the end of the paper, so each proof inherits every such
    # introduction that precedes it.
    ambient: list = []
    per_proof: dict = {}
    for node in tree.traverse():
        if isinstance(node, nodes.Proof):
            per_proof[id(node)] = list(ambient)
        elif _is_prose_intro(node):
            ambient.append(node)
    for proof in tree.traverse(nodeclass=nodes.Proof):
        _compute_state(proof, per_proof.get(id(proof), ()))


def serialize_state(proof):
    """Resolve a proof's ref-based ``step_state`` to the id-keyed form the rail
    emits as JSON. Runs at translate time, once node ids exist."""

    def entry(item):
        if item is None:
            return None
        out = {k: v for k, v in item.items() if k != "node"}
        out["id"] = item["node"].nodeid
        return out

    return [
        {
            "goal": entry(st["goal"]),
            "hyps": [entry(h) for h in st["hyps"]],
            "context": [entry(c) for c in st.get("context", [])],
        }
        for st in getattr(proof, "step_state", [])
    ]


def _compute_state(proof, ambient_intros=()) -> None:
    steps = list(proof.traverse(nodeclass=nodes.Step))
    if not steps:
        return
    # Document-wide context inherited by this proof (prose/definition intros in
    # scope here), the same for every step and shown as its own group.
    context = [{"node": c, "num": None} for c in ambient_intros]

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
        [{"node": c, "num": None} for c in own_constructs(theorem, HYP_KINDS)]
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
                # Rule 1: an introduction (:let:/:assume:) stays in scope for
                # every later sibling, whether or not the introducing step also
                # states a claim. Splitting a step never changes scope. A
                # hypothesis meant to be local to one sub-result belongs inside
                # that step's subproof (or as the antecedent of a conditional
                # goal), not as a sibling-level introduction.
                snum = str(sib.full_number)
                hyps += [
                    {"node": c, "num": snum}
                    for c in own_constructs(sib, HYP_KINDS)
                ]
            num = str(anc.full_number)
            hyps += [
                {"node": c, "num": num}
                for c in own_constructs(anc, HYP_KINDS)
            ]
        goal = None
        for anc in reversed(chain):  # innermost first
            claims = own_constructs(anc, GOAL_KINDS)
            if claims:
                goal = {"node": claims[0], "num": str(anc.full_number)}
                break
        # A setup step with no claim of its own is working toward the
        # theorem; show its conclusion as the goal.
        if goal is None and theorem is not None:
            goal = {"node": theorem, "num": theorem.reftext or None, "thm": True}
        state.append({"goal": goal, "hyps": hyps, "context": context})
    proof.step_state = state
