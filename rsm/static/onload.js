// onload.js
//
// onload() - Run ONCE when page first loads. Loads libraries, sets up event listeners.
// onrender() - Run on EVERY re-render when HTML changes. Re-typesets math, updates icons.
//
// Static imports resolve relative to THIS file's URL, making this work in both:
// - Studio: onload.js at /static/ → imports from /static/
// - Standalone: onload.js at CDN → imports from CDN (same-origin, no CORS issues)

import * as libs from './libraries.js';
import * as handrails from './handrails.js';
import * as keyboard from './keyboard.js';
import * as tooltips from './tooltips.js';
import * as tocarcs from './tocarcs.js';
import * as prooftree from './prooftree.js';
import * as focusmode from './focusmode.js';

export async function onload(root = null, { keys = true } = {}) {
  if (!root) root = document;

  if (window.__rsmInitialized) {
    return onrender(root);
  }

  try {
    // Load math renderer only when the page actually contains math.
    // Avoids injecting a CDN font on math-free pages.
    if (document.querySelector('span.math, div.mathblock')) {
      try {
        await libs.loadTemml();
      } catch (err) {
        console.warn("temml failed to load, falling back to MathJax:", err);
        try {
          await libs.loadMathJax();
        } catch (err2) {
          console.error("MathJax fallback also FAILED!", err2);
        }
      }
    }

    // Load Pseudocode (idempotent)
    try {
      await libs.loadPseudocode();
    } catch (err) {
      console.error("Loading pseudocode FAILED!", err);
    }

    // Handrails - set up event listeners once
    try {
      handrails.setup();
    } catch (err) {
      console.error("Loading handrails.js FAILED!", err);
    }

    // TOC tree view arcs - draw any default-tree TOCs, redraw on resize
    try {
      tocarcs.setup(root);
    } catch (err) {
      console.error("Loading tocarcs.js FAILED!", err);
    }

    // Floating proof-tree rail - shows the in-view proof's step tree
    try {
      prooftree.setup(root);
    } catch (err) {
      console.error("Loading prooftree.js FAILED!", err);
    }

    // Focus mode - click a rail node to collapse the proof to its cone
    try {
      focusmode.setup(root);
    } catch (err) {
      console.error("Loading focusmode.js FAILED!", err);
    }

    // Keyboard - set up event listeners once
    try {
      if (keys) {
        keyboard.setup(root);
      }
    } catch (err) {
      console.error("Loading keyboard.js FAILED!", err);
    }

    window.__rsmInitialized = true;

    // Render initial content
    await onrender(root);

  } catch (err) {
    console.error("An error occurred during initialization:", err);
  }
}

let renderInProgress = false;

export async function onrender(root = null) {
  if (renderInProgress) {
    return;
  }
  renderInProgress = true;

  if (!root) root = document;

  try {
    // Re-typeset math
    try {
      await libs.typesetMath(root);
    } catch (err) {
      console.error("Math typeset FAILED!", err);
    }

    // Redraw TOC tree arcs (row positions may have changed)
    try {
      tocarcs.drawAll(root);
    } catch (err) {
      console.error("TOC arcs redraw FAILED!", err);
    }

    // Render pseudocode elements that haven't been rendered yet
    try {
      const elements = root.querySelectorAll("pre.pseudocode:not(.rendered)");
      if (elements.length && window.pseudocode) {
        elements.forEach(el => {
          pseudocode.renderElement(el, {
            lineNumber: true,
            noEnd: true,
          });
          el.classList.add("rendered");
        });
      }
    } catch (err) {
      console.error("Pseudocode render FAILED!", err);
    }

    // Re-observe offset handrails after DOM replacement
    try {
      handrails.observeOffsetHandrails();
    } catch (err) {
      console.error("Re-observing offset handrails FAILED!", err);
    }

    // Tooltipster - already idempotent with :not(.tooltipstered) selector
    try {
      tooltips.createTooltips();
    } catch (err) {
      console.error("Loading tooltips FAILED!", err);
    }

  } catch (err) {
    console.error("An error occurred during render:", err);
  } finally {
    renderInProgress = false;
  }
}
