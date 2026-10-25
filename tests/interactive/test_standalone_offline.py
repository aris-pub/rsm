"""The standalone build renders offline with braiid.css, jQuery and tooltipster
JS inlined, so it needs no network for those (rsm-nyg piece 1)."""

import pytest
from playwright.sync_api import Page

import rsm

pytestmark = pytest.mark.interactive

SRC = (
    ":rsm:\n\n# Hello\n\n"
    "A paragraph with a :ref:thm:: link.\n\n"
    ":theorem: {:label: thm}\n  A statement. ::\n\n::"
)


def test_standalone_renders_offline_with_inlined_assets(page: Page, tmp_path):
    html = rsm.build(SRC, handrails=True, lint=False, standalone=True)
    out = tmp_path / "standalone.html"
    out.write_text(html)

    blocked: list[str] = []

    def handle(route):
        url = route.request.url
        if url.startswith(("http://", "https://")):
            blocked.append(url)
            route.abort()
        else:
            route.continue_()

    page.route("**/*", handle)
    page.goto(out.as_uri(), wait_until="load")
    page.wait_for_timeout(500)

    # braiid.css applied from the inline <style>, with no network: a reference
    # link takes braiid's --link-default (blue-700), not the UA default blue.
    link_color = page.eval_on_selector("a.reference", "a => getComputedStyle(a).color")
    assert link_color == "rgb(3, 97, 161)", link_color
    assert page.eval_on_selector(
        ".manuscriptwrapper", "e => getComputedStyle(e).maxWidth"
    ) != "none"

    # jQuery is inlined and live.
    assert page.evaluate("() => typeof window.jQuery") == "function"

    # None of the inlined libraries were fetched over the network.
    fetched = [
        u for u in blocked
        if any(k in u.lower() for k in ("jquery", "braiid", "tooltipster.bundle.js"))
    ]
    assert not fetched, fetched
