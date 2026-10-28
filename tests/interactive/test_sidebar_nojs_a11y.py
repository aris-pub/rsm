"""Keyboard and no-JS behaviour for the reader sidebar, in the standalone build.

Standalone pages load onload with keys:false, so the single-key shortcuts
(keyboard.js) never run. These tests cover the keyboard paths that must work
anyway: opening a folded block (rsm-2xr), hiding the inert strip with scripting
off (rsm-s87), and the skip link past the strip (rsm-o2h).
"""

import re

import pytest
from playwright.sync_api import Browser, Page, expect

import rsm

pytestmark = pytest.mark.interactive

# A sidebar page (toc + proof give the strip its buttons) with one folded proof.
SRC = """\
# Keyboard Fold

:toc: {
  :view: tree
}
::

## A section
  {:label: sec-one}

Some lead-in prose before the proof.

:proof: {:collapsed:}

  :step: {:label: st-1} A first step, hidden on load. ::

  :step: :qed: Done. ::

::

Trailing prose after the proof.
"""


def _standalone(tmp_path):
    html = rsm.build(SRC, handrails=True, lint=False, standalone=True, sidebar=True)
    out = tmp_path / "standalone.html"
    out.write_text(html)
    return out


def _ready(page: Page) -> None:
    page.wait_for_function("() => window.__rsmInitialized === true", timeout=10000)


def test_standalone_folded_block_opens_and_folds_by_keyboard(page: Page, tmp_path):
    out = _standalone(tmp_path)
    page.goto(out.as_uri(), wait_until="load")
    _ready(page)

    proof = page.locator(".proof.hr[data-start-collapsed]")
    expect(proof).to_have_class(re.compile(r"\bhr-collapsed\b"))

    # The fold control is a named button that announces the folded state.
    btn = proof.locator(":scope > .hr-collapse-zone > .hr-collapse")
    assert btn.evaluate("el => el.tagName") == "BUTTON"
    expect(btn).to_have_attribute("aria-expanded", "false")
    assert (btn.get_attribute("aria-label") or "").strip()
    assert btn.get_attribute("aria-controls")

    # Enter on the focused FOLDED block opens it; focus stays on the block.
    proof.evaluate("el => el.focus()")
    assert page.evaluate("() => document.activeElement.classList.contains('proof')")
    page.keyboard.press("Enter")
    expect(proof).not_to_have_class(re.compile(r"\bhr-collapsed\b"))
    assert page.evaluate("() => document.activeElement.classList.contains('proof')")
    expect(btn).to_have_attribute("aria-expanded", "true")

    # Enter on the now-open block does NOT fold it (Enter stays free there).
    page.keyboard.press("Enter")
    expect(proof).not_to_have_class(re.compile(r"\bhr-collapsed\b"))

    # It can be folded again from the fold button, reachable by Tab.
    btn.evaluate("el => el.focus()")
    page.keyboard.press("Space")
    expect(proof).to_have_class(re.compile(r"\bhr-collapsed\b"))
    expect(btn).to_have_attribute("aria-expanded", "false")

    # Space on the focused folded block opens it too.
    proof.evaluate("el => el.focus()")
    page.keyboard.press("Space")
    expect(proof).not_to_have_class(re.compile(r"\bhr-collapsed\b"))


def test_sidebar_strip_hidden_without_js(browser: Browser, tmp_path):
    out = _standalone(tmp_path)
    ctx = browser.new_context(java_script_enabled=False, viewport={"width": 1280, "height": 900})
    try:
        page = ctx.new_page()
        page.goto(out.as_uri(), wait_until="load")

        strip = page.locator(".rail-strip")
        assert strip.count() == 1, "the strip is still in the DOM"
        assert strip.evaluate("el => getComputedStyle(el).display") == "none"

        # html never gets has-rail with scripting off.
        assert not page.evaluate(
            "() => document.documentElement.classList.contains('has-rail')"
        )
        # No column margin reserved for the (absent) strip: the text uses the
        # normal centred column, not the rail offset.
        reserved = page.evaluate(
            "() => { const m = document.querySelector('main.manuscriptwrapper');"
            " return getComputedStyle(m).getPropertyValue('--rail-ml'); }"
        )
        assert reserved.strip() == "", reserved
    finally:
        ctx.close()


def test_skip_link_is_first_focusable_and_moves_focus(page: Page, tmp_path):
    out = _standalone(tmp_path)
    page.goto(out.as_uri(), wait_until="load")
    _ready(page)

    link = page.locator(".rsm-skip-link")
    assert link.count() == 1
    # Hidden until focused.
    assert link.evaluate("el => getComputedStyle(el).opacity") == "0"

    # The first Tab lands on the skip link, before the strip's buttons.
    page.keyboard.press("Tab")
    assert page.evaluate(
        "() => document.activeElement.classList.contains('rsm-skip-link')"
    )
    assert link.evaluate("el => getComputedStyle(el).opacity") == "1"

    # Activating it moves focus into the manuscript content, past the strip.
    page.keyboard.press("Enter")
    assert page.evaluate(
        "() => { const c = document.getElementById('rsm-content');"
        " return c === document.activeElement || c.contains(document.activeElement); }"
    )
