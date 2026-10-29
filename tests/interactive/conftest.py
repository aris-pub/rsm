"""Pytest fixtures for interactive behavior tests.

These tests drive a real browser (via Playwright) against a running rsm serve
instance to verify JS behavior: toasts, tooltips, clipboard, and iframe contexts.
"""

import contextlib
import os
import socket
import subprocess
import time
from contextlib import closing
from pathlib import Path
from typing import Any

import pytest
import rsm


def _find_free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with closing(socket.create_connection(("127.0.0.1", port), timeout=0.5)):
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError(f"rsm serve did not start on port {port} within {timeout}s")


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

    port = _find_free_port()
    # The server's output goes to a file, never to an unread pipe. livereload
    # logs a line for every page that connects, and once an unread pipe's buffer
    # is full (64KB on Linux) that write blocks and the whole server freezes, so
    # every later page load times out.
    log = open(serve_dir / "rsm-serve.log", "w")
    proc = subprocess.Popen(
        ["uv", "run", "rsm", "serve", "--port", str(port), "--no-browser"],
        cwd=serve_dir,
        stdout=log,
        stderr=subprocess.STDOUT,
    )

    try:
        _wait_for_server(port)
        yield f"http://127.0.0.1:{port}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()



@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict[str, Any]) -> dict[str, Any]:
    """Grant clipboard permissions so clipboard tests work outside sandboxed iframes."""
    return {
        **browser_context_args,
        "permissions": ["clipboard-read", "clipboard-write"],
    }
