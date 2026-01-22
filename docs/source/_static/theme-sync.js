/**
 * Sync PyData Sphinx Theme with RSM iframe themes
 *
 * Sphinx uses html[data-theme="light|dark"] attribute
 * RSM uses .dark-theme class on documentElement
 */

function syncIframeThemes() {
  const sphinxTheme = document.documentElement.getAttribute('data-theme');
  const isDark = sphinxTheme === 'dark';

  // Find all RSM example iframes
  const iframes = document.querySelectorAll('.rsm-example-iframe');

  iframes.forEach(iframe => {
    try {
      const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
      if (isDark) {
        iframeDoc.documentElement.classList.add('dark-theme');
      } else {
        iframeDoc.documentElement.classList.remove('dark-theme');
      }
    } catch (e) {
      console.warn('Could not access iframe document:', e);
    }
  });
}

// Sync on page load
window.addEventListener('load', syncIframeThemes);

// Watch for theme changes using MutationObserver
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
      syncIframeThemes();
    }
  });
});

// Start observing the document element for attribute changes
observer.observe(document.documentElement, {
  attributes: true,
  attributeFilter: ['data-theme']
});

// Listen for resize messages from RSM example iframes
window.addEventListener('message', function(event) {
  if (event.data.type === 'rsm-resize') {
    // Find the iframe that sent the message
    const iframes = document.querySelectorAll('.rsm-example-iframe');
    iframes.forEach(iframe => {
      if (iframe.contentWindow === event.source) {
        iframe.style.height = event.data.height + 'px';
      }
    });
  }
});
