// prooftree.js
//
// Floating sidebar with two scopes:
//   Document - the whole-paper TOC tree, and the Notation panel
//   Proof    - the step-dependency tree and live State of the proof in view
// Both DAGs are pre-rendered SVGs (laid out at build time); this module routes
// scope/sub-tab clicks, auto-follows the proof you are reading, handles the
// collapse control, and remembers your layout in localStorage.

import { wireTree, pinTreeCurrent } from "./tocarcs.js";
import { openHandrail } from "./handrails.js";
import { createTooltips } from "./tooltips.js";
import { reRenderAll } from "./notation.js";
import { typesetMath } from "./libraries.js";

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
    rail.classList.toggle("scope-pinned", scope === "pinned");
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

  // Pinned tab: a referenced excerpt kept open beside the proof. tooltips.js
  // dispatches rail:pin from a preview's pin button. One pin at a time, so a new
  // pin replaces the old. The pinned scope is deliberately not persisted (the
  // excerpt is runtime-only), so a reload returns to the pre-pin scope.
  const pinnedBody = rail.querySelector(".rail-pinned-body");
  const pinnedTitle = rail.querySelector(".rail-pinned-title");
  let prePinScope = null;
  document.addEventListener("rail:pin", (ev) => {
    if (!pinnedBody) return;
    if (!rail.classList.contains("has-pin")) {
      prePinScope =
        rail.querySelector(".rail-scope.active")?.dataset.scope || "document";
    }
    pinnedBody.innerHTML = ev.detail.html || "";
    if (pinnedTitle) pinnedTitle.textContent = ev.detail.title || "Pinned";
    typesetMath(pinnedBody);
    rail.classList.add("has-pin");
    selectScope("pinned");
  });
  const pinClose = rail.querySelector(".rail-pin-close");
  if (pinClose) {
    pinClose.addEventListener("click", () => {
      if (pinnedBody) pinnedBody.innerHTML = "";
      if (pinnedTitle) pinnedTitle.textContent = "";
      rail.classList.remove("has-pin");
      selectScope(prePinScope || "document");
      prePinScope = null;
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

  // ---- mobile bottom-drawer (<=1100px) ----
  // Below the desktop breakpoint the rail re-skins as a bottom sheet with three
  // states (data-drawer: closed | peek | open). CSS owns the layout; here we
  // inject the grip and peek-goal bar, drive the transitions, persist the state,
  // and (via updatePeekGoal, called from updateState) keep the peek goal current.
  let drawerGoalEl = null;
  if (window.matchMedia("(max-width: 1320px)").matches) {
    const handle = document.createElement("button");
    handle.type = "button";
    handle.className = "rail-handle";
    handle.setAttribute("aria-label", "Toggle the navigation drawer");
    const peek = document.createElement("div");
    peek.className = "rail-peek";
    peek.innerHTML =
      '<span class="rail-peek-label">Prove</span><span class="rail-peek-goal"></span>';
    rail.insertBefore(peek, rail.firstChild);
    rail.insertBefore(handle, rail.firstChild);
    drawerGoalEl = peek.querySelector(".rail-peek-goal");

    const DRAWER_KEY = "rsm-drawer:" + location.pathname;
    const setDrawer = (state, persist = true) => {
      rail.dataset.drawer = state;
      handle.setAttribute("aria-expanded", String(state === "open"));
      if (persist) {
        try {
          localStorage.setItem(DRAWER_KEY, state);
        } catch (e) {
          /* localStorage unavailable; state stays session-only */
        }
      }
    };
    let savedDrawer = null;
    try {
      savedDrawer = localStorage.getItem(DRAWER_KEY);
    } catch (e) {
      /* ignore */
    }
    setDrawer(["closed", "peek", "open"].includes(savedDrawer) ? savedDrawer : "peek", false);

    // Drag the grip to step between states (closed <-> peek <-> open); a tap
    // (no real drag) toggles peek<->open and reopens a closed sheet to peek.
    // There is no separate close button: dragging down reaches closed.
    const ORDER = ["closed", "peek", "open"];
    let dragY = null;
    let dragged = false;
    handle.addEventListener("pointerdown", (ev) => {
      dragY = ev.clientY;
      dragged = false;
      try {
        handle.setPointerCapture(ev.pointerId);
      } catch (e) {
        /* synthetic/uncaptured pointer */
      }
    });
    handle.addEventListener("pointermove", (ev) => {
      if (dragY !== null && Math.abs(ev.clientY - dragY) > 8) dragged = true;
    });
    handle.addEventListener("pointerup", (ev) => {
      if (dragY === null) return;
      const dy = ev.clientY - dragY;
      const i = ORDER.indexOf(rail.dataset.drawer);
      if (!dragged) {
        setDrawer(rail.dataset.drawer === "peek" ? "open" : "peek");
      } else if (dy < 0) {
        setDrawer(ORDER[Math.min(i + 1, ORDER.length - 1)]);
      } else {
        setDrawer(ORDER[Math.max(i - 1, 0)]);
      }
      dragY = null;
      dragged = false;
    });
    // Focusing a step (a map-node click) drops the sheet to peek so the body's
    // focused cone is readable; the exit bar in the rail restores it.
    document.addEventListener("rsm:focus-enter", () => setDrawer("peek"));
  }

  // Keep the peek bar showing the current proof's goal, with rendered math, on
  // one clamped line (no-op off mobile). Re-render only when the goal changes,
  // since typesetting is not free.
  let peekGoalId;
  function updatePeekGoal() {
    if (!drawerGoalEl) return;
    let g = null;
    const data = current ? stateData.get(current) : null;
    if (data && active.idx >= 0 && active.idx < data.length) g = data[active.idx].goal;
    const gid = g && g.id != null ? String(g.id) : null;
    if (gid === peekGoalId) return;
    peekGoalId = gid;
    const el = gid != null ? root.querySelector('[data-nodeid="' + gid + '"]') : null;
    if (!el) {
      rail.classList.add("drawer-no-goal");
      drawerGoalEl.textContent = "Open the navigation drawer";
      return;
    }
    rail.classList.remove("drawer-no-goal");
    // Show just the goal statement: clone the content, drop its label and any
    // let/assume preamble, then typeset the cloned math.
    const cz = el.querySelector(":scope > .hr-content-zone") || el;
    const clone = cloneClean(cz);
    clone
      .querySelectorAll(".hr-label, .construct.let, .construct.assume")
      .forEach((n) => n.remove());
    drawerGoalEl.innerHTML = "";
    drawerGoalEl.appendChild(clone);
    // Drop a leading connective ("⊢", a dangling ", then"/"Then") left behind by
    // removing the let/assume preamble, so the peek reads as a clean statement.
    // Skip text inside math (never rewrite rendered formulas), clean the first
    // prose text node, then stop.
    const tw = document.createTreeWalker(drawerGoalEl, NodeFilter.SHOW_TEXT, {
      acceptNode: (n) =>
        n.parentElement && n.parentElement.closest("math")
          ? NodeFilter.FILTER_REJECT
          : NodeFilter.FILTER_ACCEPT,
    });
    let tn;
    while ((tn = tw.nextNode())) {
      if (!tn.textContent.trim()) continue;
      tn.textContent = tn.textContent.replace(/^[\s,.;:⊢]*(?:then\b[\s,]*)?/i, "");
      break;
    }
    typesetMath(drawerGoalEl).then(() => reRenderAll(drawerGoalEl));
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
    active.idx = -1; // a newly selected proof restarts step tracking from the top
    for (const [k, item] of items) item.classList.toggle("shown", k === key);
    // Outside any proof the Proof scope has nothing live to show; CSS uses this
    // to present an empty state rather than a blank panel.
    rail.classList.toggle("no-proof", key === null);
    updateCollapsedClass();
    updateState();
  }
  show(null);

  // Follow the reader's selection (the focused / clicked block), not the scroll.
  // The keyboard cursor (j/k, h/l, Tab) moves focus, and clicking anywhere in a
  // proof selects it; either way the rail shows that proof, and a focus/click on
  // a specific step selects that step in the State view and the DAG. The cursor
  // clears the rail when it leaves every proof; a click never clears (so an
  // outside click does not blank the rail).
  function stepsOf(proofEl) {
    return [...proofEl.querySelectorAll(".step")].filter((s) => !s.closest(".calc"));
  }
  function selectFrom(target, clearOutside) {
    if (!target || !target.closest) return;
    // The rail's own controls and the portaled handrail menu are not selections.
    if (target.closest(".proof-rail") || target.closest("#hr-menu-singleton")) return;
    let el = target.closest(".proof[data-nodeid]");
    while (el && !items.has(el.getAttribute("data-nodeid"))) {
      const p = el.parentElement;
      el = p ? p.closest(".proof[data-nodeid]") : null;
    }
    if (!el) {
      if (clearOutside) show(null);
      return;
    }
    show(el.getAttribute("data-nodeid"));
    const stepEl = target.closest(".step");
    if (stepEl && !stepEl.closest(".calc") && el.contains(stepEl)) {
      // A reordered proof tags each step with its build index (data-state-idx)
      // so the State panel maps to the step's own state, not whatever step now
      // sits at its position. Unreordered proofs have no tag and fall back to
      // position, which equals the build index.
      const idx =
        stepEl.dataset.stateIdx != null
          ? Number(stepEl.dataset.stateIdx)
          : stepsOf(el).indexOf(stepEl);
      if (idx >= 0) updateState(idx);
    }
  }
  if (proofs.length) {
    root.addEventListener("click", (ev) => selectFrom(ev.target, false));
    root.addEventListener("focusin", (ev) => selectFrom(ev.target, true));
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
    // Navigate by hash so the jump pushes a browser-history entry (native Back
    // returns the reader to where they were). Every block carries an id.
    if (el.id) location.hash = el.id;
    else el.scrollIntoView({ behavior: "smooth", block: "start" });
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
  function updateState(idx) {
    if (rail.classList.contains("focusing")) {
      setCurrentNode(null);
      return;
    }
    // idx is the selected step within the shown proof. When unspecified (the
    // proof was just selected, or a collapse toggled), keep the current step,
    // defaulting to the first so the rail is never empty inside a proof.
    if (!current) idx = -1;
    else if (idx == null || idx < 0) idx = active.idx >= 0 ? active.idx : 0;
    setActiveIdx(idx);
    const item = current ? items.get(current) : null;
    const node =
      item && idx >= 0 ? item.querySelector(`.toc-node[data-idx="${idx}"]`) : null;
    setCurrentNode(node);
    // Keep the proof DAG resting on the current step's prerequisite path.
    const dag = item ? item.querySelector("svg.toc-tree") : null;
    if (dag) pinTreeCurrent(dag, idx >= 0 ? String(idx) : null);
    updatePeekGoal();
  }

  // No step scroll-observer: the State view follows the step the reader clicks
  // (handled by the proof click handler above), not the scroll position.

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
        '<div class="rail-state-empty">Click a proof to see its live hypotheses and current goal.</div>';
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
        '<span class="rail-state-caret" aria-hidden="true">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
        'stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6l6 -6"/></svg>' +
        "</span>";
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

    // The provenance number in a row's left gutter, bracketed by kind: ⟨n⟩ for a
    // step, (n) for a section. Decorative: the same fact is in the keyword
    // control's tooltip/aria-label, so it is hidden from screen readers.
    function numCell(num, kind) {
      const s = document.createElement("span");
      s.className = "rail-state-num";
      s.setAttribute("aria-hidden", "true");
      if (num) s.textContent = kind === "section" ? "(" + num + ")" : "⟨" + num + "⟩";
      return s;
    }

    // Scroll the body to wherever a state item was introduced.
    function scrollToNode(targetId) {
      const t = root.querySelector('[data-nodeid="' + targetId + '"]');
      // Navigate by hash so the jump is reversible via the browser Back button.
      if (t && t.id) location.hash = t.id;
      else if (t) t.scrollIntoView({ block: "center", behavior: "smooth" });
    }

    // Every state row jumps to where its item was introduced: prose/definition
    // for In-scope items, the introducing step for hypotheses and goals. The
    // whole row is the mouse target (inner reference links keep their own jump),
    // and the leading construct keyword is the keyboard/SR control carrying the
    // tooltip. The keyword sits beside any inner links (siblings), so there is
    // no nested-interactive violation; when a row has no keyword we fall back to
    // the row itself, but only when it holds no inner link to nest inside it.
    function makeJumpable(li, targetId, tip) {
      if (targetId == null) return;
      li.classList.add("rail-jump-row");
      li.addEventListener("click", (ev) => {
        if (ev.target.closest("a")) return; // let reference links navigate
        scrollToNode(targetId);
      });
      const host = li.querySelector(".keyword") || (li.querySelector("a") ? null : li);
      if (!host) return;
      host.classList.add("rail-jump-control");
      host.setAttribute("role", "button");
      host.setAttribute("tabindex", "0");
      host.setAttribute("aria-label", tip || "jump to source");
      if (tip) host.setAttribute("data-tooltip", tip);
      host.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          scrollToNode(targetId);
        }
      });
    }

    // PROVE first.
    const goalB = makeBlock("goal", "Prove", false);
    const g = st.goal;
    const goalEl = g && g.id != null ? root.querySelector('[data-nodeid="' + g.id + '"]') : null;
    if (goalEl && g.thm) {
      // A setup step's goal is the whole theorem: a gutter row (section marker +
      // rule + hover) showing a clamped preview of the statement so the
      // collapsed state still carries information, with a "show more" toggle.
      // The toggle is the only control, so the row is not made jumpable.
      const summary = document.createElement("div");
      summary.className = "rail-goal-summary rail-jump-row";
      summary.appendChild(numCell(g.num, g.marker));
      const preview = document.createElement("div");
      preview.className = "rail-goal-preview";
      const text = document.createElement("div");
      text.className = "rail-goal-text clamped";
      const cz = goalEl.querySelector(":scope > .hr-content-zone") || goalEl;
      const clone = cloneClean(cz);
      clone
        .querySelectorAll(".hr-label, .construct.let, .construct.assume")
        .forEach((n) => n.remove());
      text.appendChild(clone);
      preview.appendChild(text);
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "rail-goal-toggle";
      toggle.textContent = "show more";
      toggle.addEventListener("click", () => {
        const clamped = text.classList.toggle("clamped");
        toggle.textContent = clamped ? "show more" : "show less";
      });
      preview.appendChild(toggle);
      summary.appendChild(preview);
      goalB.body.appendChild(summary);
    } else if (goalEl) {
      const gbody = document.createElement("div");
      gbody.className = "rail-goal-body";
      gbody.appendChild(numCell(g.num, g.marker));
      gbody.appendChild(cloneClean(goalEl));
      makeJumpable(gbody, g.id, g.num ? "Go to step " + g.num : "Go to the goal");
      goalB.body.appendChild(gbody);
    } else {
      goalB.body.textContent = "the main result";
    }
    panel.appendChild(goalB.block);

    // ASSUME: the proof's own hypotheses, each row jumping to its introducing
    // step.
    const hyps = (st.hyps || [])
      .map((h) => ({
        el: root.querySelector('[data-nodeid="' + h.id + '"]'),
        num: h.num,
        id: h.id,
        marker: h.marker,
      }))
      .filter((h) => h.el);
    const hypB = makeBlock("hyps", "Assume", false);
    const ul = document.createElement("ul");
    if (hyps.length) {
      for (const h of hyps) {
        const li = document.createElement("li");
        li.appendChild(numCell(h.num, h.marker));
        li.appendChild(cloneClean(h.el));
        const where = h.marker === "section" ? "section " : "step ";
        makeJumpable(li, h.id, h.num ? "Introduced in " + where + h.num : "Jump to source");
        ul.appendChild(li);
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
      .map((c) => ({
        el: root.querySelector('[data-nodeid="' + c.id + '"]'),
        id: c.id,
        num: c.num,
        marker: c.marker,
      }))
      .filter((c) => c.el);
    if (ctx.length) {
      const ctxB = makeBlock("context", "In scope", ctx.length > 4);
      const cul = document.createElement("ul");
      for (const c of ctx) {
        const li = document.createElement("li");
        li.appendChild(numCell(c.num, c.marker));
        li.appendChild(cloneClean(c.el));
        makeJumpable(
          li,
          c.id,
          c.num ? "Introduced in section " + c.num : "Jump to where this is introduced"
        );
        cul.appendChild(li);
      }
      ctxB.body.appendChild(cul);
      panel.appendChild(ctxB.block);
    }

    // Size the marker gutter to the widest marker actually present (a dotted
    // ⟨3.3⟩ or ⟨1.5.1⟩ needs more room than a bare ⟨3⟩), so no marker overlaps
    // the rule and single-digit proofs waste no space. scrollWidth is the true
    // content width even while the column still clips it.
    let maxNum = 0;
    panel.querySelectorAll(".rail-state-num").forEach((n) => {
      maxNum = Math.max(maxNum, n.scrollWidth);
    });
    if (maxNum > 0) panel.style.setProperty("--rail-num-width", maxNum + "px");

    // Clones can carry math the body has not typeset yet (typesetMath runs
    // progressively, so a proof scrolled to early may still hold raw \(...\)).
    // typesetMath renders those raw spans; reRenderAll then re-applies the
    // current notation to every already-typeset span. The two are complementary
    // (each skips what the other handles), so running both covers all clones.
    typesetMath(panel).then(() => reRenderAll(panel));
    // Cloned references carry no live tooltip, and the markers carry a
    // data-tooltip; bind both with the body's initializer (idempotent).
    createTooltips();
  }
}
