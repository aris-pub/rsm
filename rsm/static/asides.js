// asides.js
//
// An aside is written below the block that calls it (the transformer puts it
// there), so with scripting off it is simply shown there, open. Once this
// script runs, html.has-asides is set (the builder's pre-paint script sets it
// even earlier, so there is no jump) and braiid.css takes over:
//
// - With the margin column on (html.rsm-margin, see margin.js), every aside sits
//   in the column level with its marker, sharing the column and its push-down
//   with captions.
// - Otherwise each aside is hidden, and its marker opens and closes it in place
//   below its block. On pointer devices, hovering the marker of a closed aside
//   shows a preview of it.
//
// Either way, hovering or focusing a marker lights its aside and the other way
// around (OPEN and LIT classes below).

import { addMarginItem, marginOn } from "./margin.js";

export const READY_CLASS = "has-asides";
const OPEN = "rsm-aside-open";
const LIT = "rsm-aside-lit";
const MARKERS = '.manuscriptwrapper a.note-marker[data-note-kind="aside"]';

let listening = false;

function asideOf(marker) {
  const id = (marker.getAttribute("href") || "").replace(/^#/, "");
  const el = id && document.getElementById(id);
  return el && el.matches(".aside") ? el : null;
}

function markerOf(aside) {
  return document.getElementById("call-" + aside.id);
}

export function setup(root = document) {
  document.documentElement.classList.add(READY_CLASS);
  for (const marker of root.querySelectorAll(MARKERS)) {
    const aside = asideOf(marker);
    if (!aside) continue;
    marker.setAttribute("aria-controls", aside.id);
    addMarginItem(marker, aside);
  }
  syncExpanded();
  if (listening) return;
  listening = true;

  document.addEventListener("click", onClick);
  document.addEventListener("keydown", onKeydown);
  document.addEventListener("mouseover", onPointer);
  document.addEventListener("mouseout", onPointer);
  document.addEventListener("focusin", onFocus);
  document.addEventListener("focusout", onFocus);
  window.addEventListener("hashchange", openHashTarget);
  openHashTarget();
  // The marker is a toggle only while the column is off.
  new MutationObserver(syncExpanded).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"],
  });
}

function syncExpanded() {
  const toggles = !marginOn();
  for (const marker of document.querySelectorAll(MARKERS)) {
    const aside = asideOf(marker);
    if (!aside) continue;
    if (toggles) {
      marker.setAttribute("aria-expanded", String(aside.classList.contains(OPEN)));
    } else {
      marker.removeAttribute("aria-expanded");
    }
  }
}

export function toggle(marker, open) {
  const aside = asideOf(marker);
  if (!aside) return;
  const now = open === undefined ? !aside.classList.contains(OPEN) : open;
  aside.classList.toggle(OPEN, now);
  if (!marginOn()) marker.setAttribute("aria-expanded", String(now));
  if (now) closePreview(marker);
}

function closestMarker(target) {
  return target && target.closest ? target.closest(MARKERS) : null;
}

function onClick(ev) {
  const marker = closestMarker(ev.target);
  if (!marker || !asideOf(marker)) return;
  // The aside is right beside the marker or opens below its block, so the
  // link's jump would only move the reader away from the text.
  ev.preventDefault();
  if (!marginOn()) toggle(marker);
}

function onKeydown(ev) {
  if (ev.key !== " " && ev.key !== "Spacebar") return;
  const marker = closestMarker(ev.target);
  if (!marker || !asideOf(marker)) return;
  // Enter already clicks a link. Space is added because the marker also
  // carries aria-expanded, and readers expect Space to work on a toggle.
  ev.preventDefault();
  ev.stopPropagation();
  if (!marginOn()) toggle(marker);
}

function light(marker, aside, on) {
  marker.classList.toggle(LIT, on);
  aside.classList.toggle(LIT, on);
}

function pairFrom(target) {
  if (!target || !target.closest) return null;
  const marker = target.closest(MARKERS);
  if (marker) {
    const aside = asideOf(marker);
    return aside ? { marker, aside } : null;
  }
  const aside = target.closest(".manuscriptwrapper .aside");
  if (!aside) return null;
  const m = markerOf(aside);
  return m ? { marker: m, aside } : null;
}

function onPointer(ev) {
  const pair = pairFrom(ev.target);
  if (!pair) return;
  const into = pairFrom(ev.relatedTarget);
  if (into && into.aside === pair.aside) return;
  light(pair.marker, pair.aside, ev.type === "mouseover");
}

function onFocus(ev) {
  const marker = closestMarker(ev.target);
  if (!marker) return;
  const aside = asideOf(marker);
  if (aside) light(marker, aside, ev.type === "focusin");
}

function openHashTarget() {
  const id = decodeURIComponent((location.hash || "").slice(1));
  const aside = id && document.getElementById(id);
  if (!aside || !aside.matches(".aside")) return;
  const marker = markerOf(aside);
  if (marker) toggle(marker, true);
}

// The hover preview of a closed aside is the reference preview (tooltips.js).
function closePreview(marker) {
  const $ = window.jQuery;
  if (!$ || !marker.classList.contains("tooltipstered")) return;
  try {
    $(marker).tooltipster("close");
  } catch (err) {
    // no tooltip instance yet
  }
}

export function previewWanted(marker) {
  const aside = asideOf(marker);
  if (!aside || marginOn()) return false;
  if (aside.classList.contains(OPEN)) return false;
  return window.matchMedia("(hover: hover)").matches;
}
