"""Interactive: a page with html.touch has no hover effects (rsm-k4fz).

On a phone a tap leaves :hover set on what was tapped, so a hover effect stays
on after the tap. A page with the touch class therefore turns hover effects
off, whatever the pointer. A page without the class keeps them.
"""

import pytest
from playwright.sync_api import Browser, Page

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"
SET_TOUCH = "() => document.documentElement.classList.add('touch')"
PHONE = {"width": 390, "height": 844}

STEP = "#stp-first"
PROOF_TEXT = ".proof > .hr-content-zone > .paragraph:not(.hr-label) p"

# Each target: the element to hover, and a script that returns the styles
# that its hover effect changes.
TARGETS = {
    "link": (
        '.manuscript a[href="https://example.com"]',
        """() => {
            const s = getComputedStyle(
                document.querySelector('.manuscript a[href="https://example.com"]'));
            return [s.color, s.textDecorationLine];
        }""",
    ),
    "step number": (
        f"{STEP} > .hr-info-zone p",
        f"""() => getComputedStyle(
            document.querySelector('{STEP} > .hr-info-zone p')).fontWeight""",
    ),
    "equation number": (
        ".mathblock.hr > .hr-content-zone",
        """() => getComputedStyle(
            document.querySelector('.mathblock.hr > .hr-info-zone p')).fontWeight""",
    ),
    "proof": (
        PROOF_TEXT,
        """() => getComputedStyle(
            document.querySelector('.proof.hr > .hr-content-zone'), '::after').content""",
    ),
    "figure": (
        "figure img",
        """() => getComputedStyle(
            document.querySelector('figure > .hr.rsm-cap-linked > .hr-border-zone')).opacity""",
    ),
}

# What a tap on a step can leave behind: the bold step number, the step's end
# mark and the proof's end mark.
STEP_TAP_MARKS = """() => {
    const q = (s) => document.querySelector(s);
    return [
        getComputedStyle(q('#stp-first > .hr-info-zone p')).fontWeight,
        getComputedStyle(q('#stp-first'), '::after').content,
        getComputedStyle(q('.proof.hr > .hr-content-zone'), '::after').content,
    ];
}"""


def _load(page: Page, url: str, touch: bool) -> None:
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto(url)
    page.wait_for_function(RSM_READY, timeout=10_000)
    if touch:
        page.evaluate(SET_TOUCH)
    page.mouse.move(1, 1)
    page.wait_for_timeout(200)


def _rest_and_hover(page: Page, name: str):
    target, measure = TARGETS[name]
    rest = page.evaluate(measure)
    page.hover(target)
    page.wait_for_timeout(300)
    return rest, page.evaluate(measure)


@pytest.mark.parametrize("name", list(TARGETS))
def test_touch_page_has_no_hover_effect(page: Page, interactive_server, name):
    _load(page, f"{interactive_server}/touch_hover.html", touch=True)
    rest, hovered = _rest_and_hover(page, name)
    assert hovered == rest


@pytest.mark.parametrize("name", list(TARGETS))
def test_without_the_class_hover_effect_shows(page: Page, interactive_server, name):
    _load(page, f"{interactive_server}/touch_hover.html", touch=False)
    rest, hovered = _rest_and_hover(page, name)
    assert hovered != rest


def test_phone_tap_on_a_step_leaves_no_hover_effect(
    browser: Browser, interactive_server
):
    ctx = browser.new_context(has_touch=True, is_mobile=True, viewport=PHONE)
    try:
        phone = ctx.new_page()
        phone.goto(f"{interactive_server}/touch_hover.html")
        phone.wait_for_function(RSM_READY, timeout=10_000)
        assert phone.evaluate("() => document.documentElement.matches('.touch')")
        rest = phone.evaluate(STEP_TAP_MARKS)
        phone.tap(f"{STEP} .statement p")
        phone.wait_for_timeout(300)
        assert phone.evaluate(
            f"() => document.querySelector('{STEP}').matches(':hover')"
        )
        assert phone.evaluate(STEP_TAP_MARKS) == rest
    finally:
        ctx.close()
