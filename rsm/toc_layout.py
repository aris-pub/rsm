"""Build-time layered layout for the table-of-contents dependency graph.

The transformer produces the TOC entries (in document order, with depth) and
the cross-section dependency edges. This module runs a Sugiyama layered layout
over them at build time, so the rendered HTML carries final coordinates and no
layout library ships to the browser. Pure Python (grandalf), no Node, no system
binary.
"""

from __future__ import annotations

NODE_H = 30
NODE_PAD_X = 11
CHAR_W = 7.0  # approx advance of the number glyphs at the TOC font size
LAYER_GAP = 58  # vertical gap between layers (grandalf yspace)
SIBLING_GAP = 26  # horizontal gap between nodes in a layer (grandalf xspace)
COMPONENT_GAP = 70  # horizontal gap between disconnected components


def _node_width(node: dict) -> int:
    # Numbered sections size to their (short) number; the unnumbered root node
    # sizes to its title text so the paper title fits.
    text = node["num"] + "." if node["num"] else node["title"]
    return int(len(text) * CHAR_W) + 2 * NODE_PAD_X


def layout_tree(nodes: list[dict], edges: list[dict]) -> dict | None:
    """Return positioned nodes and edges, or None if layout is unavailable.

    nodes: [{"num", "title", "label", "depth"}], index = document order.
    edges: [{"src", "dst", "count", "kind"}] with src/dst indexing `nodes`.
    """
    if not nodes:
        return None
    try:
        from grandalf.graphs import Edge, Graph, Vertex
        from grandalf.layouts import SugiyamaLayout
    except ImportError:
        return None

    nw = {i: _node_width(n) for i, n in enumerate(nodes)}

    verts = {i: Vertex(i) for i in range(len(nodes))}
    for i, v in verts.items():
        v.view = _View(nw[i], NODE_H)

    # Dependency and structural (outline backbone) edges define the layering;
    # both are acyclic. Forward pointers are drawn over the computed positions.
    dep = [(e["src"], e["dst"]) for e in edges if e["kind"] in ("dep", "struct")]
    g = Graph(list(verts.values()), [Edge(verts[a], verts[b]) for a, b in dep])

    placed: dict[int, tuple[float, float]] = {}
    x_cursor = 0.0
    # Stable component order: by the smallest original index they contain.
    comps = sorted(g.C, key=lambda c: min(v.data for v in c.sV))
    for comp in comps:
        sug = SugiyamaLayout(comp)
        sug.xspace = SIBLING_GAP
        sug.yspace = LAYER_GAP
        sug.init_all()
        sug.draw()
        xs = [v.view.xy[0] for v in comp.sV]
        ys = [v.view.xy[1] for v in comp.sV]
        min_x, min_y = min(xs), min(ys)
        for v in comp.sV:
            x, y = v.view.xy
            placed[v.data] = (x - min_x + x_cursor, y - min_y)
        comp_w = (max(xs) - min_x) if len(xs) > 1 else nw[comp.sV[0].data]
        x_cursor += comp_w + COMPONENT_GAP

    # Flip vertically: grandalf puts dependents (edge sources) at the top, but
    # we want the foundational sections everything depends on (the sinks, e.g.
    # section 1) at the top, with dependents flowing downward.
    max_y = max(y for _, y in placed.values())
    placed = {i: (x, max_y - y) for i, (x, y) in placed.items()}

    height = max(y for _, y in placed.values()) + NODE_H
    width = max(placed[i][0] + nw[i] for i in placed)

    out_nodes = []
    for i, n in enumerate(nodes):
        cx, cy = placed[i]
        out_nodes.append(
            {**n, "idx": i, "x": round(cx, 1), "y": round(cy, 1),
             "w": nw[i], "h": NODE_H}
        )

    out_edges = []
    for e in edges:
        a, b = out_nodes[e["src"]], out_nodes[e["dst"]]
        ax, ay, bx, by = _anchor(a, b)
        out_edges.append(
            {"src": e["src"], "dst": e["dst"], "kind": e["kind"],
             "count": e["count"], "x1": ax, "y1": ay, "x2": bx, "y2": by}
        )

    return {"width": round(width, 1), "height": round(height, 1),
            "nodes": out_nodes, "edges": out_edges}


def _anchor(a: dict, b: dict) -> tuple[float, float, float, float]:
    """Edge anchor points on the box faces, by vertical relationship."""
    acx, bcx = a["x"] + a["w"] / 2, b["x"] + b["w"] / 2
    if b["y"] > a["y"]:  # b below a: leave bottom, enter top
        return acx, a["y"] + a["h"], bcx, b["y"]
    if b["y"] < a["y"]:  # b above a: leave top, enter bottom
        return acx, a["y"], bcx, b["y"] + b["h"]
    # same layer: leave right/left
    if bcx >= acx:
        return a["x"] + a["w"], a["y"] + a["h"] / 2, b["x"], b["y"] + b["h"] / 2
    return a["x"], a["y"] + a["h"] / 2, b["x"] + b["w"], b["y"] + b["h"] / 2


class _View:
    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h
