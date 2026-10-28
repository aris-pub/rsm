// minimap.js
//
// A document map that replaces the page's native scrollbar: a thin strip at the
// right edge of the viewport with a mark per section and figure and a box over
// the part of the document on screen. It works as a scrollbar (click or drag to
// scroll) and as a map (hover a mark to see its label, click it to go there).
// Ported from Studio's ScrollbarMinimap.vue, which scrolls an inner pane; here
// the document itself scrolls.
//
// The native scrollbar is hidden only once the strip has mounted (the
// rsm-minimap-on class on <html>), so with scripting off, or if mounting fails,
// the reader keeps the native scrollbar.
//
// Off switches: the author's :config: { :minimap: false } (body[data-minimap])
// and the reader's Reading view toggle (html[data-reading-minimap], persisted in
// the rsm-reading localStorage object by prooftree.js).

const PHONE = "(max-width: 767px)";
const REDUCED_MOTION = "(prefers-reduced-motion: reduce)";
const HOVER_PX = 12;
const TOUCH_HOVER_PX = 24;
const NEAR_PX = 8;
const DRAG_PX = 3;
const FADE_MS = 1200;
const DEBOUNCE_MS = 100;
const READING_KEY = "rsm-reading";

let mm = null;
let switchObserver = null;

export function setup(root = document) {
  // Studio mounts RSM into its own scrolling pane and draws its own minimap.
  if (root !== document) return;
  if (!document.body || document.body.getAttribute("data-minimap") === "false") return;
  if (!document.querySelector("main.manuscriptwrapper")) return;
  watchReaderSwitch();
  if (!readerTurnedOff()) mount();
}

export function isMounted() {
  return mm !== null;
}

function readerTurnedOff() {
  const attr = document.documentElement.getAttribute("data-reading-minimap");
  if (attr) return attr === "off";
  try {
    const prefs = JSON.parse(localStorage.getItem(READING_KEY) || "{}") || {};
    return prefs.minimap === "off";
  } catch (e) {
    return false;
  }
}

function watchReaderSwitch() {
  if (switchObserver) return;
  switchObserver = new MutationObserver(() => {
    if (readerTurnedOff()) unmount();
    else mount();
  });
  switchObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-reading-minimap"],
  });
}

// ---------------------------------------------------------------------------
// Marks

function headingText(section) {
  const h =
    section.querySelector(":scope > .heading.hr .hr-content-zone :is(h1,h2,h3,h4,h5,h6)") ||
    section.querySelector(":scope > :is(h1,h2,h3,h4,h5,h6)") ||
    section.querySelector(":scope > .heading :is(h1,h2,h3,h4,h5,h6)");
  return h ? h.textContent.replace(/\s+/g, " ").trim() : "";
}

const FIGURE_KINDS = { html: "Widget", video: "Video", figure: "Figure" };

function figureKind(fig) {
  return Object.keys(FIGURE_KINDS).find((c) => fig.classList.contains(c));
}

// The caption's label ("Widget 4.2"). Without a caption, the same words from
// the block's number, or the kind word alone for an unnumbered block.
function figureLabel(fig) {
  const label = fig.querySelector(":scope > figcaption .label");
  const text = label ? label.textContent.replace(/\s+/g, " ").trim().replace(/\.$/, "") : "";
  if (text) return text;
  const word = FIGURE_KINDS[figureKind(fig)];
  const number = fig.getAttribute("data-number");
  return number ? word + " " + number : word;
}

// Elements inside the sidebar, previews or the strip itself are not part of the
// document's flow.
function inChrome(el) {
  return !!el.closest(".proof-rail, .rail-strip, .rsm-minimap, .tooltipster-base");
}

function laidOut(el) {
  return el.getClientRects().length > 0;
}

function collectMarks(main) {
  const sh = document.documentElement.scrollHeight || 1;
  const fraction = (el) => {
    const top = el.getBoundingClientRect().top + window.scrollY;
    return Math.max(0, Math.min(1, top / sh));
  };
  const out = [];

  // The manuscript itself is the outermost section (level-1): it starts at the
  // top of the page and its "heading" is the title, so it gets no mark.
  const sections = [...main.querySelectorAll("section")].filter(
    (s) => !inChrome(s) && laidOut(s),
  );
  const levelOf = (s) => {
    const c = [...s.classList].find((x) => /^level-\d+$/.test(x));
    return c ? parseInt(c.slice(6), 10) : 2;
  };
  const real = sections.filter((s) => levelOf(s) > 1);
  const top = real.length ? Math.min(...real.map(levelOf)) : 2;
  for (const s of real) {
    out.push({
      el: s,
      type: "section",
      top: levelOf(s) === top,
      label: headingText(s) || "Section",
      pos: fraction(s),
    });
  }

  // Every :figure:, :html: and :video: block, with or without a caption or a
  // number. A <figure> inside a widget's own HTML is part of that widget, not
  // an RSM block (it has no data-nodeid).
  for (const fig of main.querySelectorAll("figure[data-nodeid]")) {
    if (!figureKind(fig) || inChrome(fig) || fig.parentElement.closest("figure")) continue;
    if (!laidOut(fig)) continue;
    out.push({ el: fig, type: "figure", label: figureLabel(fig), pos: fraction(fig) });
  }

  out.sort((a, b) => a.pos - b.pos);
  return out;
}

// ---------------------------------------------------------------------------
// Mount / unmount

function mount() {
  if (mm) return;
  const main = document.querySelector("main.manuscriptwrapper");
  if (!main) return;
  try {
    mm = build(main);
  } catch (err) {
    console.error("Mounting the minimap FAILED!", err);
    document.querySelectorAll(".rsm-minimap").forEach((n) => n.remove());
    mm = null;
    document.documentElement.classList.remove("rsm-minimap-on");
  }
}

function unmount() {
  if (!mm) return;
  mm.teardown();
  mm = null;
}

function build(main) {
  const html = document.documentElement;
  const phoneMql = window.matchMedia(PHONE);
  const motionMql = window.matchMedia(REDUCED_MOTION);

  const nav = document.createElement("nav");
  nav.className = "rsm-minimap";
  nav.setAttribute("aria-label", "Document map");
  nav.innerHTML =
    '<div class="rsm-minimap-track" aria-hidden="true">' +
    '<div class="rsm-minimap-box"></div>' +
    '<div class="rsm-minimap-marks"></div>' +
    '<div class="rsm-minimap-tip"></div>' +
    "</div>" +
    '<ul class="rsm-minimap-links"></ul>';
  const track = nav.querySelector(".rsm-minimap-track");
  const box = nav.querySelector(".rsm-minimap-box");
  const marksEl = nav.querySelector(".rsm-minimap-marks");
  const tip = nav.querySelector(".rsm-minimap-tip");
  const list = nav.querySelector(".rsm-minimap-links");

  // Right after the sidebar strip, so Tab reaches the map before the text (the
  // skip link that leads the strip still jumps past both). Without a sidebar the
  // map leads the manuscript.
  const railStrip = main.querySelector(":scope > .rail-strip");
  if (railStrip) railStrip.after(nav);
  else main.prepend(nav);

  let marks = [];
  let hovered = -1;
  let focused = -1;
  let current = 0;
  let lastJumped = null;
  let drag = null;
  let sleepTimer = null;
  let tipTimer = null;
  let computeTimer = null;
  let frame = 0;

  const trackRect = () => track.getBoundingClientRect();
  const behavior = () => (motionMql.matches ? "auto" : "smooth");

  function render(next) {
    const same =
      next.length === marks.length && next.every((m, i) => m.el === marks[i].el);
    if (same) {
      next.forEach((m, i) => {
        marks[i].pos = m.pos;
        marks[i].label = m.label;
        marks[i].node.style.top = m.pos * 100 + "%";
        if (marks[i].link.textContent !== m.label) marks[i].link.textContent = m.label;
      });
      return;
    }
    const focusedEl = focused >= 0 && marks[focused] ? marks[focused].el : null;
    const currentEl = marks[current] ? marks[current].el : null;
    marksEl.textContent = "";
    list.textContent = "";
    next.forEach((m, i) => {
      const node = document.createElement("div");
      node.className =
        "rsm-minimap-mark " + (m.type === "section" ? "mm-section" : "mm-figure") +
        (m.top ? " mm-top" : "");
      node.style.top = m.pos * 100 + "%";
      marksEl.appendChild(node);
      const li = document.createElement("li");
      const link = document.createElement("a");
      if (m.el.id) link.href = "#" + m.el.id;
      else link.setAttribute("role", "link");
      link.textContent = m.label;
      link.dataset.idx = String(i);
      link.tabIndex = -1;
      li.appendChild(link);
      list.appendChild(li);
      m.node = node;
      m.link = link;
    });
    marks = next;
    hovered = -1;
    let ci = currentEl ? marks.findIndex((m) => m.el === currentEl) : -1;
    current = ci >= 0 ? ci : 0;
    if (marks[current]) marks[current].link.tabIndex = 0;
    focused = -1;
    if (focusedEl) {
      const fi = marks.findIndex((m) => m.el === focusedEl);
      if (fi >= 0) focusMark(fi);
    }
    paintHover();
  }

  function compute() {
    render(collectMarks(main));
    updateViewport();
  }

  function scheduleCompute() {
    clearTimeout(computeTimer);
    computeTimer = setTimeout(compute, DEBOUNCE_MS);
  }

  function updateViewport() {
    frame = 0;
    const sh = html.scrollHeight || 1;
    box.style.top = (window.scrollY / sh) * 100 + "%";
    box.style.height = Math.min(1, window.innerHeight / sh) * 100 + "%";
  }

  function onScroll() {
    if (!frame) frame = requestAnimationFrame(updateViewport);
    if (phoneMql.matches) wake();
  }

  // ---- phones: the strip shows only while the page scrolls or is touched ----
  function wake() {
    nav.classList.add("is-awake");
    clearTimeout(sleepTimer);
    sleepTimer = setTimeout(sleep, FADE_MS);
  }
  function sleep() {
    if (drag) return;
    nav.classList.remove("is-awake");
    setHovered(-1);
  }

  // ---- hover and labels ----
  function nearest(y, radius) {
    const h = trackRect().height;
    let best = -1;
    let bestDist = Infinity;
    marks.forEach((m, i) => {
      const d = Math.abs(m.pos * h - y);
      if (d < radius && d < bestDist) {
        best = i;
        bestDist = d;
      }
    });
    return best;
  }

  function showTip(i) {
    clearTimeout(tipTimer);
    if (i < 0 || !marks[i]) {
      tip.classList.remove("is-visible");
      return;
    }
    tip.textContent = marks[i].label;
    tip.style.top = marks[i].pos * 100 + "%";
    tip.classList.add("is-visible");
  }

  function paintHover() {
    const active = hovered >= 0 ? hovered : focused;
    nav.classList.toggle("has-hovered", active >= 0);
    const h = trackRect().height;
    marks.forEach((m, i) => {
      m.node.classList.toggle("is-hovered", i === active);
      m.node.classList.toggle("is-focused", i === focused);
      const near = active >= 0 && i !== active && Math.abs(m.pos - marks[active].pos) * h < NEAR_PX;
      m.node.classList.toggle("is-near", near);
    });
    showTip(active);
  }

  function setHovered(i) {
    if (i === hovered) return;
    hovered = i;
    paintHover();
  }

  // ---- scrolling ----
  function scrollToY(y, how) {
    const h = trackRect().height || 1;
    const f = Math.max(0, Math.min(1, y / h));
    window.scrollTo({ top: f * html.scrollHeight - window.innerHeight / 2, behavior: how });
  }

  function jumpTo(i) {
    const m = marks[i];
    if (!m) return;
    const top = m.el.getBoundingClientRect().top + window.scrollY;
    window.scrollTo({ top: top - window.innerHeight / 2, behavior: behavior() });
    lastJumped = m.el;
  }

  function localY(ev) {
    return ev.clientY - trackRect().top;
  }

  function onPointerDown(ev) {
    if (ev.button !== 0) return;
    ev.preventDefault();
    try {
      nav.setPointerCapture(ev.pointerId);
    } catch (e) {
      /* capture is best effort */
    }
    const y = localY(ev);
    drag = { startY: y, moved: false, touch: ev.pointerType !== "mouse" };
    nav.classList.add("is-touching");
    if (phoneMql.matches) wake();
    if (drag.touch) setHovered(nearest(y, TOUCH_HOVER_PX));
  }

  function onPointerMove(ev) {
    const y = localY(ev);
    if (drag) {
      if (!drag.moved && Math.abs(y - drag.startY) > DRAG_PX) {
        drag.moved = true;
        nav.classList.add("is-dragging");
        setHovered(-1);
      }
      if (drag.moved) scrollToY(y, "instant");
      return;
    }
    setHovered(nearest(y, ev.pointerType === "mouse" ? HOVER_PX : TOUCH_HOVER_PX));
  }

  function endDrag() {
    drag = null;
    nav.classList.remove("is-touching", "is-dragging");
    if (phoneMql.matches) wake();
  }

  function onPointerUp(ev) {
    if (!drag) return;
    const d = drag;
    const y = localY(ev);
    if (!d.moved) {
      const i = nearest(y, d.touch ? TOUCH_HOVER_PX : HOVER_PX);
      if (i >= 0) jumpTo(i);
      else scrollToY(y, "instant");
    }
    endDrag();
    if (d.touch) {
      clearTimeout(tipTimer);
      tipTimer = setTimeout(() => setHovered(-1), 900);
    }
  }

  function onPointerCancel() {
    if (drag) endDrag();
  }

  function onPointerLeave() {
    if (!drag) setHovered(-1);
  }

  // ---- keyboard ----
  function focusMark(i) {
    if (!marks[i]) return;
    if (marks[current]) marks[current].link.tabIndex = -1;
    current = i;
    marks[i].link.tabIndex = 0;
    marks[i].link.focus({ preventScroll: true });
  }

  function onFocusIn(ev) {
    const link = ev.target.closest && ev.target.closest(".rsm-minimap-links a");
    if (!link) return;
    focused = parseInt(link.dataset.idx, 10);
    if (marks[current] && current !== focused) marks[current].link.tabIndex = -1;
    current = focused;
    link.tabIndex = 0;
    paintHover();
  }

  function onFocusOut(ev) {
    // Moving between two marks keeps focus in the map.
    if (ev.relatedTarget && nav.contains(ev.relatedTarget)) return;
    focused = -1;
    paintHover();
  }

  function onKeyDown(ev) {
    if (focused < 0) return;
    const last = marks.length - 1;
    let handled = true;
    switch (ev.key) {
      case "ArrowDown":
      case "ArrowRight":
        focusMark(Math.min(last, focused + 1));
        break;
      case "ArrowUp":
      case "ArrowLeft":
        focusMark(Math.max(0, focused - 1));
        break;
      case "Home":
        focusMark(0);
        break;
      case "End":
        focusMark(last);
        break;
      case " ":
      case "Enter":
        jumpTo(focused);
        break;
      case "Escape": {
        // Leave the map for the text, at the block last jumped to.
        const target = lastJumped;
        if (target) {
          if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
          target.focus({ preventScroll: true });
        } else document.activeElement.blur();
        break;
      }
      default:
        handled = false;
    }
    if (handled) {
      ev.preventDefault();
      ev.stopPropagation();
    }
  }

  function onLinkClick(ev) {
    const link = ev.target.closest && ev.target.closest(".rsm-minimap-links a");
    if (!link) return;
    // Screen readers activate the link with a click: scroll there without
    // changing the URL, as Enter does.
    ev.preventDefault();
    jumpTo(parseInt(link.dataset.idx, 10));
  }

  nav.addEventListener("pointerdown", onPointerDown);
  nav.addEventListener("pointermove", onPointerMove);
  nav.addEventListener("pointerup", onPointerUp);
  nav.addEventListener("pointercancel", onPointerCancel);
  nav.addEventListener("pointerleave", onPointerLeave);
  nav.addEventListener("keydown", onKeyDown);
  nav.addEventListener("focusin", onFocusIn);
  nav.addEventListener("focusout", onFocusOut);
  list.addEventListener("click", onLinkClick);
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", scheduleCompute);
  window.addEventListener("load", scheduleCompute);
  document.addEventListener("rsm:handrail-toggle", scheduleCompute);
  const ro = typeof ResizeObserver !== "undefined" ? new ResizeObserver(scheduleCompute) : null;
  if (ro) ro.observe(main);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => mm && scheduleCompute());

  compute();
  html.classList.add("rsm-minimap-on");
  // Hiding the scrollbar widens the viewport, and the sidebar places the column
  // from the viewport width on resize.
  window.dispatchEvent(new Event("resize"));

  function teardown() {
    clearTimeout(sleepTimer);
    clearTimeout(tipTimer);
    clearTimeout(computeTimer);
    if (frame) cancelAnimationFrame(frame);
    window.removeEventListener("scroll", onScroll);
    window.removeEventListener("resize", scheduleCompute);
    window.removeEventListener("load", scheduleCompute);
    document.removeEventListener("rsm:handrail-toggle", scheduleCompute);
    if (ro) ro.disconnect();
    nav.remove();
    html.classList.remove("rsm-minimap-on");
    window.dispatchEvent(new Event("resize"));
  }

  return { nav, teardown, compute };
}
