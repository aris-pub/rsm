// libraries.js
//
// Load external libraries dynamically
//

let mathJaxLoaded = false;
let mathJaxLoadPromise = null;

// Load MathJax - idempotent, only loads once
export function loadMathJax() {
  if (mathJaxLoaded) {
    return Promise.resolve();
  }
  if (mathJaxLoadPromise) {
    return mathJaxLoadPromise;
  }

  // Configure MathJax BEFORE loading the script
  // All settings must be in one object - MathJax reads this on load
  const config = document.createElement('script');
  config.innerHTML = `window.MathJax = {
      startup: {
        typeset: false  // Disable auto-typeset - we call typesetPromise explicitly
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
    script.onload = () => {
      mathJaxLoaded = true;
      res();
    };
    script.onerror = rej;
  });

  return mathJaxLoadPromise;
}

// Re-typeset math after HTML content changes
export async function typesetMath(root = document) {
  console.log(`[typesetMath] ENTER, root=${root === document ? 'document' : root.tagName || 'element'}`);

  if (!mathJaxLoaded || !window.MathJax?.typesetPromise) {
    console.warn("MathJax not ready for typesetting");
    return;
  }

  const mjxBefore = root.querySelectorAll("mjx-container").length;
  const nestedBefore = root.querySelectorAll("mjx-container mjx-container").length;
  const mathSpans = root.querySelectorAll("span.math").length;
  const mathBlocks = root.querySelectorAll("div.mathblock").length;
  const docMjxBefore = document.querySelectorAll("mjx-container").length;
  console.log(`[typesetMath] BEFORE: root mjx=${mjxBefore}, root nested=${nestedBefore}, doc mjx=${docMjxBefore}, span.math=${mathSpans}, div.mathblock=${mathBlocks}`);

  // Remove any existing mjx-containers to prevent duplication
  if (mjxBefore > 0) {
    console.log(`[typesetMath] Removing ${mjxBefore} existing mjx-containers from root`);
    root.querySelectorAll("mjx-container").forEach(el => el.remove());
    const mjxAfterRemoval = root.querySelectorAll("mjx-container").length;
    console.log(`[typesetMath] After removal: root mjx=${mjxAfterRemoval}`);
  }

  try {
    if (MathJax.typesetClear) {
      console.log("[typesetMath] Calling typesetClear");
      MathJax.typesetClear([root]);
    }
    console.log("[typesetMath] Calling typesetPromise...");
    await MathJax.typesetPromise([root]);
    console.log("[typesetMath] typesetPromise resolved");
  } catch (err) {
    console.error("MathJax typeset error:", err);
  }

  const mjxAfter = root.querySelectorAll("mjx-container").length;
  const nestedAfter = root.querySelectorAll("mjx-container mjx-container").length;
  const docMjxAfter = document.querySelectorAll("mjx-container").length;
  console.log(`[typesetMath] AFTER: root mjx=${mjxAfter}, root nested=${nestedAfter}, doc mjx=${docMjxAfter}`);
  console.log(`[typesetMath] EXIT`);
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
