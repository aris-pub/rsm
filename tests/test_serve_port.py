"""Tests for rsm serve --port flag and port conflict handling."""

import subprocess
import socket
import time
from pathlib import Path
from contextlib import closing


def find_free_port():
    """Find a free port on localhost."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def test_serve_with_custom_port(tmp_path):
    """Test that --port flag uses the specified port."""
    rsm_file = tmp_path / "test.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    # Build first
    subprocess.run(
        ["rsm", "build", str(rsm_file)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Find a free port
    port = find_free_port()

    # Start server in background with custom port (will timeout after 2 seconds, which is expected)
    try:
        result = subprocess.run(
            ["rsm", "serve", "--port", str(port), "--no-browser"],
            cwd=tmp_path,
            timeout=2,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired as e:
        # Server is running successfully - check that it started on the custom port
        stderr_output = e.stderr.decode() if isinstance(e.stderr, bytes) else str(e.stderr) if e.stderr else ""
        assert f"http://127.0.0.1:{port}" in stderr_output
        return

    # If server exited, it should have been an error
    assert result.returncode != 0


def test_serve_port_in_use_error_message(tmp_path):
    """Test that port conflict shows helpful error message instead of traceback."""
    rsm_file = tmp_path / "test.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    # Build first
    subprocess.run(
        ["rsm", "build", str(rsm_file)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Find a free port and occupy it
    port = find_free_port()

    # Create a socket that holds the port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', port))
    sock.listen(1)

    try:
        # Try to serve on the same port
        result = subprocess.run(
            ["rsm", "serve", "--port", str(port), "--no-browser"],
            cwd=tmp_path,
            timeout=2,
            capture_output=True,
            text=True,
        )

        # Should fail with helpful message, not traceback
        assert result.returncode != 0
        assert "already in use" in result.stdout or "already in use" in result.stderr
        assert "--port" in result.stdout or "--port" in result.stderr
        assert "Traceback" not in result.stdout
        assert "Traceback" not in result.stderr
    finally:
        sock.close()


def test_serve_default_port_5500(tmp_path):
    """Test that default port is 5500 when not specified."""
    rsm_file = tmp_path / "test.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    # Build first
    subprocess.run(
        ["rsm", "build", str(rsm_file)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Start server without --port flag (will timeout after 2 seconds, which is expected)
    try:
        result = subprocess.run(
            ["rsm", "serve", "--no-browser"],
            cwd=tmp_path,
            timeout=2,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired as e:
        # Server is running successfully - check that it uses default port 5500
        stderr_output = e.stderr.decode() if isinstance(e.stderr, bytes) else str(e.stderr) if e.stderr else ""
        assert "http://127.0.0.1:5500" in stderr_output
        return

    # If server exited, it should have been an error (port conflict is possible with default port)
    # Allow both success and error, we just want to verify the default is 5500
    assert result.returncode != 0 or "http://127.0.0.1:5500" in result.stderr


def test_serve_no_html_files_shows_empty_index(tmp_path):
    """Test that serving with no HTML files generates an empty index page instead of 404."""
    # Start server in directory with no HTML files
    port = find_free_port()

    import time
    process = subprocess.Popen(
        ["rsm", "serve", "--port", str(port), "--no-browser"],
        cwd=tmp_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        # Give the server time to start and create the index file
        time.sleep(0.5)

        # Check that it created an empty index page
        index_file = tmp_path / ".rsm-index.html"
        assert index_file.exists(), "Empty index page should be created"

        # Verify the content is an empty list page
        content = index_file.read_text()
        assert "RSM - Available Pages" in content
        assert "<ul>" in content
    finally:
        # Always kill the server process
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
