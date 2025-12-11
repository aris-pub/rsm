// keyboard.js
//
// Keyboard interaction
//
import { toggleHandrail, collapseAll } from './handrails.js';

export function setup(root) {
  // Nagivation: next or previous
  root.addEventListener('keydown', (event) => {
    if (['j', 'k'].includes(event.key)) {
      event.preventDefault();
      event.stopPropagation();
      focusPrevOrNext(event.key == 'j' ? "next" : "prev", root);
    }
  });

  // Nagivation: up or down
  root.addEventListener('keydown', (event) => {
    if (['h', 'l'].includes(event.key)) {
      event.preventDefault();
      event.stopPropagation();
      focusUpOrDown(event.key == 'h' ? "down" : "up", root);
    }
  });

  // Navigation: back to top
  root.addEventListener('keydown', (event) => {
    if (event.key == "H") { event.stopPropagation(); focusTop(); };
  });

  // Basic actions on the currently focused element
  root.addEventListener('keydown', (event) => {
    if (event.key == ".") { event.stopPropagation(); toggleMenu(document.activeElement); };
  });
  root.addEventListener('keydown', (event) => {
    if (event.key == ",") { event.stopPropagation(); toggleCollapse(document.activeElement); };
  });
  root.addEventListener('keydown', (event) => {
    if (event.key == ";") { event.stopPropagation(); toggleCollapseAll(document.activeElement); };
  });
  root.addEventListener('keydown', (event) => {
    if (event.key == "z") { event.stopPropagation(); scrollToMiddle(document.activeElement); };
  });

  // Interaction with the menu of the currently focused element
  root.addEventListener('keydown', (event) => {
    if (["ArrowUp", "ArrowDown"].includes(event.key)) {
      event.preventDefault();
      event.stopPropagation();
      menuUpOrDown(document.activeElement, event.key == "ArrowUp" ? "up" : "down");
    }
  });
  root.addEventListener("keyup", (event) => {
    event.preventDefault();
    if (event.keyCode === 13) {
      event.preventDefault();
      event.stopPropagation();
      executeActiveMenuItem(document.activeElement);
    }
  });

  // Tooltips
  root.addEventListener('keydown', (event) => {
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
  const focusable = getFocusableElements(root);
  focusable[0].focus();
  scrollToMiddle(focusable[0], "up");
}


function toggleTooltip(el) {
  if (!el.classList.contains("tooltipstered")) return;
  if ($(el).tooltipster("status").open) {
    $(el).tooltipster("close");
  } else {
    $(el).tooltipster("open");
  }
}


function executeActiveMenuItem(el) {
  const menu = el.querySelector("& > .hr-menu-zone > .hr-menu");
  if (!menu) return;
  const activeItems = menu.querySelectorAll("& > .hr-menu-item.active:not(.disabled)");
  if (activeItems.length == 0) return;
  if (activeItems.length > 1) { console.log("more than one active items, ignoring"); return; };
  const cls = Array.from(activeItems[0].classList).filter(cls => cls !== 'active' && cls !== 'hr-menu-item');
  if (cls.length == 0) { console.log(`unknown item`); return; };
  if (cls.length > 1) { console.log(`item has too many classes, ignoring`); return; };
  switch (cls[0]) {
    case "collapse-subproof":
      toggleHandrail(el);
      break;
    case "collapse-steps":
      collapseAll(el);
      break;
    case true:
      console.log($`unknown item class: ${cls[0]}`);
  }
}


function menuUpOrDown(el, direction) {
  const menu = el.querySelector("& > .hr-menu-zone");
  if (!getComputedStyle(menu).display == "none") return;

  const qry = `
      & > .hr-menu > .hr-menu-item:hover,
      & > .hr-menu > .hr-menu-item:active,
      & > .hr-menu > .hr-menu-item:focus,
      & > .hr-menu > .hr-menu-item.active
  `;
  const currentItem = menu.querySelector(qry);
  const allItems = Array.from(menu.querySelectorAll("& > .hr-menu > .hr-menu-item"));

  let index = allItems.indexOf(currentItem);
  if (index == -1) index = 0;

  if (!currentItem || index == -1) {
    index = 0;
  } else if (direction == "down") {
    index = (index + 1) % allItems.length;
  } else if (direction == "up") {
    index = (index - 1 + allItems.length) % allItems.length;
  }
  if (currentItem) currentItem.classList.remove("active");
  allItems[index].classList.add("active");
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
  const coll1 = el.querySelector("& > .hr-collapse-zone > .hr-collapse");
  const coll2 = el.querySelector("& > .hr-menu-zone .collapse-subproof:not(.disabled)");
  if (!coll1 && !coll2) return;
  toggleHandrail(el);
}


function toggleCollapseAll(el) {
  if (!el.classList.contains("hr")) return;
  const collAll = el.querySelector(`
        & > .hr-menu-zone .collapse-all:not(.disabled),
        & > .hr-menu-zone .expand-all:not(.disabled)
    `);
  const withinSubproof = el.classList.contains("step");
  if (collAll) collapseAll(el, withinSubproof);
}


function toggleMenu(el) {
  if (!el.classList.contains("hr")) return;
  const menu = el.querySelector("& > .hr-menu-zone");
  if (!menu) return;
  const style = getComputedStyle(menu);
  if (style.display == "none") menu.style.display = "block";
  else if (style.display == "block") {
    menu.querySelectorAll("& > .hr-menu > .hr-menu-item").forEach(it => it.classList.remove("active"));
    menu.style.display = "none";
  };
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
