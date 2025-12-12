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
    script.onload = async () => {
      // Wait for MathJax to fully initialize (not just script load)
      // MathJax.startup.promise might not exist immediately, so poll for it
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

// Re-typeset math after HTML content changes
export async function typesetMath(root = document) {
  if (!window.MathJax?.typesetPromise) {
    console.warn("MathJax not ready for typesetting");
    return;
  }

  // MathJax needs actual DOM elements, not the document object
  const element = root === document ? document.body : root;

  // Remove any existing mjx-containers to prevent duplication on re-render
  const existingContainers = element.querySelectorAll("mjx-container");
  if (existingContainers.length > 0) {
    existingContainers.forEach(el => el.remove());
  }

  try {
    if (MathJax.typesetClear) {
      MathJax.typesetClear([element]);
    }
    await MathJax.typesetPromise([element]);
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
