// uitip.js
//
// Interface tooltips: one small label for the controls of the reader interface
// (the sidebar strip and panel, the pin control in reference previews). They
// are deliberately distinct from the reference previews (tooltipster), which
// show manuscript content. A control opts in with data-tip="Label".
//
// The label shows after a short hover-intent delay, or at once on keyboard
// focus, and is linked to its control with aria-describedby. Strip buttons that
// are pressed (their view is open) need no label.

const SCOPE = [
  ".rail-strip [data-tip]",
  ".proof-rail [data-tip]",
  ".tooltipster-content .ref-pin[data-tip]",
].join(", ");

let wired = false;

export function setup() {
  if (wired) return;
  if (!document.querySelector(".rail-strip, .proof-rail")) return;
  wired = true;

  const tip = document.createElement("div");
  tip.className = "ui-tip";
  tip.id = "rsm-ui-tip";
  tip.setAttribute("role", "tooltip");
  document.body.appendChild(tip);

  let timer = null;
  let owner = null;

  function place(el) {
    const b = el.getBoundingClientRect();
    tip.style.left = "0px";
    tip.style.top = "0px";
    tip.classList.add("on");
    const w = tip.offsetWidth;
    const h = tip.offsetHeight;
    let x;
    let y;
    const inStrip = el.closest(".rail-strip");
    if (inStrip && !document.documentElement.classList.contains("rail-phone")) {
      // Desktop strip: beside the button, into the page.
      x = b.right + 10;
      y = b.top + (b.height - h) / 2;
    } else {
      x = b.left + (b.width - w) / 2;
      y = b.top - h - 8;
      if (y < 8) y = b.bottom + 8;
    }
    x = Math.max(8, Math.min(x, window.innerWidth - w - 8));
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  }

  function show(el, now) {
    clearTimeout(timer);
    timer = setTimeout(
      () => {
        const text = el.dataset.tip;
        if (!text || !el.isConnected) return;
        tip.textContent = text;
        owner = el;
        el.setAttribute("aria-describedby", tip.id);
        place(el);
      },
      now ? 0 : 350,
    );
  }

  function hide() {
    clearTimeout(timer);
    tip.classList.remove("on");
    if (owner) owner.removeAttribute("aria-describedby");
    owner = null;
  }

  const eligible = (el) =>
    el && !(el.closest(".rail-strip") && el.getAttribute("aria-pressed") === "true");

  document.addEventListener("mouseover", (ev) => {
    const el = ev.target.closest && ev.target.closest(SCOPE);
    if (el && eligible(el)) show(el, false);
    else if (owner && !owner.contains(ev.target)) hide();
  });
  document.addEventListener("focusin", (ev) => {
    const el = ev.target.closest && ev.target.closest(SCOPE);
    if (el && eligible(el) && el.matches(":focus-visible")) show(el, true);
    else hide();
  });
  document.addEventListener("focusout", hide);
  document.addEventListener("click", hide, true);
  document.addEventListener("keydown", (ev) => {
    if (ev.key === "Escape") hide();
  });
  window.addEventListener("scroll", hide, { passive: true });
}
