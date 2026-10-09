// tocarcs.js
//
// Hover interaction for the TOC tree view. The dependency graph is laid out and
// fully positioned at build time (in Python, via grandalf) and shipped as a
// static SVG. This module only adds hover focus: dim unrelated nodes/edges and
// reveal the hovered section's full title. No layout runs in the browser.

// Node/label type must be a constant on-screen size no matter how the SVG is
// scaled to fit its container. The graph geometry is in user units, so a fixed
// user-unit font grows when a small graph renders large and shrinks when a big
// graph is squeezed. Counter-scale: font-size(user units) = TARGET_PX divided by
// (renderedWidth / viewBoxWidth), exposed as a CSS var the type rules read.
const LABEL_TARGET_PX = 13.5;
const HOVER_TARGET_PX = 13;

// Directed adjacency over an svg's non-forward edges. An edge from X to Y (a
// containment-up or a backward reference, never a forward pointer) means "read Y
// before X": Y is a prerequisite of X. dir "up" walks toward prerequisites
// (from -> to), dir "down" walks toward dependents (to -> from). Shared by the
// rail's hover cone and the sticky dependency lens (deplens.js).
export function buildAdj(svg, dir = "up") {
  const adj = new Map();
  for (const e of svg.querySelectorAll(".toc-edge")) {
    if (e.classList.contains("fwd")) continue;
    const a = dir === "down" ? e.dataset.to : e.dataset.from;
    const b = dir === "down" ? e.dataset.from : e.dataset.to;
    if (!adj.has(a)) adj.set(a, []);
    adj.get(a).push(b);
  }
  return adj;
}

// The transitive cone of node `idx` in a direction: every node reachable over
// non-forward edges, including `idx` itself. Returns a Set of idx strings.
export function coneOver(svg, idx, dir = "up") {
  const adj = buildAdj(svg, dir);
  const start = String(idx);
  const seen = new Set([start]);
  const stack = [start];
  while (stack.length) {
    for (const next of adj.get(stack.pop()) || []) {
      if (!seen.has(next)) {
        seen.add(next);
        stack.push(next);
      }
    }
  }
  return seen;
}

function stabilizeLabels(svg) {
  const vb = svg.viewBox && svg.viewBox.baseVal;
  const w = svg.getBoundingClientRect().width;
  if (!vb || !vb.width || !w) return; // not laid out or hidden; observer retries
  const perUnit = w / vb.width;
  svg.style.setProperty("--toc-label-px", (LABEL_TARGET_PX / perUnit).toFixed(2) + "px");
  svg.style.setProperty("--toc-hover-px", (HOVER_TARGET_PX / perUnit).toFixed(2) + "px");
  // The label font-size is in user units and grows when the graph is squeezed to
  // fit, so a build-time rect width (a character-count estimate) can be too
  // narrow and the text spills past the box. The root marker ("Top") is the
  // worst case: letters, not digits. Now that the font is applied, measure each
  // label and widen its rect to fit, keeping it centered on the same point.
  const padXU = 5 / perUnit; // about 5px on-screen inline padding each side
  for (const node of svg.querySelectorAll(".toc-node")) {
    const rect = node.querySelector("rect");
    const text = node.querySelector(".toc-secnum");
    if (!rect || !text) continue;
    const need = text.getBBox().width + 2 * padXU;
    const cur = parseFloat(rect.getAttribute("width"));
    if (need > cur) {
      const cx = parseFloat(rect.getAttribute("x")) + cur / 2;
      rect.setAttribute("width", need.toFixed(1));
      rect.setAttribute("x", (cx - need / 2).toFixed(1));
    }
  }
}

export function wireTree(svg) {
  const nodes = [...svg.querySelectorAll(".toc-node")];
  const edges = [...svg.querySelectorAll(".toc-edge")];
  if (!nodes.length) return;

  stabilizeLabels(svg);
  // Recompute when the SVG's rendered size changes: rail resize, collapse, or
  // becoming visible after a scope switch (hidden -> shown trips this too).
  if (typeof ResizeObserver !== "undefined") {
    new ResizeObserver(() => stabilizeLabels(svg)).observe(svg);
  }

  // The upstream closure of X is everything to read first (see coneOver).
  const closure = (idx) => coneOver(svg, idx, "up");

  // Light up a node's prerequisite cone (the path to read before it) and fade
  // the rest. idx == null clears the fade entirely.
  function applyCone(idx) {
    if (idx == null) {
      for (const x of svg.querySelectorAll(".toc-faded")) x.classList.remove("toc-faded");
      return;
    }
    const cone = closure(idx);
    for (const e of edges) {
      const on =
        !e.classList.contains("fwd") &&
        cone.has(e.dataset.from) &&
        cone.has(e.dataset.to);
      e.classList.toggle("toc-faded", !on);
    }
    for (const n of nodes) {
      n.classList.toggle("toc-faded", !cone.has(n.getAttribute("data-idx")));
    }
  }
  svg.__applyCone = applyCone;

  nodes.forEach((node) => {
    const idx = node.getAttribute("data-idx");
    node.addEventListener("mouseenter", () => {
      applyCone(idx);
    });
    node.addEventListener("mouseleave", () => {
      // Revert to the pinned "current path" the tree rests in (or clear).
      applyCone(svg.__pinnedIdx != null ? svg.__pinnedIdx : null);
    });
  });

  // A pin requested before this tree was wired takes effect now.
  if (svg.__pinnedIdx != null) applyCone(svg.__pinnedIdx);
}

// Persistently highlight a node's prerequisite cone: the "current path" the
// tree rests in between hovers. Pass null to clear. Safe to call before wiring.
export function pinTreeCurrent(svg, idx) {
  svg.__pinnedIdx = idx;
  if (svg.__applyCone) svg.__applyCone(idx);
}

export function drawAll(root = document) {
  root.querySelectorAll(".toc.tree svg.toc-tree").forEach((svg) => {
    if (svg.dataset.wired) return;
    svg.dataset.wired = "1";
    wireTree(svg);
  });
}

export function setup(root = document) {
  drawAll(root);
}
