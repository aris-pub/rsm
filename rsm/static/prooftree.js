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

  // Per-proof "State" data: data-proof -> [{goal, hyps}, ...] indexed by step.
  const stateData = new Map();
  for (const [key, item] of items) {
    const sd = item.querySelector(".rail-state-data");
    if (sd) {
      try {
        stateData.set(key, JSON.parse(sd.textContent));
      } catch (e) {
        /* ignore malformed */
      }
    }
  }

  let view = rail.classList.contains("view-state") ? "state" : "map";
  const active = { idx: -1 };
  let currentNode = null;
  const tabs = rail.querySelector(".rail-tabs");
  if (tabs) {
    tabs.addEventListener("click", (ev) => {
      const t = ev.target.closest(".rail-tab");
      if (!t) return;
      view = t.dataset.view;
      for (const b of tabs.querySelectorAll(".rail-tab")) b.classList.toggle("active", b === t);
      rail.classList.toggle("view-map", view === "map");
      rail.classList.toggle("view-state", view === "state");
      renderState();
    });
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
    updateState();
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
  function setCurrentNode(node) {
    if (node === currentNode) return;
    if (currentNode) currentNode.classList.remove("current-step");
    currentNode = node;
    if (node) node.classList.add("current-step");
  }
  function setActiveIdx(idx) {
    if (idx === active.idx) return;
    active.idx = idx;
    renderState();
  }
  function currentStepOf(proofEl) {
    // The deepest step whose top has passed the viewport center: the step being
    // read, and in a gap between steps the last one passed. Never nothing while
    // a step is above the center.
    const center = window.innerHeight / 2;
    let best = -1;
    let bestTop = -Infinity;
    proofEl.querySelectorAll(".step").forEach((s, i) => {
      const top = s.getBoundingClientRect().top;
      if (top <= center && top > bestTop) {
        bestTop = top;
        best = i;
      }
    });
    return best;
  }
  function updateState() {
    if (rail.classList.contains("focusing")) {
      setCurrentNode(null);
      return;
    }
    let idx = -1;
    if (current && current !== "toc") {
      const proofEl = root.querySelector(`.proof[data-nodeid="${current}"]`);
      if (proofEl) {
        idx = currentStepOf(proofEl);
        // Above the first step (the proof's opening) still shows step 1's state,
        // so the rail is never empty while you are inside a proof.
        if (idx < 0) idx = 0;
      }
    }
    setActiveIdx(idx);
    const item = current ? items.get(current) : null;
    setCurrentNode(
      item && idx >= 0 ? item.querySelector(`.toc-node[data-idx="${idx}"]`) : null,
    );
  }

  // Recompute the current step whenever a step boundary crosses the center.
  const stepObserver = new IntersectionObserver(() => updateState(), {
    rootMargin: "-50% 0px -50% 0px",
    threshold: 0,
  });
  for (const s of root.querySelectorAll(".proof[data-nodeid] .step")) {
    stepObserver.observe(s);
  }

  function cloneClean(el) {
    const c = el.cloneNode(true);
    c.removeAttribute("id");
    c.removeAttribute("data-nodeid");
    c.querySelectorAll("[id],[data-nodeid]").forEach((n) => {
      n.removeAttribute("id");
      n.removeAttribute("data-nodeid");
    });
    // Strip handrail scaffolding so the clone reads as plain prose, not a mini
    // handrail (its offset zones also overflow the narrow rail and force a
    // scrollbar).
    c.querySelectorAll(
      ".hr-collapse-zone,.hr-menu-zone,.hr-border-zone,.hr-spacer-zone,.hr-info-zone",
    ).forEach((n) => n.remove());
    c.querySelectorAll(".hr").forEach((n) =>
      n.classList.remove("hr", "hr-offset", "hr-labeled", "hr-hidden"),
    );
    return c;
  }

  // Render the State view for the shown proof at the current step: the live
  // hypotheses and the goal, cloned from the body so their math is already
  // typeset. The body element comes before the hidden source copy, so a
  // first-match lookup by nodeid returns the real one.
  function renderState() {
    if (view !== "state") return;
    const item = current ? items.get(current) : null;
    if (!item) return;
    const panel = item.querySelector(".rail-state");
    if (!panel) return;
    const data = stateData.get(item.dataset.proof);
    if (!data || active.idx < 0 || active.idx >= data.length) {
      panel.innerHTML =
        '<div class="rail-state-empty">Scroll into a proof to see its live hypotheses and current goal.</div>';
      return;
    }
    const st = data[active.idx];
    panel.innerHTML = "";

    function badge(num) {
      const b = document.createElement("span");
      b.className = "rail-step-badge";
      b.textContent = "⟨" + num + "⟩"; // the step it comes from
      return b;
    }

    // Assuming: always shown, with an explicit empty list when there's nothing.
    const hyps = (st.hyps || [])
      .map((h) => ({ el: root.querySelector(`[data-nodeid="${h.id}"]`), num: h.num }))
      .filter((h) => h.el);
    const hblock = document.createElement("div");
    hblock.className = "rail-state-block rail-hyps";
    hblock.innerHTML = '<div class="rail-state-label">Assuming</div>';
    const ul = document.createElement("ul");
    if (hyps.length) {
      for (const h of hyps) {
        const li = document.createElement("li");
        if (h.num) li.appendChild(badge(h.num));
        li.appendChild(cloneClean(h.el));
        ul.appendChild(li);
      }
    } else {
      const li = document.createElement("li");
      li.className = "rail-hyp-empty";
      li.textContent = "no assumptions yet";
      ul.appendChild(li);
    }
    hblock.appendChild(ul);
    panel.appendChild(hblock);

    // To show: the step's goal, or the theorem's conclusion for setup steps.
    const goalBlock = document.createElement("div");
    goalBlock.className = "rail-state-block rail-goal";
    goalBlock.innerHTML = '<div class="rail-state-label">To show</div>';
    const body = document.createElement("div");
    body.className = "rail-goal-body";
    const g = st.goal;
    const goalEl = g && g.id != null ? root.querySelector(`[data-nodeid="${g.id}"]`) : null;
    if (goalEl) {
      if (g.num) body.appendChild(badge(g.num));
      if (g.thm) {
        // theorem block: show its statement minus the hypotheses already listed
        const cz = goalEl.querySelector(":scope > .hr-content-zone") || goalEl;
        const clone = cloneClean(cz);
        // drop the title label and the hypotheses already shown above; keep the
        // theorem's conclusion as the goal.
        clone
          .querySelectorAll(".hr-label, .construct.let, .construct.assume")
          .forEach((n) => n.remove());
        body.appendChild(clone);
      } else {
        body.appendChild(cloneClean(goalEl));
      }
    } else {
      body.textContent = "the main result";
    }
    goalBlock.appendChild(body);
    panel.appendChild(goalBlock);
  }
}
