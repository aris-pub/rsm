"""Tests for the proof step-tree derivation and the floating proof rail."""

import rsm
import rsm.nodes as nodes
from rsm import app

# A proof whose steps reference each other, inside a tree-view TOC document.
# Blank lines between inline steps confuse the parser, so the proof stays compact.
SRC = """\
:toc: {
  :view: tree
}
::

# S

:theorem: {:label: thm-x} A claim.::

:proof:
  :step: {:label: st-1} Foo.::
  :step: {:label: st-2} Bar by :ref:st-1::.::
  :step: :qed: Done by :ref:st-2::.::
::
"""


def _proof(src):
    a = app.ProcessorApp(plain=src)
    a.run()
    return next(iter(a.translator.tree.traverse(nodeclass=nodes.Proof)))


def test_proof_tree_nodes():
    p = _proof(SRC)
    assert [(n["num"], n["depth"]) for n in p.tree_nodes] == [
        ("1", 1),
        ("2", 1),
        ("3", 1),
    ]
    assert [n["label"] for n in p.tree_nodes] == ["st-1", "st-2", ""]


def test_proof_tree_edges():
    p = _proof(SRC)
    pairs = {(e["src"], e["dst"]): e for e in p.tree_edges}
    # step 2 (row 1) depends on step 1 (row 0); qed (row 2) on step 2 (row 1)
    assert pairs[(1, 0)]["kind"] == "dep"
    assert pairs[(2, 1)]["kind"] == "dep"
    assert len(p.tree_edges) == 2


def test_proof_tree_root_title():
    p = _proof(SRC)
    # The proof has a root node distinct from the generic step fallback.
    assert p.tree_root_title and p.tree_root_title != "Proof"


def test_external_refs_excluded():
    # A reference to a result outside the proof must not create a step edge.
    src = SRC.replace("Bar by :ref:st-1::", "Bar by :ref:thm-x:: and :ref:st-1::")
    p = _proof(src)
    # still only the two intra-proof step edges
    assert len(p.tree_edges) == 2


def test_rail_emitted_with_tree_toc():
    html = rsm.render(SRC, handrails=True)
    assert 'class="proof-rail"' in html
    # at least the proof's own step-tree is shown in the rail
    assert html.count('class="proof-rail-item"') >= 1
    proof = _proof(SRC)
    assert f'data-proof="{proof.nodeid}"' in html


def test_rail_absent_without_tree_toc():
    # No TOC view directive (the default list view): no floating rail.
    html = rsm.render(SRC.replace("  :view: tree\n", ""), handrails=True)
    assert "proof-rail" not in html


def test_rail_absent_without_toc():
    html = rsm.render("# S\n\n:proof:\n  :step: Foo.::\n::\n", handrails=True)
    assert "proof-rail" not in html


def test_proofless_tree_toc_has_no_rail():
    html = rsm.render(":toc: {\n  :view: tree\n}\n::\n\n# A\n\nx\n", handrails=True)
    # No proofs, so no rail at all.
    assert "proof-rail" not in html
