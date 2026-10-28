// margin.js
//
// The right-hand margin column, shared by everything that can sit beside the
// text (captions now, asides later).
//
// Whether the column fits is decided elsewhere (sidebar.js, which knows the
// strip, the panel and the Reading width) and shown by one class on <html>:
// MARGIN_CLASS. While it is set, braiid.css widens the page by the column and
// makes each margin item absolutely positioned and MARGIN_REM wide. Without it
// items stay where the page's own CSS puts them (a caption under its block).
//
// API:
//   addMarginItem(anchor, item)  put `item` in the column, its top level with
//                                the top of `anchor`. Adding again is a no-op.
//   removeMarginItem(item)       take it out again, clearing its placement.
//   layoutMargin()               place every item now. Items are taken in the
//                                order of their anchors, and one that would
//                                overlap the item above it is pushed down below
//                                it (items never overlap).
// The column re-lays itself out on resize, on content size changes and when
// MARGIN_CLASS changes, so callers rarely need layoutMargin(). After every pass
// it dispatches "rsm:margin-layout" on document, for anything that depends on
// where the items ended up.

export const MARGIN_CLASS = "rsm-margin";
// The same numbers as --rsm-margin-width and --rsm-margin-gap in braiid.css.
export const MARGIN_REM = 15;
export const MARGIN_GAP_REM = 2;
// Space kept between two items when one is pushed down.
const STACK_GAP_REM = 0.75;

const items = new Map(); // item -> anchor
let resizeObs = null;
let frame = 0;

export function addMarginItem(anchor, item) {
  if (items.get(item) === anchor) return;
  items.set(item, anchor);
  item.classList.add("rsm-margin-item");
  if (resizeObs) {
    resizeObs.observe(item);
    resizeObs.observe(anchor);
  }
  schedule();
}

export function removeMarginItem(item) {
  if (!items.has(item)) return;
  const anchor = items.get(item);
  items.delete(item);
  item.classList.remove("rsm-margin-item");
  clear(item);
  if (resizeObs) {
    resizeObs.unobserve(item);
    resizeObs.unobserve(anchor);
  }
  schedule();
}

export function marginOn() {
  return document.documentElement.classList.contains(MARGIN_CLASS);
}

function clear(item) {
  item.style.removeProperty("left");
  item.style.removeProperty("top");
}

export function layoutMargin() {
  frame = 0;
  for (const [item, anchor] of items) {
    if (!item.isConnected || !anchor.isConnected) items.delete(item);
  }
  const live = [...items].filter(([, a]) => a.getClientRects().length);
  if (!marginOn()) {
    for (const [item] of items) clear(item);
  } else if (live.length) {
    place(live);
  }
  document.dispatchEvent(new CustomEvent("rsm:margin-layout"));
}

function place(live) {
  const rem = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
  // Measure every item at left/top 0 first: the difference between where it
  // lands and where it should be is the offset to set, whatever its containing
  // block happens to be.
  for (const [item] of live) {
    item.style.left = "0px";
    item.style.top = "0px";
  }
  const rows = live.map(([item, anchor]) => {
    const column = anchor.closest(".manuscript") || document.body;
    return {
      item,
      zero: item.getBoundingClientRect(),
      anchorTop: anchor.getBoundingClientRect().top,
      x: column.getBoundingClientRect().right + MARGIN_GAP_REM * rem,
    };
  });
  rows.sort((a, b) => a.anchorTop - b.anchorTop);
  let floor = -Infinity;
  for (const r of rows) {
    const top = Math.max(r.anchorTop, floor);
    r.item.style.left = r.x - r.zero.left + "px";
    r.item.style.top = top - r.zero.top + "px";
    floor = top + r.zero.height + STACK_GAP_REM * rem;
  }
}

function schedule() {
  if (!frame) frame = requestAnimationFrame(layoutMargin);
}

let ready = false;
export function setup() {
  if (ready) return;
  ready = true;
  const html = document.documentElement;
  new MutationObserver(schedule).observe(html, {
    attributes: true,
    attributeFilter: ["class", "data-reading-measure"],
  });
  window.addEventListener("resize", schedule);
  if (window.ResizeObserver) {
    resizeObs = new ResizeObserver(schedule);
    for (const [item, anchor] of items) {
      resizeObs.observe(item);
      resizeObs.observe(anchor);
    }
    for (const m of document.querySelectorAll(".manuscript")) resizeObs.observe(m);
  }
  // The column slides when the panel opens or the Reading width changes: follow
  // it frame by frame until the slide ends.
  let sliding = 0;
  const follow = () => {
    layoutMargin();
    if (sliding) frame = requestAnimationFrame(follow);
  };
  document.addEventListener("transitionrun", (ev) => {
    if (!ev.target.matches || !ev.target.matches("main.manuscriptwrapper")) return;
    if (!sliding++) {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(follow);
    }
  });
  const stop = (ev) => {
    if (!ev.target.matches || !ev.target.matches("main.manuscriptwrapper")) return;
    sliding = Math.max(0, sliding - 1);
    if (!sliding) schedule();
  };
  document.addEventListener("transitionend", stop);
  document.addEventListener("transitioncancel", stop);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(schedule);
  window.addEventListener("load", schedule);
  schedule();
}
