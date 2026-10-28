// prooftree.js
//
// The reader sidebar's panel. Scopes and views:
//   Document - the whole-manuscript section graph (Contents), and Notation
//   Proof    - the step graph (Steps) and live State of the proof in view
//   Pinned   - an excerpt kept open beside the text
//   Reading  - typeface, size, line height, width and theme
// The graphs are pre-rendered SVGs (laid out at build time). This module routes
// views, auto-follows the proof you are reading, keeps the pinned excerpt and
// the reading settings, and remembers the open view in localStorage. The strip
// that opens and closes the panel, and the page layout around it, live in
// sidebar.js.

import { wireTree, pinTreeCurrent } from "./tocarcs.js";
import { openHandrail } from "./handrails.js";
import { createTooltips } from "./tooltips.js";
import { reRenderAll } from "./notation.js";
import { typesetMath } from "./libraries.js";
import { setupStrip } from "./sidebar.js";

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

  // ---- views: scope + sub-view ----

  const SCOPES = ["document", "proof", "pinned", "reading"];
  function currentScope() {
    return SCOPES.find((s) => rail.classList.contains("scope-" + s)) || "document";
  }

  function selectScope(scope) {
    for (const s of SCOPES) rail.classList.toggle("scope-" + s, s === scope);
  }

  // A sub-view is a rail-tab data-view: doc-map / notation (Document) or
  // proof-map / state (Proof). The rail class is scoped (doc-view-* vs
  // proof-view-*) so both scopes can have a "map" view without colliding. The
  // sub-tabs (text tabs on phones) are kept in sync when present.
  function selectSubview(view) {
    const inDoc = view === "doc-map" || view === "notation";
    const prefix = inDoc ? "doc-view-" : "proof-view-";
    const suffix = view.replace(/^(doc|proof)-/, "");
    for (const c of [...rail.classList]) {
      if (c.startsWith(prefix)) rail.classList.remove(c);
    }
    rail.classList.add(prefix + suffix);
    const row = rail.querySelector(
      inDoc ? ".rail-subtabs-document" : ".rail-subtabs-proof",
    );
    if (row) {
      for (const t of row.querySelectorAll(".rail-tab")) {
        const on = t.dataset.view === view;
        t.classList.toggle("active", on);
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
      }
    }
    if (!inDoc) {
      proofView = view === "state" ? "state" : "map";
      renderState();
    }
  }

  function saveLayout(extra) {
    let saved = {};
    try {
      saved = JSON.parse(localStorage.getItem(lsKey) || "{}") || {};
    } catch (e) {
      saved = {};
    }
    const layout = Object.assign(saved, {
      docView: rail.classList.contains("doc-view-notation") ? "notation" : "doc-map",
      proofView: rail.classList.contains("proof-view-state") ? "state" : "proof-map",
    }, extra || {});
    try {
      localStorage.setItem(lsKey, JSON.stringify(layout));
    } catch (e) {
      /* localStorage unavailable; layout stays session-only */
    }
  }

  // The phone sheet's text tabs switch a scope's two views.
  for (const row of rail.querySelectorAll(".rail-subtabs")) {
    row.addEventListener("click", (ev) => {
      const t = ev.target.closest(".rail-tab");
      if (!t) return;
      selectSubview(t.dataset.view);
      saveLayout();
      rail.dispatchEvent(new CustomEvent("rail:subview", { bubbles: true }));
    });
    row.addEventListener("keydown", (ev) => {
      if (ev.key !== "ArrowLeft" && ev.key !== "ArrowRight") return;
      const tabs = [...row.querySelectorAll(".rail-tab")];
      const i = tabs.indexOf(document.activeElement);
      if (i < 0) return;
      ev.preventDefault();
      const next = tabs[(i + (ev.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
      next.click();
      next.focus();
    });
  }

  // Pinned: a referenced excerpt kept open beside the text. tooltips.js
  // dispatches rail:pin from a preview's pin control or a block's handrail menu.
  // One pin at a time, so a new pin replaces the old. The excerpt is
  // runtime-only (not persisted).
  const pinnedBody = rail.querySelector(".rail-pinned-body");
  const pinnedTitle = rail.querySelector(".rail-pinned-title");
  document.addEventListener("rail:pin", (ev) => {
    if (!pinnedBody) return;
    pinnedBody.innerHTML = ev.detail.html || "";
    if (pinnedTitle) pinnedTitle.textContent = ev.detail.title || "Pinned";
    typesetMath(pinnedBody);
    rail.classList.add("has-pin");
  });
  const pinClose = rail.querySelector(".rail-pin-close");
  if (pinClose) {
    pinClose.addEventListener("click", () => {
      if (pinnedBody) pinnedBody.innerHTML = "";
      if (pinnedTitle) pinnedTitle.textContent = "";
      rail.classList.remove("has-pin");
      document.dispatchEvent(new CustomEvent("rail:unpin"));
    });
  }

  // ---- reading controls (typeface, size, line height, width, theme) ----
  // Each button sets a root data-reading-* attribute (or the theme class) and
  // persists it; the inline boot script pre-applies them before first paint.
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
    if (control === "theme") {
      // Light or Dark forces the color-scheme with one class; System clears
      // both, so the page follows the operating system again.
      el.classList.toggle("dark-theme", value === "dark");
      el.classList.toggle("light-theme", value === "light");
    } else el.setAttribute("data-reading-" + control, value);
  }
  function syncReadingRow(row, value) {
    for (const o of row.querySelectorAll(".reading-opt")) {
      const on = o.dataset.value === value;
      o.classList.toggle("active", on);
      o.setAttribute("aria-pressed", String(on));
    }
  }
  const readingPanel = rail.querySelector(".rail-reading");
  if (readingPanel) {
    readingPanel.addEventListener("click", (ev) => {
      const btn = ev.target.closest(".reading-opt");
      if (!btn) return;
      const row = btn.closest(".reading-row");
      const control = row.dataset.control;
      syncReadingRow(row, btn.dataset.value);
      applyReading(control, btn.dataset.value);
      const prefs = readReadingPrefs();
      prefs[control] = btn.dataset.value;
      try {
        localStorage.setItem(READING_KEY, JSON.stringify(prefs));
      } catch (e) {
        /* localStorage unavailable; preference stays session-only */
      }
    });
    // Apply saved prefs (idempotent with the boot script) and show the reader's
    // real choice. The theme also honours the older rsm-theme key, and with no
    // stored choice at all it is System.
    const prefs = readReadingPrefs();
    if (!prefs.theme) {
      let legacy = null;
      try {
        legacy = localStorage.getItem("rsm-theme");
      } catch (e) {
        /* ignore */
      }
      if (legacy === "light" || legacy === "dark") prefs.theme = legacy;
    }
    // With no stored typeface choice, rest on the manuscript's built-in default
    // (the body carries it as data-typography) so the pressed tile matches what
    // the document actually renders, with no flash of the wrong tile.
    if (!prefs.typeface) {
      prefs.typeface =
        document.body && document.body.getAttribute("data-typography") === "serif"
          ? "serif"
          : "sans";
    }
    for (const row of readingPanel.querySelectorAll(".reading-row")) {
      const value = prefs[row.dataset.control];
      if (!value || !row.querySelector(`.reading-opt[data-value="${value}"]`)) continue;
      applyReading(row.dataset.control, value);
      syncReadingRow(row, value);
    }
  }

  // Restore the reader's last views.
  try {
    const saved = JSON.parse(localStorage.getItem(lsKey) || "null");
    if (saved) {
      if (saved.docView && rail.querySelector(".rail-doc-map") && rail.querySelector(".rail-notation")) {
        selectSubview(saved.docView === "notation" ? "notation" : "doc-map");
      }
      if (saved.proofView) selectSubview(saved.proofView === "state" ? "state" : "proof-map");
    }
  } catch (e) {
    /* ignore malformed saved layout */
  }

  // The strip (desktop) / bottom bar (phones) that opens this panel.
  const strip = root.querySelector(".rail-strip");
  if (strip) {
    setupStrip(strip, rail, {
      selectScope,
      selectSubview,
      currentScope,
      saveLayout,
      savedLayout: () => {
        try {
          return JSON.parse(localStorage.getItem(lsKey) || "null");
        } catch (e) {
          return null;
        }
      },
    });
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
    // The sidebar's own controls and the portaled handrail menu are not selections.
    if (
      target.closest(".proof-rail") ||
      target.closest(".rail-strip") ||
      target.closest("#hr-menu-singleton")
    ) return;
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
    // Asides sit inside the block that calls them but are not part of it.
    c.querySelectorAll(".aside").forEach((n) => n.remove());
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

    // The provenance number in a row's left gutter, by kind: ⟨n⟩ for a step,
    // §n for a section. The section marker gets its own class so CSS can render
    // it small and muted: beside the ⟨n⟩ step glyphs a bracketed "(n)" read as a
    // stray step number, so sections are set apart in form and in weight.
    // Decorative: the same fact is in the keyword control's tooltip/aria-label,
    // so it is hidden from screen readers.
    function numCell(num, kind) {
      const s = document.createElement("span");
      s.className = "rail-state-num";
      s.setAttribute("aria-hidden", "true");
      if (num) {
        if (kind === "section") {
          s.classList.add("rail-state-num-section");
          s.textContent = "§" + num;
        } else {
          s.textContent = "⟨" + num + "⟩";
        }
      }
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
      if (tip) host.setAttribute("data-tip", tip);
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
    // data-tip (interface tooltip); bind the references with the body's initializer (idempotent).
    createTooltips();
  }
}
