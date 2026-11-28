"""Reference previews and the handrail menu of :video: blocks (rsm-ivf0).

A copy of a video in a preview would play on its own, so the preview of a video
with :static: shows the still image with the number and caption, as for a figure
that holds HTML. A video with no :static: keeps the video in its preview. A video
has no "Static" item in its handrail menu, because a video plays without
JavaScript and the page has no still image for the item to show."""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"


def _load(page: Page, server: str) -> None:
    page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/video_preview.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _preview(page: Page, href: str):
    ref = page.locator(f'.manuscript a.reference[href="{href}"]').first
    ref.scroll_into_view_if_needed()
    ref.hover()
    tip = page.locator(
        f'.tooltipster-base:has(.ref-pin[data-pin-target="{href}"])'
    ).last
    expect(tip).to_be_visible(timeout=3000)
    return tip


def test_preview_of_video_with_static_shows_the_still(
    page: Page, interactive_server: str
):
    _load(page, interactive_server)
    tip = _preview(page, "#vid-still")
    expect(tip.locator("video")).to_have_count(0)
    img = tip.locator("img")
    expect(img).to_have_count(1)
    assert img.get_attribute("src").endswith("fixtures-static-light.png")
    assert img.get_attribute("alt") == "One frame of the video."
    assert img.evaluate("i => i.complete && i.naturalWidth > 0")
    expect(tip).to_contain_text("Video 1.1")
    expect(tip).to_contain_text("A video with a still image.")


def test_preview_of_video_without_static_keeps_the_video(
    page: Page, interactive_server: str
):
    _load(page, interactive_server)
    tip = _preview(page, "#vid-bare")
    expect(tip.locator("video")).to_have_count(1)
    expect(tip.locator("img")).to_have_count(0)
    expect(tip).to_contain_text("Video 1.2")


@pytest.mark.parametrize("label", ["vid-still", "vid-bare"])
def test_video_menu_has_no_static_item(
    page: Page, interactive_server: str, label: str
):
    _load(page, interactive_server)
    figure = page.locator(f"figure#{label}")
    figure.scroll_into_view_if_needed()
    figure.locator("figcaption .hr-border-dots").click()
    expect(page.locator("#hr-menu-singleton [data-role='link']")).to_be_visible()
    expect(
        page.locator('#hr-menu-singleton [data-role="static-toggle"]')
    ).to_be_hidden()
