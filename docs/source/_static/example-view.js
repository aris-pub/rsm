// The Desktop and Phone buttons above each example's result. Phone narrows the
// frame to a phone's width, so the page inside it takes its phone layout.
document.addEventListener("click", (event) => {
  const button = event.target.closest(".rsm-viewswitch button");
  if (!button) return;
  const wrap = button.closest(".rsm-iframe-wrap");
  const phone = button.dataset.view === "phone";
  wrap.classList.toggle("phone-view", phone);
  for (const b of wrap.querySelectorAll(".rsm-viewswitch button")) {
    b.setAttribute("aria-pressed", String(b === button));
  }
});
