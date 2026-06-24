// keyboard.js
//
// Keyboard interaction
//
import { toggleHandrail, collapseAll, toggleMenuFor, closeMenu, menuOpenOn } from './handrails.js';

export function setup(root) {
  // Single-key shortcuts must not preempt the browser. Bail when a modifier is
  // held (so CMD/CTRL+L still reaches the address bar, etc.) or when focus is in
  // an editable field (so typing letters is never hijacked). Shift is allowed:
  // "H" is an intentional shortcut.
  function ignore(event) {
    if (event.metaKey || event.ctrlKey || event.altKey) return true;
    const t = event.target;
    if (!t) return false;
    if (t.isContentEditable) return true;
    return t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT";
  }

  // Nagivation: next or previous
  root.addEventListener('keydown', (event) => {
    if (ignore(event)) return;
    if (['j', 'k'].includes(event.key)) {
      event.preventDefault();
      event.stopPropagation();
      focusPrevOrNext(event.key == 'j' ? "next" : "prev", root);
    }
  });

  // Nagivation: up or down
  root.addEventListener('keydown', (event) => {
    if (ignore(event)) return;
    if (['h', 'l'].includes(event.key)) {
      event.preventDefault();
      event.stopPropagation();
      focusUpOrDown(event.key == 'h' ? "down" : "up", root);
    }
  });

  // Navigation: back to top
  root.addEventListener('keydown', (event) => {
    if (ignore(event)) return;
    if (event.key == "H") { event.stopPropagation(); focusTop(root); };
  });

  // Escape closes any open handrail menu (allowed from inputs too).
  root.addEventListener('keydown', (event) => {
    if (event.key === "Escape") closeMenu();
  });

  // Basic actions on the currently focused element
  root.addEventListener('keydown', (event) => {
    if (ignore(event)) return;
    if (event.key == ".") { event.stopPropagation(); toggleMenuFor(document.activeElement); };
  });
  root.addEventListener('keydown', (event) => {
    if (ignore(event)) return;
    if (event.key == ",") { event.stopPropagation(); toggleCollapse(document.activeElement); };
  });
  root.addEventListener('keydown', (event) => {
    if (ignore(event)) return;
    if (event.key == ";") { event.stopPropagation(); toggleCollapseAll(document.activeElement); };
  });
  root.addEventListener('keydown', (event) => {
    if (ignore(event)) return;
    if (event.key == "z") { event.stopPropagation(); scrollToMiddle(document.activeElement); };
  });

  // Menu navigation: only when a menu is actually open on the focused handrail,
  // so the arrow keys and Enter keep their normal behavior otherwise.
  root.addEventListener('keydown', (event) => {
    if (ignore(event)) return;
    if (!["ArrowUp", "ArrowDown"].includes(event.key)) return;
    if (!menuOpenOn(document.activeElement)) return;
    event.preventDefault();
    event.stopPropagation();
    menuUpOrDown(document.activeElement, event.key == "ArrowUp" ? "up" : "down");
  });
  root.addEventListener("keyup", (event) => {
    if (ignore(event)) return;
    if (event.keyCode !== 13) return;
    if (!menuOpenOn(document.activeElement)) return;
    event.preventDefault();
    event.stopPropagation();
    executeActiveMenuItem(document.activeElement);
  });

  // Tooltips
  root.addEventListener('keydown', (event) => {
    if (ignore(event)) return;
    if (event.key == "i") {
      event.stopPropagation();
      toggleTooltip(document.activeElement);
    }
  });

  // Math functions
  // root.addEventListener('keydown', (event) => {
  //   if (event.key == "a") {
  //     highlightSymbols(document.activeElement);
  //   }
  // });

}


function focusTop(root) {
  // Jump to the top of the document. "#top" is the browser-native fragment for
  // the document top: it scrolls to the very top (no element needed) and pushes
  // a history entry, so the jump rides native Back. The global hashchange
  // handler has no element to focus for "#top", so move keyboard focus to the
  // first content block here (preventScroll so it doesn't fight the hash scroll)
  // to keep SR / keyboard users with the viewport.
  location.hash = "top";
  const top = (root.querySelector(".manuscriptwrapper") || root).querySelector(".hr[id]");
  if (top) {
    if (!top.hasAttribute("tabindex")) top.setAttribute("tabindex", "-1");
    top.focus({ preventScroll: true });
  }
}


function toggleTooltip(el) {
  if (!el.classList.contains("tooltipstered")) return;
  if ($(el).tooltipster("status").open) {
    $(el).tooltipster("close");
  } else {
    $(el).tooltipster("open");
  }
}


// The menu items live in the shared singleton. While open it is portaled to
// <body> (handrails.js, to escape ancestor stacking contexts), so locate it by
// its id rather than under the focused handrail's zone. Activate the highlighted
// one by clicking it, reusing the delegated handler in handrails.js (so data-role
// dispatch stays in one place). `el` (the open-on handrail) is unused now but
// kept so the call sites and the menuOpenOn gate stay symmetric.
function openMenuEl() {
  return document.querySelector("#hr-menu-singleton .hr-menu");
}

function executeActiveMenuItem(el) {
  const menu = openMenuEl();
  if (!menu) return;
  const active = menu.querySelector(":scope > .hr-menu-item.active:not(.disabled)");
  if (active) active.click();
}


function menuUpOrDown(el, direction) {
  const menu = openMenuEl();
  if (!menu) return;
  // Only visible, enabled items participate (hidden ones are display:none).
  const items = Array.from(menu.querySelectorAll(":scope > .hr-menu-item"))
    .filter(it => it.offsetParent !== null && !it.classList.contains("disabled"));
  if (!items.length) return;

  const current = items.find(it => it.classList.contains("active"));
  let index = current ? items.indexOf(current) : -1;
  if (index === -1) {
    index = direction === "down" ? 0 : items.length - 1;
  } else {
    index = direction === "down"
      ? (index + 1) % items.length
      : (index - 1 + items.length) % items.length;
  }
  if (current) current.classList.remove("active");
  items[index].classList.add("active");
}


function focusUpOrDown(direction, root) {
  const focusableElements = getFocusableElements(root);
  let current = document.activeElement;
  let index = focusableElements.indexOf(current);

  // If not focused on anything, just focus the top element.
  if (index == -1) {
    maybeScrollToMiddle(focusableElements[0], direction);
    return;
  }

  // When focusing a heading of, say, a Subsection, we want to go to the next
  // Subsection. However, div.heading elements are children of <section> tags so if we
  // simply look for immediate siblings, we will end up in the first paragraph of the
  // current Subsection.  Instead, we need to go up to the parent <section> and look
  // for sibling <section> elements.
  if (current.classList.contains("heading")) {
    const currentSection = current.parentElement;
    const siblingSections = Array.from(currentSection.parentElement.querySelectorAll("& > section"));
    index = siblingSections.indexOf(currentSection);
    if (index == -1) {
      console.log("something went wrong");
      return;
    }

    let targetSection;
    if (direction == "down" && index < siblingSections.length - 1) {
      targetSection = siblingSections[index + 1];
    } else if ((direction == "up" && index > 0)) {
      targetSection = siblingSections[index - 1];
    }

    const target = targetSection?.querySelector(".heading");
    if (target) {
      target.focus();
      maybeScrollToMiddle(target, direction);
    }

    return;
  };

  // Otherwise, just traverse the focusable elements in order.
  index = focusableElements.indexOf(current);
  let target;
  if (index !== -1) {
    if (direction == "up") {
      for (const el of focusableElements.slice(0, index).reverse()) {
        if (el.parentElement == current.parentElement) {
          target = el;
          break;
        }
      }
    } else if (direction == "down") {
      for (const el of focusableElements.slice(index + 1)) {
        if (el.parentElement == current.parentElement) {
          target = el;
          break;
        }
      }
    } else {
      console.log(`unknown direction ${direction}`);
    }
  }
  if (target) {
    target.focus();
    maybeScrollToMiddle(target, direction);
  }
}


function focusPrevOrNext(direction, root) {
  const focusableElements = getFocusableElements(root);
  let index = focusableElements.indexOf(document.activeElement);
  console.log('index of current focused element:', index);
  if (index !== -1) {
    if (direction == "next") {
      do { index = (index + 1) % focusableElements.length; }
      while (!isFocusable(focusableElements[index]));
    } else if (direction == "prev") {
      do { index = (index - 1 + focusableElements.length) % focusableElements.length; }
      while (!isFocusable(focusableElements[index]));
    } else {
      console.log(`unknown direction ${direction}`);
    }
  } else { index = 0; }
  console.log('element to be focused:', focusableElements[index]);
  console.log('index of element to be focused:', index);
  focusableElements[index].focus();
  maybeScrollToMiddle(focusableElements[index], direction == "next" ? "down" : "up");
}


function getFocusableElements(root) {
  return Array.from(
    root.querySelectorAll(`
      a[href]:not([tabindex="-1"]),
      button:not([disabled]):not([tabindex="-1"]),
      textarea:not([disabled]):not([tabindex="-1"]),
      input:not([disabled]):not([tabindex="-1"]),
      select:not([disabled]):not([tabindex="-1"]),
      [tabindex]:not([tabindex="-1"])
    `)
  );
}


function toggleCollapse(el) {
  if (!el.classList.contains("hr")) return;
  // Collapsible if it has a chevron, or the translator marked it collapsible
  // (data-menu-collapse). The menu item itself is no longer in the hr's zone.
  const chevron = el.querySelector(":scope > .hr-collapse-zone > .hr-collapse");
  const collapse = el.getAttribute("data-menu-collapse");
  if (!chevron && (!collapse || collapse === "disabled")) return;
  toggleHandrail(el);
}


function toggleCollapseAll(el) {
  if (!el.classList.contains("hr")) return;
  const collapseAll_ = el.getAttribute("data-menu-collapse-all");
  if (!collapseAll_ || collapseAll_ === "disabled") return;
  collapseAll(el, el.classList.contains("step"));
}


function isFocusable(el) {
  if (el.classList.contains("hr-collapsed") && !el.classList.contains("hide")) return true;
  if (el.closest(".hr-collapsed") || el.closest(".hide")) return false;
  return true;
}


function scrollToMiddle(element) {
  const rect = element.getBoundingClientRect();
  const elementCenterY = rect.top + rect.height / 2;
  const viewportCenterY = window.innerHeight / 2;
  const offset = elementCenterY - viewportCenterY;

  window.scrollBy({
    top: offset,
    behavior: 'smooth',
  });
}


function maybeScrollToMiddle(element, direction) {
  const rect = element.getBoundingClientRect();
  const elementTop = rect.top;
  const elementHeight = rect.height;
  const elementCenterY = elementTop + elementHeight / 2;
  const viewportHeight = window.innerHeight;
  const viewportCenterY = viewportHeight / 2;
  const offset = elementCenterY - viewportCenterY;
  const farEnoughFromCenter = Math.abs(offset) > 48;

  let scrollAmount;
  if (elementHeight > viewportHeight) {
    // element taller than viewport: just align its top with the top of the viewport
    scrollAmount = -elementTop;
  } else {
    // If scrolling would push the element's top above the viewport,
    // limit the scroll to align the top of the element with the top of the viewport
    if (elementTop + offset < 0) scrollAmount = -elementTop;
    // Otherwise, scroll to center the element (if far enough from center)
    else if (farEnoughFromCenter) scrollAmount = offset;
    else return;
  }

  if (direction == "down" && scrollAmount < 0) return;
  if (direction == "up" && scrollAmount > 0) return;
  window.scrollBy({
    top: scrollAmount,
    behavior: 'smooth',
  });
}


function highlightSymbols(el) {
  if (!el) return;
  const qry = `.let.assumption`;
  root.querySelectorAll(qry).forEach(el => el.classList.add("hilite"));

}
