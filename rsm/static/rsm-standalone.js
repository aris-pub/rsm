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
    nodes.forEach((node) => {
      const idx = node.getAttribute("data-idx");
      node.addEventListener("mouseenter", () => {
        const cone = closure(idx);
        for (const e of edges) {
          const on = !e.classList.contains("fwd") && cone.has(e.dataset.from) && cone.has(e.dataset.to);
          e.classList.toggle("toc-faded", !on);
        }
        for (const n of nodes) n.classList.toggle("toc-faded", !cone.has(n.getAttribute("data-idx")));
        showLabel(node);
      });
      node.addEventListener("mouseleave", () => {
        for (const x of svg.querySelectorAll(".toc-faded")) x.classList.remove("toc-faded");
        if (hover) hover.style.display = "none";
      });
    });
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
    singletonMenu.querySelectorAll(".hr-menu-item").forEach((it) => it.classList.remove("active"));
    if (activeHr) {
      const zone = activeHr.querySelector(":scope > .hr-menu-zone");
      if (zone) zone.style.display = "";
    }
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
  function notifyHandrailToggle(hr, collapsed) {
    document.dispatchEvent(
      new CustomEvent("rsm:handrail-toggle", { detail: { hr, collapsed } })
    );
  }
  function collapseInitial(root2) {
    (root2 || document).querySelectorAll(".hr[data-start-collapsed]").forEach((hr) => closeHandrail(hr));
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
    const menu = el.querySelector(":scope > .hr-menu-zone .hr-menu");
    if (!menu) return;
    const active = menu.querySelector(":scope > .hr-menu-item.active:not(.disabled)");
    if (active) active.click();
  }
  function menuUpOrDown(el, direction) {
    const menu = el.querySelector(":scope > .hr-menu-zone .hr-menu");
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
  function createTooltips() {
    $(".manuscriptwrapper a.reference:not(.external):not(.tooltipstered)").tooltipster({
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
      delay: 200,
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
        setTooltipContent(instance, $(helper.origin).attr("data-tooltip"));
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
        scope: rail.classList.contains("scope-proof") ? "proof" : "document",
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
    try {
      const saved = JSON.parse(localStorage.getItem(lsKey) || "null");
      if (saved) {
        selectScope(saved.scope === "proof" ? "proof" : "document");
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
      for (const [k, item] of items) item.classList.toggle("shown", k === key);
      rail.classList.toggle("no-proof", key === null);
      updateCollapsedClass();
      updateState();
    }
    show(null);
    if (proofs.length) {
      const visible = /* @__PURE__ */ new Set();
      const observer = new IntersectionObserver(
        (entries) => {
          for (const e of entries) {
            if (e.isIntersecting) visible.add(e.target);
            else visible.delete(e.target);
          }
          let best = null;
          let bestTop = Infinity;
          for (const p of visible) {
            const top = p.getBoundingClientRect().top;
            if (top < bestTop) {
              bestTop = top;
              best = p;
            }
          }
          show(best ? best.getAttribute("data-nodeid") : null);
        },
        { rootMargin: "-12% 0px -55% 0px", threshold: 0 }
      );
      for (const p of proofs) observer.observe(p);
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
      el.scrollIntoView({ behavior: "smooth", block: "start" });
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
    function currentStepOf(proofEl) {
      const center = window.innerHeight / 2;
      let best = -1;
      let bestTop = -Infinity;
      proofEl.querySelectorAll(".step").forEach((s, i) => {
        const top = s.getBoundingClientRect().top;
        if (top <= center && top > bestTop) {
          bestTop = top;
          best = i;
        }
      });
      return best;
    }
    function updateState() {
      if (rail.classList.contains("focusing")) {
        setCurrentNode(null);
        return;
      }
      let idx = -1;
      if (current) {
        const proofEl = root2.querySelector(`.proof[data-nodeid="${current}"]`);
        if (proofEl) {
          idx = currentStepOf(proofEl);
          if (idx < 0) idx = 0;
        }
      }
      setActiveIdx(idx);
      const item = current ? items.get(current) : null;
      setCurrentNode(
        item && idx >= 0 ? item.querySelector(`.toc-node[data-idx="${idx}"]`) : null
      );
    }
    const stepObserver = new IntersectionObserver(() => updateState(), {
      rootMargin: "-50% 0px -50% 0px",
      threshold: 0
    });
    for (const s of root2.querySelectorAll(".proof[data-nodeid] .step")) {
      stepObserver.observe(s);
    }
    function cloneClean(el) {
      const c = el.cloneNode(true);
      c.removeAttribute("id");
      c.removeAttribute("data-nodeid");
      c.querySelectorAll("[id],[data-nodeid]").forEach((n) => {
        n.removeAttribute("id");
        n.removeAttribute("data-nodeid");
      });
      c.querySelectorAll(
        ".hr-collapse-zone,.hr-menu-zone,.hr-border-zone,.hr-spacer-zone,.hr-info-zone"
      ).forEach((n) => n.remove());
      c.querySelectorAll(".hr").forEach(
        (n) => n.classList.remove("hr", "hr-offset", "hr-labeled", "hr-hidden")
      );
      return c;
    }
    function renderState() {
      if (proofView !== "state") return;
      const item = current ? items.get(current) : null;
      if (!item) return;
      const panel = item.querySelector(".rail-state");
      if (!panel) return;
      const data = stateData.get(item.dataset.proof);
      if (!data || active.idx < 0 || active.idx >= data.length) {
        panel.innerHTML = '<div class="rail-state-empty">Scroll into a proof to see its live hypotheses and current goal.</div>';
        return;
      }
      const st = data[active.idx];
      panel.innerHTML = "";
      function badge(num) {
        const b = document.createElement("span");
        b.className = "rail-step-badge";
        b.textContent = "\u27E8" + num + "\u27E9";
        return b;
      }
      const hyps = (st.hyps || []).map((h) => ({ el: root2.querySelector(`[data-nodeid="${h.id}"]`), num: h.num })).filter((h) => h.el);
      const hblock = document.createElement("div");
      hblock.className = "rail-state-block rail-hyps";
      hblock.innerHTML = '<div class="rail-state-label">Assuming</div>';
      const ul = document.createElement("ul");
      if (hyps.length) {
        for (const h of hyps) {
          const li = document.createElement("li");
          if (h.num) li.appendChild(badge(h.num));
          li.appendChild(cloneClean(h.el));
          ul.appendChild(li);
        }
      } else {
        const li = document.createElement("li");
        li.className = "rail-hyp-empty";
        li.textContent = "no assumptions yet";
        ul.appendChild(li);
      }
      hblock.appendChild(ul);
      panel.appendChild(hblock);
      const goalBlock = document.createElement("div");
      goalBlock.className = "rail-state-block rail-goal";
      goalBlock.innerHTML = '<div class="rail-state-label">To show</div>';
      const body = document.createElement("div");
      body.className = "rail-goal-body";
      const g = st.goal;
      const goalEl = g && g.id != null ? root2.querySelector(`[data-nodeid="${g.id}"]`) : null;
      if (goalEl) {
        if (g.num) body.appendChild(badge(g.num));
        if (g.thm) {
          const cz = goalEl.querySelector(":scope > .hr-content-zone") || goalEl;
          const clone = cloneClean(cz);
          clone.querySelectorAll(".hr-label, .construct.let, .construct.assume").forEach((n) => n.remove());
          body.appendChild(clone);
        } else {
          body.appendChild(cloneClean(goalEl));
        }
      } else {
        body.textContent = "the main result";
      }
      goalBlock.appendChild(body);
      panel.appendChild(goalBlock);
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
    const collapseStep = (st) => st.classList.add("proof-focus-collapsed");
    const openStep = (st) => st.classList.remove("proof-focus-collapsed");
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
    let exitBar = null;
    function setExitBar(sel) {
      const num = stepNumber(sel);
      if (!exitBar) {
        exitBar = document.createElement("div");
        exitBar.className = "proof-focus-exit";
        exitBar.setAttribute("role", "button");
        exitBar.tabIndex = 0;
        exitBar.addEventListener("click", exitFocus);
      }
      exitBar.innerHTML = `<span class="proof-focus-back">\u21A9</span><span>${num ? `Step ${num}` : "Focused"} \xB7 <span class="proof-focus-show-all">Show full proof</span></span>`;
      rail.insertBefore(exitBar, rail.firstChild);
      rail.classList.add("focusing");
    }
    function exitFocus() {
      if (!active) return;
      rail.classList.remove("focusing");
      if (exitBar) exitBar.remove();
      stepsOf(active.proofEl).forEach(openStep);
      undimRail(active.svg);
      active.proofEl.classList.remove("proof-focused");
      active = null;
    }
    function enterFocus(railItem, proofEl, startIdx) {
      exitFocus();
      const svg = railItem.querySelector("svg.toc-tree");
      if (!svg) return;
      const cone = coneOf(svg, startIdx);
      const steps = stepsOf(proofEl);
      steps.forEach((st, i) => cone.has(String(i)) ? openStep(st) : collapseStep(st));
      dimRail(svg, cone);
      proofEl.classList.add("proof-focused");
      const sel = steps[startIdx];
      active = { proofEl, svg, startIdx: String(startIdx) };
      setExitBar(sel);
      if (sel) sel.scrollIntoView({ behavior: "smooth", block: "center" });
    }
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
        if (keys) {
          setup3(root2);
        }
      } catch (err) {
        console.error("Loading keyboard.js FAILED!", err);
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
  return __toCommonJS(onload_exports);
})();
