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

// A reader's value feeds every math block at once, so one bad value would
// corrupt the whole document.  Reject anything Temml cannot render.
function isValid(latex) {
  if (!latex || !latex.trim()) return false;
  if (!window.temml) return true; // best-effort when the validator is unavailable
  try {
    window.temml.renderToString(latex, { throwOnError: true });
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
