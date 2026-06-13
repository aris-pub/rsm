"""Tests for the TOC tree view: edge derivation, build-time layout, markup."""

import logging

import rsm
import rsm.nodes as nodes
from rsm import app
from rsm.toc_layout import layout_tree

SRC = """:toc: ::

## One
  {:label: sec-one}

:theorem: {:label: thm-a} Something. ::

## Two
  {:label: sec-two}

See :ref:thm-a:: and :ref:thm-a:: again. Also :ref:sec-three::.

### Twosub
  {:label: sec-twosub}

Back to :ref:sec-one::. And to :ref:sec-two::.

## Three
  {:label: sec-three}

Done.
"""


def _toc(src):
    a = app.ProcessorApp(plain=src)
    a.run()
    return next(iter(a.translator.tree.traverse(nodeclass=nodes.Contents)))


def test_edge_derivation():
    toc = _toc(SRC)
    by_pair = {(e["src"], e["dst"]): e for e in toc.toc_edges}
    # Rows in document order: One=0, Two=1, Twosub=2, Three=3.
    assert by_pair[(1, 0)]["count"] == 2  # Two -> thm-a (in One), twice
    assert by_pair[(1, 0)]["kind"] == "dep"
    assert by_pair[(1, 3)]["kind"] == "fwd"  # Two -> Three (forward)
    assert by_pair[(2, 0)]["kind"] == "dep"  # Twosub -> One
    assert by_pair[(2, 1)]["kind"] == "dep"  # Twosub -> Two
    assert len(toc.toc_edges) == 4


def test_intra_section_refs_dropped():
    src = """:toc: ::

## Only
  {:label: s}

:theorem: {:label: t} X. ::

Same section: :ref:t::.
"""
    assert _toc(src).toc_edges == []


def test_tree_nodes_recorded():
    toc = _toc(SRC)
    nums = [(n["num"], n["depth"]) for n in toc.tree_nodes]
    assert nums == [("1", 1), ("2", 1), ("2.1", 2), ("3", 1)]


def test_toc_markup_default_list():
    html = rsm.render(SRC, handrails=False)
    assert 'svg class="toc-tree"' in html
    assert 'class="toc"' in html and "toc tree" not in html  # list is default
    assert 'ul class="contents"' in html  # list still present as fallback


def test_view_meta_sets_tree_default():
    src = ":toc: {\n  :view: tree\n}\n::\n\n## A\n\nx\n"
    html = rsm.render(src, handrails=False)
    assert 'class="toc tree"' in html


def test_svg_has_positioned_nodes_and_edges():
    html = rsm.render(SRC, handrails=False)
    # One anchor per TOC entry plus the synthetic root node holding the title.
    assert html.count('class="toc-node level-') == 5
    assert html.count("data-idx=") == 5
    assert 'class="toc-node level-0"' in html  # the root
    assert 'class="toc-edge ' in html
    assert "data-title=" in html  # title carried for hover


def test_root_node_carries_manuscript_title():
    html = rsm.render("# My Paper\n\n" + SRC, handrails=False)
    assert 'class="toc-node level-0"' in html
    assert "My Paper" in html
    # every top-level section is linked to the root by a structural edge
    assert 'class="toc-edge struct"' in html


def test_handrails_menu_wiring():
    html = rsm.render(SRC, handrails=True)
    assert 'data-menu-toc-view="true"' in html
    assert 'data-role="toc-view"' in html
    assert "View as tree" in html


def test_toc_view_attr_absent_on_other_blocks():
    html = rsm.render("## A\n\n:theorem: {:label: t} X. ::\n", handrails=True)
    assert "data-menu-toc-view" not in html


def test_toc_author_content_warned_and_dropped(caplog):
    src = ":toc: UNWANTED-CONTENT ::\n\n## A\n  {:label: s}\n\nx\n"
    with caplog.at_level(logging.WARNING, logger="RSM"):
        html = rsm.render(src, handrails=False)
    assert "UNWANTED-CONTENT" not in html
    assert any(
        "content" in r.getMessage().lower() and "toc" in r.getMessage().lower()
        for r in caplog.records
    )


# --- layout module -------------------------------------------------------


def _layout_inputs():
    nodes_ = [
        {"num": "1", "title": "Intro", "label": "a", "depth": 1},
        {"num": "2", "title": "Body", "label": "b", "depth": 1},
        {"num": "2.1", "title": "Sub", "label": "c", "depth": 2},
        {"num": "3", "title": "End", "label": "d", "depth": 1},
    ]
    edges = [
        {"src": 1, "dst": 0, "count": 1, "kind": "dep"},
        {"src": 2, "dst": 0, "count": 2, "kind": "dep"},
        {"src": 0, "dst": 3, "count": 1, "kind": "fwd"},
    ]
    return nodes_, edges


def test_layout_positions_all_nodes():
    nodes_, edges = _layout_inputs()
    out = layout_tree(nodes_, edges)
    assert out is not None
    assert len(out["nodes"]) == 4
    assert all("x" in n and "y" in n for n in out["nodes"])
    assert len(out["edges"]) == 3
    assert out["width"] > 0 and out["height"] > 0


def test_layout_is_deterministic():
    nodes_, edges = _layout_inputs()
    assert layout_tree(nodes_, edges) == layout_tree(nodes_, edges)


def test_layout_empty():
    assert layout_tree([], []) is None
