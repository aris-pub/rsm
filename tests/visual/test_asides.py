"""Visual regression for asides (rsm-zvn.2, .3, .4).

Asides in the margin column when it fits, closed or opened below their block
when it does not, and open below their block without scripts. Baselines are
generated on Linux CI. The fixture is shared with tests/interactive/test_asides.py.
"""

import functools
import http.server
import shutil
import socketserver
import threading
from pathlib import Path

import pytest
from playwright.sync_api import Page

import rsm

FIXTURES = Path(__file__).parents[1] / "interactive" / "fixtures"
SRC = (FIXTURES / "asides.rsm").read_text()

# 1280 and 1440: the column fits. 768 and 375: it does not.
WIDTHS = [("wide-1440", 1440), ("desktop-1280", 1280), ("tablet-768", 768), ("mobile-375", 375)]
NARROW = WIDTHS[2:]
WIDE = WIDTHS[:2]


def _open(page: Page, serve_rsm_html, width: int, scheme: str):
    page.set_viewport_size({"width": width, "height": 900})
    page.emulate_media(color_scheme=scheme)
    serve_rsm_html(SRC, image_dir=FIXTURES, sidebar=True)
    page.mouse.move(1, 1)


def _shot(page: Page) -> bytes:
    page.mouse.move(1, 1)
    page.wait_for_timeout(300)
    return page.screenshot(full_page=True, animations="disabled")


def _top_shot(page: Page) -> bytes:
    page.evaluate("() => scrollTo(0, 0)")
    page.mouse.move(1, 1)
    page.wait_for_timeout(300)
    return page.screenshot(animations="disabled")


@pytest.mark.visual
class TestAsides:
    @pytest.mark.parametrize("scheme", ["light", "dark"])
    @pytest.mark.parametrize("name,width", WIDTHS)
    def test_at_rest(
        self, serve_rsm_html, page: Page, assert_snapshot, name, width, scheme
    ) -> None:
        """Wide: asides in the margin, pushed down past each other and the
        caption. Narrow: all closed, only the markers show."""
        _open(page, serve_rsm_html, width, scheme)
        assert_snapshot(_shot(page))

    @pytest.mark.parametrize("scheme", ["light", "dark"])
    @pytest.mark.parametrize("name,width", NARROW)
    def test_all_open(
        self, serve_rsm_html, page: Page, assert_snapshot, name, width, scheme
    ) -> None:
        """Every aside opened below its block, two of them in one paragraph."""
        _open(page, serve_rsm_html, width, scheme)
        for i in ["a-one", "a-two", "a-three", "a-fig", "a-item", "a-step",
                  "a-pair-2", "a-pair-1"]:
            page.click(f"#call-{i}")
        assert_snapshot(_shot(page))

    @pytest.mark.parametrize("scheme", ["light", "dark"])
    @pytest.mark.parametrize("name,width", NARROW)
    def test_one_open_and_lit(
        self, serve_rsm_html, page: Page, assert_snapshot, name, width, scheme
    ) -> None:
        """One aside open and its marker focused: both lit, the paragraph's
        rail running down past the aside."""
        _open(page, serve_rsm_html, width, scheme)
        page.click("#call-a-two")
        page.focus("#call-a-two")
        page.wait_for_timeout(300)
        assert_snapshot(page.screenshot(animations="disabled"))

    @pytest.mark.parametrize("scheme", ["light", "dark"])
    @pytest.mark.parametrize("name,width", WIDE)
    def test_lit_in_margin(
        self, serve_rsm_html, page: Page, assert_snapshot, name, width, scheme
    ) -> None:
        """Hovering an aside in the margin lights it, its marker, and the rail
        of the paragraph that calls it."""
        _open(page, serve_rsm_html, width, scheme)
        page.evaluate("() => scrollTo(0, 0)")
        page.hover("#a-two")
        page.wait_for_timeout(300)
        assert_snapshot(page.screenshot(animations="disabled"))

    @pytest.mark.parametrize("scheme", ["light", "dark"])
    @pytest.mark.parametrize("name,width", WIDE)
    def test_panel_open(
        self, serve_rsm_html, page: Page, assert_snapshot, name, width, scheme
    ) -> None:
        """With the Contents panel open the column no longer fits: asides close."""
        _open(page, serve_rsm_html, width, scheme)
        page.click('.rail-strip-btn[data-view="contents"]')
        page.wait_for_timeout(700)
        assert_snapshot(_top_shot(page))

    @pytest.mark.parametrize("measure", ["narrow", "normal", "wide"])
    def test_reading_width(
        self, serve_rsm_html, page: Page, assert_snapshot, measure
    ) -> None:
        """At 1440 with the Reading panel open: the column fits at Narrow and
        Normal, not at Wide."""
        _open(page, serve_rsm_html, 1440, "light")
        page.click('.rail-strip-btn[data-view="reading"]')
        page.wait_for_timeout(700)
        page.click(
            f'.reading-row[data-control="measure"] .reading-opt[data-value="{measure}"]'
        )
        page.wait_for_timeout(700)
        assert_snapshot(_top_shot(page))

    @pytest.mark.parametrize("scheme", ["light", "dark"])
    @pytest.mark.parametrize("name,width", [("desktop-1280", 1280), ("mobile-375", 375)])
    def test_hover_preview(
        self, serve_rsm_html, page: Page, assert_snapshot, name, width, scheme
    ) -> None:
        """On a pointer device without the column, hovering the marker of a
        closed aside previews it. At 1280 the panel is opened to take the
        column away."""
        _open(page, serve_rsm_html, width, scheme)
        if width >= 1000:
            page.click('.rail-strip-btn[data-view="contents"]')
            page.wait_for_timeout(700)
        page.evaluate("() => scrollTo(0, 0)")
        page.hover("#call-a-three")
        page.wait_for_timeout(800)
        assert_snapshot(page.screenshot(animations="disabled"))


def _serve_static(tmp_path: Path):
    """Build the fixture and serve it over HTTP without driving a page, for a
    browser context that has scripts turned off. Returns (url, server)."""
    src = tmp_path / "asides.rsm"
    src.write_text(SRC, encoding="utf-8")
    out = tmp_path / "output"
    out.mkdir(exist_ok=True)
    shutil.copy(FIXTURES / "figure-light.png", out / "figure-light.png")
    rsm.build(
        path=str(src),
        output_dir=str(out),
        output_filename="asides.html",
        write_output=True,
        handrails=True,
        standalone=False,
        strict=True,
        sidebar=True,
    )
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
    server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{server.server_address[1]}/asides.html", server


@pytest.mark.visual
class TestAsidesNoJS:
    @pytest.mark.parametrize("scheme", ["light", "dark"])
    @pytest.mark.parametrize("width", [375, 1280])
    def test_without_js(self, browser, assert_snapshot, tmp_path, width, scheme) -> None:
        """Without scripts every aside is open below its block."""
        url, server = _serve_static(tmp_path)
        ctx = browser.new_context(
            java_script_enabled=False,
            viewport={"width": width, "height": 900},
            color_scheme=scheme,
        )
        try:
            page = ctx.new_page()
            page.goto(url)
            page.wait_for_timeout(500)
            img = page.screenshot(full_page=True, animations="disabled")
        finally:
            ctx.close()
            server.shutdown()
            server.server_close()
        assert_snapshot(img)
