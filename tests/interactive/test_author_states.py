"""The author block has two states, closed and open (design 4, approved by Leo
on 2026-11-26).

Three controls switch the same state: the handrail's collapse chevron, the
pill in the name list ("3 more" when closed, "Show fewer" when open), and the
summary label under the names (shown only when closed). Each author name has a
tooltip with that author's affiliation and note.
"""

import pytest
from playwright.sync_api import Browser, Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"
BLOCK = ".author-block"
CHEVRON = ".author-block .hr > .hr-collapse-zone .hr-collapse"
CHEVRON_ICON = ".author-block .hr > .hr-collapse-zone .hr-collapse .icon"
MORE = ".author-block .author-more button"
FEWER = ".author-block .author-fewer button"
SUMMARY = ".author-block .author-summary"
DETAILS = ".author-block .author-details"
NAMES = ".author-block p.author-names"
TIP = ".tooltipster-base"

SHORT = "Ada Lovelace1 , Bo Chen2, Cy Diaz3, 3 more, Gil Moreau3, Hana Sato4"
FULL = (
    "Ada Lovelace1 , Bo Chen2, Cy Diaz3, Dana Patel4, Eli Novak1, Fay Okafor2 "
    "Show fewer, Gil Moreau3, Hana Sato4"
)
ALL_NAMES = (
    "Ada Lovelace1 , Bo Chen2, Cy Diaz3, Dana Patel4, Eli Novak1, Fay Okafor2, "
    "Gil Moreau3, Hana Sato4"
)
LABEL = "4 affiliations · 1 email · 1 ORCID · 1 note"


def _load(page: Page, server: str, name: str = "author_states", touch=False):
    page.set_viewport_size({"width": 1100, "height": 800})
    page.goto(f"{server}/{name}.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    if touch:
        page.evaluate("() => document.documentElement.classList.add('touch')")


def _state(page: Page) -> str | None:
    return page.locator(BLOCK).get_attribute("data-authors")


def _names_text(page: Page) -> str:
    return " ".join(page.locator(NAMES).inner_text().split())


def _rotation(page: Page) -> str:
    return page.locator(CHEVRON_ICON).evaluate("(e) => getComputedStyle(e).transform")


def _press(page: Page, control: str) -> None:
    if control == "chevron":
        page.hover(f"{BLOCK} .hr")
        page.click(CHEVRON)
    elif control == "pill":
        page.click(MORE if _state(page) == "closed" else FEWER)
    elif control == "summary":
        page.click(SUMMARY)


def _assert_closed(page: Page, short=True):
    assert _state(page) == "closed"
    assert _names_text(page) == (SHORT if short else ALL_NAMES)
    expect(page.locator(SUMMARY)).to_be_visible()
    expect(page.locator(SUMMARY)).to_have_text(LABEL)
    expect(page.locator(DETAILS)).to_be_hidden()
    expect(page.locator(FEWER)).to_have_count(1 if short else 0)
    if short:
        expect(page.locator(FEWER)).to_be_hidden()
    assert _rotation(page) == "none"
    expect(page.locator(CHEVRON)).to_have_attribute("aria-expanded", "false")


def _assert_open(page: Page, short=True):
    assert _state(page) == "open"
    assert _names_text(page) == (FULL if short else ALL_NAMES)
    expect(page.locator(SUMMARY)).to_be_hidden()
    expect(page.locator(DETAILS)).to_be_visible()
    if short:
        expect(page.locator(MORE)).to_be_hidden()
        expect(page.locator(FEWER)).to_be_visible()
    # A quarter turn: the chevron points down.
    assert _rotation(page) == "matrix(0, 1, -1, 0, 0, 0)"
    expect(page.locator(CHEVRON)).to_have_attribute("aria-expanded", "true")


class TestShortened:
    def test_closed_on_load(self, page: Page, interactive_server):
        _load(page, interactive_server)
        _assert_closed(page)

    def test_open_content(self, page: Page, interactive_server):
        _load(page, interactive_server)
        _press(page, "pill")
        _assert_open(page)
        details = page.locator(DETAILS)
        expect(details.locator("ol.author-affiliations li")).to_have_count(4)
        expect(details).to_contain_text("University of London")
        expect(details).to_contain_text("Equal contribution")
        expect(details).to_contain_text("Correspondence: ada@example.org")
        expect(details).to_contain_text("Ada Lovelace: 0000-0002-1825-0097")

    @pytest.mark.parametrize("control", ["chevron", "pill"])
    def test_control_switches_both_ways(self, page: Page, interactive_server, control):
        _load(page, interactive_server)
        _press(page, control)
        _assert_open(page)
        _press(page, control)
        _assert_closed(page)
        _press(page, control)
        _assert_open(page)

    def test_summary_label_opens(self, page: Page, interactive_server):
        # The label is not shown when open, so it only opens.
        _load(page, interactive_server)
        _press(page, "summary")
        _assert_open(page)

    @pytest.mark.parametrize("opener", ["chevron", "pill", "summary"])
    @pytest.mark.parametrize("closer", ["chevron", "pill"])
    def test_controls_share_one_state(self, page: Page, interactive_server, opener, closer):
        _load(page, interactive_server)
        _press(page, opener)
        _assert_open(page)
        _press(page, closer)
        _assert_closed(page)

    @pytest.mark.parametrize("key", ["Enter", "Space"])
    def test_keyboard_opens_and_closes(self, page: Page, interactive_server, key):
        _load(page, interactive_server)
        page.locator(MORE).focus()
        page.keyboard.press(key)
        _assert_open(page)
        page.locator(FEWER).focus()
        page.keyboard.press(key)
        _assert_closed(page)


class TestNotShortened:
    def test_closed_on_load_shows_every_name(self, page: Page, interactive_server):
        _load(page, interactive_server, "author_states_full")
        _assert_closed(page, short=False)
        expect(page.locator(MORE)).to_have_count(0)

    def test_chevron_switches_the_details_both_ways(self, page: Page, interactive_server):
        _load(page, interactive_server, "author_states_full")
        _press(page, "chevron")
        _assert_open(page, short=False)
        _press(page, "chevron")
        _assert_closed(page, short=False)

    def test_summary_label_opens_the_details(self, page: Page, interactive_server):
        _load(page, interactive_server, "author_states_full")
        _press(page, "summary")
        _assert_open(page, short=False)


class TestTouchMenu:
    def test_menu_collapse_item_switches_the_state(self, page: Page, interactive_server):
        _load(page, interactive_server, touch=True)
        item = page.locator('#hr-menu-singleton [data-role="collapse"]')
        page.click(f"{BLOCK} .hr-border-dots")
        expect(item).to_have_text("Expand")
        item.click()
        assert _state(page) == "open"
        page.click(f"{BLOCK} .hr-border-dots")
        expect(item).to_have_text("Collapse")
        item.click()
        assert _state(page) == "closed"


class TestNameTooltip:
    def test_pointing_at_a_name_opens_its_tooltip(self, page: Page, interactive_server):
        _load(page, interactive_server)
        page.hover(".author-name-text >> text=Ada Lovelace")
        tip = page.locator(TIP)
        expect(tip).to_be_visible(timeout=3000)
        expect(tip).to_have_count(1)
        expect(tip).to_contain_text("University of London")
        expect(tip).to_contain_text("Equal contribution")

    def test_tooltip_shows_only_that_author(self, page: Page, interactive_server):
        _load(page, interactive_server)
        page.hover(".author-name-text >> text=Cy Diaz")
        tip = page.locator(TIP)
        expect(tip).to_be_visible(timeout=3000)
        assert " ".join(tip.inner_text().split()) == "Universidad de Chile"

    def test_tap_on_a_touch_page_opens_the_tooltip(self, page: Page, interactive_server):
        _load(page, interactive_server, touch=True)
        page.click(".author-name-text >> text=Bo Chen")
        tip = page.locator(TIP)
        expect(tip).to_be_visible(timeout=3000)
        expect(tip).to_contain_text("ETH Zurich")
        expect(tip).to_contain_text("Equal contribution")

    def test_tap_on_a_phone_opens_the_tooltip(self, browser: Browser, interactive_server):
        ctx = browser.new_context(
            has_touch=True, is_mobile=True, viewport={"width": 390, "height": 844}
        )
        page = ctx.new_page()
        page.goto(f"{interactive_server}/author_states.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        assert page.evaluate("() => document.documentElement.matches('.touch')")
        page.locator(".author-name-text >> text=Bo Chen").tap()
        tip = page.locator(TIP)
        expect(tip).to_be_visible(timeout=3000)
        expect(tip).to_contain_text("ETH Zurich")
        ctx.close()

    def test_superscript_keeps_its_own_tooltip(self, page: Page, interactive_server):
        _load(page, interactive_server)
        page.hover(".author-name:has-text('Bo Chen') sup")
        tip = page.locator(TIP)
        expect(tip).to_be_visible(timeout=3000)
        expect(tip).to_have_count(1)
        assert " ".join(tip.inner_text().split()) == "ETH Zurich"


class TestWithoutJavaScript:
    @pytest.mark.parametrize("name", ["author_states", "author_states_full"])
    def test_every_name_and_all_details_without_controls(
        self, browser: Browser, interactive_server, name
    ):
        ctx = browser.new_context(java_script_enabled=False)
        page = ctx.new_page()
        page.goto(f"{interactive_server}/{name}.html")
        assert _names_text(page) == ALL_NAMES
        expect(page.locator(DETAILS)).to_be_visible()
        expect(page.locator(DETAILS)).to_contain_text("Ada Lovelace: 0000-0002-1825-0097")
        expect(page.locator(SUMMARY)).to_be_hidden()
        for sel in (MORE, FEWER):
            for i in range(page.locator(sel).count()):
                expect(page.locator(sel).nth(i)).to_be_hidden()
        ctx.close()


def _reload(page: Page) -> None:
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)


class TestRemembered:
    """The block remembers the reader's choice across reloads, like other folds."""

    @pytest.mark.parametrize("control", ["chevron", "pill", "summary"])
    def test_open_stays_open_after_reload(self, page: Page, interactive_server, control):
        _load(page, interactive_server)
        _press(page, control)
        _assert_open(page)
        _reload(page)
        _assert_open(page)

    @pytest.mark.parametrize("control", ["chevron", "pill"])
    def test_closed_stays_closed_after_reload(self, page: Page, interactive_server, control):
        _load(page, interactive_server)
        _press(page, "summary")
        _reload(page)
        _assert_open(page)
        _press(page, control)
        _assert_closed(page)
        _reload(page)
        _assert_closed(page)

    def test_full_list_remembers_too(self, page: Page, interactive_server):
        _load(page, interactive_server, "author_states_full")
        _press(page, "summary")
        _reload(page)
        _assert_open(page, short=False)


class TestNothingToOpen:
    def test_no_chevron_and_no_controls(self, page: Page, interactive_server):
        _load(page, interactive_server, "author_states_bare")
        expect(page.locator(CHEVRON)).to_have_count(0)
        expect(page.locator(SUMMARY)).to_have_count(0)
        expect(page.locator(MORE)).to_have_count(0)
        assert _names_text(page) == "Ada Lovelace, Bo Chen"


class TestFoot:
    """A closed author block shows the foot of the handrail, as every other
    collapsed block does (the hr-collapsed class draws it)."""

    def _hr_collapsed(self, page: Page) -> bool:
        return page.evaluate(
            "() => document.querySelector('.author-block > .hr').classList.contains('hr-collapsed')"
        )

    def test_closed_block_has_the_foot_and_keeps_its_content(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        page.evaluate("() => localStorage.clear()")
        page.reload()
        page.wait_for_function(RSM_READY, timeout=10_000)
        assert _state(page) == "closed"
        assert self._hr_collapsed(page)
        assert page.locator(".author-names").is_visible()
        assert page.locator(".author-summary").is_visible()

    def test_open_block_has_no_foot(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        page.locator(".author-summary").click()
        page.wait_for_timeout(200)
        assert _state(page) == "open"
        assert not self._hr_collapsed(page)
