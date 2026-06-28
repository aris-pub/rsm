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
import * as notation from './notation.js';
import * as reorder from './reorder.js';
import * as deplens from './deplens.js';
import * as shareview from './shareview.js';

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
      // Collapse blocks marked :collapsed: (subtractive: JS-off shows them open).
      handrails.collapseInitial(root);
      // Then restore the reader's own collapse choices from a previous visit.
      handrails.restoreCollapse(root);
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

    // Reorder mode - opt-in drag reordering of a proof's steps
    try {
      reorder.setup(root);
    } catch (err) {
      console.error("Loading reorder.js FAILED!", err);
    }

    // Dependency lens - sticky upstream/downstream cone from a step's menu
    try {
      deplens.setup(root);
    } catch (err) {
      console.error("Loading deplens.js FAILED!", err);
    }

    // Keyboard - set up event listeners once
    try {
      if (keys) {
        keyboard.setup(root);
      }
    } catch (err) {
      console.error("Loading keyboard.js FAILED!", err);
    }

    // In-document jumps (the rail/keyboard chrome jumps and :ref:/TOC clicks)
    // navigate by URL hash so they ride the native browser Back button. Native
    // hash navigation restores scroll but NOT focus, so move focus to the target
    // block for keyboard / screen-reader users (and again on Back).
    try {
      setupBackPill();
      window.addEventListener("hashchange", () => {
        const id = decodeURIComponent(window.location.hash.slice(1));
        if (!id || id === "top") {
          // Hash cleared or jumped to the top (e.g. via the pill's own Back):
          // there is nothing to return to, so dismiss the pill.
          hideBackPill();
          return;
        }
        const el = document.getElementById(id);
        if (!el) { hideBackPill(); return; }
        if (!el.hasAttribute("tabindex")) el.setAttribute("tabindex", "-1");
        el.focus({ preventScroll: true });
        // The jump moved the reader; offer a visible handle on native Back.
        showBackPill();
      });
    } catch (err) {
      console.error("Setting up hash-focus FAILED!", err);
    }

    window.__rsmInitialized = true;

    // Render initial content
    await onrender(root);

    // Notation pane (Document scope of the sidebar) - built after the first
    // typeset so the live LaTeX preview has the math renderer available.
    try {
      notation.mountNotationPanel(root);
      // The notation buttons are created here, after the initial createTooltips
      // pass, so bind tooltips again (idempotent via :not(.tooltipstered)).
      tooltips.createTooltips();
    } catch (err) {
      console.error("Loading notation panel FAILED!", err);
    }

    // Shareable view: wire "Copy this view" and restore a ?view= link if present.
    // Runs after the first render so the rail, folds, and layout are in place.
    try {
      shareview.setup(root);
    } catch (err) {
      console.error("Loading shareview.js FAILED!", err);
    }

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


// --- Back pill -------------------------------------------------------------
// A transient, visible affordance over the native browser Back button. After an
// in-document jump (a hashchange to a block) the pill appears; clicking it calls
// history.back() to return the reader. It owns NO navigation state: native
// history is the source of truth, this is purely a discoverable, demoable handle
// on it. Dismisses on Back (the hash clears) or when the reader scrolls away.
let __backPillScroll = null;

function setupBackPill() {
  if (document.querySelector(".rsm-back-pill")) return;
  const pill = document.createElement("button");
  pill.type = "button";
  pill.className = "rsm-back-pill";
  pill.setAttribute("aria-label", "Back to where you were");
  pill.innerHTML = '<span class="rsm-back-pill-arrow" aria-hidden="true">←</span> Back';
  pill.addEventListener("click", () => window.history.back());
  document.body.appendChild(pill);
}

function showBackPill() {
  const pill = document.querySelector(".rsm-back-pill");
  if (!pill) return;
  pill.classList.add("is-visible");
  // Transient: once the reader resumes reading (scrolls well away from the
  // landing point) the pill dismisses, so it never becomes pinned chrome.
  const landingY = window.scrollY;
  if (__backPillScroll) window.removeEventListener("scroll", __backPillScroll);
  __backPillScroll = () => {
    if (Math.abs(window.scrollY - landingY) > window.innerHeight * 0.33) hideBackPill();
  };
  window.addEventListener("scroll", __backPillScroll, { passive: true });
}

function hideBackPill() {
  const pill = document.querySelector(".rsm-back-pill");
  if (pill) pill.classList.remove("is-visible");
  if (__backPillScroll) {
    window.removeEventListener("scroll", __backPillScroll);
    __backPillScroll = null;
  }
}
