// focusmode.js
//
// Focus a single step: the proof folds to that step and its transitive
// prerequisite cone (every other step collapses to its statement + ⟨n⟩ number
// via the same handrail collapse the chevron uses), and the rail dims to the
// same cone. The cone is the prerequisite closure over the rail's edges
// (dependency + containment, never forward pointers), so a step's structural
// ancestors come along automatically and the folded view stays coherent.
//
// Two ways in: the step's handrail menu ("Focus this step", the primary, dispatched
// as a "focus:step" event by handrails.js) and a click on the step's node in the
// rail's Proof map (the secondary). The "Show full proof" bar in the rail, the
// Escape key, or Enter/Space on that bar all restore the whole proof.

import { openHandrail, closeHandrail, withoutPersist } from "./handrails.js";

// Focus mode is gated behind an opt-in flag while it remains under development
// (potf-i4g): a document turns it on with <html data-focus-mode="on">. Without
// the flag (the default, including the submission paper) every trigger is inert,
// so the feature ships present but unreachable. Checked live, so tests opt in.
const focusEnabled = () =>
  document.documentElement.getAttribute("data-focus-mode") === "on";

export function setup(root = document) {
  const rail = root.querySelector(".proof-rail");
  if (!rail) return;

  // { proofEl, svg, startIdx, steps, wasCollapsed } for the proof in focus.
  let active = null;

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

  // A single polite live region announces entering and leaving focus to screen
  // readers, since the fold itself is a silent visual change.
  let liveRegion = null;
  function announce(msg) {
    if (!liveRegion) {
      liveRegion = document.createElement("div");
      liveRegion.className = "focus-sr-status";
      liveRegion.setAttribute("role", "status");
      liveRegion.setAttribute("aria-live", "polite");
      document.body.appendChild(liveRegion);
    }
    // Clear then set on the next frame so a repeated message still re-announces
    // (assistive tech ignores an unchanged text node).
    liveRegion.textContent = "";
    requestAnimationFrame(() => {
      liveRegion.textContent = msg;
    });
  }

  // Surface the rail's Proof scope and its step map (not State) so the dimmed
  // cone is visible. Mirrors what reorder.js does on entering reorder mode.
  function showProofMap() {
    const scopeBtn = rail.querySelector('.rail-scope[data-scope="proof"]');
    if (scopeBtn) scopeBtn.click();
    const mapTab = rail.querySelector(
      '.rail-subtabs-proof .rail-tab[data-view="proof-map"]',
    );
    if (mapTab && !mapTab.classList.contains("active")) mapTab.click();
  }

  // Escape leaves focus while it is active; bound on enter, dropped on exit so
  // it never competes with the menu/reorder Escape handlers when not focusing.
  function onKeydown(ev) {
    if (ev.key === "Escape") exitFocus();
  }

  // The one obvious way out lives in the rail itself, which is fixed on screen,
  // so it is always reachable no matter how far the reader has scrolled. It is a
  // role=button/tabindex=0 div, so wire Enter and Space alongside the click to
  // keep it keyboard-operable (it sits inside .proof-rail, which already paints a
  // visible :focus-visible outline).
  let exitBar = null;
  function setExitBar(sel) {
    const num = stepNumber(sel);
    if (!exitBar) {
      exitBar = document.createElement("div");
      exitBar.className = "proof-focus-exit";
      exitBar.setAttribute("role", "button");
      exitBar.tabIndex = 0;
      exitBar.addEventListener("click", exitFocus);
      exitBar.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          exitFocus();
        }
      });
    }
    exitBar.innerHTML =
      '<span class="proof-focus-back">↩</span>' +
      `<span>${num ? `Step ${num}` : "Focused"} · ` +
      '<span class="proof-focus-show-all">Show full proof</span></span>';
    rail.insertBefore(exitBar, rail.firstChild);
    rail.classList.add("focusing");
  }

  // Undo the focus view: restore each step to the collapsed state it had before
  // focus (so a step the reader had already collapsed stays collapsed, and one
  // focus folded is re-opened), un-dim the rail, and drop the focus chrome. Pure
  // teardown, no announcement, so re-focusing another step does not narrate an
  // exit it never really did.
  function teardown() {
    if (!active) return;
    document.removeEventListener("keydown", onKeydown);
    rail.classList.remove("focusing");
    if (exitBar) exitBar.remove();
    withoutPersist(() => {
      active.steps.forEach((st, i) =>
        active.wasCollapsed[i] ? closeHandrail(st) : openHandrail(st),
      );
    });
    undimRail(active.svg);
    active.proofEl.classList.remove("proof-focused");
    active = null;
  }

  function exitFocus() {
    if (!active) return;
    teardown();
    announce("Full proof restored.");
  }

  function enterFocus(railItem, proofEl, startIdx) {
    const svg = railItem.querySelector("svg.toc-tree");
    if (!svg) return;
    teardown();
    showProofMap();
    const idx = Number(startIdx);
    const cone = coneOf(svg, idx);
    const steps = stepsOf(proofEl);
    // Remember each step's pre-focus collapsed state so exit is non-destructive
    // to the reader's own manual collapses.
    const wasCollapsed = steps.map((st) => st.classList.contains("hr-collapsed"));
    withoutPersist(() => {
      steps.forEach((st, i) =>
        cone.has(String(i)) ? openHandrail(st) : closeHandrail(st),
      );
    });
    dimRail(svg, cone);
    proofEl.classList.add("proof-focused");
    const sel = steps[idx];
    active = { proofEl, svg, startIdx: String(idx), steps, wasCollapsed };
    setExitBar(sel);
    document.addEventListener("keydown", onKeydown);
    // "the K steps it depends on": the cone's body steps minus the focused one.
    const deps = steps.filter((_, i) => cone.has(String(i))).length - 1;
    const num = stepNumber(sel);
    announce(
      `Focused step ${num || idx + 1}: showing the ${Math.max(deps, 0)} ` +
        "steps it depends on; press Escape to show the full proof.",
    );
    // Let the mobile drawer drop to peek so the focused cone is readable.
    document.dispatchEvent(new CustomEvent("rsm:focus-enter"));
    if (sel) {
      const reduce =
        window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      sel.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
    }
  }

  // Primary trigger: "Focus this step" in the step's handrail menu (handrails.js
  // dispatches focus:step from the menu item).
  root.addEventListener("focus:step", (ev) => {
    if (!focusEnabled()) return;
    const step = ev.target.closest && ev.target.closest(".step");
    if (!step) return;
    const proofEl = step.closest(".proof[data-nodeid]");
    if (!proofEl) return;
    const railItem = rail.querySelector(
      `.proof-rail-item[data-proof="${proofEl.dataset.nodeid}"]`,
    );
    if (!railItem) return;
    const startIdx = stepsOf(proofEl).indexOf(step);
    if (startIdx < 0) return;
    enterFocus(railItem, proofEl, startIdx);
  });

  // Secondary trigger: a click on the step's node in the rail's Proof map.
  rail.addEventListener("click", (ev) => {
    if (!focusEnabled()) return;
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
