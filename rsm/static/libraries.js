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
  if (!mathJaxLoaded || !window.MathJax?.typesetPromise) {
    console.warn("MathJax not ready for typesetting");
    return;
  }

  // Remove any existing mjx-containers to prevent duplication on re-render
  const existingContainers = root.querySelectorAll("mjx-container");
  if (existingContainers.length > 0) {
    existingContainers.forEach(el => el.remove());
  }

  try {
    if (MathJax.typesetClear) {
      MathJax.typesetClear([root]);
    }
    await MathJax.typesetPromise([root]);
  } catch (err) {
    console.error("MathJax typeset error:", err);
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
