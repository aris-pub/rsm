"""Pytest fixtures for interactive behavior tests.

These tests drive a real browser (via Playwright) against a running static
file server to verify JS behavior: toasts, tooltips, clipboard, and iframe contexts.
"""

import contextlib
import functools
import http.server
import os
import threading
from pathlib import Path
from typing import Any

import pytest

import rsm


class _Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    # The default of 5 is too small: Chromium opens many connections at once
    # for a page's scripts and styles, and the ones that overflow wait for a
    # TCP retry, so the page loads seconds late and tests time out.
    request_queue_size = 128


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


@contextlib.contextmanager
def _chdir(path: Path):
    # contextlib.chdir needs Python 3.11 and the project supports 3.10.
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def _write_iframe_hosts(serve_dir: Path) -> None:
    """Write host pages that embed basic.html in an iframe."""
    # Mirrors the RSM Sphinx docs: sandbox="allow-scripts allow-same-origin"
    (serve_dir / "iframe-sandboxed.html").write_text(
        '<!DOCTYPE html><html><body style="margin:0">'
        '<iframe id="rsm-frame" src="basic.html"'
        ' sandbox="allow-scripts allow-same-origin"'
        ' style="width:100%;height:100vh;border:none;"></iframe>'
        "</body></html>"
    )
    # Mirrors Press: no sandbox attribute
    (serve_dir / "iframe-unsandboxed.html").write_text(
        '<!DOCTYPE html><html><body style="margin:0">'
        '<iframe id="rsm-frame" src="basic.html"'
        ' style="width:100%;height:100vh;border:none;"></iframe>'
        "</body></html>"
    )


# Fixtures built with the reader sidebar (`rsm build --sidebar`).
SIDEBAR_FIXTURES = {
    "wide-math-in-paragraph",
    "sidebar",
    "sidebar_figure",
    "sidebar_long",
    "collapsed",
    "deplens",
    "reorder",
    "minimap",
    "margin_captions",
    "asides",
    "shareview_long",
    "widget_preview",
    "calc_preview",
    "rawhtml",
    "toc_switch_sidebar",
}

# Fixtures whose :html: assets must be read at build time. Asset paths resolve
# from the working directory, so these build from inside the fixtures folder.
ASSET_FIXTURES = {"minimap"}


@pytest.fixture(scope="session")
def interactive_server(tmp_path_factory: Any):
    """Build RSM fixtures, start rsm serve, yield base URL, tear down on exit."""
    serve_dir = tmp_path_factory.mktemp("interactive")

    fixtures_dir = Path(__file__).parent / "fixtures"
    for rsm_file in sorted(fixtures_dir.glob("*.rsm")):
        cwd = fixtures_dir if rsm_file.stem in ASSET_FIXTURES else Path.cwd()
        with _chdir(cwd):
            rsm.build(
                path=str(rsm_file),
                output_dir=str(serve_dir),
                output_filename=rsm_file.stem + ".html",
                write_output=True,
                handrails=True,
                standalone=False,
                strict=True,
                sidebar=rsm_file.stem in SIDEBAR_FIXTURES,
            )

    # Copy image assets so figures can render. Most fixtures build from the
    # repo root, where their media is not found, so it goes into assets/ here,
    # where the standard build links it from.
    import shutil
    (serve_dir / "assets").mkdir(exist_ok=True)
    for img in fixtures_dir.iterdir():
        if img.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".webm", ".mp4"}:
            shutil.copy(img, serve_dir / "assets" / img.name)

    _write_iframe_hosts(serve_dir)

    # A plain static server, not `rsm serve`: livereload reloads every
    # connected page once about 3 seconds after it starts, which interrupts
    # whichever test is loading a page at that moment.
    handler = functools.partial(_QuietHandler, directory=str(serve_dir))
    httpd = _Server(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict[str, Any]) -> dict[str, Any]:
    """Grant clipboard permissions so clipboard tests work outside sandboxed iframes."""
    return {
        **browser_context_args,
        "permissions": ["clipboard-read", "clipboard-write"],
    }
