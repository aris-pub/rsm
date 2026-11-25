// The two switches above each example's page.
//
// Wide / Narrow: the selected button names the layout that the page shows (RSM
// pages take their narrow layout below 768 px). Wide puts the page under its
// source at full width; Narrow brings back the side-by-side layout, or narrows
// a page that is already under its source to a phone's width.
//
// Mouse / Touch: Touch sets the touch class on the page in the frame, which
// gives it the touch look (braiid.css, handrails.js). A page taller than a
// phone's or a tablet's screen then gets a frame of that screen's height and
// scrolls inside it, as on the device. A shorter page keeps its own height.
const NARROW_BELOW = 768;
// CSS heights of the screens of a common phone (390 x 844) and tablet (820 x 1180).
const PHONE_HEIGHT = 844;
const TABLET_HEIGHT = 1180;

// The frame's onload sizing (rsm_directive.py) caps the frame at _cap.
function fitDevice(wrap) {
  const frame = frameOf(wrap);
  const doc = frame.contentDocument;
  const touch = doc && doc.documentElement.classList.contains("touch");
  const narrow = frame.getBoundingClientRect().width < NARROW_BELOW;
  frame._cap = touch ? (narrow ? PHONE_HEIGHT : TABLET_HEIGHT) : undefined;
  if (frame._fit) frame._fit();
}

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

// Wrap / No wrap above each example's source.
document.addEventListener("click", (event) => {
  const button = event.target.closest(".rsm-wrapswitch button");
  if (!button) return;
  const code = button.closest(".rsm-example-code");
  code.classList.toggle("nowrap", button.dataset.wrap === "nowrap");
  for (const b of code.querySelectorAll(".rsm-wrapswitch button")) {
    b.setAttribute("aria-pressed", String(b === button));
  }
});

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
  fitDevice(wrap);
  mark(wrap);
});

window.addEventListener("load", markAll);
window.addEventListener("resize", markAll);
