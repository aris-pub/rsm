"""Interactive: a page with html.touch behaves as on a phone, whatever the pointer.

The builder's pre-paint script sets html.touch on a device with no hover and a
coarse pointer, and the docs' Touch switch sets it on a page shown on a
computer. Tooltips, asides, bibliography entries and the minimap read the
class, not the device, so with the class set a mouse gets what a finger gets
(rsm-k4fz). Each behavior is also checked on an emulated phone, which must keep
its behavior.
"""

import pytest
from playwright.sync_api import Browser, Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"
ASIDES_READY = (
    "() => window.__rsmShown === true && !!document.querySelector("
    "'a.aside-phrase[aria-controls]')"
)
SET_TOUCH = "() => document.documentElement.classList.add('touch')"
PREVIEW = ".tooltipster-base"
REF = 'a.reference[href="#thm-x"]'
PHONE = {"width": 390, "height": 844}
DESKTOP = {"width": 1280, "height": 800}
BIB_LINKS = "#knuth :is(.bib-line > .bibitem-doi, .bib-cited)"


def _load(page: Page, url: str, ready: str = RSM_READY, touch: bool = True) -> None:
    page.goto(url)
    page.wait_for_function(ready, timeout=10_000)
    if touch:
        page.evaluate(SET_TOUCH)


@pytest.fixture
def phone(browser: Browser):
    ctx = browser.new_context(has_touch=True, is_mobile=True, viewport=PHONE)
    pg = ctx.new_page()
    yield pg
    ctx.close()


# ---- tooltips ---------------------------------------------------------------


class TestReferenceTooltip:
    def test_pointing_does_not_open_the_preview(self, page: Page, interactive_server):
        _load(page, f"{interactive_server}/notes.html")
        page.hover(REF)
        page.wait_for_timeout(700)
        expect(page.locator(PREVIEW)).to_have_count(0)

    def test_click_opens_the_preview_and_a_second_click_follows(
        self, page: Page, interactive_server
    ):
        _load(page, f"{interactive_server}/notes.html")
        page.click(REF)
        preview = page.locator(PREVIEW)
        expect(preview).to_be_visible(timeout=3000)
        expect(preview).to_contain_text("For every graph")
        page.wait_for_timeout(300)
        assert page.evaluate("location.hash") == ""
        page.click(REF)
        page.wait_for_function("() => location.hash === '#thm-x'", timeout=3000)

    def test_enter_still_follows_the_link(self, page: Page, interactive_server):
        _load(page, f"{interactive_server}/notes.html")
        page.locator(REF).focus()
        page.keyboard.press("Enter")
        page.wait_for_function("() => location.hash === '#thm-x'", timeout=3000)

    def test_phone_first_tap_previews_and_second_follows(
        self, phone: Page, interactive_server
    ):
        _load(phone, f"{interactive_server}/notes.html", touch=False)
        assert phone.evaluate("() => document.documentElement.matches('.touch')")
        phone.locator(REF).tap()
        expect(phone.locator(PREVIEW)).to_be_visible(timeout=3000)
        phone.wait_for_timeout(300)
        assert phone.evaluate("location.hash") == ""
        phone.locator(REF).tap()
        phone.wait_for_function("() => location.hash === '#thm-x'", timeout=3000)


# ---- asides -----------------------------------------------------------------


def _aside_open(page: Page, id_: str) -> bool:
    return page.evaluate(
        "(id) => document.getElementById(id).classList.contains('rsm-aside-open')", id_
    )


def _tips(page: Page) -> list[str]:
    return page.evaluate(
        "() => [...document.querySelectorAll('.tooltipster-base')]"
        ".map(t => t.textContent.trim())"
    )


class TestAside:
    # At 1000px a computer has no room for the right-hand column, so asides
    # open below their block.
    def test_pointing_does_not_preview_the_aside(self, page: Page, interactive_server):
        page.set_viewport_size({"width": 1000, "height": 900})
        _load(page, f"{interactive_server}/asides.html", ASIDES_READY)
        page.hover("#call-a-three")
        page.wait_for_timeout(700)
        assert not any("third aside" in t for t in _tips(page))

    def test_click_opens_the_aside(self, page: Page, interactive_server):
        page.set_viewport_size({"width": 1000, "height": 900})
        _load(page, f"{interactive_server}/asides.html", ASIDES_READY)
        page.click("#call-a-three")
        page.wait_for_timeout(300)
        assert _aside_open(page, "a-three")
        assert not any("third aside" in t for t in _tips(page))

    def test_phone_tap_opens_the_aside_without_a_preview(
        self, phone: Page, interactive_server
    ):
        _load(phone, f"{interactive_server}/asides.html", ASIDES_READY, touch=False)
        phone.tap("#call-a-three")
        phone.wait_for_timeout(700)
        assert _aside_open(phone, "a-three")
        assert not any("third aside" in t for t in _tips(phone))


# ---- bibliography entries -----------------------------------------------------


def _opacities(page: Page) -> list[str]:
    return page.locator(BIB_LINKS).evaluate_all(
        "els => els.map(e => getComputedStyle(e).opacity)"
    )


def _card_bg(page: Page) -> str:
    return page.locator("#knuth .bib-card").evaluate(
        "e => getComputedStyle(e).backgroundColor"
    )


class TestBibliographyEntry:
    def test_links_show_at_rest(self, page: Page, interactive_server):
        _load(page, f"{interactive_server}/notes.html")
        page.locator("#knuth").scroll_into_view_if_needed()
        page.mouse.move(1, 1)
        page.wait_for_timeout(300)
        ops = _opacities(page)
        assert len(ops) == 2 and set(ops) == {"1"}, ops

    def test_pointing_does_not_tint_the_card(self, page: Page, interactive_server):
        _load(page, f"{interactive_server}/notes.html")
        page.locator("#knuth").scroll_into_view_if_needed()
        page.mouse.move(1, 1)
        page.wait_for_timeout(300)
        rest = _card_bg(page)
        page.locator("#knuth .bib-title").hover()
        page.wait_for_timeout(300)
        assert _card_bg(page) == rest

    def test_without_the_class_links_show_on_pointing_only(
        self, page: Page, interactive_server
    ):
        _load(page, f"{interactive_server}/notes.html", touch=False)
        page.locator("#knuth").scroll_into_view_if_needed()
        page.mouse.move(1, 1)
        page.wait_for_timeout(300)
        assert set(_opacities(page)) == {"0"}
        page.locator("#knuth .bib-title").hover()
        page.wait_for_timeout(300)
        assert set(_opacities(page)) == {"1"}

    def test_phone_links_show_at_rest(self, phone: Page, interactive_server):
        _load(phone, f"{interactive_server}/notes.html", touch=False)
        phone.locator("#knuth").scroll_into_view_if_needed()
        phone.wait_for_timeout(300)
        ops = _opacities(phone)
        assert len(ops) == 2 and set(ops) == {"1"}, ops


# ---- minimap ------------------------------------------------------------------


def _load_minimap(page: Page, server: str, touch: bool = True) -> None:
    _load(page, f"{server}/minimap.html", touch=touch)
    page.wait_for_selector(
        ".rsm-minimap .rsm-minimap-mark", state="attached", timeout=10_000
    )
    page.wait_for_timeout(400)


def _results_mark(page: Page) -> tuple[float, float]:
    """The strip's x centre and the page y of the "2. Results" mark."""
    return page.evaluate(
        """() => {
        const t = document.querySelector('.rsm-minimap-track').getBoundingClientRect();
        const links = [...document.querySelectorAll('.rsm-minimap-links a')];
        const i = links.findIndex(a => a.textContent === '2. Results');
        const r = document.querySelectorAll('.rsm-minimap-mark')[i].getBoundingClientRect();
        return [t.left + t.width / 2, r.top + r.height / 2];
    }"""
    )


def _settle_scroll(page: Page) -> float:
    return page.evaluate(
        """() => new Promise((resolve) => {
        let last = -1, same = 0;
        const tick = () => {
            const y = window.scrollY;
            same = Math.abs(y - last) < 0.5 ? same + 1 : 0;
            last = y;
            if (same >= 8) resolve(y); else requestAnimationFrame(tick);
        };
        tick();
    })"""
    )


class TestMinimap:
    # 20px from the mark: within the 24px reach of a finger, not the 12px of a
    # mouse.
    def test_pointing_uses_the_finger_reach(self, page: Page, interactive_server):
        page.set_viewport_size(DESKTOP)
        _load_minimap(page, interactive_server)
        x, y = _results_mark(page)
        page.mouse.move(x, y + 20)
        tip = page.locator(".rsm-minimap-tip")
        assert tip.is_visible()
        assert tip.inner_text() == "2. Results"

    def test_first_click_shows_the_label_second_click_goes_there(
        self, page: Page, interactive_server
    ):
        page.set_viewport_size(DESKTOP)
        page.emulate_media(reduced_motion="reduce")
        _load_minimap(page, interactive_server)
        x, y = _results_mark(page)
        before = page.evaluate("() => window.scrollY")
        page.mouse.click(x, y + 20)
        page.wait_for_timeout(300)
        assert page.locator(".rsm-minimap-tip").inner_text() == "2. Results"
        assert page.evaluate("() => window.scrollY") == before, (
            "the first click moved the page"
        )
        page.mouse.click(x, y + 20)
        _settle_scroll(page)
        top = page.evaluate(
            "() => document.getElementById('sec-results').getBoundingClientRect().top"
        )
        assert abs(top - DESKTOP["height"] / 2) <= 2

    def test_without_the_class_a_mouse_keeps_its_reach(
        self, page: Page, interactive_server
    ):
        page.set_viewport_size(DESKTOP)
        _load_minimap(page, interactive_server, touch=False)
        x, y = _results_mark(page)
        page.mouse.move(x, y + 20)
        assert not page.locator(".rsm-minimap-tip").is_visible()
