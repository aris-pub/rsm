// notation.js
//
// Reader-rebindable notation macros.
//
// The author declares macros in a :notation: block; their defaults ship as
// <script class="rsm-notation"> JSON.  A single shared macros object feeds
// every MathJax render (see typesetMath in libraries.js), so the math source
// stays clean (\eig, never a \def).  Rebinding mutates that object, persists
// the override, and re-renders all math.

import { loadMathJax, mathIdle, renderMath, retypesetMath } from "./libraries.js";

let _macros = null;

function storageKey() {
  return "rsm-notation:" + location.pathname;
}

function loadOverrides() {
  try {
    return JSON.parse(localStorage.getItem(storageKey())) || {};
  } catch {
    return {};
  }
}

function saveOverride(macro, latex) {
  const overrides = loadOverrides();
  overrides[macro] = latex;
  try {
    localStorage.setItem(storageKey(), JSON.stringify(overrides));
  } catch {
    // localStorage unavailable (e.g. private mode); rebind stays session-only
  }
}

// The shared macros object: author defaults overlaid with reader overrides.
// Built once, lazily, on the first render.
export function getNotationMacros() {
  if (_macros) return _macros;
  _macros = {};
  document.querySelectorAll("script.rsm-notation").forEach((s) => {
    try {
      for (const e of JSON.parse(s.textContent)) _macros[e.macro] = e.default;
    } catch {
      // malformed notation data; skip this block
    }
  });
  Object.assign(_macros, loadOverrides());
  return _macros;
}

// With the sidebar's Notation view on the page, every use of a declared symbol
// is marked in the rendered math (\class{nt-<name>}), so a reader can click a
// symbol to rename it. The marks ride on the same \class trust interactive
// figures already rely on.
const MARK_PREFIX = "nt-";

// Cache the answer for the current tick and clear it on the next microtask, so
// a burst of renders queries the DOM once. The marking state only changes when
// the Notation panel is built or torn down, never mid-pass.
let _markingCache = null;
function markingOn() {
  if (_markingCache === null) {
    _markingCache = !!document.querySelector(".proof-rail .rail-notation");
    queueMicrotask(() => {
      _markingCache = null;
    });
  }
  return _markingCache;
}

// The notation every math render uses, keyed by control sequence (\eig): the
// current values and, with the Notation view present, the marks on each use.
export function notationMacros() {
  const macros = { ...getNotationMacros() };
  if (markingOn()) {
    for (const k of Object.keys(macros)) {
      macros[k] = `\\class{${MARK_PREFIX}${k.slice(1)}}{${macros[k]}}`;
    }
  }
  return macros;
}

// A notation value as one formula: defined as a throwaway macro and applied, so
// a parameterized value (one containing #1..#9, e.g. "e(#1)") renders with a
// placeholder for each argument, and a value that would break the \def the
// renderer builds from it fails here too.
function notationSample(latex) {
  const params = latex.match(/#[1-9]/g);
  const n = params ? Math.max(...params.map((s) => +s[1])) : 0;
  let defArgs = "";
  for (let i = 1; i <= n; i++) defArgs += `#${i}`;
  return `\\def\\rsmNotationPreview${defArgs}{${latex}}\\rsmNotationPreview` +
    "{\\square}".repeat(n);
}

// A reader's value feeds every math block at once, so one bad value would
// corrupt the whole document.  Reject anything MathJax cannot render: a TeX
// error comes back as <merror>, an unknown command as red text that starts
// with a backslash.
function isValid(latex) {
  if (!latex || !latex.trim()) return false;
  if (!window.MathJax?.tex2mml) return true; // best-effort when the validator is unavailable
  try {
    const mml = window.MathJax.tex2mml(notationSample(latex));
    return !/<merror|mathcolor="red"[^>]*>\\/.test(mml);
  } catch {
    return false;
  }
}

// Re-render every already-typeset math element from its stored data-latex, so
// it picks up the current notation.
export function reRenderAll(root = document) {
  return retypesetMath(root);
}

// Rebind a macro to a new LaTeX value: validate, persist, re-render.
// Returns false and changes nothing if the value is invalid.
export function setMacro(macro, latex) {
  if (!isValid(latex)) return false;
  getNotationMacros()[macro] = latex;
  saveOverride(macro, latex);
  reRenderAll();
  return true;
}

// Revert a macro to the author's default: drop the override and re-render.
export function resetMacro(macro) {
  const entry = listNotation().find((e) => e.macro === macro);
  const overrides = loadOverrides();
  delete overrides[macro];
  try {
    localStorage.setItem(storageKey(), JSON.stringify(overrides));
  } catch {
    /* localStorage unavailable */
  }
  if (entry) {
    getNotationMacros()[macro] = entry.default;
    reRenderAll();
  }
}

// The declared notation as the reader UI needs it: label, author default, and
// the value currently in force (default overlaid with any reader override).
export function listNotation() {
  const macros = getNotationMacros();
  const out = [];
  const seen = new Set();
  document.querySelectorAll("script.rsm-notation").forEach((s) => {
    try {
      for (const e of JSON.parse(s.textContent)) {
        if (seen.has(e.macro)) continue;
        seen.add(e.macro);
        out.push({
          macro: e.macro,
          label: e.label || e.macro,
          default: e.default,
          current: macros[e.macro] ?? e.default,
        });
      }
    } catch {
      /* malformed notation data; skip */
    }
  });
  return out;
}

const _LOCATE_ICON =
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
  'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0"/>' +
  '<path d="M12 12m-5 0a5 5 0 1 0 10 0a5 5 0 1 0 -10 0"/>' +
  '<path d="M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/></svg>';

// Every math element whose source uses this macro, matched on the whole control
// sequence so \eig never matches \eigenvalue.
function usesOf(macro, root = document) {
  const re = new RegExp(macro.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "(?![a-zA-Z])");
  return [
    ...root.querySelectorAll("span.math[data-latex], div.mathblock[data-latex]"),
  ].filter((el) => re.test(el.dataset.latex));
}

// Briefly highlight an element so the reader can spot it.
function flash(el) {
  el.classList.add("notation-located");
  setTimeout(() => el.classList.remove("notation-located"), 1800);
}

// Of a set of elements, the one whose vertical center is closest to the
// viewport center: nearest to where the reader is currently looking.
function nearestOf(els) {
  const center = window.innerHeight / 2;
  let best = null;
  let bestDist = Infinity;
  for (const el of els) {
    const r = el.getBoundingClientRect();
    // Skip display:none uses (collapsed proofs, hidden source/static copies):
    // they report a zero box at top 0, which can beat a real but off-screen use
    // and make locate scroll to nothing. Off-screen rendered uses keep a real
    // box, so they stay eligible.
    if (r.width === 0 && r.height === 0) continue;
    const dist = Math.abs(r.top + r.height / 2 - center);
    if (dist < bestDist) {
      bestDist = dist;
      best = el;
    }
  }
  return best;
}

function jumpTo(el) {
  el.scrollIntoView({ behavior: "smooth", block: "center" });
  flash(el);
}

// Build the Notation pane (Document scope) into its .rail-notation panel: one
// row per declared symbol with a LaTeX field, a live preview, a locate, and a
// reset.
export function mountNotationPanel(root = document) {
  const panel = root.querySelector(".rail-notation");
  if (!panel) return;
  const entries = listNotation();
  panel.innerHTML = "";
  if (!entries.length) {
    const empty = document.createElement("div");
    empty.className = "rail-notation-empty";
    empty.textContent = "This manuscript declares no rebindable notation.";
    panel.appendChild(empty);
    return;
  }

  for (const e of entries) {
    const row = document.createElement("div");
    row.className = "rail-notation-row";
    row.dataset.macro = e.macro;

    const label = document.createElement("div");
    label.className = "rail-notation-label";
    label.textContent = e.label;

    const edit = document.createElement("div");
    edit.className = "rail-notation-edit";

    const input = document.createElement("input");
    input.type = "text";
    input.className = "rail-notation-input";
    input.value = e.current;
    input.spellcheck = false;
    input.setAttribute("aria-label", `LaTeX for ${e.label}`);

    const preview = document.createElement("span");
    preview.className = "rail-notation-preview";

    const apply = document.createElement("button");
    apply.type = "button";
    apply.className = "rail-notation-apply";
    apply.textContent = "Rename";
    apply.setAttribute("data-tip", "Rename this symbol everywhere in the manuscript");

    const locate = document.createElement("button");
    locate.type = "button";
    locate.className = "rail-notation-locate";
    locate.setAttribute("aria-label", "Scroll to the nearest occurrence of this symbol");
    locate.setAttribute("data-tip", "Scroll to the nearest occurrence of this symbol");
    locate.innerHTML = _LOCATE_ICON;

    const reset = document.createElement("button");
    reset.type = "button";
    reset.className = "rail-notation-reset";
    reset.setAttribute("aria-label", "Reset to the author's default");
    reset.setAttribute("data-tip", "Reset to the author's default");
    reset.textContent = "↺";

    // The preview is typeset like any math, so it gets MathJax's styles.
    function renderPreview(latex) {
      loadMathJax()
        .then(() => {
          if (!isValid(latex)) {
            input.classList.add("invalid");
            return;
          }
          input.classList.remove("invalid");
          return renderMath(notationSample(latex), preview);
        })
        .catch((err) => console.error("notation preview:", err));
    }
    renderPreview(input.value);

    // Apply the typed value: validate, re-render, and flash every instance that
    // changed so the reader sees the effect (not just the symbol on the input's
    // row). No-op if nothing changed, so clicking away doesn't re-flash.
    let lastApplied = e.current;
    async function commit() {
      if (input.value === lastApplied) return;
      const ok = setMacro(e.macro, input.value);
      input.classList.toggle("invalid", !ok);
      if (ok) {
        lastApplied = input.value;
        // Measure where the uses sit only once they show the new value.
        await mathIdle();
        const uses = usesOf(e.macro, root);
        uses.forEach(flash);
        // Always bring the nearest instance into view so the change is visible
        // even when you applied it while no instance was on screen.
        const nearest = nearestOf(uses);
        if (nearest) nearest.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }

    input.addEventListener("input", () => renderPreview(input.value));
    input.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        commit();
      }
    });
    input.addEventListener("blur", commit);

    // Keep focus in the field when a control is clicked (so blur doesn't fire a
    // duplicate commit); each button then runs its own explicit action.
    for (const btn of [apply, locate, reset]) {
      btn.addEventListener("mousedown", (ev) => ev.preventDefault());
    }
    apply.addEventListener("click", commit);
    locate.addEventListener("click", () => {
      const el = nearestOf(usesOf(e.macro, root));
      if (el) jumpTo(el);
    });
    reset.addEventListener("click", () => {
      resetMacro(e.macro);
      input.value = e.default;
      lastApplied = e.default;
      renderPreview(input.value);
      usesOf(e.macro, root).forEach(flash);
    });

    const actions = document.createElement("div");
    actions.className = "rail-notation-actions";
    actions.append(apply, locate, reset);

    edit.append(input, preview);
    row.append(label, edit, actions);
    panel.appendChild(row);
  }
}

// A symbol in the text is a way into Notation: clicking one opens the view with
// that symbol's field selected, and briefly marks where else it is used.
let entryWired = false;
export function setupSymbolEntry() {
  if (entryWired || !markingOn()) return;
  entryWired = true;
  const SEL = `.manuscript [class^="${MARK_PREFIX}"], .manuscript [class*=" ${MARK_PREFIX}"]`;
  const macroOf = (el) => {
    const c = [...el.classList].find((k) => k.startsWith(MARK_PREFIX));
    return c ? "\\" + c.slice(MARK_PREFIX.length) : null;
  };
  // Keep the click from selecting text or focusing the block underneath.
  document.addEventListener(
    "mousedown",
    (ev) => {
      if (ev.target.closest && ev.target.closest(SEL)) ev.preventDefault();
    },
    true,
  );
  document.addEventListener(
    "click",
    (ev) => {
      const sym = ev.target.closest && ev.target.closest(SEL);
      if (!sym) return;
      const macro = macroOf(sym);
      if (!macro) return;
      ev.preventDefault();
      ev.stopPropagation();
      document.dispatchEvent(
        new CustomEvent("rail:show", { detail: { view: "notation", open: true } }),
      );
      requestAnimationFrame(() =>
        requestAnimationFrame(() => {
          const row = [...document.querySelectorAll(".rail-notation-row")].find(
            (r) => r.dataset.macro === macro,
          );
          if (!row) return;
          row.scrollIntoView({ block: "nearest" });
          row.classList.remove("rail-notation-row-hi");
          void row.offsetWidth;
          row.classList.add("rail-notation-row-hi");
          const input = row.querySelector(".rail-notation-input");
          if (input) {
            input.focus({ preventScroll: true });
            input.select();
          }
        }),
      );
      const cls = MARK_PREFIX + macro.slice(1);
      for (const use of document.querySelectorAll(".manuscript ." + cls)) {
        use.classList.remove("notation-located");
        void use.getBoundingClientRect();
        flash(use);
      }
    },
    true,
  );
}
