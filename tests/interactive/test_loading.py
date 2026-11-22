"""Pages load behind a spinner and are shown once, when their layout has
settled (rsm-hc8).

While a page loads, its title, author block and abstract show, and a spinner
stands where the rest of the content goes. Once RSM has typeset the math, laid
out the page and applied a shared view or a #target, the rest is shown at once
with a fade. With JavaScript off nothing is hidden. If loading gets stuck, the
page is shown anyway after 3 seconds.

The page's load event is held back here by an image that the test serves
slowly, so the loading state can be seen."""

import time

import pytest
from playwright.sync_api import Page, expect

import rsm

pytestmark = pytest.mark.interactive

SLOW_IMG = "http://slow.test/pixel.png"
PIXEL = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000154a24f5d00000000"
    "49454e44ae426082"
)

SECTIONS = "\n\n".join(
    f"## Section {i}\n{{:label: sec-{i}}}\n\n"
    + "\n\n".join(
        f"Paragraph {i}.{j} with $x_{{{i}}} + y^{{{j}}}$ in it." for j in range(8)
    )
    for i in range(1, 7)
)

DOC = f"""# A loading test

:author: {{:name: Ada}}
::

:abstract:
  An abstract with $a^2 + b^2$.
::

:toc: ::

## Start

Text with a slow picture :html:{{:alt: a pixel}} <img src="{SLOW_IMG}" width="1" height="1"> ::.

{SECTIONS}
"""

REVEALED = (
    "() => window.__rsmShown === true"
    " && !document.documentElement.classList.contains('rsm-loading')"
)


def _build(tmp_path, src: str = DOC, sidebar: bool = True):
    out = tmp_path / "page.html"
    out.write_text(
        rsm.build(src, handrails=True, lint=False, standalone=True, sidebar=sidebar)
    )
    return out.as_uri()


class _HeldImage:
    """Holds the page's image request, and with it the page's load event, until
    release() is called. A route handler that sleeps would hold the test too."""

    def __init__(self, page: Page):
        self.routes = []
        page.route(SLOW_IMG, lambda route: self.routes.append(route))

    def release(self) -> None:
        for route in self.routes:
            route.fulfill(status=200, content_type="image/png", body=PIXEL)
        self.routes.clear()


def _goto_held(page: Page, url: str) -> _HeldImage:
    held = _HeldImage(page)
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(300)
    return held


def _goto_and_release(page: Page, url: str) -> None:
    _goto_held(page, url).release()


def _spinner_shown(page: Page) -> bool:
    """The spinner has no height of its own; its circle is its ::before."""
    return page.eval_on_selector(
        ".rsm-loading-spinner",
        """el => {
          const b = getComputedStyle(el, '::before');
          return getComputedStyle(el).display !== 'none' && b.content !== 'none'
            && parseFloat(b.width) > 0 && b.visibility === 'visible';
        }""",
    )


def _visibility(page: Page, selector: str) -> str:
    return page.eval_on_selector(selector, "el => getComputedStyle(el).visibility")


def test_title_and_abstract_show_while_the_rest_waits(page: Page, tmp_path):
    page.set_viewport_size({"width": 1400, "height": 900})
    held = _goto_held(page, _build(tmp_path))
    assert page.evaluate(
        "() => document.documentElement.classList.contains('rsm-loading')"
    )
    assert _visibility(page, ".manuscript h1") == "visible"
    assert _visibility(page, ".manuscript .author-block") == "visible"
    assert _visibility(page, ".manuscript .abstract") == "visible"
    assert _visibility(page, "#sec-1") == "hidden"
    assert _visibility(page, ".manuscript nav.toc") == "hidden"
    assert _spinner_shown(page)
    # The spinner sits below the abstract.
    abstract_bottom = page.eval_on_selector(
        ".abstract", "el => el.getBoundingClientRect().bottom"
    )
    spinner_top = page.eval_on_selector(
        ".rsm-loading-spinner", "el => el.getBoundingClientRect().top"
    )
    assert spinner_top >= abstract_bottom - 1
    held.release()


def test_the_rest_shows_once_the_page_is_ready(page: Page, tmp_path):
    _goto_and_release(page, _build(tmp_path))
    page.wait_for_function(REVEALED, timeout=10_000)
    assert _visibility(page, "#sec-1") == "visible"
    expect(page.locator(".rsm-loading-spinner")).to_be_hidden()


def test_nothing_moves_after_the_reveal(page: Page, tmp_path):
    page.set_viewport_size({"width": 1400, "height": 900})
    _goto_and_release(page, _build(tmp_path))
    page.wait_for_function(REVEALED, timeout=10_000)
    tops = set()
    for _ in range(15):
        tops.add(
            page.evaluate(
                "() => [document.documentElement.scrollHeight,"
                " Math.round(document.getElementById('sec-4').getBoundingClientRect().top + scrollY)].join()"
            )
        )
        page.wait_for_timeout(100)
    assert len(tops) == 1, tops


def test_a_hash_link_lands_on_its_target_and_stays(page: Page, tmp_path):
    page.set_viewport_size({"width": 1400, "height": 900})
    _goto_and_release(page, _build(tmp_path) + "#sec-4")
    page.wait_for_function(REVEALED, timeout=10_000)
    first = page.eval_on_selector("#sec-4", "el => el.getBoundingClientRect().top")
    assert 0 <= first < 200, first
    page.wait_for_timeout(1000)
    later = page.eval_on_selector("#sec-4", "el => el.getBoundingClientRect().top")
    assert abs(later - first) <= 1, (first, later)
    assert page.evaluate("() => document.activeElement.id") == "sec-4"


def test_a_stuck_load_shows_the_page_after_3_seconds(page: Page, tmp_path):
    held = _HeldImage(page)
    page.goto(_build(tmp_path), wait_until="commit")
    t0 = time.time()
    page.wait_for_function(
        "() => document.documentElement.classList.contains('rsm-loading')",
        timeout=3_000,
    )
    page.wait_for_function(
        "() => !document.documentElement.classList.contains('rsm-loading')",
        timeout=6_000,
    )
    waited = time.time() - t0
    assert 2.5 <= waited <= 4.5, waited
    assert _visibility(page, "#sec-1") == "visible"
    held.release()


def test_without_javascript_nothing_is_hidden(browser, tmp_path):
    url = _build(tmp_path)
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()
    page.route(
        SLOW_IMG,
        lambda route: route.fulfill(status=200, content_type="image/png", body=PIXEL),
    )
    page.goto(url)
    assert not page.evaluate(
        "() => document.documentElement.classList.contains('rsm-loading')"
    )
    assert _visibility(page, "#sec-1") == "visible"
    expect(page.locator(".rsm-loading-spinner")).to_be_hidden()
    context.close()


def test_reduced_motion_has_no_fade(page: Page, tmp_path):
    page.emulate_media(reduced_motion="reduce")
    _goto_and_release(page, _build(tmp_path))
    page.wait_for_function(REVEALED, timeout=10_000)
    assert (
        page.eval_on_selector("#sec-1", "el => getComputedStyle(el).animationName")
        == "none"
    )


@pytest.mark.parametrize(
    "head, before",
    [
        ("# T\n\n:author: {:name: Ada}\n::\n\n", ".author-block"),
        ("# T\n\n", ".manuscript h1"),
    ],
    ids=["no-abstract", "title-only"],
)
def test_the_spinner_follows_the_last_part_of_the_header(
    page: Page, tmp_path, head, before
):
    src = head + f'## One\n\nText :html:{{:alt: a pixel}} <img src="{SLOW_IMG}"> ::.\n'
    held = _goto_held(page, _build(tmp_path, src))
    assert _visibility(page, before) == "visible"
    assert _visibility(page, ".manuscript section.level-2") == "hidden"
    assert _spinner_shown(page)
    held.release()


def test_a_page_without_the_sidebar_loads_the_same_way(page: Page, tmp_path):
    held = _goto_held(page, _build(tmp_path, sidebar=False))
    assert _visibility(page, "#sec-1") == "hidden"
    held.release()
    page.wait_for_function(REVEALED, timeout=10_000)
    assert _visibility(page, "#sec-1") == "visible"


def test_the_spinner_takes_no_room(page: Page, tmp_path):
    # Nothing below the header may move when the spinner goes.
    page.set_viewport_size({"width": 1400, "height": 900})
    held = _goto_held(page, _build(tmp_path))
    before = page.eval_on_selector(
        "#sec-1", "el => el.getBoundingClientRect().top + scrollY"
    )
    held.release()
    page.wait_for_function(REVEALED, timeout=10_000)
    after = page.eval_on_selector(
        "#sec-1", "el => el.getBoundingClientRect().top + scrollY"
    )
    assert abs(after - before) <= 1, (before, after)
