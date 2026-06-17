// prooftree.js
//
// Floating sidebar with two scopes:
//   Document - the whole-paper TOC tree, and the Notation panel
//   Proof    - the step-dependency tree and live State of the proof in view
// Both DAGs are pre-rendered SVGs (laid out at build time); this module routes
// scope/sub-tab clicks, auto-follows the proof you are reading, handles the
// collapse control, and remembers your layout in localStorage.

import { wireTree } from "./tocarcs.js";

export function setup(root = document) {
  const rail = root.querySelector(".proof-rail");
  if (!rail) return;

  const lsKey = "rsm-sidebar:" + location.pathname;

  // Wire hover behavior on every pre-rendered tree (the TOC and each proof).
  rail.querySelectorAll("svg.toc-tree").forEach((svg) => {
    if (!svg.dataset.wired) {
      svg.dataset.wired = "1";
      wireTree(svg);
    }
  });

  // Per-proof items live under the Proof scope; the TOC is a Document panel.
  const items = new Map();
  for (const item of rail.querySelectorAll(".rail-proof .proof-rail-item")) {
    items.set(item.dataset.proof, item);
  }
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

  // State, declared up front so early calls (restore, show) never hit the TDZ.
  let proofView = rail.classList.contains("proof-view-state") ? "state" : "map";
  // data-proof of the proof in view, or null outside one. Starts undefined so
  // the first show(null) actually runs (and sets the no-proof state).
  let current;
  let currentNode = null;
  const active = { idx: -1 };

  rail.classList.add("active");

  // ---- layout: scope, sub-tabs, collapse (persisted) ----

  // Map a sub-tab button to the rail class that selects its panel. The class is
  // scoped (doc-view-* vs proof-view-*) so Document and Proof can both have a
  // "map" sub-tab without colliding.
  function railClassFor(tab) {
    const inDoc = !!tab.closest(".rail-subtabs-document");
    const suffix = tab.dataset.view.replace(/^(doc|proof)-/, "");
    return (inDoc ? "doc-view-" : "proof-view-") + suffix;
  }

  function saveLayout() {
    const layout = {
      scope: rail.classList.contains("scope-proof") ? "proof" : "document",
      docView: rail.classList.contains("doc-view-notation") ? "notation" : "doc-map",
      proofView: rail.classList.contains("proof-view-state") ? "state" : "proof-map",
      collapsed: rail.classList.contains("collapsed"),
    };
    try {
      localStorage.setItem(lsKey, JSON.stringify(layout));
    } catch (e) {
      /* localStorage unavailable; layout stays session-only */
    }
  }

  function selectScope(scope) {
    for (const s of rail.querySelectorAll(".rail-scope")) {
      s.classList.toggle("active", s.dataset.scope === scope);
    }
    rail.classList.toggle("scope-document", scope === "document");
    rail.classList.toggle("scope-proof", scope === "proof");
  }

  function selectTab(tab) {
    const row = tab.closest(".rail-subtabs");
    for (const t of row.querySelectorAll(".rail-tab")) {
      t.classList.toggle("active", t === tab);
      rail.classList.remove(railClassFor(t));
    }
    rail.classList.add(railClassFor(tab));
    if (row.classList.contains("rail-subtabs-proof")) {
      proofView = tab.dataset.view === "state" ? "state" : "map";
      renderState();
    }
  }

  const scopeRow = rail.querySelector(".rail-scopes");
  if (scopeRow) {
    scopeRow.addEventListener("click", (ev) => {
      const s = ev.target.closest(".rail-scope");
      if (!s) return;
      selectScope(s.dataset.scope);
      saveLayout();
    });
  }
  for (const row of rail.querySelectorAll(".rail-subtabs")) {
    row.addEventListener("click", (ev) => {
      const t = ev.target.closest(".rail-tab");
      if (!t) return;
      selectTab(t);
      saveLayout();
    });
  }
  const collapseBtn = rail.querySelector(".rail-collapse");
  if (collapseBtn) {
    collapseBtn.addEventListener("click", () => {
      rail.classList.toggle("collapsed");
      saveLayout();
    });
  }

  // Restore a previously saved layout.
  try {
    const saved = JSON.parse(localStorage.getItem(lsKey) || "null");
    if (saved) {
      selectScope(saved.scope === "proof" ? "proof" : "document");
      const docTab = rail.querySelector(
        `.rail-subtabs-document .rail-tab[data-view="${saved.docView}"]`,
      );
      if (docTab) selectTab(docTab);
      const proofTab = rail.querySelector(
        `.rail-subtabs-proof .rail-tab[data-view="${saved.proofView}"]`,
      );
      if (proofTab) selectTab(proofTab);
      rail.classList.toggle("collapsed", !!saved.collapsed);
    }
  } catch (e) {
    /* ignore malformed saved layout */
  }

  // ---- proof auto-follow ----

  const proofs = [...root.querySelectorAll(".proof[data-nodeid]")];

  function show(key) {
    if (!items.has(key)) key = null;
    if (key === current) return;
    current = key;
    for (const [k, item] of items) item.classList.toggle("shown", k === key);
    // Outside any proof the Proof scope has nothing live to show; CSS uses this
    // to present an empty state rather than a blank panel.
    rail.classList.toggle("no-proof", key === null);
    updateState();
  }
  show(null);

  if (proofs.length) {
    // The active proof is the one whose box is highest while still overlapping
    // the reading band near the top of the viewport.
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
        show(best ? best.getAttribute("data-nodeid") : null);
      },
      { rootMargin: "-12% 0px -55% 0px", threshold: 0 },
    );
    for (const p of proofs) observer.observe(p);
  }

  // ---- active-step tracking + State view ----

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
    // read, and in a gap between steps the last one passed.
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
    if (current) {
      const proofEl = root.querySelector(`.proof[data-nodeid="${current}"]`);
      if (proofEl) {
        idx = currentStepOf(proofEl);
        // Above the first step the proof's opening still shows step 1's state,
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
    // handrail (its offset zones also overflow the narrow rail).
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
  // typeset.
  function renderState() {
    if (proofView !== "state") return;
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
        const cz = goalEl.querySelector(":scope > .hr-content-zone") || goalEl;
        const clone = cloneClean(cz);
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
