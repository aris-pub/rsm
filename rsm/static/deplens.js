// deplens.js
//
// Dependency lens. From a proof step OR a named result (theorem/lemma/...) the
// reader lights its UPSTREAM cone ("what does this rest on?", the prerequisites)
// and/or its DOWNSTREAM cone ("what rests on this?", everything that breaks if
// it is wrong), marked in the prose and echoed in the rail. Unlike the rail's
// hover cone the lens is STICKY (it holds while the reader scrolls and reads the
// marked blocks, the dual of focus mode without the fold), and the two
// directions COMPOSE for one anchor, which is what makes "the argument is an
// architecture, not a sequence" concrete.
//
// Two granularities, one engine:
//   - a STEP reads its per-proof step DAG (the .toc-tree in the proof's rail
//     item), the same graph reorder and focus read;
//   - a RESULT reads a document-level result-dependency graph aggregated from
//     every proof's citation graph (each proof is stamped data-of=<result it
//     proves>, and its rail graph carries a toc-node-result per result it cites,
//     so "R rests on S" iff R's proof cites S). Built once, lazily.
// Everything downstream of the model (marking, the bar, compose, exit, a11y) is
// identical for both, so steps and results get the same treatment.

import { coneOver } from "./tocarcs.js";

// Steps inside a :calc: chain read as one step and are not DAG nodes (mirrors
// reorder.js / proof.py).
const isDagStep = (el) => !el.closest(".calc");
const stepsOf = (proofEl) =>
  [...proofEl.querySelectorAll(".step")].filter(isDagStep);

// Named results that are dependency nodes (mirrors proof.py _is_named_result:
// the theorem family, never definitions/remarks/examples).
const RESULT_SELECTOR =
  ".theorem[id], .lemma[id], .corollary[id], .proposition[id]";
const isResultEl = (el) =>
  el.matches(RESULT_SELECTOR) && !el.classList.contains("definition");

const stepNumber = (st) => {
  const el = st && st.querySelector(":scope > .hr-info-zone .step-number");
  return el ? el.textContent.trim().replace(/[^0-9.]/g, "") : "";
};
const resultLabel = (el) => (el && (el.dataset.menuLabel || el.id)) || "";

const docMapSvg = () =>
  document.querySelector(".rail-doc-map svg.toc-tree");
const railItemForProof = (proof) => {
  const id = proof.dataset.nodeid;
  return id
    ? document.querySelector(`.proof-rail-item[data-proof="${id}"]`)
    : null;
};

function closureMap(adj, start) {
  const seen = new Set([start]);
  const stack = [start];
  while (stack.length) {
    for (const n of adj.get(stack.pop()) || []) {
      if (!seen.has(n)) {
        seen.add(n);
        stack.push(n);
      }
    }
  }
  return seen;
}

// --- result-level graph (aggregated once from the per-proof citation graphs) --
let _resultGraph = null;
function resultGraph() {
  if (_resultGraph) return _resultGraph;
  const results = new Map();
  for (const el of document.querySelectorAll(RESULT_SELECTOR)) {
    if (el.id && !el.classList.contains("definition")) results.set(el.id, el);
  }
  const up = new Map();
  const down = new Map();
  const add = (a, b) => {
    if (a === b || !results.has(a) || !results.has(b)) return;
    if (!up.has(a)) up.set(a, new Set());
    up.get(a).add(b);
    if (!down.has(b)) down.set(b, new Set());
    down.get(b).add(a);
  };
  for (const proof of document.querySelectorAll(".proof[data-of]")) {
    const r = proof.dataset.of;
    if (!results.has(r)) continue;
    const item = railItemForProof(proof);
    if (item) {
      for (const node of item.querySelectorAll("a.toc-node.toc-node-result")) {
        const href = node.getAttribute("href") || "";
        if (href.startsWith("#")) add(r, href.slice(1));
      }
    }
    // Belt and suspenders: result citations made directly in the proof prose.
    for (const a of proof.querySelectorAll('a[href^="#"]')) {
      add(r, a.getAttribute("href").slice(1));
    }
  }
  // Citations in a result's own statement (e.g. a corollary "by Theorem X").
  for (const [id, el] of results) {
    for (const a of el.querySelectorAll('a[href^="#"]')) {
      add(id, a.getAttribute("href").slice(1));
    }
  }
  _resultGraph = { results, up, down };
  return _resultGraph;
}

// --- models --------------------------------------------------------------
// A model exposes: units [{key, bodyEl}], anchorKey, coneUp()/coneDown()
// (transitive sets of unit keys excluding the anchor), railSvg, applyRail(),
// and label/noun for the bar and announcements.

function stepModel(step) {
  const proofEl = step.closest(".proof[data-nodeid]");
  if (!proofEl) return null;
  const rail = document.querySelector(".proof-rail");
  if (!rail) return null;
  const railItem = rail.querySelector(
    `.proof-rail-item[data-proof="${proofEl.dataset.nodeid}"]`,
  );
  const svg = railItem && railItem.querySelector("svg.toc-tree");
  if (!svg) return null;
  const steps = stepsOf(proofEl);
  const idx = steps.indexOf(step);
  if (idx < 0) return null;
  const lim = steps.length;
  const toIdx = (raw) => {
    const out = new Set();
    for (const s of raw) {
      const i = Number(s);
      if (i !== idx && i >= 0 && i < lim) out.add(String(i));
    }
    return out;
  };
  return {
    units: steps.map((bodyEl, i) => ({ key: String(i), bodyEl })),
    anchorKey: String(idx),
    coneUp: () => toIdx(coneOver(svg, idx, "up")),
    coneDown: () => toIdx(coneOver(svg, idx, "down")),
    railSvg: svg,
    scope: "proof",
    applyRail: (up, down, upActive) =>
      applyGraphRail(svg, up, down, String(idx), upActive, (n) => n.dataset.idx),
    label: (k) => `Step ${stepNumber(steps[Number(k)]) || Number(k) + 1}`,
    noun: "step",
  };
}

function resultModel(el) {
  const g = resultGraph();
  if (!g.results.has(el.id)) return null;
  const exclude = (set, k) => {
    const out = new Set(set);
    out.delete(k);
    return out;
  };
  // Map a cone of result ids to the doc-map section nodes that contain them, so
  // the section TOC echoes the result-level lens (the rail has no result graph).
  const sectionOf = (id) => {
    const r = g.results.get(id);
    const sec = r && r.closest("section, .section");
    return sec ? sec.id : null;
  };
  return {
    units: [...g.results].map(([key, bodyEl]) => ({ key, bodyEl })),
    anchorKey: el.id,
    coneUp: () => exclude(closureMap(g.up, el.id), el.id),
    coneDown: () => exclude(closureMap(g.down, el.id), el.id),
    railSvg: docMapSvg(),
    scope: "document",
    applyRail: (up, down, upActive) => {
      const svg = docMapSvg();
      if (!svg) return;
      const upSecs = new Set([...up].map(sectionOf).filter(Boolean));
      const downSecs = new Set([...down].map(sectionOf).filter(Boolean));
      const anchorSec = sectionOf(el.id);
      applyGraphRail(
        svg,
        upSecs,
        downSecs,
        anchorSec,
        upActive,
        (node) => {
          const h = node.getAttribute("href") || "";
          return h.startsWith("#") ? h.slice(1) : null;
        },
      );
    },
    label: () => resultLabel(el),
    noun: "result",
  };
}

function buildModel(anchorEl) {
  if (!anchorEl) return null;
  if (anchorEl.classList.contains("step") && !anchorEl.closest(".calc")) {
    return stepModel(anchorEl);
  }
  if (isResultEl(anchorEl)) return resultModel(anchorEl);
  return null;
}

// Shared rail painter for a .toc-tree. keyOf(node) returns the cone key a node
// belongs to (its data-idx for the step graph, its href section id for the doc
// map). Edges are keyed by data-from/data-to (idx strings): they light only when
// those keys are themselves cone keys, which holds for the step graph; the doc
// map's edges use section indices and stay unlit, which is the intended quiet
// section echo.
function applyGraphRail(svg, up, down, anchorKey, upActive, keyOf) {
  for (const n of svg.querySelectorAll(".toc-node")) {
    const k = keyOf(n);
    const isAnchor = k != null && k === anchorKey;
    const isUp = k != null && up.has(k);
    const isDown = k != null && down.has(k);
    n.classList.toggle("deplens-anchor", isAnchor);
    n.classList.toggle("deplens-up", isUp && !isAnchor);
    n.classList.toggle("deplens-down", isDown && !isAnchor);
    n.classList.toggle("deplens-faded", upActive && !isAnchor && !isUp && !isDown);
  }
  const upSet = new Set([...up, anchorKey]);
  const downSet = new Set([...down, anchorKey]);
  for (const e of svg.querySelectorAll(".toc-edge")) {
    const fwd = e.classList.contains("fwd");
    const f = e.dataset.from;
    const t = e.dataset.to;
    const isUp = !fwd && up.size && upSet.has(f) && upSet.has(t);
    const isDown = !fwd && down.size && downSet.has(f) && downSet.has(t);
    e.classList.toggle("deplens-up", !!isUp);
    e.classList.toggle("deplens-down", !!isDown);
    e.classList.toggle("deplens-faded", upActive && !isUp && !isDown);
  }
}

const MARK_CLASSES = [
  "deplens-anchor",
  "deplens-up",
  "deplens-down",
  "deplens-faded",
];

export function lensConeSizes(anchorEl) {
  const m = buildModel(anchorEl);
  if (!m) return { up: 0, down: 0 };
  return { up: m.coneUp().size, down: m.coneDown().size };
}

export function setup(root = document) {
  const rail = root.querySelector(".proof-rail");
  let active = null; // { model, anchorEl, dirs:Set }

  let liveRegion = null;
  function announce(msg) {
    if (!liveRegion) {
      liveRegion = document.createElement("div");
      liveRegion.className = "deplens-sr-status";
      liveRegion.setAttribute("role", "status");
      liveRegion.setAttribute("aria-live", "polite");
      document.body.appendChild(liveRegion);
    }
    liveRegion.textContent = "";
    requestAnimationFrame(() => {
      liveRegion.textContent = msg;
    });
  }

  // Surface the rail scope whose graph echoes this lens: a step's proof map, or
  // a result's document map.
  function showRail(model) {
    if (!rail) return;
    const scopeBtn = rail.querySelector(
      `.rail-scope[data-scope="${model.scope}"]`,
    );
    if (scopeBtn) scopeBtn.click();
    if (model.scope === "proof") {
      const mapTab = rail.querySelector(
        '.rail-subtabs-proof .rail-tab[data-view="proof-map"]',
      );
      if (mapTab && !mapTab.classList.contains("active")) mapTab.click();
    }
  }

  function clearMarks() {
    if (!active) return;
    for (const u of active.model.units) u.bodyEl.classList.remove(...MARK_CLASSES);
    const svg = active.model.railSvg;
    if (svg) {
      svg
        .querySelectorAll("." + MARK_CLASSES.join(", ."))
        .forEach((x) => x.classList.remove(...MARK_CLASSES));
    }
  }

  function applyMarks() {
    const { model, dirs } = active;
    const upActive = dirs.has("up");
    const up = upActive ? model.coneUp() : new Set();
    const down = dirs.has("down") ? model.coneDown() : new Set();
    for (const u of model.units) {
      const isAnchor = u.key === model.anchorKey;
      const isUp = up.has(u.key);
      const isDown = down.has(u.key);
      u.bodyEl.classList.toggle("deplens-anchor", isAnchor);
      u.bodyEl.classList.toggle("deplens-up", isUp);
      u.bodyEl.classList.toggle("deplens-down", isDown);
      u.bodyEl.classList.toggle(
        "deplens-faded",
        upActive && !isAnchor && !isUp && !isDown,
      );
    }
    model.applyRail(up, down, upActive);
  }

  let bar = null;
  function setBar() {
    if (!rail) return;
    const { model, dirs } = active;
    const upN = dirs.has("up") ? model.coneUp().size : 0;
    const downN = dirs.has("down") ? model.coneDown().size : 0;
    const sizes = { up: model.coneUp().size, down: model.coneDown().size };
    const other =
      dirs.has("up") && !dirs.has("down") && sizes.down > 0
        ? "down"
        : dirs.has("down") && !dirs.has("up") && sizes.up > 0
        ? "up"
        : null;

    if (!bar) {
      bar = document.createElement("div");
      bar.className = "deplens-bar";
      bar.setAttribute("role", "status");
    }
    const noun = model.noun;
    const parts = [];
    if (upN) parts.push(`${upN} ${noun}${upN === 1 ? "" : "s"} it rests on`);
    if (downN) parts.push(`${downN} rest on it`);
    // A fixed pill (appended to body, not the rail) so the active state and how
    // to dismiss it stay visible wherever the reader has scrolled.
    bar.innerHTML =
      '<span class="deplens-bar-badge">Dependency lens</span>' +
      `<span class="deplens-bar-label">${model.label(model.anchorKey)}` +
      ` · ${parts.join(", ")}</span>` +
      (other
        ? `<span class="deplens-add" role="button" tabindex="0" data-dir="${other}">` +
          `${other === "up" ? "Also: what it rests on" : "Also: what rests on it"}</span>`
        : "") +
      '<span class="deplens-exit" role="button" tabindex="0" aria-label="Clear dependency lens">' +
      '<kbd class="deplens-kbd">Esc</kbd> Clear ' +
      '<span class="deplens-exit-x" aria-hidden="true">×</span></span>';

    bar.querySelector(".deplens-exit").onclick = exit;
    const add = bar.querySelector(".deplens-add");
    if (add) add.onclick = () => toggleDir(add.dataset.dir);
    bar.onkeydown = (ev) => {
      if (ev.key !== "Enter" && ev.key !== " ") return;
      const t = ev.target.closest(".deplens-exit, .deplens-add");
      if (!t) return;
      ev.preventDefault();
      if (t.classList.contains("deplens-exit")) exit();
      else toggleDir(t.dataset.dir);
    };
    if (!bar.isConnected) document.body.appendChild(bar);
    if (rail) rail.classList.add("deplensing");
  }

  function render() {
    applyMarks();
    setBar();
    const { model, dirs } = active;
    const label = model.label(model.anchorKey);
    const upN = dirs.has("up") ? model.coneUp().size : 0;
    const downN = dirs.has("down") ? model.coneDown().size : 0;
    const noun = model.noun;
    let msg;
    if (upN && downN) {
      msg =
        `Showing ${label}'s dependencies: the ${upN} ${noun}s it rests on and ` +
        `the ${downN} that rest on it. Press Escape to clear.`;
    } else if (upN) {
      msg = `Showing the ${upN} ${noun}s that ${label} rests on. Press Escape to clear.`;
    } else {
      msg = `Showing the ${downN} ${noun}s that rest on ${label}. Press Escape to clear.`;
    }
    announce(msg);
  }

  function teardown() {
    if (!active) return;
    clearMarks();
    if (bar) bar.remove();
    if (rail) rail.classList.remove("deplensing");
    document.removeEventListener("keydown", onKeydown);
    document.removeEventListener("click", onClickAway, true);
    active = null;
  }

  function exit() {
    if (!active) return;
    teardown();
    announce("Dependency lens cleared.");
  }

  function onKeydown(ev) {
    if (ev.key === "Escape") exit();
  }

  function onClickAway(ev) {
    if (!active) return;
    const t = ev.target;
    if (!t.closest) return;
    if (
      t.closest(".deplens-bar") ||
      t.closest(".proof-rail") ||
      t.closest("#hr-menu-singleton") ||
      active.anchorEl.contains(t) ||
      active.model.units.some((u) => u.bodyEl.contains(t))
    ) {
      return;
    }
    exit();
  }

  function toggleDir(dir) {
    if (!active) return;
    clearMarks();
    if (active.dirs.has(dir)) active.dirs.delete(dir);
    else active.dirs.add(dir);
    if (!active.dirs.size) {
      exit();
      return;
    }
    render();
  }

  function show(anchorEl, dir) {
    const model = buildModel(anchorEl);
    if (!model) return;
    if (active && active.anchorEl === anchorEl) {
      toggleDir(dir);
      return;
    }
    teardown();
    active = { model, anchorEl, dirs: new Set([dir]) };
    showRail(model);
    render();
    document.addEventListener("keydown", onKeydown);
    document.addEventListener("click", onClickAway, true);
    document.dispatchEvent(new CustomEvent("rsm:focus-enter"));
  }

  root.addEventListener("deplens:show", (ev) => {
    const anchor =
      ev.target.closest &&
      ev.target.closest(".step, " + RESULT_SELECTOR);
    if (!anchor) return;
    const dir = ev.detail && ev.detail.direction;
    if (dir !== "up" && dir !== "down") return;
    show(anchor, dir);
  });
}
