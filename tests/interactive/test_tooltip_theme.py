"""The reference tooltip must use BRAIID's card, not tooltipster's default dark
frame. braiid.css styles the tooltip inside @layer base; tooltipster's CSS is
loaded in a lower @layer vendor so the base layer wins in every build mode
(rsm-3y7)."""

import pytest
from playwright.sync_api import Page

import rsm

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

FIXTURE_SRC = (
    "# Tooltip theme\n\n"
    ":theorem: {:label: thm-x}\n\n"
    "  For every graph on $n$ vertices the edge count is at most $n(n-1)/2$.\n\n"
    "::\n\n"
    "See :ref:thm-x:: for the bound.\n"
)

# A detached probe styled with the BRAIID tooltip tokens: its computed values are
# what the tooltip box should match, in either theme, without hardcoding colors.
PROBE_JS = """() => {
  const p = document.createElement('div');
  p.style.background = 'var(--surface-page)';
  p.style.border = 'var(--border-thin) solid var(--border-primary)';
  p.style.borderRadius = 'var(--radius-xl)';
  document.body.appendChild(p);
  const cs = getComputedStyle(p);
  const out = {bg: cs.backgroundColor, bw: cs.borderTopWidth,
               bc: cs.borderTopColor, br: cs.borderTopLeftRadius};
  p.remove();
  return out;
}"""

BOX_JS = """() => {
  const b = document.querySelector('.tooltipster-box');
  const cs = getComputedStyle(b);
  return {bg: cs.backgroundColor, bw: cs.borderTopWidth,
          bc: cs.borderTopColor, br: cs.borderTopLeftRadius};
}"""

# BRAIID renders the tooltip as a plain card with no pointer. The vendored shadow
# theme would draw one, so guard against it coming back (rsm-3y7).
ARROW_JS = """() => {
  const a = document.querySelector('.tooltipster-arrow');
  if (!a) return {present: false, display: null, h: 0};
  const r = a.getBoundingClientRect();
  return {present: true, display: getComputedStyle(a).display, h: Math.round(r.height)};
}"""


def _open_tooltip(page: Page):
    ref = page.locator('.manuscript a.reference[href="#thm-x"]').first
    ref.scroll_into_view_if_needed()
    ref.hover()
    page.wait_for_selector(".tooltipster-box", state="visible", timeout=3000)
    page.wait_for_timeout(200)


@pytest.mark.parametrize("dark", [False, True])
def test_tooltip_box_uses_braiid_card(page: Page, interactive_server: str, dark: bool):
    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto(f"{interactive_server}/tooltip-theme.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    if dark:
        page.eval_on_selector("html", "h => h.classList.add('dark-theme')")

    _open_tooltip(page)
    want = page.evaluate(PROBE_JS)
    got = page.evaluate(BOX_JS)
    assert got == want, f"dark={dark}: tooltip box {got} != BRAIID card {want}"

    arrow = page.evaluate(ARROW_JS)
    assert arrow["display"] == "none", f"dark={dark}: tooltip should have no pointer, got {arrow}"


@pytest.mark.parametrize("dark", [False, True])
def test_tooltip_box_uses_braiid_card_standalone(page: Page, tmp_path, dark: bool):
    """The same must hold in the standalone build, where tooltipster CSS is
    inlined into the vendor layer rather than linked (rsm-3y7)."""
    html = rsm.build(FIXTURE_SRC, handrails=True, lint=False, standalone=True)
    out = tmp_path / "standalone.html"
    out.write_text(html)

    page.set_viewport_size({"width": 1280, "height": 720})
    page.goto(out.as_uri(), wait_until="load")
    page.wait_for_function(RSM_READY, timeout=10_000)
    if dark:
        page.eval_on_selector("html", "h => h.classList.add('dark-theme')")

    _open_tooltip(page)
    want = page.evaluate(PROBE_JS)
    got = page.evaluate(BOX_JS)
    assert got == want, f"dark={dark}: standalone tooltip box {got} != BRAIID card {want}"

    arrow = page.evaluate(ARROW_JS)
    assert arrow["display"] == "none", f"dark={dark}: standalone tooltip should have no pointer, got {arrow}"
