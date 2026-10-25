"""WCAG 2.1 AA checks for the reader sidebar (strip, panel views, phone bar)."""

import re

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
    page = serve_rsm_a11y(SIDEBAR_SRC, sidebar=True)
    v = _violations(page)
    assert not v, "\n" + _fmt(v)


@pytest.mark.parametrize("view", ["contents", "notation", "steps", "state", "pinned", "reading"])
def test_sidebar_view_wcag(serve_rsm_a11y, page, view):
    page.set_viewport_size({"width": 1400, "height": 900})
    page = serve_rsm_a11y(SIDEBAR_SRC, sidebar=True)
    page.click(f'.rail-strip-btn[data-view="{view}"]')
    page.wait_for_selector(".proof-rail.open", timeout=5000)
    page.mouse.move(900, 600)
    v = _violations(page)
    assert not v, "\n" + _fmt(v)


@pytest.mark.parametrize("view", ["document", "reading"])
def test_sidebar_phone_wcag(serve_rsm_a11y, page, view):
    page.set_viewport_size({"width": 375, "height": 812})
    page = serve_rsm_a11y(SIDEBAR_SRC, sidebar=True)
    page.click(f'.rail-strip-btn[data-view="{view}"]')
    page.wait_for_selector(".proof-rail.open", timeout=5000)
    v = _violations(page)
    assert not v, "\n" + _fmt(v)


# An 8-step proof whose steps form a chain, so step <1>'s prerequisite cone is
# just itself (plus the always-in-cone Goal) and steps <2>..<8> all fade.
STEPS_SRC = """\
# Eight Step Proof

:toc: {
  :view: tree
}
::

## Results
  {:label: sec-results}

:theorem: {:label: thm-x} A claim about $x$.::

:proof:
  :step: {:label: st-1} Step one, a base fact.::
  :step: {:label: st-2} Step two, by :ref:st-1::.::
  :step: {:label: st-3} Step three, by :ref:st-2::.::
  :step: {:label: st-4} Step four, by :ref:st-3::.::
  :step: {:label: st-5} Step five, by :ref:st-4::.::
  :step: {:label: st-6} Step six, by :ref:st-5::.::
  :step: {:label: st-7} Step seven, by :ref:st-6::.::
  :step: :qed: Done by :ref:st-7::.::
::

Trailing prose so the proof can scroll fully into the reading band.
Trailing prose so the proof can scroll fully into the reading band.
"""


def _rgb(s):
    nums = [float(x) for x in re.findall(r"[\d.]+", s)]
    return tuple(nums[:3])


def _lin(ch):
    s = ch / 255
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def _luminance(rgb):
    r, g, b = (_lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(a, b):
    la, lb = _luminance(a), _luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _composite(fill, panel, opacity):
    # The faded label is painted at its effective opacity over the panel, so its
    # on-screen colour is that blend, not the raw fill.
    return tuple(opacity * f + (1 - opacity) * p for f, p in zip(fill, panel))


# For each faded step node, read the label colour, the label's effective opacity
# (its own opacity times every ancestor's, which captures a faded node group),
# and the panel background, so the test can reproduce the painted colour exactly.
_MEASURE_FADED = """() => {
  const panel = getComputedStyle(
    document.querySelector('.proof-rail.active')).backgroundColor;
  const faded = [...document.querySelectorAll(
    '.rail-map svg.toc-tree .toc-node.toc-faded')];
  return {
    panel,
    nodes: faded.map((n) => {
      const label = n.querySelector('.toc-secnum');
      let op = 1, el = label;
      while (el && el.nodeType === 1) {
        op *= parseFloat(getComputedStyle(el).opacity || '1');
        el = el.parentNode;
      }
      return {
        fill: getComputedStyle(label).fill,
        opacity: op,
        text: label.textContent,
      };
    }),
  };
}"""


def _force_theme(page, theme):
    page.evaluate(
        "(t) => { const c = document.documentElement.classList;"
        " c.remove('light-theme', 'dark-theme'); c.add(t + '-theme'); }",
        theme,
    )


def _pin_first_step(page):
    # Steps (map) is the default proof view; clicking the proof's first step pins
    # its (small) prerequisite cone, so the later steps rest faded.
    page.click('.rail-strip-btn[data-view="steps"]')
    page.evaluate(
        """() => {
            const step = [...document.querySelectorAll('.proof[data-nodeid] .step')]
                .find((s) => !s.closest('.calc'));
            step.scrollIntoView({ block: 'center' });
            step.click();
        }"""
    )
    page.wait_for_selector(
        ".rail-map svg.toc-tree .toc-node.current-step", timeout=5000
    )
    page.wait_for_function(
        "() => document.querySelectorAll("
        "'.rail-map svg.toc-tree .toc-node.toc-faded').length > 0",
        timeout=5000,
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_proof_steps_faded_node_labels_meet_ui_contrast(serve_rsm_a11y, page, theme):
    """WCAG 1.4.11 (UI component contrast): in the Proof > Steps map with step
    <1> current, steps <2>..<8> fade but stay clickable controls, so every faded
    node label must keep >= 3:1 against the panel, in both themes."""
    page.set_viewport_size({"width": 1400, "height": 900})
    page = serve_rsm_a11y(STEPS_SRC, sidebar=True)
    _force_theme(page, theme)
    _pin_first_step(page)

    data = page.evaluate(_MEASURE_FADED)
    assert data["nodes"], "expected faded step nodes with step <1> current"
    panel = _rgb(data["panel"])

    for node in data["nodes"]:
        painted = _composite(_rgb(node["fill"]), panel, node["opacity"])
        ratio = _contrast(painted, panel)
        assert ratio >= 3.0, (
            f"{theme}: faded label {node['text']!r} has {ratio:.2f}:1 against the "
            f"panel, below the 3:1 UI-contrast floor "
            f"(fill={node['fill']}, opacity={node['opacity']:.3f}, panel={data['panel']})"
        )

    # The current path stays distinct: the current step is not among the faded.
    current_faded = page.evaluate(
        "() => document.querySelector("
        "'.rail-map svg.toc-tree .toc-node.current-step')"
        ".classList.contains('toc-faded')"
    )
    assert not current_faded, "the current step must not be faded"


def test_sidebar_notation_pane_wcag(serve_rsm_a11y, page):
    page.set_viewport_size({"width": 1400, "height": 900})
    page = serve_rsm_a11y(SIDEBAR_SRC, sidebar=True)
    page.click('.rail-strip-btn[data-view="notation"]')
    page.wait_for_selector(".rail-notation-input", timeout=5000)
    page.mouse.move(900, 600)
    v = _violations(page)
    assert not v, "\n" + _fmt(v)
