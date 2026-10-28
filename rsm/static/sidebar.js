// sidebar.js
//
// The strip that opens the sidebar's panel, and the page layout around it.
//
// Wide windows: an icon strip in the left margin, one icon per view (Contents,
// Notation, Proof steps, Proof state, Pinned, Reading) plus Copy link. A view
// opens as a panel beside the strip. The panel never covers the text: the
// column moves right (CSS, keyed on html.rail-open). The block at the top of
// the window keeps its place while the column moves. Clicking the open view's icon again, or Escape,
// closes the panel.
//
// Phones (below 768px): the strip becomes a bottom bar with one labelled button
// per scope (Document, Proof, Pinned, Reading, Copy link), and a view opens as
// a sheet above it; a scope with two views switches between them with text
// tabs at the top of the sheet.
//
// prooftree.js owns the panel's content and calls setupStrip with its view API.

import { MARGIN_CLASS, MARGIN_REM, MARGIN_GAP_REM } from "./margin.js";

const PHONE = "(max-width: 767px)";

// Geometry, in rem (the same numbers as the --rail-* tokens in braiid.css):
// the strip's left edge plus its width and gap; the panel's width; the
// window's right margin.
const STRIP_REM = 1 + 3 + 0.5;
const PANEL_REM = 17;
const RIGHT_REM = 1.5;

// Each strip button's view: [scope, sub-view] (sub-view null: the scope's own
// current one, or none).
const VIEWS = {
  contents: ["document", "doc-map"],
  notation: ["document", "notation"],
  steps: ["proof", "proof-map"],
  state: ["proof", "state"],
  document: ["document", null],
  proof: ["proof", null],
  pinned: ["pinned", null],
  reading: ["reading", null],
};

export function setupStrip(strip, rail, api) {
  const html = document.documentElement;
  const mql = window.matchMedia(PHONE);
  html.classList.add("has-rail");

  let view = null; // the open (or last) view id
  let open = false;

  const buttons = () => [...strip.querySelectorAll(".rail-strip-btn[data-view]")];
  const isPhone = () => mql.matches;
  const mode = () => (isPhone() ? "grouped" : "split");
  const visible = (b) => b.dataset.mode === "both" || b.dataset.mode === mode();
  const has = (id) => buttons().some((b) => b.dataset.view === id && visible(b));

  function subviewNow(scope) {
    if (scope === "document") {
      return rail.classList.contains("doc-view-notation") ? "notation" : "doc-map";
    }
    if (scope === "proof") {
      return rail.classList.contains("proof-view-state") ? "state" : "proof-map";
    }
    return null;
  }

  // The same view in the other arrangement: a phone's Document is the desktop's
  // Contents or Notation (whichever is showing), and back.
  function translate(id) {
    if (!id) return id;
    if (isPhone()) {
      if (id === "contents" || id === "notation") return "document";
      if (id === "steps" || id === "state") return "proof";
      return id;
    }
    if (id === "document") {
      const wantsNotation = subviewNow("document") === "notation";
      if (wantsNotation && has("notation")) return "notation";
      return has("contents") ? "contents" : "notation";
    }
    if (id === "proof") return subviewNow("proof") === "state" ? "state" : "steps";
    return id;
  }

  // ---- the panel head: what is showing and what it shows ----
  const title = rail.querySelector(".rail-title");
  const hint = rail.querySelector(".rail-hint");
  function paintHead() {
    const scope = api.currentScope();
    const sub = subviewNow(scope);
    // On phones a scope with two views shows text tabs instead of the title.
    const row = rail.querySelector(".rail-subtabs-" + scope);
    rail.classList.toggle("has-tabs", !!row && isPhone());
    let name = "";
    let text = "";
    const btn = buttons().find((b) => b.dataset.view === view && visible(b));
    if (btn) name = btn.getAttribute("aria-label") || "";
    if (sub) {
      const tab = row && row.querySelector(`.rail-tab[data-view="${sub}"]`);
      const split = buttons().find(
        (b) => b.dataset.mode === "split" && VIEWS[b.dataset.view][1] === sub,
      );
      text = (tab && tab.dataset.hint) || (split && split.dataset.hint) || "";
      if (split && isPhone() && !row) name = split.getAttribute("aria-label") || name;
    } else if (btn) {
      text = btn.dataset.hint || "";
    }
    if (title) title.textContent = name;
    if (hint) {
      hint.textContent = text;
      hint.hidden = !text;
    }
  }

  function paintStrip() {
    const scope = api.currentScope();
    const sub = subviewNow(scope);
    for (const b of buttons()) {
      const [bScope, bSub] = VIEWS[b.dataset.view] || [];
      const on = open && visible(b) && bScope === scope && (!bSub || bSub === sub);
      b.setAttribute("aria-pressed", String(on));
    }
  }

  // ---- keeping the reader's place while the column moves ----
  function anchorTop() {
    const els = document.querySelectorAll(
      ".manuscript .hr, .manuscript h2, .manuscript figure",
    );
    let best = null;
    let bestTop = Infinity;
    for (const el of els) {
      const r = el.getBoundingClientRect();
      if (!r.height) continue;
      if (r.bottom > 0 && r.top > -40 && r.top < bestTop) {
        bestTop = r.top;
        best = el;
      }
    }
    return best ? { el: best, top: bestTop } : null;
  }
  // Follow the anchor while the column animates. Anything else that scrolls
  // the page meanwhile (the reader, a jump) wins: holding stops.
  function holdAnchor(a) {
    if (!a) return;
    const t0 = performance.now();
    let expected = window.scrollY;
    const step = () => {
      if (Math.abs(window.scrollY - expected) > 1) return;
      const d = a.el.getBoundingClientRect().top - a.top;
      if (Math.abs(d) > 0.5) window.scrollBy(0, d);
      expected = window.scrollY;
      if (performance.now() - t0 < 450) requestAnimationFrame(step);
    };
    step();
  }

  // Place the column: right of the strip, centred in the space left when that
  // space allows; with a view open, next to the panel.
  //
  // The margin column (margin.js) is on only when it fits whole beside the
  // text column at the current Reading width. The page then widens by the
  // column, and the text keeps its centred place unless that would push the
  // column off the right edge, in which case it moves left just enough.
  function layout() {
    if (isPhone()) {
      html.style.removeProperty("--rail-ml");
      html.style.removeProperty("--rail-mw");
      html.classList.remove(MARGIN_CLASS);
      return;
    }
    const rem = parseFloat(getComputedStyle(html).fontSize) || 16;
    const vw = html.clientWidth;
    const colRem =
      parseFloat(getComputedStyle(html).getPropertyValue("--content-max-width")) || 54;
    const left = (open ? STRIP_REM + PANEL_REM : STRIP_REM + 1) * rem;
    const right = RIGHT_REM * rem;
    const avail = vw - left - right;
    const width = Math.min(colRem * rem, avail);
    const extra = (MARGIN_REM + MARGIN_GAP_REM) * rem;
    const margin = width + extra <= avail;
    const centred = Math.max(0, (avail - width) / 2);
    const shift = margin ? Math.min(centred, avail - width - extra) : centred;
    const ml = left + (open ? 0 : shift);
    html.style.setProperty("--rail-ml", ml + "px");
    html.style.setProperty("--rail-mw", width + (margin ? extra : 0) + "px");
    html.classList.toggle(MARGIN_CLASS, margin);
  }
  // A graph (Contents, Proof steps) scales down to fit what is left of the
  // panel below its head, so it is never cut off.
  function fitGraphs() {
    if (!open) return;
    const cs = getComputedStyle(rail);
    const box = rail.getBoundingClientRect();
    const maxH = parseFloat(cs.maxHeight);
    const bottom = box.top + (Number.isFinite(maxH) ? Math.max(maxH, box.height) : box.height);
    for (const svg of rail.querySelectorAll("svg.toc-tree")) {
      if (!svg.getClientRects().length) continue;
      svg.style.maxHeight = "";
      const section = svg.closest(".rail-section");
      const pad =
        parseFloat(cs.paddingBottom) +
        (section ? parseFloat(getComputedStyle(section).paddingBottom) : 0) +
        parseFloat(cs.borderBottomWidth);
      // Measured from the top of the graph's section (just below the head),
      // not the graph itself, which may already overflow it.
      const top = section
        ? section.getBoundingClientRect().top + parseFloat(getComputedStyle(section).paddingTop)
        : svg.getBoundingClientRect().top;
      const room = bottom - pad - top;
      if (room > 0) svg.style.maxHeight = Math.floor(room) + "px";
    }
  }
  window.addEventListener("resize", () => {
    layout();
    requestAnimationFrame(fitGraphs);
  });
  // The reading width changes the column.
  new MutationObserver(layout).observe(html, {
    attributes: true,
    attributeFilter: ["data-reading-measure"],
  });

  function setOpen(on, { persist = true } = {}) {
    const anchor = !isPhone() && on !== open ? anchorTop() : null;
    open = on;
    html.classList.toggle("rail-open", on);
    rail.classList.toggle("open", on);
    paintStrip();
    layout();
    requestAnimationFrame(fitGraphs);
    holdAnchor(anchor);
    if (persist && !isPhone()) api.saveLayout({ view: view });
  }

  function select(id) {
    const [scope, sub] = VIEWS[id];
    api.selectScope(scope);
    if (sub) api.selectSubview(sub);
    view = id;
    paintHead();
    paintStrip();
    requestAnimationFrame(fitGraphs);
  }

  // Open a view; the open view's own button closes it.
  function openView(id, { toggle = true } = {}) {
    id = translate(id);
    if (!VIEWS[id] || !has(id)) return;
    if (toggle && open && id === view) {
      setOpen(false);
      return;
    }
    select(id);
    setOpen(true);
    if (isPhone()) rail.scrollTop = 0;
  }

  strip.addEventListener("click", (ev) => {
    const b = ev.target.closest(".rail-strip-btn");
    if (!b || !b.dataset.view) return; // Copy link: shareview.js
    openView(b.dataset.view);
  });

  document.addEventListener("keydown", (ev) => {
    if (ev.key !== "Escape" || !open || ev.defaultPrevented) return;
    // Escape belongs to an open handrail menu, focus mode or reorder first.
    if (document.querySelector(".hr-menu-open, .proof-rail.focusing")) return;
    const inside = rail.contains(document.activeElement);
    setOpen(false);
    if (inside) strip.querySelector(`.rail-strip-btn[data-view="${view}"]`)?.focus();
  });

  // A sub-view chosen in the sheet's text tabs.
  rail.addEventListener("rail:subview", () => {
    paintHead();
    paintStrip();
    requestAnimationFrame(fitGraphs);
  });

  // Other modules ask for a view: { view, open }. Without open, the view is
  // switched only if the panel is already open, so nothing moves the text the
  // reader did not ask for.
  document.addEventListener("rail:show", (ev) => {
    const d = ev.detail || {};
    const sub = VIEWS[d.view] && VIEWS[d.view][1];
    const id = translate(d.view);
    if (!VIEWS[id] || !has(id)) return;
    // A specific view (Notation, say) picks its sub-view first, so a phone's
    // Document sheet opens on that tab. Done only after the target panel is
    // known to exist: otherwise a rail:show for an absent view flips the
    // subview class toward a panel that was never built. On a phone the panel
    // check above used to be skipped (the old bail was desktop-only).
    if (sub) api.selectSubview(sub);
    if (d.open) openView(id, { toggle: false });
    else select(id);
  });

  // Pinning shows the excerpt.
  document.addEventListener("rail:pin", () => {
    requestAnimationFrame(() => openView("pinned", { toggle: false }));
  });

  // Crossing the phone breakpoint switches arrangement; the open view (if any)
  // is carried over, but a sheet never opens by itself.
  function arrange() {
    html.classList.toggle("rail-phone", isPhone());
    view = translate(view);
    if (isPhone() && open) setOpen(false, { persist: false });
    layout();
    paintHead();
    paintStrip();
  }
  mql.addEventListener("change", arrange);

  // Start: the first view, or the reader's last one (re-opened on desktop).
  const saved = api.savedLayout() || {};
  html.classList.toggle("rail-phone", isPhone());
  const first = buttons().find(visible);
  const restore = saved.view && VIEWS[translate(saved.view)] && has(translate(saved.view))
    ? translate(saved.view)
    : first && first.dataset.view;
  if (restore) select(restore);
  // The panel always starts closed; only the view is remembered.
  layout();
  paintHead();
  paintStrip();
  requestAnimationFrame(() =>
    requestAnimationFrame(() => html.classList.add("rail-ready")),
  );

  return { open: (id) => openView(id, { toggle: false }), close: () => setOpen(false) };
}
