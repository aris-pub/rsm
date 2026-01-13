"""Tests for rsm-build CLI file output behavior.

The rsm-build command should write files to disk (index.html + static/ folder).
The rsm.make() Python API should return HTML without writing files.
"""

import subprocess

import pytest

import rsm


class TestMakeCLIFileOutput:
    """Test that rsm-build CLI writes files to disk."""

    @pytest.mark.slow
    def test_make_cli_creates_index_html(self, tmp_path):
        """Test that rsm-build creates index.html file."""
        src = "# Test\n\nHello world.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        # Run rsm-build in tmp_path directory
        subprocess.run(
            f"rsm-build {src_file}",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create index.html
        index_html = tmp_path / "index.html"
        assert index_html.exists(), "rsm-build should create index.html"
        assert index_html.read_text().strip() != "", "index.html should not be empty"
        assert "<html>" in index_html.read_text()
        assert "Hello world" in index_html.read_text()

    @pytest.mark.slow
    def test_make_cli_creates_static_folder(self, tmp_path):
        """Test that rsm-build creates static/ folder with assets."""
        src = "# Test\n\nHello world.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        subprocess.run(
            f"rsm-build {src_file}",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create static/ folder
        static_dir = tmp_path / "static"
        assert static_dir.exists(), "rsm-build should create static/ folder"
        assert static_dir.is_dir()

        # Should contain CSS and JS files
        assert (static_dir / "rsm.css").exists()
        assert (static_dir / "jquery-3.6.0.js").exists()
        assert (static_dir / "tooltipster.bundle.js").exists()

    @pytest.mark.slow
    def test_make_cli_with_string_flag_creates_files_in_cwd(self, tmp_path):
        """Test that rsm-build with -c flag creates files in current directory."""
        src = ":rsm:\n# Test\n\nString source.\n"

        # Run with -c flag in tmp_path
        subprocess.run(
            f'rsm-build "{src}" -c',
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
    def test_make_cli_default_no_stdout(self, tmp_path):
        """Test that rsm-build default behavior produces no stdout."""
        src = "# Test\n\nDefault mode.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        result = subprocess.run(
            f"rsm-build {src_file}",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should produce no stdout by default
        # Filter out warnings
        stdout = result.stdout.decode("utf-8")
        lines = [line for line in stdout.split("\n") if "pkg_resources" not in line]
        clean_stdout = "\n".join(lines).strip()
        assert clean_stdout == "", "Default mode should produce no output to stdout"

        # But should still create files
        index_html = tmp_path / "index.html"
        assert index_html.exists()
        assert "Default mode" in index_html.read_text()

    @pytest.mark.slow
    def test_make_cli_output_flag_filename(self, tmp_path):
        """Test rsm-build -o filename creates custom-named file."""
        src = "# Test\n\nCustom filename.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        subprocess.run(
            f"rsm-build {src_file} -o myfile",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create myfile.html instead of index.html
        output_html = tmp_path / "myfile.html"
        assert output_html.exists()
        assert "Custom filename" in output_html.read_text()
        assert not (tmp_path / "index.html").exists()

    @pytest.mark.slow
    def test_make_cli_output_flag_directory(self, tmp_path):
        """Test rsm-build -o dir/ creates files in directory."""
        src = "# Test\n\nCustom directory.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        subprocess.run(
            f"rsm-build {src_file} -o build/",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create build/index.html
        build_dir = tmp_path / "build"
        assert build_dir.exists() and build_dir.is_dir()
        output_html = build_dir / "index.html"
        assert output_html.exists()
        assert "Custom directory" in output_html.read_text()

    @pytest.mark.slow
    def test_make_cli_output_flag_both(self, tmp_path):
        """Test rsm-build -o dir/filename creates custom file in directory."""
        src = "# Test\n\nBoth custom.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        subprocess.run(
            f"rsm-build {src_file} -o dist/document",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create dist/document.html
        dist_dir = tmp_path / "dist"
        assert dist_dir.exists() and dist_dir.is_dir()
        output_html = dist_dir / "document.html"
        assert output_html.exists()
        assert "Both custom" in output_html.read_text()

    @pytest.mark.slow
    def test_make_cli_print_flag(self, tmp_path):
        """Test rsm-build -p prints HTML to stdout AND creates files."""
        src = "# Test\n\nPrint flag.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        result = subprocess.run(
            f"rsm-build {src_file} -p",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should print HTML to stdout
        stdout = result.stdout.decode("utf-8")
        assert "<html>" in stdout
        assert "Print flag" in stdout

        # Should also create files
        index_html = tmp_path / "index.html"
        assert index_html.exists()
        assert "Print flag" in index_html.read_text()

    @pytest.mark.slow
    def test_make_cli_standalone_flag(self, tmp_path):
        """Test rsm-build --standalone creates single HTML file."""
        src = "# Test\n\nStandalone.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        subprocess.run(
            f"rsm-build {src_file} --standalone",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create index.html
        index_html = tmp_path / "index.html"
        assert index_html.exists()
        assert "Standalone" in index_html.read_text()

        # Should NOT create static/ folder
        static_dir = tmp_path / "static"
        assert not static_dir.exists()

        # Should use CDN URLs
        html_content = index_html.read_text()
        assert "cdn.jsdelivr.net" in html_content


class TestMakePythonAPINoFileOutput:
    """Test that rsm.make() Python API returns HTML without writing files."""

    def test_make_api_returns_html_string(self):
        """Test that rsm.make() returns HTML as string."""
        src = "# Test\n\nAPI call.\n"
        result = rsm.make(src)

        assert isinstance(result, str)
        assert "<html>" in result
        assert "API call" in result

    def test_make_api_does_not_write_files(self, tmp_path):
        """Test that rsm.make() does NOT write files to disk."""
        src = "# Test\n\nAPI call.\n"

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
        src = "# Test\n\nAPI with path.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        # Call API with path
        result = rsm.make(path=str(src_file))
        assert isinstance(result, str)
        assert "API with path" in result

        # Should NOT create index.html or static/ in tmp_path
        assert not (tmp_path / "index.html").exists()
        assert not (tmp_path / "static").exists()
