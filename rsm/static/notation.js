// notation.js
//
// Reader-rebindable notation macros.
//
// The author declares macros in a :notation: block; their defaults ship as
// <script class="rsm-notation"> JSON.  A single shared macros object feeds
// every Temml render (see typesetMath in libraries.js), so the math source
// stays clean (\eig, never a \def).  Rebinding mutates that object, persists
// the override, and re-renders all math.

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

// Render a notation value to a string for validation and preview. A
// parameterized value (one containing #1..#9, e.g. "e(#1)") only renders inside
// a macro call, not on its own, so render it as a throwaway macro body applied
// to a placeholder; a plain value renders directly.
function renderNotationToString(latex) {
  const params = latex.match(/#[1-9]/g);
  if (params) {
    const n = Math.max(...params.map((s) => +s[1]));
    const args = "{\\square}".repeat(n);
    return window.temml.renderToString("\\rsmNotationPreview" + args, {
      throwOnError: true,
      macros: { "\\rsmNotationPreview": latex },
    });
  }
  return window.temml.renderToString(latex, { throwOnError: true });
}

// A reader's value feeds every math block at once, so one bad value would
// corrupt the whole document.  Reject anything Temml cannot render.
function isValid(latex) {
  if (!latex || !latex.trim()) return false;
  if (!window.temml) return true; // best-effort when the validator is unavailable
  try {
    renderNotationToString(latex);
    return true;
  } catch {
    return false;
  }
}

// Re-render every already-typeset math element from its stored data-latex.
// A fresh copy of the macros object is passed per call so a stray author \gdef
// cannot leak into the canonical set or between blocks.
export function reRenderAll(root = document) {
  if (!window.temml) return;
  const macros = getNotationMacros();
  root.querySelectorAll("span.math[data-latex]").forEach((el) => {
    try {
      window.temml.render(el.dataset.latex, el, {
        throwOnError: false,
        macros: { ...macros },
      });
    } catch (err) {
      console.error("notation re-render (inline):", err);
    }
  });
  root.querySelectorAll("div.mathblock[data-latex]").forEach((el) => {
    const target = el.querySelector(".hr-content-zone") || el;
    try {
      window.temml.render(el.dataset.latex, target, {
        displayMode: true,
        throwOnError: false,
        macros: { ...macros },
      });
    } catch (err) {
      console.error("notation re-render (display):", err);
    }
  });
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
    empty.textContent = "This paper declares no rebindable notation.";
    panel.appendChild(empty);
    return;
  }

  for (const e of entries) {
    const row = document.createElement("div");
    row.className = "rail-notation-row";

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
    apply.textContent = "Apply";
    apply.setAttribute("data-tooltip", "Apply this symbol throughout the paper");

    const locate = document.createElement("button");
    locate.type = "button";
    locate.className = "rail-notation-locate";
    locate.setAttribute("aria-label", "Scroll to the nearest occurrence of this symbol");
    locate.setAttribute("data-tooltip", "Scroll to the nearest occurrence of this symbol");
    locate.innerHTML = _LOCATE_ICON;

    const reset = document.createElement("button");
    reset.type = "button";
    reset.className = "rail-notation-reset";
    reset.setAttribute("aria-label", "Reset to the author's default");
    reset.setAttribute("data-tooltip", "Reset to the author's default");
    reset.textContent = "↺";

    function renderPreview(latex) {
      if (!window.temml) {
        preview.textContent = "";
        return;
      }
      try {
        preview.innerHTML = renderNotationToString(latex);
        input.classList.remove("invalid");
      } catch {
        input.classList.add("invalid");
      }
    }
    renderPreview(input.value);

    // Apply the typed value: validate, re-render, and flash every instance that
    // changed so the reader sees the effect (not just the symbol on the input's
    // row). No-op if nothing changed, so clicking away doesn't re-flash.
    let lastApplied = e.current;
    function commit() {
      if (input.value === lastApplied) return;
      const ok = setMacro(e.macro, input.value);
      input.classList.toggle("invalid", !ok);
      if (ok) {
        lastApplied = input.value;
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
