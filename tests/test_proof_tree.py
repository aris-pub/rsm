"""Tests for the proof step-tree derivation and the reader sidebar markup."""

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


def test_external_result_refs_included():
    # A reference to a named result (theorem/lemma/...) outside the proof now
    # gets its own node in the DAG, with a dependency edge from the citing step.
    src = SRC.replace("Bar by :ref:st-1::", "Bar by :ref:thm-x:: and :ref:st-1::")
    p = _proof(src)
    results = [n for n in p.tree_nodes if n.get("type") == "result"]
    assert len(results) == 1
    assert results[0]["label"] == "thm-x"
    row = p.tree_nodes.index(results[0])
    to_result = [e for e in p.tree_edges if e["dst"] == row]
    assert len(to_result) == 1
    assert to_result[0]["src"] == 1 and to_result[0]["kind"] == "dep"
    # the two intra-proof step edges (whose targets are among the 3 steps) remain
    assert len([e for e in p.tree_edges if e["dst"] < 3]) == 2


def test_external_definition_refs_excluded():
    # Definitions are not dependencies for the DAG; citing one adds no node.
    src = SRC.replace(
        ":theorem: {:label: thm-x} A claim.::",
        ":definition: {:label: def-x} A def.::",
    ).replace("Bar by :ref:st-1::", "Bar by :ref:def-x:: and :ref:st-1::")
    p = _proof(src)
    assert not any(n.get("type") == "result" for n in p.tree_nodes)
    assert len(p.tree_edges) == 2


# A document with a title, a tree-view TOC over several sections, and a proof,
# so the floating sidebar has real content under both the Document scope (TOC
# tree) and the Proof scope (the proof's step-tree).
RAIL_SRC = """\
# Demo

:toc: {
  :view: tree
}
::

## One
  {:label: sec-one}

:theorem: {:label: thm-x} A claim.::

:proof:
  :step: {:label: st-1} Foo.::
  :step: {:label: st-2} Bar by :ref:st-1::.::
  :step: :qed: Done by :ref:st-2::.::
::

## Two
  {:label: sec-two}

See :ref:thm-x::.
"""

# The same document plus a :notation: block, so the Document scope grows a
# Notation sub-tab.
RAIL_SRC_NOTATION = RAIL_SRC.replace(
    "  {:label: sec-one}\n\n",
    "  {:label: sec-one}\n\n:notation:\n  \\eig $\\lambda$ eigenvalue\n::\n\n",
)


def _sidebar(src):
    return rsm.render(src, handrails=True, sidebar=True)


def _strip_views(html):
    import re

    strip = html[html.index('<nav class="rail-strip"'):html.index("</nav>", html.index('<nav class="rail-strip"'))]
    return re.findall(r'class="rail-strip-btn" data-view="([a-z]+)" data-mode="(split|grouped|both)"', strip)


def test_sidebar_is_a_build_option():
    # The sidebar comes from the build option, not from the TOC view.
    assert 'class="proof-rail' in _sidebar(RAIL_SRC)
    assert "proof-rail" not in rsm.render(RAIL_SRC, handrails=True)
    no_tree = RAIL_SRC.replace("  :view: tree\n", "")
    assert 'class="proof-rail' in _sidebar(no_tree)


def test_sidebar_without_toc_still_has_contents():
    # The section graph is computed even when the author wrote no :toc:.
    src = RAIL_SRC.replace(":toc: {\n  :view: tree\n}\n::\n\n", "")
    assert ":toc:" not in src
    html = _sidebar(src)
    assert 'class="rail-panel rail-doc-map"' in html
    assert ("contents", "split") in _strip_views(html)


def test_strip_has_one_icon_per_view():
    html = _sidebar(RAIL_SRC_NOTATION)
    assert _strip_views(html) == [
        ("contents", "split"), ("notation", "split"), ("document", "grouped"),
        ("steps", "split"), ("state", "split"), ("proof", "grouped"),
        ("pinned", "both"), ("reading", "both"),
    ]
    # Copy link, and no old header, scope tabs or collapse control.
    assert 'class="rail-strip-btn rail-strip-action rail-share-view"' in html
    for old in ('class="rail-header', 'class="rail-scope', 'class="rail-collapse"'):
        assert old not in html


def test_strip_buttons_are_named_with_hints():
    html = _sidebar(RAIL_SRC_NOTATION)
    assert 'aria-label="Contents" data-tip="Contents" data-hint="The contents of the manuscript as a dependency graph."' in html
    assert "Rename one and it changes everywhere." in html


def test_no_notation_without_notation():
    html = _sidebar(RAIL_SRC)
    assert 'data-view="notation"' not in html
    assert "rail-notation" not in html


def test_no_proof_views_without_structured_proofs():
    # A proof with no steps has no step graph, so no Steps / State / Proof.
    src = "# S\n\n## A\n\n:theorem: {:label: t} X.::\n\n:proof:\n  Plain prose proof.\n::\n"
    views = [v for v, _ in _strip_views(_sidebar(src))]
    assert "steps" not in views and "state" not in views and "proof" not in views
    assert "contents" in views and "pinned" in views and "reading" in views


def test_proof_items_live_under_proof_scope():
    html = _sidebar(RAIL_SRC)
    assert html.count('class="proof-rail-item"') >= 1
    proof = _proof(RAIL_SRC)
    assert f'data-proof="{proof.nodeid}"' in html
    assert 'data-proof="toc"' not in html


def test_phone_tabs_only_for_two_views():
    # Document has two views only with notation; Proof always has Steps/State.
    assert "rail-subtabs-document" not in _sidebar(RAIL_SRC)
    html = _sidebar(RAIL_SRC_NOTATION)
    assert 'class="rail-subtabs rail-subtabs-document" role="tablist"' in html
    assert 'class="rail-subtabs rail-subtabs-proof" role="tablist"' in html


def test_reading_tiles_and_system_theme():
    html = _sidebar(RAIL_SRC)
    assert 'data-value="system" aria-pressed="true" aria-label="System"' in html
    assert 'class="reading-ag" data-face="serif"' in html
    assert 'class="reading-a" data-size="4"' in html


def test_handrail_menu_has_pin_item():
    assert 'data-role="pin"' in _sidebar(RAIL_SRC)


def test_interface_says_manuscript_not_paper():
    import re

    html = _sidebar(RAIL_SRC_NOTATION)
    rail = html[html.index('<nav class="rail-strip"'):]
    rail = rail[: rail.index('<div class="hr-menu')]
    assert not re.search(r"\bpaper\b", rail, re.I)


def test_cli_build_sidebar_flag(tmp_path):
    import subprocess, sys

    src = tmp_path / "doc.rsm"
    src.write_text(RAIL_SRC)
    out = tmp_path / "out.html"
    run = "import sys; from rsm.cli import main; sys.argv[0] = 'rsm'; sys.exit(main())"
    cmd = [sys.executable, "-c", run, "build", str(src), "--standalone", "-o", str(out)]
    subprocess.run(cmd + ["--sidebar"], check=True, capture_output=True)
    assert 'class="proof-rail' in out.read_text()
    subprocess.run(cmd, check=True, capture_output=True)
    assert 'class="proof-rail' not in out.read_text()


def test_prose_introduction_enters_proof_context():
    # A :write:/:let:/:assume: in running prose is in scope from that point to
    # the end of the document, so a later proof inherits it as ambient context
    # (a separate group from the proof's own hypotheses).
    src = (
        "# S\n\n"
        "We :write: $A$ for the adjacency matrix ::.\n\n"
        ":theorem: {:label: thm-y} A claim about $A$.::\n\n"
        ":proof:\n"
        "  :step: {:label: st-1} Foo.::\n"
        "::\n"
    )
    p = _proof(src)
    ctx = p.step_state[0].get("context", [])
    assert [c["node"].kind for c in ctx] == ["write"]


def test_theorem_hypothesis_not_in_context():
    # A :let: inside a theorem statement is that theorem's local antecedent
    # (a hypothesis), not document-wide ambient context.
    src = (
        "# S\n\n"
        ":theorem: {:label: thm-z} :let: $G$ be a graph ::. A claim.::\n\n"
        ":proof:\n"
        "  :step: {:label: st-1} Foo.::\n"
        "::\n"
    )
    p = _proof(src)
    assert p.step_state[0].get("context", []) == []
    assert [h["node"].kind for h in p.step_state[0]["hyps"]] == ["let"]


def test_definition_introduction_in_context():
    # A :write: inside a :definition: is document-wide, so it does enter context.
    src = (
        "# S\n\n"
        ":definition: {:label: def-x} :write: $T$ for the thing ::.::\n\n"
        ":theorem: {:label: thm-w} A claim about $T$.::\n\n"
        ":proof:\n"
        "  :step: {:label: st-1} Foo.::\n"
        "::\n"
    )
    p = _proof(src)
    ctx = p.step_state[0].get("context", [])
    assert [c["node"].kind for c in ctx] == ["write"]


def test_theorem_premise_serializes_with_section_marker():
    # A :let: in the theorem statement is a hypothesis with no step number; it is
    # introduced with the theorem, so its serialized marker is the section (like
    # the goal), while a step's own :let: keeps a step marker.
    from rsm.proof import serialize_state

    src = (
        "# Title\n\n"
        "## S\n\n"
        ":theorem: {:label: thm-z} :let: $G$ be a graph ::. A claim.::\n\n"
        ":proof:\n"
        "  :step: {:label: st-1} :let: $x$ be a vertex ::. Foo.::\n"
        "::\n"
    )
    p = _proof(src)
    hyps = serialize_state(p)[0]["hyps"]
    markers = {h["marker"] for h in hyps}
    assert "section" in markers and "step" in markers
    premise = next(h for h in hyps if h["marker"] == "section")
    assert premise["num"] == "1"  # the theorem's section, not None


def test_section_marker_uses_subsection_precision():
    # A symbol introduced inside a subsection is marked with the full subsection
    # number (X.Y), matching how nested steps show ⟨X.Y⟩, not just the enclosing
    # top-level section.
    from rsm.proof import serialize_state

    src = (
        "# Title\n\n"
        "## S\n\n"
        "### Sub\n\n"
        "We :write: $A$ for the matrix ::.\n\n"
        ":theorem: {:label: thm-q} A claim about $A$.::\n\n"
        ":proof:\n"
        "  :step: {:label: st-1} Foo.::\n"
        "::\n"
    )
    p = _proof(src)
    ctx = serialize_state(p)[0]["context"]
    assert ctx and ctx[0]["num"] == "1.1"


def test_proof_dag_step_labels_are_bracketed():
    # Proof DAG step nodes render ⟨X⟩ to match the State panel markers; the
    # document section tree keeps the plain "X." format (bracket_nums default).
    html = _sidebar(SRC)
    assert ">⟨1⟩<" in html  # ⟨1⟩ appears as a proof-DAG node label
    # nothing before the proof rail-map (the document tree) is bracketed
    assert "⟨" not in html.split('class="rail-panel rail-map"')[0]


def test_pick_introduces_a_hypothesis():
    # :pick: brings a symbol into scope, so a later sibling step sees it among
    # its hypotheses (like :let:), not just :let:/:assume:.
    src = (
        "# Title\n\n## S\n\n"
        ":theorem: {:label: thm-p} A claim.::\n\n"
        ":proof:\n"
        "  :step: {:label: st-a} :pick: $x$ ::. Foo.::\n"
        "  :step: {:label: st-b} Bar by :ref:st-a::.::\n"
        "::\n"
    )
    p = _proof(src)
    # the later step's hypotheses include the pick'd symbol from the first step
    assert any(h["node"].kind == "pick" for h in p.step_state[1]["hyps"])
