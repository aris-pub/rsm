// The two switches above each example's page.
//
// Wide / Narrow: the selected button names the layout that the page shows (RSM
// pages take their narrow layout below 768 px). Wide puts the page under its
// source at full width; Narrow brings back the side-by-side layout, or narrows
// a page that is already under its source to a phone's width.
//
// Mouse / Touch: Touch sets the touch class on the page in the frame, which
// gives it the touch look (braiid.css, handrails.js), as on a phone or tablet.
const NARROW_BELOW = 768;

function frameOf(wrap) {
  return wrap.querySelector(".rsm-example-iframe");
}

function press(wrap, attr, value) {
  for (const b of wrap.querySelectorAll(`.rsm-viewswitch button[${attr}]`)) {
    b.setAttribute("aria-pressed", String(b.getAttribute(attr) === value));
  }
}

function mark(wrap) {
  const frame = frameOf(wrap);
  press(wrap, "data-width", frame.getBoundingClientRect().width < NARROW_BELOW ? "narrow" : "wide");
  const doc = frame.contentDocument;
  if (doc) press(wrap, "data-input", doc.documentElement.classList.contains("touch") ? "touch" : "mouse");
}

function markAll() {
  for (const wrap of document.querySelectorAll(".rsm-iframe-wrap")) mark(wrap);
}

document.addEventListener("click", (event) => {
  const button = event.target.closest(".rsm-viewswitch button");
  if (!button) return;
  const wrap = button.closest(".rsm-iframe-wrap");
  if (button.dataset.width) {
    const example = wrap.closest(".rsm-example");
    const wide = button.dataset.width === "wide";
    example.classList.toggle("desktop-view", wide);
    // A page that is under its source on its own has no side-by-side layout to
    // go back to, so Narrow narrows it instead.
    const stacked = example.classList.contains("stacked") ||
      getComputedStyle(example).gridTemplateColumns.split(" ").length < 2;
    wrap.classList.toggle("phone-view", !wide && stacked);
  } else {
    const doc = frameOf(wrap).contentDocument;
    doc.documentElement.classList.toggle("touch", button.dataset.input === "touch");
  }
  mark(wrap);
});

window.addEventListener("load", markAll);
window.addEventListener("resize", markAll);
