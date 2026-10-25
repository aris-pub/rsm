"""The sidebar must paint its strip, panel and cards from the document's
semantic surface tokens, not raw palette grays.

A document that overrides --surface-page / --surface-primary / --border-primary
expects the whole UI (the rest of BRAIID already does this) to follow. Before
rsm-flh the rail panel and the collapsed-proof card used raw grays, so they
floated as a cool blue-gray card on a document that had recolored its surfaces.

These assertions read computed colors (not pixels), so they are deterministic
and need no visual baseline.
"""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"

# Distinct sentinels: none is any default gray, so a rule still reading a raw
# gray cannot accidentally match.
OVERRIDE = {
    "--surface-page": "rgb(1, 2, 3)",
    "--surface-primary": "rgb(4, 5, 6)",
    "--border-primary": "rgb(7, 8, 9)",
}

_READ_COLORS = """() => {
    const rail = document.querySelector('.proof-rail.active');
    const card = document.querySelector(
        '.proof-rail.proof-collapsed .proof-rail-item.shown .rail-collapsed-card');
    const rs = getComputedStyle(rail);
    const cs = getComputedStyle(card);
    const ss = getComputedStyle(document.querySelector('.rail-strip'));
    return {
        display: cs.display,
        stripBg: ss.backgroundColor, stripBorder: ss.borderTopColor,
        panelBg: rs.backgroundColor, panelBorder: rs.borderTopColor,
        cardBg: cs.backgroundColor, cardBorder: cs.borderTopColor,
    };
}"""


def _resolve_token(page: Page, token: str) -> str:
    """The computed color a bare `var(<token>)` resolves to in the current theme."""
    return page.evaluate(
        """(token) => {
            const el = document.createElement('div');
            el.style.color = `var(${token})`;
            document.body.appendChild(el);
            const c = getComputedStyle(el).color;
            el.remove();
            return c;
        }""",
        token,
    )


def _setup_collapsed_card(page: Page, server: str, dark: bool) -> None:
    # Acceptance is stated at desktop width, where the rail is the floating panel.
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_selector(".proof-rail.active", state="attached", timeout=10_000)
    if dark:
        page.evaluate("() => document.documentElement.classList.add('dark-theme')")
    # Select the proof so its rail item is the shown one, then put the rail in
    # the collapsed-proof state the way prooftree.js does when the followed proof
    # is collapsed: the single-node card replaces the step graph.
    page.click('.rail-strip-btn[data-view="steps"]')
    page.evaluate(
        """() => {
            const el = document.querySelector('.proof[data-nodeid]');
            el.scrollIntoView({ block: 'center' });
            el.click();
        }"""
    )
    page.wait_for_selector(".rail-proof .proof-rail-item.shown", timeout=5_000)
    page.evaluate(
        "() => document.querySelector('.proof-rail').classList.add('proof-collapsed')"
    )
    page.wait_for_selector(
        ".proof-rail.proof-collapsed .proof-rail-item.shown .rail-collapsed-card",
        timeout=5_000,
    )


@pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
def test_sidebar_surfaces_follow_semantic_tokens(
    page: Page, interactive_server: str, dark: bool
):
    """With no override, the panel and collapsed-proof card compute to the same
    colors as the semantic tokens (so they track the document, not a fixed gray).
    """
    _setup_collapsed_card(page, interactive_server, dark)
    colors = page.evaluate(_READ_COLORS)
    # The collapsed-card rule is the one under test, so confirm it is active.
    assert colors["display"] == "flex"

    surface_page = _resolve_token(page, "--surface-page")
    surface_primary = _resolve_token(page, "--surface-primary")
    border_primary = _resolve_token(page, "--border-primary")

    assert colors["panelBg"] == surface_page
    assert colors["panelBorder"] == border_primary
    assert colors["stripBg"] == surface_page
    assert colors["stripBorder"] == border_primary
    assert colors["cardBg"] == surface_primary
    assert colors["cardBorder"] == border_primary


@pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
def test_sidebar_surfaces_follow_document_override(
    page: Page, interactive_server: str, dark: bool
):
    """A document that sets the semantic surface tokens recolors the rail panel
    and the collapsed-proof card in both themes."""
    _setup_collapsed_card(page, interactive_server, dark)
    css = ":root{" + "".join(f"{k}:{v};" for k, v in OVERRIDE.items()) + "}"
    page.add_style_tag(content=css)

    colors = page.evaluate(_READ_COLORS)
    assert colors["panelBg"] == OVERRIDE["--surface-page"]
    assert colors["panelBorder"] == OVERRIDE["--border-primary"]
    assert colors["stripBg"] == OVERRIDE["--surface-page"]
    assert colors["stripBorder"] == OVERRIDE["--border-primary"]
    assert colors["cardBg"] == OVERRIDE["--surface-primary"]
    assert colors["cardBorder"] == OVERRIDE["--border-primary"]
