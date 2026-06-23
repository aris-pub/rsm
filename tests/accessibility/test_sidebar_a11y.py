"""WCAG 2.1 AA checks for the two-scope floating sidebar and notation pane."""

import pytest
from axe_playwright_python.sync_playwright import Axe

pytestmark = pytest.mark.accessibility

SIDEBAR_SRC = """\
# Sidebar Accessibility

:toc: {
  :view: tree
}
::

## One
  {:label: sec-one}

:notation:
  \\eig $\\lambda$ eigenvalue
::

Inline use of $\\eig$ in the prose.

:theorem: {:label: thm-x} A claim about $\\eig$.::

:proof:
  :step: {:label: st-1} First.::
  :step: {:label: st-2} Then by :ref:st-1::.::
  :step: :qed: Done by :ref:st-2::.::
::

## Two
  {:label: sec-two}

See :ref:thm-x::.
"""


def _violations(page):
    return Axe().run(page).response["violations"]


def _fmt(violations):
    lines = []
    for v in violations:
        targets = ", ".join(
            (n["target"][0] if n.get("target") else "?") for n in v["nodes"][:6]
        )
        lines.append(f"[{v['impact']}] {v['id']}: {v['help']}  ->  {targets}")
    return "\n".join(lines)


def test_sidebar_default_wcag(serve_rsm_a11y, page):
    page = serve_rsm_a11y(SIDEBAR_SRC)
    v = _violations(page)
    assert not v, "\n" + _fmt(v)


def test_sidebar_notation_pane_wcag(serve_rsm_a11y, page):
    # The notation subtab lives in the desktop sidebar's sub-tabs, which are
    # hidden below the 1320px drawer breakpoint (the rail becomes a bottom sheet
    # whose sub-tabs are display:none in the default peek state). Force a desktop
    # viewport so the sub-tabs are present and clickable.
    page.set_viewport_size({"width": 1400, "height": 900})
    page = serve_rsm_a11y(SIDEBAR_SRC)
    page.click('.rail-subtabs-document .rail-tab[data-view="notation"]')
    page.wait_for_selector(".rail-notation-input", timeout=5000)
    v = _violations(page)
    assert not v, "\n" + _fmt(v)
