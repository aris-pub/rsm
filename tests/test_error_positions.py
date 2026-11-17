"""Positions printed for a user to read are 1-based for both line and column,
like the linter and editors (rsm-7nj)."""

import logging
import subprocess

import pytest

import rsm
from rsm.rsmlogger import logger

# Line 2, column 3 holds ":accent: bogus".
# Line 7, column 23 holds the second "," in the span meta.
# Line 9, column 1 holds the stray "::".
SRC = (
    ":manuscript: {\n"
    "  :accent: bogus\n"
    "}\n"
    "\n"
    "OK.\n"
    "\n"
    "Bad :span: {:title: a,, :class: b} x:: here.\n"
    "\n"
    "::\n"
)


def _render(src: str) -> str:
    return rsm.render(src, handrails=False, source_offsets=False)


def _records(caplog, text: str) -> list[logging.LogRecord]:
    return [r for r in caplog.records if text in r.getMessage()]


def _point(rec: logging.LogRecord) -> tuple[int, int, int, int]:
    return (rec.start_row, rec.start_col, rec.end_row, rec.end_col)


def test_bad_meta_value_position_is_1_based(caplog):
    _render(SRC)
    (rec,) = _records(caplog, "Invalid value for :accent:")
    assert _point(rec) == (2, 3, 2, 17), caplog.text
    assert "on line 2:" in rec.getMessage()


def test_meta_parse_error_position_is_1_based(caplog):
    _render(SRC)
    (rec,) = _records(caplog, "Parse error in meta")
    assert _point(rec) == (7, 23, 7, 24), caplog.text


def test_cst_error_position_is_1_based(caplog):
    _render("A.\n\n::\n")
    (rec,) = _records(caplog, "The CST contains errors.")
    assert _point(rec) == (3, 1, 3, 3), caplog.text


def test_rawhtml_warning_position_is_1_based(caplog):
    with caplog.at_level(logging.WARNING):
        _render("A :rawhtml: <b>x</b> :: b.\n")
    (rec,) = _records(caplog, "has no :alt:")
    assert (rec.start_row, rec.start_col) == (1, 3), caplog.text


def test_cst_error_text_in_page_is_1_based():
    html = _render("A.\n\n::\n")
    assert "[CST error at (3, 1) - (3, 3)]" in html, html


@pytest.fixture
def stderr_logs(capsys):
    def run(fmt: str) -> list[str]:
        try:
            capsys.readouterr()
            rsm.render(
                SRC,
                handrails=False,
                source_offsets=False,
                log_format=fmt,
                log_time=False,
                log_lineno=False,
            )
            return capsys.readouterr().err.strip().split("\n")
        finally:
            logger.handlers.clear()

    return run


def test_lint_format_positions_are_1_based(stderr_logs):
    lines = stderr_logs("lint")
    assert "src:2:3: ERROR: Invalid value for :accent: on line 2: 'bogus'." in "\n".join(lines)
    assert "src:7:23: ERROR: Parse error in meta" in "\n".join(lines)
    assert "src:9:1: WRN: The CST contains errors." in lines


def test_rsm_format_positions_are_1_based(stderr_logs):
    text = "\n".join(stderr_logs("rsm"))
    assert "on line 2: 'bogus'" in text
    assert "| (2, 3) - (2, 17) |" in text
    assert "| (7, 23) - (7, 24) |" in text
    assert "| (9, 1) - (9, 3) |" in text


@pytest.mark.parametrize("fmt", ["plain", "json"])
def test_plain_and_json_line_in_message_is_1_based(stderr_logs, fmt):
    text = "\n".join(stderr_logs(fmt))
    assert "Invalid value for :accent: on line 2:" in text


@pytest.mark.slow
def test_rsm_check_lint_format_is_1_based(tmp_path):
    src_file = tmp_path / "t.rsm"
    src_file.write_text(SRC)
    proc = subprocess.run(
        ["rsm", "check", str(src_file), "--log-format", "lint"],
        capture_output=True,
        text=True,
    )
    lines = proc.stderr.strip().split("\n")
    assert any(line.startswith("src:2:3: ERROR: Invalid value for :accent:") for line in lines), proc.stderr
    assert any(line.startswith("src:7:23: ERROR: Parse error in meta") for line in lines), proc.stderr
    assert "src:9:1: WRN: The CST contains errors." in lines, proc.stderr
