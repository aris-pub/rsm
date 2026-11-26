// authors.js
//
// The author block has two states, closed and open, kept in data-authors on
// .author-block. braiid.css lays out each state: closed shows the short name
// list (set with :author-display-first: and :author-display-last:) and the
// summary label, open shows every name and the details. The handrail's
// collapse chevron, the "N more" and "Show fewer" pills and the summary label
// all switch the same state. Without JavaScript the attribute is never set, so
// every name and all the details show and the controls stay hidden.

import { openHandrail, closeHandrail } from "./handrails.js";

const BLOCK = ".author-block";

// A block with no hidden names and no details has nothing to open, so it gets
// no state.
function hasTwoStates(block) {
  return !!block.querySelector(".author-hidden-names, .author-details");
}

export function setup(root) {
  for (const block of (root || document).querySelectorAll(BLOCK)) {
    if (block.hasAttribute("data-authors") || !hasTwoStates(block)) continue;
    block.setAttribute("data-authors", "closed");
  }
  setupClicks();
}

// The handrail inside the block, when the page has handrails.
function handrailOf(block) {
  return block.querySelector(":scope > .hr");
}

// handrails.js calls this for the author block's handrail, so the chevron and
// the menu's Collapse item switch the same state as the pills.
export function authorBlockOf(hr) {
  const block = hr.parentElement;
  return block && block.matches(`${BLOCK}[data-authors]`) ? block : null;
}

export function isOpen(block) {
  return block.getAttribute("data-authors") === "open";
}

export function setOpen(block, open) {
  block.setAttribute("data-authors", open ? "open" : "closed");
}

// Go through the handrail when there is one, so that its chevron and its menu
// label stay in step.
function toggle(block) {
  const hr = handrailOf(block);
  const open = !isOpen(block);
  if (hr) (open ? openHandrail : closeHandrail)(hr);
  else setOpen(block, open);
}

let clicksAttached = false;
function setupClicks() {
  if (clicksAttached) return;
  clicksAttached = true;
  document.addEventListener("click", (ev) => {
    const control = ev.target.closest(
      `${BLOCK} .author-more-button, ${BLOCK} .author-summary`
    );
    if (!control) return;
    const block = control.closest(`${BLOCK}[data-authors]`);
    if (block) toggle(block);
  });
}
