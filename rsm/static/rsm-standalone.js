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

  // rsm/static/notation.js
  var _macros = null;
  function storageKey() {
    return "rsm-notation:" + location.pathname;
  }
  function loadOverrides() {
    try {
      return JSON.parse(localStorage.getItem(storageKey())) || {};
    } catch {
      return {};
    }
  }
  function saveOverride(macro, latex) {
    const overrides = loadOverrides();
    overrides[macro] = latex;
    try {
      localStorage.setItem(storageKey(), JSON.stringify(overrides));
    } catch {
    }
  }
  function getNotationMacros() {
    if (_macros) return _macros;
    _macros = {};
    document.querySelectorAll("script.rsm-notation").forEach((s) => {
      try {
        for (const e of JSON.parse(s.textContent)) _macros[e.macro] = e.default;
      } catch {
      }
    });
    Object.assign(_macros, loadOverrides());
    return _macros;
  }
  function isValid(latex) {
    if (!latex || !latex.trim()) return false;
    if (!window.temml) return true;
    try {
      window.temml.renderToString(latex, { throwOnError: true });
      return true;
    } catch {
      return false;
    }
  }
  function reRenderAll(root2 = document) {
    if (!window.temml) return;
    const macros = getNotationMacros();
    root2.querySelectorAll("span.math[data-latex]").forEach((el) => {
      try {
        window.temml.render(el.dataset.latex, el, {
          throwOnError: false,
          macros: { ...macros }
        });
      } catch (err) {
        console.error("notation re-render (inline):", err);
      }
    });
    root2.querySelectorAll("div.mathblock[data-latex]").forEach((el) => {
      const target = el.querySelector(".hr-content-zone") || el;
      try {
        window.temml.render(el.dataset.latex, target, {
          displayMode: true,
          throwOnError: false,
          macros: { ...macros }
        });
      } catch (err) {
        console.error("notation re-render (display):", err);
      }
    });
  }
  function setMacro(macro, latex) {
    if (!isValid(latex)) return false;
    getNotationMacros()[macro] = latex;
    saveOverride(macro, latex);
    reRenderAll();
    return true;
  }
  function resetMacro(macro) {
    const entry = listNotation().find((e) => e.macro === macro);
    const overrides = loadOverrides();
    delete overrides[macro];
    try {
      localStorage.setItem(storageKey(), JSON.stringify(overrides));
    } catch {
    }
    if (entry) {
      getNotationMacros()[macro] = entry.default;
      reRenderAll();
    }
  }
  function listNotation() {
    const macros = getNotationMacros();
    const out = [];
    const seen = /* @__PURE__ */ new Set();
    document.querySelectorAll("script.rsm-notation").forEach((s) => {
      try {
        for (const e of JSON.parse(s.textContent)) {
          if (seen.has(e.macro)) continue;
          seen.add(e.macro);
          out.push({
            macro: e.macro,
            label: e.label || e.macro,
            default: e.default,
            current: macros[e.macro] ?? e.default
          });
        }
      } catch {
      }
    });
    return out;
  }
  var _LOCATE_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0"/><path d="M12 12m-5 0a5 5 0 1 0 10 0a5 5 0 1 0 -10 0"/><path d="M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/></svg>';
  function usesOf(macro, root2 = document) {
    const re = new RegExp(macro.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "(?![a-zA-Z])");
    return [
      ...root2.querySelectorAll("span.math[data-latex], div.mathblock[data-latex]")
    ].filter((el) => re.test(el.dataset.latex));
  }
  function flash(el) {
    el.classList.add("notation-located");
    setTimeout(() => el.classList.remove("notation-located"), 1800);
  }
  function nearestOf(els) {
    const center = window.innerHeight / 2;
    let best = null;
    let bestDist = Infinity;
    for (const el of els) {
      const r = el.getBoundingClientRect();
      const dist = Math.abs(r.top + r.height / 2 - center);
      if (dist < bestDist) {
        bestDist = dist;
        best = el;
      }
    }
    return best;
  }
  function jumpTo(el) {
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    flash(el);
  }
  function mountNotationPanel(root2 = document) {
    const panel = root2.querySelector(".rail-notation");
    if (!panel) return;
    const entries = listNotation();
    panel.innerHTML = "";
    if (!entries.length) {
      const empty = document.createElement("div");
      empty.className = "rail-notation-empty";
      empty.textContent = "This paper declares no rebindable notation.";
      panel.appendChild(empty);
      return;
    }
    for (const e of entries) {
      let renderPreview = function(latex) {
        if (!window.temml) {
          preview.textContent = "";
          return;
        }
        try {
          preview.innerHTML = window.temml.renderToString(latex, { throwOnError: true });
          input.classList.remove("invalid");
        } catch {
          input.classList.add("invalid");
        }
      }, commit = function() {
        if (input.value === lastApplied) return;
        const ok = setMacro(e.macro, input.value);
        input.classList.toggle("invalid", !ok);
        if (ok) {
          lastApplied = input.value;
          const uses = usesOf(e.macro, root2);
          uses.forEach(flash);
          const nearest = nearestOf(uses);
          if (nearest) nearest.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      };
      const row = document.createElement("div");
      row.className = "rail-notation-row";
      const label = document.createElement("div");
      label.className = "rail-notation-label";
      label.textContent = e.label;
      const edit = document.createElement("div");
      edit.className = "rail-notation-edit";
      const input = document.createElement("input");
      input.type = "text";
      input.className = "rail-notation-input";
      input.value = e.current;
      input.spellcheck = false;
      input.setAttribute("aria-label", `LaTeX for ${e.label}`);
      const preview = document.createElement("span");
      preview.className = "rail-notation-preview";
      const apply = document.createElement("button");
      apply.type = "button";
      apply.className = "rail-notation-apply";
      apply.textContent = "Apply";
      apply.setAttribute("data-tooltip", "Apply this symbol throughout the paper");
      const locate = document.createElement("button");
      locate.type = "button";
      locate.className = "rail-notation-locate";
      locate.setAttribute("aria-label", "Scroll to the nearest occurrence of this symbol");
      locate.setAttribute("data-tooltip", "Scroll to the nearest occurrence of this symbol");
      locate.innerHTML = _LOCATE_ICON;
      const reset = document.createElement("button");
      reset.type = "button";
      reset.className = "rail-notation-reset";
      reset.setAttribute("aria-label", "Reset to the author's default");
      reset.setAttribute("data-tooltip", "Reset to the author's default");
      reset.textContent = "\u21BA";
      renderPreview(input.value);
      let lastApplied = e.current;
      input.addEventListener("input", () => renderPreview(input.value));
      input.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") {
          ev.preventDefault();
          commit();
        }
      });
      input.addEventListener("blur", commit);
      for (const btn of [apply, locate, reset]) {
        btn.addEventListener("mousedown", (ev) => ev.preventDefault());
      }
      apply.addEventListener("click", commit);
      locate.addEventListener("click", () => {
        const el = nearestOf(usesOf(e.macro, root2));
        if (el) jumpTo(el);
      });
      reset.addEventListener("click", () => {
        resetMacro(e.macro);
        input.value = e.default;
        lastApplied = e.default;
        renderPreview(input.value);
        usesOf(e.macro, root2).forEach(flash);
      });
      const actions = document.createElement("div");
      actions.className = "rail-notation-actions";
      actions.append(apply, locate, reset);
      edit.append(input, preview);
      row.append(label, edit, actions);
      panel.appendChild(row);
    }
  }

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
    const notationMacros = {};
    for (const [name, value] of Object.entries(getNotationMacros())) {
      notationMacros[name.replace(/^\\/, "")] = value;
    }
    const config = document.createElement("script");
    config.innerHTML = `window.MathJax = {
      startup: {
        typeset: false
      },
      tex: {
        macros: ${JSON.stringify(notationMacros)},
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
    const hasMath = element.querySelector("span.math, div.mathblock");
    if (!hasMath) return;
    if (!window.temml && !window.MathJax?.typesetPromise) {
      try {
        await loadTemml();
      } catch {
        try {
          await loadMathJax();
        } catch {
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
          temml.render(latex, el, { throwOnError: false, macros: { ...getNotationMacros() } });
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
          temml.render(latex, contentEl, { displayMode: true, throwOnError: false, macros: { ...getNotationMacros() } });
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

  // rsm/static/tocarcs.js
  function wireTree(svg) {
    const nodes = [...svg.querySelectorAll(".toc-node")];
    const edges = [...svg.querySelectorAll(".toc-edge")];
    const hover = svg.querySelector(".toc-hover-label");
    if (!nodes.length) return;
    const hRect = hover && hover.querySelector("rect");
    const hText = hover && hover.querySelector("text");
    const prereq = /* @__PURE__ */ new Map();
    for (const e of edges) {
      if (e.classList.contains("fwd")) continue;
      const f = e.dataset.from;
      if (!prereq.has(f)) prereq.set(f, []);
      prereq.get(f).push(e.dataset.to);
    }
    function closure(idx) {
      const seen = /* @__PURE__ */ new Set([idx]);
      const stack = [idx];
      while (stack.length) {
        for (const to of prereq.get(stack.pop()) || []) {
          if (!seen.has(to)) {
            seen.add(to);
            stack.push(to);
          }
        }
      }
      return seen;
    }
    function showLabel(node) {
      if (!hover || !hText) return;
      hText.textContent = node.getAttribute("data-title") || "";
      const rect = node.querySelector("rect");
      const nx = parseFloat(rect.getAttribute("x"));
      const ny = parseFloat(rect.getAttribute("y"));
      const nw = parseFloat(rect.getAttribute("width"));
      const box = hText.getBBox();
      const padX = 9;
      const w = box.width + 2 * padX;
      const h = box.height + 10;
      let lx = nx + nw / 2 - w / 2;
      let ly = ny - h - 8;
      if (ly < -10) ly = ny + parseFloat(rect.getAttribute("height")) + 8;
      hRect.setAttribute("x", lx);
      hRect.setAttribute("y", ly);
      hRect.setAttribute("width", w);
      hRect.setAttribute("height", h);
      hText.setAttribute("x", lx + padX);
      hText.setAttribute("y", ly + h / 2);
      hText.setAttribute("dominant-baseline", "central");
      hover.style.display = "";
      svg.appendChild(hover);
    }
    function applyCone(idx) {
      if (idx == null) {
        for (const x of svg.querySelectorAll(".toc-faded")) x.classList.remove("toc-faded");
        return;
      }
      const cone = closure(idx);
      for (const e of edges) {
        const on = !e.classList.contains("fwd") && cone.has(e.dataset.from) && cone.has(e.dataset.to);
        e.classList.toggle("toc-faded", !on);
      }
      for (const n of nodes) {
        n.classList.toggle("toc-faded", !cone.has(n.getAttribute("data-idx")));
      }
    }
    svg.__applyCone = applyCone;
    nodes.forEach((node) => {
      const idx = node.getAttribute("data-idx");
      node.addEventListener("mouseenter", () => {
        applyCone(idx);
        showLabel(node);
      });
      node.addEventListener("mouseleave", () => {
        applyCone(svg.__pinnedIdx != null ? svg.__pinnedIdx : null);
        if (hover) hover.style.display = "none";
      });
    });
    if (svg.__pinnedIdx != null) applyCone(svg.__pinnedIdx);
  }
  function pinTreeCurrent(svg, idx) {
    svg.__pinnedIdx = idx;
    if (svg.__applyCone) svg.__applyCone(idx);
  }
  function drawAll(root2 = document) {
    root2.querySelectorAll(".toc.tree svg.toc-tree").forEach((svg) => {
      if (svg.dataset.wired) return;
      svg.dataset.wired = "1";
      wireTree(svg);
    });
  }
  function setup(root2 = document) {
    drawAll(root2);
  }

  // rsm/static/handrails.js
  var singletonMenu = null;
  var activeHr = null;
  var IS_TOUCH = typeof window !== "undefined" && typeof window.matchMedia === "function" && window.matchMedia("(hover: none) and (pointer: coarse)").matches;
  var delegationAttached = false;
  function setup2() {
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
        else if (role === "collapse") {
          toggleHandrail(activeHr);
          refreshCollapseLabels(activeHr);
        } else if (role === "collapse-all") {
          const withinSubproof = activeHr.classList.contains("step");
          collapseAll(activeHr, withinSubproof);
          refreshCollapseLabels(activeHr);
        } else if (role === "static-toggle") toggleStaticView(activeHr, menuItem);
        else if (role === "toc-view") toggleTocView(activeHr, menuItem);
        else if (role === "reorder") toggleReorder(activeHr);
        else if (role === "focus") triggerFocus(activeHr);
        return;
      }
      const collapseBtn = ev.target.closest(".hr-collapse");
      if (collapseBtn && collapseBtn.closest(".hr-collapse-zone")) {
        toggleHandrail(ev.target);
        return;
      }
    });
    document.addEventListener("mousedown", function(ev) {
      if (!ev.target.closest) return;
      if (ev.target.closest(".hr-collapse-zone") || ev.target.closest(".hr-border-zone") || ev.target.closest("#hr-menu-singleton")) {
        ev.preventDefault();
      }
    });
    document.addEventListener("mouseout", function(ev) {
      const menu = ev.target.closest && ev.target.closest("#hr-menu-singleton .hr-menu");
      if (!menu) return;
      if (ev.relatedTarget && menu.contains(ev.relatedTarget)) return;
      hideMenu();
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
    hr.classList.add("hr-menu-open");
    const label = hr.getAttribute("data-menu-label") || "";
    let collapse = hr.getAttribute("data-menu-collapse");
    const collapseAll2 = hr.getAttribute("data-menu-collapse-all");
    if (IS_TOUCH && (!collapse || collapse === "disabled") && hr.querySelector(":scope > .hr-collapse-zone .hr-collapse")) {
      collapse = "enabled";
      hr.setAttribute("data-menu-collapse", collapse);
    }
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
    refreshCollapseLabels(hr);
    const collapseSep = singletonMenu.querySelector('[data-role="collapse-sep"]');
    if (collapseSep) {
      const anyCollapse = collapse || collapseAll2;
      collapseSep.style.display = anyCollapse ? "" : "none";
    }
    configureItem(singletonMenu.querySelector('[data-role="link"]'), link);
    configureItem(singletonMenu.querySelector('[data-role="code"]'), code);
    const staticToggle = hr.getAttribute("data-menu-static-toggle");
    const staticToggleEl = singletonMenu.querySelector('[data-role="static-toggle"]');
    const staticSep = singletonMenu.querySelector('[data-role="static-sep"]');
    configureItem(staticToggleEl, staticToggle);
    if (staticSep) staticSep.style.display = staticToggle ? "" : "none";
    if (staticToggleEl && staticToggle && staticToggle !== "disabled") {
      const figure = hr.closest("figure") || hr.closest("figcaption")?.parentElement;
      const isShowingStatic = figure && figure.classList.contains("showing-static");
      const textEl = staticToggleEl.querySelector(".hr-menu-item-text");
      if (textEl) textEl.textContent = isShowingStatic ? "Interactive" : "Static";
      const useEl = staticToggleEl.querySelector("svg use");
      if (useEl) useEl.setAttribute("href", isShowingStatic ? "#hr-icon-play" : "#hr-icon-image");
    }
    const tocView = hr.getAttribute("data-menu-toc-view");
    const tocViewEl = singletonMenu.querySelector('[data-role="toc-view"]');
    const tocViewSep = singletonMenu.querySelector('[data-role="toc-view-sep"]');
    configureItem(tocViewEl, tocView);
    if (tocViewSep) tocViewSep.style.display = tocView ? "" : "none";
    if (tocViewEl && tocView && tocView !== "disabled") {
      const toc = hr.closest(".toc");
      const isTree = toc && toc.classList.contains("tree");
      const textEl = tocViewEl.querySelector(".hr-menu-item-text");
      if (textEl) textEl.textContent = isTree ? "View as list" : "View as tree";
    }
    const isProof = hr.classList.contains("proof");
    const touch = window.matchMedia("(hover: none) and (pointer: coarse)").matches;
    const reorder = isProof ? touch ? "disabled" : "true" : null;
    const reorderEl = singletonMenu.querySelector('[data-role="reorder"]');
    const reorderSep = singletonMenu.querySelector('[data-role="reorder-sep"]');
    configureItem(reorderEl, reorder);
    if (reorderSep) reorderSep.style.display = reorder ? "" : "none";
    if (reorderEl && reorder) {
      const textEl = reorderEl.querySelector(".hr-menu-item-text");
      if (touch) {
        reorderEl.setAttribute("aria-disabled", "true");
        reorderEl.removeAttribute("aria-pressed");
        if (textEl) textEl.textContent = "Reorder steps (desktop only)";
      } else {
        const on = hr.classList.contains("reorder-active");
        reorderEl.removeAttribute("aria-disabled");
        reorderEl.setAttribute("aria-pressed", on ? "true" : "false");
        if (textEl) textEl.textContent = on ? "Done reordering" : "Reorder steps";
      }
    }
    const isStep = hr.classList.contains("step") && !hr.closest(".calc");
    const hasRail = !!document.querySelector(".proof-rail");
    const focus = isStep && hasRail ? "true" : null;
    const focusEl = singletonMenu.querySelector('[data-role="focus"]');
    const focusSep = singletonMenu.querySelector('[data-role="focus-sep"]');
    configureItem(focusEl, focus);
    if (focusSep) focusSep.style.display = focus ? "" : "none";
    const zone = hr.querySelector(":scope > .hr-menu-zone");
    if (zone) {
      zone.appendChild(singletonMenu);
      singletonMenu.style.display = "";
      zone.style.display = "block";
      portalMenuToBody();
    }
  }
  function toggleReorder(hr) {
    const active = hr.classList.toggle("reorder-active");
    hideMenu();
    hr.dispatchEvent(
      new CustomEvent("reorder:toggle", { bubbles: true, detail: { active } })
    );
  }
  function triggerFocus(hr) {
    hideMenu();
    hr.dispatchEvent(new CustomEvent("focus:step", { bubbles: true }));
  }
  function menuPopup() {
    return singletonMenu && singletonMenu.querySelector(".hr-menu");
  }
  function portalMenuToBody() {
    const popup = menuPopup();
    if (!popup) return;
    const rect = popup.getBoundingClientRect();
    document.body.appendChild(singletonMenu);
    singletonMenu.classList.add("hr-menu-portaled");
    popup.style.position = "absolute";
    popup.style.left = `${rect.left + window.scrollX}px`;
    popup.style.top = `${rect.top + window.scrollY}px`;
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
  function syncCollapseLabel(item, collapsed, opts) {
    if (!item) return;
    const [text, iconClass, href] = collapsed ? opts.expand : opts.collapse;
    const textEl = item.querySelector(".hr-menu-item-text");
    if (textEl) textEl.textContent = text;
    const icon = item.querySelector(".icon");
    if (icon) {
      icon.classList.remove(opts.collapse[1], opts.expand[1]);
      icon.classList.add(iconClass);
    }
    const use = item.querySelector("svg use");
    if (use) use.setAttribute("href", href);
  }
  function refreshCollapseLabels(hr) {
    if (!singletonMenu || !hr) return;
    const collapse = hr.getAttribute("data-menu-collapse");
    if (collapse && collapse !== "disabled") {
      syncCollapseLabel(
        singletonMenu.querySelector('[data-role="collapse"]'),
        hr.classList.contains("hr-collapsed"),
        {
          collapse: ["Collapse", "collapse", "#hr-icon-collapse"],
          expand: ["Expand", "expand", "#hr-icon-expand"]
        }
      );
    }
    const collapseAll2 = hr.getAttribute("data-menu-collapse-all");
    if (collapseAll2 && collapseAll2 !== "disabled") {
      syncCollapseLabel(
        singletonMenu.querySelector('[data-role="collapse-all"]'),
        allSubstepsCollapsed(hr),
        {
          collapse: ["Collapse all", "collapse-all", "#hr-icon-collapse-all"],
          expand: ["Expand all", "expand-all", "#hr-icon-expand-all"]
        }
      );
    }
  }
  function allSubstepsCollapsed(hr) {
    const withinSubproof = hr.classList.contains("step");
    const qry = withinSubproof ? ":scope > .hr-content-zone > .subproof > .hr-content-zone > .step:has(.subproof)" : ":scope > .hr-content-zone > .step:has(.subproof)";
    const steps = hr.querySelectorAll(qry);
    if (steps.length === 0) return false;
    return Array.from(steps).every((s) => s.classList.contains("hr-collapsed"));
  }
  function hideMenu() {
    if (!singletonMenu) return;
    singletonMenu.style.display = "none";
    singletonMenu.classList.remove("hr-menu-portaled");
    const popup = menuPopup();
    if (popup) {
      popup.style.position = "";
      popup.style.left = "";
      popup.style.top = "";
    }
    singletonMenu.querySelectorAll(".hr-menu-item").forEach((it) => it.classList.remove("active"));
    if (activeHr) {
      activeHr.classList.remove("hr-menu-open");
      const zone = activeHr.querySelector(":scope > .hr-menu-zone");
      if (zone) zone.style.display = "";
    }
    const home = document.querySelector(".manuscriptwrapper");
    if (home && singletonMenu.parentElement !== home) home.appendChild(singletonMenu);
    activeHr = null;
  }
  function toggleMenuFor(hr) {
    if (!hr || !hr.classList || !hr.classList.contains("hr")) return;
    if (activeHr === hr) {
      hideMenu();
    } else {
      singletonMenu = document.getElementById("hr-menu-singleton");
      showMenuFor(hr);
    }
  }
  function closeMenu() {
    if (activeHr) hideMenu();
  }
  function menuOpenOn(hr) {
    return !!hr && activeHr === hr;
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
    notifyHandrailToggle(hr, false);
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
    notifyHandrailToggle(hr, true);
    const icon = hr.querySelector(":scope > .hr-collapse-zone .icon.collapse");
    if (!icon) return;
    icon.classList.remove("collapse");
    icon.classList.add("expand");
    const use = icon.querySelector("use");
    if (use) use.setAttribute("href", "#hr-icon-expand");
  }
  var COLLAPSE_KEY = "rsm-collapse:" + location.pathname;
  var suppressPersist = false;
  function loadCollapseState() {
    try {
      return JSON.parse(localStorage.getItem(COLLAPSE_KEY)) || {};
    } catch {
      return {};
    }
  }
  function collapseKey(hr) {
    const nid = hr.getAttribute("data-nodeid");
    if (nid != null) return "n:" + nid;
    const sec = hr.closest("section");
    if (sec && sec.id) return "s:" + sec.id;
    if (hr.id) return "e:" + hr.id;
    const txt = (hr.textContent || "").replace(/\s+/g, " ").trim();
    return txt ? "t:" + txt : null;
  }
  function persistCollapse(hr, collapsed) {
    const key = collapseKey(hr);
    if (key == null) return;
    try {
      const state = loadCollapseState();
      state[key] = collapsed;
      localStorage.setItem(COLLAPSE_KEY, JSON.stringify(state));
    } catch {
    }
  }
  function notifyHandrailToggle(hr, collapsed) {
    if (!suppressPersist) persistCollapse(hr, collapsed);
    document.dispatchEvent(
      new CustomEvent("rsm:handrail-toggle", { detail: { hr, collapsed } })
    );
  }
  function collapseInitial(root2) {
    suppressPersist = true;
    (root2 || document).querySelectorAll(".hr[data-start-collapsed]").forEach((hr) => closeHandrail(hr));
    suppressPersist = false;
  }
  function restoreCollapse(root2) {
    const state = loadCollapseState();
    suppressPersist = true;
    for (const hr of (root2 || document).querySelectorAll(".hr")) {
      if (hr.closest(".rsm-source")) continue;
      const key = collapseKey(hr);
      if (key == null || !(key in state)) continue;
      const wantCollapsed = state[key];
      const isCollapsed = hr.classList.contains("hr-collapsed");
      if (wantCollapsed && !isCollapsed) closeHandrail(hr);
      else if (!wantCollapsed && isCollapsed) openHandrail(hr);
    }
    suppressPersist = false;
  }
  function withoutPersist(fn) {
    const prev = suppressPersist;
    suppressPersist = true;
    try {
      fn();
    } finally {
      suppressPersist = prev;
    }
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
    const qry = withinSubproof ? ":scope > .hr-content-zone > .subproof > .hr-content-zone > .step:has(.subproof)" : ":scope > .hr-content-zone > .step:has(.subproof)";
    const hr = target.closest ? target.closest(".hr") : target;
    const steps = Array.from(hr.querySelectorAll(qry));
    if (!steps.length) return;
    const allCollapsed = steps.every((s) => s.classList.contains("hr-collapsed"));
    steps.forEach((s) => allCollapsed ? openHandrail(s) : closeHandrail(s));
    refreshCollapseLabels(hr);
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
      window.focus();
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
        window.focus();
        await navigator.clipboard.writeText(source);
        launchToast("Source copied to clipboard.", "success");
      } catch (error) {
        launchToast("Could not copy source.", "error");
      }
    });
  }
  function toggleTocView(hr, menuItem) {
    const toc = hr.closest(".toc");
    if (!toc) return;
    const isTree = toc.classList.toggle("tree");
    if (isTree) (void 0)(toc);
    if (menuItem) {
      const textEl = menuItem.querySelector(".hr-menu-item-text");
      if (textEl) textEl.textContent = isTree ? "View as list" : "View as tree";
    }
  }
  function toggleStaticView(hr, menuItem) {
    const figure = hr.closest("figure") || hr.closest("figcaption")?.parentElement;
    if (!figure) return;
    const fallback = figure.querySelector(".static-fallback");
    if (!fallback) return;
    const isShowingStatic = figure.classList.toggle("showing-static");
    const container = fallback.parentElement;
    for (const child of container.children) {
      if (child === fallback) continue;
      child.style.display = isShowingStatic ? "none" : "";
    }
    fallback.style.display = isShowingStatic ? "" : "none";
    const textEl = menuItem.querySelector(".hr-menu-item-text");
    if (textEl) textEl.textContent = isShowingStatic ? "Interactive" : "Static";
    const useEl = menuItem.querySelector("svg use");
    if (useEl) useEl.setAttribute("href", isShowingStatic ? "#hr-icon-play" : "#hr-icon-image");
  }

  // rsm/static/keyboard.js
  function setup3(root2) {
    function ignore(event) {
      if (event.metaKey || event.ctrlKey || event.altKey) return true;
      const t = event.target;
      if (!t) return false;
      if (t.isContentEditable) return true;
      return t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT";
    }
    root2.addEventListener("keydown", (event) => {
      if (ignore(event)) return;
      if (["j", "k"].includes(event.key)) {
        event.preventDefault();
        event.stopPropagation();
        focusPrevOrNext(event.key == "j" ? "next" : "prev", root2);
      }
    });
    root2.addEventListener("keydown", (event) => {
      if (ignore(event)) return;
      if (["h", "l"].includes(event.key)) {
        event.preventDefault();
        event.stopPropagation();
        focusUpOrDown(event.key == "h" ? "down" : "up", root2);
      }
    });
    root2.addEventListener("keydown", (event) => {
      if (ignore(event)) return;
      if (event.key == "H") {
        event.stopPropagation();
        focusTop(root2);
      }
      ;
    });
    root2.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeMenu();
    });
    root2.addEventListener("keydown", (event) => {
      if (ignore(event)) return;
      if (event.key == ".") {
        event.stopPropagation();
        toggleMenuFor(document.activeElement);
      }
      ;
    });
    root2.addEventListener("keydown", (event) => {
      if (ignore(event)) return;
      if (event.key == ",") {
        event.stopPropagation();
        toggleCollapse(document.activeElement);
      }
      ;
    });
    root2.addEventListener("keydown", (event) => {
      if (ignore(event)) return;
      if (event.key == ";") {
        event.stopPropagation();
        toggleCollapseAll(document.activeElement);
      }
      ;
    });
    root2.addEventListener("keydown", (event) => {
      if (ignore(event)) return;
      if (event.key == "z") {
        event.stopPropagation();
        scrollToMiddle(document.activeElement);
      }
      ;
    });
    root2.addEventListener("keydown", (event) => {
      if (ignore(event)) return;
      if (!["ArrowUp", "ArrowDown"].includes(event.key)) return;
      if (!menuOpenOn(document.activeElement)) return;
      event.preventDefault();
      event.stopPropagation();
      menuUpOrDown(document.activeElement, event.key == "ArrowUp" ? "up" : "down");
    });
    root2.addEventListener("keyup", (event) => {
      if (ignore(event)) return;
      if (event.keyCode !== 13) return;
      if (!menuOpenOn(document.activeElement)) return;
      event.preventDefault();
      event.stopPropagation();
      executeActiveMenuItem(document.activeElement);
    });
    root2.addEventListener("keydown", (event) => {
      if (ignore(event)) return;
      if (event.key == "i") {
        event.stopPropagation();
        toggleTooltip(document.activeElement);
      }
    });
  }
  function focusTop(root2) {
    location.hash = "top";
    const top = (root2.querySelector(".manuscriptwrapper") || root2).querySelector(".hr[id]");
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
    const items = Array.from(menu.querySelectorAll(":scope > .hr-menu-item")).filter((it) => it.offsetParent !== null && !it.classList.contains("disabled"));
    if (!items.length) return;
    const current = items.find((it) => it.classList.contains("active"));
    let index = current ? items.indexOf(current) : -1;
    if (index === -1) {
      index = direction === "down" ? 0 : items.length - 1;
    } else {
      index = direction === "down" ? (index + 1) % items.length : (index - 1 + items.length) % items.length;
    }
    if (current) current.classList.remove("active");
    items[index].classList.add("active");
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
  var PIN_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 4.5l-4 4l-4 1.5l-1.5 1.5l7 7l1.5 -1.5l1.5 -4l4 -4"/><path d="M9 15l-4.5 4.5"/><path d="M14.5 4l5.5 5.5"/></svg>';
  function buildExcerpt(rawHref) {
    if (!rawHref) return { content: "", error: "no-href" };
    const target = rawHref.replaceAll(".", "\\.").replaceAll(":", "\\:");
    if (target === "#") return { content: "", error: "no-label" };
    const $t = $(target);
    if (!$t[0]) return { content: "", error: "unknown" };
    const tag = $t.prop("tagName");
    const classes = $t[0].classList;
    let content = "";
    let clone;
    if (["P", "LI", "FIGURE"].includes(tag)) {
      content = `<div>${$t.html()}</div>`;
    } else if (tag === "SPAN" && classes.contains("math")) {
      content = `<div>${$t.html()}</div>`;
    } else if (tag === "SPAN") {
      content = `<div>${$t.parent().html()}</div>`;
    } else if (tag === "DT") {
      content = $t.next().html() || "";
    } else if (tag === "TABLE") {
      content = $t[0].outerHTML;
    } else if (tag === "SECTION") {
      clone = $t.clone();
      clone.children().slice(2).remove();
      stripHandrail(clone);
      clone.css("font-size", "0.7rem");
      content = clone.html();
    } else if (tag === "A") {
      content = `<div>${$t.parent().html()}</div>`;
    } else if (tag === "DIV") {
      if (classes.contains("step")) {
        clone = $t.find(".statement").clone();
        stripHandrail(clone);
        clone.css("font-size", "0.7rem");
        content = clone.html();
      } else if (["math", "algorithm"].some((c) => classes.contains(c))) {
        clone = $t.clone();
        stripHandrail(clone);
        content = clone.html();
      } else if ([
        "paragraph",
        "mathblock",
        "theorem",
        "lemma",
        "corollary",
        "example",
        "exercise",
        "proposition",
        "problem",
        "porism",
        "remark",
        "definition",
        "bibitem"
      ].some((c) => classes.contains(c))) {
        clone = $t.clone();
        stripHandrail(clone);
        content = clone.html();
      }
    }
    return { content: content || "", error: content ? null : "unsupported" };
  }
  function pinBar(href, title) {
    const h = (href || "").replaceAll('"', "&quot;");
    const t = (title || "").replaceAll('"', "&quot;");
    return `<div class="ref-pin-bar"><button type="button" class="ref-pin" data-pin-target="${h}" data-pin-title="${t}" aria-label="Pin this beside the proof">` + PIN_ICON + "<span>Pin</span></button></div>";
  }
  var pinDelegated = false;
  function setupPinDelegation() {
    if (pinDelegated) return;
    pinDelegated = true;
    document.addEventListener("click", (ev) => {
      const btn = ev.target.closest && ev.target.closest(".ref-pin");
      if (!btn) return;
      const { content } = buildExcerpt(btn.dataset.pinTarget);
      if (!content) return;
      const tmp = document.createElement("div");
      tmp.innerHTML = content;
      tmp.querySelectorAll("[id]").forEach((e) => e.removeAttribute("id"));
      tmp.querySelectorAll("[data-nodeid]").forEach((e) => e.removeAttribute("data-nodeid"));
      btn.dispatchEvent(
        new CustomEvent("rail:pin", {
          bubbles: true,
          detail: { html: tmp.innerHTML, title: btn.dataset.pinTitle || "" }
        })
      );
    });
  }
  function createTooltips() {
    setupPinDelegation();
    $(".manuscriptwrapper a.reference:not(.external):not(.tooltipstered)").tooltipster({
      theme: ["tooltipster-shadow", "tooltipster-shadow-rsm"],
      delay: 200,
      minWidth: 100,
      maxWidth: 500,
      // Interactive so the reader can move into the preview to click its pin
      // button without it closing on the way.
      interactive: true,
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
        const rawHref = $(helper.origin).attr("href");
        const { content, error } = buildExcerpt(rawHref);
        if (error === "no-href") {
          console.warn("Target does not have an href attribute");
          return;
        }
        if (error === "no-label") {
          setTooltipContent(
            instance,
            '<span class="error">target node has no label</span>'
          );
          helper.origin.classList.add("error");
          return;
        }
        if (error === "unknown") return;
        if (!content) {
          setTooltipContent(instance, "");
          return;
        }
        const title = (helper.origin.textContent || "").trim();
        setTooltipContent(instance, pinBar(rawHref, title) + content);
      },
      functionReady: function(instance, helper) {
        const el = instance.elementTooltip ? instance.elementTooltip() : helper.tooltip;
        if (el) typesetMath(el instanceof $ ? el[0] : el);
      }
    });
    $(".manuscriptwrapper .author-names sup[data-tooltip]:not(.tooltipstered)").tooltipster({
      theme: ["tooltipster-shadow", "tooltipster-shadow-rsm"],
      delay: 200,
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
    $(".proof-rail [data-tooltip]:not(.tooltipstered)").tooltipster({
      theme: ["tooltipster-shadow", "tooltipster-shadow-rsm"],
      // Rail controls are glanced past constantly; a longer hover-intent delay
      // keeps their hints from flashing up while the pointer just crosses the rail.
      delay: 500,
      // Cap the width: setTooltipContent wraps the label in .manuscriptwrapper,
      // which is width:100% up to the document column width, so without a maxWidth
      // a control hint stretches into a full-page banner (the body/author tooltips
      // both cap at 500; these are short labels, so a touch tighter).
      minWidth: 100,
      maxWidth: 360,
      side: "bottom",
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
        instance.content($(`<div class="rail-tip">${$(helper.origin).attr("data-tooltip")}</div>`));
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
    const $content = $(`<div class="manuscriptwrapper">${content}</div>`);
    $content.find("[id]").removeAttr("id");
    $content.find("[data-nodeid]").removeAttr("data-nodeid");
    tt.content($content);
  }

  // rsm/static/prooftree.js
  function setup4(root2 = document) {
    const rail = root2.querySelector(".proof-rail");
    if (!rail) return;
    const lsKey = "rsm-sidebar:" + location.pathname;
    rail.querySelectorAll("svg.toc-tree").forEach((svg) => {
      if (!svg.dataset.wired) {
        svg.dataset.wired = "1";
        wireTree(svg);
      }
    });
    const items = /* @__PURE__ */ new Map();
    for (const item of rail.querySelectorAll(".rail-proof .proof-rail-item")) {
      items.set(item.dataset.proof, item);
    }
    const stateData = /* @__PURE__ */ new Map();
    for (const [key, item] of items) {
      const sd = item.querySelector(".rail-state-data");
      if (sd) {
        try {
          stateData.set(key, JSON.parse(sd.textContent));
        } catch (e) {
        }
      }
    }
    let proofView = rail.classList.contains("proof-view-state") ? "state" : "map";
    let current;
    let currentNode = null;
    const active = { idx: -1 };
    rail.classList.add("active");
    function railClassFor(tab) {
      const inDoc = !!tab.closest(".rail-subtabs-document");
      const suffix = tab.dataset.view.replace(/^(doc|proof)-/, "");
      return (inDoc ? "doc-view-" : "proof-view-") + suffix;
    }
    function saveLayout() {
      const layout = {
        scope: rail.querySelector(".rail-scope.active")?.dataset.scope || "document",
        docView: rail.classList.contains("doc-view-notation") ? "notation" : "doc-map",
        proofView: rail.classList.contains("proof-view-state") ? "state" : "proof-map",
        collapsed: rail.classList.contains("collapsed")
      };
      try {
        localStorage.setItem(lsKey, JSON.stringify(layout));
      } catch (e) {
      }
    }
    function selectScope(scope) {
      for (const s of rail.querySelectorAll(".rail-scope")) {
        const on = s.dataset.scope === scope;
        s.classList.toggle("active", on);
        s.setAttribute("aria-pressed", String(on));
      }
      rail.classList.toggle("scope-document", scope === "document");
      rail.classList.toggle("scope-proof", scope === "proof");
      rail.classList.toggle("scope-reading", scope === "reading");
      rail.classList.toggle("scope-pinned", scope === "pinned");
    }
    function selectTab(tab) {
      const row = tab.closest(".rail-subtabs");
      for (const t of row.querySelectorAll(".rail-tab")) {
        t.classList.toggle("active", t === tab);
        t.setAttribute("aria-pressed", String(t === tab));
        rail.classList.remove(railClassFor(t));
      }
      rail.classList.add(railClassFor(tab));
      if (row.classList.contains("rail-subtabs-proof")) {
        proofView = tab.dataset.view === "state" ? "state" : "map";
        renderState();
      }
    }
    const scopeRow = rail.querySelector(".rail-scopes");
    if (scopeRow) {
      scopeRow.addEventListener("click", (ev) => {
        const s = ev.target.closest(".rail-scope");
        if (!s) return;
        selectScope(s.dataset.scope);
        saveLayout();
      });
    }
    for (const row of rail.querySelectorAll(".rail-subtabs")) {
      row.addEventListener("click", (ev) => {
        const t = ev.target.closest(".rail-tab");
        if (!t) return;
        selectTab(t);
        saveLayout();
      });
    }
    const collapseBtn = rail.querySelector(".rail-collapse");
    if (collapseBtn) {
      collapseBtn.addEventListener("click", () => {
        rail.classList.toggle("collapsed");
        saveLayout();
      });
    }
    const pinnedBody = rail.querySelector(".rail-pinned-body");
    const pinnedTitle = rail.querySelector(".rail-pinned-title");
    let prePinScope = null;
    document.addEventListener("rail:pin", (ev) => {
      if (!pinnedBody) return;
      if (!rail.classList.contains("has-pin")) {
        prePinScope = rail.querySelector(".rail-scope.active")?.dataset.scope || "document";
      }
      pinnedBody.innerHTML = ev.detail.html || "";
      if (pinnedTitle) pinnedTitle.textContent = ev.detail.title || "Pinned";
      typesetMath(pinnedBody);
      rail.classList.add("has-pin");
      selectScope("pinned");
    });
    const pinClose = rail.querySelector(".rail-pin-close");
    if (pinClose) {
      pinClose.addEventListener("click", () => {
        if (pinnedBody) pinnedBody.innerHTML = "";
        if (pinnedTitle) pinnedTitle.textContent = "";
        rail.classList.remove("has-pin");
        selectScope(prePinScope || "document");
        prePinScope = null;
      });
    }
    const READING_KEY = "rsm-reading";
    function readReadingPrefs() {
      try {
        return JSON.parse(localStorage.getItem(READING_KEY) || "{}") || {};
      } catch (e) {
        return {};
      }
    }
    function applyReading(control, value) {
      const el = document.documentElement;
      if (control === "theme") el.classList.toggle("dark-theme", value === "dark");
      else el.setAttribute("data-reading-" + control, value);
    }
    const readingPanel = rail.querySelector(".rail-reading");
    if (readingPanel) {
      readingPanel.addEventListener("click", (ev) => {
        const btn = ev.target.closest(".reading-opt");
        if (!btn) return;
        const row = btn.closest(".reading-row");
        const control = row.dataset.control;
        for (const o of row.querySelectorAll(".reading-opt")) {
          const on = o === btn;
          o.classList.toggle("active", on);
          o.setAttribute("aria-pressed", String(on));
        }
        applyReading(control, btn.dataset.value);
        const prefs2 = readReadingPrefs();
        prefs2[control] = btn.dataset.value;
        try {
          localStorage.setItem(READING_KEY, JSON.stringify(prefs2));
        } catch (e) {
        }
      });
      const prefs = readReadingPrefs();
      for (const row of readingPanel.querySelectorAll(".reading-row")) {
        const value = prefs[row.dataset.control];
        if (!value) continue;
        applyReading(row.dataset.control, value);
        for (const o of row.querySelectorAll(".reading-opt")) {
          const on = o.dataset.value === value;
          o.classList.toggle("active", on);
          o.setAttribute("aria-pressed", String(on));
        }
      }
    }
    try {
      const saved = JSON.parse(localStorage.getItem(lsKey) || "null");
      if (saved) {
        selectScope(saved.scope || "document");
        const docTab = rail.querySelector(
          `.rail-subtabs-document .rail-tab[data-view="${saved.docView}"]`
        );
        if (docTab) selectTab(docTab);
        const proofTab = rail.querySelector(
          `.rail-subtabs-proof .rail-tab[data-view="${saved.proofView}"]`
        );
        if (proofTab) selectTab(proofTab);
        rail.classList.toggle("collapsed", !!saved.collapsed);
      }
    } catch (e) {
    }
    let drawerGoalEl = null;
    if (window.matchMedia("(max-width: 1320px)").matches) {
      const handle = document.createElement("button");
      handle.type = "button";
      handle.className = "rail-handle";
      handle.setAttribute("aria-label", "Toggle the navigation drawer");
      const peek = document.createElement("div");
      peek.className = "rail-peek";
      peek.innerHTML = '<span class="rail-peek-label">Prove</span><span class="rail-peek-goal"></span>';
      rail.insertBefore(peek, rail.firstChild);
      rail.insertBefore(handle, rail.firstChild);
      drawerGoalEl = peek.querySelector(".rail-peek-goal");
      const DRAWER_KEY = "rsm-drawer:" + location.pathname;
      const setDrawer = (state, persist = true) => {
        rail.dataset.drawer = state;
        handle.setAttribute("aria-expanded", String(state === "open"));
        if (persist) {
          try {
            localStorage.setItem(DRAWER_KEY, state);
          } catch (e) {
          }
        }
      };
      let savedDrawer = null;
      try {
        savedDrawer = localStorage.getItem(DRAWER_KEY);
      } catch (e) {
      }
      setDrawer(["closed", "peek", "open"].includes(savedDrawer) ? savedDrawer : "peek", false);
      const ORDER = ["closed", "peek", "open"];
      let dragY = null;
      let dragged = false;
      handle.addEventListener("pointerdown", (ev) => {
        dragY = ev.clientY;
        dragged = false;
        try {
          handle.setPointerCapture(ev.pointerId);
        } catch (e) {
        }
      });
      handle.addEventListener("pointermove", (ev) => {
        if (dragY !== null && Math.abs(ev.clientY - dragY) > 8) dragged = true;
      });
      handle.addEventListener("pointerup", (ev) => {
        if (dragY === null) return;
        const dy = ev.clientY - dragY;
        const i = ORDER.indexOf(rail.dataset.drawer);
        if (!dragged) {
          setDrawer(rail.dataset.drawer === "peek" ? "open" : "peek");
        } else if (dy < 0) {
          setDrawer(ORDER[Math.min(i + 1, ORDER.length - 1)]);
        } else {
          setDrawer(ORDER[Math.max(i - 1, 0)]);
        }
        dragY = null;
        dragged = false;
      });
      document.addEventListener("rsm:focus-enter", () => setDrawer("peek"));
    }
    let peekGoalId;
    function updatePeekGoal() {
      if (!drawerGoalEl) return;
      let g = null;
      const data = current ? stateData.get(current) : null;
      if (data && active.idx >= 0 && active.idx < data.length) g = data[active.idx].goal;
      const gid = g && g.id != null ? String(g.id) : null;
      if (gid === peekGoalId) return;
      peekGoalId = gid;
      const el = gid != null ? root2.querySelector('[data-nodeid="' + gid + '"]') : null;
      if (!el) {
        rail.classList.add("drawer-no-goal");
        drawerGoalEl.textContent = "Open the navigation drawer";
        return;
      }
      rail.classList.remove("drawer-no-goal");
      const cz = el.querySelector(":scope > .hr-content-zone") || el;
      const clone = cloneClean(cz);
      clone.querySelectorAll(".hr-label, .construct.let, .construct.assume").forEach((n) => n.remove());
      drawerGoalEl.innerHTML = "";
      drawerGoalEl.appendChild(clone);
      const tw = document.createTreeWalker(drawerGoalEl, NodeFilter.SHOW_TEXT, {
        acceptNode: (n) => n.parentElement && n.parentElement.closest("math") ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT
      });
      let tn;
      while (tn = tw.nextNode()) {
        if (!tn.textContent.trim()) continue;
        tn.textContent = tn.textContent.replace(/^[\s,.;:⊢]*(?:then\b[\s,]*)?/i, "");
        break;
      }
      typesetMath(drawerGoalEl).then(() => reRenderAll(drawerGoalEl));
    }
    const proofs = [...root2.querySelectorAll(".proof[data-nodeid]")];
    function proofElFor(key) {
      return key ? root2.querySelector(`.proof[data-nodeid="${key}"]`) : null;
    }
    function updateCollapsedClass() {
      const el = proofElFor(current);
      rail.classList.toggle(
        "proof-collapsed",
        !!(el && el.classList.contains("hr-collapsed"))
      );
    }
    function show(key) {
      if (!items.has(key)) key = null;
      if (key === current) return;
      current = key;
      active.idx = -1;
      for (const [k, item] of items) item.classList.toggle("shown", k === key);
      rail.classList.toggle("no-proof", key === null);
      updateCollapsedClass();
      updateState();
    }
    show(null);
    function stepsOf(proofEl) {
      return [...proofEl.querySelectorAll(".step")].filter((s) => !s.closest(".calc"));
    }
    function selectFrom(target, clearOutside) {
      if (!target || !target.closest) return;
      if (target.closest(".proof-rail") || target.closest("#hr-menu-singleton")) return;
      let el = target.closest(".proof[data-nodeid]");
      while (el && !items.has(el.getAttribute("data-nodeid"))) {
        const p = el.parentElement;
        el = p ? p.closest(".proof[data-nodeid]") : null;
      }
      if (!el) {
        if (clearOutside) show(null);
        return;
      }
      show(el.getAttribute("data-nodeid"));
      const stepEl = target.closest(".step");
      if (stepEl && !stepEl.closest(".calc") && el.contains(stepEl)) {
        const idx = stepEl.dataset.stateIdx != null ? Number(stepEl.dataset.stateIdx) : stepsOf(el).indexOf(stepEl);
        if (idx >= 0) updateState(idx);
      }
    }
    if (proofs.length) {
      root2.addEventListener("click", (ev) => selectFrom(ev.target, false));
      root2.addEventListener("focusin", (ev) => selectFrom(ev.target, true));
    }
    document.addEventListener("rsm:handrail-toggle", (ev) => {
      const hr = ev.detail && ev.detail.hr;
      if (hr && hr.matches && hr.matches(".proof[data-nodeid]")) {
        updateCollapsedClass();
        updateState();
      }
    });
    rail.addEventListener("click", (ev) => {
      const btn = ev.target.closest(".rail-expand-proof");
      if (!btn) return;
      const el = proofElFor(btn.dataset.proof);
      if (!el) return;
      openHandrail(el);
      if (el.id) location.hash = el.id;
      else el.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    function setCurrentNode(node) {
      if (node === currentNode) return;
      if (currentNode) currentNode.classList.remove("current-step");
      currentNode = node;
      if (node) node.classList.add("current-step");
    }
    function setActiveIdx(idx) {
      if (idx === active.idx) return;
      active.idx = idx;
      renderState();
    }
    function updateState(idx) {
      if (rail.classList.contains("focusing")) {
        setCurrentNode(null);
        return;
      }
      if (!current) idx = -1;
      else if (idx == null || idx < 0) idx = active.idx >= 0 ? active.idx : 0;
      setActiveIdx(idx);
      const item = current ? items.get(current) : null;
      const node = item && idx >= 0 ? item.querySelector(`.toc-node[data-idx="${idx}"]`) : null;
      setCurrentNode(node);
      const dag = item ? item.querySelector("svg.toc-tree") : null;
      if (dag) pinTreeCurrent(dag, idx >= 0 ? String(idx) : null);
      updatePeekGoal();
    }
    function cloneClean(el) {
      const c = el.cloneNode(true);
      c.removeAttribute("id");
      c.removeAttribute("data-nodeid");
      c.querySelectorAll("[id],[data-nodeid]").forEach((n) => {
        n.removeAttribute("id");
        n.removeAttribute("data-nodeid");
      });
      c.classList.remove("tooltipstered");
      c.querySelectorAll(".tooltipstered").forEach(
        (n) => n.classList.remove("tooltipstered")
      );
      c.querySelectorAll(
        ".hr-collapse-zone,.hr-menu-zone,.hr-border-zone,.hr-spacer-zone,.hr-info-zone"
      ).forEach((n) => n.remove());
      c.querySelectorAll(".hr").forEach(
        (n) => n.classList.remove("hr", "hr-offset", "hr-labeled", "hr-hidden")
      );
      return c;
    }
    const collapseState = {};
    function renderState() {
      if (proofView !== "state") return;
      const item = current ? items.get(current) : null;
      if (!item) return;
      const panel = item.querySelector(".rail-state");
      if (!panel) return;
      panel.setAttribute("aria-live", "polite");
      const data = stateData.get(item.dataset.proof);
      if (!data || active.idx < 0 || active.idx >= data.length) {
        panel.innerHTML = '<div class="rail-state-empty">Click a proof to see its live hypotheses and current goal.</div>';
        return;
      }
      const st = data[active.idx];
      const proofKey = item.dataset.proof;
      panel.innerHTML = "";
      function makeBlock(role, label, defaultCollapsed) {
        const key = proofKey + ":" + role;
        const collapsed = key in collapseState ? collapseState[key] : defaultCollapsed;
        const block = document.createElement("div");
        block.className = "rail-state-block rail-" + role + (collapsed ? " collapsed" : "");
        block.setAttribute("role", "group");
        block.setAttribute("aria-label", label);
        const head = document.createElement("button");
        head.type = "button";
        head.className = "rail-state-head";
        head.setAttribute("aria-expanded", String(!collapsed));
        head.innerHTML = '<span class="rail-state-label">' + label + '</span><span class="rail-state-caret" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6l6 -6"/></svg></span>';
        const body = document.createElement("div");
        body.className = "rail-state-body";
        head.addEventListener("click", () => {
          const nowCollapsed = !block.classList.contains("collapsed");
          block.classList.toggle("collapsed", nowCollapsed);
          head.setAttribute("aria-expanded", String(!nowCollapsed));
          collapseState[key] = nowCollapsed;
        });
        block.appendChild(head);
        block.appendChild(body);
        return { block, body };
      }
      function numCell(num, kind) {
        const s = document.createElement("span");
        s.className = "rail-state-num";
        s.setAttribute("aria-hidden", "true");
        if (num) s.textContent = kind === "section" ? "(" + num + ")" : "\u27E8" + num + "\u27E9";
        return s;
      }
      function scrollToNode(targetId) {
        const t = root2.querySelector('[data-nodeid="' + targetId + '"]');
        if (t && t.id) location.hash = t.id;
        else if (t) t.scrollIntoView({ block: "center", behavior: "smooth" });
      }
      function makeJumpable(li, targetId, tip) {
        if (targetId == null) return;
        li.classList.add("rail-jump-row");
        li.addEventListener("click", (ev) => {
          if (ev.target.closest("a")) return;
          scrollToNode(targetId);
        });
        const host = li.querySelector(".keyword") || (li.querySelector("a") ? null : li);
        if (!host) return;
        host.classList.add("rail-jump-control");
        host.setAttribute("role", "button");
        host.setAttribute("tabindex", "0");
        host.setAttribute("aria-label", tip || "jump to source");
        if (tip) host.setAttribute("data-tooltip", tip);
        host.addEventListener("keydown", (ev) => {
          if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            scrollToNode(targetId);
          }
        });
      }
      const goalB = makeBlock("goal", "Prove", false);
      const g = st.goal;
      const goalEl = g && g.id != null ? root2.querySelector('[data-nodeid="' + g.id + '"]') : null;
      if (goalEl && g.thm) {
        const summary = document.createElement("div");
        summary.className = "rail-goal-summary rail-jump-row";
        summary.appendChild(numCell(g.num, g.marker));
        const preview = document.createElement("div");
        preview.className = "rail-goal-preview";
        const text = document.createElement("div");
        text.className = "rail-goal-text clamped";
        const cz = goalEl.querySelector(":scope > .hr-content-zone") || goalEl;
        const clone = cloneClean(cz);
        clone.querySelectorAll(".hr-label, .construct.let, .construct.assume").forEach((n) => n.remove());
        text.appendChild(clone);
        preview.appendChild(text);
        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "rail-goal-toggle";
        toggle.textContent = "show more";
        toggle.addEventListener("click", () => {
          const clamped = text.classList.toggle("clamped");
          toggle.textContent = clamped ? "show more" : "show less";
        });
        preview.appendChild(toggle);
        summary.appendChild(preview);
        goalB.body.appendChild(summary);
      } else if (goalEl) {
        const gbody = document.createElement("div");
        gbody.className = "rail-goal-body";
        gbody.appendChild(numCell(g.num, g.marker));
        gbody.appendChild(cloneClean(goalEl));
        makeJumpable(gbody, g.id, g.num ? "Go to step " + g.num : "Go to the goal");
        goalB.body.appendChild(gbody);
      } else {
        goalB.body.textContent = "the main result";
      }
      panel.appendChild(goalB.block);
      const hyps = (st.hyps || []).map((h) => ({
        el: root2.querySelector('[data-nodeid="' + h.id + '"]'),
        num: h.num,
        id: h.id,
        marker: h.marker
      })).filter((h) => h.el);
      const hypB = makeBlock("hyps", "Assume", false);
      const ul = document.createElement("ul");
      if (hyps.length) {
        for (const h of hyps) {
          const li = document.createElement("li");
          li.appendChild(numCell(h.num, h.marker));
          li.appendChild(cloneClean(h.el));
          const where = h.marker === "section" ? "section " : "step ";
          makeJumpable(li, h.id, h.num ? "Introduced in " + where + h.num : "Jump to source");
          ul.appendChild(li);
        }
      } else {
        const li = document.createElement("li");
        li.className = "rail-hyp-empty";
        li.textContent = "no assumptions yet";
        ul.appendChild(li);
      }
      hypB.body.appendChild(ul);
      panel.appendChild(hypB.block);
      const ctx = (st.context || []).map((c) => ({
        el: root2.querySelector('[data-nodeid="' + c.id + '"]'),
        id: c.id,
        num: c.num,
        marker: c.marker
      })).filter((c) => c.el);
      if (ctx.length) {
        const ctxB = makeBlock("context", "In scope", ctx.length > 4);
        const cul = document.createElement("ul");
        for (const c of ctx) {
          const li = document.createElement("li");
          li.appendChild(numCell(c.num, c.marker));
          li.appendChild(cloneClean(c.el));
          makeJumpable(
            li,
            c.id,
            c.num ? "Introduced in section " + c.num : "Jump to where this is introduced"
          );
          cul.appendChild(li);
        }
        ctxB.body.appendChild(cul);
        panel.appendChild(ctxB.block);
      }
      let maxNum = 0;
      panel.querySelectorAll(".rail-state-num").forEach((n) => {
        maxNum = Math.max(maxNum, n.scrollWidth);
      });
      if (maxNum > 0) panel.style.setProperty("--rail-num-width", maxNum + "px");
      typesetMath(panel).then(() => reRenderAll(panel));
      createTooltips();
    }
  }

  // rsm/static/focusmode.js
  function setup5(root2 = document) {
    const rail = root2.querySelector(".proof-rail");
    if (!rail) return;
    let active = null;
    function coneOf(svg, startIdx) {
      const prereq = /* @__PURE__ */ new Map();
      for (const e of svg.querySelectorAll(".toc-edge")) {
        if (e.classList.contains("fwd")) continue;
        const f = e.dataset.from;
        if (!prereq.has(f)) prereq.set(f, []);
        prereq.get(f).push(e.dataset.to);
      }
      const seen = /* @__PURE__ */ new Set([String(startIdx)]);
      const stack = [String(startIdx)];
      while (stack.length) {
        for (const to of prereq.get(stack.pop()) || []) {
          if (!seen.has(to)) {
            seen.add(to);
            stack.push(to);
          }
        }
      }
      return seen;
    }
    const stepsOf = (proofEl) => [...proofEl.querySelectorAll(".step")];
    function dimRail(svg, cone) {
      for (const n of svg.querySelectorAll(".toc-node")) {
        const lit = cone.has(n.dataset.idx);
        n.classList.toggle("focus-lit", lit);
        n.classList.toggle("focus-faded", !lit);
      }
      for (const e of svg.querySelectorAll(".toc-edge")) {
        const lit = !e.classList.contains("fwd") && cone.has(e.dataset.from) && cone.has(e.dataset.to);
        e.classList.toggle("focus-lit", lit);
        e.classList.toggle("focus-faded", !lit);
      }
    }
    const undimRail = (svg) => svg.querySelectorAll(".focus-faded, .focus-lit").forEach((x) => x.classList.remove("focus-faded", "focus-lit"));
    function stepNumber(st) {
      const el = st && st.querySelector(":scope > .hr-info-zone .step-number");
      return el ? el.textContent.trim() : "";
    }
    let liveRegion2 = null;
    function announce2(msg) {
      if (!liveRegion2) {
        liveRegion2 = document.createElement("div");
        liveRegion2.className = "focus-sr-status";
        liveRegion2.setAttribute("role", "status");
        liveRegion2.setAttribute("aria-live", "polite");
        document.body.appendChild(liveRegion2);
      }
      liveRegion2.textContent = "";
      requestAnimationFrame(() => {
        liveRegion2.textContent = msg;
      });
    }
    function showProofMap() {
      const scopeBtn = rail.querySelector('.rail-scope[data-scope="proof"]');
      if (scopeBtn) scopeBtn.click();
      const mapTab = rail.querySelector(
        '.rail-subtabs-proof .rail-tab[data-view="proof-map"]'
      );
      if (mapTab && !mapTab.classList.contains("active")) mapTab.click();
    }
    function onKeydown(ev) {
      if (ev.key === "Escape") exitFocus();
    }
    let exitBar = null;
    function setExitBar(sel) {
      const num = stepNumber(sel);
      if (!exitBar) {
        exitBar = document.createElement("div");
        exitBar.className = "proof-focus-exit";
        exitBar.setAttribute("role", "button");
        exitBar.tabIndex = 0;
        exitBar.addEventListener("click", exitFocus);
        exitBar.addEventListener("keydown", (ev) => {
          if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            exitFocus();
          }
        });
      }
      exitBar.innerHTML = `<span class="proof-focus-back">\u21A9</span><span>${num ? `Step ${num}` : "Focused"} \xB7 <span class="proof-focus-show-all">Show full proof</span></span>`;
      rail.insertBefore(exitBar, rail.firstChild);
      rail.classList.add("focusing");
    }
    function teardown() {
      if (!active) return;
      document.removeEventListener("keydown", onKeydown);
      rail.classList.remove("focusing");
      if (exitBar) exitBar.remove();
      withoutPersist(() => {
        active.steps.forEach(
          (st, i) => active.wasCollapsed[i] ? closeHandrail(st) : openHandrail(st)
        );
      });
      undimRail(active.svg);
      active.proofEl.classList.remove("proof-focused");
      active = null;
    }
    function exitFocus() {
      if (!active) return;
      teardown();
      announce2("Full proof restored.");
    }
    function enterFocus(railItem, proofEl, startIdx) {
      const svg = railItem.querySelector("svg.toc-tree");
      if (!svg) return;
      teardown();
      showProofMap();
      const idx = Number(startIdx);
      const cone = coneOf(svg, idx);
      const steps = stepsOf(proofEl);
      const wasCollapsed = steps.map((st) => st.classList.contains("hr-collapsed"));
      withoutPersist(() => {
        steps.forEach(
          (st, i) => cone.has(String(i)) ? openHandrail(st) : closeHandrail(st)
        );
      });
      dimRail(svg, cone);
      proofEl.classList.add("proof-focused");
      const sel = steps[idx];
      active = { proofEl, svg, startIdx: String(idx), steps, wasCollapsed };
      setExitBar(sel);
      document.addEventListener("keydown", onKeydown);
      const deps = steps.filter((_, i) => cone.has(String(i))).length - 1;
      const num = stepNumber(sel);
      announce2(
        `Focused step ${num || idx + 1}: showing the ${Math.max(deps, 0)} steps it depends on; press Escape to show the full proof.`
      );
      document.dispatchEvent(new CustomEvent("rsm:focus-enter"));
      if (sel) {
        const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        sel.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
      }
    }
    root2.addEventListener("focus:step", (ev) => {
      const step = ev.target.closest && ev.target.closest(".step");
      if (!step) return;
      const proofEl = step.closest(".proof[data-nodeid]");
      if (!proofEl) return;
      const railItem = rail.querySelector(
        `.proof-rail-item[data-proof="${proofEl.dataset.nodeid}"]`
      );
      if (!railItem) return;
      const startIdx = stepsOf(proofEl).indexOf(step);
      if (startIdx < 0) return;
      enterFocus(railItem, proofEl, startIdx);
    });
    rail.addEventListener("click", (ev) => {
      const node = ev.target.closest(".toc-node");
      if (!node) return;
      const railItem = node.closest(".proof-rail-item");
      if (!railItem || railItem.dataset.proof === "toc") return;
      ev.preventDefault();
      if (node.classList.contains("level-0")) return;
      const proofEl = root2.querySelector(`.proof[data-nodeid="${railItem.dataset.proof}"]`);
      if (!proofEl) return;
      enterFocus(railItem, proofEl, node.dataset.idx);
    });
  }

  // rsm/static/reorder.js
  function isDagStep(stepEl) {
    return !stepEl.closest(".calc");
  }
  function extractModel(railItem) {
    const svg = railItem.querySelector("svg.toc-tree");
    if (!svg) return null;
    const svgNodes = [...svg.querySelectorAll("a.toc-node")];
    let proofEl = null;
    for (const n2 of svgNodes) {
      const href = n2.getAttribute("href") || "";
      if (href.length > 1) {
        const el = document.getElementById(href.slice(1));
        if (el && el.classList.contains("step")) {
          proofEl = el.closest(".proof");
          break;
        }
      }
    }
    if (!proofEl) return null;
    const bodySteps = [...proofEl.querySelectorAll(".step")].filter(isDagStep);
    const n = bodySteps.length;
    if (!n) return null;
    const svgByIdx = /* @__PURE__ */ new Map();
    for (const node of svgNodes) svgByIdx.set(Number(node.getAttribute("data-idx")), node);
    const byId = /* @__PURE__ */ new Map();
    const idToId = /* @__PURE__ */ new Map();
    bodySteps.forEach((el, i) => {
      const id = el.dataset.nodeid || "idx-" + i;
      byId.set(id, { id, idx: i, bodyEl: el, svgNode: svgByIdx.get(i) || null, parent: null });
      idToId.set(i, id);
    });
    const deps = [];
    for (const edge of svg.querySelectorAll("path.toc-edge.dep")) {
      const s = Number(edge.getAttribute("data-from"));
      const d = Number(edge.getAttribute("data-to"));
      if (s < n && d < n) deps.push({ src: idToId.get(s), dst: idToId.get(d) });
    }
    for (const step of byId.values()) {
      let anc = step.bodyEl.parentElement;
      while (anc && anc !== proofEl) {
        if (anc.classList.contains("step") && anc.dataset.nodeid && byId.has(anc.dataset.nodeid)) {
          step.parent = anc.dataset.nodeid;
          break;
        }
        anc = anc.parentElement;
      }
    }
    const children = /* @__PURE__ */ new Map();
    for (const step of byId.values()) {
      const key = step.parent || "";
      if (!children.has(key)) children.set(key, []);
      children.get(key).push(step.id);
    }
    for (const arr of children.values()) arr.sort((a, b) => byId.get(a).idx - byId.get(b).idx);
    return { byId, deps, children, svg, proofEl };
  }
  function flatten(children) {
    const out = [];
    const walk = (key) => {
      for (const id of children.get(key) || []) {
        out.push(id);
        walk(id);
      }
    };
    walk("");
    return out;
  }
  function isValidOrder(model, flat) {
    const pos = new Map(flat.map((id, i) => [id, i]));
    return model.deps.every((e) => pos.get(e.dst) < pos.get(e.src));
  }
  function legalPositions(model, id) {
    const step = model.byId.get(id);
    if (!step) return [];
    const key = step.parent || "";
    const without = (model.children.get(key) || []).filter((x) => x !== id);
    const legal = [];
    for (let p = 0; p <= without.length; p++) {
      const trial = new Map(model.children);
      trial.set(key, [...without.slice(0, p), id, ...without.slice(p)]);
      if (isValidOrder(model, flatten(trial))) legal.push(p);
    }
    return legal;
  }
  function moveTo(model, id, pos) {
    const step = model.byId.get(id);
    const key = step.parent || "";
    const without = (model.children.get(key) || []).filter((x) => x !== id);
    const next = new Map(model.children);
    next.set(key, [...without.slice(0, pos), id, ...without.slice(pos)]);
    return next;
  }
  function applyToBody(model, newChildren) {
    for (const [key, ids] of newChildren) {
      const current = model.children.get(key) || [];
      if (ids.length === current.length && ids.every((id, i) => id === current[i])) continue;
      const els = ids.map((id) => model.byId.get(id).bodyEl);
      if (els.length < 2) continue;
      const container = els[0].parentElement;
      const domOrder = [...els].sort(
        (a, b) => a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1
      );
      const after = domOrder[domOrder.length - 1].nextSibling;
      for (const el of els) container.insertBefore(el, after);
    }
    model.children = newChildren;
  }
  var GRIP = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M9 5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/><path d="M9 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/><path d="M9 19m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/><path d="M15 5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/><path d="M15 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/><path d="M15 19m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"/></svg>';
  var reorderState = /* @__PURE__ */ new WeakMap();
  var liveRegion = null;
  function announce(msg) {
    if (!liveRegion) {
      liveRegion = document.createElement("div");
      liveRegion.className = "reorder-sr-status";
      liveRegion.setAttribute("role", "status");
      liveRegion.setAttribute("aria-live", "polite");
      document.body.appendChild(liveRegion);
    }
    liveRegion.textContent = "";
    requestAnimationFrame(() => {
      liveRegion.textContent = msg;
    });
  }
  function setup6(root2 = document) {
    root2.addEventListener("reorder:toggle", (ev) => {
      const proof = ev.target.closest && ev.target.closest(".proof.hr");
      if (!proof) return;
      if (ev.detail && ev.detail.active) activate(proof);
      else deactivate(proof);
    });
    root2.addEventListener("keydown", (ev) => {
      if (ev.key !== "Escape") return;
      for (const proof of document.querySelectorAll(".proof.reorder-active")) {
        proof.classList.remove("reorder-active");
        deactivate(proof);
      }
    });
  }
  function railItemFor(proof) {
    const id = proof.dataset.nodeid;
    return id ? document.querySelector(`.proof-rail-item[data-proof="${id}"]`) : null;
  }
  function activate(proof) {
    if (reorderState.has(proof)) return;
    const railItem = railItemFor(proof);
    const model = railItem && extractModel(railItem);
    if (!model || model.byId.size < 2) {
      proof.classList.remove("reorder-active");
      return;
    }
    const handles = [];
    for (const step of model.byId.values()) {
      step.bodyEl.dataset.stateIdx = String(step.idx);
      const handle = document.createElement("button");
      handle.type = "button";
      handle.className = "reorder-handle";
      const label = step.bodyEl.dataset.menuLabel || "this step";
      handle.setAttribute("aria-label", `Reorder ${label}`);
      handle.innerHTML = GRIP;
      step.bodyEl.appendChild(handle);
      wireHandle(handle, step.id, proof, model);
      handles.push(handle);
    }
    const scopeBtn = document.querySelector('.rail-scope[data-scope="proof"]');
    if (scopeBtn) scopeBtn.click();
    reorderState.set(proof, { model, handles });
    announce(`Reorder mode on, ${model.byId.size} steps. Drag a step's handle to reorder it.`);
  }
  function flipMove(model, applyFn) {
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      applyFn();
      return;
    }
    const els = [...model.byId.values()].map((s) => s.bodyEl);
    const before = new Map(els.map((el) => [el, el.getBoundingClientRect().top]));
    applyFn();
    for (const el of els) {
      const dy = before.get(el) - el.getBoundingClientRect().top;
      if (!dy) continue;
      el.style.transition = "transform 0s";
      el.style.transform = `translateY(${dy}px)`;
      requestAnimationFrame(() => {
        el.style.transition = "transform 220ms cubic-bezier(.2,.7,.3,1)";
        el.style.transform = "";
      });
      el.addEventListener(
        "transitionend",
        () => {
          el.style.transition = "";
          el.style.transform = "";
        },
        { once: true }
      );
    }
  }
  function deactivate(proof) {
    const st = reorderState.get(proof);
    if (!st) return;
    for (const h of st.handles) h.remove();
    reorderState.delete(proof);
    announce("Reorder mode off.");
  }
  function siblingEls(model, id) {
    const step = model.byId.get(id);
    const key = step.parent || "";
    return (model.children.get(key) || []).filter((x) => x !== id).map((x) => model.byId.get(x).bodyEl);
  }
  function slotUnderPointer(els, y) {
    let slot = 0;
    for (const el of els) {
      const r = el.getBoundingClientRect();
      if (r.top + r.height / 2 < y) slot++;
    }
    return slot;
  }
  function wireHandle(handle, id, proof, model) {
    handle.addEventListener("pointerdown", (ev) => {
      ev.preventDefault();
      ev.stopPropagation();
      const step = model.byId.get(id);
      const key = step.parent || "";
      const legal = new Set(legalPositions(model, id));
      const others = siblingEls(model, id);
      const container = step.bodyEl.parentElement;
      const start = (model.children.get(key) || []).indexOf(id);
      const prevPin = model.svg ? model.svg.__pinnedIdx : null;
      let target = start;
      const indicator = document.createElement("div");
      indicator.className = "reorder-indicator";
      proof.classList.add("reorder-dragging");
      step.bodyEl.classList.add("reorder-dragged");
      if (model.svg) pinTreeCurrent(model.svg, String(step.idx));
      const place = (slot) => {
        if (slot < others.length) container.insertBefore(indicator, others[slot]);
        else container.appendChild(indicator);
      };
      const onMove = (e) => {
        const slot = slotUnderPointer(others, e.clientY);
        place(slot);
        if (legal.has(slot)) {
          target = slot;
          indicator.classList.remove("illegal");
        } else {
          target = start;
          indicator.classList.add("illegal");
        }
      };
      const onUp = () => {
        document.removeEventListener("pointermove", onMove);
        document.removeEventListener("pointerup", onUp);
        indicator.remove();
        proof.classList.remove("reorder-dragging");
        step.bodyEl.classList.remove("reorder-dragged");
        if (model.svg) pinTreeCurrent(model.svg, prevPin);
        if (target !== start && legal.has(target)) {
          flipMove(model, () => applyToBody(model, moveTo(model, id, target)));
          const sib = model.children.get(key) || [];
          const label = step.bodyEl.dataset.menuLabel || "Step";
          announce(`${label} moved to position ${sib.indexOf(id) + 1} of ${sib.length}.`);
        }
      };
      document.addEventListener("pointermove", onMove);
      document.addEventListener("pointerup", onUp);
    });
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
        setup2();
        collapseInitial(root2);
        restoreCollapse(root2);
      } catch (err) {
        console.error("Loading handrails.js FAILED!", err);
      }
      try {
        setup(root2);
      } catch (err) {
        console.error("Loading tocarcs.js FAILED!", err);
      }
      try {
        setup4(root2);
      } catch (err) {
        console.error("Loading prooftree.js FAILED!", err);
      }
      try {
        setup5(root2);
      } catch (err) {
        console.error("Loading focusmode.js FAILED!", err);
      }
      try {
        setup6(root2);
      } catch (err) {
        console.error("Loading reorder.js FAILED!", err);
      }
      try {
        if (keys) {
          setup3(root2);
        }
      } catch (err) {
        console.error("Loading keyboard.js FAILED!", err);
      }
      try {
        setupBackPill();
        window.addEventListener("hashchange", () => {
          const id = decodeURIComponent(window.location.hash.slice(1));
          if (!id || id === "top") {
            hideBackPill();
            return;
          }
          const el = document.getElementById(id);
          if (!el) {
            hideBackPill();
            return;
          }
          if (!el.hasAttribute("tabindex")) el.setAttribute("tabindex", "-1");
          el.focus({ preventScroll: true });
          showBackPill();
        });
      } catch (err) {
        console.error("Setting up hash-focus FAILED!", err);
      }
      window.__rsmInitialized = true;
      await onrender(root2);
      try {
        mountNotationPanel(root2);
        createTooltips();
      } catch (err) {
        console.error("Loading notation panel FAILED!", err);
      }
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
        drawAll(root2);
      } catch (err) {
        console.error("TOC arcs redraw FAILED!", err);
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
  var __backPillScroll = null;
  function setupBackPill() {
    if (document.querySelector(".rsm-back-pill")) return;
    const pill = document.createElement("button");
    pill.type = "button";
    pill.className = "rsm-back-pill";
    pill.setAttribute("aria-label", "Back to where you were");
    pill.innerHTML = '<span class="rsm-back-pill-arrow" aria-hidden="true">\u2190</span> Back';
    pill.addEventListener("click", () => window.history.back());
    document.body.appendChild(pill);
  }
  function showBackPill() {
    const pill = document.querySelector(".rsm-back-pill");
    if (!pill) return;
    pill.classList.add("is-visible");
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
  return __toCommonJS(onload_exports);
})();
