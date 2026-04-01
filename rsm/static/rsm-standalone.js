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
  var temmlLoaded = false;
  var temmlLoadPromise = null;
  function loadTemml() {
    if (temmlLoaded) return Promise.resolve();
    if (temmlLoadPromise) return temmlLoadPromise;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://cdn.jsdelivr.net/npm/temml/dist/Temml.css";
    document.head.appendChild(link);
    const script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/temml/dist/temml.min.js";
    document.head.appendChild(script);
    temmlLoadPromise = new Promise((res, rej) => {
      script.onload = () => {
        temmlLoaded = true;
        if (window.temml && !window.katex) {
          window.katex = window.temml;
        }
        res();
      };
      script.onerror = rej;
    });
    return temmlLoadPromise;
  }
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
        typeset: false
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
    const element = root2 === document ? document.body : root2;
    if (!window.temml && !window.MathJax?.typesetPromise) {
      const hasMath = element.querySelector("span.math, div.mathblock");
      if (hasMath) {
        try {
          await loadTemml();
        } catch {
          try {
            await loadMathJax();
          } catch {
          }
        }
      }
    }
    if (window.temml) {
      const BATCH = 30;
      const inlines = element.querySelectorAll("span.math");
      for (let i = 0; i < inlines.length; i++) {
        const el = inlines[i];
        const src = el.textContent;
        if (!src.startsWith("\\(") || !src.endsWith("\\)")) continue;
        const latex = src.slice(2, -2);
        el.dataset.latex = latex;
        try {
          temml.render(latex, el, { throwOnError: false });
        } catch (err) {
          console.error("temml inline error:", err);
        }
        if ((i + 1) % BATCH === 0 && i + 1 < inlines.length) {
          await new Promise((r) => requestAnimationFrame(r));
        }
      }
      const displays = element.querySelectorAll("div.mathblock");
      for (let i = 0; i < displays.length; i++) {
        const el = displays[i];
        const contentEl = el.querySelector(".hr-content-zone") || el;
        const src = contentEl.textContent.trim();
        if (!src.startsWith("$$") || !src.endsWith("$$")) continue;
        const latex = src.slice(2, -2).trim();
        el.dataset.latex = latex;
        try {
          temml.render(latex, contentEl, { displayMode: true, throwOnError: false });
        } catch (err) {
          console.error("temml display error:", err);
        }
        if ((i + 1) % BATCH === 0 && i + 1 < displays.length) {
          await new Promise((r) => requestAnimationFrame(r));
        }
      }
      return;
    }
    if (!window.MathJax?.typesetPromise) {
      console.warn("Neither temml nor MathJax ready for typesetting");
      return;
    }
    const existingContainers = element.querySelectorAll("mjx-container");
    existingContainers.forEach((el) => el.remove());
    try {
      if (MathJax.typesetClear) MathJax.typesetClear([element]);
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
  var singletonMenu = null;
  var activeHr = null;
  var delegationAttached = false;
  function setup() {
    if (delegationAttached) return;
    delegationAttached = true;
    document.addEventListener("click", function(ev) {
      const dots = ev.target.closest(".hr-border-dots");
      if (dots && dots.closest(".hr")) {
        const hr = dots.closest(".hr");
        if (activeHr === hr) {
          hideMenu();
        } else {
          singletonMenu = document.getElementById("hr-menu-singleton");
          showMenuFor(hr);
        }
        return;
      }
      const menuItem = ev.target.closest("[data-role]");
      if (menuItem && menuItem.closest("#hr-menu-singleton")) {
        const role = menuItem.getAttribute("data-role");
        if (menuItem.classList.contains("disabled")) return;
        if (!activeHr) return;
        if (role === "link") copyLink(activeHr);
        else if (role === "code") showSource(activeHr);
        else if (role === "collapse") toggleHandrail(activeHr);
        else if (role === "collapse-all") {
          const withinSubproof = activeHr.classList.contains("step");
          collapseAll(activeHr, withinSubproof);
        }
        return;
      }
      const collapseBtn = ev.target.closest(".hr-collapse");
      if (collapseBtn && collapseBtn.closest(".hr-collapse-zone")) {
        toggleHandrail(ev.target);
        return;
      }
    });
    document.addEventListener("mouseleave", function(ev) {
      if (ev.target.closest && ev.target.closest(".hr-menu") && ev.target.closest("#hr-menu-singleton")) {
        hideMenu();
      }
    }, true);
    observeOffsetHandrails();
  }
  var resizeObserver = new ResizeObserver(updateHeight);
  function observeOffsetHandrails() {
    resizeObserver.disconnect();
    document.querySelectorAll(".hr.hr-offset > .hr-content-zone").forEach((el) => resizeObserver.observe(el));
  }
  function showMenuFor(hr) {
    if (!singletonMenu) return;
    activeHr = hr;
    const label = hr.getAttribute("data-menu-label") || "";
    const collapse = hr.getAttribute("data-menu-collapse");
    const collapseAll2 = hr.getAttribute("data-menu-collapse-all");
    const link = hr.getAttribute("data-menu-link");
    const code = hr.getAttribute("data-menu-code");
    const labelEl = singletonMenu.querySelector('[data-role="label"]');
    const labelSep = singletonMenu.querySelector('[data-role="label-sep"]');
    if (labelEl) {
      labelEl.textContent = label;
      labelEl.parentElement.style.display = label ? "" : "none";
    }
    if (labelSep) labelSep.style.display = label ? "" : "none";
    configureItem(singletonMenu.querySelector('[data-role="collapse"]'), collapse);
    configureItem(singletonMenu.querySelector('[data-role="collapse-all"]'), collapseAll2);
    const collapseSep = singletonMenu.querySelector('[data-role="collapse-sep"]');
    if (collapseSep) {
      const anyCollapse = collapse || collapseAll2;
      collapseSep.style.display = anyCollapse ? "" : "none";
    }
    configureItem(singletonMenu.querySelector('[data-role="link"]'), link);
    configureItem(singletonMenu.querySelector('[data-role="code"]'), code);
    const zone = hr.querySelector(":scope > .hr-menu-zone");
    if (zone) {
      zone.appendChild(singletonMenu);
      singletonMenu.style.display = "";
      zone.style.display = "block";
    }
  }
  function configureItem(el, value) {
    if (!el) return;
    if (!value) {
      el.style.display = "none";
      el.classList.remove("disabled");
      return;
    }
    el.style.display = "";
    if (value === "disabled") {
      el.classList.add("disabled");
    } else {
      el.classList.remove("disabled");
    }
  }
  function hideMenu() {
    if (!singletonMenu) return;
    singletonMenu.style.display = "none";
    singletonMenu.querySelectorAll(".hr-menu-item").forEach((it) => it.classList.remove("active"));
    if (activeHr) {
      const zone = activeHr.querySelector(":scope > .hr-menu-zone");
      if (zone) zone.style.display = "";
    }
    activeHr = null;
  }
  function updateHeight(entries) {
    for (const entry of entries) {
      const hr = entry.target.parentElement;
      const elementsToResize = hr.querySelectorAll(":scope > .hr-border-zone, :scope > .hr-spacer-zone, :scope > .hr-info-zone");
      elementsToResize.forEach((el) => {
        el.style.height = `${entry.contentRect.height}px`;
      });
    }
  }
  function toggleHandrail(target) {
    const hr = target.closest ? target.closest(".hr") : target;
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
    const icon = hr.querySelector(":scope > .hr-collapse-zone .icon.expand");
    if (!icon) return;
    icon.classList.remove("expand");
    icon.classList.add("collapse");
    const use = icon.querySelector("use");
    if (use) use.setAttribute("href", "#hr-icon-collapse");
  }
  function closeHandrail(hr) {
    hr.classList.add("hr-collapsed");
    const rest = getRest(hr);
    rest.forEach((el) => {
      el.classList.add("hide");
    });
    const icon = hr.querySelector(":scope > .hr-collapse-zone .icon.collapse");
    if (!icon) return;
    icon.classList.remove("collapse");
    icon.classList.add("expand");
    const use = icon.querySelector("use");
    if (use) use.setAttribute("href", "#hr-icon-expand");
  }
  function getRest(hr) {
    let rest;
    if (hr.classList.contains("hr-labeled")) {
      rest = hr.querySelectorAll(":scope > .hr-content-zone > :not(.hr-label)");
    } else if (hr.classList.contains("step")) {
      rest = hr.querySelectorAll(":scope > .hr-content-zone > :not(.statement)");
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
      qry = ":scope > .hr-content-zone > .subproof > .hr-content-zone > .step:has(.subproof)";
    } else {
      qry = ":scope > .hr-content-zone > .step:has(.subproof)";
    }
    const hr = target.closest ? target.closest(".hr") : target;
    const collapseAllItem = singletonMenu ? singletonMenu.querySelector('[data-role="collapse-all"]') : null;
    const icon = collapseAllItem ? collapseAllItem.querySelector(".icon") : null;
    if (icon && icon.classList.contains("expand-all")) {
      hr.querySelectorAll(qry).forEach((st) => openHandrail(st));
      icon.classList.remove("expand-all");
      icon.classList.add("collapse-all");
      const use = icon.querySelector("use");
      if (use) use.setAttribute("href", "#hr-icon-collapse-all");
      const text = icon.nextElementSibling;
      if (text) text.textContent = "Collapse all";
    } else if (icon) {
      hr.querySelectorAll(qry).forEach((st) => closeHandrail(st));
      icon.classList.remove("collapse-all");
      icon.classList.add("expand-all");
      const use = icon.querySelector("use");
      if (use) use.setAttribute("href", "#hr-icon-expand-all");
      const text = icon.nextElementSibling;
      if (text) text.textContent = "Expand all";
    }
  }
  async function copyLink(hr) {
    let url;
    try {
      if (window.self !== window.parent) {
        url = window.parent.location.href.split("#")[0];
      } else {
        url = document.location.href.split("#")[0];
      }
    } catch (error) {
      url = document.location.href.split("#")[0];
    }
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
    const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    icon.setAttribute("class", `icon ${style}`);
    const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
    use.setAttribute("href", `#hr-icon-${style}`);
    icon.appendChild(use);
    toast.appendChild(icon);
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
  function showSource(hr) {
    const start = hr.getAttribute("data-source-start");
    const end = hr.getAttribute("data-source-end");
    const sourceDiv = document.querySelector(".rsm-source");
    if (!start || !end || !sourceDiv) {
      launchToast("No source available for this element.", "error");
      return;
    }
    const source = sourceDiv.textContent.slice(parseInt(start), parseInt(end));
    const modal = document.createElement("div");
    modal.className = "rsm-source-modal";
    modal.innerHTML = `
    <div class="rsm-source-modal-content">
      <div class="rsm-source-modal-actions">
        <button class="rsm-source-modal-icon-button copy-source" title="Copy">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
            <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
          </svg>
        </button>
        <button class="rsm-source-modal-icon-button close-modal" title="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 6 6 18"/>
            <path d="m6 6 12 12"/>
          </svg>
        </button>
      </div>
      <div class="rsm-source-modal-body">
        <pre>${source.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</pre>
      </div>
    </div>
  `;
    document.body.appendChild(modal);
    modal.style.display = "block";
    const closeBtn = modal.querySelector(".close-modal");
    const copyBtn = modal.querySelector(".copy-source");
    const closeModal = () => {
      modal.remove();
    };
    closeBtn.addEventListener("click", closeModal);
    modal.addEventListener("click", (ev) => {
      if (ev.target === modal) {
        closeModal();
      }
    });
    const escHandler = (ev) => {
      if (ev.key === "Escape") {
        closeModal();
        document.removeEventListener("keydown", escHandler);
      }
    };
    document.addEventListener("keydown", escHandler);
    copyBtn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(source);
        launchToast("Source copied to clipboard.", "success");
      } catch (error) {
        launchToast("Could not copy source.", "error");
      }
    });
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

  // rsm/static/tooltips.js
  function createTooltips() {
    $(".manuscriptwrapper a.reference:not(.external):not(.tooltipstered)").tooltipster({
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
              clone = $(target).clone();
              stripHandrail(clone);
              content = clone.html();
              break;
            case Array.from(classes).filter((cls) => ["paragraph", "mathblock", "theorem", "lemma", "corollary", "example", "exercise", "proposition", "problem", "porism", "remark", "definition", "bibitem"].includes(cls)).length > 0:
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
    $(".manuscriptwrapper .author-names sup[data-tooltip]:not(.tooltipstered)").tooltipster({
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
        let text = $(helper.origin).attr("data-tooltip");
        setTooltipContent(instance, text);
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
      if (document.querySelector("span.math, div.mathblock")) {
        try {
          await loadTemml();
        } catch (err) {
          console.warn("temml failed to load, falling back to MathJax:", err);
          try {
            await loadMathJax();
          } catch (err2) {
            console.error("MathJax fallback also FAILED!", err2);
          }
        }
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
        await typesetMath(root2);
      } catch (err) {
        console.error("Math typeset FAILED!", err);
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
        observeOffsetHandrails();
      } catch (err) {
        console.error("Re-observing offset handrails FAILED!", err);
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
