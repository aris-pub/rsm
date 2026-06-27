// tooltips.js
//
// Setup tooltips on <a> tags.
//

import { typesetMath } from "./libraries.js";

const PIN_ICON =
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 4.5l-4 4l-4 1.5l-1.5 1.5l7 7l1.5 -1.5l1.5 -4l4 -4"/><path d="M9 15l-4.5 4.5"/><path d="M14.5 4l5.5 5.5"/></svg>';

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

function pinBar(href, title) {
  const h = (href || "").replaceAll('"', "&quot;");
  const t = (title || "").replaceAll('"', "&quot;");
  return (
    '<div class="ref-pin-bar">' +
    `<button type="button" class="ref-pin" data-pin-target="${h}" ` +
    `data-pin-title="${t}" aria-label="Pin this beside the proof">` +
    PIN_ICON + "<span>Pin</span></button></div>"
  );
}

// One delegated handler: a click on any reference tooltip's pin button rebuilds
// the excerpt from the target (so it does not depend on the closing tooltip DOM)
// and dispatches rail:pin, which prooftree.js (owner of the rail) handles.
let pinDelegated = false;
function setupPinDelegation() {
  if (pinDelegated) return;
  pinDelegated = true;
  document.addEventListener("click", (ev) => {
    const btn = ev.target.closest && ev.target.closest(".ref-pin");
    if (!btn) return;
    const { content } = buildExcerpt(btn.dataset.pinTarget);
    if (!content) return;
    // The excerpt lands in the live rail, so strip ids/data-nodeid (as the
    // tooltip path does) or it duplicates the source block's id and breaks
    // getElementById and hash navigation.
    const tmp = document.createElement("div");
    tmp.innerHTML = content;
    tmp.querySelectorAll("[id]").forEach((e) => e.removeAttribute("id"));
    tmp
      .querySelectorAll("[data-nodeid]")
      .forEach((e) => e.removeAttribute("data-nodeid"));
    btn.dispatchEvent(
      new CustomEvent("rail:pin", {
        bubbles: true,
        detail: { html: tmp.innerHTML, title: btn.dataset.pinTitle || "" },
      })
    );
  });
}

export function createTooltips() {
  setupPinDelegation();
  $(".manuscriptwrapper a.reference:not(.external):not(.tooltipstered)").tooltipster({
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
      const title = (helper.origin.textContent || "").trim();
      setTooltipContent(instance, pinBar(rawHref, title) + content);
    },
    functionReady: function (instance, helper) {
      // The tooltip content is a clone of the target and can carry un-typeset
      // math (raw \(...\) inline or $$...$$ display); render it the same way the
      // body and the sidebar do, so tooltips are never the odd one out.
      const el = instance.elementTooltip ? instance.elementTooltip() : helper.tooltip;
      if (el) typesetMath(el instanceof $ ? el[0] : el);
    }
  });


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

  // Sidebar control labels: the same tooltipster mechanism as the body, with a
  // plain-text label taken from data-tooltip.
  $(".proof-rail [data-tooltip]:not(.tooltipstered)").tooltipster({
    theme: ['tooltipster-shadow', 'tooltipster-shadow-rsm'],
    // Rail controls are glanced past constantly; a longer hover-intent delay
    // keeps their hints from flashing up while the pointer just crosses the rail.
    delay: 500,
    // Cap the width: setTooltipContent wraps the label in .manuscriptwrapper,
    // which is width:100% up to the document column width, so without a maxWidth
    // a control hint stretches into a full-page banner (the body/author tooltips
    // both cap at 500; these are short labels, so a touch tighter).
    minWidth: 100,
    maxWidth: 360,
    side: 'bottom',
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
      // Rail control labels are short plain-text hints, not document content.
      // Keep them OUT of .manuscriptwrapper: its body font-size and width:100%
      // (up to the document column width) blow a one-line hint into a full-width
      // banner that overflows even a capped tooltip box. A light .rail-tip
      // wrapper carries the body font; tooltipster's maxWidth then wraps it.
      instance.content($(`<div class="rail-tip">${$(helper.origin).attr("data-tooltip")}</div>`));
    },
  });

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
