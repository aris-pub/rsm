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
LABEL_CHAR_W = 10.0  # the root marker ("Goal") is letters, wider than digits
ROOT_DOT_R = 5.0  # radius of the unlabelled TOC root dot, in user units
LAYER_GAP = 58  # vertical gap between layers (grandalf yspace)
MIN_LAYER_GAP = 34  # the gap never goes below this, however many layers
MAX_TREE_H = 300  # a TOC graph taller than this gets its gaps closed up
MIN_STACK_GAP = 8  # least gap between sections stacked in one column (horizontal TOC)
HORIZ_LAYER_GAP = 38  # tighter depth gap when laid out left-to-right
GUTTER_ASPECT = 0.62  # target width/height for the horizontal rail tree
SIBLING_GAP = 26  # horizontal gap between nodes in a layer (grandalf xspace)
COMPONENT_GAP = 70  # horizontal gap between disconnected components


ROOT_LABEL = "Goal"  # horizontal proof-rail root; full statement shown on hover


def _node_width(node: dict, root_label: str | None = None) -> int:
    if node["depth"] == 0:
        # A labelled root (the proof rail's "Goal") sizes to that short marker,
        # full statement on hover. An unlabelled root is the TOC dot: it reserves
        # a small fixed slot for the dot, not a title, so a long title cannot
        # widen the drawing.
        if root_label is not None:
            return int(len(root_label) * LABEL_CHAR_W) + 2 * NODE_PAD_X
        return int(2 * ROOT_DOT_R) + 2 * NODE_PAD_X
    # Numbered sections size to their (short) number.
    text = node["num"] if node["num"] else node["title"]
    return int(len(text) * CHAR_W) + 2 * NODE_PAD_X


def _layer_gap(n_layers: int) -> float:
    """Gap between layers of a vertical tree: LAYER_GAP, smaller when the tree
    has so many layers that it would be taller than MAX_TREE_H."""
    if n_layers < 2:
        return LAYER_GAP
    fit = (MAX_TREE_H - NODE_H * n_layers) / (n_layers - 1)
    return max(MIN_LAYER_GAP, min(LAYER_GAP, fit))


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

    # grandalf collects edges in plain sets, and its vertices and edges hash by
    # memory address, so the set order, and with it the layout, changed from one
    # build to the next. Hashing by node index makes every build the same.
    class _Vertex(Vertex):
        def __hash__(self):
            return hash(self.data)

    class _Edge(Edge):
        def __hash__(self):
            return hash((self.v[0].data, self.v[1].data))

    horizontal = orient == "horizontal"
    nw = {i: _node_width(n, root_label) for i, n in enumerate(nodes)}

    verts = {i: _Vertex(i) for i in range(len(nodes))}
    for i, v in verts.items():
        # In horizontal mode the layer axis (grandalf's "vertical") must leave
        # room for each node's text width, so hand grandalf swapped dimensions.
        v.view = _View(NODE_H, nw[i]) if horizontal else _View(nw[i], NODE_H)

    # Dependency and structural (outline backbone) edges define the layering;
    # both are acyclic. Forward pointers are drawn over the computed positions.
    dep = [(e["src"], e["dst"]) for e in edges if e["kind"] in ("dep", "struct")]
    g = Graph(list(verts.values()), [_Edge(verts[a], verts[b]) for a, b in dep])

    # Stable component order: by the smallest original index they contain.
    comps = sorted(g.C, key=lambda c: min(v.data for v in c.sV))

    def place(xspace: float) -> dict[int, tuple[float, float]]:
        placed: dict[int, tuple[float, float]] = {}
        x_cursor = 0.0
        for comp in comps:
            sug = SugiyamaLayout(comp)
            sug.xspace = xspace
            sug.init_all()
            sug.yspace = HORIZ_LAYER_GAP if horizontal else _layer_gap(len(sug.layers))
            sug.draw()
            xs = [v.view.xy[0] for v in comp.sV]
            ys = [v.view.xy[1] for v in comp.sV]
            min_x, min_y = min(xs), min(ys)
            for v in comp.sV:
                x, y = v.view.xy
                placed[v.data] = (x - min_x + x_cursor, y - min_y)
            comp_w = (max(xs) - min_x) if len(xs) > 1 else nw[comp.sV[0].data]
            x_cursor += comp_w + COMPONENT_GAP
        return placed

    # A horizontal TOC stacks the sections of one depth column, so many in a
    # column make it tall. Lay it out again with a smaller sibling gap until it
    # fits MAX_TREE_H. Proof rails (root_label set) fit their gutter instead.
    gaps = (SIBLING_GAP, 18, 12, MIN_STACK_GAP) if horizontal and root_label is None else (SIBLING_GAP,)
    for xspace in gaps:
        placed = place(xspace)
        stack = max(x for x, _ in placed.values()) - min(x for x, _ in placed.values()) + NODE_H
        if stack <= MAX_TREE_H:
            break

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
