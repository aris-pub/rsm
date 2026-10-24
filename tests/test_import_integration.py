"""End-to-end tests for the assembled import path (app.import_project).

These exercise resolve -> pandoc -> drop pandoc's bibliography -> append the
real one, the one function the `rsm import` CLI and rsmify both call. They need
pandoc; the structured output needs AnyStyle, so they assert the parts that
hold either way (the key is present, pandoc's collapsed copy is gone).
"""

import shutil

import pytest

from rsm import app

HAS_PANDOC = shutil.which("pandoc") is not None

pytestmark = pytest.mark.skipif(not HAS_PANDOC, reason="pandoc not installed")

_INLINE = r"""\documentclass{article}
\begin{document}
We build on prior work \cite{knuth}.
\begin{thebibliography}{9}
\bibitem{knuth} Donald E. Knuth. The Art of Computer Programming. Addison-Wesley, 1968.
\end{thebibliography}
\end{document}
"""


def test_import_project_inline_bibliography(tmp_path):
    (tmp_path / "main.tex").write_text(_INLINE, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    body, sep, refs = out.partition(":references:")
    assert sep, "no :references: block emitted"
    assert ":cite:knuth::" in body
    assert "knuth" in refs
    # pandoc's collapsed copy is suppressed: the reference text appears only in
    # our block, never in the body.
    assert "Art of Computer Programming" in refs
    assert "Art of Computer Programming" not in body


def test_import_project_bib_passthrough(tmp_path):
    (tmp_path / "main.tex").write_text(
        r"\documentclass{article}" "\n\\begin{document}\n\\cite{k}\n"
        r"\bibliography{refs}" "\n\\end{document}\n",
        encoding="utf-8",
    )
    (tmp_path / "refs.bib").write_text(
        "@book{k, title={A Passthrough Book}, author={Writer, A}, year={2000}}",
        encoding="utf-8",
    )
    out = app.import_project(str(tmp_path))
    _body, sep, refs = out.partition(":references:")
    assert sep
    assert "@book{k" in refs
    assert "A Passthrough Book" in refs


def test_import_project_single_tex_file(tmp_path):
    f = tmp_path / "paper.tex"
    f.write_text(_INLINE, encoding="utf-8")
    out = app.import_project(str(f))
    assert ":cite:knuth::" in out
    assert ":references:" in out


_XREF = r"""\documentclass{article}
\newtheorem{theorem}{Theorem}
\begin{document}
\section{Intro}\label{sec:intro}
See Section~\ref{sec:intro}.
\begin{equation}\label{eq:e}
E = mc^2
\end{equation}
By \eqref{eq:e}.
\begin{theorem}\label{thm:main}
A statement.
\end{theorem}
See Theorem~\ref{thm:main}.
\end{document}
"""


_MACROS = r"""\documentclass{article}
\newcommand{\RR}{\mathbb{R}}
\newcommand{\abs}[1]{\lvert #1 \rvert}
\DeclareMathOperator{\argmin}{arg\,min}
\begin{document}
\section{Body}
Text $x \in \RR$ and $\abs{y}$ and $\argmin f$.
\end{document}
"""


def test_import_project_emits_preamble_macros(tmp_path):
    import rsm

    (tmp_path / "main.tex").write_text(_MACROS, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    # the preamble's macro definitions carry into RSM's hidden preamble block,
    # so Temml can expand any macro pandoc left raw in the math.
    assert ":mathblock: {:preamble:}" in out
    assert "\\newcommand{\\RR}{\\mathbb{R}}" in out
    assert "\\newcommand{\\abs}[1]{\\lvert #1 \\rvert}" in out
    # \DeclareMathOperator is translated to a Temml-safe \newcommand.
    assert "\\newcommand{\\argmin}{\\operatorname{arg\\,min}}" in out
    # placed so the document still renders, with the math-preamble class.
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert "math-preamble" in html


_TABLE = r"""\documentclass{article}
\begin{document}
\section{T}
\begin{tabular}{ll}
a & b \\
c & d \\
\end{tabular}
\end{document}
"""


def test_import_project_table(tmp_path):
    import re

    import rsm

    (tmp_path / "main.tex").write_text(_TABLE, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    assert ":table:" in out
    assert ":td:a::" in out and ":td:d::" in out
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert "<table" in html
    cells = [
        re.sub("<[^>]+>", "", x).strip()
        for x in re.findall(r"<td[^>]*>(.*?)</td>", html, re.S)
    ]
    assert cells == ["a", "b", "c", "d"]


def test_import_project_crossrefs(tmp_path):
    import rsm

    (tmp_path / "main.tex").write_text(_XREF, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    # Every section, equation, and theorem gets a plain generated label.
    assert ":label: sec-1" in out
    assert ":label: eqn-1" in out
    assert ":label: thm-1" in out
    # \ref, \eqref, and \ref to the theorem resolve to those generated labels.
    assert ":ref:sec-1::" in out
    assert ":ref:eqn-1::" in out
    assert ":ref:thm-1::" in out
    # The result renders with resolvable labels.
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'id="sec-1"' in html
    assert 'id="eqn-1"' in html
    assert 'id="thm-1"' in html


_PARAGRAPH = r"""\documentclass{article}
\begin{document}
\section{Model Architecture}
\subsection{Encoder and Decoder Stacks}
\paragraph{Encoder:} The encoder is composed of a stack of six identical layers.
\end{document}
"""

_SKIP = r"""\documentclass{article}
\begin{document}
\section{Results}
\subsubsection{Machine Translation} We report BLEU scores here.
\end{document}
"""


def test_import_paragraph_becomes_titled_paragraph(tmp_path):
    import rsm

    (tmp_path / "main.tex").write_text(_PARAGRAPH, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    # A LaTeX \paragraph is a titled paragraph in RSM, not a level-4 heading.
    assert ":paragraph: {:title: Encoder" in out
    assert "#### " not in out
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out
    assert "six identical layers" in html


def test_import_skipped_heading_levels_renumbered(tmp_path):
    import rsm

    # A subsubsection directly under a section skips the subsection level, which
    # RSM's strict nesting rejects unless the importer renumbers.
    (tmp_path / "main.tex").write_text(_SKIP, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    # A section plus a subsubsection renumbers to contiguous ## then ###, never
    # a #### that skips the subsection level.
    assert "#### " not in out
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out


_GLUED_MATH = r"""\documentclass{article}
\begin{document}
The model AOP$_1$ performs well in our tests.
\end{document}
"""


def test_import_inline_math_glues_to_text(tmp_path):
    import rsm

    (tmp_path / "main.tex").write_text(_GLUED_MATH, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    # Inline math uses $...$, which can sit directly against text; the verbose
    # :math: form cannot, so "AOP$_1$" would otherwise fail to parse.
    assert "$_1$" in out
    assert ":math: _1 ::" not in out
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out


_TITLED = r"""\documentclass{article}
\title{A Paper}
\begin{document}
\maketitle
\section{Introduction} First section text.
\section{Background} Second section text.
\end{document}
"""


def test_import_title_and_sibling_sections(tmp_path):
    import rsm

    (tmp_path / "main.tex").write_text(_TITLED, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    # The paper title is the single leading #; real sections start at ##, so two
    # sibling \section commands must not collide with the title.
    assert out.lstrip().startswith("# A Paper")
    assert "## Introduction" in out
    assert "## Background" in out
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out


_CITE_COLON = (
    r"\documentclass{article}" "\n\\begin{document}\n"
    r"Prior work \cite{DBLP:journals/corr/X}." "\n"
    r"\bibliography{refs}" "\n\\end{document}\n"
)

_FIG_REF = r"""\documentclass{article}
\begin{document}
\begin{figure}\caption{The model architecture.}\label{fig:x}\end{figure}
As shown in Figure \ref{fig:x}, it works.
\end{document}
"""

_TABLE_REF = r"""\documentclass{article}
\begin{document}
\begin{table}\caption{Results.}\begin{tabular}{cc}a&b\end{tabular}\label{tab:y}\end{table}
See Table \ref{tab:y} for results.
\end{document}
"""


def test_import_cite_key_with_colon_resolves(tmp_path):
    import rsm

    (tmp_path / "main.tex").write_text(_CITE_COLON, encoding="utf-8")
    (tmp_path / "refs.bib").write_text(
        "@article{DBLP:journals/corr/X, title={A Title}, author={Writer, A}, year={2020}}",
        encoding="utf-8",
    )
    out = app.import_project(str(tmp_path))
    # The colon is sanitized on both the cite and the bibitem key, so they match.
    assert ":cite:DBLP-journals/corr/X::" in out
    assert "@article{DBLP-journals/corr/X" in out
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out


def test_import_figure_ref_resolves(tmp_path):
    import rsm

    (tmp_path / "main.tex").write_text(_FIG_REF, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    assert ":label: fig-1" in out
    assert ":ref:fig-1::" in out
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out


def test_import_table_ref_resolves(tmp_path):
    import rsm

    (tmp_path / "main.tex").write_text(_TABLE_REF, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    assert ":label: tab-1" in out
    assert ":ref:tab-1::" in out
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out


_COLON_LIST = r"""\documentclass{article}
\begin{document}
The model works in three ways:
\begin{itemize}
\item first
\item second
\end{itemize}
\end{document}
"""


def test_import_colon_before_block_escaped(tmp_path):
    import rsm

    (tmp_path / "main.tex").write_text(_COLON_LIST, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    # A paragraph ending in a colon before a tag block is mis-tokenized, so the
    # importer escapes the trailing colon.
    assert r"three ways\:" in out
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out
    # The escaped colon renders as a plain colon.
    assert "three ways:" in html
