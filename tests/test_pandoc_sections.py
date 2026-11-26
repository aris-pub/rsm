"""Section numbers in LaTeX and PDF export.

The HTML prints RSM's section numbers (1, 1.1, A) and references to sections use the
same numbers, so LaTeX and PDF must print RSM's numbers too.
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


@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="pdflatex not installed")
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
