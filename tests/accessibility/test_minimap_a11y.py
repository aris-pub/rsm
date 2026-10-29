"""WCAG 2.1 AA checks for the document minimap (rsm/static/minimap.js).

The strip is checked at rest, hovered (label showing) and focused from the
keyboard, in both themes, at desktop and phone widths, with and without the
sidebar. Behaviour is covered by tests/interactive/test_minimap.py.
"""

import pytest
from axe_playwright_python.sync_playwright import Axe

pytestmark = pytest.mark.accessibility

SRC = """\
# Minimap Accessibility

## One
  {:label: sec-one}

Text in the first section.

### One point one
  {:label: sec-one-one}

More text.

## Two
  {:label: sec-two}

:theorem: {:label: thm-x} A claim.::

:proof:
  :step: {:label: st-1} First.::
  :step: :qed: Done by :ref:st-1::.::
::

## Three
  {:label: sec-three}

The end.
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


def _force_theme(page, theme):
    page.evaluate(
        "(t) => { const c = document.documentElement.classList;"
        " c.remove('light-theme', 'dark-theme'); c.add(t + '-theme'); }",
        theme,
    )
    page.wait_for_timeout(400)


def _focus_strip(page):
    for _ in range(40):
        page.keyboard.press("Tab")
        if page.evaluate("() => !!document.activeElement.closest('.rsm-minimap')"):
            page.keyboard.press("ArrowDown")
            return
    raise AssertionError("Tab never reached the minimap")


@pytest.mark.parametrize("sidebar", [True, False], ids=["sidebar", "plain"])
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("state", ["rest", "hover", "focus"])
def test_minimap_desktop_wcag(serve_rsm_a11y, page, theme, state, sidebar):
    page.set_viewport_size({"width": 1280, "height": 800})
    page = serve_rsm_a11y(SRC, sidebar=sidebar)
    assert page.locator(".rsm-minimap").count() == 1
    _force_theme(page, theme)
    if state == "hover":
        box = page.locator(".rsm-minimap-track").bounding_box()
        y = page.evaluate(
            "() => { const m = document.querySelector('.rsm-minimap-mark');"
            " const r = m.getBoundingClientRect(); return r.top + r.height / 2; }"
        )
        page.mouse.move(box["x"] + box["width"] / 2, y)
        assert page.locator(".rsm-minimap-tip").is_visible()
    elif state == "focus":
        _focus_strip(page)
    page.wait_for_timeout(400)
    v = _violations(page)
    assert not v, "\n" + _fmt(v)


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_minimap_phone_wcag(serve_rsm_a11y, page, theme):
    page.set_viewport_size({"width": 375, "height": 812})
    page = serve_rsm_a11y(SRC, sidebar=True)
    _force_theme(page, theme)
    page.evaluate("() => window.scrollBy(0, 100)")
    page.wait_for_timeout(200)
    v = _violations(page)
    assert not v, "\n" + _fmt(v)
