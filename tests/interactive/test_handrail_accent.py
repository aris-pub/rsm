"""rsm-vv3: the active handrail background follows :accent:, not a hard-coded blue.

Clicking or focusing a handrailed block (proof, step, theorem) paints its zones.
That paint must use the accent's 50 token (--primary-50) so a green-accented
manuscript shows green, not a blue slab. Before the fix the zones used
var(--blue-100) regardless of accent, which was the only blue on a green page.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"


def _measure(page: Page, accent: str, theme: str) -> dict:
    """Set accent and theme, mark a proof active, and read resolved colors.

    Returns the active content zone background alongside probe values for the
    accent's 50 token and the old blue-100, all as fully resolved rgb strings.
    """
    return page.evaluate(
        """({accent, theme}) => {
          const root = document.documentElement;
          root.classList.remove('dark-theme', 'light-theme');
          root.classList.add(theme === 'dark' ? 'dark-theme' : 'light-theme');
          root.setAttribute('data-accent', accent);
          document.body.setAttribute('data-accent', accent);

          const proof = document.querySelector('.proof.hr');
          proof.classList.add('active');
          const zone = proof.querySelector(':scope > .hr-content-zone');
          const zoneBg = getComputedStyle(zone).backgroundColor;

          const probe = document.createElement('div');
          document.body.appendChild(probe);
          probe.style.backgroundColor = 'var(--primary-50)';
          const accent50 = getComputedStyle(probe).backgroundColor;
          probe.style.backgroundColor = 'var(--blue-100)';
          const blue100 = getComputedStyle(probe).backgroundColor;
          probe.remove();

          return {zoneBg, accent50, blue100};
        }""",
        {"accent": accent, "theme": theme},
    )


def _load(page: Page, server: str) -> None:
    # Handrails render in full form on a desktop width; keep the measurement off
    # the mobile drawer path.
    if page.viewport_size["width"] < 1321:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/reorder.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("accent", ["green", "blue"])
def test_active_background_is_accent_50(
    page: Page, interactive_server: str, accent: str, theme: str
):
    _load(page, interactive_server)
    m = _measure(page, accent, theme)
    assert m["zoneBg"] == m["accent50"], (
        f"{accent}/{theme}: active background {m['zoneBg']} is not the accent 50 "
        f"{m['accent50']}"
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_green_active_background_is_not_blue(
    page: Page, interactive_server: str, theme: str
):
    _load(page, interactive_server)
    m = _measure(page, "green", theme)
    assert m["zoneBg"] != m["blue100"], (
        f"green/{theme}: active background is still blue-100 ({m['zoneBg']})"
    )
