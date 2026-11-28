// tooltips.js
//
// Setup tooltips on <a> tags.
//

import { typesetMath } from "./libraries.js";
import { previewWanted } from "./asides.js";
import { cloneWithoutRawHtml, withoutRawHtml } from "./rawhtml.js";
import { isTouch } from "./touch.js";

// Like $el.clone(), but an :html: or :htmlblock: in the copy shows its fallback (rawhtml.js).
const copyOf = ($el) => $($el.toArray().map(cloneWithoutRawHtml));

// Tabler pin, outline (not pinned) and filled (pinned).
const PIN_ICON =
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 4.5l-4 4l-4 1.5l-1.5 1.5l7 7l1.5 -1.5l1.5 -4l4 -4"/><path d="M9 15l-4.5 4.5"/><path d="M14.5 4l5.5 5.5"/></svg>';
const PIN_FILLED_ICON =
  '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M15.113 3.21l.094 .083l5.5 5.5a1 1 0 0 1 -1.175 1.59l-3.172 3.171l-1.424 3.797a1 1 0 0 1 -.158 .277l-.07 .08l-1.5 1.5a1 1 0 0 1 -1.32 .082l-.095 -.083l-2.793 -2.792l-3.793 3.792a1 1 0 0 1 -1.497 -1.32l.083 -.094l3.792 -3.793l-2.792 -2.793a1 1 0 0 1 -.083 -1.32l.083 -.094l1.5 -1.5a1 1 0 0 1 .258 -.187l.098 -.042l3.796 -1.425l3.171 -3.17a1 1 0 0 1 1.497 -1.26z"/></svg>';
const PIN_LABEL = "Pin to the sidebar";
const PINNED_LABEL = "Pinned in the sidebar";

// The hrefs of the pinned blocks, newest first.
const pinned = [];

// What is pinned now, newest first, for shareview.js to put in a view link.
export function currentPins() {
  return [...pinned];
}

export function isPinned(href) {
  return pinned.includes(href);
}

// Build the inert excerpt shown for a reference: a clone of the target with
// handrails stripped. Returns { content, error }.
function buildExcerpt(rawHref) {
  if (!rawHref) return { content: "", error: "no-href" };
  // escape '.' (class) and ':' (protocol) so they read as a selector
  const target = rawHref.replaceAll(".", "\\.").replaceAll(":", "\\:");
  if (target === "#") return { content: "", error: "no-label" };
  const $t = $(target);
  if (!$t[0]) return { content: "", error: "unknown" };
  const tag = $t.prop("tagName");
  const classes = $t[0].classList;
  let content = "";
  let clone;
  if (tag === "LI" && classes.contains("note")) {
    // An entry of the notes list: show its text and number, without the
    // backlink (the reader is already at the call) or the alignment handrail.
    clone = copyOf($t);
    clone.find(".note-backlink").remove();
    const zone = clone.find(".hr-content-zone").first();
    content = `<div class="note-preview">${(zone[0] ? zone : clone).html()}</div>`;
  } else if (tag === "DIV" && classes.contains("aside")) {
    // An aside has no handrail of its own, so its content is the excerpt. The
    // class is not "aside", so excerpt cleanup does not strip it.
    content = `<div class="aside-preview">${$t.html()}</div>`;
  } else if (["P", "LI"].includes(tag)) {
    // A paragraph's or list item's handrail wraps it from OUTSIDE the element,
    // so its own innerHTML carries no handrail chrome to strip.
    content = `<div>${$t.html()}</div>`;
  } else if (tag === "FIGURE" && classes.contains("html")) {
    content = widgetPreview($t[0]);
  } else if (tag === "FIGURE") {
    // A figure keeps its handrail chrome INSIDE itself: the figcaption is its
    // own hr, with the menu dots (in .hr-border-zone) and data-menu-*
    // attributes. Take the HTML from a stripped clone, like the block branches
    // below, so a previewed figure is just the image and caption,
    // with no interactive menu dots or leftover menu metadata.
    clone = copyOf($t);
    stripHandrail(clone);
    clone
      .find("[data-menu-label]")
      .removeAttr("data-menu-label data-menu-link data-menu-code data-menu-static-toggle tabindex");
    content = `<div>${clone.html()}</div>`;
  } else if (tag === "SPAN" && classes.contains("math")) {
    content = `<div>${$t.html()}</div>`;
  } else if (tag === "SPAN") {
    content = `<div>${$t.parent().html()}</div>`;
  } else if (tag === "DT") {
    content = $t.next().html() || "";
  } else if (tag === "TABLE") {
    content = $t[0].outerHTML;
  } else if (tag === "SECTION") {
    clone = copyOf($t);
    clone.children().slice(2).remove();
    stripHandrail(clone);
    // The section's first block is copied whole, so it keeps the class that
    // gives its label the handrail line. A block's own tooltip copies only its
    // inside, so it never has the class.
    clone.find(".hr-labeled").removeClass("hr-labeled");
    content = clone.html();
  } else if (tag === "A") {
    content = `<div>${$t.parent().html()}</div>`;
  } else if (tag === "DIV") {
    if (classes.contains("calc")) {
      content = calcPreview($t);
    } else if (classes.contains("step")) {
      clone = copyOf($t.find(".statement"));
      stripHandrail(clone);
      content = clone.html();
    } else if (classes.contains("proof")) {
      clone = copyOf($t);
      // A collapsed proof hides its body with .hide. The preview shows the proof
      // itself, so undo the proof's own fold (nested folds stay as they are).
      clone.children(".hr-content-zone").children(".hide").removeClass("hide");
      stripHandrail(clone);
      content = clone.html();
    } else if (["math", "algorithm"].some((c) => classes.contains(c))) {
      clone = copyOf($t);
      stripHandrail(clone);
      content = clone.html();
    } else if (
      ["paragraph", "mathblock", "theorem", "lemma", "corollary", "example",
       "exercise", "proposition", "problem", "porism", "remark", "definition",
       "bibitem"].some((c) => classes.contains(c))
    ) {
      clone = copyOf($t);
      stripHandrail(clone);
      content = clone.html();
    }
  }
  content = withWidgetStills(content);
  // The branches above that read the live target's HTML directly copy its
  // :html: and :htmlblock: too.
  content = withoutRawHtml(content);
  return { content: content || "", error: content ? null : "unsupported" };
}

// An excerpt's HTML with each figure that holds HTML inside it swapped for its
// still image, or else its alt text, as such a figure alone is (widgetPreview): a live
// copy attaches to the original's scripts and state, and two copies of one
// control can fight over it.
function withWidgetStills(html) {
  if (!html || !html.includes("html")) return html;
  const t = document.createElement("template");
  t.innerHTML = html;
  const widgets = t.content.querySelectorAll("figure.html");
  if (!widgets.length) return html;
  for (const fig of widgets) fig.replaceWith(widgetStill(fig));
  return t.innerHTML;
}

// The still image of a figure that holds HTML, or else its alt text.
function widgetStill(fig) {
  const still = document.createElement("div");
  const imgs = fig.querySelectorAll(".static-fallback img");
  if (imgs.length) {
    still.className = "widget-preview-still";
    for (const img of imgs) still.append(img.cloneNode());
  } else {
    still.className = "widget-preview-alt";
    still.textContent = fig.getAttribute("data-alt") || "";
  }
  return still;
}

// The excerpt of a figure that holds HTML. A copy of the live HTML does not
// work out of its place (its styles and scripts are tied to the original), so
// show its number, its still image when it has one (both light and dark, and
// braiid.css shows the one for the current theme, so a pinned excerpt follows a
// theme switch) or else its alt text, its caption, and a line saying where the
// interactive version is.
function widgetPreview(fig) {
  const esc = (s) =>
    String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll('"', "&quot;");
  const capLabel = fig.querySelector(":scope > figcaption .label");
  const number = fig.getAttribute("data-number");
  const label =
    (capLabel && capLabel.textContent.replace(/\s+/g, " ").trim().replace(/\.$/, "")) ||
    (number ? `Figure ${number}` : "Figure");
  let body = "";
  const imgs = fig.querySelectorAll(".static-fallback img");
  if (imgs.length) {
    body = '<div class="widget-preview-still">';
    for (const img of imgs) {
      const cls = img.className ? ` class="${esc(img.className)}"` : "";
      body += `<img${cls} src="${esc(img.getAttribute("src") || "")}" alt="${esc(img.alt)}">`;
    }
    body += "</div>";
  } else if (fig.getAttribute("data-alt")) {
    body = `<p class="widget-preview-alt">${esc(fig.getAttribute("data-alt"))}</p>`;
  }
  const cap = fig.querySelector(":scope > figcaption");
  if (cap) {
    const c = copyOf($(cap));
    stripHandrail(c);
    c.find(".label").first().remove();
    c.find("[data-menu-label]").removeAttr(
      "data-menu-label data-menu-link data-menu-code data-menu-static-toggle tabindex"
    );
    const text = c.text().trim();
    if (text) body += `<div class="widget-preview-caption">${c.html()}</div>`;
  }
  return (
    '<div class="widget-preview">' +
    `<p class="widget-preview-label">${esc(label)}</p>` +
    body +
    '<p class="widget-preview-note">Interactive in the manuscript.</p></div>'
  );
}

// The pin control in a reference preview: an icon in the preview's top-right
// corner. Offered only when the page has the sidebar (`--sidebar`), the place a
// pinned block goes.
function pinBar(href) {
  if (!document.querySelector(".proof-rail")) return "";
  if (!pinBlockOf(targetOf(href))) return "";
  const h = (href || "").replaceAll('"', "&quot;");
  const on = isPinned(href);
  const label = on ? PINNED_LABEL : PIN_LABEL;
  return (
    '<div class="ref-pin-bar">' +
    `<button type="button" class="ref-pin" data-pin-target="${h}" ` +
    `aria-label="${label}" data-tip="${label}" ` +
    `aria-pressed="${on}"${on ? " data-pinned" : ""}>` +
    (on ? PIN_FILLED_ICON : PIN_ICON) + "</button></div>"
  );
}

// Repaint every visible preview's pin control after the pins change.
function paintPins() {
  for (const btn of document.querySelectorAll(".ref-pin")) {
    const on = isPinned(btn.dataset.pinTarget);
    const label = on ? PINNED_LABEL : PIN_LABEL;
    btn.toggleAttribute("data-pinned", on);
    btn.setAttribute("aria-pressed", String(on));
    btn.setAttribute("aria-label", label);
    btn.dataset.tip = label;
    btn.innerHTML = on ? PIN_FILLED_ICON : PIN_ICON;
  }
}

const UNPIN_BUTTON =
  '<button type="button" class="pin-unpin" aria-label="Unpin" data-tip="Unpin">' +
  '<svg aria-hidden="true"><use href="#hr-icon-unpin" width="100%" height="100%"/></svg>' +
  "</button>";

function targetOf(href) {
  const id = decodeURIComponent((href || "").replace(/^#/, ""));
  return id ? document.getElementById(id) : null;
}

// The handrail of a pinned block that holds the unpin icon: the block's own,
// else its caption's (figures and tables), else that of its direct child
// (bibliography entries, footnotes, figures without a caption).
function handrailOf(block) {
  if (block.matches(".hr")) return block;
  return block.querySelector(":scope > figcaption.hr") || block.querySelector(":scope > .hr");
}

// The block that pinning a target copies, or null when the target cannot be
// pinned. A table's caption is its sibling, so a table pins with its wrapper.
// Sections are not pinned.
function pinBlockOf(target) {
  if (!target || target.matches("section")) return null;
  const block = target.matches("table") ? target.closest(".table-wrapper") : target;
  const hr = block && handrailOf(block);
  return hr && hr.querySelector(":scope > .hr-info-zone") ? block : null;
}

// A copy of the block that an href points at, with its handrail, for the
// Pinned view. Null when the target cannot be pinned.
function pinCopy(href) {
  const block = pinBlockOf(targetOf(href));
  if (!block) return null;
  const copy = cloneWithoutRawHtml(block);
  const hr = handrailOf(copy);
  const info = hr.querySelector(":scope > .hr-info-zone");
  // The copy sits in the live page, so ids and node ids would duplicate the
  // source block's and break getElementById and hash navigation.
  for (const el of [copy, ...copy.querySelectorAll("[id], [data-nodeid]")]) {
    el.removeAttribute("id");
    el.removeAttribute("data-nodeid");
  }
  copy.querySelectorAll(".aside").forEach((e) => e.remove());
  for (const el of [copy, ...copy.querySelectorAll(".hr-menu-open")]) {
    el.classList.remove("hr-menu-open");
  }
  // A step or a nested block draws its handrail in its parent's gutter. In the
  // panel it stands alone, so it lays out its handrail like a top-level block.
  copy.classList.remove("hr-offset");
  hr.classList.add("pin-hr");
  info.insertAdjacentHTML("afterbegin", UNPIN_BUTTON);
  // A live copy of HTML attaches to the original's scripts and state, so a
  // figure that holds HTML shows its still instead. A pinned one keeps its
  // handrails, with the still in place of the HTML.
  if (copy.matches("figure.html")) {
    const zone = copy.querySelector(":scope > .hr:not(figcaption) > .hr-content-zone");
    if (zone) zone.replaceChildren(widgetStill(block));
  }
  for (const fig of copy.querySelectorAll("figure.html")) fig.replaceWith(widgetStill(fig));
  copy.dataset.pinTarget = href;
  return copy;
}

// Pin the block an href points at and dispatch rail:pin, which prooftree.js
// (owner of the rail) handles. Used by the preview's pin control and by the
// handrail menu's Pin item. Pinning a block that is pinned already only shows
// the Pinned view. Returns false if nothing could be pinned. A transient pin
// (from a shared view link) does not save the open sidebar view, so the
// recipient's own settings stay as they were.
export function pinTarget(href, origin = document, { transient = false } = {}) {
  if (isPinned(href)) {
    document.dispatchEvent(
      new CustomEvent("rail:show", { detail: { view: "pinned", open: true } })
    );
    return true;
  }
  const node = pinCopy(href);
  if (!node) return false;
  pinned.unshift(href);
  origin.dispatchEvent(
    new CustomEvent("rail:pin", { bubbles: true, detail: { node, target: href, transient } })
  );
  paintPins();
  return true;
}

export function unpinTarget(href) {
  const i = pinned.indexOf(href);
  if (i < 0) return;
  pinned.splice(i, 1);
  document.dispatchEvent(
    new CustomEvent("rail:unpin", { detail: { target: href, remaining: pinned.length } })
  );
  paintPins();
}

// One delegated handler for every preview's pin control and every pinned
// block's unpin icon.
let pinDelegated = false;
function setupPinDelegation() {
  if (pinDelegated) return;
  pinDelegated = true;
  document.addEventListener("click", (ev) => {
    if (!ev.target.closest) return;
    const unpin = ev.target.closest(".pin-unpin");
    if (unpin) {
      const copy = unpin.closest("[data-pin-target]");
      if (copy) unpinTarget(copy.dataset.pinTarget);
      return;
    }
    const btn = ev.target.closest(".ref-pin");
    if (btn) pinTarget(btn.dataset.pinTarget, btn);
  });
}

// The reference preview, also used by footnote markers. Touch opens it through
// tapToPreview, not tooltipster's touchstart, so the tap does not also follow
// the link.
const PREVIEW_OPTIONS = {
  theme: ['tooltipster-shadow', 'tooltipster-shadow-rsm'],
  delay: 200,
  minWidth: 100,
  maxWidth: 500,
  // Interactive so the reader can move into the preview to click its pin
  // button without it closing on the way.
  interactive: true,
  trigger: 'custom',
  triggerOpen: { mouseenter: true },
  triggerClose: { click: true, mouseleave: true, originClick: true, tap: true },
  functionInit: function (instance, helper) {
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
    setTooltipContent(instance, pinBar(rawHref) + content);
  },
  functionReady: function (instance, helper) {
    // The tooltip content is a clone of the target and can carry un-typeset
    // math (raw \(...\) inline or $$...$$ display); render it the same way the
    // body and the sidebar do, so tooltips are never the odd one out.
    const el = instance.elementTooltip ? instance.elementTooltip() : helper.tooltip;
    if (el) typesetMath(el instanceof $ ? el[0] : el);
  }
};

// On touch, the first tap on `el` opens its preview instead of following the
// link, and a second tap on it while the preview is open follows the link. A
// tap anywhere else closes the preview (tooltipster's tap close). On a touch
// page (isTouch) a mouse click counts as a tap. Elsewhere a mouse click, and
// Enter on any page, still follow the link at once. `el` must already have its
// tooltip. A WeakSet, not a data attribute, marks bound links: the sidebar
// clones references (prooftree.js) and a copied attribute would leave the clone
// unbound.
const tapBound = new WeakSet();
export function tapToPreview(el) {
  if (tapBound.has(el)) return;
  tapBound.add(el);
  let touched = false;
  el.addEventListener("pointerdown", (ev) => {
    touched = ev.pointerType === "touch" || isTouch();
  });
  el.addEventListener("click", (ev) => {
    if (!touched) return;
    touched = false;
    if ($(el).tooltipster("status").open) return;
    $(el).tooltipster("open");
    // Tooltipster opens nothing when there is no excerpt (an unknown target),
    // and then the tap follows the link as before.
    if ($(el).tooltipster("status").open) ev.preventDefault();
  });
}

// On a phone tooltipster ignores the mouseenter that a tap fires, so pointing
// opens no tooltip. Do the same for a mouse on a touch page.
let pointingStopped = false;
function stopPointingOnTouchPages() {
  if (pointingStopped) return;
  pointingStopped = true;
  $.tooltipster.on("start", (ev) => {
    if (isTouch() && ev.event && ev.event.type === "mouseenter") ev.stop();
  });
}

export function createTooltips() {
  setupPinDelegation();
  stopPointingOnTouchPages();
  // Footnote markers get the same preview as references, and both open it on a
  // tap through tapToPreview. Aside phrases are set up below.
  const $previewed = $(
    ".manuscriptwrapper a.reference:not(.external):not(.tooltipstered), " +
      '.manuscriptwrapper a.note-marker[data-note-kind="note"]:not(.tooltipstered)'
  );
  $previewed.tooltipster(PREVIEW_OPTIONS);
  $previewed.each((_, el) => tapToPreview(el));

  // The Proof panel's list of proofs previews each proof on hover. A tap goes
  // straight to the proof, so touch gets no preview.
  $(".proof-rail a.rail-proof-link:not(.tooltipstered)").tooltipster({
    ...PREVIEW_OPTIONS,
    side: "right",
  });

  // Aside phrases get the same preview, but only while the aside is closed
  // below its block on a page without html.touch (asides.js says when). A tap or click
  // opens the aside itself, so touch never opens a preview.
  $(".manuscriptwrapper a.aside-phrase:not(.tooltipstered)").tooltipster({
    ...PREVIEW_OPTIONS,
    triggerOpen: { mouseenter: true },
    triggerClose: { click: true, mouseleave: true, originClick: true },
    functionBefore: (instance, helper) => previewWanted(helper.origin),
  });

  $(".manuscriptwrapper .author-names sup:is([data-affiliation], [data-note]):not(.tooltipstered)").tooltipster({
    theme: ['tooltipster-shadow', 'tooltipster-shadow-rsm'],
    delay: 200,
    minWidth: 100,
    maxWidth: 500,
    trigger: 'custom',
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
    functionInit: function (instance, helper) {
      const tip = $("<div></div>");
      for (const key of ["affiliation", "note"]) {
        tip.append(authorDetail(helper.origin, key));
      }
      instance.content($('<div class="manuscriptwrapper"></div>').append(tip));
    },
  });

  // An author's name shows that author's affiliation and note. Touch opens it
  // through tapToPreview, as for references.
  const $authorNames = $(
    ".manuscriptwrapper .author-name-text:is([data-affiliation], [data-note]):not(.tooltipstered)"
  );
  $authorNames.tooltipster({
    ...PREVIEW_OPTIONS,
    interactive: false,
    functionInit: function (instance, helper) {
      const tip = $('<div class="author-tip"></div>');
      for (const key of ["affiliation", "note"]) {
        const detail = authorDetail(helper.origin, key);
        if (detail) tip.append($("<p></p>").append(detail));
      }
      // .manuscriptwrapper so that the page's CSS applies inside the tooltip.
      instance.content($('<div class="manuscriptwrapper"></div>').append(tip));
    },
    functionReady: undefined,
  });
  $authorNames.each((_, el) => tapToPreview(el));

  // DAG nodes: show the link target's rendered excerpt (math and all), the same
  // way reference tooltips do, so the graph is not the odd one out. Falls back to
  // the plain-text statement in data-tooltip when the target cannot be excerpted.
  $(".proof-rail a.toc-node:not(.tooltipstered), .manuscriptwrapper a.toc-node:not(.tooltipstered)").tooltipster({
    theme: ['tooltipster-shadow', 'tooltipster-shadow-rsm'],
    delay: 200,
    maxWidth: 360,
    side: 'bottom',
    functionInit: function (instance, helper) {
      const rawHref = $(helper.origin).attr("href");
      const { content } = buildExcerpt(rawHref);
      if (content) {
        setTooltipContent(instance, content);
      } else {
        setTooltipContent(
          instance,
          `<div class="rail-tip">${$(helper.origin).attr("data-tooltip") || ""}</div>`
        );
      }
    },
    functionReady: function (instance, helper) {
      const el = instance.elementTooltip ? instance.elementTooltip() : helper.tooltip;
      if (el) typesetMath(el instanceof $ ? el[0] : el);
    }
  });

  // Sidebar controls carry data-tip and use the interface tooltip (uitip.js),
  // not these reference previews.

  // Disabled dependency-lens menu items explain their absence with one of OUR
  // tooltips, not a native title. The items live in the singleton menu (portaled
  // to <body> on open), so bind them by role -- they exist at load even before a
  // reason is set -- and read the reason dynamically each open: an ENABLED item
  // carries no data-tooltip, so functionBefore returns false and shows nothing.
  $('#hr-menu-singleton [data-role="deplens-up"]:not(.tooltipstered), '
    + '#hr-menu-singleton [data-role="deplens-down"]:not(.tooltipstered)').tooltipster({
    theme: ['tooltipster-shadow', 'tooltipster-shadow-rsm'],
    delay: 200,
    minWidth: 100,
    maxWidth: 280,
    side: ['right', 'bottom', 'top'],
    trigger: 'custom',
    triggerOpen: { mouseenter: true, touchstart: true },
    triggerClose: { click: true, mouseleave: true, originClick: true, touchleave: true },
    functionBefore: function (instance, helper) {
      const text = $(helper.origin).attr("data-tooltip");
      if (!text) return false; // enabled item: no hint
      instance.content($(`<div class="rail-tip">${text}</div>`));
    },
  });
}


// The excerpt of a :calc:. Its number sits in the first row's info zone,
// stacked with that row's collapse button, so stripHandrail (which drops the
// whole info zone) would lose it. Keep the rows' info zones, emptied of their
// controls, so every row keeps the same width. The reasons are dropped, as the
// page shows them by default: hover previews are built at load, so following
// the reader's open reasons would show them only in some previews.
function calcPreview($calc) {
  const clone = copyOf($calc);
  clone.children(".hr-content-zone").children(".step").each((_, row) => {
    $(row).children(".hr-content-zone").children(":not(.statement)").remove();
    row.classList.remove("hr-collapsed");
  });
  clone.find(".hr-collapse-zone, .hr-menu-zone, .hr-border-zone, .hr-spacer-zone").remove();
  clone.find(".hr-collapse").remove();
  clone.find(".hr-info-zone").not(clone.find(".step").children(".hr-info-zone")).remove();
  clone
    .find("[data-menu-label], [tabindex]")
    .addBack()
    .removeAttr(
      "data-menu-label data-menu-link data-menu-code data-menu-collapse " +
        "data-menu-collapse-all data-menu-static-toggle data-start-collapsed tabindex"
    );
  return `<div class="calc-preview">${clone[0].outerHTML}</div>`;
}

// A copy of the affiliation or note that an author name or superscript points
// at, taken from the author details. The details are already rendered and
// escaped, so no HTML is read from the attribute.
function authorDetail(origin, key) {
  const value = origin.getAttribute(`data-${key}`);
  if (!value) return null;
  const source = $(origin)
    .closest(".author-block")
    .find(`.author-details [data-${key}]`)
    .filter((_, el) => el.getAttribute(`data-${key}`) === value)
    .first();
  if (!source.length) return null;
  const nodes = source.clone().contents();
  // The details start each entry with its number or symbol, which the
  // tooltip does not repeat.
  const first = nodes.first();
  return first.is("sup") ? nodes.slice(1) : nodes;
}

function stripHandrail(hr) {
  hr.find(".hr-collapse-zone").remove();
  hr.find(".hr-menu-zone").remove();
  hr.find(".hr-border-zone").remove();
  hr.find(".hr-spacer-zone").remove();
  hr.find(".hr-info-zone").remove();
}

function setTooltipContent(tt, content) {
  // add .manuscriptwrapper so that all CSS rules apply inside the tooltip
  const $content = $(`<div class="manuscriptwrapper">${content}</div>`);
  // The tooltip lives in the live DOM, so strip ids/data-nodeid from the cloned
  // subtree: otherwise it duplicates the source block's id, which breaks
  // getElementById and hash-based navigation to that block.
  $content.find("[id]").removeAttr("id");
  // Asides sit inside the block that calls them but are not part of its excerpt.
  $content.find(".aside").remove();
  $content.find("[data-nodeid]").removeAttr("data-nodeid");
  tt.content($content);
}
