"""Section numbers in pandoc export.

The HTML prints RSM's section numbers (1, 1.1, A) and references to sections use the
same numbers, so every export format must print RSM's numbers too.
"""

import re
import shutil
import subprocess
from textwrap import dedent

import pytest

from rsm.app import pandoc_export

pytestmark = pytest.mark.skipif(
    shutil.which("pandoc") is None, reason="pandoc not installed"
)

SRC = dedent(
    """\
    # Doc

    ## Intro {:nonum:}

    Hello.

    ## Sec

    Text.

    ### Sub {:label: sub-a}

    More text.

    #### Subsub

    Deep text.

    :appendix:

    ## Extra

    See :ref:sub-a::.

    :references:
      @book{knuth,
        title={The Art},
        author={Knuth, D.},
        year={2014}
      }
    ::

    :cite:knuth::
    """
)


@pytest.fixture(scope="module")
def latex():
    return pandoc_export(source=SRC, to_format="latex")


def test_sections_are_numbered(latex):
    assert r"\setcounter{secnumdepth}{3}" in latex.split(r"\begin{document}")[0]


def test_headings_carry_rsm_numbers(latex):
    assert re.search(r"\\renewcommand\{\\rsmsecnum\}\{1\}\s*\\section\{Sec\}", latex)
    assert re.search(
        r"\\renewcommand\{\\rsmsecnum\}\{1\.1\}\s*\\subsection\{Sub\}", latex
    )
    assert re.search(
        r"\\renewcommand\{\\rsmsecnum\}\{1\.1\.1\}\s*\\subsubsection\{Subsub\}", latex
    )
    assert re.search(r"\\renewcommand\{\\rsmsecnum\}\{A\}\s*\\section\{Extra\}", latex)


def test_unnumbered_headings_are_starred(latex):
    assert r"\section*{Intro}" in latex
    assert r"\section*{References}" in latex


def test_reference_matches_heading(latex):
    assert r"\hyperref[sub-a]{Section 1.1}" in latex


@pytest.mark.skipif(shutil.which("xelatex") is None, reason="xelatex not installed")
@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="pdftotext not installed")
def test_pdf_headings_have_rsm_numbers(tmp_path):
    out = tmp_path / "doc.pdf"
    pandoc_export(source=SRC, to_format="pdf", output=str(out))
    text = subprocess.run(
        ["pdftotext", "-layout", str(out), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    lines = [" ".join(line.split()) for line in text.splitlines()]
    assert "Intro" in lines
    assert "1 Sec" in lines
    assert "1.1 Sub" in lines
    assert "1.1.1 Subsub" in lines
    assert "A Extra" in lines
    assert "References" in lines
    assert "See Section 1.1." in lines


# Formats other than LaTeX do not number headings, so the number is part of the title.


def test_markdown_headings_have_rsm_numbers():
    md = pandoc_export(source=SRC, to_format="markdown")
    headings = [line.split(" {")[0] for line in md.splitlines() if line.startswith("#")]
    assert headings == [
        "# Intro",
        "# 1 Sec",
        "## 1.1 Sub",
        "### 1.1.1 Subsub",
        "# A Extra",
        "# References",
    ]


def test_html_headings_have_rsm_numbers():
    html = pandoc_export(source=SRC, to_format="html")
    assert re.search(r"<h1[^>]*>1 Sec</h1>", html)
    assert re.search(r"<h2[^>]*>1\.1 Sub</h2>", html)
    assert re.search(r"<h1[^>]*>A Extra</h1>", html)
    assert re.search(r"<h1[^>]*>Intro</h1>", html)


def test_latex_section_titles_have_no_number(latex):
    assert r"\section{Sec}" in latex
    assert "1 Sec" not in latex


@pytest.mark.parametrize("fmt", ["docx", "odt", "epub"])
def test_binary_formats_have_section_numbers(tmp_path, fmt):
    out = tmp_path / f"doc.{fmt}"
    pandoc_export(source=SRC, to_format=fmt, output=str(out))
    plain = subprocess.run(
        ["pandoc", str(out), "-t", "plain", "--wrap=none"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    lines = [" ".join(line.split()) for line in plain.splitlines()]
    for heading in ["Intro", "1 Sec", "1.1 Sub", "1.1.1 Subsub", "A Extra"]:
        assert heading in lines
