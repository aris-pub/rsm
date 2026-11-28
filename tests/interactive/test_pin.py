"""Interactive tests for pinning blocks into the sidebar's Pinned view.

Hovering a reference shows an inert preview (tooltips.js). A pin control in the
preview's corner keeps a copy of the block open in the Pinned view, and a
block's handrail menu offers the same as "Pin". Pinning opens the Pinned view.
A reader can pin any number of blocks. The newest pin is on top. Each pin is a
copy of the block with its own handrail, so it folds like the block in the
text. A crossed-out pin icon in the copy's info zone unpins it, and the
handrail menu shows "Unpin" for a pinned block, both in the text and in the
panel.
"""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"
PINS = ".rail-pinned-body > [data-pin-target]"


def _load(page: Page, server: str) -> None:
    if page.viewport_size["width"] < 768:
        page.set_viewport_size({"width": 1400, "height": 900})
    page.goto(f"{server}/sidebar.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)


def _hover_ref(page: Page, href: str):
    ref = page.locator(f'.manuscript a.reference[href="{href}"]').first
    ref.scroll_into_view_if_needed()
    ref.hover()
    return ref


def _pin_button(page: Page, href: str):
    # Target the pin control for THIS reference: tooltipster leaves closed
    # tooltips in the DOM, so a bare .first can match a stale one.
    _hover_ref(page, href)
    pin = page.locator(f'.tooltipster-base .ref-pin[data-pin-target="{href}"]').last
    expect(pin).to_be_visible(timeout=3000)
    return pin


def _pin(page: Page, href: str) -> None:
    _pin_button(page, href).click()
    expect(page.locator(f'{PINS}[data-pin-target="{href}"]')).to_have_count(1)


def _open_menu(page: Page, block) -> None:
    block.scroll_into_view_if_needed()
    block.hover()
    block.locator(":scope > .hr-border-zone .hr-border-dots").click()
    expect(page.locator('#hr-menu-singleton [data-role="pin"]')).to_be_visible()


def _menu_pin_text(page: Page) -> str:
    return page.locator(
        '#hr-menu-singleton [data-role="pin"] .hr-menu-item-text'
    ).inner_text()


def _targets(page: Page) -> list[str]:
    return page.locator(PINS).evaluate_all("els => els.map(e => e.dataset.pinTarget)")


def _first_paragraph(page: Page):
    return (
        page.locator(".manuscript .paragraph.hr")
        .filter(has_text="This paragraph is filler")
        .first
    )


class TestPinToSidebar:
    def test_reference_preview_has_pin_control(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        pin = _pin_button(page, "#thm-x")
        assert pin.get_attribute("aria-label") == "Pin to the sidebar"
        assert pin.get_attribute("aria-pressed") == "false"

    def test_pin_opens_pinned_view(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        rail = page.locator(".proof-rail")
        expect(rail).to_have_class(re.compile(r"\bhas-pin\b"))
        expect(rail).to_have_class(re.compile(r"\bscope-pinned\b"))
        expect(rail).to_have_class(re.compile(r"\bopen\b"))
        expect(page.locator('.rail-strip-btn[data-view="pinned"]')).to_have_attribute(
            "aria-pressed", "true"
        )
        expect(page.locator(".rail-pinned")).to_contain_text("A claim about")

    def test_pinned_preview_shows_pinned_state(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        page.keyboard.press("Escape")
        pin = _pin_button(page, "#thm-x")
        expect(pin).to_have_attribute("aria-pressed", "true")
        assert pin.get_attribute("aria-label") == "Pinned in the sidebar"
        assert pin.get_attribute("data-pinned") is not None
        # Clicking it again shows the pins rather than pinning it anew.
        pin.click()
        expect(page.locator(".proof-rail")).to_have_class(
            re.compile(r"\bscope-pinned\b")
        )
        expect(page.locator(".proof-rail")).to_have_class(re.compile(r"\bopen\b"))
        expect(page.locator(PINS)).to_have_count(1)

    def test_pinned_view_has_empty_state(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        page.click('.rail-strip-btn[data-view="pinned"]')
        rail = page.locator(".proof-rail")
        expect(rail).to_have_class(re.compile(r"\bscope-pinned\b"))
        expect(page.locator(".rail-pinned-empty")).to_be_visible()
        expect(page.locator(".rail-pinned-body")).to_be_hidden()

    def test_handrail_menu_pins_block(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _open_menu(page, page.locator(".manuscript .theorem").first)
        assert _menu_pin_text(page) == "Pin"
        page.locator('#hr-menu-singleton [data-role="pin"]').click()
        rail = page.locator(".proof-rail")
        expect(rail).to_have_class(re.compile(r"\bscope-pinned\b"))
        expect(page.locator(".rail-pinned")).to_contain_text("A claim about")


class TestSeveralPins:
    def test_pins_stack_newest_on_top(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        _pin(page, "#st-1")
        _pin(page, "#st-2")
        assert _targets(page) == ["#st-2", "#st-1", "#thm-x"]
        expect(page.locator(".rail-pinned")).to_contain_text("A claim about")
        expect(page.locator(".rail-pinned")).to_contain_text("First")

    def test_pinning_a_pinned_block_adds_no_copy(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        _pin(page, "#st-1")
        _pin_button(page, "#thm-x").click()
        assert _targets(page) == ["#st-1", "#thm-x"]

    def test_no_single_pin_header(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        expect(page.locator(".rail-pinned-head")).to_have_count(0)
        expect(page.locator(".rail-pin-close")).to_have_count(0)

    def test_copies_keep_their_handrail_and_label(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        copy = page.locator(f'{PINS}[data-pin-target="#thm-x"]')
        expect(copy).to_have_class(re.compile(r"\bhr\b"))
        expect(copy.locator(":scope > .hr-border-zone .hr-border-dots")).to_have_count(
            1
        )
        expect(copy.locator(":scope > .hr-collapse-zone .hr-collapse")).to_have_count(1)
        expect(copy.locator(":scope > .hr-info-zone")).to_have_count(1)
        # The label is part of the copy, once.
        count = page.locator(".rail-pinned").evaluate(
            "el => (el.innerText.match(/Theorem 2\\.1/g) || []).length"
        )
        assert count == 1

    def test_copies_carry_no_duplicate_ids(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        _pin(page, "#st-1")
        result = page.locator(".rail-pinned-body").evaluate(
            """b => {
            const outside = new Set([...document.querySelectorAll('[id]')]
              .filter(e => !b.contains(e)).map(e => e.id));
            const inside = [...b.querySelectorAll('[id]')].map(e => e.id);
            return {
              dups: inside.filter(id => outside.has(id) || inside.indexOf(id) !== inside.lastIndexOf(id)),
              nodeids: b.querySelectorAll('[data-nodeid]').length,
            };
        }"""
        )
        assert result == {"dups": [], "nodeids": 0}

    def test_copy_folds_with_its_own_handrail(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        folds = "() => localStorage.getItem('rsm-collapse:' + location.pathname)"
        saved = page.evaluate(folds)
        copy = page.locator(f'{PINS}[data-pin-target="#thm-x"]')
        copy.hover()
        copy.locator(":scope > .hr-collapse-zone .hr-collapse").click()
        expect(copy).to_have_class(re.compile(r"\bhr-collapsed\b"))
        expect(copy).not_to_contain_text("A claim about", use_inner_text=True)
        expect(page.locator(".manuscript #thm-x")).not_to_have_class(
            re.compile(r"\bhr-collapsed\b")
        )
        # A pin's fold is not saved. The sidebar saves its open view on its
        # own schedule, so only the saved folds are compared.
        assert page.evaluate(folds) == saved
        copy.locator(":scope > .hr-collapse-zone .hr-collapse").click()
        expect(copy).to_contain_text("A claim about")

    def test_pinned_paragraph_shows_no_handrail_line_at_rest(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        par = _first_paragraph(page)
        _open_menu(page, par)
        page.locator('#hr-menu-singleton [data-role="pin"]').click()
        copy = page.locator(PINS).first
        expect(copy).to_contain_text("This paragraph is filler")
        page.mouse.move(5, 5)
        expect(copy.locator(":scope > .hr-border-zone")).to_have_css("opacity", "0")


class TestUnpin:
    def _icon(self, page: Page, href: str):
        return page.locator(
            f'{PINS}[data-pin-target="{href}"] > .hr-info-zone .pin-unpin'
        )

    def test_unpin_icon_sits_in_the_info_zone(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        icon = self._icon(page, "#thm-x")
        expect(icon).to_have_count(1)
        assert icon.get_attribute("aria-label") == "Unpin"
        expect(icon.locator("use")).to_have_attribute("href", "#hr-icon-unpin")

    def test_unpin_icon_shows_only_on_hover(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        _pin(page, "#st-1")
        page.mouse.move(5, 5)
        icon = self._icon(page, "#thm-x")
        expect(icon).to_have_css("opacity", "0")
        page.locator(f'{PINS}[data-pin-target="#thm-x"]').hover()
        expect(icon).to_have_css("opacity", "1")
        expect(self._icon(page, "#st-1")).to_have_css("opacity", "0")

    @pytest.mark.parametrize("href", ["#thm-x", "#st-1", "paragraph"])
    def test_unpin_icon_bottom_on_first_baseline(
        self, page: Page, interactive_server: str, href: str
    ):
        _load(page, interactive_server)
        if href == "paragraph":
            _open_menu(page, _first_paragraph(page))
            page.locator('#hr-menu-singleton [data-role="pin"]').click()
            copy = page.locator(PINS).first
        else:
            _pin(page, href)
            copy = page.locator(f'{PINS}[data-pin-target="{href}"]')
        expect(copy).to_be_visible()
        page.wait_for_timeout(300)
        geom = copy.evaluate(
            """b => {
            const zone = b.querySelector(':scope > .hr-content-zone');
            const w = document.createTreeWalker(zone, NodeFilter.SHOW_TEXT,
              {acceptNode: n => n.textContent.trim() ? 1 : 3});
            const first = w.nextNode();
            const probe = document.createElement('span');
            probe.style.cssText = 'display:inline-block;width:0;height:0';
            first.parentNode.insertBefore(probe, first);
            const baseline = probe.getBoundingClientRect().bottom;
            probe.remove();
            const svg = b.querySelector(':scope > .hr-info-zone .pin-unpin svg')
              .getBoundingClientRect();
            const info = b.querySelector(':scope > .hr-info-zone').getBoundingClientRect();
            // The drawn glyph ends 2 units above the bottom of its 24-unit box.
            const glyphBottom = svg.bottom - svg.height * 2 / 24;
            return {baseline, bottom: glyphBottom, left: svg.left, right: svg.right,
                    infoLeft: info.left, infoRight: info.right};
        }"""
        )
        assert abs(geom["bottom"] - geom["baseline"]) <= 1.5, geom
        assert (
            geom["infoLeft"] - 0.5 <= geom["left"]
            and geom["right"] <= geom["infoRight"] + 0.5
        ), geom

    def test_unpin_icon_removes_that_pin_only(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        _pin(page, "#st-1")
        page.locator(f'{PINS}[data-pin-target="#thm-x"]').hover()
        self._icon(page, "#thm-x").click()
        expect(page.locator(PINS)).to_have_count(1)
        assert _targets(page) == ["#st-1"]
        expect(page.locator(".proof-rail")).to_have_class(re.compile(r"\bhas-pin\b"))
        # The preview of the unpinned block offers Pin again.
        expect(_pin_button(page, "#thm-x")).to_have_attribute("aria-pressed", "false")

    def test_menu_in_text_says_unpin_and_unpins(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        theorem = page.locator(".manuscript #thm-x")
        _open_menu(page, theorem)
        page.locator('#hr-menu-singleton [data-role="pin"]').click()
        _pin(page, "#st-1")
        _open_menu(page, theorem)
        assert _menu_pin_text(page) == "Unpin"
        expect(
            page.locator('#hr-menu-singleton [data-role="pin"] use')
        ).to_have_attribute("href", "#hr-icon-unpin")
        page.locator('#hr-menu-singleton [data-role="pin"]').click()
        assert _targets(page) == ["#st-1"]
        _open_menu(page, theorem)
        assert _menu_pin_text(page) == "Pin"
        expect(
            page.locator('#hr-menu-singleton [data-role="pin"] use')
        ).to_have_attribute("href", "#hr-icon-pin")

    def test_menu_on_copy_says_unpin_and_unpins(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        _pin(page, "#st-1")
        _open_menu(page, page.locator(f'{PINS}[data-pin-target="#thm-x"]'))
        assert _menu_pin_text(page) == "Unpin"
        page.locator('#hr-menu-singleton [data-role="pin"]').click()
        assert _targets(page) == ["#st-1"]


def _rail_open(page: Page) -> bool:
    return page.evaluate(
        "() => document.documentElement.classList.contains('rail-open')"
    )


class TestUnpinClosesThePanel:
    """The panel closes when the last pin is removed, and stays open while
    pins remain."""

    def test_unpin_last_closes_the_panel_on_desktop(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        page.wait_for_function(
            "() => document.documentElement.classList.contains('rail-open')"
        )
        page.locator(f"{PINS}").hover()
        page.locator(f"{PINS} .pin-unpin").click()
        page.wait_for_function(
            "() => !document.documentElement.classList.contains('rail-open')",
            timeout=3000,
        )

    def test_unpin_with_pins_left_keeps_the_panel_open(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        _pin(page, "#st-1")
        page.wait_for_function(
            "() => document.documentElement.classList.contains('rail-open')"
        )
        copy = page.locator(f'{PINS}[data-pin-target="#thm-x"]')
        copy.hover()
        copy.locator(".pin-unpin").click()
        expect(page.locator(PINS)).to_have_count(1)
        page.wait_for_timeout(500)
        assert _rail_open(page)
        expect(page.locator(".proof-rail")).to_have_class(
            re.compile(r"\bscope-pinned\b")
        )
        # Unpin from the menu in the text keeps it open too while a pin remains.
        _open_menu(page, page.locator(".manuscript #thm-x"))
        page.locator('#hr-menu-singleton [data-role="pin"]').click()
        _open_menu(page, page.locator(".manuscript #thm-x"))
        page.locator('#hr-menu-singleton [data-role="pin"]').click()
        expect(page.locator(PINS)).to_have_count(1)
        assert _rail_open(page)

    def test_unpin_last_closes_the_sheet_on_a_phone(
        self, playwright, browser, interactive_server: str
    ):
        ctx = browser.new_context(**playwright.devices["iPhone 13"])
        page = ctx.new_page()
        try:
            page.goto(f"{interactive_server}/sidebar.html")
            page.wait_for_function(RSM_READY, timeout=10_000)
            theorem = page.locator(".manuscript .theorem").first
            theorem.scroll_into_view_if_needed()
            theorem.locator(":scope > .hr-border-zone .hr-border-dots").click()
            page.locator('#hr-menu-singleton [data-role="pin"]').click()
            page.wait_for_function(
                "() => document.documentElement.classList.contains('rail-open')"
            )
            page.locator(f"{PINS} .pin-unpin").click()
            page.wait_for_function(
                "() => !document.documentElement.classList.contains('rail-open')",
                timeout=3000,
            )
        finally:
            ctx.close()


# The unpin icon takes the first line of the info zone, and a number in the
# same column (an equation's, a step's, a calc's) moves one line down.
_ICON_AND_NUMBERS = """b => {
    const icon = b.querySelector('.pin-unpin svg').getBoundingClientRect();
    const others = [...b.querySelectorAll('.eqn-number, .step-number, .hr-info-zone .hr-collapse')]
      .filter(e => e.getClientRects().length && !e.closest('.hide'))
      .map(e => { const r = e.getBoundingClientRect();
                  return {cls: e.className, top: r.top, bottom: r.bottom, left: r.left, right: r.right}; });
    return {icon: {top: icon.top, bottom: icon.bottom, left: icon.left, right: icon.right}, others};
}"""


def _assert_numbers_below_icon(copy, number_selector: str) -> None:
    geom = copy.evaluate(_ICON_AND_NUMBERS)
    icon = geom["icon"]
    for o in geom["others"]:
        overlap = not (
            o["bottom"] <= icon["top"] + 0.5
            or o["top"] >= icon["bottom"] - 0.5
            or o["right"] <= icon["left"] + 0.5
            or o["left"] >= icon["right"] - 0.5
        )
        assert not overlap, (o, icon)
    num = copy.locator(number_selector).first.bounding_box()
    assert num["y"] >= icon["bottom"] - 0.5, (num, icon)


class TestUnpinIconAndNumbers:
    def test_step_number_moves_below_the_icon(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _pin(page, "#st-1")
        copy = page.locator(f'{PINS}[data-pin-target="#st-1"]')
        copy.hover()
        _assert_numbers_below_icon(copy, ".step-number")

    def test_equation_number_moves_below_the_icon(
        self, page: Page, interactive_server: str
    ):
        page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{interactive_server}/pin_targets.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        _pin(page, "#eq-a")
        copy = page.locator(f'{PINS}[data-pin-target="#eq-a"]')
        copy.hover()
        _assert_numbers_below_icon(copy, ".eqn-number")

    def test_calc_number_and_reason_dots_move_below_the_icon(
        self, page: Page, interactive_server: str
    ):
        page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{interactive_server}/calc_preview.html")
        page.wait_for_function(RSM_READY, timeout=10_000)
        _pin(page, "#eq-chain")
        copy = page.locator(f'{PINS}[data-pin-target="#eq-chain"]')
        copy.hover()
        _assert_numbers_below_icon(copy, ".eqn-number")


class TestTouch:
    def test_unpin_icon_always_shown_on_touch(
        self, playwright, browser, interactive_server: str
    ):
        ctx = browser.new_context(**playwright.devices["iPhone 13"])
        page = ctx.new_page()
        try:
            page.goto(f"{interactive_server}/sidebar.html")
            page.wait_for_function(RSM_READY, timeout=10_000)
            theorem = page.locator(".manuscript .theorem").first
            theorem.scroll_into_view_if_needed()
            theorem.locator(":scope > .hr-border-zone .hr-border-dots").click()
            page.locator('#hr-menu-singleton [data-role="pin"]').click()
            icon = page.locator(f"{PINS} > .hr-info-zone .pin-unpin")
            expect(icon).to_have_css("opacity", "1")
        finally:
            ctx.close()


class TestPinFigures:
    """Figures can be pinned too: from a reference's preview and from the
    figure's own handrail menu. A figure's handrail sits on its caption."""

    def _load(self, page: Page, server: str) -> None:
        page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{server}/sidebar_figure.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

    def test_figure_reference_preview_pins_figure(
        self, page: Page, interactive_server: str
    ):
        self._load(page, interactive_server)
        _pin(page, "#fig-a")
        expect(page.locator(".rail-pinned-body img")).to_have_count(1)

    def test_pinned_figure_keeps_its_caption_handrail(
        self, page: Page, interactive_server: str
    ):
        self._load(page, interactive_server)
        _pin(page, "#fig-a")
        copy = page.locator(f'{PINS}[data-pin-target="#fig-a"]')
        cap = copy.locator(":scope > figcaption.hr")
        expect(cap.locator(":scope > .hr-border-zone .hr-border-dots")).to_have_count(1)
        expect(cap.locator(":scope > .hr-info-zone .pin-unpin")).to_have_count(1)

    def test_figure_handrail_menu_has_pin(self, page: Page, interactive_server: str):
        self._load(page, interactive_server)
        fig = page.locator("figure#fig-a")
        fig.scroll_into_view_if_needed()
        fig.hover()
        fig.locator(".hr-border-dots").first.click()
        item = page.locator('#hr-menu-singleton [data-role="pin"]')
        expect(item).to_be_visible()
        item.click()
        expect(page.locator(".proof-rail")).to_have_class(
            re.compile(r"\bscope-pinned\b")
        )
        expect(page.locator(".rail-pinned-body img")).to_have_count(1)
        expect(page.locator(".rail-pinned")).to_contain_text("Figure 1.1")


class TestPinProofs:
    def test_handrail_menu_pins_a_proof(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _open_menu(page, page.locator(".manuscript .proof.hr").first)
        page.locator('#hr-menu-singleton [data-role="pin"]').click()
        expect(page.locator(".proof-rail")).to_have_class(
            re.compile(r"\bscope-pinned\b")
        )
        expect(page.locator(".rail-pinned-body")).to_contain_text("First")


class TestPinTargets:
    """Every pinnable target has a handrail: on itself, as a direct child (a
    bibliography entry, a footnote), or on its caption (a figure, a table). The
    copy keeps that handrail, and the unpin icon sits in its info zone.
    Sections cannot be pinned."""

    def _load(self, page: Page, server: str) -> None:
        page.set_viewport_size({"width": 1400, "height": 900})
        page.goto(f"{server}/pin_targets.html")
        page.wait_for_function(RSM_READY, timeout=10_000)

    @pytest.mark.parametrize(
        "href, handrail, text",
        [
            ("#knuth", ":scope > .hr", "Knuth"),
            ("#fn-a", ":scope > .hr", "The footnote text."),
            ("#fig-a", ":scope > figcaption.hr", "A figure a reader can pin."),
            ("#tab-a", ":scope > figcaption.hr", "A table a reader can pin."),
        ],
    )
    def test_target_pins_with_its_handrail(
        self, page: Page, interactive_server: str, href: str, handrail: str, text: str
    ):
        self._load(page, interactive_server)
        _pin(page, href)
        copy = page.locator(f'{PINS}[data-pin-target="{href}"]')
        expect(copy).to_contain_text(text)
        hr = copy.locator(handrail)
        expect(hr).to_have_count(1)
        icon = hr.locator(":scope > .hr-info-zone .pin-unpin")
        expect(icon).to_have_count(1)
        copy.hover()
        icon.click()
        expect(page.locator(PINS)).to_have_count(0)

    def test_pinned_table_keeps_its_cells(self, page: Page, interactive_server: str):
        self._load(page, interactive_server)
        _pin(page, "#tab-a")
        copy = page.locator(f'{PINS}[data-pin-target="#tab-a"]')
        expect(copy.locator("table td")).to_have_count(2)

    def test_table_caption_menu_says_unpin_when_pinned(
        self, page: Page, interactive_server: str
    ):
        self._load(page, interactive_server)
        _pin(page, "#tab-a")
        cap = page.locator(".manuscript #tab-a + figcaption.hr")
        cap.scroll_into_view_if_needed()
        cap.hover()
        cap.locator(":scope > .hr-border-zone .hr-border-dots").click()
        assert _menu_pin_text(page) == "Unpin"
        page.locator('#hr-menu-singleton [data-role="pin"]').click()
        expect(page.locator(PINS)).to_have_count(0)

    def test_section_preview_has_no_pin_control(
        self, page: Page, interactive_server: str
    ):
        self._load(page, interactive_server)
        _hover_ref(page, "#sec-targets")
        expect(page.locator(".tooltipster-base").last).to_be_visible(timeout=3000)
        expect(page.locator('.ref-pin[data-pin-target="#sec-targets"]')).to_have_count(
            0
        )


class TestCopyLinkInPinnedCopy:
    """A pinned copy has no ids, so its menu offers no Copy link, for the pinned
    block or for any block inside it. The blocks in the text keep Copy link."""

    LINK = '#hr-menu-singleton [data-role="link"]'

    def test_pinned_block_has_no_copy_link(self, page: Page, interactive_server: str):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        _open_menu(page, page.locator(f'{PINS}[data-pin-target="#thm-x"]'))
        expect(page.locator(self.LINK)).to_be_hidden()

    def test_block_inside_a_pinned_copy_has_no_copy_link(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _open_menu(page, page.locator(".manuscript .proof.hr").first)
        page.locator('#hr-menu-singleton [data-role="pin"]').click()
        step = page.locator(f"{PINS} .step.hr").filter(has_text="First").first
        step.scroll_into_view_if_needed()
        step.hover()
        step.locator(":scope > .hr-border-zone .hr-border-dots").click()
        expect(page.locator("#hr-menu-singleton .hr-menu")).to_be_visible()
        expect(page.locator(self.LINK)).to_be_hidden()

    def test_block_in_the_text_keeps_copy_link(
        self, page: Page, interactive_server: str
    ):
        _load(page, interactive_server)
        _pin(page, "#thm-x")
        _open_menu(page, page.locator(f'{PINS}[data-pin-target="#thm-x"]'))
        page.keyboard.press("Escape")
        _open_menu(page, page.locator(".manuscript #thm-x"))
        expect(page.locator(self.LINK)).to_be_visible()
