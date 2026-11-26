"""The mail and ORCID icons next to an author's name are icon buttons, and
behave like BRAIID's other icon buttons: a gray background when the mouse is
over them, a focus ring for the keyboard, and a short label that says where the
link goes."""

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"


def _load(page: Page, server: str) -> None:
    page.set_viewport_size({"width": 1100, "height": 800})
    page.goto(f"{server}/author_states.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.wait_for_timeout(300)


def _bg(page: Page, selector: str) -> str:
    return page.evaluate(
        f"() => getComputedStyle(document.querySelector('{selector}')).backgroundColor"
    )


def test_hover_gives_the_icon_the_standard_background(page: Page, interactive_server: str):
    _load(page, interactive_server)
    icon = 'a.author-contact[href^="mailto:"]'
    before = _bg(page, icon)
    page.hover(icon)
    page.wait_for_timeout(200)
    after = _bg(page, icon)
    hover = page.evaluate(
        "() => { const d = document.createElement('div');"
        " d.style.background = 'var(--primary-100)';"
        " document.querySelector('.manuscriptwrapper').appendChild(d);"
        " const c = getComputedStyle(d).backgroundColor; d.remove(); return c; }"
    )
    assert before != after
    assert after == hover


def test_hover_shows_a_label_saying_where_the_link_goes(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.hover('a.author-contact[href^="mailto:"]')
    page.wait_for_selector(".ui-tip.on", timeout=3_000)
    assert page.locator(".ui-tip.on").inner_text().startswith("Email ")
    page.mouse.move(5, 5)
    page.hover('a.author-contact[href^="https://orcid.org/"]')
    page.wait_for_function(
        "() => (document.querySelector('.ui-tip.on')||{}).innerText?.startsWith('ORCID record of')",
        timeout=3_000,
    )


def test_keyboard_focus_shows_a_ring(page: Page, interactive_server: str):
    _load(page, interactive_server)
    page.focus('a.author-contact[href^="mailto:"]')
    page.keyboard.press("Shift+Tab")
    page.keyboard.press("Tab")
    style = page.evaluate(
        "() => { const s = getComputedStyle(document.activeElement);"
        " return [document.activeElement.className, s.outlineStyle, s.outlineWidth]; }"
    )
    assert "author-contact" in style[0]
    assert style[1] != "none" and style[2] != "0px", style
