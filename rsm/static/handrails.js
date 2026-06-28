// handrails.js
//
// Basic user interactions, mostly dealing with handrails and their menus.
//

import * as tocarcs from './tocarcs.js';
import { lensConeSizes } from './deplens.js';

let singletonMenu = null;
let activeHr = null;

// Touch (no-hover, coarse pointer): mirrors the @media query that hides the
// per-block collapse chevron, so the menu carries collapse/expand instead.
const IS_TOUCH =
  typeof window !== "undefined" &&
  typeof window.matchMedia === "function" &&
  window.matchMedia("(hover: none) and (pointer: coarse)").matches;
let delegationAttached = false;

export function setup() {

  // Event delegation: attach once to document, works across Vue re-renders.
  if (delegationAttached) return;
  delegationAttached = true;

  // Dots click → show singleton menu
  document.addEventListener("click", function (ev) {
    const dots = ev.target.closest(".hr-border-dots");
    if (dots && dots.closest(".hr")) {
      const hr = dots.closest(".hr");
      if (activeHr === hr) {
        hideMenu();
      } else {
        singletonMenu = document.getElementById("hr-menu-singleton");
        showMenuFor(hr);
      }
      return;
    }

    // Menu item clicks (delegated on singleton)
    const menuItem = ev.target.closest("[data-role]");
    if (menuItem && menuItem.closest("#hr-menu-singleton")) {
      const role = menuItem.getAttribute("data-role");
      if (menuItem.classList.contains("disabled")) return;
      if (!activeHr) return;
      if (role === "link") copyLink(activeHr);
      else if (role === "code") showSource(activeHr);
      else if (role === "collapse") { toggleHandrail(activeHr); refreshCollapseLabels(activeHr); }
      else if (role === "collapse-all") {
        const withinSubproof = activeHr.classList.contains("step");
        collapseAll(activeHr, withinSubproof);
        refreshCollapseLabels(activeHr);
      }
      else if (role === "static-toggle") toggleStaticView(activeHr, menuItem);
      else if (role === "toc-view") toggleTocView(activeHr, menuItem);
      else if (role === "reorder") toggleReorder(activeHr);
      else if (role === "focus") triggerFocus(activeHr);
      else if (role === "deplens-up") triggerDeplens(activeHr, "up");
      else if (role === "deplens-down") triggerDeplens(activeHr, "down");
      return;
    }

    // Collapse zone click (left-side toggle)
    const collapseBtn = ev.target.closest(".hr-collapse");
    if (collapseBtn && collapseBtn.closest(".hr-collapse-zone")) {
      toggleHandrail(ev.target);
      return;
    }
  });

  // A click on the handrail's controls (collapse chevron, the dots, or any menu
  // item) must not focus (and so visually select) the enclosing handrail.
  // Suppressing the default on mousedown prevents that focus without blurring
  // whatever the reader had focused before.
  document.addEventListener("mousedown", function (ev) {
    if (!ev.target.closest) return;
    if (
      ev.target.closest(".hr-collapse-zone") ||
      ev.target.closest(".hr-border-zone") ||
      ev.target.closest("#hr-menu-singleton")
    ) {
      ev.preventDefault();
    }
  });

  // Mouse leave on singleton menu → hide
  // Use capture on mouseout (which bubbles, unlike mouseleave) and check
  // that relatedTarget is outside the menu before hiding.
  document.addEventListener("mouseout", function (ev) {
    const menu = ev.target.closest && ev.target.closest("#hr-menu-singleton .hr-menu");
    if (!menu) return;
    if (ev.relatedTarget && menu.contains(ev.relatedTarget)) return;
    hideMenu();
  }, true);

  // Set height of offset handrails' borders — re-observed on every call
  observeOffsetHandrails();

}

const resizeObserver = new ResizeObserver(updateHeight);

export function observeOffsetHandrails() {
  resizeObserver.disconnect();
  document.querySelectorAll('.hr.hr-offset > .hr-content-zone').forEach(el => resizeObserver.observe(el));
}


function showMenuFor(hr) {
  if (!singletonMenu) return;

  activeHr = hr;
  hr.classList.add("hr-menu-open");
  const label = hr.getAttribute("data-menu-label") || "";
  let collapse = hr.getAttribute("data-menu-collapse");
  const collapseAll = hr.getAttribute("data-menu-collapse-all");
  // On touch the per-block collapse chevron is hidden (CSS), so move its action
  // into the menu: any chevron-collapsible block gets a Collapse/Expand item,
  // even if the build did not mark it menu-collapsible. Persist it on the node so
  // refreshCollapseLabels (which re-reads the attribute) keeps the label in sync.
  // Desktop is unaffected: the chevron stays and IS_TOUCH is false.
  if (
    IS_TOUCH &&
    (!collapse || collapse === "disabled") &&
    hr.querySelector(":scope > .hr-collapse-zone .hr-collapse")
  ) {
    collapse = "enabled";
    hr.setAttribute("data-menu-collapse", collapse);
  }
  const link = hr.getAttribute("data-menu-link");
  const code = hr.getAttribute("data-menu-code");

  // Configure label
  const labelEl = singletonMenu.querySelector('[data-role="label"]');
  const labelSep = singletonMenu.querySelector('[data-role="label-sep"]');
  if (labelEl) {
    labelEl.textContent = label;
    labelEl.parentElement.style.display = label ? "" : "none";
  }
  if (labelSep) labelSep.style.display = label ? "" : "none";

  // Configure collapse items
  configureItem(singletonMenu.querySelector('[data-role="collapse"]'), collapse);
  configureItem(singletonMenu.querySelector('[data-role="collapse-all"]'), collapseAll);

  // Reflect the handrail's collapsed state in the collapse item labels (the
  // per-handrail flip open/closeHandrail used to do was lost in the singleton
  // refactor). Done here on open, and again right after a collapse click.
  refreshCollapseLabels(hr);

  // Show/hide collapse separator based on whether any collapse item is visible
  const collapseSep = singletonMenu.querySelector('[data-role="collapse-sep"]');
  if (collapseSep) {
    const anyCollapse = collapse || collapseAll;
    collapseSep.style.display = anyCollapse ? "" : "none";
  }

  // Configure link and code items
  configureItem(singletonMenu.querySelector('[data-role="link"]'), link);
  configureItem(singletonMenu.querySelector('[data-role="code"]'), code);

  // Configure static toggle
  const staticToggle = hr.getAttribute("data-menu-static-toggle");
  const staticToggleEl = singletonMenu.querySelector('[data-role="static-toggle"]');
  const staticSep = singletonMenu.querySelector('[data-role="static-sep"]');
  configureItem(staticToggleEl, staticToggle);
  if (staticSep) staticSep.style.display = staticToggle ? "" : "none";
  if (staticToggleEl && staticToggle && staticToggle !== "disabled") {
    const figure = hr.closest("figure") || hr.closest("figcaption")?.parentElement;
    const isShowingStatic = figure && figure.classList.contains("showing-static");
    const textEl = staticToggleEl.querySelector(".hr-menu-item-text");
    if (textEl) textEl.textContent = isShowingStatic ? "Interactive" : "Static";
    const useEl = staticToggleEl.querySelector("svg use");
    if (useEl) useEl.setAttribute("href", isShowingStatic ? "#hr-icon-play" : "#hr-icon-image");
  }

  // Configure TOC view toggle
  const tocView = hr.getAttribute("data-menu-toc-view");
  const tocViewEl = singletonMenu.querySelector('[data-role="toc-view"]');
  const tocViewSep = singletonMenu.querySelector('[data-role="toc-view-sep"]');
  configureItem(tocViewEl, tocView);
  if (tocViewSep) tocViewSep.style.display = tocView ? "" : "none";
  if (tocViewEl && tocView && tocView !== "disabled") {
    const toc = hr.closest(".toc");
    const isTree = toc && toc.classList.contains("tree");
    const textEl = tocViewEl.querySelector(".hr-menu-item-text");
    if (textEl) textEl.textContent = isTree ? "View as list" : "View as tree";
  }

  // Reorder steps: offered on proofs only. It needs a pointer and the wide
  // floating dependency rail (the constraint view), neither of which a phone
  // affords, so on coarse-pointer touch devices it is shown disabled and
  // labeled rather than offered as a broken affordance. On desktop the label
  // flips to reflect the current mode.
  const isProof = hr.classList.contains("proof");
  const touch = window.matchMedia("(hover: none) and (pointer: coarse)").matches;
  const reorder = isProof ? (touch ? "disabled" : "true") : null;
  const reorderEl = singletonMenu.querySelector('[data-role="reorder"]');
  const reorderSep = singletonMenu.querySelector('[data-role="reorder-sep"]');
  configureItem(reorderEl, reorder);
  if (reorderSep) reorderSep.style.display = reorder ? "" : "none";
  if (reorderEl && reorder) {
    const textEl = reorderEl.querySelector(".hr-menu-item-text");
    if (touch) {
      reorderEl.setAttribute("aria-disabled", "true");
      reorderEl.removeAttribute("aria-pressed");
      if (textEl) textEl.textContent = "Reorder (desktop only)";
    } else {
      const on = hr.classList.contains("reorder-active");
      reorderEl.removeAttribute("aria-disabled");
      reorderEl.setAttribute("aria-pressed", on ? "true" : "false");
      if (textEl) textEl.textContent = on ? "Done" : "Reorder";
    }
  }

  // Focus this step: offered on steps only, and only when the document ships the
  // floating proof rail (focus mode folds the proof against the rail's
  // dependency map; without a rail there is nothing to fold against, so the item
  // would be a dead affordance). A step inside a :calc: chain is not a node in
  // that map (it reads as one step, like reorder's isDagStep), so it has no cone
  // to focus and is excluded. focusmode.js does the work on the dispatched event;
  // here we just gate visibility.
  const isStep = hr.classList.contains("step") && !hr.closest(".calc");
  const hasRail = !!document.querySelector(".proof-rail");
  // Focus mode is opt-in while under development (potf-i4g): only offer the item
  // when the document sets <html data-focus-mode="on">. The submission paper does
  // not, so the item never appears there. Mirrors the guard in focusmode.js.
  const focusOn = document.documentElement.getAttribute("data-focus-mode") === "on";
  const focus = isStep && hasRail && focusOn ? "true" : null;
  const focusEl = singletonMenu.querySelector('[data-role="focus"]');
  const focusSep = singletonMenu.querySelector('[data-role="focus-sep"]');
  configureItem(focusEl, focus);
  if (focusSep) focusSep.style.display = focus ? "" : "none";

  // Dependency lens: on a proof step OR a named result (theorem/lemma/...),
  // offer "What does this rest on?" (its upstream cone) and "What rests on
  // this?" (its downstream cone). Each is offered only when that cone is
  // non-empty so it is never a dead affordance. deplens.js reads the per-proof
  // step graph for steps and an aggregated result graph for results; both need
  // the floating rail, so the items only appear when the rail is present.
  const isResult =
    !!hr.id &&
    (hr.classList.contains("theorem") ||
      hr.classList.contains("lemma") ||
      hr.classList.contains("corollary") ||
      hr.classList.contains("proposition")) &&
    !hr.classList.contains("definition");
  let lensUp = null;
  let lensDown = null;
  if ((isStep || isResult) && document.querySelector(".proof-rail")) {
    const sizes = lensConeSizes(hr);
    // Always offer both directions; DISABLE (rather than hide) the one whose
    // cone is empty, with a tooltip that says why, so the pair is discoverable
    // and a missing direction is explained instead of silently absent.
    lensUp = sizes.up > 0 ? "true" : "disabled";
    lensDown = sizes.down > 0 ? "true" : "disabled";
  }
  const lensUpEl = singletonMenu.querySelector('[data-role="deplens-up"]');
  const lensDownEl = singletonMenu.querySelector('[data-role="deplens-down"]');
  const lensSep = singletonMenu.querySelector('[data-role="deplens-sep"]');
  configureItem(lensUpEl, lensUp);
  configureItem(lensDownEl, lensDown);
  setLensHint(
    lensUpEl,
    lensUp,
    isStep
      ? "This step depends on nothing earlier in the proof."
      : "This result depends on no other result.",
  );
  setLensHint(
    lensDownEl,
    lensDown,
    isStep
      ? "Nothing else in the proof uses this step."
      : "No other result uses this one.",
  );
  if (lensSep) lensSep.style.display = lensUp || lensDown ? "" : "none";

  // Position, then portal to <body>. An open menu can pop into the gutter where
  // the floating proof-rail sits; an ancestor of the handrail (proof/section/
  // figure) establishes a stacking context that paints below that fixed rail, so
  // any z-index on the menu or handrail is trapped beneath it. Escape the trap by
  // reparenting the singleton to <body>: first append it into the handrail's zone
  // so the existing CSS (left/right, offset, touch variants) computes the correct
  // on-screen spot, measure that, then move it to <body> and re-anchor it in page
  // coordinates so it sits above the rail regardless of which ancestor trapped it.
  const zone = hr.querySelector(":scope > .hr-menu-zone");
  if (zone) {
    zone.appendChild(singletonMenu);
    singletonMenu.style.display = "";
    zone.style.display = "block";
    portalMenuToBody();
  }
}


// Toggle a proof into or out of reorder mode. reorder.js (set up in onload)
// listens for the dispatched event and adds/removes the drag handles.
function toggleReorder(hr) {
  const active = hr.classList.toggle("reorder-active");
  hideMenu();
  hr.dispatchEvent(
    new CustomEvent("reorder:toggle", { bubbles: true, detail: { active } })
  );
}


// Enter focus mode on a step. focusmode.js (set up in onload) listens for the
// dispatched event, finds the step's proof and rail map, and folds the proof to
// this step's prerequisite cone. Mirrors toggleReorder's menu->event handoff.
function triggerFocus(hr) {
  hideMenu();
  hr.dispatchEvent(new CustomEvent("focus:step", { bubbles: true }));
}


// Light a step's dependency cone in the given direction ("up" = what it rests
// on, "down" = what rests on it). deplens.js (set up in onload) listens for the
// dispatched event and marks the body + rail. Mirrors triggerFocus.
function triggerDeplens(hr, direction) {
  hideMenu();
  hr.dispatchEvent(
    new CustomEvent("deplens:show", { bubbles: true, detail: { direction } })
  );
}


// The inner popup, whose computed rect we capture when portaling to <body>.
function menuPopup() {
  return singletonMenu && singletonMenu.querySelector(".hr-menu");
}


// Re-anchor the menu's CSS-computed screen position as page coordinates on
// <body>, escaping every ancestor stacking context. Called only with the menu
// already laid out inside its handrail zone (so the rect is meaningful).
function portalMenuToBody() {
  const popup = menuPopup();
  if (!popup) return;
  const rect = popup.getBoundingClientRect();
  document.body.appendChild(singletonMenu);
  singletonMenu.classList.add("hr-menu-portaled");
  // The inner popup is normally position:relative inside the zone. Re-anchor it as
  // position:absolute in PAGE coordinates (viewport rect + scroll offset) on the
  // body: this keeps it where it opened, scrolls with the page like the in-flow
  // menu did, and -- being a body child rather than nested in the handrail -- sits
  // in the root stacking context, above the fixed rail. (Fixed positioning would
  // also escape the trap but pins to the viewport: a menu opened near the bottom
  // edge would then stay off-screen and unreachable.)
  popup.style.position = "absolute";
  popup.style.left = `${rect.left + window.scrollX}px`;
  popup.style.top = `${rect.top + window.scrollY}px`;
}


// A disabled dependency-lens item explains its absence on hover (via our
// tooltip system, keyed off data-tooltip in tooltips.js) and to assistive tech
// (aria-disabled, plus the reason folded into the accessible name). An enabled
// item carries none of these.
function setLensHint(el, value, disabledText) {
  if (!el) return;
  if (value === "disabled") {
    el.setAttribute("data-tooltip", disabledText);
    el.setAttribute("aria-disabled", "true");
    const label = el.querySelector(".hr-menu-item-text");
    el.setAttribute(
      "aria-label",
      `${label ? label.textContent.trim() + " " : ""}(unavailable: ${disabledText})`
    );
  } else {
    el.removeAttribute("data-tooltip");
    el.removeAttribute("aria-disabled");
    el.removeAttribute("aria-label");
  }
}


function configureItem(el, value) {
  if (!el) return;
  if (!value) {
    el.style.display = "none";
    el.classList.remove("disabled");
    return;
  }
  el.style.display = "";
  if (value === "disabled") {
    el.classList.add("disabled");
  } else {
    el.classList.remove("disabled");
  }
}


// Set a collapse menu item's label, icon class, and icon href from state. opts
// is {collapse: [text, iconClass, href], expand: [text, iconClass, href]}; the
// icon class also drives collapseAll's toggle direction, so keep it in sync.
function syncCollapseLabel(item, collapsed, opts) {
  if (!item) return;
  const [text, iconClass, href] = collapsed ? opts.expand : opts.collapse;
  const textEl = item.querySelector(".hr-menu-item-text");
  if (textEl) textEl.textContent = text;
  const icon = item.querySelector(".icon");
  if (icon) {
    icon.classList.remove(opts.collapse[1], opts.expand[1]);
    icon.classList.add(iconClass);
  }
  const use = item.querySelector("svg use");
  if (use) use.setAttribute("href", href);
}


// Sync both collapse item labels to hr's current state. Called on menu open and
// again right after a collapse action, so the open menu updates in place.
function refreshCollapseLabels(hr) {
  if (!singletonMenu || !hr) return;
  const collapse = hr.getAttribute("data-menu-collapse");
  if (collapse && collapse !== "disabled") {
    syncCollapseLabel(
      singletonMenu.querySelector('[data-role="collapse"]'),
      hr.classList.contains("hr-collapsed"),
      { collapse: ["Collapse", "collapse", "#hr-icon-collapse"],
        expand: ["Expand", "expand", "#hr-icon-expand"] },
    );
  }
  const collapseAll = hr.getAttribute("data-menu-collapse-all");
  if (collapseAll && collapseAll !== "disabled") {
    syncCollapseLabel(
      singletonMenu.querySelector('[data-role="collapse-all"]'),
      allSubstepsCollapsed(hr),
      { collapse: ["Collapse all", "collapse-all", "#hr-icon-collapse-all"],
        expand: ["Expand all", "expand-all", "#hr-icon-expand-all"] },
    );
  }
}


// Whether every collapsible sub-step under hr is currently collapsed. Mirrors
// the query collapseAll() uses so the label matches what the action would do.
function allSubstepsCollapsed(hr) {
  const withinSubproof = hr.classList.contains("step");
  const qry = withinSubproof
    ? ":scope > .hr-content-zone > .subproof > .hr-content-zone > .step:has(.subproof)"
    : ":scope > .hr-content-zone > .step:has(.subproof)";
  const steps = hr.querySelectorAll(qry);
  if (steps.length === 0) return false;
  return Array.from(steps).every((s) => s.classList.contains("hr-collapsed"));
}


function hideMenu() {
  if (!singletonMenu) return;
  singletonMenu.style.display = "none";
  // Undo the portal: drop the inline absolute coordinates and the marker class so
  // the next open re-measures from a clean state inside the handrail zone.
  singletonMenu.classList.remove("hr-menu-portaled");
  const popup = menuPopup();
  if (popup) {
    popup.style.position = "";
    popup.style.left = "";
    popup.style.top = "";
  }
  singletonMenu.querySelectorAll(".hr-menu-item").forEach(it => it.classList.remove("active"));
  if (activeHr) {
    activeHr.classList.remove("hr-menu-open");
    const zone = activeHr.querySelector(":scope > .hr-menu-zone");
    if (zone) zone.style.display = "";
  }
  // Return the (now hidden) singleton to its build-time home in the manuscript,
  // rather than leaving it parented to <body>, so it stays a single element
  // inside the manuscript subtree (where clone/strip passes and re-renders expect
  // it) instead of an orphan on <body>.
  const home = document.querySelector(".manuscriptwrapper");
  if (home && singletonMenu.parentElement !== home) home.appendChild(singletonMenu);
  activeHr = null;
}


// Toggle the singleton menu for a handrail, mirroring a click on its dots. Used
// by the "." keyboard shortcut, which must drive the singleton rather than the
// old per-handrail menu-zone (empty until the singleton is moved into it).
export function toggleMenuFor(hr) {
  if (!hr || !hr.classList || !hr.classList.contains("hr")) return;
  if (activeHr === hr) {
    hideMenu();
  } else {
    singletonMenu = document.getElementById("hr-menu-singleton");
    showMenuFor(hr);
  }
}


// Close the open menu, if any (used by the Escape shortcut).
export function closeMenu() {
  if (activeHr) hideMenu();
}


// Whether a menu is currently open on hr (its zone holds the singleton).
export function menuOpenOn(hr) {
  return !!hr && activeHr === hr;
}


function updateHeight(entries) {
  for (const entry of entries) {
    const hr = entry.target.parentElement;
    const elementsToResize = hr.querySelectorAll(':scope > .hr-border-zone, :scope > .hr-spacer-zone, :scope > .hr-info-zone');
    elementsToResize.forEach(el => { el.style.height = `${entry.contentRect.height}px`; })
  }
};


export function toggleHandrail(target) {
  const hr = target.closest ? target.closest(".hr") : target;
  if (hr.classList.contains("hr-collapsed")) { openHandrail(hr) }
  else { closeHandrail(hr) };
};


export function openHandrail(hr) {
  hr.classList.remove("hr-collapsed");
  const rest = getRest(hr);
  rest.forEach(el => { el.classList.remove("hide"); });
  notifyHandrailToggle(hr, false);
  const icon = hr.querySelector(":scope > .hr-collapse-zone .icon.expand");
  if (!icon) return;
  icon.classList.remove("expand");
  icon.classList.add("collapse");
  const use = icon.querySelector("use");
  if (use) use.setAttribute("href", "#hr-icon-collapse");
}


export function closeHandrail(hr) {
  hr.classList.add("hr-collapsed");
  const rest = getRest(hr);
  rest.forEach(el => { el.classList.add("hide"); });
  notifyHandrailToggle(hr, true);
  const icon = hr.querySelector(":scope > .hr-collapse-zone .icon.collapse");
  if (!icon) return;
  icon.classList.remove("collapse");
  icon.classList.add("expand");
  const use = icon.querySelector("use");
  if (use) use.setAttribute("href", "#hr-icon-expand");
}


// Persist each block's/step's collapsed state per document, so a reader's
// disclosure choices survive a reload. `suppressPersist` guards the programmatic
// load-time passes (initial author collapses and the restore below) from writing
// back.
const COLLAPSE_KEY = "rsm-collapse:" + location.pathname;
let suppressPersist = false;

function loadCollapseState() {
  try {
    return JSON.parse(localStorage.getItem(COLLAPSE_KEY)) || {};
  } catch {
    return {};
  }
}

// A stable per-document persistence key for any collapsible handrail.
//
// data-nodeid is emitted only on a node's full container (the element wrapping
// heading + content). For self-wrapping blocks (theorem, proof, step, ...) that
// container IS the .hr handrail, so it carries the nodeid directly. A section is
// the exception: its nodeid lands on the <section> wrapper, while the
// collapsible handrail is the inner .heading.hr, whose body are its *siblings*
// inside that section. So the heading element itself has no nodeid, and every
// id-less collapsible block is a heading. The fallbacks below therefore only
// ever apply to headings:
//   - section id (the author's label): present on numbered sections, and more
//     stable across rebuilds than a renumbered nodeid.
//   - heading text: the document title, the generated table-of-contents, and
//     the bibliography have no <section> of their own (they climb to the
//     manuscript root), so borrowing an ancestor's nodeid would collide them
//     all onto root nodeid 0. Their text is the only handle that stays distinct.
export function collapseKey(hr) {
  const nid = hr.getAttribute("data-nodeid");
  if (nid != null) return "n:" + nid;
  const sec = hr.closest("section");
  if (sec && sec.id) return "s:" + sec.id;
  if (hr.id) return "e:" + hr.id;
  const txt = (hr.textContent || "").replace(/\s+/g, " ").trim();
  return txt ? "t:" + txt : null;
}

function persistCollapse(hr, collapsed) {
  const key = collapseKey(hr);
  if (key == null) return;
  try {
    const state = loadCollapseState();
    state[key] = collapsed;
    localStorage.setItem(COLLAPSE_KEY, JSON.stringify(state));
  } catch {
    /* private mode / storage full: persistence is best-effort */
  }
}


// Let other modules (the floating sidebar) react when a handrail is collapsed
// or expanded, so the rail can mirror the body's disclosure state instead of
// asserting a step graph the body is hiding.
function notifyHandrailToggle(hr, collapsed) {
  if (!suppressPersist) persistCollapse(hr, collapsed);
  document.dispatchEvent(
    new CustomEvent("rsm:handrail-toggle", { detail: { hr, collapsed } }),
  );
}


// Collapse, on load, every handrail the author marked with :collapsed:. Done in
// JS (not baked into the HTML) so that with scripting off the block renders
// fully expanded and the document stays a complete, readable paper.
export function collapseInitial(root) {
  suppressPersist = true;
  (root || document)
    .querySelectorAll(".hr[data-start-collapsed]")
    .forEach(hr => closeHandrail(hr));
  suppressPersist = false;
}


// Re-apply the reader's persisted collapse choices, overriding the author
// defaults from collapseInitial. Call after collapseInitial on load. Iterates
// every .hr, not just .hr[data-nodeid], because section headings carry no
// nodeid (see collapseKey) yet are collapsible and must be restored too.
export function restoreCollapse(root) {
  const state = loadCollapseState();
  suppressPersist = true;
  for (const hr of (root || document).querySelectorAll(".hr")) {
    if (hr.closest(".rsm-source")) continue;
    const key = collapseKey(hr);
    if (key == null || !(key in state)) continue;
    const wantCollapsed = state[key];
    const isCollapsed = hr.classList.contains("hr-collapsed");
    if (wantCollapsed && !isCollapsed) closeHandrail(hr);
    else if (!wantCollapsed && isCollapsed) openHandrail(hr);
  }
  suppressPersist = false;
}


// Run open/closeHandrail calls without writing the result to the reader's
// persisted collapse state. Focus mode folds the off-cone steps on enter and
// restores them on exit; those are transient view changes, not disclosure
// choices, so they must not pollute localStorage the way a manual collapse does.
export function withoutPersist(fn) {
  const prev = suppressPersist;
  suppressPersist = true;
  try {
    fn();
  } finally {
    suppressPersist = prev;
  }
}


function getRest(hr) {
  let rest;
  if (hr.classList.contains("hr-labeled")) {
    rest = hr.querySelectorAll(":scope > .hr-content-zone > :not(.hr-label)");
  } else if (hr.classList.contains("step")) {
    rest = hr.querySelectorAll(":scope > .hr-content-zone > :not(.statement)");
  } else {
    rest = Array.from(hr.parentElement.children).filter(el => { return el !== hr });
  };
  return rest;
}


export function collapseAll(target, withinSubproof = true) {
  const qry = withinSubproof
    ? ":scope > .hr-content-zone > .subproof > .hr-content-zone > .step:has(.subproof)"
    : ":scope > .hr-content-zone > .step:has(.subproof)";

  const hr = target.closest ? target.closest(".hr") : target;
  const steps = Array.from(hr.querySelectorAll(qry));
  if (!steps.length) return;

  // Direction comes from the actual substep state, not the singleton menu icon
  // (which is null until the menu has been opened, breaking the "." path).
  const allCollapsed = steps.every(s => s.classList.contains("hr-collapsed"));
  steps.forEach(s => (allCollapsed ? openHandrail(s) : closeHandrail(s)));

  // Keep the shared menu label in sync if it is currently shown for this hr;
  // otherwise showMenuFor re-derives it on the next open.
  refreshCollapseLabels(hr);
};

async function copyLink(hr) {
  let url;
  try {
    if (window.self !== window.parent) {
      url = window.parent.location.href.split('#')[0];
    } else {
      url = document.location.href.split('#')[0];
    }
  } catch (error) {
    url = document.location.href.split('#')[0];
  }

  let needs_anchor = true;
  let anchor = "";
  let link = "";
  if (!hr.classList.contains("heading")) {
    anchor = hr.id;
  } else {
    const section = hr.closest("section");
    if (!section.classList.contains("level-1")) {
      anchor = section.id;
    } else {
      needs_anchor = false;
    }
  }
  if (needs_anchor && !anchor) {
    launchToast("Could not copy link.", "error");
    return;
  }
  link = `${url}#${anchor}`
  try {
    // The mousedown that stops a menu click from selecting the handrail also
    // stops the document (notably an embedding iframe) from taking focus, and
    // clipboard.writeText requires a focused document. Re-focus the window (not
    // the handrail) so copy-link still works inside an iframe.
    window.focus();
    await navigator.clipboard.writeText(link);
    launchToast("Link copied to clipboard.", "success");
  } catch (error) {
    launchToast("Could not copy link.", "error");
  }
};


function makeToast(text, style) {
  const toast = document.createElement("div");
  toast.className = `toast ${style}`

  const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  icon.setAttribute("class", `icon ${style}`);
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttribute("href", `#hr-icon-${style}`);
  icon.appendChild(use);
  toast.appendChild(icon);

  const msg = document.createElement("span");
  msg.className = "msg";
  msg.innerText = text;
  toast.appendChild(msg);

  const spacer = document.createElement("span");
  spacer.className = "spacer";
  toast.appendChild(spacer);

  const close = document.createElement("span");
  close.className = "icon close";
  close.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
          <path d="M13 1L1 13M1 1L13 13" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        `
  close.addEventListener("click", ev => toast.remove());
  toast.appendChild(close);

  const bg = document.createElement("div");
  bg.className = "bg";
  toast.appendChild(bg);

  return toast;
}


export function launchToast(text, style = "information") {
  const toast = makeToast(text, style);
  document.querySelector(".manuscriptwrapper").appendChild(toast);
  setTimeout(() => { toast.remove(); }, 5000);
};


function showSource(hr) {
  const start = hr.getAttribute("data-source-start");
  const end = hr.getAttribute("data-source-end");
  const sourceDiv = document.querySelector(".rsm-source");

  if (!start || !end || !sourceDiv) {
    launchToast("No source available for this element.", "error");
    return;
  }

  const source = sourceDiv.textContent.slice(parseInt(start), parseInt(end));

  const modal = document.createElement("div");
  modal.className = "rsm-source-modal";
  modal.innerHTML = `
    <div class="rsm-source-modal-content">
      <div class="rsm-source-modal-actions">
        <button class="rsm-source-modal-icon-button copy-source" title="Copy">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
            <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
          </svg>
        </button>
        <button class="rsm-source-modal-icon-button close-modal" title="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 6 6 18"/>
            <path d="m6 6 12 12"/>
          </svg>
        </button>
      </div>
      <div class="rsm-source-modal-body">
        <pre>${source.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
  modal.style.display = "block";

  const closeBtn = modal.querySelector(".close-modal");
  const copyBtn = modal.querySelector(".copy-source");

  const closeModal = () => {
    modal.remove();
  };

  closeBtn.addEventListener("click", closeModal);

  modal.addEventListener("click", (ev) => {
    if (ev.target === modal) {
      closeModal();
    }
  });

  const escHandler = (ev) => {
    if (ev.key === "Escape") {
      closeModal();
      document.removeEventListener("keydown", escHandler);
    }
  };
  document.addEventListener("keydown", escHandler);

  copyBtn.addEventListener("click", async () => {
    try {
      window.focus();  // see copyLink: clipboard.writeText needs a focused document
      await navigator.clipboard.writeText(source);
      launchToast("Source copied to clipboard.", "success");
    } catch (error) {
      launchToast("Could not copy source.", "error");
    }
  });
};


export function toggleTocView(hr, menuItem) {
  const toc = hr.closest(".toc");
  if (!toc) return;
  const isTree = toc.classList.toggle("tree");
  if (isTree) tocarcs.draw(toc);
  if (menuItem) {
    const textEl = menuItem.querySelector(".hr-menu-item-text");
    if (textEl) textEl.textContent = isTree ? "View as list" : "View as tree";
  }
}

function toggleStaticView(hr, menuItem) {
  const figure = hr.closest("figure") || hr.closest("figcaption")?.parentElement;
  if (!figure) return;

  const fallback = figure.querySelector(".static-fallback");
  if (!fallback) return;

  const isShowingStatic = figure.classList.toggle("showing-static");

  // The interactive content and the fallback are siblings inside the asset's
  // content zone (a chromeless .hr-bare handrail wraps them). Toggle them there:
  // hiding the figure's direct children instead would bury the fallback inside
  // the very wrapper it lives in.
  const container = fallback.parentElement;
  for (const child of container.children) {
    if (child === fallback) continue;
    child.style.display = isShowingStatic ? "none" : "";
  }
  fallback.style.display = isShowingStatic ? "" : "none";

  const textEl = menuItem.querySelector(".hr-menu-item-text");
  if (textEl) textEl.textContent = isShowingStatic ? "Interactive" : "Static";
  const useEl = menuItem.querySelector("svg use");
  if (useEl) useEl.setAttribute("href", isShowingStatic ? "#hr-icon-play" : "#hr-icon-image");
}
