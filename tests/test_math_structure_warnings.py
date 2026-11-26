"""Warnings for LaTeX commands in math that are about document structure.

LaTeX in RSM math is for typesetting and layout only. Labels, numbers, references,
sections and captions come from RSM tags and meta keys, so RSM warns when math uses
the LaTeX commands for them.
"""

import logging
from textwrap import dedent

import pytest

import rsm


def _warnings(caplog, src: str) -> list[logging.LogRecord]:
    caplog.set_level(logging.WARNING, logger="RSM")
    rsm.render(dedent(src), handrails=False)
    return [r for r in caplog.records if r.levelno == logging.WARNING]


def _messages(records: list[logging.LogRecord]) -> list[str]:
    return [r.getMessage() for r in records]


LABEL = "\\label in math is ignored by RSM. Give the block a :label: instead."
TAG = (
    "\\tag in math does not set the number in RSM. RSM numbers the block. "
    "Use :nonum: on the block to remove the number."
)
NOTAG = "\\notag does not remove the number in RSM. Use :nonum: on the block."
NONUMBER = "\\nonumber does not remove the number in RSM. Use :nonum: on the block."
REF = (
    "\\ref in math is not a reference in RSM. Write :ref:<label>:: outside the "
    "math instead."
)
EQREF = (
    "\\eqref in math is not a reference in RSM. Write :ref:<label>:: outside the "
    "math instead."
)
CITE = (
    "\\cite in math is not a citation in RSM. Write :cite:<key>:: outside the "
    "math instead."
)
SECTION = (
    "\\section in math does not start a section in RSM. Use a heading such as "
    "## Title instead."
)
CAPTION = (
    "\\caption in math is ignored by RSM. Use :caption: in a :figure: or a "
    ":table: instead."
)


@pytest.mark.parametrize(
    "latex,message",
    [
        (r"a = b \label{eq}", LABEL),
        (r"a = b \tag{5}", TAG),
        (r"a = b \tag*{5}", TAG),
        (r"a = b \notag", NOTAG),
        (r"a = b \nonumber", NONUMBER),
        (r"a = \ref{x}", REF),
        (r"a = \eqref{x}", EQREF),
        (r"a = \cite{x}", CITE),
        (r"\section{A} a = b", SECTION),
        (r"\caption{A} a = b", CAPTION),
    ],
)
def test_display_math_warns(caplog, latex, message):
    records = _warnings(caplog, f"# T\n\n:mathblock:\n  {latex}\n::\n")
    assert message in _messages(records)


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
def test_every_sectioning_command_warns(caplog, command):
    records = _warnings(caplog, f"# T\n\n$$\n\\{command}{{A}} a = b\n$$\n")
    assert (
        f"\\{command} in math does not start a section in RSM. Use a heading such "
        "as ## Title instead."
    ) in _messages(records)


def test_inline_math_warns(caplog):
    records = _warnings(caplog, "# T\n\nSee $a \\label{x}$ here.\n")
    assert LABEL in _messages(records)


def test_preamble_warns(caplog):
    records = _warnings(
        caplog,
        "# T\n\n$$ {:preamble:}\n\\newcommand{\\R}{\\mathbb{R}} \\label{p}\n$$\n",
    )
    assert LABEL in _messages(records)


def test_warning_gives_the_line(caplog):
    src = "# T\n\n:mathblock:\n  a = b \\\\\n  c = d \\label{x}\n::\n"
    (record,) = [r for r in _warnings(caplog, src) if r.getMessage() == LABEL]
    # Rows and columns in a warning count from 1. \label is on the fifth line.
    assert record.start_row == 5
    assert record.start_col == 9


def test_inline_warning_gives_the_column(caplog):
    (record,) = _warnings(caplog, "# T\n\nSee $a \\label{x}$ here.\n")
    assert (record.start_row, record.start_col) == (3, 8)


@pytest.mark.parametrize(
    "env", ["align*", "gather*", "multline*", "flalign*", "alignat*", "equation*"]
)
def test_starred_environment_warns(caplog, env):
    args = "{2}" if env == "alignat*" else ""
    src = f"# T\n\n:mathblock:\n  \\begin{{{env}}}{args} a &= b \\end{{{env}}}\n::\n"
    records = _warnings(caplog, src)
    assert (
        f"{env} does not remove the number in RSM. Use :nonum: on the block."
    ) in _messages(records)


def test_starred_environment_in_nonum_block_does_not_warn(caplog):
    src = "# T\n\n:mathblock: {:nonum:}\n  \\begin{align*} a &= b \\end{align*}\n::\n"
    assert _warnings(caplog, src) == []


def test_starred_environment_with_numbering_none_does_not_warn(caplog):
    src = (
        ":config: {\n  :numbering: none\n}\n::\n\n# T\n\n"
        ":mathblock:\n  \\begin{align*} a &= b \\end{align*}\n::\n"
    )
    assert _warnings(caplog, src) == []


def test_starred_environment_in_preamble_does_not_warn(caplog):
    src = "# T\n\n$$ {:preamble:}\n\\begin{align*} a \\end{align*}\n$$\n"
    assert _warnings(caplog, src) == []


@pytest.mark.parametrize(
    "latex",
    [
        r"\partial f",
        r"\tagged",
        r"\labelx",
        r"\refstepcounter",
        r"\captionof",
        r"a \\label",
        r"\begin{aligned} a &= b \end{aligned}",
        r"\begin{cases} 1 \end{cases}",
    ],
)
def test_layout_commands_do_not_warn(caplog, latex):
    assert _warnings(caplog, f"# T\n\n:mathblock:\n  {latex}\n::\n") == []


@pytest.mark.parametrize("latex", [r"a \\ \label{x}", r"a \% \label{x}"])
def test_command_after_escape_warns(caplog, latex):
    records = _warnings(caplog, f"# T\n\n:mathblock:\n  {latex}\n::\n")
    assert _messages(records) == [LABEL]


def test_comment_in_math_does_not_warn(caplog):
    src = "# T\n\n:mathblock:\n  a = b % \\label{x}\n::\n"
    assert _warnings(caplog, src) == []


def test_html_numbers_starred_block():
    html = rsm.render(
        "# T\n\n## S\n\n:mathblock: {:label: e}\n  \\begin{align*} a &= b "
        "\\end{align*}\n::\n\nSee :ref:e::.\n",
        handrails=False,
    )
    assert "(1.1)" in html
