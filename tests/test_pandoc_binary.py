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
