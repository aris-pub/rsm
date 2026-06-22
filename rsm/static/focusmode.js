// focusmode.js
//
// Click a node in the floating proof rail to focus that step: the proof
// collapses to just that step and its transitive prerequisite cone, every
// other step shrinks to its bare "⟨n⟩" number, and the rail dims to the same
// cone. The cone is the prerequisite closure over the rail's edges (dependency
// + containment, never forward pointers), so a step's structural ancestors
// come along automatically and the collapsed view stays coherent.
//
// Restore the whole proof from the "Show full proof" bar in the rail.

export function setup(root = document) {
  const rail = root.querySelector(".proof-rail");
  if (!rail) return;

  let active = null; // { proofEl, svg, startIdx }

  function coneOf(svg, startIdx) {
    // Prerequisite closure: an edge X->Y (not forward) means "read Y before X".
    const prereq = new Map();
    for (const e of svg.querySelectorAll(".toc-edge")) {
      if (e.classList.contains("fwd")) continue;
      const f = e.dataset.from;
      if (!prereq.has(f)) prereq.set(f, []);
      prereq.get(f).push(e.dataset.to);
    }
    const seen = new Set([String(startIdx)]);
    const stack = [String(startIdx)];
    while (stack.length) {
      for (const to of prereq.get(stack.pop()) || []) {
        if (!seen.has(to)) {
          seen.add(to);
          stack.push(to);
        }
      }
    }
    return seen; // set of idx strings; may include the root idx (no step)
  }

  // Tree-node idx (document order) maps 1:1 to the proof's steps in DOM order.
  const stepsOf = (proofEl) => [...proofEl.querySelectorAll(".step")];

  // Folding is pure CSS: the row collapses to a thin line, its number kept in
  // the right margin where every expanded step also shows it.
  const collapseStep = (st) => st.classList.add("proof-focus-collapsed");
  const openStep = (st) => st.classList.remove("proof-focus-collapsed");

  // Light the cone path (focus-lit) and recede everything else (focus-faded).
  // Dedicated classes, untouched by hover, so the focus styling persists while
  // the reader mouses over the tree.
  function dimRail(svg, cone) {
    for (const n of svg.querySelectorAll(".toc-node")) {
      const lit = cone.has(n.dataset.idx);
      n.classList.toggle("focus-lit", lit);
      n.classList.toggle("focus-faded", !lit);
    }
    for (const e of svg.querySelectorAll(".toc-edge")) {
      const lit =
        !e.classList.contains("fwd") &&
        cone.has(e.dataset.from) &&
        cone.has(e.dataset.to);
      e.classList.toggle("focus-lit", lit);
      e.classList.toggle("focus-faded", !lit);
    }
  }

  const undimRail = (svg) =>
    svg
      .querySelectorAll(".focus-faded, .focus-lit")
      .forEach((x) => x.classList.remove("focus-faded", "focus-lit"));

  // A step's own number ("⟨4⟩"), not a descendant's.
  function stepNumber(st) {
    const el = st && st.querySelector(":scope > .hr-info-zone .step-number");
    return el ? el.textContent.trim() : "";
  }

  // The one obvious way out lives in the rail itself, which is fixed on screen,
  // so it is always reachable no matter how far the reader has scrolled.
  let exitBar = null;
  function setExitBar(sel) {
    const num = stepNumber(sel);
    if (!exitBar) {
      exitBar = document.createElement("div");
      exitBar.className = "proof-focus-exit";
      exitBar.setAttribute("role", "button");
      exitBar.tabIndex = 0;
      exitBar.addEventListener("click", exitFocus);
    }
    exitBar.innerHTML =
      '<span class="proof-focus-back">↩</span>' +
      `<span>${num ? `Step ${num}` : "Focused"} · ` +
      '<span class="proof-focus-show-all">Show full proof</span></span>';
    rail.insertBefore(exitBar, rail.firstChild);
    rail.classList.add("focusing");
  }

  function exitFocus() {
    if (!active) return;
    rail.classList.remove("focusing");
    if (exitBar) exitBar.remove();
    stepsOf(active.proofEl).forEach(openStep);
    undimRail(active.svg);
    active.proofEl.classList.remove("proof-focused");
    active = null;
  }

  function enterFocus(railItem, proofEl, startIdx) {
    exitFocus();
    const svg = railItem.querySelector("svg.toc-tree");
    if (!svg) return;
    const cone = coneOf(svg, startIdx);
    const steps = stepsOf(proofEl);
    steps.forEach((st, i) => (cone.has(String(i)) ? openStep(st) : collapseStep(st)));
    dimRail(svg, cone);
    proofEl.classList.add("proof-focused");
    const sel = steps[startIdx];
    active = { proofEl, svg, startIdx: String(startIdx) };
    setExitBar(sel);
    // Let the mobile drawer drop to peek so the focused cone is readable.
    document.dispatchEvent(new CustomEvent("rsm:focus-enter"));
    if (sel) sel.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  rail.addEventListener("click", (ev) => {
    const node = ev.target.closest(".toc-node");
    if (!node) return;
    const railItem = node.closest(".proof-rail-item");
    if (!railItem || railItem.dataset.proof === "toc") return; // TOC fallback navigates
    ev.preventDefault();
    if (node.classList.contains("level-0")) return; // the "Goal" root isn't a step
    const proofEl = root.querySelector(`.proof[data-nodeid="${railItem.dataset.proof}"]`);
    if (!proofEl) return;
    enterFocus(railItem, proofEl, node.dataset.idx);
  });
}
