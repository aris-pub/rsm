"""Pytest fixtures for visual regression tests."""

import http.server
import socketserver
import threading
from pathlib import Path
from typing import Any, Callable

import pytest
import rsm


# Override default threshold to tolerate sub-pixel rendering variance under parallel execution
@pytest.fixture
def assert_snapshot(pytestconfig: Any, request: Any, browser_name: str) -> Callable:
    """Override pytest-playwright-visual's assert_snapshot with higher threshold.

    Increases threshold from 0.1 to 0.2 to tolerate minor anti-aliasing and font hinting
    differences that occur under CPU contention during parallel test execution.
    """
    import sys
    import os
    import shutil
    from io import BytesIO
    from pathlib import Path
    from PIL import Image
    from pixelmatch.contrib.PIL import pixelmatch

    test_name = str(Path(request.node.name))
    test_dir = str(Path(request.node.name)).split('[', 1)[0]

    def compare(img: bytes, *, threshold: float = 0.2, name=f'{test_name}.png', fail_fast=False, max_diff_pixels: int = 0) -> None:
        update_snapshot = pytestconfig.getoption("--update-snapshots")
        test_file_name = str(os.path.basename(Path(request.node.fspath))).strip('.py')
        filepath = (
                Path(request.node.fspath).parent.resolve()
                / 'snapshots'
                / test_file_name
                / test_dir
        )
        filepath.mkdir(parents=True, exist_ok=True)
        file = filepath / name
        results_dir_name = (Path(request.node.fspath).parent.resolve()
                            / "snapshot_tests_failures")
        test_results_dir = (results_dir_name
                            / test_file_name / test_name)
        if test_results_dir.exists():
            shutil.rmtree(test_results_dir)
        if update_snapshot:
            file.write_bytes(img)
            pytest.fail("--> Snapshots updated. Please review images")
        if not file.exists():
            file.write_bytes(img)
            pytest.fail("--> New snapshot(s) created. Please review images")
        img_a = Image.open(BytesIO(img))
        img_b = Image.open(file)
        img_diff = Image.new("RGBA", img_a.size)
        # fail_fast off so pixelmatch counts every differing pixel for the budget.
        # max_diff_pixels stays 0 by default (exact match), so most tests are
        # unchanged; callers opt into a small budget only where justified.
        mismatch = pixelmatch(img_a, img_b, img_diff, threshold=threshold, fail_fast=False)
        if mismatch <= max_diff_pixels:
            return
        else:
            test_results_dir.mkdir(parents=True, exist_ok=True)
            img_diff.save(f'{test_results_dir}/Diff_{name}')
            img_a.save(f'{test_results_dir}/Actual_{name}')
            img_b.save(f'{test_results_dir}/Expected_{name}')
            pytest.fail(
                f"--> Snapshots DO NOT match! {mismatch} px differ (budget {max_diff_pixels})"
            )

    return compare


# Viewport configurations aligned with BRAIID responsive breakpoints
# Mobile-first approach: 12px base (< 640px), 14px (640px+), 16px (1024px+)
VIEWPORTS = [
    ("mobile", 375, 667),    # iPhone SE - tests mobile default (12px base)
    ("tablet", 768, 1024),   # iPad - tests sm breakpoint (14px base, 640px-1024px)
    ("desktop", 1280, 720),  # Standard desktop - tests lg breakpoint (16px base, 1024px+)
]


@pytest.fixture
def serve_rsm_html(page: Any, tmp_path: Path) -> Callable[[str, bool], Any]:
    """
    Fixture that serves RSM HTML to a Playwright page and returns the content element.

    Usage:
        def test_example(serve_rsm_html):
            fixture = Path("fixtures/example.rsm").read_text()
            content = serve_rsm_html(fixture)
            content.screenshot(path="test.png")

    Args:
        page: Playwright page fixture (injected by pytest-playwright)
        tmp_path: Pytest temporary path fixture

    Returns:
        Function that takes RSM source and optional dark_theme flag,
        returns the body element locator for screenshots
    """

    # Start HTTP server on random available port
    handler = http.server.SimpleHTTPRequestHandler

    def _serve(rsm_source: str, dark_theme: bool = False, image_dir: Path | None = None) -> Any:
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

        # Copy extra asset files (e.g. images) so the HTTP server can serve them
        if image_dir is not None:
            import shutil
            for img in image_dir.iterdir():
                if img.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}:
                    shutil.copy(img, output_dir / img.name)

        # Read the generated HTML file
        html_file = output_dir / "test.html"
        html_content = html_file.read_text()

        # Add dark theme class if requested
        if dark_theme:
            html_content = html_content.replace("<html>", '<html class="dark-theme">')
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

            # Wait for fonts to fully load, including dynamically-injected @font-face
            # rules (e.g. Temml.css). A single document.fonts.ready check is unreliable
            # here: if the CSS hasn't been parsed yet, status is trivially 'loaded'
            # because no font loads are pending. The double-ready pattern gives the
            # browser a tick to discover newly-injected @font-face rules.
            page.wait_for_function("""async () => {
                await document.fonts.ready;
                await new Promise(r => setTimeout(r, 100));
                await document.fonts.ready;
                return document.fonts.status === 'loaded';
            }""", timeout=15000)

            # Wait for rendering (CSS transitions, layout reflow after font swap)
            page.wait_for_timeout(1500)

            # Return the body element for clean screenshots
            return page.locator("body")
        finally:
            server.shutdown()
            os.chdir(original_dir)

    return _serve


def pytest_collection_modifyitems(config: Any, items: list[Any]) -> None:
    """Group desktop tests to reduce CPU contention during parallel execution.

    Desktop tests have 16+ MathJax formulas and render significantly more content,
    causing CPU contention when run in parallel with 8 workers. By grouping them,
    pytest-xdist ensures they run on dedicated workers with less competition.
    """
    for item in items:
        if "desktop-1280-720" in item.nodeid:
            item.add_marker(pytest.mark.xdist_group(name="desktop_only"))


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict[str, Any]) -> dict[str, Any]:
    """Configure browser context for consistent visual testing."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "device_scale_factor": 1,
    }
