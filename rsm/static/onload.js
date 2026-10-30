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
import * as uitip from './uitip.js';
import * as minimap from './minimap.js';
import * as margin from './margin.js';
import * as captions from './captions.js';
import * as asides from './asides.js';

// For widgets and figures that render their own math, so they get MathJax with
// the document's notation without loading a renderer of their own.
window.rsm = Object.assign(window.rsm || {}, {
  renderMath: libs.renderMath,
  typesetMath: libs.typesetMath,
  // Resolves once all math, including math typeset after the page, is done.
  mathIdle: libs.mathIdle,
});

export async function onload(root = null, { keys = true } = {}) {
  if (!root) root = document;

  if (window.__rsmInitialized) {
    return onrender(root);
  }

  try {
    // Load MathJax only when the page has math. pseudocode.js typesets the
    // math in an algorithm with MathJax too.
    if (document.querySelector('span.math, div.mathblock, pre.pseudocode')) {
      try {
        await libs.loadMathJax();
      } catch (err) {
        console.error("Loading MathJax FAILED!", err);
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
      // Name and wire each fold button before the collapse passes change state.
      handrails.initCollapseButtons(root);
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

    // Margin column - captions (and later asides) beside the text when it fits
    try {
      margin.setup();
    } catch (err) {
      console.error("Loading margin.js FAILED!", err);
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
        const el = revealHashTarget(id);
        if (!el) { hideBackPill(); return; }
        // The jump moved the reader; offer a visible handle on native Back.
        showBackPill();
      });
    } catch (err) {
      console.error("Setting up hash-focus FAILED!", err);
    }

    window.__rsmInitialized = true;

    // Render initial content
    await onrender(root);

    // Initial load with a hash (e.g. a shared link to #st-inner): the native
    // anchor jump cannot reach a target that collapseInitial has folded shut,
    // so expand its collapsed ancestors, then scroll it into view and focus it.
    // No back pill here: the reader arrived at this hash, there is nothing to
    // return to.
    try {
      revealHashTarget(decodeURIComponent(window.location.hash.slice(1)));
    } catch (err) {
      console.error("Initial hash reveal FAILED!", err);
    }

    // Notation pane (Document scope of the sidebar) - built after the first
    // typeset so the live LaTeX preview has the math renderer available.
    try {
      notation.mountNotationPanel(root);
      // A symbol in the text opens Notation with that symbol selected.
      notation.setupSymbolEntry();
      // The notation buttons are created here, after the initial createTooltips
      // pass, so bind tooltips again (idempotent via :not(.tooltipstered)).
      tooltips.createTooltips();
    } catch (err) {
      console.error("Loading notation panel FAILED!", err);
    }

    // Interface tooltips for the sidebar's controls.
    try {
      uitip.setup();
    } catch (err) {
      console.error("Loading interface tooltips FAILED!", err);
    }

    // Shareable view: wire "Copy this view" and restore a ?view= link if present.
    // Runs after the first render so the rail, folds, and layout are in place.
    try {
      shareview.setup(root);
    } catch (err) {
      console.error("Loading shareview.js FAILED!", err);
    }

    // Document minimap. Mounted after the first typeset so the marks are
    // measured against rendered math.
    try {
      minimap.setup(root);
    } catch (err) {
      console.error("Loading minimap.js FAILED!", err);
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
        await libs.loadMathJax();
        elements.forEach(el => {
          pseudocode.renderElement(el, {
            lineNumber: true,
            noEnd: true,
          });
          el.classList.add("rendered");
        });
        libs.refreshMathStyles();
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

    // Captions into the margin column (idempotent, picks up replaced DOM)
    try {
      captions.setup(root);
    } catch (err) {
      console.error("Placing captions FAILED!", err);
    }

    // Asides: into the margin column, or closed below their block (idempotent)
    try {
      asides.setup(root);
    } catch (err) {
      console.error("Setting up asides FAILED!", err);
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
// Move focus (and, when needed, the viewport) to the block named by a URL hash,
// opening any collapsed fold it sits inside first so focus never lands on hidden
// content. Shared by the hashchange handler and the initial load. Returns the
// target element, or null when the hash is empty, "top", or names no element.
function revealHashTarget(id) {
  if (!id || id === "top") return null;
  const el = document.getElementById(id);
  if (!el) return null;
  if (!el.hasAttribute("tabindex")) el.setAttribute("tabindex", "-1");
  const opened = handrails.expandAncestorsTo(el);
  // Native hash navigation restores scroll but NOT focus, so move focus here.
  el.focus({ preventScroll: true });
  // When we had to expand a fold, the native jump scrolled while the target was
  // still hidden, so its position is stale: reposition it into view.
  if (opened) el.scrollIntoView({ block: "center" });
  return el;
}


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
