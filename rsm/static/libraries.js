// libraries.js
//
// Load external libraries dynamically
//

let temmlLoaded = false;
let temmlLoadPromise = null;

// Load temml (primary math renderer) - idempotent, only loads once
export function loadTemml() {
  if (temmlLoaded) return Promise.resolve();
  if (temmlLoadPromise) return temmlLoadPromise;

  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://cdn.jsdelivr.net/npm/temml/dist/Temml.css';
  document.head.appendChild(link);

  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/temml/dist/temml.min.js';
  document.head.appendChild(script);

  temmlLoadPromise = new Promise((res, rej) => {
    script.onload = () => {
      temmlLoaded = true;
      // Alias temml as katex so pseudocode.js (which checks for window.katex) can use it.
      // temml exposes the same renderToString API that pseudocode.js expects.
      if (window.temml && !window.katex) {
        window.katex = window.temml;
      }
      res();
    };
    script.onerror = rej;
  });

  return temmlLoadPromise;
}

let mathJaxLoaded = false;
let mathJaxLoadPromise = null;

// Load MathJax - fallback if temml is unavailable, idempotent
export function loadMathJax() {
  if (mathJaxLoaded) {
    return Promise.resolve();
  }
  if (mathJaxLoadPromise) {
    return mathJaxLoadPromise;
  }

  const config = document.createElement('script');
  config.innerHTML = `window.MathJax = {
      startup: {
        typeset: false
      },
      tex: {
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
        processEscapes: true,
        processEnvironments: true
      },
      options: {
        menuOptions: {
          settings: {
            inTabOrder: false
          }
        }
      }
    };`;
  document.body.appendChild(config);

  const script = document.createElement('script');
  script.type = "text/javascript";
  script.id = "MathJax-script";
  script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js";
  document.body.appendChild(script);

  mathJaxLoadPromise = new Promise((res, rej) => {
    script.onload = async () => {
      const waitForStartup = () => {
        if (window.MathJax?.startup?.promise) {
          window.MathJax.startup.promise.then(() => {
            mathJaxLoaded = true;
            res();
          });
        } else {
          setTimeout(waitForStartup, 10);
        }
      };
      waitForStartup();
    };
    script.onerror = rej;
  });

  return mathJaxLoadPromise;
}

// Re-typeset math after HTML content changes.
// Uses temml (sync, native MathML) when available; falls back to MathJax.
// Idempotent: already-rendered elements are skipped (their content is no
// longer the raw \(...\) / $$...$$ delimiter strings).
export async function typesetMath(root = document) {
  const element = root === document ? document.body : root;

  // Load Temml on-demand if math elements exist but no renderer is loaded.
  // This handles the case where the initial render had no math (so onload
  // skipped Temml), then a subsequent compile introduces math.
  if (!window.temml && !window.MathJax?.typesetPromise) {
    const hasMath = element.querySelector('span.math, div.mathblock');
    if (hasMath) {
      try {
        await loadTemml();
      } catch {
        try { await loadMathJax(); } catch { /* both failed */ }
      }
    }
  }

  if (window.temml) {
    // Inline math: <span class="math">\(...\)</span>
    element.querySelectorAll('span.math').forEach(el => {
      const src = el.textContent;
      if (!src.startsWith('\\(') || !src.endsWith('\\)')) return;
      const latex = src.slice(2, -2);
      el.dataset.latex = latex;
      try {
        temml.render(latex, el, { throwOnError: false });
      } catch (err) {
        console.error('temml inline error:', err);
      }
    });

    // Display math: <div class="mathblock">$$\n...\n$$</div>
    // In handrails mode the LaTeX lives inside .hr-content-zone.
    element.querySelectorAll('div.mathblock').forEach(el => {
      const contentEl = el.querySelector('.hr-content-zone') || el;
      const src = contentEl.textContent.trim();
      if (!src.startsWith('$$') || !src.endsWith('$$')) return;
      const latex = src.slice(2, -2).trim();
      el.dataset.latex = latex;
      try {
        temml.render(latex, contentEl, { displayMode: true, throwOnError: false });
      } catch (err) {
        console.error('temml display error:', err);
      }
    });

    return;
  }

  // MathJax fallback
  if (!window.MathJax?.typesetPromise) {
    console.warn('Neither temml nor MathJax ready for typesetting');
    return;
  }

  const existingContainers = element.querySelectorAll('mjx-container');
  existingContainers.forEach(el => el.remove());

  try {
    if (MathJax.typesetClear) MathJax.typesetClear([element]);
    await MathJax.typesetPromise([element]);
  } catch (err) {
    console.error('MathJax typeset error:', err);
  }
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

  const script = document.createElement('script');
  script.type = "text/javascript";
  script.id = "pseudocode-script";
  script.src = "https://cdn.jsdelivr.net/npm/pseudocode@latest/build/pseudocode.min.js"
  document.body.appendChild(script);

  pseudocodeLoadPromise = new Promise((res, rej) => {
    script.onload = () => {
      pseudocodeLoaded = true;
      res();
    };
    script.onerror = rej;
  });

  return pseudocodeLoadPromise;
}
