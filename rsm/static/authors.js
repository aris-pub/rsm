// authors.js
//
// Shortens an author list set with :author-display-first: and
// :author-display-last:. The HTML holds every name, so the list is shortened
// here and readers without JavaScript see all authors.

export function setup(root) {
  for (const more of (root || document).querySelectorAll(".author-names > .author-more[hidden]")) {
    const names = more.parentElement;
    names.classList.add("is-shortened");
    more.hidden = false;
    more.querySelector("button").addEventListener("click", () => {
      names.classList.remove("is-shortened");
      more.remove();
    });
  }
}
