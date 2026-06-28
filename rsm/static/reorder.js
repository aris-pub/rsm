// reorder.js
//
// Logic-preserving reordering of a proof's steps. A proof ships with a step
// dependency DAG (the same one drawn in the rail's Proof map): an edge of kind
// "dep" from S to D means S depends on D, so D must be read before S. The reader
// may rearrange steps into any order that still respects every such edge; this
// module is the pure core that decides which orders are legal. The drag
// interaction, the body reflow, and the State-panel recompute build on top of
// it (see prooftree.js).
//
// Two constraints define the legal space (see potf-bzv):
//   - hierarchy-respecting: a step moves only among its siblings, and a step's
//     subtree travels with it as one contiguous block. This is NOT implied by
//     "topological sort" (a raw topo sort would interleave a substep between two
//     top-level steps); we impose it so the proof keeps its shape.
//   - globally valid: the resulting flat reading order must respect every dep
//     edge, not just edges local to the moved sibling group. A top-level swap
//     can violate a deep cross-subtree dependency, so validity is checked on the
//     whole flattened order. Proof DAGs are tiny, so brute force is fine.
//
// Steps are identified by data-nodeid, not by label: an authored proof may leave
// a step (e.g. the closing "combining ... yields ..." step) unlabeled, but it is
// still a real DAG node with real dependencies, so it must be in the model or
// the validity check would miss the constraints it imposes.

import { pinTreeCurrent } from "./tocarcs.js";

// Steps inside a :calc: chain read as one step and are not DAG nodes (mirrors
// proof.py, which drops steps under a Calc).
function isDagStep(stepEl) {
  return !stepEl.closest(".calc");
}

// Build the model from a proof's rail item, or null if it has no reorderable
// graph. Nodes 0..n-1 of the DAG are the proof's steps in document order; nodes
// at index >= n are external results (cited theorems) and the root, which never
// move and impose no intra-proof ordering, so they are excluded.
export function extractModel(railItem) {
  const svg = railItem.querySelector("svg.toc-tree");
  if (!svg) return null;
  const svgNodes = [...svg.querySelectorAll("a.toc-node")];

  // Locate the body proof via any labeled step node, then take its steps in
  // document order (the order proof.py numbers them). Index i of the DAG is the
  // i-th body step.
  let proofEl = null;
  for (const n of svgNodes) {
    const href = n.getAttribute("href") || "";
    if (href.length > 1) {
      const el = document.getElementById(href.slice(1));
      if (el && el.classList.contains("step")) {
        proofEl = el.closest(".proof");
        break;
      }
    }
  }
  if (!proofEl) return null;
  const bodySteps = [...proofEl.querySelectorAll(".step")].filter(isDagStep);
  const n = bodySteps.length;
  if (!n) return null;

  const svgByIdx = new Map();
  for (const node of svgNodes) svgByIdx.set(Number(node.getAttribute("data-idx")), node);

  // steps keyed by data-nodeid, carrying their body element, DAG node, and index
  const byId = new Map();
  const idToId = new Map(); // dag index -> nodeid, for step indices only
  bodySteps.forEach((el, i) => {
    const id = el.dataset.nodeid || "idx-" + i;
    byId.set(id, { id, idx: i, bodyEl: el, svgNode: svgByIdx.get(i) || null, parent: null });
    idToId.set(i, id);
  });

  // dependency edges among steps; edges into a result/root node (index >= n) are
  // always satisfied from inside the proof and are skipped.
  const deps = [];
  for (const edge of svg.querySelectorAll("path.toc-edge.dep")) {
    const s = Number(edge.getAttribute("data-from"));
    const d = Number(edge.getAttribute("data-to"));
    if (s < n && d < n) deps.push({ src: idToId.get(s), dst: idToId.get(d) });
  }

  // hierarchy from the body nesting: a step's parent is its nearest ancestor
  // .step within this proof; null parent is the proof's top level.
  for (const step of byId.values()) {
    let anc = step.bodyEl.parentElement;
    while (anc && anc !== proofEl) {
      if (anc.classList.contains("step") && anc.dataset.nodeid && byId.has(anc.dataset.nodeid)) {
        step.parent = anc.dataset.nodeid;
        break;
      }
      anc = anc.parentElement;
    }
  }

  // children: parent id (or "" for top level) -> child ids in document order
  const children = new Map();
  for (const step of byId.values()) {
    const key = step.parent || "";
    if (!children.has(key)) children.set(key, []);
    children.get(key).push(step.id);
  }
  for (const arr of children.values()) arr.sort((a, b) => byId.get(a).idx - byId.get(b).idx);

  return { byId, deps, children, svg, proofEl };
}

// Flatten the tree into a linear reading order given a `children` map (parent ->
// ordered child ids), depth-first: each step immediately followed by its
// subtree. This is the order the reader actually sees.
export function flatten(children) {
  const out = [];
  const walk = (key) => {
    for (const id of children.get(key) || []) {
      out.push(id);
      walk(id);
    }
  };
  walk("");
  return out;
}

// A flat order is logic-preserving iff every dependency's prerequisite precedes
// it.
export function isValidOrder(model, flat) {
  const pos = new Map(flat.map((id, i) => [id, i]));
  return model.deps.every((e) => pos.get(e.dst) < pos.get(e.src));
}

// The legal insertion positions for step `id` within its sibling group: every
// index at which placing it (subtree intact) keeps the whole flattened order
// valid. Includes its current index. Returns indices into the sibling list.
export function legalPositions(model, id) {
  const step = model.byId.get(id);
  if (!step) return [];
  const key = step.parent || "";
  const without = (model.children.get(key) || []).filter((x) => x !== id);
  const legal = [];
  for (let p = 0; p <= without.length; p++) {
    const trial = new Map(model.children);
    trial.set(key, [...without.slice(0, p), id, ...without.slice(p)]);
    if (isValidOrder(model, flatten(trial))) legal.push(p);
  }
  return legal;
}

// Apply a move: place step `id` at sibling index `pos`, returning a new
// `children` map. Caller is responsible for having checked legality.
export function moveTo(model, id, pos) {
  const step = model.byId.get(id);
  const key = step.parent || "";
  const without = (model.children.get(key) || []).filter((x) => x !== id);
  const next = new Map(model.children);
  next.set(key, [...without.slice(0, pos), id, ...without.slice(pos)]);
  return next;
}

// Reorder the body .step elements to match `newChildren`, and commit it into the
// model. Each changed sibling group is re-laid in the given order; a step's
// subtree moves with it because the subtree lives inside the step's own element.
// Steps in a group are assumed contiguous (true for authored proofs), so the
// block is rebuilt at its current location, leaving surrounding prose in place.
export function applyToBody(model, newChildren) {
  for (const [key, ids] of newChildren) {
    const current = model.children.get(key) || [];
    if (ids.length === current.length && ids.every((id, i) => id === current[i])) continue;
    const els = ids.map((id) => model.byId.get(id).bodyEl);
    if (els.length < 2) continue;
    const container = els[0].parentElement;
    const domOrder = [...els].sort((a, b) =>
      a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1
    );
    const after = domOrder[domOrder.length - 1].nextSibling;
    for (const el of els) container.insertBefore(el, after);
  }
  model.children = newChildren;
}

// ---- interaction: opt-in drag reorder ------------------------------------
//
// A proof enters reorder mode from its handrail menu (handrails.js toggles
// .reorder-active and dispatches "reorder:toggle"). While active each step gets
// a gutter drag handle; dragging shows the legal insertion slots among the
// step's siblings (illegal ones turn the marker red and reject the drop), the
// rail DAG lights the dragged step's prerequisite cone, and a drop reflows the
// body. The State panel stays correct because each step is tagged with its build
// index (data-state-idx), which prooftree.js maps to instead of the step's
// position. (A step that itself introduces a hypothesis and is moved relative to
// an independent sibling could show a stale ASSUME entry; in practice such steps
// are pinned by what depends on them. See potf-bzv.)

const GRIP =
  '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M9 5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/><path d="M9 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/><path d="M9 19m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/><path d="M15 5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/><path d="M15 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/><path d="M15 19m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/></svg>';

const reorderState = new WeakMap(); // proof element -> { model, handles }

// A single polite live region announces reorder activity to screen readers
// (mode on/off, a step picked up, moved, dropped, or a rejected move).
let liveRegion = null;
function announce(msg) {
  if (!liveRegion) {
    liveRegion = document.createElement("div");
    liveRegion.className = "reorder-sr-status";
    liveRegion.setAttribute("role", "status");
    liveRegion.setAttribute("aria-live", "polite");
    document.body.appendChild(liveRegion);
  }
  // Clear then set on the next frame so a repeated identical message still
  // re-announces (assistive tech ignores an unchanged text node).
  liveRegion.textContent = "";
  requestAnimationFrame(() => {
    liveRegion.textContent = msg;
  });
}

export function setup(root = document) {
  root.addEventListener("reorder:toggle", (ev) => {
    const proof = ev.target.closest && ev.target.closest(".proof.hr");
    if (!proof) return;
    if (ev.detail && ev.detail.active) activate(proof);
    else deactivate(proof);
  });
  // Esc cancels reorder mode on every active proof.
  root.addEventListener("keydown", (ev) => {
    if (ev.key !== "Escape") return;
    for (const proof of document.querySelectorAll(".proof.reorder-active")) {
      proof.classList.remove("reorder-active");
      deactivate(proof);
    }
  });
}

function railItemFor(proof) {
  const id = proof.dataset.nodeid;
  return id ? document.querySelector(`.proof-rail-item[data-proof="${id}"]`) : null;
}

function activate(proof) {
  if (reorderState.has(proof)) return;
  const railItem = railItemFor(proof);
  const model = railItem && extractModel(railItem);
  if (!model || model.byId.size < 2) {
    proof.classList.remove("reorder-active");
    return;
  }
  const handles = [];
  for (const step of model.byId.values()) {
    // Tag each step with its build index so the State panel keeps mapping to
    // this step's own state after it moves; left in place after deactivate so a
    // reordered proof stays correct.
    step.bodyEl.dataset.stateIdx = String(step.idx);
    const handle = document.createElement("button");
    handle.type = "button";
    handle.className = "reorder-handle";
    // Name each handle for its step so a screen reader navigating the gutter
    // controls can tell them apart (otherwise all read identically).
    const label = step.bodyEl.dataset.menuLabel || "this step";
    handle.setAttribute("aria-label", `Reorder ${label}`);
    handle.innerHTML = GRIP;
    step.bodyEl.appendChild(handle);
    wireHandle(handle, step.id, proof, model);
    handles.push(handle);
  }
  // Surface the proof's dependency graph (the rail's Proof scope) so the cone
  // lit during a drag shows the constraints the reorder is respecting.
  const scopeBtn = document.querySelector('.rail-scope[data-scope="proof"]');
  if (scopeBtn) scopeBtn.click();
  reorderState.set(proof, { model, handles });
  announce(`Reorder mode on, ${model.byId.size} steps. Drag a step's handle to reorder it.`);
}

// FLIP: record step positions, run the DOM move, then animate each step from
// where it was to where it landed, so a reorder reads as a glide rather than a
// jump.
function flipMove(model, applyFn) {
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    applyFn();
    return;
  }
  const els = [...model.byId.values()].map((s) => s.bodyEl);
  const before = new Map(els.map((el) => [el, el.getBoundingClientRect().top]));
  applyFn();
  for (const el of els) {
    const dy = before.get(el) - el.getBoundingClientRect().top;
    if (!dy) continue;
    el.style.transition = "transform 0s";
    el.style.transform = `translateY(${dy}px)`;
    requestAnimationFrame(() => {
      el.style.transition = "transform 220ms cubic-bezier(.2,.7,.3,1)";
      el.style.transform = "";
    });
    el.addEventListener(
      "transitionend",
      () => {
        el.style.transition = "";
        el.style.transform = "";
      },
      { once: true }
    );
  }
}

function deactivate(proof) {
  const st = reorderState.get(proof);
  if (!st) return;
  for (const h of st.handles) h.remove();
  reorderState.delete(proof);
  announce("Reorder mode off.");
}

// The sibling bodyEls of `id` (excluding it) in current document order.
function siblingEls(model, id) {
  const step = model.byId.get(id);
  const key = step.parent || "";
  return (model.children.get(key) || [])
    .filter((x) => x !== id)
    .map((x) => model.byId.get(x).bodyEl);
}

// Insertion slot (0..n) under a pointer y, among the sibling els: the number of
// siblings whose vertical center sits above y.
function slotUnderPointer(els, y) {
  let slot = 0;
  for (const el of els) {
    const r = el.getBoundingClientRect();
    if (r.top + r.height / 2 < y) slot++;
  }
  return slot;
}

// A step's printed number ("4", "1.2"), read off its info zone, for naming it
// in the rejection reason. Digits and dots only (drops the ⟨⟩ glyphs).
function stepNum(model, id) {
  const el = model.byId
    .get(id)
    .bodyEl.querySelector(":scope > .hr-info-zone .step-number");
  return el ? el.textContent.replace(/[^0-9.]/g, "") : "";
}

// id and all of its descendant steps (the block that travels with it).
function subtreeIds(model, id) {
  const out = new Set([id]);
  const walk = (k) => {
    for (const c of model.children.get(k) || []) {
      out.add(c);
      walk(c);
    }
  };
  walk(id);
  return out;
}

// Why placing step `id` at sibling `slot` is illegal: the dependency edge it
// would violate. An edge {src, dst} means src uses dst, so dst must precede src;
// the move breaks it when it lands src before dst. Among the broken edges that
// touch the moved block, return the tightest (endpoints closest in the trial
// order) as the single clearest culprit. null if the slot is actually legal.
function blockingEdge(model, id, slot) {
  const step = model.byId.get(id);
  const key = step.parent || "";
  const without = (model.children.get(key) || []).filter((x) => x !== id);
  const trial = new Map(model.children);
  trial.set(key, [...without.slice(0, slot), id, ...without.slice(slot)]);
  const flat = flatten(trial);
  const pos = new Map(flat.map((x, i) => [x, i]));
  const moved = subtreeIds(model, id);
  let best = null;
  for (const e of model.deps) {
    if (pos.get(e.dst) < pos.get(e.src)) continue; // satisfied
    if (!moved.has(e.src) && !moved.has(e.dst)) continue; // unrelated to the move
    const gap = Math.abs(pos.get(e.src) - pos.get(e.dst));
    if (!best || gap < best.gap) best = { e, gap };
  }
  return best ? best.e : null;
}

// "Step 4 uses Step 2": the human reason for a rejected drop.
function reasonText(model, edge) {
  const src = stepNum(model, edge.src);
  const dst = stepNum(model, edge.dst);
  if (!src || !dst) return "That move breaks a dependency.";
  return `Step ${src} uses Step ${dst}`;
}

function wireHandle(handle, id, proof, model) {
  handle.addEventListener("pointerdown", (ev) => {
    ev.preventDefault();
    ev.stopPropagation();
    const step = model.byId.get(id);
    const key = step.parent || "";
    const legal = new Set(legalPositions(model, id));
    const others = siblingEls(model, id);
    const container = step.bodyEl.parentElement;
    const start = (model.children.get(key) || []).indexOf(id);
    const prevPin = model.svg ? model.svg.__pinnedIdx : null;
    let target = start;

    const indicator = document.createElement("div");
    indicator.className = "reorder-indicator";
    // The rejection reason rides the indicator (so it tracks the target slot)
    // but renders in the handrail gutter to its left. Empty/hidden until a slot
    // is illegal.
    const reason = document.createElement("div");
    reason.className = "reorder-reason";
    indicator.appendChild(reason);
    let lastReason = "";
    proof.classList.add("reorder-dragging");
    step.bodyEl.classList.add("reorder-dragged");
    if (model.svg) pinTreeCurrent(model.svg, String(step.idx));

    const place = (slot) => {
      if (slot < others.length) container.insertBefore(indicator, others[slot]);
      else container.appendChild(indicator);
    };
    const onMove = (e) => {
      const slot = slotUnderPointer(others, e.clientY);
      place(slot);
      if (legal.has(slot)) {
        target = slot;
        indicator.classList.remove("illegal");
        reason.textContent = "";
        lastReason = "";
      } else {
        target = start;
        indicator.classList.add("illegal");
        const edge = blockingEdge(model, id, slot);
        const text = edge ? reasonText(model, edge) : "";
        reason.textContent = text;
        lastReason = text;
      }
    };
    const onUp = () => {
      document.removeEventListener("pointermove", onMove);
      document.removeEventListener("pointerup", onUp);
      // lastReason is set only while over an illegal slot and cleared on a legal
      // one, so a non-empty value at drop means the drop itself was rejected.
      const rejected = !!lastReason;
      indicator.remove();
      proof.classList.remove("reorder-dragging");
      step.bodyEl.classList.remove("reorder-dragged");
      if (model.svg) pinTreeCurrent(model.svg, prevPin);
      if (target !== start && legal.has(target)) {
        flipMove(model, () => applyToBody(model, moveTo(model, id, target)));
        // Announce the result so a screen reader perceives the reorder.
        const sib = model.children.get(key) || [];
        const label = step.bodyEl.dataset.menuLabel || "Step";
        announce(`${label} moved to position ${sib.indexOf(id) + 1} of ${sib.length}.`);
      } else if (rejected) {
        // Dropped on an illegal slot: state the blocking dependency for SR too.
        announce(`Move blocked: ${lastReason}.`);
      }
    };
    document.addEventListener("pointermove", onMove);
    document.addEventListener("pointerup", onUp);
  });
}
