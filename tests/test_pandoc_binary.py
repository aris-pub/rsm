"""Export to formats that pandoc writes as binary files (Word, EPUB, and others).

pandoc writes these formats as bytes, so they cannot be read back as text from
its output. Like PDF, they go to a file given with -o.
"""

import shutil
import zipfile

import pytest

from rsm.app import RSMApplicationError, pandoc_export

pytestmark = pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")

SRC = "# Title\n\n## Results\n\nA graph with $n$ vertices.\n"


@pytest.mark.parametrize("fmt", ["docx", "odt", "epub", "pptx"])
def test_binary_format_is_written_to_the_output_file(tmp_path, fmt):
    out = tmp_path / f"doc.{fmt}"
    pandoc_export(source=SRC, to_format=fmt, output=str(out))
    # Each of these formats is a zip archive.
    assert zipfile.is_zipfile(out)


@pytest.mark.parametrize("fmt", ["docx", "epub"])
def test_binary_format_without_output_file_is_an_error(fmt):
    with pytest.raises(RSMApplicationError, match="output file"):
        pandoc_export(source=SRC, to_format=fmt)


@pytest.mark.skipif(shutil.which("xelatex") is None, reason="xelatex not installed")
@pytest.mark.skipif(shutil.which("pdfinfo") is None, reason="pdfinfo not installed")
def test_pdf_uses_the_braiid_styles(tmp_path):
    # braiid.sty sets an A4 page. Pandoc's own default is US letter, so an A4
    # page shows that the PDF was made with braiid.sty.
    import subprocess

    out = tmp_path / "doc.pdf"
    pandoc_export(source=SRC, to_format="pdf", output=str(out))
    info = subprocess.run(
        ["pdfinfo", str(out)], capture_output=True, text=True, check=True
    ).stdout
    assert "(A4)" in info, info


def test_reference_title_has_opening_and_closing_quotes():
    # A straight " prints as a closing quote on both sides in LaTeX output.
    src = (
        "# T\n\nSee :cite:k::.\n\n:references:\n"
        "@book{k,\n  author = {A. Author},\n  title = {Graph Theory},\n  year = {2008}\n}\n::\n"
    )
    tex = pandoc_export(source=src, to_format="latex")
    assert "``Graph Theory''" in tex, tex
