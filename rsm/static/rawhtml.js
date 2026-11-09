// rawhtml.js
//
// An inline :rawhtml: is written as
//   <span class="rawhtml"><span class="rawhtml-alt" hidden>fallback</span>HTML</span>
// The page makes copies of its own content (reference previews, the pinned
// excerpt, the proof State view). In a copy the HTML is replaced by its
// fallback: a copy of a raw element such as a widget would be a second live
// widget. The copies are made in an inert <template>, where the raw elements
// are parsed but never created as live elements (no custom element
// constructor runs there).

// Replace the HTML of every :rawhtml: under root with its fallback, in place.
// A swapped one is marked, as a copy of a copy must keep its fallback.
function swapIn(root) {
  for (const el of root.querySelectorAll(".rawhtml:not([data-fallback])")) {
    const alt = el.querySelector(":scope > .rawhtml-alt");
    el.replaceChildren(...(alt ? alt.childNodes : []));
    el.setAttribute("data-fallback", "");
  }
}

// An HTML string with the HTML of every :rawhtml: replaced by its fallback.
export function withoutRawHtml(html) {
  if (!html || !html.includes("rawhtml")) return html;
  const t = document.createElement("template");
  t.innerHTML = html;
  swapIn(t.content);
  return t.innerHTML;
}

// A deep copy of el, like el.cloneNode(true), with the HTML of every
// :rawhtml: replaced by its fallback.
export function cloneWithoutRawHtml(el) {
  if (!el.matches(".rawhtml") && !el.querySelector(".rawhtml")) {
    return el.cloneNode(true);
  }
  const t = document.createElement("template");
  t.innerHTML = el.outerHTML;
  swapIn(t.content);
  return document.importNode(t.content.firstElementChild, true);
}
