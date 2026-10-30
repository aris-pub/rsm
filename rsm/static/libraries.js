// libraries.js
//
// Load external libraries dynamically
//

import { notationMacros } from './notation.js';

// The math libraries are pinned and shipped in static/ next to this file, so a
// new upstream release cannot change a published page. The pinned CDN copy is
// only a fallback for hosts that serve this file without the vendored ones.
// The full MathJax component has every TeX extension built in, so no formula
// makes it fetch one. Its fonts sit at MathJax's own relative path beside it,
// so the vendored copy and the CDN copy each find their own fonts.
const MATHJAX_FILE = 'mathjax-3.2.2/tex-chtml-full.js';
const MATHJAX_CDN = 'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml-full.js';
const PSEUDOCODE_FILE = 'pseudocode-2.4.1.min.js';
const PSEUDOCODE_CDN = 'https://cdn.jsdelivr.net/npm/pseudocode@2.4.1/build/pseudocode.min.js';

// In the esbuild IIFE bundle import.meta is empty and new URL() throws. The
// standalone build inlines the libraries, so that path never needs a URL.
function besideThisFile(name) {
  try {
    return new URL(`./${name}`, import.meta.url).href;
  } catch {
    return null;
  }
}

// Append a classic <script> for each URL in turn until one loads.
function loadScript(urls, parent, attrs = {}) {
  const candidates = urls.filter(Boolean);
  return new Promise((res, rej) => {
    const tryNext = (i) => {
      if (i >= candidates.length) {
        rej(new Error(`could not load ${urls.join(' or ')}`));
        return;
      }
      const script = document.createElement('script');
      Object.assign(script, attrs);
      script.src = candidates[i];
      script.onload = () => res();
      script.onerror = () => {
        script.remove();
        tryNext(i + 1);
      };
      parent.appendChild(script);
    };
    tryNext(0);
  });
}

// The html extension gives \class, \cssId, \style and \href. Interactive
// figures and the notation marks need \class. The other three can inject
// links or arbitrary styling, so they are removed, as Temml left them
// untrusted. They then render as undefined commands.
const UNTRUSTED_HTML_MACROS = ['href', 'style', 'cssId'];

function mathJaxConfig(resolve, reject) {
  return {
    startup: {
      typeset: false,
      ready() {
        const MJ = window.MathJax;
        const html = MJ._?.input?.tex?.MapHandler?.MapHandler?.getMap('html_macros');
        for (const name of UNTRUSTED_HTML_MACROS) html?.remove(name);
        MJ.startup.defaultReady();
        MJ.startup.promise.then(resolve, reject);
      },
    },
    tex: {
      inlineMath: [['\\(', '\\)']],
      displayMath: [['$$', '$$']],
      processEscapes: false,
      processEnvironments: false,
    },
    // MathJax scales math so its x-height matches the text's (its default),
    // chosen over a fixed size so math reads at the text's size.
    chtml: {
      matchFontHeight: true,
    },
    options: {
      menuOptions: {
        settings: {
          inTabOrder: false,
        },
      },
    },
  };
}

let mathJaxPromise = null;

// Load MathJax once. The standalone build inlines it as window.__rsmMathJax,
// a function, so it runs only after the config below is in place.
export function loadMathJax() {
  if (mathJaxPromise) return mathJaxPromise;
  mathJaxPromise = new Promise((resolve, reject) => {
    if (window.MathJax?.startup?.promise) {
      window.MathJax.startup.promise.then(resolve, reject);
      return;
    }
    window.MathJax = mathJaxConfig(resolve, reject);
    if (typeof window.__rsmMathJax === 'function') {
      window.__rsmMathJax();
      return;
    }
    loadScript(
      [besideThisFile(MATHJAX_FILE), MATHJAX_CDN], document.head, { id: 'MathJax-script' }
    ).catch(reject);
  });
  return mathJaxPromise;
}

// MathJax must not run two typeset calls at once, so every render goes
// through this queue.
let mathQueue = Promise.resolve();
function enqueue(task) {
  const run = mathQueue.then(task);
  mathQueue = run.catch(() => {});
  return run;
}

// Renders asked for but not finished. A render joins the queue only once
// MathJax has loaded, so the queue alone can miss one that was just asked for.
let mathPending = 0;
function track(promise) {
  mathPending++;
  return promise.finally(() => { mathPending--; });
}

// Resolves once no math render is pending, including renders asked for while
// waiting (a pinned excerpt or an opened aside typesets after the page does).
export async function mathIdle() {
  for (;;) {
    const q = mathQueue;
    await q;
    await new Promise((r) => setTimeout(r, 0));
    if (q === mathQueue && mathPending === 0) return;
  }
}

// MathJax keeps a \def from one formula for the next ones, so the notation is
// (re)defined once before a render, not passed per formula as Temml needed.
// One \def per macro, so a broken value cannot take the others down with it.
let definedNotation = null;
function defineNotation() {
  const entries = Object.entries(notationMacros());
  const key = JSON.stringify(entries);
  if (key === definedNotation) return;
  definedNotation = key;
  for (const [name, value] of entries) {
    const params = value.match(/#[1-9]/g);
    const n = params ? Math.max(...params.map((s) => Number(s[1]))) : 0;
    let args = '';
    for (let i = 1; i <= n; i++) args += `#${i}`;
    try {
      window.MathJax.tex2mml(`\\def${name}${args}{${value}}`);
    } catch (err) {
      console.error(`notation ${name}:`, err);
    }
  }
}

// The elements in root that still hold raw \(...\) or $$...$$ source. Each
// keeps its source in data-latex, which notation re-renders and locate use.
// In handrails mode a display block's source sits in its .hr-content-zone.
function rawMath(root) {
  const targets = [];
  root.querySelectorAll('span.math').forEach((el) => {
    const src = el.textContent;
    if (!src.startsWith('\\(') || !src.endsWith('\\)')) return;
    el.dataset.latex = src.slice(2, -2);
    targets.push(el);
  });
  root.querySelectorAll('div.mathblock').forEach((el) => {
    const zone = el.querySelector('.hr-content-zone') || el;
    const src = zone.textContent.trim();
    if (!src.startsWith('$$') || !src.endsWith('$$')) return;
    el.dataset.latex = src.slice(2, -2).trim();
    targets.push(zone);
  });
  return targets;
}

// Typeset the raw math in root. Returns a promise that resolves once the math
// is laid out, so anything that measures the page can wait for it.
// Idempotent: math already typeset no longer holds raw source and is skipped.
export function typesetMath(root = document) {
  const element = root === document ? document.body : root;

  // Studio's editor re-runs onrender on every keystroke, so a math-less
  // document must not load MathJax.
  if (!element.querySelector('span.math, div.mathblock')) return Promise.resolve();

  return track(loadMathJax().then(() => enqueue(() => typesetRaw(element))).catch((err) => {
    console.error('MathJax typeset error:', err);
  }));
}

async function typesetRaw(element) {
  const targets = rawMath(element);
  if (!targets.length) return;
  defineNotation();
  await window.MathJax.typesetPromise(targets);
}

// Typeset every math element in root again from its data-latex, so a change
// to the notation reaches math that is already typeset.
export function retypesetMath(root = document) {
  if (!window.MathJax?.typesetPromise) return Promise.resolve();
  const element = root === document ? document.body : root;
  return enqueue(() => {
    const zones = [];
    root.querySelectorAll('span.math[data-latex]').forEach((el) => {
      zones.push([el, `\\(${el.dataset.latex}\\)`]);
    });
    root.querySelectorAll('div.mathblock[data-latex]').forEach((el) => {
      zones.push([el.querySelector('.hr-content-zone') || el, `$$${el.dataset.latex}$$`]);
    });
    window.MathJax.typesetClear(zones.map(([zone]) => zone));
    for (const [zone, src] of zones) zone.textContent = src;
    return typesetRaw(element);
  }).catch((err) => {
    console.error('MathJax re-typeset error:', err);
  });
}

// Render a LaTeX string into el, with the document's notation. For widgets and
// figures that build their own math: rsm.renderMath(latex, el, { display }).
export function renderMath(latex, el, { display = false } = {}) {
  return track(loadMathJax().then(() => enqueue(async () => {
    window.MathJax.typesetClear([el]);
    el.textContent = display ? `$$${latex}$$` : `\\(${latex}\\)`;
    defineNotation();
    await window.MathJax.typesetPromise([el]);
  })));
}

// Math that MathJax converted outside a typeset call (pseudocode.js uses
// MathJax.tex2chtml) has no CSS for its characters until the stylesheet is
// brought up to date.
export function refreshMathStyles() {
  const MJ = window.MathJax;
  if (!MJ?.startup?.output || !MJ.startup.document) return;
  const sheet = MJ.startup.output.styleSheet(MJ.startup.document);
  if (sheet && !sheet.isConnected) document.head.appendChild(sheet);
}

let pseudocodeLoaded = false;
let pseudocodeLoadPromise = null;

// Load pseudocode.js - idempotent, only loads once
// https://github.com/SaswatPadhi/pseudocode.js
export function loadPseudocode() {
  if (pseudocodeLoaded) {
    return Promise.resolve();
  }
  if (pseudocodeLoadPromise) {
    return pseudocodeLoadPromise;
  }

  // The standalone build inlines pseudocode.js, so it is already here.
  if (window.pseudocode) {
    pseudocodeLoaded = true;
    return Promise.resolve();
  }

  pseudocodeLoadPromise = loadScript(
    [besideThisFile(PSEUDOCODE_FILE), PSEUDOCODE_CDN],
    document.body,
    { type: 'text/javascript', id: 'pseudocode-script' },
  ).then(() => {
    pseudocodeLoaded = true;
  });

  return pseudocodeLoadPromise;
}
