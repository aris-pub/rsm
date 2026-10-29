"""Reference previews of :html: blocks (widgets).

A copy of the live widget does not work out of its place (its styles and
scripts are tied to the original), so the preview and the pinned excerpt show
the widget's number, its still image (:static:, or :dark: in dark theme) or else
its alt text, and the line "Interactive in the manuscript." (rsm-9wa)."""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"
NOTE = "Interactive in the manuscript."


def _load(page: Page, server: str, dark: bool = False) -> None:
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/widget_preview.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    if dark:
        page.eval_on_selector("html", "h => h.classList.add('dark-theme')")


def _preview(page: Page, href: str):
    ref = page.locator(f'.manuscript a.reference[href="{href}"]').first
    ref.scroll_into_view_if_needed()
    ref.hover()
    tip = page.locator(
        f'.tooltipster-base:has(.ref-pin[data-pin-target="{href}"])'
    ).last
    expect(tip).to_be_visible(timeout=3000)
    return tip


def _shown_img_src(scope) -> list[str]:
    return scope.evaluate(
        """el => [...el.querySelectorAll('img')]
            .filter(i => i.getClientRects().length)
            .map(i => i.getAttribute('src'))"""
    )


def _wait_one_shown(scope, name: str) -> None:
    """Wait until exactly one image shows in scope and it is the named file."""
    scope.page.wait_for_function(
        """([el, name]) => {
            const shown = [...el.querySelectorAll('img')].filter(i => i.getClientRects().length)
            return shown.length === 1 && shown[0].getAttribute('src').endsWith(name)
        }""",
        arg=[scope.element_handle(), name],
        timeout=5000,
    )


@pytest.mark.parametrize("dark", [False, True])
def test_preview_shows_still_image_not_widget(page: Page, interactive_server: str, dark: bool):
    _load(page, interactive_server, dark)
    tip = _preview(page, "#wid-still")
    expect(tip.locator(".live-widget")).to_have_count(0)
    expect(tip.locator("script, style")).to_have_count(0)
    expect(tip.locator(".widget-preview-label")).to_have_text("Widget 1.1")
    expect(tip.locator(".widget-preview-note")).to_have_text(NOTE)
    want = "fixtures-static-dark.png" if dark else "fixtures-static-light.png"
    shown = _shown_img_src(tip)
    assert len(shown) == 1 and shown[0].endswith(want), shown
    for img in tip.locator("img").all():
        assert img.get_attribute("alt") == "A still picture of the widget."
    # The image is a real file that loaded, not a broken link.
    assert tip.locator("img:visible").evaluate("i => i.complete && i.naturalWidth > 0")


def test_preview_uses_manuscript_font(page: Page, interactive_server: str):
    _load(page, interactive_server)
    tip = _preview(page, "#wid-still")
    body_font = page.evaluate(
        "() => getComputedStyle(document.querySelector('.manuscript p')).fontFamily"
    )
    for sel in (".widget-preview-label", ".widget-preview-note"):
        font = tip.locator(sel).evaluate("e => getComputedStyle(e).fontFamily")
        assert font == body_font, (sel, font, body_font)


def test_preview_without_still_image_shows_alt_text(page: Page, interactive_server: str):
    _load(page, interactive_server)
    tip = _preview(page, "#wid-bare")
    expect(tip.locator(".live-widget")).to_have_count(0)
    expect(tip.locator("img")).to_have_count(0)
    expect(tip.locator(".widget-preview-label")).to_have_text("Widget 1.2")
    expect(tip.locator(".widget-preview-alt")).to_have_text("A widget with no still picture.")
    expect(tip.locator(".widget-preview-note")).to_have_text(NOTE)


def test_pinned_widget_follows_theme_switch(page: Page, interactive_server: str):
    _load(page, interactive_server)
    tip = _preview(page, "#wid-still")
    tip.locator(".ref-pin").click()
    body = page.locator(".rail-pinned-body")
    expect(body.locator(".widget-preview-note")).to_have_text(NOTE)
    expect(body.locator(".live-widget")).to_have_count(0)
    # The card's header already names the widget, so the body does not repeat it.
    expect(body.locator(".widget-preview-label")).to_have_count(0)
    expect(page.locator(".rail-pinned")).to_contain_text("Widget 1.1")
    # The card is filled and laid out after the click returns, so wait for the
    # image to show rather than reading it once.
    _wait_one_shown(body, "fixtures-static-light.png")
    page.eval_on_selector("html", "h => h.classList.add('dark-theme')")
    _wait_one_shown(body, "fixtures-static-dark.png")
