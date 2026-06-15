// prooftree.js
//
// Floating left rail that shows the step-dependency tree of the proof the
// reader is currently in (or the section TOC when between proofs). The trees
// are pre-rendered SVGs inside .proof-rail (one per proof, plus a TOC
// fallback), laid out at build time; this module only chooses which one is
// shown as the reader scrolls, and reuses the tree hover logic from tocarcs.

import { wireTree } from "./tocarcs.js";

export function setup(root = document) {
  const rail = root.querySelector(".proof-rail");
  if (!rail) return;

  const items = new Map();
  for (const item of rail.querySelectorAll(".proof-rail-item")) {
    items.set(item.dataset.proof, item);
    const svg = item.querySelector("svg.toc-tree");
    if (svg && !svg.dataset.wired) {
      svg.dataset.wired = "1";
      wireTree(svg);
    }
  }

  const proofs = [...root.querySelectorAll(".proof[data-nodeid]")];
  if (!proofs.length && !items.has("toc")) return;

  rail.classList.add("active");
  let current = null;
  function show(key) {
    if (!items.has(key)) key = items.has("toc") ? "toc" : null;
    if (key === current) return;
    current = key;
    for (const [k, item] of items) item.classList.toggle("shown", k === key);
  }
  show("toc");

  // The active proof is the one whose box is highest while still overlapping
  // the reading band near the top of the viewport; otherwise the TOC fallback.
  const visible = new Set();
  const observer = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (e.isIntersecting) visible.add(e.target);
        else visible.delete(e.target);
      }
      let best = null;
      let bestTop = Infinity;
      for (const p of visible) {
        const top = p.getBoundingClientRect().top;
        if (top < bestTop) {
          bestTop = top;
          best = p;
        }
      }
      show(best ? best.getAttribute("data-nodeid") : "toc");
    },
    { rootMargin: "-12% 0px -55% 0px", threshold: 0 },
  );
  for (const p of proofs) observer.observe(p);

  // Active-step tracking: mark the rail node of the step currently being read,
  // using the same "topmost in the reading band" rule. Suppressed during focus
  // mode, which provides its own emphasis.
  let currentNode = null;
  function clearCurrent() {
    if (currentNode) {
      currentNode.classList.remove("current-step");
      currentNode = null;
    }
  }
  function markStep(stepEl) {
    if (!stepEl || rail.classList.contains("focusing")) return clearCurrent();
    const proofEl = stepEl.closest(".proof[data-nodeid]");
    const item = proofEl && items.get(proofEl.getAttribute("data-nodeid"));
    if (!item) return clearCurrent();
    // step index in document order == the rail node's data-idx
    const idx = [...proofEl.querySelectorAll(".step")].indexOf(stepEl);
    const node = idx >= 0 ? item.querySelector(`.toc-node[data-idx="${idx}"]`) : null;
    if (node === currentNode) return;
    clearCurrent();
    if (node) {
      node.classList.add("current-step");
      currentNode = node;
    }
  }

  const stepsInView = new Set();
  const stepObserver = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (e.isIntersecting) stepsInView.add(e.target);
        else stepsInView.delete(e.target);
      }
      // The root is a zero-height line at the viewport's vertical center, so the
      // intersecting steps are those crossing it: an ancestor chain whose
      // deepest member (largest top) is the step actually being read.
      let best = null;
      let bestTop = -Infinity;
      for (const s of stepsInView) {
        const top = s.getBoundingClientRect().top;
        if (top > bestTop) {
          bestTop = top;
          best = s;
        }
      }
      markStep(best);
    },
    { rootMargin: "-50% 0px -50% 0px", threshold: 0 },
  );
  for (const s of root.querySelectorAll(".proof[data-nodeid] .step")) {
    stepObserver.observe(s);
  }
}
