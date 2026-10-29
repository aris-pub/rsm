"""A standard build served from a subfolder (here /a/b/) loads its scripts,
CSS, figures and math, because every link is relative to the page (rsm-3wf).
Temml and pseudocode.js come from static/, not from a CDN (rsm-nyg.2)."""

import functools
import http.server
import threading
from pathlib import Path

import pytest
from playwright.sync_api import Page

import rsm

pytestmark = pytest.mark.interactive

SRC = """# Subfolder

Inline math $x + y$ and display math:

$$
\\sum_{i=1}^n i = \\frac{n(n+1)}{2}
$$

:figure: {
  :path: figs/plot.svg
  :label: fig-plot
}
:caption: A plot.
::

:html: {
  :path: figs/widget.html
  :label: fig-widget
}

  :caption: A widget.
::

:algorithm:
\\begin{algorithm}
\\caption{Euclid}
\\begin{algorithmic}
\\PROCEDURE{Euclid}{$a, b$}
    \\RETURN $a$
\\ENDPROCEDURE
\\end{algorithmic}
\\end{algorithm}
::
"""

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="20">'
    '<rect width="40" height="20" fill="#36c"/></svg>'
)
WIDGET = '<div id="widget"><img id="inner" src="figs/inner.svg" alt="inner"></div>'
CSS = "body { --subpath-marker: 7; }\n"

# The Temml.css link 404s and belongs to rsm-r3u, so it is not counted here.
R3U_TEMML_CSS = "https://cdn.jsdelivr.net/npm/temml/dist/Temml.css"
PINNED_TEMML_CDN = "https://cdn.jsdelivr.net/npm/temml@0.14.0/dist/temml.min.js"


@pytest.fixture
def subpath_site(tmp_path, monkeypatch):
    """Build into <root>/a/b/ and serve <root>. Yields the page URL."""
    src = tmp_path / "src"
    (src / "figs").mkdir(parents=True)
    (src / "figs" / "plot.svg").write_text(SVG)
    (src / "figs" / "inner.svg").write_text(SVG)
    (src / "figs" / "widget.html").write_text(WIDGET)
    (src / "paper.css").write_text(CSS)
    (src / "paper.rsm").write_text(SRC)

    root = tmp_path / "site"
    monkeypatch.chdir(src)
    rsm.build(
        path="paper.rsm",
        output_dir=str(root / "a" / "b"),
        output_filename="index.html",
        write_output=True,
        handrails=True,
        standalone=False,
        custom_css="paper.css",
    )

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(root)
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/a/b/index.html"
    finally:
        server.shutdown()
        server.server_close()


def _watch(page: Page):
    """Abort every request to jsDelivr or cdnjs and record it, and record
    local responses that failed."""
    cdn: list[str] = []
    failed: list[str] = []

    def handle(route):
        cdn.append(route.request.url)
        route.abort()

    page.route("https://cdn.jsdelivr.net/**", handle)
    page.route("https://cdnjs.cloudflare.com/**", handle)
    page.on(
        "response",
        lambda r: r.url.startswith("http://127.0.0.1") and r.status >= 400
        and failed.append(f"{r.status} {r.url}"),
    )
    return cdn, failed


def _wait_ready(page: Page):
    page.wait_for_function("() => window.__rsmInitialized === true", timeout=15_000)
    page.wait_for_function(
        "() => document.querySelector('.ps-root') && document.querySelectorAll('math').length >= 2",
        timeout=15_000,
    )


def test_page_works_under_a_subfolder(page: Page, subpath_site: str):
    cdn, failed = _watch(page)
    page.goto(subpath_site, wait_until="load")
    _wait_ready(page)

    assert not failed, failed
    # No math library came from a CDN.
    assert [u for u in cdn if u != R3U_TEMML_CSS] == [], cdn

    # braiid.css applied: the manuscript column has braiid's width cap.
    assert page.evaluate(
        "() => getComputedStyle(document.querySelector('.manuscriptwrapper')).maxWidth"
    ) != "none"
    # The author CSS from assets/ applied.
    assert page.evaluate(
        "() => getComputedStyle(document.body).getPropertyValue('--subpath-marker').trim()"
    ) == "7"
    # jQuery and tooltipster from static/.
    assert page.evaluate("() => typeof window.jQuery") == "function"
    assert page.evaluate("() => typeof window.jQuery.fn.tooltipster") == "function"

    # Figures from assets/, including one referenced inside an inlined widget.
    images = page.evaluate(
        """() => [...document.querySelectorAll('img')].map(i => ({
             src: i.getAttribute('src'), ok: i.complete && i.naturalWidth > 0 }))"""
    )
    assert {i["src"] for i in images} >= {"assets/figs/plot.svg", "assets/figs/inner.svg"}
    assert all(i["ok"] for i in images), images

    # Math by Temml from static/, algorithm by pseudocode.js from static/.
    loaded = page.evaluate(
        "() => performance.getEntriesByType('resource').map(e => e.name)"
    )
    assert any(u.endswith("/a/b/static/temml-0.14.0.min.js") for u in loaded), loaded
    assert any(u.endswith("/a/b/static/pseudocode-2.4.1.min.js") for u in loaded), loaded
    assert any(u.endswith("/a/b/static/pseudocode-2.4.1.min.css") for u in loaded), loaded
    assert page.evaluate("() => typeof window.temml.render") == "function"
    assert page.evaluate("() => window.katex === window.temml")
    assert page.locator(".ps-root .ps-funcname").first.inner_text().lower() == "euclid"


def test_temml_falls_back_to_the_pinned_cdn(page: Page, subpath_site: str):
    """When static/ lacks the vendored file, libraries.js loads the pinned CDN
    copy. The CDN is stubbed with the vendored file, so no network is used."""
    cdn: list[str] = []
    vendored = (Path(rsm.__file__).parent / "static" / "temml-0.14.0.min.js").read_text()

    def handle_cdn(route):
        url = route.request.url
        cdn.append(url)
        if url == PINNED_TEMML_CDN:
            route.fulfill(body=vendored, content_type="application/javascript")
        else:
            route.abort()

    page.route("**/static/temml-0.14.0.min.js", lambda route: route.abort())
    page.route("https://cdn.jsdelivr.net/**", handle_cdn)
    page.route("https://cdnjs.cloudflare.com/**", handle_cdn)
    page.goto(subpath_site, wait_until="load")
    _wait_ready(page)

    assert PINNED_TEMML_CDN in cdn, cdn
    assert page.evaluate("() => document.querySelectorAll('math').length") >= 2
