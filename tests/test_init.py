"""Tests for rsm init command."""

import subprocess
from pathlib import Path


def test_init_creates_basic_structure(tmp_path, monkeypatch):
    """Test that rsm init creates the basic project structure."""
    monkeypatch.chdir(tmp_path)

    # Simulate user input
    inputs = "test-doc\nTest Author\n"
    result = subprocess.run(
        ["rsm", "init"],
        input=inputs,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "✓ RSM project initialized successfully!" in result.stdout

    # Check created files and directories
    assert (tmp_path / "test-doc.rsm").exists()
    assert (tmp_path / "assets").is_dir()
    assert (tmp_path / "assets" / "aris-logo.svg").exists()
    assert (tmp_path / "README.md").exists()
    assert not (tmp_path / "custom.css").exists()  # Not created without --css


def test_init_rsm_file_content(tmp_path, monkeypatch):
    """Test that generated RSM file has correct content."""
    monkeypatch.chdir(tmp_path)

    inputs = "my-paper\nJohn Doe\n"
    subprocess.run(
        ["rsm", "init"],
        input=inputs,
        text=True,
        capture_output=True,
        check=True,
    )

    rsm_file = tmp_path / "my-paper.rsm"
    content = rsm_file.read_text()

    # Check for author and title (new format)
    assert "# My Paper" in content
    assert ":name: John Doe" in content

    # Check for syntax examples
    assert "## Introduction" in content
    assert ":figure:" in content
    assert "assets/aris-logo.svg" in content
    assert ":cite:" in content
    assert ":references:" in content


def test_init_with_css_flag(tmp_path, monkeypatch):
    """Test that --css flag creates custom.css."""
    monkeypatch.chdir(tmp_path)

    inputs = "article\nJane Smith\n"
    result = subprocess.run(
        ["rsm", "init", "--css"],
        input=inputs,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert (tmp_path / "custom.css").exists()

    # Check custom.css content
    css_content = (tmp_path / "custom.css").read_text()
    assert "Custom CSS for your RSM document" in css_content


def test_init_readme_content(tmp_path, monkeypatch):
    """Test that README has correct content."""
    monkeypatch.chdir(tmp_path)

    inputs = "document\nAuthor Name\n"
    subprocess.run(
        ["rsm", "init"],
        input=inputs,
        text=True,
        capture_output=True,
        check=True,
    )

    readme = tmp_path / "README.md"
    content = readme.read_text()

    # Check for key sections
    assert "# Document" in content
    assert "rsm build document.rsm" in content
    assert "rsm serve document.rsm" in content
    assert "rsm check document.rsm" in content


def test_init_readme_with_css(tmp_path, monkeypatch):
    """Test that README includes CSS info when --css is used."""
    monkeypatch.chdir(tmp_path)

    inputs = "article\nAuthor\n"
    subprocess.run(
        ["rsm", "init", "--css"],
        input=inputs,
        text=True,
        capture_output=True,
        check=True,
    )

    readme = tmp_path / "README.md"
    content = readme.read_text()

    # Should mention custom.css
    assert "custom.css" in content
    assert "--css custom.css" in content


def test_init_fails_with_existing_rsm_files(tmp_path, monkeypatch):
    """Test that init fails if RSM files already exist."""
    monkeypatch.chdir(tmp_path)

    # Create an existing RSM file
    (tmp_path / "existing.rsm").write_text("# Existing")

    inputs = "new-doc\nAuthor\n"
    result = subprocess.run(
        ["rsm", "init"],
        input=inputs,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "already contains RSM files" in result.stdout
    assert "Use --force" in result.stdout


def test_init_force_flag(tmp_path, monkeypatch):
    """Test that --force allows init in directory with existing RSM files."""
    monkeypatch.chdir(tmp_path)

    # Create an existing RSM file
    (tmp_path / "existing.rsm").write_text("# Existing")

    inputs = "new-doc\nAuthor\n"
    result = subprocess.run(
        ["rsm", "init", "--force"],
        input=inputs,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert (tmp_path / "new-doc.rsm").exists()
    assert (tmp_path / "existing.rsm").exists()  # Original still there


def test_init_default_filename(tmp_path, monkeypatch):
    """Test that pressing enter uses default filename."""
    monkeypatch.chdir(tmp_path)

    # Just press enter for filename, provide author
    inputs = "\nDefault Author\n"
    result = subprocess.run(
        ["rsm", "init"],
        input=inputs,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert (tmp_path / "document.rsm").exists()  # Default name

    content = (tmp_path / "document.rsm").read_text()
    assert "# Document" in content
    assert ":name: Default Author" in content


def test_init_filename_with_underscores(tmp_path, monkeypatch):
    """Test that filename with underscores creates nice title."""
    monkeypatch.chdir(tmp_path)

    inputs = "my_research_paper\nAuthor\n"
    subprocess.run(
        ["rsm", "init"],
        input=inputs,
        text=True,
        capture_output=True,
        check=True,
    )

    content = (tmp_path / "my_research_paper.rsm").read_text()
    assert "# My Research Paper" in content


def test_init_filename_with_dashes(tmp_path, monkeypatch):
    """Test that filename with dashes creates nice title."""
    monkeypatch.chdir(tmp_path)

    inputs = "my-research-paper\nAuthor\n"
    subprocess.run(
        ["rsm", "init"],
        input=inputs,
        text=True,
        capture_output=True,
        check=True,
    )

    content = (tmp_path / "my-research-paper.rsm").read_text()
    assert "# My Research Paper" in content
