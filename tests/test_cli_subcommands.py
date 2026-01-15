"""Tests for rsm CLI subcommand structure.

Tests that the rsm command works with subcommands: build, render, lint, serve.
"""

import subprocess

import pytest


class TestCLISubcommands:
    """Test that rsm command works with subcommands."""

    @pytest.mark.slow
    def test_rsm_build_subcommand(self, tmp_path):
        """Test that 'rsm build' works as a subcommand."""
        src = "# Test\n\nBuild subcommand.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        result = subprocess.run(
            f"rsm build {src_file}",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create test.html (derived from test.rsm)
        output_html = tmp_path / "test.html"
        assert output_html.exists(), "rsm build should create test.html"
        assert "Build subcommand" in output_html.read_text()

    @pytest.mark.slow
    def test_rsm_render_subcommand(self, tmp_path):
        """Test that 'rsm render' works as a subcommand."""
        src = "# Test\n\nRender subcommand.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        result = subprocess.run(
            f"rsm render {src_file}",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should print HTML body to stdout (not full document)
        stdout = result.stdout.decode("utf-8")
        assert "<body>" in stdout
        assert "Render subcommand" in stdout

        # Should NOT create files
        assert not (tmp_path / "index.html").exists()

    @pytest.mark.slow
    def test_rsm_check_subcommand(self, tmp_path):
        """Test that 'rsm check' works as a subcommand."""
        src = "# Test\n\nCheck subcommand.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        result = subprocess.run(
            f"rsm check {src_file}",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should succeed without errors
        assert result.returncode == 0

    @pytest.mark.slow
    def test_rsm_build_no_serve_flag(self, tmp_path):
        """Test that 'rsm build --serve' is no longer valid."""
        src = "# Test\n\nNo serve flag.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        result = subprocess.run(
            f"rsm build {src_file} --serve",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
        )

        # Should fail with error about unrecognized argument
        assert result.returncode != 0
        stderr = result.stderr.decode("utf-8")
        assert "--serve" in stderr or "unrecognized" in stderr.lower()

    @pytest.mark.slow
    def test_rsm_serve_subcommand_basic(self, tmp_path):
        """Test that 'rsm serve' subcommand exists and accepts arguments."""
        src = "# Test\n\nServe subcommand.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        # Just test that the command is recognized (we won't actually start the server)
        # We can test this by checking --help
        result = subprocess.run(
            "rsm serve --help",
            shell=True,
            capture_output=True,
        )

        # Should succeed and show help for serve subcommand
        assert result.returncode == 0
        stdout = result.stdout.decode("utf-8")
        assert "serve" in stdout.lower()

    @pytest.mark.slow
    def test_rsm_version_flag(self, tmp_path):
        """Test that 'rsm --version' works."""
        result = subprocess.run(
            "rsm --version",
            shell=True,
            capture_output=True,
        )

        # Should succeed and show version
        assert result.returncode == 0
        stdout = result.stdout.decode("utf-8")
        assert "rsm-markup" in stdout

    @pytest.mark.slow
    def test_rsm_help_shows_subcommands(self, tmp_path):
        """Test that 'rsm --help' shows available subcommands."""
        result = subprocess.run(
            "rsm --help",
            shell=True,
            capture_output=True,
        )

        # Should succeed and list subcommands
        assert result.returncode == 0
        stdout = result.stdout.decode("utf-8")
        assert "build" in stdout
        assert "render" in stdout
        assert "check" in stdout
        assert "serve" in stdout

    @pytest.mark.slow
    def test_rsm_build_with_output_flag(self, tmp_path):
        """Test that 'rsm build -o' flag still works."""
        src = "# Test\n\nOutput flag.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        subprocess.run(
            f"rsm build {src_file} -o custom",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create custom.html
        output_html = tmp_path / "custom.html"
        assert output_html.exists()
        assert "Output flag" in output_html.read_text()

    @pytest.mark.slow
    def test_rsm_build_with_standalone_flag(self, tmp_path):
        """Test that 'rsm build --standalone' flag still works."""
        src = "# Test\n\nStandalone.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        subprocess.run(
            f"rsm build {src_file} --standalone",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create test.html without static/ folder
        output_html = tmp_path / "test.html"
        assert output_html.exists()
        assert not (tmp_path / "static").exists()
