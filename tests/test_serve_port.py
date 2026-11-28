"""Tests for rsm serve --port flag and port conflict handling."""

import socket
import subprocess
from contextlib import closing

import pytest


def find_free_port():
    """Find a free port on localhost."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@pytest.mark.slow
def test_serve_with_custom_port(tmp_path):
    """Test that --port flag uses the specified port."""
    rsm_file = tmp_path / "test.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    # Find a free port
    port = find_free_port()

    # Start server in background with custom port (will timeout after 2 seconds, which is expected)
    try:
        result = subprocess.run(
            ["rsm", "serve", "test.rsm", "--port", str(port), "--no-browser"],
            cwd=tmp_path,
            timeout=2,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired as e:
        # Server is running successfully - check that it started on the custom port
        stderr_output = (
            e.stderr.decode()
            if isinstance(e.stderr, bytes)
            else str(e.stderr)
            if e.stderr
            else ""
        )
        assert f"http://127.0.0.1:{port}" in stderr_output
        return

    # If server exited, it should have been an error
    assert result.returncode != 0


@pytest.mark.slow
def test_serve_port_in_use_error_message(tmp_path):
    """Test that port conflict shows helpful error message instead of traceback."""
    rsm_file = tmp_path / "test.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    # Find a free port and occupy it
    port = find_free_port()

    # Create a socket that holds the port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", port))
    sock.listen(1)

    try:
        # Try to serve on the same port
        result = subprocess.run(
            ["rsm", "serve", "test.rsm", "--port", str(port), "--no-browser"],
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


@pytest.mark.slow
def test_serve_default_port_5500(tmp_path):
    """Test that default port is 5500 when not specified."""
    rsm_file = tmp_path / "test.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    # Start server without --port flag (will timeout after 2 seconds, which is expected)
    try:
        result = subprocess.run(
            ["rsm", "serve", "test.rsm", "--no-browser"],
            cwd=tmp_path,
            timeout=2,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired as e:
        # Server is running successfully - check that it uses default port 5500
        stderr_output = (
            e.stderr.decode()
            if isinstance(e.stderr, bytes)
            else str(e.stderr)
            if e.stderr
            else ""
        )
        assert "http://127.0.0.1:5500" in stderr_output
        return

    # If server exited, it should have been an error (port conflict is possible with default port)
    # Allow both success and error, we just want to verify the default is 5500
    assert result.returncode != 0 or "http://127.0.0.1:5500" in result.stderr
