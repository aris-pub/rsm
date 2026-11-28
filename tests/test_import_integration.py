"""End-to-end tests for the assembled import path (app.import_project).

These exercise resolve -> pandoc -> drop pandoc's bibliography -> append the
real one, the one function the `rsm import` CLI and rsmify both call. They need
pandoc; the structured output needs AnyStyle, so they assert the parts that
hold either way (the key is present, pandoc's collapsed copy is gone).
"""

import logging
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
        r"\documentclass{article}"
        "\n\\begin{document}\n\\cite{k}\n"
        r"\bibliography{refs}"
        "\n\\end{document}\n",
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
    # so MathJax can expand any macro pandoc left raw in the math.
    assert ":mathblock: {:preamble:}" in out
    assert "\\newcommand{\\RR}{\\mathbb{R}}" in out
    assert "\\newcommand{\\abs}[1]{\\lvert #1 \\rvert}" in out
    # \DeclareMathOperator is translated to a MathJax-safe \newcommand.
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
    r"\documentclass{article}"
    "\n\\begin{document}\n"
    r"Prior work \cite{DBLP:journals/corr/X}."
    "\n"
    r"\bibliography{refs}"
    "\n\\end{document}\n"
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


_NESTED_LIST = r"""\documentclass{article}
\begin{document}
We include the following:
\begin{itemize}
\item First point.
\item Second point, with sub-items:
  \begin{itemize}
  \item Sub A.
  \item Sub B.
  \end{itemize}
\item Third point.
\end{itemize}
\end{document}
"""


def test_import_nested_list(tmp_path):
    import rsm

    (tmp_path / "main.tex").write_text(_NESTED_LIST, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    assert ":itemize:" in out
    assert ":--: " in out  # sub-items use the depth-2 marker
    assert "::itemize:" not in out  # not the old glued nested block
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out
    # Sub A nests: a <ul> opens inside Second point's <li> before it closes.
    rest = html[html.index("Second point") :]
    assert "<ul" in rest and rest.index("<ul") < rest.index("</li>"), out


_TITLE_COLON = r"""\documentclass{article}
\begin{document}
\section{Methods}
\subsection{Pre-training}
\paragraph{Task \#1: Masked LM} We mask some input tokens at random.
\end{document}
"""


def test_import_paragraph_title_with_colon(tmp_path):
    import rsm

    (tmp_path / "main.tex").write_text(_TITLE_COLON, encoding="utf-8")
    out = app.import_project(str(tmp_path))
    # An internal colon in a title is escaped so the meta value parses.
    assert r"\:" in out
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out
    # It renders as a plain colon, backslash gone.
    assert "Task #1: Masked LM" in html


# rsm-dyb: pandoc drops a LaTeX command that it cannot expand, and reports it
# only with --verbose. The import turns each report into a warning.

_UNKNOWN_COMMANDS = r"""\documentclass{article}
\begin{document}
We study the co\Ktheory{} of rings, and the map\fooarrow{} below.
\end{document}
"""


def _skipped_warnings(caplog) -> list[str]:
    return [
        r.getMessage()
        for r in caplog.records
        if r.levelno == logging.WARNING and "pandoc dropped" in r.getMessage()
    ]


def test_import_warns_about_each_dropped_command(tmp_path, caplog):
    caplog.set_level(logging.WARNING, logger="RSM")
    (tmp_path / "t.tex").write_text(_UNKNOWN_COMMANDS, encoding="utf-8")
    app.import_project(str(tmp_path / "t.tex"))
    warnings = _skipped_warnings(caplog)
    assert len(warnings) == 2, warnings
    assert "\\Ktheory{}" in warnings[0] and "line 3" in warnings[0]
    assert "\\fooarrow{}" in warnings[1] and "line 3" in warnings[1]


def test_import_of_a_string_warns_about_dropped_commands(caplog):
    caplog.set_level(logging.WARNING, logger="RSM")
    app.pandoc_import(source=_UNKNOWN_COMMANDS, from_format="latex")
    assert len(_skipped_warnings(caplog)) == 2


def test_import_of_a_file_warns_about_dropped_commands(tmp_path, caplog):
    caplog.set_level(logging.WARNING, logger="RSM")
    (tmp_path / "t.tex").write_text(_UNKNOWN_COMMANDS, encoding="utf-8")
    app.pandoc_import(path=str(tmp_path / "t.tex"), from_format="latex")
    assert len(_skipped_warnings(caplog)) == 2


def test_import_without_dropped_commands_warns_about_none(tmp_path, caplog):
    caplog.set_level(logging.WARNING, logger="RSM")
    (tmp_path / "main.tex").write_text(_XREF, encoding="utf-8")
    app.import_project(str(tmp_path))
    assert not [r for r in caplog.records if "pandoc" in r.getMessage().lower()], (
        caplog.text
    )


# rsm-9oh: pandoc looks for the .sty file of a \usepackage in the folder where
# it runs, so the import runs it in the project's folder, wherever rsm runs.

_LOCAL_STY = r"""\documentclass{article}
\usepackage{mymacros}
\begin{document}
We study the co\Ktheory{} of rings.
\end{document}
"""


def _paper(tmp_path):
    paper = tmp_path / "paper"
    paper.mkdir()
    (paper / "t3.tex").write_text(_LOCAL_STY, encoding="utf-8")
    (paper / "mymacros.sty").write_text(
        r"\newcommand{\Ktheory}{$K$-theory}" + "\n", encoding="utf-8"
    )
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    return paper, elsewhere


def _tar(paper, out):
    import tarfile

    with tarfile.open(out, "w:gz") as tar:
        for f in paper.iterdir():
            tar.add(f, arcname=f.name)
    return out


def _zip(paper, out):
    import zipfile

    with zipfile.ZipFile(out, "w") as z:
        for f in paper.iterdir():
            z.write(f, arcname=f.name)
    return out


@pytest.mark.parametrize("kind", ["file", "folder", "tar", "zip"])
def test_import_uses_macros_from_a_local_sty(tmp_path, monkeypatch, kind):
    paper, elsewhere = _paper(tmp_path)
    src = {
        "file": lambda: paper / "t3.tex",
        "folder": lambda: paper,
        "tar": lambda: _tar(paper, tmp_path / "paper.tar.gz"),
        "zip": lambda: _zip(paper, tmp_path / "paper.zip"),
    }[kind]()
    monkeypatch.chdir(elsewhere)
    out = app.import_project(str(src))
    assert "co$K$-theory of rings" in out, out


# LaTeX looks for a .sty in the folder of the main file, so pandoc runs there,
# also when the main file is in a subfolder of the folder or the archive.
@pytest.mark.parametrize("kind", ["folder", "tar", "zip"])
def test_import_uses_a_local_sty_next_to_a_main_file_in_a_subfolder(
    tmp_path, monkeypatch, kind
):
    paper, elsewhere = _paper(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    paper.rename(project / "paper")
    if kind == "folder":
        src = project
    else:
        import tarfile
        import zipfile

        files = sorted((project / "paper").iterdir())
        if kind == "tar":
            src = tmp_path / "project.tar.gz"
            with tarfile.open(src, "w:gz") as tar:
                for f in files:
                    tar.add(f, arcname=f"paper/{f.name}")
        else:
            src = tmp_path / "project.zip"
            with zipfile.ZipFile(src, "w") as z:
                for f in files:
                    z.write(f, arcname=f"paper/{f.name}")
    monkeypatch.chdir(elsewhere)
    out = app.import_project(str(src))
    assert "co$K$-theory of rings" in out, out


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")
def test_import_warning_for_a_dropped_math_command_gives_its_line(caplog):
    import logging

    from rsm.app import pandoc_import

    caplog.set_level(logging.WARNING, logger="RSM")
    tex = "\\documentclass{article}\n\\begin{document}\nSee $x = \\eqref{a}$ here.\n\\end{document}\n"
    pandoc_import(source=tex, from_format="latex")
    assert "dropped \\eqref from math at line 3" in caplog.text, caplog.text
