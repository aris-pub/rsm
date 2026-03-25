// handrails.js
//
// Basic user interactions, mostly dealing with handrails and their menus.
//

let singletonMenu = null;
let activeHr = null;

export function setup() {

  singletonMenu = document.getElementById("hr-menu-singleton");

  // Dots click: populate singleton menu from handrail data attrs, show it
  document.querySelectorAll(".hr > .hr-border-zone > .hr-border-dots").forEach(dots => {
    dots.addEventListener("click", function () {
      const hr = this.closest(".hr");
      if (activeHr === hr) {
        hideMenu();
        return;
      }
      showMenuFor(hr);
    });
  });

  // Singleton menu item handlers
  if (singletonMenu) {
    const menu = singletonMenu.querySelector(".hr-menu");
    menu.addEventListener("mouseleave", hideMenu);

    const linkItem = singletonMenu.querySelector('[data-role="link"]');
    if (linkItem) linkItem.addEventListener("click", () => { if (activeHr) copyLink(activeHr); });

    const codeItem = singletonMenu.querySelector('[data-role="code"]');
    if (codeItem) codeItem.addEventListener("click", () => { if (activeHr) showSource(activeHr); });

    const collapseItem = singletonMenu.querySelector('[data-role="collapse"]');
    if (collapseItem) collapseItem.addEventListener("click", () => { if (activeHr) toggleHandrail(activeHr); });

    const collapseAllItem = singletonMenu.querySelector('[data-role="collapse-all"]');
    if (collapseAllItem) {
      collapseAllItem.addEventListener("click", () => {
        if (!activeHr) return;
        const withinSubproof = activeHr.classList.contains("step");
        collapseAll(activeHr, withinSubproof);
      });
    }
  }

  // Collapse zone click (this is separate from the menu — it's the left-side toggle)
  document.querySelectorAll(".hr > .hr-collapse-zone > .hr-collapse").forEach(btn => {
    btn.addEventListener("click", ev => toggleHandrail(ev.target));
  });

  // Set height of offset handrails' borders
  const resizeObserver = new ResizeObserver(updateHeight);
  document.querySelectorAll('.hr.hr-offset > .hr-content-zone').forEach(el => resizeObserver.observe(el));

}


function showMenuFor(hr) {
  if (!singletonMenu) return;

  activeHr = hr;
  const label = hr.getAttribute("data-menu-label") || "";
  const collapse = hr.getAttribute("data-menu-collapse");
  const collapseAll = hr.getAttribute("data-menu-collapse-all");
  const link = hr.getAttribute("data-menu-link");
  const code = hr.getAttribute("data-menu-code");

  // Configure label
  const labelEl = singletonMenu.querySelector('[data-role="label"]');
  const labelSep = singletonMenu.querySelector('[data-role="label-sep"]');
  if (labelEl) {
    labelEl.textContent = label;
    labelEl.parentElement.style.display = label ? "" : "none";
  }
  if (labelSep) labelSep.style.display = label ? "" : "none";

  // Configure collapse items
  configureItem(singletonMenu.querySelector('[data-role="collapse"]'), collapse);
  configureItem(singletonMenu.querySelector('[data-role="collapse-all"]'), collapseAll);

  // Show/hide collapse separator based on whether any collapse item is visible
  const collapseSep = singletonMenu.querySelector('[data-role="collapse-sep"]');
  if (collapseSep) {
    const anyCollapse = collapse || collapseAll;
    collapseSep.style.display = anyCollapse ? "" : "none";
  }

  // Configure link and code items
  configureItem(singletonMenu.querySelector('[data-role="link"]'), link);
  configureItem(singletonMenu.querySelector('[data-role="code"]'), code);

  // Move singleton into the handrail's menu zone
  const zone = hr.querySelector(":scope > .hr-menu-zone");
  if (zone) {
    zone.appendChild(singletonMenu);
    singletonMenu.style.display = "";
    zone.style.display = "block";
  }
}


function configureItem(el, value) {
  if (!el) return;
  if (!value) {
    el.style.display = "none";
    el.classList.remove("disabled");
    return;
  }
  el.style.display = "";
  if (value === "disabled") {
    el.classList.add("disabled");
  } else {
    el.classList.remove("disabled");
  }
}


function hideMenu() {
  if (!singletonMenu) return;
  singletonMenu.style.display = "none";
  singletonMenu.querySelectorAll(".hr-menu-item").forEach(it => it.classList.remove("active"));
  if (activeHr) {
    const zone = activeHr.querySelector(":scope > .hr-menu-zone");
    if (zone) zone.style.display = "";
  }
  activeHr = null;
}


function updateHeight(entries) {
  for (const entry of entries) {
    const hr = entry.target.parentElement;
    const elementsToResize = hr.querySelectorAll(':scope > .hr-border-zone, :scope > .hr-spacer-zone, :scope > .hr-info-zone');
    elementsToResize.forEach(el => { el.style.height = `${entry.contentRect.height}px`; })
  }
};


export function toggleHandrail(target) {
  const hr = target.closest ? target.closest(".hr") : target;
  if (hr.classList.contains("hr-collapsed")) { openHandrail(hr) }
  else { closeHandrail(hr) };
};


function openHandrail(hr) {
  hr.classList.remove("hr-collapsed");
  const rest = getRest(hr);
  rest.forEach(el => { el.classList.remove("hide"); });
  const icon = hr.querySelector(":scope > .hr-collapse-zone .icon.expand");
  if (!icon) return;
  icon.classList.remove("expand");
  icon.classList.add("collapse");
  const use = icon.querySelector("use");
  if (use) use.setAttribute("href", "#hr-icon-collapse");
}


function closeHandrail(hr) {
  hr.classList.add("hr-collapsed");
  const rest = getRest(hr);
  rest.forEach(el => { el.classList.add("hide"); });
  const icon = hr.querySelector(":scope > .hr-collapse-zone .icon.collapse");
  if (!icon) return;
  icon.classList.remove("collapse");
  icon.classList.add("expand");
  const use = icon.querySelector("use");
  if (use) use.setAttribute("href", "#hr-icon-expand");
}


function getRest(hr) {
  let rest;
  if (hr.classList.contains("hr-labeled")) {
    rest = hr.querySelectorAll(":scope > .hr-content-zone > :not(.hr-label)");
  } else if (hr.classList.contains("step")) {
    rest = hr.querySelectorAll(":scope > .hr-content-zone > :not(.statement)");
  } else {
    rest = Array.from(hr.parentElement.children).filter(el => { return el !== hr });
  };
  return rest;
}


export function collapseAll(target, withinSubproof = true) {
  let qry;
  if (withinSubproof) {
    qry = ":scope > .hr-content-zone > .subproof > .hr-content-zone > .step:has(.subproof)";
  } else {
    qry = ":scope > .hr-content-zone > .step:has(.subproof)";
  }

  const hr = target.closest ? target.closest(".hr") : target;

  // Check current state of the collapse-all icon in the singleton
  const collapseAllItem = singletonMenu ? singletonMenu.querySelector('[data-role="collapse-all"]') : null;
  const icon = collapseAllItem ? collapseAllItem.querySelector(".icon") : null;

  if (icon && icon.classList.contains("expand-all")) {
    hr.querySelectorAll(qry).forEach(st => openHandrail(st));
    icon.classList.remove("expand-all");
    icon.classList.add("collapse-all");
    const use = icon.querySelector("use");
    if (use) use.setAttribute("href", "#hr-icon-collapse-all");
    const text = icon.nextElementSibling;
    if (text) text.textContent = "Collapse all";
  } else if (icon) {
    hr.querySelectorAll(qry).forEach(st => closeHandrail(st));
    icon.classList.remove("collapse-all");
    icon.classList.add("expand-all");
    const use = icon.querySelector("use");
    if (use) use.setAttribute("href", "#hr-icon-expand-all");
    const text = icon.nextElementSibling;
    if (text) text.textContent = "Expand all";
  }
};

async function copyLink(hr) {
  let url;
  try {
    if (window.self !== window.parent) {
      url = window.parent.location.href.split('#')[0];
    } else {
      url = document.location.href.split('#')[0];
    }
  } catch (error) {
    url = document.location.href.split('#')[0];
  }

  let needs_anchor = true;
  let anchor = "";
  let link = "";
  if (!hr.classList.contains("heading")) {
    anchor = hr.id;
  } else {
    const section = hr.closest("section");
    if (!section.classList.contains("level-1")) {
      anchor = section.id;
    } else {
      needs_anchor = false;
    }
  }
  if (needs_anchor && !anchor) {
    launchToast("Could not copy link.", "error");
    return;
  }
  link = `${url}#${anchor}`
  try {
    await navigator.clipboard.writeText(link);
    launchToast("Link copied to clipboard.", "success");
  } catch (error) {
    launchToast("Could not copy link.", "error");
  }
};


function makeToast(text, style) {
  const toast = document.createElement("div");
  toast.className = `toast ${style}`

  const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  icon.setAttribute("class", `icon ${style}`);
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttribute("href", `#hr-icon-${style}`);
  icon.appendChild(use);
  toast.appendChild(icon);

  const msg = document.createElement("span");
  msg.className = "msg";
  msg.innerText = text;
  toast.appendChild(msg);

  const spacer = document.createElement("span");
  spacer.className = "spacer";
  toast.appendChild(spacer);

  const close = document.createElement("span");
  close.className = "icon close";
  close.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
          <path d="M13 1L1 13M1 1L13 13" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        `
  close.addEventListener("click", ev => toast.remove());
  toast.appendChild(close);

  const bg = document.createElement("div");
  bg.className = "bg";
  toast.appendChild(bg);

  return toast;
}


function launchToast(text, style = "information") {
  const toast = makeToast(text, style);
  document.querySelector(".manuscriptwrapper").appendChild(toast);
  setTimeout(() => { toast.remove(); }, 5000);
};


function showSource(hr) {
  const start = hr.getAttribute("data-source-start");
  const end = hr.getAttribute("data-source-end");
  const sourceDiv = document.querySelector(".rsm-source");

  if (!start || !end || !sourceDiv) {
    launchToast("No source available for this element.", "error");
    return;
  }

  const source = sourceDiv.textContent.slice(parseInt(start), parseInt(end));

  const modal = document.createElement("div");
  modal.className = "rsm-source-modal";
  modal.innerHTML = `
    <div class="rsm-source-modal-content">
      <div class="rsm-source-modal-actions">
        <button class="rsm-source-modal-icon-button copy-source" title="Copy">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
            <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
          </svg>
        </button>
        <button class="rsm-source-modal-icon-button close-modal" title="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 6 6 18"/>
            <path d="m6 6 12 12"/>
          </svg>
        </button>
      </div>
      <div class="rsm-source-modal-body">
        <pre>${source.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
  modal.style.display = "block";

  const closeBtn = modal.querySelector(".close-modal");
  const copyBtn = modal.querySelector(".copy-source");

  const closeModal = () => {
    modal.remove();
  };

  closeBtn.addEventListener("click", closeModal);

  modal.addEventListener("click", (ev) => {
    if (ev.target === modal) {
      closeModal();
    }
  });

  const escHandler = (ev) => {
    if (ev.key === "Escape") {
      closeModal();
      document.removeEventListener("keydown", escHandler);
    }
  };
  document.addEventListener("keydown", escHandler);

  copyBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(source);
      launchToast("Source copied to clipboard.", "success");
    } catch (error) {
      launchToast("Could not copy source.", "error");
    }
  });
};
