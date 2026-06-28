// shareview.js
//
// Shareable presentation-state link ("read it the way I read it"). A reader's
// constructed view (rail scope, fold/resolution state, logic-preserving reorder
// order, scroll anchor; notation rebindings and pin follow) is captured on
// demand into a ?view= URL token and restored on load, turning a private reading
// into researcher-to-researcher communication.
//
// Design (potf-44f, approved): the capture is an explicit, named act ("Copy this
// view" in the document-scope sidebar); the per-block "Copy link" stays the
// canonical anchor. State rides a QUERY param, never the #fragment (which is a
// hard contract: focus + native Back + back-pill). The token is read once on
// load and stripped via replaceState so that contract is left byte-untouched.
// The sender's view is applied TRANSIENTLY (never overwriting the recipient's
// own saved reading); a quiet "Shared view / Reset to original" pill, shown only
// when a view is loaded, returns the recipient to the pristine paper.

import { collapseKey, openHandrail, closeHandrail, withoutPersist, launchToast } from "./handrails.js";
import { extractModel, applyToBody, flatten, isValidOrder } from "./reorder.js";
import { getNotationMacros, listNotation, reRenderAll } from "./notation.js";

const SCHEMA = 1;

// --- token (de)serialization: compact, URL-safe, UTF-8 clean ----------------
function encodeToken(state) {
  const json = JSON.stringify(state);
  const utf8 = new TextEncoder().encode(json);
  let bin = "";
  for (const b of utf8) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function decodeToken(token) {
  let s = token.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  const bin = atob(s);
  const bytes = Uint8Array.from(bin, (c) => c.charCodeAt(0));
  return JSON.parse(new TextDecoder().decode(bytes));
}

// --- capture ----------------------------------------------------------------
const isDagStep = (el) => !el.closest(".calc");

// The block at the top of the reading viewport, to land the recipient where the
// sender was. The first labeled handrail whose top is at or below the viewport.
function currentAnchorId() {
  let best = null;
  let bestTop = Infinity;
  for (const hr of document.querySelectorAll(".hr[id]")) {
    if (hr.closest(".rsm-source")) continue;
    const top = hr.getBoundingClientRect().top;
    if (top >= -2 && top < bestTop) {
      best = hr.id;
      bestTop = top;
    }
  }
  return best;
}

export function captureState() {
  const state = { v: SCHEMA };

  // (Rail scope is intentionally NOT captured: prooftree.js already persists it
  // and auto-switches it by scroll, so restoring it here would fight that and
  // add no real value; the restored anchor drives the scope naturally.)

  // Folds: only deviations from the author's default (data-start-collapsed), so
  // the token stays compact and reproduces the sender's view exactly on restore.
  const folds = {};
  for (const hr of document.querySelectorAll(".hr")) {
    if (hr.closest(".rsm-source")) continue;
    const key = collapseKey(hr);
    if (!key) continue;
    const def = hr.hasAttribute("data-start-collapsed");
    const cur = hr.classList.contains("hr-collapsed");
    if (cur !== def) folds[key] = cur;
  }
  if (Object.keys(folds).length) state.folds = folds;

  // Reorder: a proof's current flat step order, only if it has actually been
  // reordered (its steps carry data-state-idx, set on reorder, and the current
  // order differs from ascending build order).
  const order = {};
  for (const proof of document.querySelectorAll(".proof[data-nodeid]")) {
    const steps = [...proof.querySelectorAll(".step")].filter(isDagStep);
    if (steps.length < 2) continue;
    if (!steps.some((s) => s.dataset.stateIdx != null)) continue;
    const cur = steps.map((s) => s.dataset.nodeid || "");
    const sorted = [...steps]
      .sort((a, b) => Number(a.dataset.stateIdx) - Number(b.dataset.stateIdx))
      .map((s) => s.dataset.nodeid || "");
    if (cur.join(",") !== sorted.join(",")) order[proof.dataset.nodeid] = cur;
  }
  if (Object.keys(order).length) state.order = order;

  // Notation rebindings: the macros the reader renamed (current != author default).
  const notation = {};
  try {
    for (const e of listNotation()) {
      if (e.current !== e.default) notation[e.macro] = e.current;
    }
  } catch {
    /* no notation in this document */
  }
  if (Object.keys(notation).length) state.notation = notation;

  const anchor = currentAnchorId();
  if (anchor) state.anchor = anchor;

  return state;
}

// --- restore ----------------------------------------------------------------
// Apply the sender's notation rebindings transiently (mutate the shared macros
// object directly, never setMacro, so the recipient's own localStorage is left
// alone) and re-typeset. Runs first so the re-render lands before fold/reorder.
function restoreNotation(state) {
  if (!state.notation) return;
  try {
    const macros = getNotationMacros();
    for (const [m, latex] of Object.entries(state.notation)) macros[m] = latex;
    reRenderAll();
  } catch {
    /* notation unavailable; skip */
  }
}

function restoreFolds(state) {
  withoutPersist(() => {
    for (const hr of document.querySelectorAll(".hr")) {
      if (hr.closest(".rsm-source")) continue;
      const key = collapseKey(hr);
      if (!key) continue;
      const target =
        state.folds && key in state.folds
          ? state.folds[key]
          : hr.hasAttribute("data-start-collapsed");
      const cur = hr.classList.contains("hr-collapsed");
      if (target && !cur) closeHandrail(hr);
      else if (!target && cur) openHandrail(hr);
    }
  });
}

function restoreOrder(state) {
  if (!state.order) return;
  for (const [pid, ord] of Object.entries(state.order)) {
    try {
      const railItem = document.querySelector(
        `.proof-rail-item[data-proof="${pid}"]`,
      );
      if (!railItem) continue;
      const model = extractModel(railItem);
      if (!model) continue;
      const rank = new Map(ord.map((id, i) => [id, i]));
      const at = (id) => (rank.has(id) ? rank.get(id) : 1e9);
      const newChildren = new Map(model.children);
      for (const [k, ids] of model.children) {
        newChildren.set(k, [...ids].sort((a, b) => at(a) - at(b)));
      }
      if (!isValidOrder(model, flatten(newChildren))) continue;
      // Tag build index so the State panel stays bound to each step after the
      // reflow (mirrors reorder.js activate).
      for (const s of model.byId.values()) s.bodyEl.dataset.stateIdx = String(s.idx);
      applyToBody(model, newChildren);
    } catch {
      /* a single unrestorable proof must not abort the rest */
    }
  }
}

function restoreAnchor(state) {
  if (!state.anchor) return;
  const el = document.getElementById(state.anchor);
  if (!el) return;
  const reduce =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  el.scrollIntoView({ behavior: reduce ? "auto" : "auto", block: "start" });
}

// Apply a decoded view. Folds and reorder do not need the math typeset, so they
// run synchronously; the scroll anchor runs last, after layout settles.
function applyState(state) {
  if (!state || state.v !== SCHEMA) {
    launchToast("This shared view was made for a different version.", "error");
    return false;
  }
  restoreNotation(state);
  restoreFolds(state);
  restoreOrder(state);
  requestAnimationFrame(() => restoreAnchor(state));
  return true;
}

// --- the "Shared view / Reset to original" pill -----------------------------
function showResetPill() {
  if (document.querySelector(".rsm-shared-pill")) return;
  const pill = document.createElement("div");
  pill.className = "rsm-shared-pill is-visible";
  pill.setAttribute("role", "status");
  pill.setAttribute("aria-live", "polite");
  pill.innerHTML =
    '<span class="rsm-shared-pill-label">Shared view</span>' +
    '<button type="button" class="rsm-shared-pill-reset">Reset to original</button>' +
    '<button type="button" class="rsm-shared-pill-x" aria-label="Dismiss">×</button>';
  // Reset returns to the pristine paper: the ?view param was already stripped,
  // so a reload restores the recipient's own (or the author's default) reading.
  pill.querySelector(".rsm-shared-pill-reset").addEventListener("click", () => {
    window.location.reload();
  });
  pill.querySelector(".rsm-shared-pill-x").addEventListener("click", () => {
    pill.remove();
  });
  document.body.appendChild(pill);
}

function stripViewParam() {
  try {
    const u = new URL(window.location.href);
    if (!u.searchParams.has("view")) return;
    u.searchParams.delete("view");
    window.history.replaceState(null, "", u.pathname + u.search + u.hash);
  } catch {
    /* replaceState unavailable: leave the URL as-is */
  }
}

// --- the "Copy this view" action --------------------------------------------
function shareUrlForCurrentView() {
  let base;
  try {
    base = window.self !== window.parent ? window.parent.location.href : window.location.href;
  } catch {
    base = window.location.href;
  }
  const u = new URL(base);
  u.hash = "";
  u.searchParams.set("view", encodeToken(captureState()));
  return u.toString();
}

async function copyView() {
  try {
    window.focus(); // clipboard.writeText needs a focused document (see copyLink)
    await navigator.clipboard.writeText(shareUrlForCurrentView());
    launchToast("View link copied: opens the paper arranged the way you have it.", "success");
  } catch {
    launchToast("Could not copy the view link.", "error");
  }
}

export function setup(root = document) {
  // Wire the document-scope "Copy this view" button (delegated, survives the
  // rail being re-rendered).
  if (!window.__shareviewWired) {
    window.__shareviewWired = true;
    document.addEventListener("click", (ev) => {
      const btn = ev.target.closest && ev.target.closest(".rail-share-view");
      if (btn) {
        ev.preventDefault();
        copyView();
      }
    });
  }

  // Restore a shared view, if the URL carries one.
  let token = null;
  try {
    token = new URLSearchParams(window.location.search).get("view");
  } catch {
    token = null;
  }
  if (!token) return;
  let ok = false;
  try {
    ok = applyState(decodeToken(token));
  } catch {
    ok = false;
  }
  // Strip the param either way so the #fragment contract and copyLink stay clean.
  stripViewParam();
  if (ok) showResetPill();
}
