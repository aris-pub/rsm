// prooftree.js
//
// Floating sidebar with two scopes:
//   Document - the whole-paper TOC tree, and the Notation panel
//   Proof    - the step-dependency tree and live State of the proof in view
// Both DAGs are pre-rendered SVGs (laid out at build time); this module routes
// scope/sub-tab clicks, auto-follows the proof you are reading, handles the
// collapse control, and remembers your layout in localStorage.

import { wireTree } from "./tocarcs.js";
import { openHandrail } from "./handrails.js";
import { createTooltips } from "./tooltips.js";
import { reRenderAll } from "./notation.js";

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
      scope: rail.querySelector(".rail-scope.active")?.dataset.scope || "document",
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
      const on = s.dataset.scope === scope;
      s.classList.toggle("active", on);
      s.setAttribute("aria-pressed", String(on));
    }
    rail.classList.toggle("scope-document", scope === "document");
    rail.classList.toggle("scope-proof", scope === "proof");
    rail.classList.toggle("scope-reading", scope === "reading");
  }

  function selectTab(tab) {
    const row = tab.closest(".rail-subtabs");
    for (const t of row.querySelectorAll(".rail-tab")) {
      t.classList.toggle("active", t === tab);
      t.setAttribute("aria-pressed", String(t === tab));
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

  // ---- reading controls (typeface, size, line height, width, theme) ----
  // Each button sets a root data-reading-* attribute (or the dark-theme class)
  // and persists it; the inline boot script pre-applies them before first paint.
  const READING_KEY = "rsm-reading";
  function readReadingPrefs() {
    try {
      return JSON.parse(localStorage.getItem(READING_KEY) || "{}") || {};
    } catch (e) {
      return {};
    }
  }
  function applyReading(control, value) {
    const el = document.documentElement;
    if (control === "theme") el.classList.toggle("dark-theme", value === "dark");
    else el.setAttribute("data-reading-" + control, value);
  }
  const readingPanel = rail.querySelector(".rail-reading");
  if (readingPanel) {
    readingPanel.addEventListener("click", (ev) => {
      const btn = ev.target.closest(".reading-opt");
      if (!btn) return;
      const row = btn.closest(".reading-row");
      const control = row.dataset.control;
      for (const o of row.querySelectorAll(".reading-opt")) {
        const on = o === btn;
        o.classList.toggle("active", on);
        o.setAttribute("aria-pressed", String(on));
      }
      applyReading(control, btn.dataset.value);
      const prefs = readReadingPrefs();
      prefs[control] = btn.dataset.value;
      try {
        localStorage.setItem(READING_KEY, JSON.stringify(prefs));
      } catch (e) {
        /* localStorage unavailable; preference stays session-only */
      }
    });
    // Apply saved prefs (idempotent with the boot script) and sync the buttons.
    const prefs = readReadingPrefs();
    for (const row of readingPanel.querySelectorAll(".reading-row")) {
      const value = prefs[row.dataset.control];
      if (!value) continue;
      applyReading(row.dataset.control, value);
      for (const o of row.querySelectorAll(".reading-opt")) {
        const on = o.dataset.value === value;
        o.classList.toggle("active", on);
        o.setAttribute("aria-pressed", String(on));
      }
    }
  }

  // Restore a previously saved layout.
  try {
    const saved = JSON.parse(localStorage.getItem(lsKey) || "null");
    if (saved) {
      selectScope(saved.scope || "document");
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

  function proofElFor(key) {
    return key ? root.querySelector(`.proof[data-nodeid="${key}"]`) : null;
  }
  // Mirror the body: when the followed proof is collapsed, CSS swaps its step
  // graph for a single-node card so the rail never shows steps the page hides.
  function updateCollapsedClass() {
    const el = proofElFor(current);
    rail.classList.toggle(
      "proof-collapsed",
      !!(el && el.classList.contains("hr-collapsed")),
    );
  }

  function show(key) {
    if (!items.has(key)) key = null;
    if (key === current) return;
    current = key;
    for (const [k, item] of items) item.classList.toggle("shown", k === key);
    // Outside any proof the Proof scope has nothing live to show; CSS uses this
    // to present an empty state rather than a blank panel.
    rail.classList.toggle("no-proof", key === null);
    updateCollapsedClass();
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

  // The body's collapse control flips the rail between the step graph and the
  // single-node card; the card flips it back by expanding the proof in place
  // and scrolling to it (never a silent off-screen body change).
  document.addEventListener("rsm:handrail-toggle", (ev) => {
    const hr = ev.detail && ev.detail.hr;
    if (hr && hr.matches && hr.matches(".proof[data-nodeid]")) {
      updateCollapsedClass();
      updateState();
    }
  });
  rail.addEventListener("click", (ev) => {
    const btn = ev.target.closest(".rail-expand-proof");
    if (!btn) return;
    const el = proofElFor(btn.dataset.proof);
    if (!el) return;
    openHandrail(el);
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  });

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
    // cloneNode copies tooltipster's marker class but not its instance, leaving
    // dead links the re-init would skip. Clear it so createTooltips() rebinds
    // the cloned references to the same body tooltip.
    c.classList.remove("tooltipstered");
    c.querySelectorAll(".tooltipstered").forEach((n) =>
      n.classList.remove("tooltipstered"),
    );
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

  // Collapse state for the State panel's bands, keyed by proof+role, so a
  // reader's collapse choice survives the panel's re-render on scroll.
  const collapseState = {};

  // Render the State view for the shown proof at the current step. Order is
  // PROVE -> ASSUME -> IN SCOPE: the goal first (what the reader most needs),
  // then the proof's own hypotheses, then document-wide context. Each is a
  // labeled, collapsible band; math is cloned from the body and re-typeset.
  function renderState() {
    if (proofView !== "state") return;
    const item = current ? items.get(current) : null;
    if (!item) return;
    const panel = item.querySelector(".rail-state");
    if (!panel) return;
    panel.setAttribute("aria-live", "polite");
    const data = stateData.get(item.dataset.proof);
    if (!data || active.idx < 0 || active.idx >= data.length) {
      panel.innerHTML =
        '<div class="rail-state-empty">Scroll into a proof to see its live hypotheses and current goal.</div>';
      return;
    }
    const st = data[active.idx];
    const proofKey = item.dataset.proof;
    panel.innerHTML = "";

    // A labeled, collapsible band. The header is a real button (keyboard- and
    // screen-reader-operable); collapse state persists across re-renders.
    function makeBlock(role, label, defaultCollapsed) {
      const key = proofKey + ":" + role;
      const collapsed = key in collapseState ? collapseState[key] : defaultCollapsed;
      const block = document.createElement("div");
      block.className = "rail-state-block rail-" + role + (collapsed ? " collapsed" : "");
      block.setAttribute("role", "group");
      block.setAttribute("aria-label", label);
      const head = document.createElement("button");
      head.type = "button";
      head.className = "rail-state-head";
      head.setAttribute("aria-expanded", String(!collapsed));
      head.innerHTML =
        '<span class="rail-state-label">' + label + "</span>" +
        '<span class="rail-state-caret" aria-hidden="true"></span>';
      const body = document.createElement("div");
      body.className = "rail-state-body";
      head.addEventListener("click", () => {
        const nowCollapsed = !block.classList.contains("collapsed");
        block.classList.toggle("collapsed", nowCollapsed);
        head.setAttribute("aria-expanded", String(!nowCollapsed));
        collapseState[key] = nowCollapsed;
      });
      block.appendChild(head);
      block.appendChild(body);
      return { block, body };
    }

    // A chip marking where something came from; clicking jumps to it in the body.
    function badge(text, targetId, tip) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "rail-step-badge";
      b.textContent = "⟨" + text + "⟩";
      if (tip) b.setAttribute("data-tooltip", tip);
      if (targetId != null) {
        b.addEventListener("click", () => {
          const t = root.querySelector('[data-nodeid="' + targetId + '"]');
          if (t) t.scrollIntoView({ block: "center", behavior: "smooth" });
        });
      }
      return b;
    }

    // PROVE first.
    const goalB = makeBlock("goal", "Prove", false);
    const g = st.goal;
    const goalEl = g && g.id != null ? root.querySelector('[data-nodeid="' + g.id + '"]') : null;
    if (goalEl && g.thm) {
      // A setup step's goal is the whole theorem: show a one-line chip and tuck
      // the full statement behind an inline disclosure.
      const summary = document.createElement("div");
      summary.className = "rail-goal-summary";
      if (g.num) summary.appendChild(badge(g.num, g.id, "jump to " + g.num));
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "rail-goal-toggle";
      toggle.textContent = "show statement";
      summary.appendChild(toggle);
      goalB.body.appendChild(summary);
      const full = document.createElement("div");
      full.className = "rail-goal-full collapsed";
      const cz = goalEl.querySelector(":scope > .hr-content-zone") || goalEl;
      const clone = cloneClean(cz);
      clone
        .querySelectorAll(".hr-label, .construct.let, .construct.assume")
        .forEach((n) => n.remove());
      full.appendChild(clone);
      goalB.body.appendChild(full);
      toggle.addEventListener("click", () => {
        const hidden = full.classList.toggle("collapsed");
        toggle.textContent = hidden ? "show statement" : "hide statement";
      });
    } else if (goalEl) {
      const gbody = document.createElement("div");
      gbody.className = "rail-goal-body";
      if (g.num) gbody.appendChild(badge(g.num, g.id, "introduced in step " + g.num));
      gbody.appendChild(cloneClean(goalEl));
      goalB.body.appendChild(gbody);
    } else {
      goalB.body.textContent = "the main result";
    }
    panel.appendChild(goalB.block);

    // ASSUME: the proof's own hypotheses, with a ⟨n⟩ chip on the first of each
    // run of same-step introductions (consecutive same-step rows share a chip).
    const hyps = (st.hyps || [])
      .map((h) => ({ el: root.querySelector('[data-nodeid="' + h.id + '"]'), num: h.num, id: h.id }))
      .filter((h) => h.el);
    const hypB = makeBlock("hyps", "Assume", false);
    const ul = document.createElement("ul");
    if (hyps.length) {
      let prev = null;
      for (const h of hyps) {
        const li = document.createElement("li");
        if (h.num && h.num !== prev) {
          li.appendChild(badge(h.num, h.id, "introduced in step " + h.num));
        } else {
          li.classList.add("rail-hyp-cont");
        }
        li.appendChild(cloneClean(h.el));
        ul.appendChild(li);
        prev = h.num;
      }
    } else {
      const li = document.createElement("li");
      li.className = "rail-hyp-empty";
      li.textContent = "no assumptions yet";
      ul.appendChild(li);
    }
    hypB.body.appendChild(ul);
    panel.appendChild(hypB.block);

    // IN SCOPE: document-wide introductions (prose + definitions), reference
    // material, collapsed by default once there are more than a few.
    const ctx = (st.context || [])
      .map((c) => ({ el: root.querySelector('[data-nodeid="' + c.id + '"]') }))
      .filter((c) => c.el);
    if (ctx.length) {
      const ctxB = makeBlock("context", "In scope", ctx.length > 4);
      const cul = document.createElement("ul");
      for (const c of ctx) {
        const li = document.createElement("li");
        li.appendChild(cloneClean(c.el));
        cul.appendChild(li);
      }
      ctxB.body.appendChild(cul);
      panel.appendChild(ctxB.block);
    }

    // Cloned fragments can carry un-typeset math (raw \(...\)); re-render every
    // math element in the panel from its stored data-latex.
    reRenderAll(panel);
    // Cloned references carry no live tooltip, and the chips carry a
    // data-tooltip; bind both with the body's initializer (idempotent).
    createTooltips();
  }
}
