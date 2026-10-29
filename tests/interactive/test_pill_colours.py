"""rsm-wpv: the handrail dots pill takes its colours from the rail and the page.

The pill is the small rounded tab holding the three dots on a block's handrail.
It has four desktop states:

- block hovered, not active: the document's --surface-primary, subtle dots
- pill hovered, not active: --surface-hint
- block active: the rail's own colour (--handrail-active), dark dots
- active and pill hovered: a lighter shade of the rail colour, dark dots

The dots must keep at least 3:1 contrast against the pill in every state, in
both themes, for the default accent and for :accent: green. Colours are read
from the computed style and resolved to sRGB through a canvas (so color-mix()
and light-dark() results compare as plain pixels), then the WCAG contrast
ratio is computed from them.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"
MIN_CONTRAST = 3.0
STATES = ["block-hover", "pill-hover", "active", "active-pill-hover"]

# Resolve any CSS colour to [r, g, b] by painting it over the page background,
# which also composites a translucent colour the way the browser would.
RESOLVE_JS = """
window.__pillResolve = (css) => {
  const c = document.createElement('canvas');
  c.width = c.height = 1;
  const ctx = c.getContext('2d');
  ctx.fillStyle = getComputedStyle(document.body).backgroundColor;
  ctx.fillRect(0, 0, 1, 1);
  ctx.fillStyle = css;
  ctx.fillRect(0, 0, 1, 1);
  const d = ctx.getImageData(0, 0, 1, 1).data;
  return [d[0], d[1], d[2]];
};
"""

READ_JS = """() => {
  const thm = document.querySelector('.theorem.hr');
  const dots = thm.querySelector(':scope > .hr-border-zone > .hr-border-dots');
  const rect = thm.querySelector(':scope > .hr-border-zone > .hr-border-rect');
  const svg = dots.querySelector('svg');
  return {
    pill: window.__pillResolve(getComputedStyle(dots).backgroundColor),
    dots: window.__pillResolve(getComputedStyle(svg).color),
    rail: window.__pillResolve(getComputedStyle(rect).borderLeftColor),
  };
}"""


def _lum(rgb):
    def ch(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (ch(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _load(page: Page, server: str, accent: str, theme: str) -> None:
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/pill.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.evaluate(
        """({accent, theme}) => {
          const root = document.documentElement;
          root.classList.remove('dark-theme', 'light-theme');
          root.classList.add(theme === 'dark' ? 'dark-theme' : 'light-theme');
          if (accent !== 'default') {
            root.setAttribute('data-accent', accent);
            document.body.setAttribute('data-accent', accent);
          }
        }""",
        {"accent": accent, "theme": theme},
    )
    page.evaluate(RESOLVE_JS)


def _measure(page: Page, state: str) -> dict:
    thm = page.locator(".theorem.hr").first
    dots = thm.locator(":scope > .hr-border-zone > .hr-border-dots")
    content = thm.locator(":scope > .hr-content-zone")
    # A click on the content lands on the nested paragraph, which takes focus
    # itself, so focus the theorem directly to make it the active block.
    if state.startswith("active"):
        thm.focus()
    if state.endswith("pill-hover"):
        dots.hover()
    else:
        content.hover()
    return page.evaluate(READ_JS)


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("accent", ["default", "green"])
@pytest.mark.parametrize("state", STATES)
def test_dots_contrast(
    page: Page, interactive_server: str, accent: str, theme: str, state: str
):
    _load(page, interactive_server, accent, theme)
    m = _measure(page, state)
    ratio = _contrast(m["pill"], m["dots"])
    print(f"{state} {accent} {theme}: pill {m['pill']} dots {m['dots']} {ratio:.2f}:1")
    assert ratio >= MIN_CONTRAST, (
        f"{state}/{accent}/{theme}: dots {m['dots']} on pill {m['pill']} "
        f"is {ratio:.2f}:1, below {MIN_CONTRAST}:1"
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("accent", ["default", "green"])
def test_active_pill_matches_rail(
    page: Page, interactive_server: str, accent: str, theme: str
):
    _load(page, interactive_server, accent, theme)
    m = _measure(page, "active")
    assert m["pill"] == m["rail"], (
        f"{accent}/{theme}: active pill {m['pill']} differs from rail {m['rail']}"
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("accent", ["default", "green"])
def test_active_pill_hover_is_lighter_than_rail(
    page: Page, interactive_server: str, accent: str, theme: str
):
    _load(page, interactive_server, accent, theme)
    m = _measure(page, "active-pill-hover")
    assert _lum(m["pill"]) > _lum(m["rail"]), (
        f"{accent}/{theme}: hovered active pill {m['pill']} is not lighter "
        f"than the rail {m['rail']}"
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_hovered_pill_follows_surface_primary(
    page: Page, interactive_server: str, theme: str
):
    """A document that sets warm surfaces gets a warm pill, not a cool gray."""
    _load(page, interactive_server, "default", theme)
    page.evaluate(
        "() => document.documentElement.style.setProperty('--surface-primary', '#f3e9d6')"
    )
    m = _measure(page, "block-hover")
    assert m["pill"] == [0xF3, 0xE9, 0xD6], (
        f"{theme}: hovered pill {m['pill']} does not follow --surface-primary"
    )
