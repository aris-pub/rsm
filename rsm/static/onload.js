// onload.js
//
// onload() - Run ONCE when page first loads. Loads libraries, sets up event listeners.
// onrender() - Run on EVERY re-render when HTML changes. Re-typesets math, updates icons.
//

export async function onload(root = null, { path = "/static/", keys = true } = {}) {
  if (!root) root = document;

  // Use window globals because dynamic import() creates new module instances
  if (window.__rsmInitialized) {
    window.__rsmCachedPath = path;
    return onrender(root);
  }

  try {
    // Cache the libraries module to avoid re-importing on every render
    window.__rsmCachedLibs = await import(`${path}libraries.js`);
    window.__rsmCachedPath = path;

    // Load MathJax (idempotent)
    try {
      await window.__rsmCachedLibs.loadMathJax();
    } catch (err) {
      console.error("Loading MathJax FAILED!", err);
    }

    // Load Pseudocode (idempotent)
    try {
      await window.__rsmCachedLibs.loadPseudocode();
    } catch (err) {
      console.error("Loading pseudocode FAILED!", err);
    }

    // Handrails - set up event listeners once
    try {
      const hr = await import(`${path}handrails.js`);
      hr.setup();
    } catch (err) {
      console.error("Loading handrails.js FAILED!", err);
    }

    // Keyboard - set up event listeners once
    try {
      if (keys) {
        const kbd = await import(`${path}keyboard.js`);
        kbd.setup(root);
      }
    } catch (err) {
      console.error("Loading keyboard.js FAILED!", err);
    }

    // Minimap - set up event listeners once
    try {
      const mm = await import(`${path}minimap.js`);
      mm.setup();
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

  // Use cached libraries - don't re-import
  if (!window.__rsmCachedLibs) {
    console.warn("onrender called before onload - libraries not cached");
    renderInProgress = false;
    return;
  }

  try {
    // Icons - safe to call multiple times
    try {
      const icons = await import(`${window.__rsmCachedPath}icons.js`);
      icons.setup(root);
    } catch (err) {
      console.error("Loading icons.js FAILED!", err);
    }

    // Re-typeset math
    try {
      await window.__rsmCachedLibs.typesetMath(root);
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
      const tips = await import(`${window.__rsmCachedPath}tooltips.js`);
      tips.createTooltips();
    } catch (err) {
      console.error("Loading tooltips FAILED!", err);
    }

  } catch (err) {
    console.error("An error occurred during render:", err);
  } finally {
    renderInProgress = false;
  }
}
