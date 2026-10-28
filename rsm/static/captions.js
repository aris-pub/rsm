// captions.js
//
// Captions of every captioned block (figure, widget, video, table) go in the
// margin column when it fits (margin.js), top-aligned with their block, and
// stay under the block otherwise. Either way the caption's handrail is drawn
// in the left gutter beside the block, spanning the block's height, never in
// the margin: the caption keeps its gutter zones (menu dots, rail) in the DOM,
// and braiid.css places them with the --cap-rail-* offsets set here.

import { addMarginItem } from "./margin.js";

const CAPTIONS = ".manuscript :is(figure, .table-wrapper) > figcaption.hr";

let listening = false;

export function setup(root = document) {
  for (const cap of root.querySelectorAll(CAPTIONS)) {
    cap.classList.add("rsm-cap-linked");
    addMarginItem(cap.parentElement, cap);
  }
  if (listening) return;
  listening = true;
  document.addEventListener("rsm:margin-layout", alignRails);
  // A wide table scrolls sideways inside its wrapper, and its caption with it.
  document.addEventListener(
    "scroll",
    (ev) => {
      if (ev.target.matches && ev.target.matches(".table-wrapper")) alignRails();
    },
    { capture: true, passive: true },
  );
}

function alignRails() {
  const rem = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
  for (const cap of document.querySelectorAll("figcaption.rsm-cap-linked")) {
    const block = cap.parentElement.getBoundingClientRect();
    const box = cap.getBoundingClientRect();
    if (!box.height && !box.width) continue;
    const zone = cap.querySelector(":scope > .hr-border-zone")?.offsetWidth || rem;
    // A nested caption's gutter sits three zones left of its block, like every
    // other offset handrail.
    const x = block.left - (cap.classList.contains("hr-offset") ? 3 * zone : 0);
    cap.style.setProperty("--cap-rail-x", x - box.left + "px");
    cap.style.setProperty("--cap-rail-y", block.top - box.top + "px");
    cap.style.setProperty("--cap-rail-h", block.height + "px");
  }
}
