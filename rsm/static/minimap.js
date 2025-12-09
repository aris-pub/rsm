// minimap.js
//
// Table of contents and floating minimap.
//

export function setup() {

  // Table of contents
  const items = document.querySelectorAll('ul.contents li.item');
  const num_items = items.length;
  items.forEach((item, idx) => {
    let percent = (idx + 1) / num_items * 100;
    item.addEventListener('mouseenter', () => { highlightMinimap(percent, "mouse") });
    item.querySelectorAll("a.reference").forEach(
      a => a.addEventListener('focus', () => { highlightMinimap(percent, "mouse") })
    );
  });

  // Floating minimap
  window.addEventListener('scroll', () => {
    const toc_mm = document.querySelector(".toc-wrapper > .minimap");
    const float_mm = document.querySelector(".float-minimap-wrapper > .minimap");
    if (!toc_mm || !float_mm) return;
    if (withinView(toc_mm, false)) {
      float_mm.classList.add("hide");
    } else {
      float_mm.classList.remove("hide");
    };
  });

  const mm = document.querySelector(".float-minimap-wrapper > .minimap");
  const sections = Array.from(document.querySelectorAll('section'));
  window.addEventListener('scroll', () => {
    if (!mm) return;

    const isHidden = mm.classList.contains("hide") || getComputedStyle(mm).display == "none" || getComputedStyle(mm.parentElement).display == "none";
    if (isHidden) return;

    const lastInViewport = sections.findLast(sec => withinView(sec, true));
    const circle = document.querySelector(`#mm-${lastInViewport?.id}`)
    let percent;
    if (circle) {
      const circle_rect = circle.getBoundingClientRect();
      const mm_rect = mm.getBoundingClientRect();
      percent = (circle_rect.bottom - mm_rect.top + 12) / mm.offsetHeight * 100;
    } else {
      percent = 0;
    };
    highlightMinimap(percent, 'scroll');
  });

}


function withinView(el, top = true) {
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
  const rect = el.getBoundingClientRect();
  if (top) {
    return rect.top < viewportHeight / 2 && rect.bottom > 0;
  } else {
    return rect.top < viewportHeight && rect.bottom > 0;
  };
};


function highlightMinimap(percent, name) {
  document.getElementById(`stop-follow-${name}-1`).setAttribute("offset", `${percent}%`);
  document.getElementById(`stop-follow-${name}-2`).setAttribute("offset", `${percent}%`);
}
