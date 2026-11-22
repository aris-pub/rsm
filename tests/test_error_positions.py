"""Positions printed for a user to read are 1-based for both line and column,
like the linter and editors (rsm-7nj)."""

import logging
import subprocess

import pytest
import ujson as json

import rsm
from rsm.rsmlogger import JSONFormatter, logger

# Line 2, column 3 holds ":accent: bogus".
# Line 7, column 13 holds ":title:", which has no value.
# Line 9, column 1 holds the stray "::".
SRC = (
    ":manuscript: {\n"
    "  :accent: bogus\n"
    "}\n"
    "\n"
    "OK.\n"
    "\n"
    "Bad :span: {:title: :class: b} x:: here.\n"
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
    assert _point(rec) == (7, 13, 7, 20), caplog.text


def test_cst_error_position_is_1_based(caplog):
    _render("A.\n\n::\n")
    (rec,) = _records(caplog, "The CST contains errors.")
    assert _point(rec) == (3, 1, 3, 3), caplog.text


def test_rawhtml_warning_position_is_1_based(caplog):
    with caplog.at_level(logging.WARNING):
        _render("A :html: <b>x</b> :: b.\n")
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
    assert (
        "src:2:3: ERROR: Invalid value for :accent: on line 2: 'bogus'."
        in "\n".join(lines)
    )
    assert "src:7:13: ERROR: Parse error in meta" in "\n".join(lines)
    assert "src:9:1: WRN: The CST contains errors." in lines


def test_rsm_format_positions_are_1_based(stderr_logs):
    text = "\n".join(stderr_logs("rsm"))
    assert "on line 2: 'bogus'" in text
    assert "| (2, 3) - (2, 17) |" in text
    assert "| (7, 13) - (7, 20) |" in text
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
    assert any(
        line.startswith("src:2:3: ERROR: Invalid value for :accent:") for line in lines
    ), proc.stderr
    assert any(
        line.startswith("src:7:13: ERROR: Parse error in meta") for line in lines
    ), proc.stderr
    assert "src:9:1: WRN: The CST contains errors." in lines, proc.stderr


# The section and the manuscript start at line 1 and the math block at line 5.
# The section ends at line 7, column 3, and the manuscript at line 8, column 1.
LINT_SRC = "## Sec\n\nHello.\n\n$$\nx\n$$\n"

POSITION_FIELDS = ("start_row", "start_col", "end_row", "end_col")


@pytest.fixture
def lint_stderr(capsys):
    def run(src: str, fmt: str) -> str:
        try:
            capsys.readouterr()
            rsm.lint(src, log_format=fmt, log_time=False, log_lineno=False)
            return capsys.readouterr().err
        finally:
            logger.handlers.clear()

    return run


def _json_records(err: str) -> dict[str, dict]:
    return {r["msg"]: r for r in map(json.loads, err.strip().split("\n"))}


def _json_point(rec: dict) -> tuple[int, ...]:
    return tuple(rec[k] for k in POSITION_FIELDS)


def test_rsm_format_prints_lint_messages(lint_stderr):
    err = lint_stderr(LINT_SRC, "rsm")
    assert "Logging error" not in err, err
    assert "Manuscript with no title" in err
    assert "| (1, 1) - (8, 1) |" in err
    assert "Section with no label" in err
    assert "| (1, 1) - (7, 3) |" in err
    assert "MathBlock must be direct child of Paragraph" in err
    assert "| (5, 1) - (7, 3) |" in err


def test_rsm_format_prints_lint_messages_with_parse_error(lint_stderr):
    err = lint_stderr("A.\n\n::\n", "rsm")
    assert "Logging error" not in err, err
    assert "The CST contains errors." in err
    assert "| (3, 1) - (3, 3) |" in err
    assert "Manuscript with no title" in err
    assert "| (1, 1) - (4, 1) |" in err


def test_json_format_has_positions_of_lint_messages(lint_stderr):
    recs = _json_records(lint_stderr(LINT_SRC, "json"))
    assert _json_point(recs["Manuscript with no title"]) == (1, 1, 8, 1)
    assert _json_point(recs["Section with no label"]) == (1, 1, 7, 3)


def test_json_format_has_positions_of_parse_errors(stderr_logs):
    recs = _json_records("\n".join(stderr_logs("json")))
    assert _json_point(recs["The CST contains errors."]) == (9, 1, 9, 3)
    (meta,) = [r for m, r in recs.items() if m.startswith("Parse error in meta")]
    assert _json_point(meta) == (7, 13, 7, 20)


def test_json_format_leaves_out_positions_that_a_record_lacks():
    rec = logging.LogRecord(
        "RSM", logging.WARNING, "x.py", 1, "No position.", None, None
    )
    out = json.loads(JSONFormatter(log_time=False, log_lineno=False).format(rec))
    assert not set(POSITION_FIELDS) & set(out)


@pytest.mark.slow
def test_rsm_check_rsm_format_prints_lint_messages(tmp_path):
    src_file = tmp_path / "t.rsm"
    src_file.write_text("A.\n\n::\n")
    proc = subprocess.run(
        ["rsm", "check", str(src_file), "--log-format", "rsm"],
        capture_output=True,
        text=True,
    )
    assert "Logging error" not in proc.stderr, proc.stderr
    assert "| (3, 1) - (3, 3) |" in proc.stderr, proc.stderr
    assert "Manuscript with no title" in proc.stderr, proc.stderr
    assert "| (1, 1) - (4, 1) |" in proc.stderr, proc.stderr
