"""Visual regression for proof-step number alignment under nesting.

Every step's box must stay flush at the content column regardless of nesting
depth (.hr-shift-1 pins it), so step numbers land on one right-hand column at
every depth and the focus highlight leaves no transparent band before the
number. These assert the rendered geometry, which depends on braiid.css, so
they guard the layout against regressing to the per-depth-offset drift.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

# Collect, for each step's number, its rendered left edge and .subproof depth.
_COLLECT = """() => {
  const rows = [];
  for (const sn of document.querySelectorAll('.hr-info-zone .step-number')) {
    if (sn.closest('.rsm-source')) continue;
    const r = sn.getBoundingClientRect();
    if (r.width === 0) continue;
    const step = sn.closest('.step');
    const proof = step.closest('.proof');
    let depth = 0, node = step;
    while (node && node !== proof) {
      if (node.classList && node.classList.contains('subproof')) depth++;
      node = node.parentElement;
    }
    rows.push({ depth, left: Math.round(r.left) });
  }
  return rows;
}"""


def _load(page: Page, server: str) -> None:
    page.set_viewport_size({"width": 1440, "height": 1100})
    page.goto(f"{server}/nested_steps.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def test_step_numbers_share_one_column(page: Page, interactive_server: str):
    _load(page, interactive_server)
    rows = page.evaluate(_COLLECT)
    assert rows, "no visible step numbers found"
    depths = {r["depth"] for r in rows}
    assert {0, 1, 2, 3} <= depths, f"fixture should reach depth 3; got depths {sorted(depths)}"
    lefts = {r["left"] for r in rows}
    assert max(lefts) - min(lefts) <= 1, (
        f"step numbers drift off the column with depth: distinct lefts {sorted(lefts)}"
    )


def test_focus_highlight_has_no_band(page: Page, interactive_server: str):
    """Activating any block must not leave a transparent gap between its
    content-zone highlight and the number column."""
    _load(page, interactive_server)
    worst = page.evaluate("""() => {
      const blocks = [...document.querySelectorAll('.hr.hr-offset')]
        .filter(el => !el.closest('.rsm-source') && !el.classList.contains('subproof'));
      let worst = -1e9;
      for (const el of blocks) {
        const cz = el.querySelector(':scope > .hr-content-zone');
        const iz = el.querySelector(':scope > .hr-info-zone');
        if (!cz || !iz) continue;
        el.classList.add('active');
        const gap = Math.round(iz.getBoundingClientRect().left - cz.getBoundingClientRect().right);
        el.classList.remove('active');
        if (gap > worst) worst = gap;
      }
      return worst;
    }""")
    assert worst <= 2, f"focus highlight leaves a {worst}px transparent band before the number"
