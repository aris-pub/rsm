"""Pytest fixtures for accessibility tests."""

import http.server
import socketserver
import threading
from pathlib import Path
from typing import Any, Callable

import pytest
import rsm


@pytest.fixture
def serve_rsm_a11y(page: Any, tmp_path: Path) -> Callable[[str, bool], Any]:
    """
    Fixture that serves RSM HTML for accessibility testing.

    Similar to serve_rsm_html from visual tests, but returns the page object
    for axe-core analysis rather than a locator for screenshots.

    Usage:
        def test_accessibility(serve_rsm_a11y):
            fixture = Path("fixtures/example.rsm").read_text()
            page = serve_rsm_a11y(fixture)
            # Run axe-core analysis on page

    Args:
        page: Playwright page fixture (injected by pytest-playwright)
        tmp_path: Pytest temporary path fixture

    Returns:
        Function that takes RSM source and optional dark_theme flag,
        returns the page object ready for accessibility analysis
    """

    # Start HTTP server on random available port
    handler = http.server.SimpleHTTPRequestHandler

    def _serve(rsm_source: str, dark_theme: bool = False) -> Any:
        # Write RSM source to temp file
        rsm_file = tmp_path / "test.rsm"
        rsm_file.write_text(rsm_source, encoding="utf-8")

        # Build complete HTML using rsm.build()
        output_dir = tmp_path / "output"
        output_dir.mkdir(exist_ok=True)

        rsm.build(
            path=str(rsm_file),
            output_dir=str(output_dir),
            output_filename="test.html",
            write_output=True,
            handrails=True,
            standalone=False,
            strict=True,
        )

        # Read the generated HTML file
        html_file = output_dir / "test.html"
        html_content = html_file.read_text()

        # Add dark theme class if requested
        if dark_theme:
            html_content = html_content.replace('<html lang="en"', '<html lang="en" class="dark-theme"')
            html_file.write_text(html_content)

        # Start HTTP server in background thread
        class ThreadedHTTPServer(socketserver.TCPServer):
            allow_reuse_address = True

        # Find available port
        with socketserver.TCPServer(("127.0.0.1", 0), handler) as s:
            port = s.server_address[1]

        # Create server serving the output directory
        import os
        original_dir = os.getcwd()
        os.chdir(output_dir)

        server = ThreadedHTTPServer(("127.0.0.1", port), handler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        try:
            # Navigate to the file using HTTP
            page.goto(f"http://127.0.0.1:{port}/test.html")

            # Wait for RSM JavaScript initialization to complete
            page.wait_for_function("() => window.__rsmInitialized === true", timeout=10000)

            # Wait for fonts to load
            page.evaluate("() => document.fonts.ready")

            # Wait for rendering to complete
            page.wait_for_timeout(1500)

            # Return the page object for axe analysis
            return page
        finally:
            server.shutdown()
            os.chdir(original_dir)

    return _serve
