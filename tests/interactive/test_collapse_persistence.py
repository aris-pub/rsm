"""Interactive regression: a reader's collapse choices persist across reload.

handrails.js writes each block's collapsed state to localStorage and replays it
on load. This must hold for *every* collapsible handrail, including section
headings (which carry no data-nodeid) and the unlabeled blocks (document title,
auto-generated ToC and bibliography), not just the labeled content blocks.

This lives in the interactive (behavioral) suite, not the visual one: the thing
under test is *state surviving a reload*, which a screenshot diff cannot see.
The collapsed *appearance* is already covered by the visual snapshots
(test_states / test_nesting); duplicating it here would test the wrong thing.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

# Every block the reader can collapse by clicking its chevron, in document order
# (stable for a given build), so the Nth entry before reload is the Nth after.
_COLLAPSIBLE = """
  const blocks = [...document.querySelectorAll('.hr')].filter(h =>
    !h.closest('.rsm-source') &&
    h.querySelector(':scope > .hr-collapse-zone .hr-collapse'));
"""

_COLLAPSE_ALL = "() => {" + _COLLAPSIBLE + """
  for (const h of blocks) {
    if (!h.classList.contains('hr-collapsed'))
      h.querySelector(':scope > .hr-collapse-zone .hr-collapse').click();
  }
  return blocks.length;
}"""

_FLAGS = "() => {" + _COLLAPSIBLE + r"""
  return blocks.map(h => ({
    collapsed: h.classList.contains('hr-collapsed'),
    heading: h.classList.contains('heading'),
    text: (h.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 40),
  }));
}"""


def _load(page: Page, server: str) -> None:
    page.goto(f"{server}/collapse-persist.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)


def test_section_heading_collapse_persists(page: Page, interactive_server: str):
    """The original bug: a section heading carries no data-nodeid, so collapsing
    a whole section did not survive a reload."""
    _load(page, interactive_server)
    heading = page.locator("section#sec-alpha > .heading.hr")
    heading.locator(":scope > .hr-collapse-zone .hr-collapse").click()
    assert page.evaluate(
        "() => document.querySelector('section#sec-alpha > .heading.hr')"
        ".classList.contains('hr-collapsed')"
    )
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    assert page.evaluate(
        "() => document.querySelector('section#sec-alpha > .heading.hr')"
        ".classList.contains('hr-collapsed')"
    ), "section heading collapse did not persist across reload"


def test_every_collapsible_block_persists(page: Page, interactive_server: str):
    """Collapse every clickable block, reload, and every one must stay collapsed."""
    _load(page, interactive_server)
    n = page.evaluate(_COLLAPSE_ALL)
    assert n > 0, "fixture exposes no collapsible blocks"
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    flags = page.evaluate(_FLAGS)
    dropped = [f for f in flags if not f["collapsed"]]
    assert not dropped, (
        f"{len(dropped)}/{len(flags)} blocks did not persist collapsed; "
        f"dropped: {[(f['heading'], f['text']) for f in dropped]}"
    )
