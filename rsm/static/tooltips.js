// tooltips.js
//
// Setup tooltips on <a> tags.
//

import { typesetMath } from "./libraries.js";

// Tabler pin, outline (not pinned) and filled (pinned).
const PIN_ICON =
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 4.5l-4 4l-4 1.5l-1.5 1.5l7 7l1.5 -1.5l1.5 -4l4 -4"/><path d="M9 15l-4.5 4.5"/><path d="M14.5 4l5.5 5.5"/></svg>';
const PIN_FILLED_ICON =
  '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M15.113 3.21l.094 .083l5.5 5.5a1 1 0 0 1 -1.175 1.59l-3.172 3.171l-1.424 3.797a1 1 0 0 1 -.158 .277l-.07 .08l-1.5 1.5a1 1 0 0 1 -1.32 .082l-.095 -.083l-2.793 -2.792l-3.793 3.792a1 1 0 0 1 -1.497 -1.32l.083 -.094l3.792 -3.793l-2.792 -2.793a1 1 0 0 1 -.083 -1.32l.083 -.094l1.5 -1.5a1 1 0 0 1 .258 -.187l.098 -.042l3.796 -1.425l3.171 -3.17a1 1 0 0 1 1.497 -1.26z"/></svg>';
const PIN_LABEL = "Pin to the sidebar";
const PINNED_LABEL = "Pinned in the sidebar";

// The href and title of the excerpt currently pinned in the sidebar, or null.
let pinnedTarget = null;
let pinnedTitle = "";

// What is pinned now, for shareview.js to put in a view link.
export function currentPin() {
  return pinnedTarget ? { target: pinnedTarget, title: pinnedTitle } : null;
}

// Build the inert excerpt shown for a reference: a clone of the target with
// handrails stripped. Shared by the hover tooltip and the pin action so both
// show exactly the same thing. Returns { content, error }.
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
    clone = $t.clone();
    clone.find(".note-backlink").remove();
    const zone = clone.find(".hr-content-zone").first();
    content = `<div class="note-preview">${(zone[0] ? zone : clone).html()}</div>`;
  } else if (["P", "LI"].includes(tag)) {
    // A paragraph's or list item's handrail wraps it from OUTSIDE the element,
    // so its own innerHTML carries no handrail chrome to strip.
    content = `<div>${$t.html()}</div>`;
  } else if (tag === "FIGURE") {
    // A figure keeps its handrail chrome INSIDE itself: the figcaption is its
    // own hr, with the menu dots (in .hr-border-zone) and data-menu-*
    // attributes. Take the HTML from a stripped clone, like the block branches
    // below, so a pinned or previewed figure is just the image and caption,
    // with no interactive menu dots or leftover menu metadata.
    clone = $t.clone();
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
    } else if (classes.contains("proof")) {
      clone = $t.clone();
      stripHandrail(clone);
      content = clone.html();
    } else if (["math", "algorithm"].some((c) => classes.contains(c))) {
      clone = $t.clone();
      stripHandrail(clone);
      content = clone.html();
    } else if (
      ["paragraph", "mathblock", "theorem", "lemma", "corollary", "example",
       "exercise", "proposition", "problem", "porism", "remark", "definition",
       "bibitem"].some((c) => classes.contains(c))
    ) {
      clone = $t.clone();
      stripHandrail(clone);
      content = clone.html();
    }
  }
  return { content: content || "", error: content ? null : "unsupported" };
}

// The pin control in a reference preview: an icon in the preview's top-right
// corner. Offered only when the page has the sidebar (`--sidebar`), the place a
// pinned excerpt goes.
function pinBar(href, title) {
  if (!document.querySelector(".proof-rail")) return "";
  const h = (href || "").replaceAll('"', "&quot;");
  const t = (title || "").replaceAll('"', "&quot;");
  const on = !!pinnedTarget && href === pinnedTarget;
  const label = on ? PINNED_LABEL : PIN_LABEL;
  return (
    '<div class="ref-pin-bar">' +
    `<button type="button" class="ref-pin" data-pin-target="${h}" ` +
    `data-pin-title="${t}" aria-label="${label}" data-tip="${label}" ` +
    `aria-pressed="${on}"${on ? " data-pinned" : ""}>` +
    (on ? PIN_FILLED_ICON : PIN_ICON) + "</button></div>"
  );
}

// Repaint every visible preview's pin control after the pinned excerpt changes.
function paintPins() {
  for (const btn of document.querySelectorAll(".ref-pin")) {
    const on = !!pinnedTarget && btn.dataset.pinTarget === pinnedTarget;
    const label = on ? PINNED_LABEL : PIN_LABEL;
    btn.toggleAttribute("data-pinned", on);
    btn.setAttribute("aria-pressed", String(on));
    btn.setAttribute("aria-label", label);
    btn.dataset.tip = label;
    btn.innerHTML = on ? PIN_FILLED_ICON : PIN_ICON;
  }
}

// Pin the block an href points at: rebuild its excerpt from the target (so it
// does not depend on a closing tooltip's DOM) and dispatch rail:pin, which
// prooftree.js (owner of the rail) handles. Used by the preview's pin control
// and by the handrail menu's Pin item. Returns false if nothing could be pinned.
// A transient pin (from a shared view link) does not save the open sidebar
// view, so the recipient's own settings stay as they were.
export function pinTarget(href, title, origin = document, { transient = false } = {}) {
  const { content } = buildExcerpt(href);
  if (!content) return false;
  // The excerpt lands in the live rail, so strip ids/data-nodeid (as the
  // tooltip path does) or it duplicates the source block's id and breaks
  // getElementById and hash navigation.
  const tmp = document.createElement("div");
  tmp.innerHTML = content;
  tmp.querySelectorAll("[id]").forEach((e) => e.removeAttribute("id"));
  tmp
    .querySelectorAll("[data-nodeid]")
    .forEach((e) => e.removeAttribute("data-nodeid"));
  // The Pinned card shows the block's label as its header, so drop the block's
  // own rendered label from the body to avoid showing it twice. Only the
  // leading one (this block's label). Nested labels stay. Mirrors the State
  // view, which likewise strips .hr-label from its clone.
  if (title) {
    const leadLabel = tmp.querySelector(".hr-label");
    if (leadLabel) leadLabel.remove();
  }
  pinnedTarget = href;
  pinnedTitle = title || "";
  origin.dispatchEvent(
    new CustomEvent("rail:pin", {
      bubbles: true,
      detail: { html: tmp.innerHTML, title: title || "", target: href, transient },
    })
  );
  paintPins();
  return true;
}

// One delegated handler for every preview's pin control. A click on the control
// of the excerpt that is already pinned shows it (opens the Pinned view)
// rather than pinning it again.
let pinDelegated = false;
function setupPinDelegation() {
  if (pinDelegated) return;
  pinDelegated = true;
  document.addEventListener("click", (ev) => {
    const btn = ev.target.closest && ev.target.closest(".ref-pin");
    if (!btn) return;
    if (btn.hasAttribute("data-pinned")) {
      document.dispatchEvent(
        new CustomEvent("rail:show", { detail: { view: "pinned", open: true } })
      );
      return;
    }
    pinTarget(btn.dataset.pinTarget, btn.dataset.pinTitle || "", btn);
  });
  document.addEventListener("rail:unpin", () => {
    pinnedTarget = null;
    pinnedTitle = "";
    paintPins();
  });
}

// The reference preview. Footnote markers use the same options, apart from how
// a touch opens them (see tapToPreview).
const PREVIEW_OPTIONS = {
  theme: ['tooltipster-shadow', 'tooltipster-shadow-rsm'],
  delay: 200,
  minWidth: 100,
  maxWidth: 500,
  // Interactive so the reader can move into the preview to click its pin
  // button without it closing on the way.
  interactive: true,
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
    // Title the excerpt like the block names itself ("Equation (1)"), not by
    // the link text ("(1)"), falling back to the link text.
    const target = document.getElementById((rawHref || "").replace(/^#/, ""));
    const noteNumber = helper.origin.classList.contains("note-marker")
      ? helper.origin.dataset.noteNumber
      : "";
    const title = (
      (noteNumber && `Note ${noteNumber}`) ||
      (target && target.getAttribute("data-menu-label")) ||
      helper.origin.textContent ||
      ""
    ).trim().replace(/\.$/, "");
    setTooltipContent(instance, pinBar(rawHref, title) + content);
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
// tap anywhere else closes the preview (tooltipster's tap close). A mouse click
// or Enter still follows the link at once. `el` must already have its tooltip.
export function tapToPreview(el) {
  if (el.dataset.tapPreview) return;
  el.dataset.tapPreview = "true";
  let touched = false;
  el.addEventListener("pointerdown", (ev) => {
    touched = ev.pointerType === "touch";
  });
  el.addEventListener("click", (ev) => {
    if (!touched) return;
    touched = false;
    if ($(el).tooltipster("status").open) return;
    ev.preventDefault();
    $(el).tooltipster("open");
  });
}

export function createTooltips() {
  setupPinDelegation();
  $(".manuscriptwrapper a.reference:not(.external):not(.tooltipstered)").tooltipster(PREVIEW_OPTIONS);

  // Footnote markers get the same preview as references. Aside markers do not,
  // since an aside is shown next to its call. Touch opens the preview through
  // tapToPreview, not tooltipster's touchstart, so the tap does not also jump
  // to the notes list.
  const $markers = $(
    '.manuscriptwrapper a.note-marker[data-note-kind="note"]:not(.tooltipstered)'
  );
  $markers.tooltipster({
    ...PREVIEW_OPTIONS,
    triggerOpen: { mouseenter: true },
    triggerClose: { click: true, mouseleave: true, originClick: true, tap: true },
  });
  $markers.each((_, el) => tapToPreview(el));


  $(".manuscriptwrapper .author-names sup[data-tooltip]:not(.tooltipstered)").tooltipster({
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
      let text = $(helper.origin).attr("data-tooltip");
      setTooltipContent(instance, text);
    },
  });

  // DAG nodes: show the link target's rendered excerpt (math and all), the same
  // way reference tooltips do, so the graph is not the odd one out. Falls back to
  // the plain-text statement in data-tooltip when the target cannot be excerpted.
  $(".proof-rail a.toc-node:not(.tooltipstered)").tooltipster({
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
  $content.find("[data-nodeid]").removeAttr("data-nodeid");
  tt.content($content);
}
