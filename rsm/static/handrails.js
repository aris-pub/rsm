// handrails.js
//
// Basic user interactions, mostly dealing with handrails and their menus.
//

export function setup() {

  // Handrail menu: show and hide
  document.querySelectorAll(".hr > .hr-menu-zone > .hr-menu").forEach(menu => {
    menu.addEventListener("mouseleave", function () {
      closeMenu(menu);
    });
  });
  document.querySelectorAll(".hr > .hr-border-zone > .hr-border-dots").forEach(dots => {
    dots.addEventListener("click", function (ev) {
      const siblings = Array.from(this.parentElement.parentElement.children);
      const target = siblings.find(sibling => sibling.classList.contains("hr-menu-zone"));
      if (target) { target.style.display = "block" };
    });
  });

  // Handrail menu: link button
  document.querySelectorAll(".hr > .hr-menu-zone > .hr-menu > .hr-menu-item.link:not(.disabled)").forEach(btn => {
    btn.addEventListener("click", ev => copyLink(ev.target));
  });

  // Handrail menu: source button
  document.querySelectorAll(".hr > .hr-menu-zone > .hr-menu > .hr-menu-item:has(.icon.code):not(.disabled)").forEach(btn => {
    btn.addEventListener("click", ev => showSource(ev.target));
  });

  // Handrail menu: collapse and collapse-all buttons
  document.querySelectorAll(".hr > .hr-collapse-zone > .hr-collapse").forEach(btn => {
    btn.addEventListener("click", ev => toggleHandrail(ev.target));
  });
  document.querySelectorAll(".hr.step > .hr-menu-zone > .hr-menu > .hr-menu-item.collapse-subproof:not(.disabled)").forEach(btn => {
    btn.addEventListener("click", ev => toggleHandrail(ev.target));
  });
  document.querySelectorAll(".hr.step > .hr-menu-zone > .hr-menu > .hr-menu-item.collapse-steps:not(.disabled)").forEach(btn => {
    btn.addEventListener("click", ev => collapseAll(ev.target, true));
  });
  document.querySelectorAll(".hr.proof > .hr-menu-zone > .hr-menu > .hr-menu-item.collapse-steps:not(.disabled)").forEach(btn => {
    btn.addEventListener("click", ev => collapseAll(ev.target, false));
  });

  // Set height of offset handrails' borders
  const resizeObserver = new ResizeObserver(updateHeight);
  document.querySelectorAll('.hr.hr-offset > .hr-content-zone').forEach(el => resizeObserver.observe(el));

}


function closeMenu(menu) {
  menu.parentElement.style.display = "none";
  menu.querySelectorAll("& > .hr-menu-item").forEach(it => it.classList.remove("active"));
}


function updateHeight(entries) {
  for (const entry of entries) {
    const hr = entry.target.parentElement;
    const elementsToResize = hr.querySelectorAll('& > .hr-border-zone, & > .hr-spacer-zone, & > .hr-info-zone');
    elementsToResize.forEach(el => { el.style.height = `${entry.contentRect.height}px`; })
  }
};


export function toggleHandrail(target) {
  const hr = target.closest(".hr");
  if (hr.classList.contains("hr-collapsed")) { openHandrail(hr) }
  else { closeHandrail(hr) };
};


function openHandrail(hr) {
  hr.classList.remove("hr-collapsed");
  const rest = getRest(hr);
  rest.forEach(el => { el.classList.remove("hide"); });
  const icon = hr.querySelector("& .icon.expand");
  if (!icon) return;
  icon.classList.remove("expand");
  icon.classList.add("collapse");
  icon.innerHTML = `
                    <svg width="8" height="14" viewBox="0 0 8 14" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
                      <path d="M1 1L7 7L1 13" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    `;
  const item_text = icon.nextElementSibling;
  if (item_text && item_text.classList.contains("hr-menu-item-text")) { item_text.textContent = "Collapse" };
}


function closeHandrail(hr) {
  hr.classList.add("hr-collapsed");
  const rest = getRest(hr);
  rest.forEach(el => { el.classList.add("hide"); });
  const icon = hr.querySelector("& .icon.collapse");
  if (!icon) return;
  icon.classList.remove("collapse");
  icon.classList.add("expand");
  icon.innerHTML = `
                    <svg width="14" height="8" viewBox="0 0 14 8" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
                      <path d="M1 1L7 7L13 1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    `;
  const item_text = icon.nextElementSibling;
  if (item_text && item_text.classList.contains("hr-menu-item-text")) { item_text.textContent = "Expand" };
}


function getRest(hr) {
  let rest;
  if (hr.classList.contains("hr-labeled")) {
    rest = hr.querySelectorAll("& > .hr-content-zone > :not(.hr-label)");
  } else if (hr.classList.contains("step")) {
    rest = hr.querySelectorAll("& > .hr-content-zone > :not(.statement)");
  } else {
    rest = Array.from(hr.parentElement.children).filter(el => { return el !== hr });
  };
  return rest;
}


export function collapseAll(target, withinSubproof = true) {
  let qry;
  if (withinSubproof) {
    qry = "& > .hr-content-zone > .subproof > .hr-content-zone > .step:has(.subproof)";
  } else {
    qry = "& > .hr-content-zone > .step:has(.subproof)";
  }

  const hr = target.closest(".hr");
  const ex_icon = hr.querySelector("& .icon.expand-all");
  if (ex_icon) {
    hr.querySelectorAll(qry).forEach(st => openHandrail(st));
    ex_icon.classList.remove("expand-all");
    ex_icon.classList.add("collapse-all");
    ex_icon.innerHTML = `
                    <svg width="9" height="9" viewBox="5 5 14 14" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
                      <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
                      <path d="M7 7l5 5l-5 5" />
                      <path d="M13 7l5 5l-5 5" />
                    </svg>
                    `;
    const item_text = ex_icon.nextElementSibling;
    if (item_text && item_text.classList.contains("hr-menu-item-text")) { item_text.textContent = "Collapse all" };
    return;
  }

  const co_icon = hr.querySelector("& .icon.collapse-all");
  if (co_icon) {
    hr.querySelectorAll(qry).forEach(st => closeHandrail(st));
    co_icon.classList.remove("collapse-all");
    co_icon.classList.add("expand-all");
    co_icon.innerHTML = `
                    <svg width="9" height="9" viewBox="5 5 14 14" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
                      <path d="M7 7l5 5l5 -5" />
                      <path d="M7 13l5 5l5 -5" />
                    </svg>
                    `;
    const item_text = co_icon.nextElementSibling;
    if (item_text && item_text.classList.contains("hr-menu-item-text")) { item_text.textContent = "Expand all" };
    return;
  }

};

async function copyLink(target) {
  let url;
  try {
    // If we're in an iframe and same-origin, use parent URL
    if (window.self !== window.parent) {
      url = window.parent.location.href.split('#')[0];
    } else {
      url = document.location.href.split('#')[0];
    }
  } catch (error) {
    // Cross-origin iframe, fall back to iframe URL
    url = document.location.href.split('#')[0];
  }

  const hr = target.closest(".hr")
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

  const icon = document.createElement("span");
  icon.className = `icon ${style}`;
  toast.appendChild(icon);

  switch (style) {
    case "success":
      icon.innerHTML = `
        <svg width="18" height="18" viewBox="2 2 20 20" fill="#3C4952" stroke-width="0" xmlns="http://www.w3.org/2000/svg">
          <path d="M17 3.34a10 10 0 1 1 -14.995 8.984l-.005 -.324l.005 -.324a10 10 0 0 1 14.995 -8.336zm-1.293 5.953a1 1 0 0 0 -1.32 -.083l-.094 .083l-3.293 3.292l-1.293 -1.292l-.094 -.083a1 1 0 0 0 -1.403 1.403l.083 .094l2 2l.094 .083a1 1 0 0 0 1.226 0l.094 -.083l4 -4l.083 -.094a1 1 0 0 0 -.083 -1.32z" />
        </svg>
        `
      break;
    case "error":
      icon.innerHTML = `
        <svg width="18" height="18" viewBox="2 2 20 20" fill="#3C4952" stroke-width="0" xmlns="http://www.w3.org/2000/svg">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M17 3.34a10 10 0 1 1 -14.995 8.984l-.005 -.324l.005 -.324a10 10 0 0 1 14.995 -8.336zm-6.489 5.8a1 1 0 0 0 -1.218 1.567l1.292 1.293l-1.292 1.293l-.083 .094a1 1 0 0 0 1.497 1.32l1.293 -1.292l1.293 1.292l.094 .083a1 1 0 0 0 1.32 -1.497l-1.292 -1.293l1.292 -1.293l.083 -.094a1 1 0 0 0 -1.497 -1.32l-1.293 1.292l-1.293 -1.292l-.094 -.083z" />
        </svg>
        `
      break;
  }

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


function showSource(target) {
  const hr = target.closest(".hr");
  const source = hr.getAttribute("data-rsm-source");

  if (!source) {
    launchToast("No source available for this element.", "error");
    return;
  }

  // Create modal
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

  // Close button handlers
  const closeBtn = modal.querySelector(".close-modal");
  const copyBtn = modal.querySelector(".copy-source");

  const closeModal = () => {
    modal.remove();
  };

  closeBtn.addEventListener("click", closeModal);

  // Close on click outside
  modal.addEventListener("click", (ev) => {
    if (ev.target === modal) {
      closeModal();
    }
  });

  // Close on ESC key
  const escHandler = (ev) => {
    if (ev.key === "Escape") {
      closeModal();
      document.removeEventListener("keydown", escHandler);
    }
  };
  document.addEventListener("keydown", escHandler);

  // Copy button
  copyBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(source);
      launchToast("Source copied to clipboard.", "success");
    } catch (error) {
      launchToast("Could not copy source.", "error");
    }
  });
};
