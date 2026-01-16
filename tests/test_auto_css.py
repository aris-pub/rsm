"""Tests for automatic CSS file detection based on input filename."""

import subprocess
from pathlib import Path


def test_auto_detects_matching_css_file(tmp_path):
    """Test that building file.rsm automatically includes file.css if it exists."""
    # Create RSM file
    rsm_file = tmp_path / "document.rsm"
    rsm_file.write_text("# Test\n\nContent with auto CSS.")

    # Create matching CSS file
    css_file = tmp_path / "document.css"
    css_content = ".auto-detected { color: blue; }"
    css_file.write_text(css_content)

    # Build without --css flag
    subprocess.run(
        ["rsm", "build", str(rsm_file)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Check that CSS was copied to static/
    static_css = tmp_path / "static" / "document.css"
    assert static_css.exists(), "Matching CSS should be auto-detected and copied to static/"
    assert css_content in static_css.read_text()

    # Check that HTML links to it
    html_file = tmp_path / "document.html"
    html_content = html_file.read_text()
    assert '<link rel="stylesheet" type="text/css" href="/static/document.css"' in html_content


def test_no_css_when_matching_file_not_present(tmp_path):
    """Test that building works normally when no matching CSS file exists."""
    rsm_file = tmp_path / "document.rsm"
    rsm_file.write_text("# Test\n\nContent without CSS.")

    # Build without CSS file present
    subprocess.run(
        ["rsm", "build", str(rsm_file)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Should build successfully
    html_file = tmp_path / "document.html"
    assert html_file.exists()

    # Static dir should have rsm.css but not document.css
    static_dir = tmp_path / "static"
    assert (static_dir / "rsm.css").exists()
    assert not (static_dir / "document.css").exists()


def test_css_flag_overrides_auto_detection(tmp_path):
    """Test that --css flag overrides auto-detected matching CSS file."""
    # Create RSM file
    rsm_file = tmp_path / "document.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    # Create matching CSS file (should be ignored)
    auto_css = tmp_path / "document.css"
    auto_css.write_text(".auto { color: blue; }")

    # Create custom CSS file
    custom_css = tmp_path / "custom.css"
    custom_content = ".custom { color: red; }"
    custom_css.write_text(custom_content)

    # Build with --css flag
    subprocess.run(
        ["rsm", "build", str(rsm_file), "--css", str(custom_css)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Should use custom.css, not document.css
    assert (tmp_path / "static" / "custom.css").exists()
    assert not (tmp_path / "static" / "document.css").exists()

    # HTML should link to custom.css
    html_content = (tmp_path / "document.html").read_text()
    assert "/static/custom.css" in html_content
    assert "/static/document.css" not in html_content


def test_css_flag_works_without_auto_css(tmp_path):
    """Test that --css flag works as before when no auto-detected CSS exists."""
    rsm_file = tmp_path / "document.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    custom_css = tmp_path / "styles.css"
    custom_css.write_text(".custom { color: green; }")

    subprocess.run(
        ["rsm", "build", str(rsm_file), "--css", str(custom_css)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    assert (tmp_path / "static" / "styles.css").exists()

    html_content = (tmp_path / "document.html").read_text()
    assert "/static/styles.css" in html_content


def test_auto_css_with_string_input_not_applied(tmp_path):
    """Test that auto CSS detection doesn't apply to string input (-c flag)."""
    # Create a CSS file that could match
    css_file = tmp_path / "anything.css"
    css_file.write_text(".test { color: blue; }")

    # Build with string input
    result = subprocess.run(
        ["rsm", "build", "# Test\n\nString input.", "-c"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Should create index.html without auto-detecting CSS
    html_file = tmp_path / "index.html"
    assert html_file.exists()

    # Should not include any custom CSS
    html_content = html_file.read_text()
    assert "anything.css" not in html_content


def test_auto_css_with_different_directory(tmp_path):
    """Test auto CSS detection when RSM file is in a subdirectory."""
    # Create subdirectory
    subdir = tmp_path / "docs"
    subdir.mkdir()

    # Create RSM file in subdirectory
    rsm_file = subdir / "article.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    # Create matching CSS in same subdirectory
    css_file = subdir / "article.css"
    css_file.write_text(".article { color: purple; }")

    # Build from parent directory
    subprocess.run(
        ["rsm", "build", "docs/article.rsm"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # CSS should be found and used
    html_file = tmp_path / "article.html"
    html_content = html_file.read_text()
    assert "/static/article.css" in html_content


def test_auto_css_with_output_flag(tmp_path):
    """Test that auto CSS detection works with -o flag."""
    rsm_file = tmp_path / "paper.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    css_file = tmp_path / "paper.css"
    css_file.write_text(".paper { font-size: 14px; }")

    # Build with output flag
    subprocess.run(
        ["rsm", "build", str(rsm_file), "-o", "output"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    # Should still auto-detect paper.css
    assert (tmp_path / "static" / "paper.css").exists()

    html_content = (tmp_path / "output.html").read_text()
    assert "/static/paper.css" in html_content
