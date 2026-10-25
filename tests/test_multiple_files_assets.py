"""Test that multiple RSM files in the same directory handle assets correctly."""

import os
import subprocess

import pytest

import rsm


def _write_figure_doc(src_dir, with_webp=True):
    assets = src_dir / "assets"
    assets.mkdir()
    (assets / "fig.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<circle cx="5" cy="5" r="4"/></svg>'
    )
    # Non-UTF-8 bytes, as real binary images are: the resolver returns bytes,
    # which is the path that crashed the build when routed through write_text.
    (assets / "fig.png").write_bytes(b"\x89PNG\r\n\x1a\n\xff\xd8\xff\x00png")
    body = (
        "# Doc\n\n"
        ":figure: {\n  :path: assets/fig.svg\n}\n:caption: Vector.\n::\n\n"
        ":figure: {\n  :path: assets/fig.png\n}\n:caption: Raster.\n::\n"
    )
    if with_webp:
        (assets / "fig.webp").write_bytes(b"RIFF\xff\x00\x00\x00WEBPVP8 \xff\xd8")
        body += "\n:figure: {\n  :path: assets/fig.webp\n}\n:caption: Webp.\n::\n"
    (src_dir / "doc.rsm").write_text(body)


def test_folder_build_relocated_is_self_contained(tmp_path):
    """A non-standalone build into a separate output directory copies every
    referenced figure asset into that folder at its relative path, so the folder
    can be moved and still render. Binary formats (png, webp) must not crash the
    build (rsm-en4)."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    _write_figure_doc(src_dir, with_webp=True)
    out_dir = tmp_path / "out"

    cwd = os.getcwd()
    os.chdir(src_dir)
    try:
        rsm.build(
            path="doc.rsm",
            output_dir=str(out_dir),
            output_filename="doc.html",
            write_output=True,
            handrails=True,
            standalone=False,
            strict=True,
        )
    finally:
        os.chdir(cwd)

    html = (out_dir / "doc.html").read_text()
    assert 'src="assets/fig.svg"' in html
    assert 'src="assets/fig.png"' in html
    assert 'src="assets/fig.webp"' in html

    # Every asset copied into the output folder at its authored relative path.
    assert (out_dir / "assets" / "fig.svg").exists()
    assert (out_dir / "assets" / "fig.png").exists()
    assert (out_dir / "assets" / "fig.webp").exists()

    # User media is not dumped into static/ (only framework files live there).
    assert not (out_dir / "static" / "fig.svg").exists()
    assert not (out_dir / "static" / "fig.png").exists()

    # Originals are copied, not moved.
    assert (src_dir / "assets" / "fig.svg").exists()
    assert (src_dir / "assets" / "fig.png").exists()


@pytest.mark.slow
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
    subprocess.run(
        ["rsm", "build", "doc1.rsm"], cwd=tmp_path, check=True, capture_output=True
    )
    subprocess.run(
        ["rsm", "build", "doc2.rsm"], cwd=tmp_path, check=True, capture_output=True
    )

    # Check outputs exist
    html1 = tmp_path / "doc1.html"
    html2 = tmp_path / "doc2.html"
    assert html1.exists()
    assert html2.exists()

    # Check that each HTML references the correct image
    content1 = html1.read_text()
    content2 = html2.read_text()

    # Check that image paths are in the HTML (checking for presence, not exact format)
    assert "images/pic1.png" in content1, "doc1.html should reference pic1.png"
    assert "images/pic2.png" in content2, "doc2.html should reference pic2.png"
    assert "<img src=" in content1, "doc1.html should have an img tag"
    assert "<img src=" in content2, "doc2.html should have an img tag"

    # Images should NOT be copied to static/
    static_dir = tmp_path / "static"
    assert not (static_dir / "pic1.png").exists(), (
        "Images should NOT be copied to static/"
    )
    assert not (static_dir / "pic2.png").exists(), (
        "Images should NOT be copied to static/"
    )
    assert not (static_dir / "images").exists(), (
        "Images directory should NOT be in static/"
    )

    # Images should remain in their original location
    assert (images_dir / "pic1.png").exists(), "Original images should remain in place"
    assert (images_dir / "pic2.png").exists(), "Original images should remain in place"

    # Both documents share the same static/ folder for RSM framework files
    assert (static_dir / "braiid.css").exists(), "Both should share RSM CSS in static/"


@pytest.mark.slow
def test_multiple_files_share_static_assets(tmp_path):
    """Test that multiple RSM files share the same static/ directory.

    This is correct behavior because the static/ directory only contains
    RSM framework files (CSS, JS) which are identical for all documents.
    """
    # Create three RSM files
    for i in range(1, 4):
        rsm_file = tmp_path / f"doc{i}.rsm"
        rsm_file.write_text(f"# Document {i}\n\nContent {i}.")
        subprocess.run(
            ["rsm", "build", f"doc{i}.rsm"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

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
        assert "/static/braiid.css" in content, (
            f"doc{i}.html should reference shared static/braiid.css"
        )

    # The static files are the same for all documents, so sharing is safe
    rsm_css = (static_dir / "braiid.css").read_text()
    assert len(rsm_css) > 0, "Static CSS should exist and be non-empty"
