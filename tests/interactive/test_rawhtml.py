"""Inline :rawhtml: in a live page.

The page holds each raw HTML body once, where the author wrote it. The copies
the page makes of its own content (reference previews, the pinned excerpt,
the proof State view, a widget preview's caption) show the :alt: fallback
instead, so a raw element such as a widget is never made a second time.

The fixture's raw HTML is a custom element, <x-probe>, that counts how many
times it is made. It is defined before the page loads, so each of the three
bodies in the fixture is made exactly once while the page is parsed.
"""

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmInitialized === true"
BODIES = 3

PROBE = """
window.__probeMade = 0;
customElements.define("x-probe", class extends HTMLElement {
  constructor() { super(); window.__probeMade++; }
  connectedCallback() { this.textContent = "LIVE"; }
});
"""


def _load(page: Page, server: str) -> None:
    page.set_viewport_size({"width": 1400, "height": 900})
    page.add_init_script(PROBE)
    page.goto(f"{server}/rawhtml.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _made(page: Page) -> int:
    return page.evaluate("() => window.__probeMade")


def _assert_bodies_untouched(page: Page) -> None:
    assert _made(page) == BODIES
    assert page.locator("x-probe").count() == BODIES
    assert page.locator(".manuscript .rawhtml > x-probe").count() == BODIES


def _preview(page: Page, href: str):
    ref = page.locator(f'.manuscript a.reference[href="{href}"]').first
    ref.scroll_into_view_if_needed()
    ref.hover()
    tip = page.locator(
        f'.tooltipster-base:has(.ref-pin[data-pin-target="{href}"])'
    ).last
    expect(tip).to_be_visible(timeout=3000)
    return tip


def test_each_body_is_in_the_page_once(page: Page, interactive_server: str):
    _load(page, interactive_server)
    _assert_bodies_untouched(page)
    # The source kept for the Source menu item is text, not live elements.
    assert page.locator(".rsm-source x-probe").count() == 0
    for alt in page.locator(".manuscript .rawhtml-alt").all():
        expect(alt).to_be_hidden()
    expect(page.locator(".manuscript .theorem x-probe")).to_have_text("LIVE")


def test_preview_shows_the_fallback(page: Page, interactive_server: str):
    _load(page, interactive_server)
    tip = _preview(page, "#thm-chain")
    expect(tip).to_contain_text("the circle")
    expect(tip.locator("x-probe")).to_have_count(0)
    expect(tip.locator(".rawhtml-alt")).to_have_count(0)
    # The math in the fallback is typeset like any math in a preview.
    expect(tip.locator(".rawhtml mjx-container")).to_have_count(1, timeout=5000)
    _assert_bodies_untouched(page)


def test_pinned_excerpt_shows_the_fallback(page: Page, interactive_server: str):
    _load(page, interactive_server)
    tip = _preview(page, "#thm-chain")
    tip.locator(".ref-pin").click()
    body = page.locator(".rail-pinned-body")
    expect(body).to_contain_text("the circle")
    expect(body.locator("x-probe")).to_have_count(0)
    _assert_bodies_untouched(page)


def test_widget_preview_caption_shows_the_fallback(page: Page, interactive_server: str):
    _load(page, interactive_server)
    tip = _preview(page, "#wid-a")
    expect(tip.locator(".widget-preview-caption")).to_contain_text("the dial")
    expect(tip.locator("x-probe")).to_have_count(0)
    _assert_bodies_untouched(page)


def test_proof_state_shows_the_fallback(page: Page, interactive_server: str):
    _load(page, interactive_server)
    btn = page.locator('.rail-strip-btn[data-view="state"]')
    if btn.get_attribute("aria-pressed") != "true":
        btn.click()
    page.wait_for_selector(".proof-rail.open", timeout=5_000)
    page.evaluate(
        """() => {
            const steps = [...document.querySelectorAll('.proof[data-nodeid] .step')];
            const el = steps[steps.length - 1];
            el.scrollIntoView({ block: 'center' });
            el.click();
        }"""
    )
    page.wait_for_selector(".rail-state .rail-hyps li", timeout=5_000)
    state = page.locator(".rail-state")
    expect(state.locator(".rail-hyps")).to_contain_text("the chain")
    expect(state.locator(".rail-goal")).to_contain_text("the circle")
    expect(state.locator("x-probe")).to_have_count(0)
    _assert_bodies_untouched(page)


def test_source_menu_shows_the_markup_as_written(page: Page, interactive_server: str):
    _load(page, interactive_server)
    hr = page.locator(".theorem.hr").first
    hr.scroll_into_view_if_needed()
    hr.hover()
    hr.locator(".hr-border-dots").first.click()
    page.locator('#hr-menu-singleton [data-role="code"]').click()
    modal = page.locator(".rsm-source-modal")
    expect(modal).to_be_visible()
    expect(modal.locator("pre")).to_contain_text(
        ":rawhtml:{:alt: the circle $C_0$} <x-probe></x-probe> ::"
    )
    _assert_bodies_untouched(page)


def test_without_javascript_the_body_shows_and_the_fallback_does_not(
    browser, interactive_server: str
):
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()
    try:
        page.goto(f"{interactive_server}/rawhtml.html")
        assert page.locator(".manuscript .rawhtml > x-probe").count() == BODIES
        for alt in page.locator(".manuscript .rawhtml-alt").all():
            expect(alt).to_be_hidden()
        assert "the circle" not in page.locator(".manuscript .theorem").inner_text()
    finally:
        context.close()
