"""Test output filename derivation and .html suffix handling."""

import subprocess
from pathlib import Path


def test_default_output_derives_from_input(tmp_path):
    """Test that foo.rsm creates foo.html by default."""
    rsm_file = tmp_path / "myfile.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    result = subprocess.run(
        ["rsm", "build", str(rsm_file)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output_file = tmp_path / "myfile.html"
    assert output_file.exists(), "Should create myfile.html from myfile.rsm"


def test_output_flag_strips_html_suffix(tmp_path):
    """Test that -o foo.html doesn't create foo.html.html."""
    rsm_file = tmp_path / "test.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    result = subprocess.run(
        ["rsm", "build", str(rsm_file), "-o", "output.html"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output_file = tmp_path / "output.html"
    assert output_file.exists(), "Should create output.html"
    # Make sure we didn't create output.html.html
    bad_file = tmp_path / "output.html.html"
    assert not bad_file.exists(), "Should NOT create output.html.html"


def test_output_flag_without_suffix_adds_html(tmp_path):
    """Test that -o foo creates foo.html."""
    rsm_file = tmp_path / "test.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    result = subprocess.run(
        ["rsm", "build", str(rsm_file), "-o", "myoutput"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output_file = tmp_path / "myoutput.html"
    assert output_file.exists(), "Should create myoutput.html from -o myoutput"


def test_output_directory_only_derives_from_input(tmp_path):
    """Test that -o build/ creates build/foo.html from foo.rsm."""
    rsm_file = tmp_path / "document.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    build_dir = tmp_path / "build"
    build_dir.mkdir()

    result = subprocess.run(
        ["rsm", "build", str(rsm_file), "-o", "build/"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output_file = build_dir / "document.html"
    assert output_file.exists(), "Should create build/document.html from document.rsm"


def test_output_directory_and_filename(tmp_path):
    """Test that -o build/custom.html works correctly."""
    rsm_file = tmp_path / "test.rsm"
    rsm_file.write_text("# Test\n\nContent.")

    build_dir = tmp_path / "build"
    build_dir.mkdir()

    result = subprocess.run(
        ["rsm", "build", str(rsm_file), "-o", "build/custom.html"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output_file = build_dir / "custom.html"
    assert output_file.exists(), "Should create build/custom.html"


def test_string_input_defaults_to_index(tmp_path):
    """Test that string input (-c) still creates index.html by default."""
    result = subprocess.run(
        ["rsm", "build", "# Test", "-c"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    output_file = tmp_path / "index.html"
    assert output_file.exists(), "String input should create index.html by default"


def test_multiple_files_same_directory(tmp_path):
    """Test building multiple RSM files to the same directory."""
    # Create multiple RSM files
    for i in range(1, 4):
        rsm_file = tmp_path / f"doc{i}.rsm"
        rsm_file.write_text(f"# Document {i}\n\nContent {i}.")

    # Build all files
    for i in range(1, 4):
        result = subprocess.run(
            ["rsm", "build", f"doc{i}.rsm"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    # Check all outputs exist
    for i in range(1, 4):
        output_file = tmp_path / f"doc{i}.html"
        assert output_file.exists(), f"Should create doc{i}.html"

    # Check that static directory exists
    static_dir = tmp_path / "static"
    assert static_dir.exists(), "Should create static/ directory"

    # Check that static files are there (they should be shared across all builds)
    assert (static_dir / "rsm.css").exists(), "Should have rsm.css"
