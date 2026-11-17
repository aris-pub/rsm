"""axe checks for the list/graph switch on the table of contents (rsm-ucv)."""

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect

SRC = (
    "# Contents switch\n\n"
    ":toc: {{\n  :view: {view}\n}}\n::\n\n"
    "## Introduction\n  {{:label: sec-intro}}\n\nIntro body.\n\n"
    "## Methods\n\nMethods body, after :ref:sec-intro::.\n"
)


@pytest.mark.accessibility
@pytest.mark.parametrize("view", ["list", "tree"])
@pytest.mark.parametrize("dark_theme", [False, True])
def test_toc_switch_passes_axe(serve_rsm_a11y, page: Page, view: str, dark_theme: bool):
    page = serve_rsm_a11y(SRC.format(view=view), dark_theme)
    expect(page.locator("nav.toc .toc-switch")).to_be_visible()
    # Hover the button of the view not on screen, so its hover colour is checked too.
    other = "list" if view == "tree" else "tree"
    page.locator(f".toc-switch button[data-toc-view='{other}']").hover()
    results = Axe().run(page, options={
        "runOnly": {
            "type": "tag",
            "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"],
        }
    })
    _assert_clean(results)


def _assert_clean(results):
    violations = results.response["violations"]
    assert violations == [], "\n".join(
        f"{v['id']}: {[n['target'] for n in v['nodes']]}" for v in violations
    )


@pytest.mark.accessibility
@pytest.mark.parametrize("view", ["list", "tree"])
@pytest.mark.parametrize("dark_theme", [False, True])
def test_sidebar_contents_switch_passes_axe(
    serve_rsm_a11y, page: Page, view: str, dark_theme: bool
):
    page.set_viewport_size({"width": 1400, "height": 900})
    page = serve_rsm_a11y(SRC.format(view=view), dark_theme, sidebar=True)
    page.locator('.rail-strip-btn[data-view="contents"]').click()
    expect(page.locator(".rail-toc-switch")).to_be_visible()
    results = Axe().run(page, options={
        "runOnly": {
            "type": "tag",
            "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"],
        }
    })
    _assert_clean(results)
