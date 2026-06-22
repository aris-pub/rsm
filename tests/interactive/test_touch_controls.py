"""Interactive: handrail controls are usable on touch devices (no hover).

On desktop the collapse chevron and menu-dots live in the left gutter and appear
on :hover. Touch has no hover, so under @media (hover: none) and (pointer: coarse):

  - the per-block collapse chevron is dropped (collapse/expand moves into the
    dots menu, so every block carries a single control, not two);
  - the menu-dots are revealed at rest, opaque (a page-coloured background that
    breaks the vertical rule rather than sitting on top of it), with a >=24px
    invisible hit target.

Desktop keeps the chevron and the hover reveal.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

_PROBE = r"""() => {
  const hr = [...document.querySelectorAll('.hr')].find(e =>
    !e.closest('.rsm-source') &&
    e.querySelector(':scope > .hr-collapse-zone .hr-collapse') &&
    e.querySelector(':scope > .hr-border-zone .hr-border-dots'));
  if (!hr) return null;
  const c = hr.querySelector(':scope > .hr-collapse-zone .hr-collapse');
  const d = hr.querySelector(':scope > .hr-border-zone .hr-border-dots');
  const csd = getComputedStyle(d);
  const hit = getComputedStyle(d, '::before');
  const alpha = (col) => {
    const m = col.match(/rgba?\(([^)]+)\)/);
    if (!m) return 1;
    const p = m[1].split(',').map((s) => s.trim());
    return p.length === 4 ? parseFloat(p[3]) : 1;
  };
  return {
    hoverNone: matchMedia('(hover: none) and (pointer: coarse)').matches,
    chevronDisplay: getComputedStyle(c).display,
    dotsOpacity: +csd.opacity,
    dotsBgAlpha: alpha(csd.backgroundColor),
    dotsHit: { w: parseFloat(hit.width) || 0, h: parseFloat(hit.height) || 0 },
  };
}"""


@pytest.fixture
def touch_page(browser, interactive_server: str):
    ctx = browser.new_context(
        has_touch=True, is_mobile=True, viewport={"width": 390, "height": 844}
    )
    pg = ctx.new_page()
    pg.goto(f"{interactive_server}/sidebar.html")
    pg.wait_for_function(RSM_READY, timeout=10_000)
    yield pg
    ctx.close()


def test_touch_media_matches(touch_page: Page):
    """Sanity: the emulated context is actually a no-hover, coarse-pointer one."""
    assert touch_page.evaluate(
        "() => matchMedia('(hover: none) and (pointer: coarse)').matches"
    )


def test_chevron_dropped_on_touch(touch_page: Page):
    c = touch_page.evaluate(_PROBE)
    assert c, "no block with both controls found"
    assert c["chevronDisplay"] == "none", "the per-block collapse chevron must be hidden on touch"


def test_dots_break_the_rule_at_rest(touch_page: Page):
    c = touch_page.evaluate(_PROBE)
    assert c["dotsOpacity"] >= 0.9, "the dots are the block's control on touch; show them solid"
    assert c["dotsBgAlpha"] == 1, (
        "at rest the dots match the page background (opaque), breaking the rule"
    )


def test_dots_pill_appears_on_menu_open(touch_page: Page):
    """The visible rounded pill appears only while that block's menu is open: the
    background changes from the page colour (at rest) to the pill colour."""
    r = touch_page.evaluate(
        """() => {
        const hr = [...document.querySelectorAll('.hr')].find(e =>
          !e.closest('.rsm-source') &&
          e.querySelector(':scope > .hr-border-zone .hr-border-dots'));
        const d = hr.querySelector(':scope > .hr-border-zone .hr-border-dots');
        const rest = getComputedStyle(d).backgroundColor;
        d.dispatchEvent(new MouseEvent('click', {bubbles: true}));
        return { rest, open: getComputedStyle(d).backgroundColor,
                 radius: getComputedStyle(d).borderRadius };
    }"""
    )
    assert r["open"] != r["rest"], "the pill background should appear (change) when the menu opens"
    assert r["radius"] != "0px", "the open-menu pill is rounded"


def test_dots_hit_target_meets_24px(touch_page: Page):
    c = touch_page.evaluate(_PROBE)
    assert c["dotsHit"]["w"] >= 24 and c["dotsHit"]["h"] >= 24, (
        f"dots hit target too small: {c['dotsHit']}"
    )


# A block that collapses via its chevron but has NO build-time menu collapse item
# (headings, theorems, proofs are like this). On touch its chevron is hidden, so
# the menu must grow a Collapse item; on desktop it must not.
_OPEN_CHEVRON_BLOCK_MENU = """() => {
  const hr = [...document.querySelectorAll('.hr')].find(e =>
    !e.closest('.rsm-source') &&
    e.querySelector(':scope > .hr-collapse-zone .hr-collapse') &&
    e.querySelector(':scope > .hr-border-zone .hr-border-dots') &&
    (!e.getAttribute('data-menu-collapse') ||
     e.getAttribute('data-menu-collapse') === 'disabled'));
  if (!hr) return false;
  hr.querySelector(':scope > .hr-border-zone .hr-border-dots')
    .dispatchEvent(new MouseEvent('click', {bubbles: true}));
  return true;
}"""


def test_collapse_moves_into_menu_on_touch(touch_page: Page):
    """The chevron is hidden on touch, so its collapse/expand action must appear
    as a menu item for every chevron-collapsible block, even ones the build did
    not mark menu-collapsible."""
    assert touch_page.evaluate(_OPEN_CHEVRON_BLOCK_MENU), "no chevron-collapsible block found"
    expect(
        touch_page.locator('#hr-menu-singleton [data-role="collapse"]')
    ).to_be_visible()


def test_collapse_stays_off_the_menu_on_desktop(page: Page, interactive_server: str):
    """Mobile-only: on desktop such a block collapses via its chevron, so its dots
    menu does not gain a Collapse item."""
    page.goto(f"{interactive_server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    assert page.evaluate(_OPEN_CHEVRON_BLOCK_MENU), "no chevron-collapsible block found"
    expect(
        page.locator('#hr-menu-singleton [data-role="collapse"]')
    ).to_be_hidden()


def test_menu_opens_within_viewport_on_touch(touch_page: Page):
    """The dots sit near the left edge; the menu must open to the right so it
    does not clip off-screen (desktop opens it left into the gutter)."""
    opened = touch_page.evaluate(
        """() => {
        const hr = [...document.querySelectorAll('.hr')].find(e =>
          !e.closest('.rsm-source') &&
          e.querySelector(':scope > .hr-border-zone .hr-border-dots'));
        if (!hr) return false;
        hr.querySelector(':scope > .hr-border-zone .hr-border-dots')
          .dispatchEvent(new MouseEvent('click', {bubbles: true}));
        return true;
    }"""
    )
    assert opened, "no block with dots found"
    box = touch_page.evaluate(
        """() => {
        const m = document.querySelector('#hr-menu-singleton .hr-menu');
        const r = m.getBoundingClientRect();
        return { left: Math.round(r.left), right: Math.round(r.right), vw: window.innerWidth };
    }"""
    )
    assert box["left"] >= 0, f"menu clips off the left edge: {box}"
    assert box["right"] <= box["vw"] + 1, f"menu clips off the right edge: {box}"


def test_desktop_keeps_chevron_and_hover_gating(page: Page, interactive_server: str):
    """The default (hover-capable) context keeps the chevron and hover reveal."""
    page.goto(f"{interactive_server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    c = page.evaluate(_PROBE)
    assert c, "no block with both controls found"
    assert not c["hoverNone"], "desktop context should be hover-capable"
    assert c["chevronDisplay"] != "none", "desktop keeps the collapse chevron"
