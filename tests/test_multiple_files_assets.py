"""Test that multiple RSM files in the same directory handle assets correctly."""

import subprocess
from pathlib import Path


def test_multiple_files_with_different_images(tmp_path):
    """Test that multiple RSM files can reference different images.

    The images are NOT copied to static/ - they're referenced with relative
    paths from the RSM source. Only the RSM framework files (CSS, JS) go in
    static/, and those are identical for all documents.
    """
    # Create images directory
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    # Create placeholder images
    (images_dir / "pic1.png").write_bytes(b"fake-png-1")
    (images_dir / "pic2.png").write_bytes(b"fake-png-2")

    # Create doc1.rsm that references pic1.png
    doc1 = tmp_path / "doc1.rsm"
    doc1.write_text("""\
# Document 1

:figure: {:path: images/pic1.png}
:caption: Picture 1
::
""")

    # Create doc2.rsm that references pic2.png
    doc2 = tmp_path / "doc2.rsm"
    doc2.write_text("""\
# Document 2

:figure: {:path: images/pic2.png}
:caption: Picture 2
::
""")

    # Build both documents
    subprocess.run(["rsm", "build", "doc1.rsm"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["rsm", "build", "doc2.rsm"], cwd=tmp_path, check=True, capture_output=True)

    # Check outputs exist
    html1 = tmp_path / "doc1.html"
    html2 = tmp_path / "doc2.html"
    assert html1.exists()
    assert html2.exists()

    # Check that each HTML references the correct image
    content1 = html1.read_text()
    content2 = html2.read_text()

    # Check that image paths are in the HTML (checking for presence, not exact format)
    assert 'images/pic1.png' in content1, "doc1.html should reference pic1.png"
    assert 'images/pic2.png' in content2, "doc2.html should reference pic2.png"
    assert '<img src=' in content1, "doc1.html should have an img tag"
    assert '<img src=' in content2, "doc2.html should have an img tag"

    # Images should NOT be copied to static/
    static_dir = tmp_path / "static"
    assert not (static_dir / "pic1.png").exists(), "Images should NOT be copied to static/"
    assert not (static_dir / "pic2.png").exists(), "Images should NOT be copied to static/"
    assert not (static_dir / "images").exists(), "Images directory should NOT be in static/"

    # Images should remain in their original location
    assert (images_dir / "pic1.png").exists(), "Original images should remain in place"
    assert (images_dir / "pic2.png").exists(), "Original images should remain in place"

    # Both documents share the same static/ folder for RSM framework files
    assert (static_dir / "rsm.css").exists(), "Both should share RSM CSS in static/"


def test_multiple_files_share_static_assets(tmp_path):
    """Test that multiple RSM files share the same static/ directory.

    This is correct behavior because the static/ directory only contains
    RSM framework files (CSS, JS) which are identical for all documents.
    """
    # Create three RSM files
    for i in range(1, 4):
        rsm_file = tmp_path / f"doc{i}.rsm"
        rsm_file.write_text(f"# Document {i}\n\nContent {i}.")
        subprocess.run(["rsm", "build", f"doc{i}.rsm"], cwd=tmp_path, check=True, capture_output=True)

    # All three should create HTML files
    assert (tmp_path / "doc1.html").exists()
    assert (tmp_path / "doc2.html").exists()
    assert (tmp_path / "doc3.html").exists()

    # All three share the same static/ directory
    static_dir = tmp_path / "static"
    assert static_dir.exists()

    # All HTML files reference the same static assets
    for i in range(1, 4):
        html_file = tmp_path / f"doc{i}.html"
        content = html_file.read_text()
        assert '/static/rsm.css' in content, f"doc{i}.html should reference shared static/rsm.css"

    # The static files are the same for all documents, so sharing is safe
    rsm_css = (static_dir / "rsm.css").read_text()
    assert len(rsm_css) > 0, "Static CSS should exist and be non-empty"
