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
import * as minimap from './minimap.js';
import * as icons from './icons.js';
import * as tooltips from './tooltips.js';

export async function onload(root = null, { keys = true } = {}) {
  if (!root) root = document;

  if (window.__rsmInitialized) {
    return onrender(root);
  }

  try {
    // Load MathJax (idempotent)
    try {
      await libs.loadMathJax();
    } catch (err) {
      console.error("Loading MathJax FAILED!", err);
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

    // Keyboard - set up event listeners once
    try {
      if (keys) {
        keyboard.setup(root);
      }
    } catch (err) {
      console.error("Loading keyboard.js FAILED!", err);
    }

    // Minimap - set up event listeners once
    try {
      minimap.setup();
    } catch (err) {
      console.error("Loading minimap.js FAILED!", err);
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
    // Icons - safe to call multiple times
    try {
      icons.setup(root);
    } catch (err) {
      console.error("Loading icons.js FAILED!", err);
    }

    // Re-typeset math
    try {
      await libs.typesetMath(root);
    } catch (err) {
      console.error("MathJax typeset FAILED!", err);
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
