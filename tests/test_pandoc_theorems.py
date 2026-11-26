"""Theorem-like blocks, proofs and equations in LaTeX and PDF export.

RSM numbers these blocks itself. The heading of each block and every reference to it
must print the same number, and :blockname: must name the block in both places, as
in the HTML output.
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

    ## Sec

    :theorem: {
      :label: thm-main
      :title: Main result
    }

      Every graph is fine.

    ::

    :lemma: {:label: lem-a}

      Some lemma.

    ::

    :proof:

      Clearly true.

    ::

    :remark: {
      :label: hint
      :blockname: Hint
    }

      What does inversion make of two tangent circles?

    ::

    :mathblock: {:label: eq-one}
      a + b = c
    ::

    See :ref:thm-main::, :ref:lem-a::, :ref:hint:: and :ref:eq-one::.
    """
)


@pytest.fixture(scope="module")
def latex():
    return pandoc_export(source=SRC, to_format="latex")


def test_theorem_heading_has_number_and_title(latex):
    assert re.search(
        r"\\renewcommand\{\\rsmblockname\}\{Theorem 1\.1\}\s*"
        r"\\begin\{theorem\}\[\{Main result\}\]",
        latex,
    )


def test_lemma_heading_has_number(latex):
    assert re.search(
        r"\\renewcommand\{\\rsmblockname\}\{Lemma 1\.2\}\s*\\begin\{lemma\}", latex
    )


def test_blockname_names_the_heading(latex):
    assert re.search(
        r"\\renewcommand\{\\rsmblockname\}\{Hint 1\.3\}\s*\\begin\{remark\}", latex
    )
    assert "Remark" not in latex


def test_theorem_environments_have_unnumbered_definitions(latex):
    # LaTeX must not number the blocks itself, or its numbers could differ from RSM's.
    assert r"\newtheorem*{theorem}{\rsmblockname}" in latex
    assert r"\newtheorem*{remark}{\rsmblockname}" in latex


def test_references_match_headings(latex):
    assert r"\hyperref[thm-main]{Theorem 1.1}" in latex
    assert r"\hyperref[lem-a]{Lemma 1.2}" in latex
    assert r"\hyperref[hint]{Hint 1.3}" in latex
    assert r"\hyperref[eq-one]{(1.1)}" in latex


def test_labels_have_anchors(latex):
    for label in ["thm-main", "lem-a", "hint"]:
        assert rf"\phantomsection\label{{{label}}}" in latex


def test_proof_environment(latex):
    assert re.search(r"\\begin\{proof\}\s*Clearly true\.\s*\\end\{proof\}", latex)


def test_equation_has_rsm_number_and_label(latex):
    assert re.search(
        r"\\begin\{equation\}\s*a \+ b = c\s*\\tag\{1\.1\}\\label\{eq-one\}\s*"
        r"\\end\{equation\}",
        latex,
    )


def test_title_is_escaped():
    src = SRC.replace(":title: Main result", ":title: Cats & dogs")
    latex = pandoc_export(source=src, to_format="latex")
    assert r"\begin{theorem}[{Cats \& dogs}]" in latex


def test_nonum_block_has_no_number():
    src = SRC.replace("  :title: Main result", "  :title: Main result\n  :nonum:")
    latex = pandoc_export(source=src, to_format="latex")
    assert r"\renewcommand{\rsmblockname}{Theorem}" in latex
    assert r"\renewcommand{\rsmblockname}{Lemma 1.1}" in latex


def _pdf_text(tmp_path) -> str:
    out = tmp_path / "doc.pdf"
    pandoc_export(source=SRC, to_format="pdf", output=str(out))
    # -layout keeps the equation and its number on one line.
    return subprocess.run(
        ["pdftotext", "-layout", str(out), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="pdflatex not installed")
@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="pdftotext not installed")
def test_pdf_headings_and_references(tmp_path):
    layout = _pdf_text(tmp_path)
    assert re.search(r"^\s*a\+b=c\s+\(1\.1\)\s*$", layout, re.MULTILINE)
    text = " ".join(layout.split())
    assert "Theorem 1.1 (Main result). Every graph is fine." in text
    assert "Lemma 1.2. Some lemma." in text
    assert "Proof. Clearly true." in text
    assert "Hint 1.3. What does inversion" in text
    assert "See Theorem 1.1, Lemma 1.2, Hint 1.3 and (1.1)." in text
    assert "Remark" not in text
