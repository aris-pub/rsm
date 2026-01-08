"""Tests for rsm-make CLI file output behavior.

The rsm-make command should write files to disk (index.html + static/ folder).
The rsm.make() Python API should return HTML without writing files.
"""

import subprocess

import pytest

import rsm


class TestMakeCLIFileOutput:
    """Test that rsm-make CLI writes files to disk."""

    @pytest.mark.slow
    def test_make_cli_creates_index_html(self, tmp_path):
        """Test that rsm-make creates index.html file."""
        src = ":rsm:\n# Test\n\nHello world.\n\n::"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        # Run rsm-make in tmp_path directory
        subprocess.run(
            f"rsm-make {src_file}",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create index.html
        index_html = tmp_path / "index.html"
        assert index_html.exists(), "rsm-make should create index.html"
        assert index_html.read_text().strip() != "", "index.html should not be empty"
        assert "<html>" in index_html.read_text()
        assert "Hello world" in index_html.read_text()

    @pytest.mark.slow
    def test_make_cli_creates_static_folder(self, tmp_path):
        """Test that rsm-make creates static/ folder with assets."""
        src = ":rsm:\n# Test\n\nHello world.\n\n::"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        subprocess.run(
            f"rsm-make {src_file}",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create static/ folder
        static_dir = tmp_path / "static"
        assert static_dir.exists(), "rsm-make should create static/ folder"
        assert static_dir.is_dir()

        # Should contain CSS and JS files
        assert (static_dir / "rsm.css").exists()
        assert (static_dir / "jquery-3.6.0.js").exists()
        assert (static_dir / "tooltipster.bundle.js").exists()

    @pytest.mark.slow
    def test_make_cli_with_string_flag_creates_files_in_cwd(self, tmp_path):
        """Test that rsm-make with -c flag creates files in current directory."""
        src = ":rsm:\n# Test\n\nString source.\n\n::"

        # Run with -c flag in tmp_path
        subprocess.run(
            f'rsm-make "{src}" -c',
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should still create files even with -c flag
        index_html = tmp_path / "index.html"
        assert index_html.exists()
        assert "String source" in index_html.read_text()

    @pytest.mark.slow
    def test_make_cli_silent_flag_still_creates_files(self, tmp_path):
        """Test that rsm-make with -s flag still creates files (just no stdout)."""
        src = ":rsm:\n# Test\n\nSilent mode.\n\n::"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        result = subprocess.run(
            f"rsm-make {src_file} -s",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should produce no stdout (silent mode)
        # Filter out warnings
        stdout = result.stdout.decode("utf-8")
        lines = [line for line in stdout.split("\n") if "pkg_resources" not in line]
        clean_stdout = "\n".join(lines).strip()
        assert clean_stdout == "", "Silent mode should produce no output to stdout"

        # But should still create files
        index_html = tmp_path / "index.html"
        assert index_html.exists()
        assert "Silent mode" in index_html.read_text()


class TestMakePythonAPINoFileOutput:
    """Test that rsm.make() Python API returns HTML without writing files."""

    def test_make_api_returns_html_string(self):
        """Test that rsm.make() returns HTML as string."""
        src = ":rsm:\n# Test\n\nAPI call.\n\n::"
        result = rsm.make(src)

        assert isinstance(result, str)
        assert "<html>" in result
        assert "API call" in result

    def test_make_api_does_not_write_files(self, tmp_path):
        """Test that rsm.make() does NOT write files to disk."""
        src = ":rsm:\n# Test\n\nAPI call.\n\n::"

        # Change to tmp_path to ensure no files are written
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Call API
            result = rsm.make(src)
            assert isinstance(result, str)

            # Should NOT create index.html or static/
            assert not (tmp_path / "index.html").exists()
            assert not (tmp_path / "static").exists()

        finally:
            os.chdir(original_cwd)

    def test_make_api_with_path_does_not_write_files(self, tmp_path):
        """Test that rsm.make(path=...) does NOT write files to disk."""
        src = ":rsm:\n# Test\n\nAPI with path.\n\n::"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        # Call API with path
        result = rsm.make(path=str(src_file))
        assert isinstance(result, str)
        assert "API with path" in result

        # Should NOT create index.html or static/ in tmp_path
        assert not (tmp_path / "index.html").exists()
        assert not (tmp_path / "static").exists()
