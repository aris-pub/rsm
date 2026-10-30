"""Tests for the TOC tree view: edge derivation, build-time layout, markup."""

import json
import logging
import re

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


def test_nonum_section_excluded_from_toc():
    src = """:toc: ::

## One
  {:label: sec-one}

x

## Colophon
  {:label: sec-colophon :nonum:}

Back-matter, out of the TOC.
"""
    titles = [n["title"] for n in _toc(src).tree_nodes]
    assert titles == ["One"]
    assert "Colophon" not in titles


def test_ref_into_nonum_section_drops_edge():
    # A reference whose target is an out-of-TOC (nonum) section contributes no
    # edge and must not raise from the missing row.
    src = """:toc: ::

## One
  {:label: sec-one}

See :ref:sec-colophon::.

## Colophon
  {:label: sec-colophon :nonum:}

Out of the TOC.
"""
    assert _toc(src).toc_edges == []


def test_toc_markup_default_list():
    html = rsm.render(SRC, handrails=False)
    assert 'svg class="toc-tree"' in html
    assert 'class="toc"' in html and "toc tree" not in html  # list is default
    # id-agnostic: every block now carries a synthetic id, so the <ul> renders
    # as <ul id="n.." class="contents">.
    assert 'class="contents"' in html  # list still present as fallback


def test_toc_is_navigation_landmark():
    # The TOC container is a <nav> with an accessible name, not a bare div, so it
    # is exposed as a navigation landmark (WCAG 1.3.1) that screen readers can
    # jump to. The rail is a separate (complementary) landmark, hence the name.
    html = rsm.render(SRC, handrails=False)
    assert '<nav class="toc"' in html
    assert 'aria-label="Table of contents"' in html
    assert '<div class="toc">' not in html


def test_view_meta_sets_tree_default():
    src = ":toc: {\n  :view: tree\n}\n::\n\n## A\n\nx\n"
    html = rsm.render(src, handrails=False)
    assert 'class="toc tree"' in html
    assert '<nav class="toc tree"' in html  # nav landmark holds in tree view too


def test_svg_has_positioned_nodes_and_edges():
    html = rsm.render(SRC, handrails=False)
    # One anchor per TOC entry plus the synthetic root node holding the title.
    assert html.count('class="toc-node level-') == 5
    assert html.count("data-idx=") == 5
    assert 'class="toc-node level-0"' in html  # the root
    assert 'class="toc-edge ' in html
    assert "data-tooltip=" in html  # title carried for hover
    # Each section link's accessible name is its full "num. title", not just the
    # visible secnum, so screen readers can tell the links apart (a11y).
    assert 'aria-label="1. One"' in html


def test_root_node_carries_manuscript_title():
    html = rsm.render("# My Paper\n\n" + SRC, handrails=False)
    assert 'class="toc-node level-0"' in html
    assert "My Paper" in html
    # every top-level section is linked to the root by a structural edge
    assert 'class="toc-edge struct"' in html


def test_root_node_is_muted_dot():
    # The TOC graph root stands in for the title/abstract but must be quiet: a
    # small dot, not a filled accent box. It carries no visible label and no box,
    # yet stays a link to the top of the manuscript whose accessible name is the
    # manuscript title.
    html = rsm.render("# My Paper\n\n" + SRC, handrails=False)
    svg = re.search(r'<svg class="toc-tree".*?</svg>', html, re.S).group(0)
    root = re.search(
        r'<a [^>]*class="toc-node level-0"[^>]*>.*?</a>', svg, re.S
    ).group(0)
    assert "<circle" in root  # drawn as a dot
    assert "<rect" not in root  # no box
    assert "<text" not in root  # no label text
    assert 'href="#"' in root  # links to the top of the manuscript
    assert 'aria-label="My Paper"' in root  # title is the accessible name
    assert 'data-tooltip="My Paper"' in root


def _root_node(html):
    """Return (tooltip, aria_label) for the TOC tree's root dot."""
    svg = re.search(r'<svg class="toc-tree".*?</svg>', html, re.S).group(0)
    a = re.search(r'<a [^>]*class="toc-node level-0"[^>]*>.*?</a>', svg, re.S).group(0)
    tooltip = re.search(r'data-tooltip="([^"]*)"', a).group(1)
    aria = re.search(r'aria-label="([^"]*)"', a).group(1)
    return tooltip, aria


def _svg_width(html):
    return float(re.search(r'<svg class="toc-tree" width="([\d.]+)"', html).group(1))


LONG_TITLE = "A Very Long Manuscript Title That Overruns the Narrow Tree Drawing Area"
TREE = "\n\n:toc: {\n  :view: tree\n}\n::\n\n## One\n  {:label: s1}\n\nx\n\n## Two\n  {:label: s2}\n\ny\n"


def test_root_title_does_not_widen_the_drawing():
    # The root is a small dot, not a title box, so even a very long manuscript
    # title no longer sizes the drawing (rsm-kay, superseding the rsm-tj7 "Top"
    # collapse). A long and a short title give the same narrow graph.
    long_html = rsm.render(f"# {LONG_TITLE}" + TREE, handrails=False)
    short_html = rsm.render("# My Paper" + TREE, handrails=False)
    assert _svg_width(long_html) == _svg_width(short_html)
    assert _svg_width(long_html) < 200


def test_root_dot_keeps_full_title_as_name_whatever_its_length():
    # No visible label, but the full title stays the dot's tooltip and accessible
    # name however long it is: there is no "Top" collapse any more.
    tooltip, aria = _root_node(rsm.render(f"# {LONG_TITLE}" + TREE, handrails=False))
    assert tooltip == LONG_TITLE
    assert aria == LONG_TITLE
    tooltip, aria = _root_node(rsm.render("# My Paper" + TREE, handrails=False))
    assert tooltip == "My Paper"
    assert aria == "My Paper"


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


# The section graph of a real paper (lipschitz-embedding): eleven nodes, long
# arrows that skip depth columns, laid out horizontally.
_PAPER_NODES = [{"num": "1", "title": "S0", "label": "s0", "depth": 1}, {"num": "2", "title": "S1", "label": "s1", "depth": 1}, {"num": "3", "title": "S2", "label": "s2", "depth": 1}, {"num": "4", "title": "S3", "label": "s3", "depth": 1}, {"num": "5", "title": "S4", "label": "s4", "depth": 1}, {"num": "6", "title": "S5", "label": "s5", "depth": 1}, {"num": "7", "title": "S6", "label": "s6", "depth": 1}, {"num": "8", "title": "S7", "label": "s7", "depth": 1}, {"num": "9", "title": "S8", "label": "s8", "depth": 1}, {"num": "10", "title": "S9", "label": "s9", "depth": 1}, {"num": "", "title": "S10", "label": "s10", "depth": 0}]
_PAPER_EDGES = [
    {"src": s, "dst": d, "count": c, "kind": k}
    for s, d, c, k in [[1, 0, 2, "dep"], [2, 0, 2, "dep"], [2, 1, 1, "dep"], [2, 5, 1, "fwd"], [2, 6, 1, "fwd"], [2, 9, 1, "fwd"], [3, 2, 2, "dep"], [4, 3, 2, "dep"], [5, 3, 1, "dep"], [5, 4, 4, "dep"], [6, 0, 1, "dep"], [6, 3, 2, "dep"], [6, 5, 2, "dep"], [7, 6, 1, "dep"], [8, 6, 1, "dep"], [8, 7, 1, "dep"], [9, 6, 3, "dep"], [9, 8, 2, "dep"], [0, 10, 1, "struct"], [1, 10, 1, "struct"], [2, 10, 1, "struct"], [3, 10, 1, "struct"], [4, 10, 1, "struct"], [5, 10, 1, "struct"], [6, 10, 1, "struct"], [7, 10, 1, "struct"], [8, 10, 1, "struct"], [9, 10, 1, "struct"]]
]


def test_layout_does_not_depend_on_set_order(monkeypatch):
    """grandalf keeps edges in sets, and its objects hash by memory address, so
    the layout used to change from one build to the next. Random hashes give a
    different set order on each run, and the layout must not change."""
    import random

    from grandalf import graphs

    outs = set()
    for seed in range(8):
        rng = random.Random(seed)
        table = {}
        rand_hash = lambda self: table.setdefault(id(self), rng.getrandbits(48))
        monkeypatch.setattr(graphs.Vertex, "__hash__", rand_hash)
        monkeypatch.setattr(graphs.Edge, "__hash__", rand_hash)
        out = layout_tree(_PAPER_NODES, _PAPER_EDGES, "horizontal")
        outs.add(json.dumps(out, sort_keys=True))
    assert len(outs) == 1


def test_tall_horizontal_toc_closes_up_its_stack():
    from rsm import toc_layout as tl

    out = layout_tree(_PAPER_NODES, _PAPER_EDGES, "horizontal")
    wide = tl.MAX_TREE_H
    try:
        tl.MAX_TREE_H = 10_000
        loose = layout_tree(_PAPER_NODES, _PAPER_EDGES, "horizontal")
    finally:
        tl.MAX_TREE_H = wide
    assert out["height"] < loose["height"]
    ys = sorted({n["y"] for n in out["nodes"]})
    assert all(b - a >= tl.NODE_H / 2 for a, b in zip(ys, ys[1:]))


def test_proof_rail_keeps_its_spacing():
    """The cap is for TOC graphs. A proof rail (root_label set) fits its gutter."""
    from rsm import toc_layout as tl

    out = layout_tree(_PAPER_NODES, _PAPER_EDGES, "horizontal", root_label="Goal")
    wide = tl.MAX_TREE_H
    try:
        tl.MAX_TREE_H = 10_000
        loose = layout_tree(_PAPER_NODES, _PAPER_EDGES, "horizontal", root_label="Goal")
    finally:
        tl.MAX_TREE_H = wide
    assert out == loose
