"""Tests for rsm build CLI file output behavior.

The rsm build command should write files to disk (index.html + static/ folder).
The rsm.build() Python API should return HTML without writing files.
"""

import subprocess

import pytest

import rsm


class TestMakeCLIFileOutput:
    """Test that rsm build CLI writes files to disk."""

    @pytest.mark.slow
    def test_make_cli_creates_index_html(self, tmp_path):
        """Test that rsm build creates index.html file."""
        src = "# Test\n\nHello world.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        # Run rsm build in tmp_path directory
        subprocess.run(
            f"rsm build {src_file}",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create test.html (derived from test.rsm)
        output_html = tmp_path / "test.html"
        assert output_html.exists(), "rsm build should create test.html from test.rsm"
        assert output_html.read_text().strip() != "", "test.html should not be empty"
        assert "<html>" in output_html.read_text()
        assert "Hello world" in output_html.read_text()

    @pytest.mark.slow
    def test_make_cli_creates_static_folder(self, tmp_path):
        """Test that rsm build creates static/ folder with assets."""
        src = "# Test\n\nHello world.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        subprocess.run(
            f"rsm build {src_file}",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create static/ folder
        static_dir = tmp_path / "static"
        assert static_dir.exists(), "rsm build should create static/ folder"
        assert static_dir.is_dir()

        # Should contain CSS and JS files
        assert (static_dir / "rsm.css").exists()
        assert (static_dir / "jquery-3.6.0.js").exists()
        assert (static_dir / "tooltipster.bundle.js").exists()

    @pytest.mark.slow
    def test_make_cli_with_string_flag_creates_files_in_cwd(self, tmp_path):
        """Test that rsm build with -c flag creates files in current directory."""
        src = ":rsm:\n# Test\n\nString source.\n"

        # Run with -c flag in tmp_path
        subprocess.run(
            f'rsm build "{src}" -c',
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
        """Test that rsm build default behavior produces no stdout."""
        src = "# Test\n\nDefault mode.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        result = subprocess.run(
            f"rsm build {src_file}",
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

        # But should still create files (test.html from test.rsm)
        output_html = tmp_path / "test.html"
        assert output_html.exists()
        assert "Default mode" in output_html.read_text()

    @pytest.mark.slow
    def test_make_cli_output_flag_filename(self, tmp_path):
        """Test rsm build -o filename creates custom-named file."""
        src = "# Test\n\nCustom filename.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        subprocess.run(
            f"rsm build {src_file} -o myfile",
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
        """Test rsm build -o dir/ creates files in directory."""
        src = "# Test\n\nCustom directory.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        subprocess.run(
            f"rsm build {src_file} -o build/",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should create build/test.html (derived from test.rsm)
        build_dir = tmp_path / "build"
        assert build_dir.exists() and build_dir.is_dir()
        output_html = build_dir / "test.html"
        assert output_html.exists()
        assert "Custom directory" in output_html.read_text()

    @pytest.mark.slow
    def test_make_cli_output_flag_both(self, tmp_path):
        """Test rsm build -o dir/filename creates custom file in directory."""
        src = "# Test\n\nBoth custom.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        subprocess.run(
            f"rsm build {src_file} -o dist/document",
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
        """Test rsm build -p prints HTML to stdout AND creates files."""
        src = "# Test\n\nPrint flag.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        result = subprocess.run(
            f"rsm build {src_file} -p",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should print HTML to stdout
        stdout = result.stdout.decode("utf-8")
        assert "<html>" in stdout
        assert "Print flag" in stdout

        # Should also create files (test.html from test.rsm)
        output_html = tmp_path / "test.html"
        assert output_html.exists()
        assert "Print flag" in output_html.read_text()

    @pytest.mark.slow
    def test_make_cli_standalone_flag(self, tmp_path):
        """Test rsm build --standalone creates single HTML file."""
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

        # Should create test.html
        output_html = tmp_path / "test.html"
        assert output_html.exists()
        assert "Standalone" in output_html.read_text()

        # Should NOT create static/ folder
        static_dir = tmp_path / "static"
        assert not static_dir.exists()

        # Should use CDN URLs
        html_content = output_html.read_text()
        assert "cdn.jsdelivr.net" in html_content

    @pytest.mark.slow
    def test_make_cli_custom_css_flag(self, tmp_path):
        """Test rsm build --css copies custom CSS to static/ folder."""
        src = "# Test\n\n:paragraph: {:types: mytype} Custom styled text\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        # Create custom CSS file
        custom_css = ".mytype { color: red; }"
        custom_css_file = tmp_path / "custom.css"
        custom_css_file.write_text(custom_css)

        subprocess.run(
            f"rsm build {src_file} --css {custom_css_file}",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should copy custom.css to static/ folder
        static_dir = tmp_path / "static"
        custom_css_in_static = static_dir / "custom.css"
        assert custom_css_in_static.exists(), "Custom CSS should be copied to static/"
        assert custom_css in custom_css_in_static.read_text()

        # Should add link tag in HTML
        output_html = tmp_path / "test.html"
        html_content = output_html.read_text()
        assert '<link rel="stylesheet" type="text/css" href="/static/custom.css"' in html_content

        # Custom CSS link should come after rsm.css
        rsm_css_pos = html_content.find('/static/rsm.css')
        custom_css_pos = html_content.find('/static/custom.css')
        assert rsm_css_pos < custom_css_pos, "Custom CSS should load after rsm.css"

    @pytest.mark.slow
    def test_custom_css_overrides_rsm_css(self, tmp_path):
        """Test that rsm.css is wrapped in @layer base to allow custom CSS to override."""
        src = "# Test\n\nA simple paragraph.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        # Create custom CSS with low specificity (will still win due to @layer)
        custom_css = ".custom { color: red; }"
        custom_css_file = tmp_path / "custom.css"
        custom_css_file.write_text(custom_css)

        subprocess.run(
            f"rsm build {src_file} --css {custom_css_file}",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Verify custom CSS is present
        custom_css_in_static = tmp_path / "static" / "custom.css"
        assert custom_css in custom_css_in_static.read_text()

        # Verify rsm.css is wrapped in @layer base
        rsm_css_in_static = tmp_path / "static" / "rsm.css"
        rsm_css_content = rsm_css_in_static.read_text()
        assert "@layer base" in rsm_css_content, "rsm.css should use @layer base"

    @pytest.mark.slow
    def test_make_cli_custom_css_standalone(self, tmp_path):
        """Test rsm build --css --standalone inlines custom CSS."""
        src = "# Test\n\n:paragraph: {:types: mytype} Custom styled text\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        # Create custom CSS file
        custom_css = ".mytype { color: red; }"
        custom_css_file = tmp_path / "custom.css"
        custom_css_file.write_text(custom_css)

        subprocess.run(
            f"rsm build {src_file} --css {custom_css_file} --standalone",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
            check=True,
        )

        # Should NOT create static/ folder
        static_dir = tmp_path / "static"
        assert not static_dir.exists(), "--standalone should not create static/ folder"

        # Should inline custom CSS in <style> tag
        output_html = tmp_path / "test.html"
        html_content = output_html.read_text()
        assert "<style>" in html_content
        assert custom_css in html_content

        # <style> tag should come after CDN rsm.css link
        cdn_css_pos = html_content.find('cdn.jsdelivr.net')
        style_tag_pos = html_content.find('<style>')
        assert cdn_css_pos < style_tag_pos, "Inline custom CSS should come after CDN rsm.css"

    @pytest.mark.slow
    def test_make_cli_custom_css_nonexistent_file(self, tmp_path):
        """Test rsm build with nonexistent CSS file logs warning but continues."""
        src = "# Test\n\nNonexistent CSS.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        result = subprocess.run(
            f"rsm build {src_file} --css nonexistent.css",
            cwd=tmp_path,
            shell=True,
            capture_output=True,
        )

        # Should still succeed (or at least not crash)
        # Check stderr for warning
        stderr = result.stderr.decode("utf-8")
        assert "nonexistent.css" in stderr or "not found" in stderr.lower()

        # Should still create test.html
        output_html = tmp_path / "test.html"
        assert output_html.exists()


class TestMakePythonAPINoFileOutput:
    """Test that rsm.build() Python API returns HTML without writing files."""

    def test_make_api_returns_html_string(self):
        """Test that rsm.build() returns HTML as string."""
        src = "# Test\n\nAPI call.\n"
        result = rsm.build(src)

        assert isinstance(result, str)
        assert "<html>" in result
        assert "API call" in result

    def test_make_api_does_not_write_files(self, tmp_path):
        """Test that rsm.build() does NOT write files to disk."""
        src = "# Test\n\nAPI call.\n"

        # Change to tmp_path to ensure no files are written
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Call API
            result = rsm.build(src)
            assert isinstance(result, str)

            # Should NOT create index.html or static/
            assert not (tmp_path / "index.html").exists()
            assert not (tmp_path / "static").exists()

        finally:
            os.chdir(original_cwd)

    def test_make_api_with_path_does_not_write_files(self, tmp_path):
        """Test that rsm.build(path=...) does NOT write files to disk."""
        src = "# Test\n\nAPI with path.\n"
        src_file = tmp_path / "test.rsm"
        src_file.write_text(src)

        # Call API with path
        result = rsm.build(path=str(src_file))
        assert isinstance(result, str)
        assert "API with path" in result

        # Should NOT create index.html or static/ in tmp_path
        assert not (tmp_path / "index.html").exists()
        assert not (tmp_path / "static").exists()
