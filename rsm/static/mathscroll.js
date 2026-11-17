// mathscroll.js
//
// A display equation wider than its column scrolls inside its content zone.
// While a zone overflows, it gets tabindex=0, role=region and a label, so
// keyboard users can Tab to it and scroll it with the arrow keys. Zones that fit
// get none of these, so equations that fit add no Tab stop.

import { mathIdle } from './libraries.js';

const ZONES = '.mathblock > .hr-content-zone';

let observer = null;
const observed = new Set();

export function zoneOverflows(zone) {
  return zone.scrollWidth > zone.clientWidth;
}

function label(zone) {
  const number = zone.parentElement?.querySelector(':scope > .hr-info-zone .eqn-number');
  const text = number ? number.textContent.trim() : '';
  return text ? `Equation ${text}, scrolls horizontally` : 'Equation, scrolls horizontally';
}

function update(zone) {
  if (zoneOverflows(zone)) {
    zone.setAttribute('tabindex', '0');
    zone.setAttribute('role', 'region');
    zone.setAttribute('aria-label', label(zone));
  } else {
    zone.removeAttribute('tabindex');
    zone.removeAttribute('role');
    zone.removeAttribute('aria-label');
  }
}

export function refresh(root = document) {
  root.querySelectorAll(ZONES).forEach(update);
}

// Safe to call again after the DOM changes: zones seen before are not observed
// twice.
export async function setup(root = document) {
  if (!observer && typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver((entries) => entries.forEach((e) => update(e.target)));
  }
  // Studio replaces the page HTML on each re-render. Zones removed with the old
  // HTML are unobserved so that the observer does not keep them in memory.
  observed.forEach((zone) => {
    if (!zone.isConnected) {
      observer.unobserve(zone);
      observed.delete(zone);
    }
  });
  root.querySelectorAll(ZONES).forEach((zone) => {
    if (observer && !observed.has(zone)) {
      observer.observe(zone);
      observed.add(zone);
    }
  });
  refresh(root);
  // Typesetting and web fonts change how wide an equation is without changing
  // the size of its zone, so the ResizeObserver does not fire for them.
  await mathIdle();
  refresh(root);
  if (document.fonts) {
    document.fonts.ready.then(() => refresh(root));
  }
}
