"""Theorem-like blocks, proofs and equations in pandoc export.

RSM numbers these blocks itself. The heading of each block and every reference to it
must print the same number, and :blockname: must name the block in both places, as
in the HTML output. Every export format prints these headings, not only LaTeX and PDF.
"""

import re
import shutil
import subprocess
import zipfile
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


PROOF_OF = SRC.replace(":proof:\n", ":proof: {:of: thm-main}\n")


def test_proof_of_names_the_result():
    latex = pandoc_export(source=PROOF_OF, to_format="latex")
    assert re.search(
        r"\\begin\{proof\}\[\{\{Proof of \\hyperref\[thm-main\]\{Theorem 1\.1\}\}\}\]\s*"
        r"Clearly true\.\s*\\end\{proof\}",
        latex,
    )


@pytest.mark.skipif(shutil.which("xelatex") is None, reason="xelatex not installed")
@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="pdftotext not installed")
def test_pdf_proof_of_names_the_result(tmp_path):
    out = tmp_path / "doc.pdf"
    pandoc_export(source=PROOF_OF, to_format="pdf", output=str(out))
    text = subprocess.run(
        ["pdftotext", str(out), "-"], capture_output=True, text=True, check=True
    ).stdout
    assert "Proof of Theorem 1.1. Clearly true." in " ".join(text.split())


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


@pytest.mark.skipif(shutil.which("xelatex") is None, reason="xelatex not installed")
@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="pdftotext not installed")
def test_pdf_headings_and_references(tmp_path):
    layout = _pdf_text(tmp_path)
    # XeLaTeX writes math letters as Unicode math italics, so normalize them
    # before looking for the equation line with its number.
    import unicodedata

    plain = unicodedata.normalize("NFKC", layout)
    assert re.search(r"^\s*a\s*\+\s*b\s*=\s*c\s+\(1\.1\)\s*$", plain, re.MULTILINE)
    text = " ".join(layout.split())
    assert "Theorem 1.1 (Main result). Every graph is fine." in text
    assert "Lemma 1.2. Some lemma." in text
    assert "Proof. Clearly true." in text
    assert "Hint 1.3. What does inversion" in text
    assert "See Theorem 1.1, Lemma 1.2, Hint 1.3 and (1.1)." in text
    assert "Remark" not in text


# A math block may hold a whole amsmath environment. The HTML gives such a block one
# number, so LaTeX and PDF must too, instead of numbering each line.

MULTI = dedent(
    r"""
    # Doc

    ## Sec

    :mathblock: {:label: e-align}
      \begin{align} a &= b \\ c &= d \end{align}
    ::

    :mathblock: {:label: e-gather}
      \begin{gather} x = 1 \\ y = 2 \end{gather}
    ::

    :mathblock: {:label: e-alignat}
      \begin{alignat}{2} a &= b &\quad c &= d \end{alignat}
    ::

    :mathblock: {:label: e-multline}
      \begin{multline} p + q \\ + r \end{multline}
    ::

    :mathblock: {:label: e-nonum, :nonum:}
      \begin{align} s &= t \end{align}
    ::

    :mathblock: {:label: e-flalign}
      \begin{flalign} a &= b \\ c &= \begin{cases} 1 \\ 2 \end{cases} \\ e &= \sum_{\substack{f \\ g}} h \end{flalign}
    ::

    :mathblock: {:label: e-flnonum, :nonum:}
      \begin{flalign} h &= i \\ j &= k \end{flalign}
    ::

    :mathblock: {:label: e-eq}
      \begin{equation} o = p \end{equation}
    ::

    See :ref:e-align::, :ref:e-gather::, :ref:e-alignat::, :ref:e-multline::,
    :ref:e-flalign:: and :ref:e-eq::.
    """
)


@pytest.fixture(scope="module")
def multi_latex():
    return " ".join(pandoc_export(source=MULTI, to_format="latex").split())


def test_align_has_one_rsm_number(multi_latex):
    assert (
        r"\begin{equation} \begin{aligned} a &= b \\ c &= d \end{aligned}"
        r" \tag{1.1}\label{e-align} \end{equation}"
    ) in multi_latex


def test_gather_has_one_rsm_number(multi_latex):
    assert (
        r"\begin{equation} \begin{gathered} x = 1 \\ y = 2 \end{gathered}"
        r" \tag{1.2}\label{e-gather} \end{equation}"
    ) in multi_latex


def test_alignat_has_one_rsm_number(multi_latex):
    assert (
        r"\begin{equation} \begin{alignedat}{2} a &= b &\quad c &= d \end{alignedat}"
        r" \tag{1.3}\label{e-alignat} \end{equation}"
    ) in multi_latex


def test_multline_has_one_rsm_number(multi_latex):
    assert (
        r"\begin{multline} p + q \\ + r \tag{1.4}\label{e-multline} \end{multline}"
    ) in multi_latex


def test_equation_has_one_rsm_number(multi_latex):
    # An equation inside the equation that carries RSM's number is a LaTeX error.
    assert (
        r"\begin{equation} o = p \tag{1.6}\label{e-eq} \end{equation}"
    ) in multi_latex


def test_flalign_has_one_rsm_number(multi_latex):
    # amsmath has no inner form of flalign, so every line but the last gets \notag.
    # A \\ inside braces or inside a nested environment does not end a line.
    assert (
        r"\begin{flalign} a &= b \notag\\ c &= \begin{cases} 1 \\ 2 \end{cases}"
        r" \notag\\ e &= \sum_{\substack{f \\ g}} h \tag{1.5}\label{e-flalign}"
        r" \end{flalign}"
    ) in multi_latex


def test_nonum_flalign_has_no_number(multi_latex):
    assert r"\begin{flalign*} h &= i \\ j &= k \end{flalign*}" in multi_latex


def test_nonum_multiline_block_has_no_number(multi_latex):
    assert (
        r"\begin{equation*} \begin{aligned} s &= t \end{aligned} \end{equation*}"
    ) in multi_latex
    assert r"\begin{align} s" not in multi_latex


def test_multiline_references_match(multi_latex):
    assert r"\hyperref[e-align]{(1.1)}" in multi_latex
    assert r"\hyperref[e-gather]{(1.2)}" in multi_latex
    assert r"\hyperref[e-alignat]{(1.3)}" in multi_latex
    assert r"\hyperref[e-multline]{(1.4)}" in multi_latex
    assert r"\hyperref[e-flalign]{(1.5)}" in multi_latex
    assert r"\hyperref[e-eq]{(1.6)}" in multi_latex


@pytest.mark.skipif(shutil.which("xelatex") is None, reason="xelatex not installed")
@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="pdftotext not installed")
def test_pdf_multiline_numbers(tmp_path):
    out = tmp_path / "multi.pdf"
    pandoc_export(source=MULTI, to_format="pdf", output=str(out))
    text = subprocess.run(
        ["pdftotext", str(out), "-"], capture_output=True, text=True, check=True
    ).stdout
    # Each numbered block prints its number once, and the sentence
    # that refers to them prints each number once more. No line has a number of its
    # own, and the :nonum: blocks print none.
    numbers = re.findall(r"\(\d[\d.]*\)", text)
    printed = [f"(1.{n})" for n in range(1, 7)]
    assert sorted(numbers) == sorted(printed * 2)


# Formats other than LaTeX have no theorem environments, so the headings are part of
# the text. Each heading must appear once.


def test_markdown_theorem_has_bold_run_in_heading():
    md = pandoc_export(source=SRC, to_format="markdown")
    assert "**Theorem 1.1 (Main result).** Every graph is fine." in md
    assert "**Lemma 1.2.** Some lemma." in md
    assert "**Hint 1.3.** What does inversion" in md
    assert "Remark" not in md


def test_markdown_proof_has_title():
    md = pandoc_export(source=SRC, to_format="markdown")
    assert "*Proof.* Clearly true." in md


def test_markdown_proof_of_names_the_result():
    md = pandoc_export(source=PROOF_OF, to_format="markdown")
    assert "*Proof of [Theorem 1.1](#thm-main).* Clearly true." in md


def test_markdown_nonum_heading_has_no_number():
    src = SRC.replace("  :title: Main result", "  :title: Main result\n  :nonum:")
    md = pandoc_export(source=src, to_format="markdown")
    assert "**Theorem (Main result).** Every graph is fine." in md
    assert "**Lemma 1.1.** Some lemma." in md


def test_html_theorem_heading():
    html = pandoc_export(source=PROOF_OF, to_format="html")
    text = " ".join(re.sub(r"<[^>]+>", "", html).split())
    assert "Theorem 1.1 (Main result). Every graph is fine." in text
    assert "Proof of Theorem 1.1. Clearly true." in text
    assert text.count("Theorem 1.1 (Main result).") == 1


def test_latex_has_no_text_heading(latex):
    assert "Theorem 1.1 (Main result)." not in latex
    assert r"\textbf{Lemma" not in latex
    assert r"\emph{Proof" not in latex


def _plain_text_of(tmp_path, src: str, fmt: str) -> str:
    out = tmp_path / f"doc.{fmt}"
    pandoc_export(source=src, to_format=fmt, output=str(out))
    plain = subprocess.run(
        ["pandoc", str(out), "-t", "plain", "--wrap=none"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return " ".join(plain.split())


@pytest.mark.parametrize("fmt", ["docx", "odt", "epub"])
def test_binary_formats_have_theorem_and_proof_headings(tmp_path, fmt):
    text = _plain_text_of(tmp_path, PROOF_OF, fmt)
    assert "Theorem 1.1 (Main result). Every graph is fine." in text
    assert "Lemma 1.2. Some lemma." in text
    assert "Proof of Theorem 1.1. Clearly true." in text
    assert "Hint 1.3. What does inversion" in text
    assert text.count("Theorem 1.1 (Main result).") == 1


# Formats other than LaTeX have no equation tags (pandoc drops \tag outside LaTeX),
# so the number is written into the math after a wide space.


def test_markdown_equation_has_rsm_number():
    md = pandoc_export(source=SRC, to_format="markdown")
    assert r"$$a + b = c \qquad (1.1)$$" in md


def test_html_equation_has_rsm_number():
    html = pandoc_export(source=SRC, to_format="html")
    assert re.search(r"<mn>1\.1</mn>", html)


@pytest.mark.parametrize("fmt", ["docx", "epub"])
def test_binary_formats_have_equation_numbers(tmp_path, fmt):
    text = _plain_text_of(tmp_path, SRC, fmt)
    assert re.search(r"a \+ b = c \(1\.1\)", text)


def test_unnumbered_equation_has_no_number():
    src = SRC.replace(":mathblock: {:label: eq-one}", ":mathblock: {:nonum:}").replace(
        " and :ref:eq-one::", ""
    )
    md = pandoc_export(source=src, to_format="markdown")
    assert "$$a + b = c$$" in md
    assert "qquad" not in md


# Formats other than LaTeX cannot show raw LaTeX, so a math block that holds an
# amsmath environment is sent to them as display math, in the inner form where
# amsmath has one, with RSM's number after it.


@pytest.fixture(scope="module")
def multi_markdown():
    return pandoc_export(source=MULTI, to_format="markdown")


@pytest.mark.parametrize(
    "math",
    [
        r"$$\begin{aligned} a &= b \\ c &= d \end{aligned} \qquad (1.1)$$",
        r"$$\begin{gathered} x = 1 \\ y = 2 \end{gathered} \qquad (1.2)$$",
        r"$$\begin{alignedat}{2} a &= b &\quad c &= d \end{alignedat} \qquad (1.3)$$",
        r"$$\begin{multline} p + q \\ + r \end{multline} \qquad (1.4)$$",
        r"$$\begin{aligned} s &= t \end{aligned}$$",
        r"$$\begin{flalign} a &= b \\ c &= \begin{cases} 1 \\ 2 \end{cases} \\ e &= "
        r"\sum_{\substack{f \\ g}} h \end{flalign} \qquad (1.5)$$",
        r"$$\begin{flalign} h &= i \\ j &= k \end{flalign}$$",
        r"$$o = p \qquad (1.6)$$",
    ],
)
def test_markdown_amsmath_block_is_display_math(multi_markdown, math):
    assert math in " ".join(multi_markdown.split())


def test_markdown_amsmath_block_has_no_raw_latex(multi_markdown):
    assert r"\begin{equation}" not in multi_markdown
    assert r"\tag" not in multi_markdown
    assert "{=latex}" not in multi_markdown


def _numbers(text: str) -> list[str]:
    return sorted(re.findall(r"\(1\.\d+\)", text))


# Each numbered block shows its number once, and the sentence that refers to them
# shows each number once more. The :nonum: blocks show none.
PRINTED_TWICE = sorted([f"(1.{n})" for n in range(1, 7)] * 2)


def _mathml_text(xhtml: str) -> str:
    # The annotation repeats the TeX source of each formula.
    text = re.sub(r"<annotation[^>]*>.*?</annotation>", "", xhtml, flags=re.DOTALL)
    return re.sub(r"<[^>]+>", "", text)


def test_html_amsmath_blocks_are_math_with_numbers():
    html = pandoc_export(source=MULTI, to_format="html")
    assert html.count('<math display="block"') == 8
    assert _numbers(_mathml_text(html)) == PRINTED_TWICE


def test_docx_amsmath_blocks_are_word_math_with_numbers(tmp_path):
    out = tmp_path / "multi.docx"
    pandoc_export(source=MULTI, to_format="docx", output=str(out))
    with zipfile.ZipFile(out) as z:
        xml = z.read("word/document.xml").decode()
    assert xml.count("<m:oMathPara>") == 8
    md = subprocess.run(
        ["pandoc", str(out), "-s", "-t", "markdown", "--wrap=none"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert _numbers(md) == PRINTED_TWICE


def test_epub_amsmath_blocks_are_math_with_numbers(tmp_path):
    out = tmp_path / "multi.epub"
    pandoc_export(source=MULTI, to_format="epub", output=str(out))
    with zipfile.ZipFile(out) as z:
        xhtml = "".join(z.read(n).decode() for n in z.namelist() if n.endswith(".xhtml"))
    assert xhtml.count('<math display="block"') == 8
    assert _numbers(_mathml_text(xhtml)) == PRINTED_TWICE
