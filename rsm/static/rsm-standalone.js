var RSM = (() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // rsm/static/onload.js
  var onload_exports = {};
  __export(onload_exports, {
    onload: () => onload,
    onrender: () => onrender
  });

  // rsm/static/libraries.js
  var mathJaxLoaded = false;
  var mathJaxLoadPromise = null;
  function loadMathJax() {
    if (mathJaxLoaded) {
      return Promise.resolve();
    }
    if (mathJaxLoadPromise) {
      return mathJaxLoadPromise;
    }
    const config = document.createElement("script");
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
    const script = document.createElement("script");
    script.type = "text/javascript";
    script.id = "MathJax-script";
    script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js";
    document.body.appendChild(script);
    mathJaxLoadPromise = new Promise((res, rej) => {
      script.onload = async () => {
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
  async function typesetMath(root2 = document) {
    if (!window.MathJax?.typesetPromise) {
      console.warn("MathJax not ready for typesetting");
      return;
    }
    const element = root2 === document ? document.body : root2;
    const existingContainers = element.querySelectorAll("mjx-container");
    if (existingContainers.length > 0) {
      existingContainers.forEach((el) => el.remove());
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
  var pseudocodeLoaded = false;
  var pseudocodeLoadPromise = null;
  function loadPseudocode() {
    if (pseudocodeLoaded) {
      return Promise.resolve();
    }
    if (pseudocodeLoadPromise) {
      return pseudocodeLoadPromise;
    }
    const script = document.createElement("script");
    script.type = "text/javascript";
    script.id = "pseudocode-script";
    script.src = "https://cdn.jsdelivr.net/npm/pseudocode@latest/build/pseudocode.min.js";
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

  // rsm/static/handrails.js
  function setup() {
    document.querySelectorAll(".hr > .hr-menu-zone > .hr-menu").forEach((menu) => {
      menu.addEventListener("mouseleave", function() {
        closeMenu(menu);
      });
    });
    document.querySelectorAll(".hr > .hr-border-zone > .hr-border-dots").forEach((dots) => {
      dots.addEventListener("click", function(ev) {
        const siblings = Array.from(this.parentElement.parentElement.children);
        const target = siblings.find((sibling) => sibling.classList.contains("hr-menu-zone"));
        if (target) {
          target.style.display = "block";
        }
        ;
      });
    });
    document.querySelectorAll(".hr > .hr-menu-zone > .hr-menu > .hr-menu-item.link:not(.disabled)").forEach((btn) => {
      btn.addEventListener("click", (ev) => copyLink(ev.target));
    });
    document.querySelectorAll(".hr > .hr-collapse-zone > .hr-collapse").forEach((btn) => {
      btn.addEventListener("click", (ev) => toggleHandrail(ev.target));
    });
    document.querySelectorAll(".hr.step > .hr-menu-zone > .hr-menu > .hr-menu-item.collapse-subproof:not(.disabled)").forEach((btn) => {
      btn.addEventListener("click", (ev) => toggleHandrail(ev.target));
    });
    document.querySelectorAll(".hr.step > .hr-menu-zone > .hr-menu > .hr-menu-item.collapse-steps:not(.disabled)").forEach((btn) => {
      btn.addEventListener("click", (ev) => collapseAll(ev.target, true));
    });
    document.querySelectorAll(".hr.proof > .hr-menu-zone > .hr-menu > .hr-menu-item.collapse-steps:not(.disabled)").forEach((btn) => {
      btn.addEventListener("click", (ev) => collapseAll(ev.target, false));
    });
    const resizeObserver = new ResizeObserver(updateHeight);
    document.querySelectorAll(".hr.hr-offset > .hr-content-zone").forEach((el) => resizeObserver.observe(el));
  }
  function closeMenu(menu) {
    menu.parentElement.style.display = "none";
    menu.querySelectorAll("& > .hr-menu-item").forEach((it) => it.classList.remove("active"));
  }
  function updateHeight(entries) {
    for (const entry of entries) {
      const hr = entry.target.parentElement;
      const elementsToResize = hr.querySelectorAll("& > .hr-border-zone, & > .hr-spacer-zone, & > .hr-info-zone");
      elementsToResize.forEach((el) => {
        el.style.height = `${entry.contentRect.height}px`;
      });
    }
  }
  function toggleHandrail(target) {
    const hr = target.closest(".hr");
    if (hr.classList.contains("hr-collapsed")) {
      openHandrail(hr);
    } else {
      closeHandrail(hr);
    }
    ;
  }
  function openHandrail(hr) {
    hr.classList.remove("hr-collapsed");
    const rest = getRest(hr);
    rest.forEach((el) => {
      el.classList.remove("hide");
    });
    const icon = hr.querySelector("& .icon.expand");
    if (!icon) return;
    icon.classList.remove("expand");
    icon.classList.add("collapse");
    icon.innerHTML = `
                    <svg width="8" height="14" viewBox="0 0 8 14" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
                      <path d="M1 1L7 7L1 13" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    `;
    const item_text = icon.nextElementSibling;
    if (item_text && item_text.classList.contains("hr-menu-item-text")) {
      item_text.textContent = "Collapse";
    }
    ;
  }
  function closeHandrail(hr) {
    hr.classList.add("hr-collapsed");
    const rest = getRest(hr);
    rest.forEach((el) => {
      el.classList.add("hide");
    });
    const icon = hr.querySelector("& .icon.collapse");
    if (!icon) return;
    icon.classList.remove("collapse");
    icon.classList.add("expand");
    icon.innerHTML = `
                    <svg width="14" height="8" viewBox="0 0 14 8" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
                      <path d="M1 1L7 7L13 1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    `;
    const item_text = icon.nextElementSibling;
    if (item_text && item_text.classList.contains("hr-menu-item-text")) {
      item_text.textContent = "Expand";
    }
    ;
  }
  function getRest(hr) {
    let rest;
    if (hr.classList.contains("hr-labeled")) {
      rest = hr.querySelectorAll("& > .hr-content-zone > :not(.hr-label)");
    } else if (hr.classList.contains("step")) {
      rest = hr.querySelectorAll("& > .hr-content-zone > :not(.statement)");
    } else {
      rest = Array.from(hr.parentElement.children).filter((el) => {
        return el !== hr;
      });
    }
    ;
    return rest;
  }
  function collapseAll(target, withinSubproof = true) {
    let qry;
    if (withinSubproof) {
      qry = "& > .hr-content-zone > .subproof > .hr-content-zone > .step:has(.subproof)";
    } else {
      qry = "& > .hr-content-zone > .step:has(.subproof)";
    }
    const hr = target.closest(".hr");
    const ex_icon = hr.querySelector("& .icon.expand-all");
    if (ex_icon) {
      hr.querySelectorAll(qry).forEach((st) => openHandrail(st));
      ex_icon.classList.remove("expand-all");
      ex_icon.classList.add("collapse-all");
      ex_icon.innerHTML = `
                    <svg width="9" height="9" viewBox="5 5 14 14" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
                      <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                      <path d="M7 7l5 5l-5 5" />
                      <path d="M13 7l5 5l-5 5" />
                    </svg>
                    `;
      const item_text = ex_icon.nextElementSibling;
      if (item_text && item_text.classList.contains("hr-menu-item-text")) {
        item_text.textContent = "Collapse all";
      }
      ;
      return;
    }
    const co_icon = hr.querySelector("& .icon.collapse-all");
    if (co_icon) {
      hr.querySelectorAll(qry).forEach((st) => closeHandrail(st));
      co_icon.classList.remove("collapse-all");
      co_icon.classList.add("expand-all");
      co_icon.innerHTML = `
                    <svg width="9" height="9" viewBox="5 5 14 14" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
                      <path d="M7 7l5 5l5 -5" />
                      <path d="M7 13l5 5l5 -5" />
                    </svg>
                    `;
      const item_text = co_icon.nextElementSibling;
      if (item_text && item_text.classList.contains("hr-menu-item-text")) {
        item_text.textContent = "Expand all";
      }
      ;
      return;
    }
  }
  async function copyLink(target) {
    const url = document.location.href.split("#")[0];
    const hr = target.closest(".hr");
    let needs_anchor = true;
    let anchor = "";
    let link = "";
    if (!hr.classList.contains("heading")) {
      anchor = hr.id;
    } else {
      const section = hr.closest("section");
      if (!section.classList.contains("level-1")) {
        anchor = section.id;
      } else {
        needs_anchor = false;
      }
    }
    if (needs_anchor && !anchor) {
      launchToast("Could not copy link.", "error");
      return;
    }
    link = `${url}#${anchor}`;
    try {
      await navigator.clipboard.writeText(link);
      launchToast("Link copied to clipboard.", "success");
    } catch (error) {
      launchToast("Could not copy link.", "error");
    }
  }
  function makeToast(text, style) {
    const toast = document.createElement("div");
    toast.className = `toast ${style}`;
    const icon = document.createElement("span");
    icon.className = `icon ${style}`;
    toast.appendChild(icon);
    switch (style) {
      case "success":
        icon.innerHTML = `
        <svg width="18" height="18" viewBox="2 2 20 20" fill="#3C4952" stroke-width="0" xmlns="http://www.w3.org/2000/svg">
          <path d="M17 3.34a10 10 0 1 1 -14.995 8.984l-.005 -.324l.005 -.324a10 10 0 0 1 14.995 -8.336zm-1.293 5.953a1 1 0 0 0 -1.32 -.083l-.094 .083l-3.293 3.292l-1.293 -1.292l-.094 -.083a1 1 0 0 0 -1.403 1.403l.083 .094l2 2l.094 .083a1 1 0 0 0 1.226 0l.094 -.083l4 -4l.083 -.094a1 1 0 0 0 -.083 -1.32z" />
        </svg>
        `;
        break;
      case "error":
        icon.innerHTML = `
        <svg width="18" height="18" viewBox="2 2 20 20" fill="#3C4952" stroke-width="0" xmlns="http://www.w3.org/2000/svg">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M17 3.34a10 10 0 1 1 -14.995 8.984l-.005 -.324l.005 -.324a10 10 0 0 1 14.995 -8.336zm-6.489 5.8a1 1 0 0 0 -1.218 1.567l1.292 1.293l-1.292 1.293l-.083 .094a1 1 0 0 0 1.497 1.32l1.293 -1.292l1.293 1.292l.094 .083a1 1 0 0 0 1.32 -1.497l-1.292 -1.293l1.292 -1.293l.083 -.094a1 1 0 0 0 -1.497 -1.32l-1.293 1.292l-1.293 -1.292l-.094 -.083z" />
        </svg>
        `;
        break;
    }
    const msg = document.createElement("span");
    msg.className = "msg";
    msg.innerText = text;
    toast.appendChild(msg);
    const spacer = document.createElement("span");
    spacer.className = "spacer";
    toast.appendChild(spacer);
    const close = document.createElement("span");
    close.className = "icon close";
    close.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
          <path d="M13 1L1 13M1 1L13 13" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        `;
    close.addEventListener("click", (ev) => toast.remove());
    toast.appendChild(close);
    const bg = document.createElement("div");
    bg.className = "bg";
    toast.appendChild(bg);
    return toast;
  }
  function launchToast(text, style = "information") {
    const toast = makeToast(text, style);
    document.querySelector(".manuscriptwrapper").appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 5e3);
  }

  // rsm/static/keyboard.js
  function setup2(root2) {
    root2.addEventListener("keydown", (event) => {
      if (["j", "k"].includes(event.key)) {
        event.preventDefault();
        event.stopPropagation();
        focusPrevOrNext(event.key == "j" ? "next" : "prev", root2);
      }
    });
    root2.addEventListener("keydown", (event) => {
      if (["h", "l"].includes(event.key)) {
        event.preventDefault();
        event.stopPropagation();
        focusUpOrDown(event.key == "h" ? "down" : "up", root2);
      }
    });
    root2.addEventListener("keydown", (event) => {
      if (event.key == "H") {
        event.stopPropagation();
        focusTop();
      }
      ;
    });
    root2.addEventListener("keydown", (event) => {
      if (event.key == ".") {
        event.stopPropagation();
        toggleMenu(document.activeElement);
      }
      ;
    });
    root2.addEventListener("keydown", (event) => {
      if (event.key == ",") {
        event.stopPropagation();
        toggleCollapse(document.activeElement);
      }
      ;
    });
    root2.addEventListener("keydown", (event) => {
      if (event.key == ";") {
        event.stopPropagation();
        toggleCollapseAll(document.activeElement);
      }
      ;
    });
    root2.addEventListener("keydown", (event) => {
      if (event.key == "z") {
        event.stopPropagation();
        scrollToMiddle(document.activeElement);
      }
      ;
    });
    root2.addEventListener("keydown", (event) => {
      if (["ArrowUp", "ArrowDown"].includes(event.key)) {
        event.preventDefault();
        event.stopPropagation();
        menuUpOrDown(document.activeElement, event.key == "ArrowUp" ? "up" : "down");
      }
    });
    root2.addEventListener("keyup", (event) => {
      event.preventDefault();
      if (event.keyCode === 13) {
        event.preventDefault();
        event.stopPropagation();
        executeActiveMenuItem(document.activeElement);
      }
    });
    root2.addEventListener("keydown", (event) => {
      if (event.key == "i") {
        event.stopPropagation();
        toggleTooltip(document.activeElement);
      }
    });
  }
  function focusTop(root2) {
    const focusable = getFocusableElements(root2);
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
    if (activeItems.length > 1) {
      console.log("more than one active items, ignoring");
      return;
    }
    ;
    const cls = Array.from(activeItems[0].classList).filter((cls2) => cls2 !== "active" && cls2 !== "hr-menu-item");
    if (cls.length == 0) {
      console.log(`unknown item`);
      return;
    }
    ;
    if (cls.length > 1) {
      console.log(`item has too many classes, ignoring`);
      return;
    }
    ;
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
  function focusUpOrDown(direction, root2) {
    const focusableElements = getFocusableElements(root2);
    let current = document.activeElement;
    let index = focusableElements.indexOf(current);
    if (index == -1) {
      maybeScrollToMiddle(focusableElements[0], direction);
      return;
    }
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
      } else if (direction == "up" && index > 0) {
        targetSection = siblingSections[index - 1];
      }
      const target2 = targetSection?.querySelector(".heading");
      if (target2) {
        target2.focus();
        maybeScrollToMiddle(target2, direction);
      }
      return;
    }
    ;
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
  function focusPrevOrNext(direction, root2) {
    const focusableElements = getFocusableElements(root2);
    let index = focusableElements.indexOf(document.activeElement);
    console.log("index of current focused element:", index);
    if (index !== -1) {
      if (direction == "next") {
        do {
          index = (index + 1) % focusableElements.length;
        } while (!isFocusable(focusableElements[index]));
      } else if (direction == "prev") {
        do {
          index = (index - 1 + focusableElements.length) % focusableElements.length;
        } while (!isFocusable(focusableElements[index]));
      } else {
        console.log(`unknown direction ${direction}`);
      }
    } else {
      index = 0;
    }
    console.log("element to be focused:", focusableElements[index]);
    console.log("index of element to be focused:", index);
    focusableElements[index].focus();
    maybeScrollToMiddle(focusableElements[index], direction == "next" ? "down" : "up");
  }
  function getFocusableElements(root2) {
    return Array.from(
      root2.querySelectorAll(`
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
      menu.querySelectorAll("& > .hr-menu > .hr-menu-item").forEach((it) => it.classList.remove("active"));
      menu.style.display = "none";
    }
    ;
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
      behavior: "smooth"
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
      scrollAmount = -elementTop;
    } else {
      if (elementTop + offset < 0) scrollAmount = -elementTop;
      else if (farEnoughFromCenter) scrollAmount = offset;
      else return;
    }
    if (direction == "down" && scrollAmount < 0) return;
    if (direction == "up" && scrollAmount > 0) return;
    window.scrollBy({
      top: scrollAmount,
      behavior: "smooth"
    });
  }

  // rsm/static/minimap.js
  function setup3() {
    const items = document.querySelectorAll("ul.contents li.item");
    const num_items = items.length;
    items.forEach((item, idx) => {
      let percent = (idx + 1) / num_items * 100;
      item.addEventListener("mouseenter", () => {
        highlightMinimap(percent, "mouse");
      });
      item.querySelectorAll("a.reference").forEach(
        (a) => a.addEventListener("focus", () => {
          highlightMinimap(percent, "mouse");
        })
      );
    });
    window.addEventListener("scroll", () => {
      const toc_mm = document.querySelector(".toc-wrapper > .minimap");
      const float_mm = document.querySelector(".float-minimap-wrapper > .minimap");
      if (!toc_mm || !float_mm) return;
      if (withinView(toc_mm, false)) {
        float_mm.classList.add("hide");
      } else {
        float_mm.classList.remove("hide");
      }
      ;
    });
    const mm = document.querySelector(".float-minimap-wrapper > .minimap");
    const sections = Array.from(document.querySelectorAll("section"));
    window.addEventListener("scroll", () => {
      if (!mm) return;
      const isHidden = mm.classList.contains("hide") || getComputedStyle(mm).display == "none" || getComputedStyle(mm.parentElement).display == "none";
      if (isHidden) return;
      const lastInViewport = sections.findLast((sec) => withinView(sec, true));
      const circle = document.querySelector(`#mm-${lastInViewport?.id}`);
      let percent;
      if (circle) {
        const circle_rect = circle.getBoundingClientRect();
        const mm_rect = mm.getBoundingClientRect();
        percent = (circle_rect.bottom - mm_rect.top + 12) / mm.offsetHeight * 100;
      } else {
        percent = 0;
      }
      ;
      highlightMinimap(percent, "scroll");
    });
  }
  function withinView(el, top = true) {
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
    const rect = el.getBoundingClientRect();
    if (top) {
      return rect.top < viewportHeight / 2 && rect.bottom > 0;
    } else {
      return rect.top < viewportHeight && rect.bottom > 0;
    }
    ;
  }
  function highlightMinimap(percent, name) {
    document.getElementById(`stop-follow-${name}-1`).setAttribute("offset", `${percent}%`);
    document.getElementById(`stop-follow-${name}-2`).setAttribute("offset", `${percent}%`);
  }

  // rsm/static/icons.js
  var icons = {
    "collapse": `<svg width="8" height="14" viewBox="0 0 8 14" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
<path d="M1 1L7 7L1 13" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`,
    "collapse-all": `<svg width="9" height="9" viewBox="5 5 14 14" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
<path stroke="none" d="M0 0h24v24H0z" fill="none"/>
<path d="M7 7l5 5l-5 5" />
<path d="M13 7l5 5l-5 5" />
</svg>`,
    "ext": `<svg width="15" height="15" viewBox="3 3 18 18" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
<path stroke="none" d="M0 0h24v24H0z" fill="none"/>
<path d="M12 6h-6a2 2 0 0 0 -2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-6" />
<path d="M11 13l9 -9" />
<path d="M15 4h5v5" />
</svg>`,
    "dots": `<svg width="24" height="24" viewBox="10 3 4 18" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
<path stroke="none" d="M0 0h24v24H0z" fill="none"/>
<path d="M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
<path d="M12 19m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
<path d="M12 5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
</svg>`,
    "link": `<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
<path d="M6 12.0003L12 6.00031M8 3.00031L8.463 2.46431C9.40081 1.52663 10.6727 0.999906 11.9989 1C13.325 1.00009 14.5968 1.527 15.5345 2.46481C16.4722 3.40261 16.9989 4.6745 16.9988 6.00066C16.9987 7.32682 16.4718 8.59863 15.534 9.53631L15 10.0003M10.0001 15.0003L9.60314 15.5343C8.65439 16.4725 7.37393 16.9987 6.03964 16.9987C4.70535 16.9987 3.42489 16.4725 2.47614 15.5343C2.0085 15.0719 1.63724 14.5213 1.38385 13.9144C1.13047 13.3076 1 12.6565 1 11.9988C1 11.3412 1.13047 10.69 1.38385 10.0832C1.63724 9.47628 2.0085 8.92571 2.47614 8.46331L3.00014 8.00031" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`,
    "tree": `<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
<path d="M3.57525 14.0448L6.00051 10.36M7.78824 7.64238L10.211 3.95918M7.79153 10.364L10.2134 14.044M12.0004 3.96001L14.4265 7.64801M4.36842 15.4C4.36842 14.9757 4.19098 14.5687 3.87513 14.2686C3.55928 13.9686 3.13089 13.8 2.68421 13.8C2.23753 13.8 1.80914 13.9686 1.49329 14.2686C1.17744 14.5687 1 14.9757 1 15.4C1 15.8243 1.17744 16.2313 1.49329 16.5314C1.80914 16.8314 2.23753 17 2.68421 17C3.13089 17 3.55928 16.8314 3.87513 16.5314C4.19098 16.2313 4.36842 15.8243 4.36842 15.4ZM12.7895 2.6C12.7895 2.17565 12.612 1.76869 12.2962 1.46863C11.9803 1.16857 11.5519 1 11.1053 1C10.6586 1 10.2302 1.16857 9.91435 1.46863C9.5985 1.76869 9.42105 2.17565 9.42105 2.6C9.42105 3.02435 9.5985 3.43131 9.91435 3.73137C10.2302 4.03143 10.6586 4.2 11.1053 4.2C11.5519 4.2 11.9803 4.03143 12.2962 3.73137C12.612 3.43131 12.7895 3.02435 12.7895 2.6ZM12.7895 15.4C12.7895 14.9757 12.612 14.5687 12.2962 14.2686C11.9803 13.9686 11.5519 13.8 11.1053 13.8C10.6586 13.8 10.2302 13.9686 9.91435 14.2686C9.5985 14.5687 9.42105 14.9757 9.42105 15.4C9.42105 15.8243 9.5985 16.2313 9.91435 16.5314C10.2302 16.8314 10.6586 17 11.1053 17C11.5519 17 11.9803 16.8314 12.2962 16.5314C12.612 16.2313 12.7895 15.8243 12.7895 15.4ZM8.57895 9C8.57895 8.57565 8.4015 8.16869 8.08565 7.86863C7.7698 7.56857 7.34142 7.4 6.89474 7.4C6.44806 7.4 6.01967 7.56857 5.70382 7.86863C5.38797 8.16869 5.21053 8.57565 5.21053 9C5.21053 9.42435 5.38797 9.83131 5.70382 10.1314C6.01967 10.4314 6.44806 10.6 6.89474 10.6C7.34142 10.6 7.7698 10.4314 8.08565 10.1314C8.4015 9.83131 8.57895 9.42435 8.57895 9ZM17 9C17 8.57565 16.8226 8.16869 16.5067 7.86863C16.1909 7.56857 15.7625 7.4 15.3158 7.4C14.8691 7.4 14.4407 7.56857 14.1249 7.86863C13.809 8.16869 13.6316 8.57565 13.6316 9C13.6316 9.42435 13.809 9.83131 14.1249 10.1314C14.4407 10.4314 14.8691 10.6 15.3158 10.6C15.7625 10.6 16.1909 10.4314 16.5067 10.1314C16.8226 9.83131 17 9.42435 17 9Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`,
    "code": `<svg width="18" height="16" viewBox="0 0 18 16" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
<path d="M4.55556 4.5L1 8L4.55556 11.5M13.4444 4.5L17 8L13.4444 11.5M10.7778 1L7.22222 15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`
  };
  function setup4(root2) {
    for (const icon in icons) {
      root2.querySelectorAll(`.icon.${icon}`).forEach((iw) => {
        iw.innerHTML = icons[`${icon}`];
      });
    }
  }

  // rsm/static/tooltips.js
  function createTooltips() {
    $(".manuscriptwrapper a.reference:not(.tooltipstered)").tooltipster({
      theme: ["tooltipster-shadow", "tooltipster-shadow-rsm"],
      minWidth: 100,
      maxWidth: 500,
      trigger: "custom",
      triggerOpen: {
        mouseenter: true,
        touchstart: true
      },
      triggerClose: {
        click: true,
        mouseleave: true,
        originClick: true,
        touchleave: true
      },
      functionInit: function(instance, helper) {
        let target = $(helper.origin).attr("href");
        if (!target) {
          console.warn("Target does not have an href attribute");
          return;
        }
        let content = "";
        target = target.replaceAll(".", "\\.");
        target = target.replaceAll(":", "\\:");
        if (target == "#") {
          content = '<span class="error">target node has no label</span>';
          setTooltipContent(instance, content);
          helper.origin.classList.add("error");
          return;
        }
        ;
        let tag = $(target).prop("tagName");
        if (!$(target)[0]) {
          return;
        }
        let classes = $(target)[0].classList;
        let clone = void 0;
        if (["P", "LI", "FIGURE"].includes(tag)) {
          content = $(target).html();
          content = `<div>${content}</div>`;
        } else if (tag == "SPAN" && classes.contains("math")) {
          content = $(target).html();
          content = `<div>${content}</div>`;
        } else if (tag == "SPAN") {
          content = $(target).parent().html();
          content = `<div>${content}</div>`;
        } else if (tag == "DT") {
          content = $(target).next().html();
        } else if (tag == "TABLE") {
          content = $(target)[0].outerHTML;
        } else if (tag == "SECTION") {
          clone = $(target).clone();
          clone.children().slice(2).remove();
          stripHandrail(clone);
          clone.css("font-size", "0.7rem");
          content = clone.html();
        } else if (tag == "A") {
          content = $(target).parent().html();
          content = `<div>${content}</div>`;
        } else if (tag == "DIV") {
          switch (true) {
            case classes.contains("step"):
              clone = $(target).find(".statement").clone();
              stripHandrail(clone);
              clone.css("font-size", "0.7rem");
              content = clone.html();
              break;
            case Array.from(classes).filter((cls) => ["math", "algorithm"].includes(cls)).length > 0:
              content = $(target).html();
              break;
            case Array.from(classes).filter((cls) => ["paragraph", "mathblock", "theorem", "proposition", "remark", "bibitem"].includes(cls)).length > 0:
              clone = $(target).clone();
              stripHandrail(clone);
              content = $(clone).html();
              break;
            case true:
              console.log(`tooltip target DIV with unknown class: ${classes}`);
          }
        } else {
          console.log(`tooltip target with unknown tag ${tag}`);
        }
        setTooltipContent(instance, content);
      }
    });
  }
  function stripHandrail(hr) {
    hr.find(".hr-collapse-zone").remove();
    hr.find(".hr-menu-zone").remove();
    hr.find(".hr-border-zone").remove();
    hr.find(".hr-spacer-zone").remove();
    hr.find(".hr-info-zone").remove();
  }
  function setTooltipContent(tt, content) {
    content = `<div class="manuscriptwrapper">${content}</div>`;
    tt.content($(content));
  }

  // rsm/static/onload.js
  async function onload(root2 = null, { keys = true } = {}) {
    if (!root2) root2 = document;
    if (window.__rsmInitialized) {
      return onrender(root2);
    }
    try {
      try {
        await loadMathJax();
      } catch (err) {
        console.error("Loading MathJax FAILED!", err);
      }
      try {
        await loadPseudocode();
      } catch (err) {
        console.error("Loading pseudocode FAILED!", err);
      }
      try {
        setup();
      } catch (err) {
        console.error("Loading handrails.js FAILED!", err);
      }
      try {
        if (keys) {
          setup2(root2);
        }
      } catch (err) {
        console.error("Loading keyboard.js FAILED!", err);
      }
      try {
        setup3();
      } catch (err) {
        console.error("Loading minimap.js FAILED!", err);
      }
      window.__rsmInitialized = true;
      await onrender(root2);
    } catch (err) {
      console.error("An error occurred during initialization:", err);
    }
  }
  var renderInProgress = false;
  async function onrender(root2 = null) {
    if (renderInProgress) {
      return;
    }
    renderInProgress = true;
    if (!root2) root2 = document;
    try {
      try {
        setup4(root2);
      } catch (err) {
        console.error("Loading icons.js FAILED!", err);
      }
      try {
        await typesetMath(root2);
      } catch (err) {
        console.error("MathJax typeset FAILED!", err);
      }
      try {
        const elements = root2.querySelectorAll("pre.pseudocode:not(.rendered)");
        if (elements.length && window.pseudocode) {
          elements.forEach((el) => {
            pseudocode.renderElement(el, {
              lineNumber: true,
              noEnd: true
            });
            el.classList.add("rendered");
          });
        }
      } catch (err) {
        console.error("Pseudocode render FAILED!", err);
      }
      try {
        createTooltips();
      } catch (err) {
        console.error("Loading tooltips FAILED!", err);
      }
    } catch (err) {
      console.error("An error occurred during render:", err);
    } finally {
      renderInProgress = false;
    }
  }
  return __toCommonJS(onload_exports);
})();
