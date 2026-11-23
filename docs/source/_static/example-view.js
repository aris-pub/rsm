// The Desktop and Phone buttons above each example's page. The selected button
// names the layout that the page shows: RSM pages take their phone layout
// below 768 px. Desktop puts the page under its source at full width; Phone
// brings back the side-by-side layout, or narrows a page that is already
// under its source to a phone's width.
const PHONE_BELOW = 768;

function frameWidth(wrap) {
  return wrap.querySelector(".rsm-example-iframe").getBoundingClientRect().width;
}

function mark(wrap) {
  const phone = frameWidth(wrap) < PHONE_BELOW;
  for (const b of wrap.querySelectorAll(".rsm-viewswitch button")) {
    b.setAttribute("aria-pressed", String((b.dataset.view === "phone") === phone));
  }
}

function markAll() {
  for (const wrap of document.querySelectorAll(".rsm-iframe-wrap")) mark(wrap);
}

document.addEventListener("click", (event) => {
  const button = event.target.closest(".rsm-viewswitch button");
  if (!button) return;
  const wrap = button.closest(".rsm-iframe-wrap");
  const example = wrap.closest(".rsm-example");
  const desktop = button.dataset.view === "desktop";
  example.classList.toggle("desktop-view", desktop);
  // A page that is under its source on its own has no side-by-side layout to
  // go back to, so Phone narrows it instead.
  const stacked = example.classList.contains("stacked") || getComputedStyle(example).gridTemplateColumns.split(" ").length < 2;
  wrap.classList.toggle("phone-view", !desktop && stacked);
  mark(wrap);
});

document.addEventListener("DOMContentLoaded", markAll);
window.addEventListener("resize", markAll);
