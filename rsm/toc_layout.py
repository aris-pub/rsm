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
HORIZ_LAYER_GAP = 38  # tighter depth gap when laid out left-to-right
GUTTER_ASPECT = 0.62  # target width/height for the horizontal rail tree
SIBLING_GAP = 26  # horizontal gap between nodes in a layer (grandalf xspace)
COMPONENT_GAP = 70  # horizontal gap between disconnected components


ROOT_LABEL = "Goal"  # horizontal proof-rail root; full statement shown on hover


def _node_width(node: dict, root_label: str | None = None) -> int:
    # When a root_label is given, the root collapses to that short marker (full
    # title/statement on hover) so it doesn't eat the limited width. Numbered
    # sections size to their (short) number; an unlabelled root sizes to its
    # full title.
    if root_label is not None and node["depth"] == 0:
        return int(len(root_label) * CHAR_W) + 2 * NODE_PAD_X
    text = node["num"] if node["num"] else node["title"]
    return int(len(text) * CHAR_W) + 2 * NODE_PAD_X


def layout_tree(
    nodes: list[dict], edges: list[dict], orient: str = "vertical",
    root_label: str | None = None,
) -> dict | None:
    """Return positioned nodes and edges, or None if layout is unavailable.

    nodes: [{"num", "title", "label", "depth"}], index = document order.
    edges: [{"src", "dst", "count", "kind"}] with src/dst indexing `nodes`.
    orient: "vertical" stacks layers top-to-bottom (foundations on top); this is
    the TOC block default. "horizontal" runs depth left-to-right and stacks the
    sibling steps vertically, giving a tall, narrow graph that fits the proof
    rail at full text size and scrolls as the reader moves through the proof.
    grandalf only lays out top-down, so for the horizontal case we feed it node
    boxes with width/height swapped (so layer and sibling gaps are sized for the
    final orientation) and transpose the resulting coordinates.
    """
    if not nodes:
        return None
    try:
        from grandalf.graphs import Edge, Graph, Vertex
        from grandalf.layouts import SugiyamaLayout
    except ImportError:
        return None

    horizontal = orient == "horizontal"
    nw = {i: _node_width(n, root_label) for i, n in enumerate(nodes)}

    verts = {i: Vertex(i) for i in range(len(nodes))}
    for i, v in verts.items():
        # In horizontal mode the layer axis (grandalf's "vertical") must leave
        # room for each node's text width, so hand grandalf swapped dimensions.
        v.view = _View(NODE_H, nw[i]) if horizontal else _View(nw[i], NODE_H)

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
        sug.yspace = HORIZ_LAYER_GAP if horizontal else LAYER_GAP
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

    # grandalf puts dependents (edge sources) in the first layer and the sinks
    # everything depends on (the foundations, e.g. section 1 or a proof's root
    # statement) in the last. We want the foundations to lead: at the top in
    # vertical mode, at the left in horizontal mode.
    max_y = max(y for _, y in placed.values())
    if horizontal:
        # depth -> x (foundation at left), sibling spread -> y
        placed = {i: (max_y - y, x) for i, (x, y) in placed.items()}
        # grandalf orders siblings to minimize crossings; reassign the vertical
        # slots in document order so the rail reads top-to-bottom in step
        # sequence (step 1 above step 2, ...), keeping grandalf's spacing.
        from collections import defaultdict

        layers: dict[float, list[int]] = defaultdict(list)
        for i, (x, _) in placed.items():
            layers[round(x, 1)].append(i)
        for idxs in layers.values():
            slots = sorted(placed[i][1] for i in idxs)
            for slot, i in zip(slots, sorted(idxs)):
                placed[i] = (placed[i][0], slot)
        # A proof step DAG is naturally tall and thin, so when fit into the
        # gutter it scales to the height and leaves the width empty (and the
        # nodes small). Spread the depth axis until the tree is about as wide
        # as the gutter is, so it scales up to fill the space.
        cur_w = max(placed[i][0] + nw[i] for i in placed)
        cur_h = max(placed[i][1] + NODE_H for i in placed)
        target_w = cur_h * GUTTER_ASPECT
        if 0 < cur_w < target_w:
            sx = target_w / cur_w
            placed = {i: (x * sx, y) for i, (x, y) in placed.items()}
    else:
        placed = {i: (x, max_y - y) for i, (x, y) in placed.items()}

    height = max(placed[i][1] + NODE_H for i in placed)
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
        ax, ay, bx, by = _anchor(a, b, horizontal)
        out_edges.append(
            {"src": e["src"], "dst": e["dst"], "kind": e["kind"],
             "count": e["count"], "x1": ax, "y1": ay, "x2": bx, "y2": by}
        )

    return {"width": round(width, 1), "height": round(height, 1),
            "nodes": out_nodes, "edges": out_edges}


def _anchor(
    a: dict, b: dict, horizontal: bool = False
) -> tuple[float, float, float, float]:
    """Edge anchor points on the box faces, by layer relationship."""
    acx, bcx = a["x"] + a["w"] / 2, b["x"] + b["w"] / 2
    acy, bcy = a["y"] + a["h"] / 2, b["y"] + b["h"] / 2
    if horizontal:  # depth runs left-to-right
        if b["x"] > a["x"]:  # b right of a: leave right, enter left
            return a["x"] + a["w"], acy, b["x"], bcy
        if b["x"] < a["x"]:  # b left of a: leave left, enter right
            return a["x"], acy, b["x"] + b["w"], bcy
        # same layer: leave bottom/top
        if bcy >= acy:
            return acx, a["y"] + a["h"], bcx, b["y"]
        return acx, a["y"], bcx, b["y"] + b["h"]
    if b["y"] > a["y"]:  # b below a: leave bottom, enter top
        return acx, a["y"] + a["h"], bcx, b["y"]
    if b["y"] < a["y"]:  # b above a: leave top, enter bottom
        return acx, a["y"], bcx, b["y"] + b["h"]
    # same layer: leave right/left
    if bcx >= acx:
        return a["x"] + a["w"], acy, b["x"], bcy
    return a["x"], acy, b["x"] + b["w"], bcy


class _View:
    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h
