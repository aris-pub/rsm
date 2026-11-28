"""Errors for LaTeX commands in math that do what RSM tags already do.

LaTeX in RSM math is for typesetting only. Labels, numbers, references, citations,
sections, captions and footnotes come from RSM tags and meta keys, so the build
stops when math uses the LaTeX commands for them.
"""

from textwrap import dedent

import pytest

import rsm
from rsm.tsparser import RSMParserError, TSParser

LABEL = "Give the math block a :label: instead."
TAG = "RSM numbers the block. Use :nonum: on the block to remove the number."
NONUM = "Use :nonum: on the block to remove the number."
REF = "Write :ref:<label>:: outside the math instead."
CITE = "Write :cite:<key>:: outside the math instead."
SECTION = "Use a heading such as ## Title instead."
CAPTION = "Use :caption: in a :figure: or a :table: instead."
FOOTNOTE = "Use a :note: outside the math instead."


def _error(src: str) -> RSMParserError:
    with pytest.raises(RSMParserError) as info:
        TSParser().parse(dedent(src))
    return info.value


def _message(name: str, line: int, advice: str) -> str:
    return f"\\{name} cannot be used in math (line {line}). {advice}"


@pytest.mark.parametrize(
    "latex,name,advice",
    [
        (r"a = b \label{eq}", "label", LABEL),
        (r"a = b \tag{5}", "tag", TAG),
        (r"a = b \tag*{5}", "tag", TAG),
        (r"a = b \notag", "notag", NONUM),
        (r"a = b \nonumber", "nonumber", NONUM),
        (r"a = \ref{x}", "ref", REF),
        (r"a = \eqref{x}", "eqref", REF),
        (r"a = \pageref{x}", "pageref", REF),
        (r"a = \autoref{x}", "autoref", REF),
        (r"a = \cref{x}", "cref", REF),
        (r"a = \Cref{x}", "Cref", REF),
        (r"a = \nameref{x}", "nameref", REF),
        (r"a = \hyperref[x]{y}", "hyperref", REF),
        (r"a = \cite{x}", "cite", CITE),
        (r"a = \citep{x}", "citep", CITE),
        (r"a = \citet{x}", "citet", CITE),
        (r"a = \citealp{x}", "citealp", CITE),
        (r"a = \citeauthor{x}", "citeauthor", CITE),
        (r"\section{A} a = b", "section", SECTION),
        (r"\caption{A} a = b", "caption", CAPTION),
        (r"a = b \footnote{A}", "footnote", FOOTNOTE),
    ],
)
def test_display_math_errors(latex, name, advice):
    err = _error(f"# T\n\n:mathblock:\n  {latex}\n::\n")
    assert err.msg == _message(name, 4, advice)


@pytest.mark.parametrize(
    "command",
    [
        "part",
        "chapter",
        "section",
        "subsection",
        "subsubsection",
        "paragraph",
        "subparagraph",
    ],
)
def test_every_sectioning_command_errors(command):
    err = _error(f"# T\n\n$$\n\\{command}{{A}} a = b\n$$\n")
    assert err.msg == _message(command, 4, SECTION)


def test_inline_math_errors():
    err = _error("# T\n\nSee $a \\label{x}$ here.\n")
    assert err.msg == _message("label", 3, LABEL)


def test_preamble_errors():
    err = _error(
        "# T\n\n$$ {:preamble:}\n\\newcommand{\\R}{\\mathbb{R}} \\label{p}\n$$\n"
    )
    assert err.msg == _message("label", 4, LABEL)


def test_error_gives_the_position():
    err = _error("# T\n\n:mathblock:\n  a = b \\\\\n  c = d \\label{x}\n::\n")
    assert err.msg == _message("label", 5, LABEL)
    # Rows and columns in a position count from 1. \label is on the fifth line.
    assert (err.position["start_row"], err.position["start_col"]) == (5, 9)


def test_inline_error_gives_the_column():
    err = _error("# T\n\nSee $a \\label{x}$ here.\n")
    assert (err.position["start_row"], err.position["start_col"]) == (3, 8)


def test_build_stops():
    with pytest.raises(RSMParserError):
        rsm.build("# T\n\n:mathblock:\n  a = b \\label{x}\n::\n")


def test_rsm_check_reports_the_position(tmp_path, capsys):
    path = tmp_path / "doc.rsm"
    path.write_text("# T\n\n:mathblock:\n  a = b \\label{x}\n::\n")
    rsm.app.lint(path=str(path), log_format="lint")
    out = capsys.readouterr()
    assert f"4:9: ERROR: There was an error: {_message('label', 4, LABEL)}" in (
        out.out + out.err
    )


STARRED = ["align*", "gather*", "multline*", "flalign*", "alignat*", "equation*"]


def _starred_block(env: str, meta: str = "") -> str:
    args = "{2}" if env == "alignat*" else ""
    return f":mathblock:{meta}\n  \\begin{{{env}}}{args} a &= b \\end{{{env}}}\n::\n"


@pytest.mark.parametrize("env", STARRED)
def test_starred_environment_errors(env):
    err = _error(f"# T\n\n{_starred_block(env)}")
    plain = env.removesuffix("*")
    assert err.msg == (
        f"{env} cannot be used in math (line 4). Use {plain} and put :nonum: on "
        "the block to remove the number."
    )


@pytest.mark.parametrize(
    "src",
    [
        f"# T\n\n{_starred_block('align*', ' {:nonum:}')}",
        f":config: {{\n  :numbering: none\n}}\n::\n\n# T\n\n{_starred_block('align*')}",
        f"# T\n\n{_starred_block('align*')}\n:config: {{\n  :numbering: none\n}}\n::\n",
        "# T\n\n$$ {:preamble:}\n\\begin{align*} a \\end{align*}\n$$\n",
        "# T\n\nSee $\\begin{align*} a \\end{align*}$ here.\n",
    ],
    ids=["nonum", "numbering-none", "config-after", "preamble", "inline"],
)
def test_starred_environment_errors_in_every_kind_of_math(src):
    assert _error(src).msg.startswith("align* cannot be used in math")


@pytest.mark.parametrize("env", ["eqnarray", "eqnarray*"])
def test_eqnarray_errors(env):
    err = _error(f"# T\n\n:mathblock:\n  \\begin{{{env}}} a &=& b \\end{{{env}}}\n::\n")
    assert err.msg == (
        f"{env} cannot be used in math (line 4). Use align instead, and :nonum: on "
        "the block to remove the number."
    )


@pytest.mark.parametrize(
    "latex",
    [
        r"\partial f",
        r"\tagged",
        r"\labelx",
        r"\refstepcounter",
        r"\captionof",
        r"\citex",
        r"a \\label",
        r"\begin{align} a &= b \end{align}",
        r"\begin{aligned} a &= b \end{aligned}",
        r"\begin{cases} 1 \end{cases}",
    ],
)
def test_typesetting_commands_build(latex):
    TSParser().parse(f"# T\n\n:mathblock:\n  {latex}\n::\n")


@pytest.mark.parametrize("latex", [r"a \\ \label{x}", r"a \% \label{x}"])
def test_command_after_escape_errors(latex):
    err = _error(f"# T\n\n:mathblock:\n  {latex}\n::\n")
    assert err.msg == _message("label", 4, LABEL)


def test_comment_in_math_builds():
    TSParser().parse("# T\n\n:mathblock:\n  a = b % \\label{x}\n::\n")


def test_command_outside_math_builds():
    TSParser().parse("# T\n\nThe LaTeX command \\label is not math.\n")
