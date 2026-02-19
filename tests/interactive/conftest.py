"""Pytest fixtures for interactive behavior tests.

These tests drive a real browser (via Playwright) against a running rsm serve
instance to verify JS behavior: toasts, tooltips, clipboard, and iframe contexts.
"""

import socket
import subprocess
import time
from contextlib import closing
from pathlib import Path
from subprocess import PIPE
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


@pytest.fixture(scope="session")
def interactive_server(tmp_path_factory: Any):
    """Build RSM fixtures, start rsm serve, yield base URL, tear down on exit."""
    serve_dir = tmp_path_factory.mktemp("interactive")

    fixtures_dir = Path(__file__).parent / "fixtures"
    for rsm_file in sorted(fixtures_dir.glob("*.rsm")):
        rsm.build(
            path=str(rsm_file),
            output_dir=str(serve_dir),
            output_filename=rsm_file.stem + ".html",
            write_output=True,
            handrails=True,
            standalone=False,
            strict=True,
        )

    _write_iframe_hosts(serve_dir)

    port = _find_free_port()
    proc = subprocess.Popen(
        ["uv", "run", "rsm", "serve", "--port", str(port), "--no-browser"],
        cwd=serve_dir,
        stdout=PIPE,
        stderr=PIPE,
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



@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict[str, Any]) -> dict[str, Any]:
    """Grant clipboard permissions so clipboard tests work outside sandboxed iframes."""
    return {
        **browser_context_args,
        "permissions": ["clipboard-read", "clipboard-write"],
    }
