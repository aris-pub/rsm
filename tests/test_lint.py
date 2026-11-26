import re
import subprocess

import pytest
import ujson as json

EMPTY_MANUSCRIPT = " "
EMPTY_MANUSCRIPT_LOGS = [
    {
        "name": "RSM",
        "level": "LINT",
        "msg": "Manuscript with no title",
        "filename": "linter.py",
        "start_row": 1,
        "start_col": 2,
        "end_row": 1,
        "end_col": 2,
    }
]

WRONG_MANUSCRIPT = "::"
WRONG_MANUSCRIPT_LOGS = [
    {
        "name": "RSM.parse",
        "level": "WRN",
        "msg": "The CST contains errors.",
        "filename": "tsparser.py",
        "start_row": 1,
        "start_col": 1,
        "end_row": 1,
        "end_col": 3,
    },
    {
        "name": "RSM",
        "level": "LINT",
        "msg": "Manuscript with no title",
        "filename": "linter.py",
        "start_row": 1,
        "start_col": 1,
        "end_row": 1,
        "end_col": 3,
    },
]


def cmd(src: str, log_format: str, verbose: int = 0):
    args = [
        "rsm",
        "check",
        f'"{src}"',
        "--string",
        f"--log-format {log_format}",
        "--log-no-timestamps",
        "--log-no-lineno",
    ]
    if verbose:
        args.append("-" + ("v" * verbose))
    return " ".join(args)


def run(src: str, log_format: str, verbose: int = 0, replace=False, split=False):
    proc = subprocess.run(
        cmd(src, log_format, verbose),
        check=True,
        shell=True,
        capture_output=True,
    )
    # JSON output goes to stderr, warnings go to stderr too, so we need to filter
    result = proc.stderr.decode("utf-8")

    # Filter out the pkg_resources warning lines
    lines = result.split("\n")
    filtered_lines = []
    for line in lines:
        if (
            "pkg_resources is deprecated" not in line
            and '__import__("pkg_resources")' not in line
        ):
            filtered_lines.append(line)
    result = "\n".join(filtered_lines).strip()

    if replace:
        result = re.sub(r"}\s*{", "},{", result)
    if split:
        result = [line.strip() for line in result.strip().split("\n")]
    return result


@pytest.mark.slow
def test_json_logs_of_empty_manuscript():
    have = [json.loads(run(EMPTY_MANUSCRIPT, "json"))]
    assert have == EMPTY_MANUSCRIPT_LOGS


@pytest.mark.slow
def test_plain_logs_of_empty_manuscript():
    have = run(EMPTY_MANUSCRIPT, "plain").strip()
    assert have == EMPTY_MANUSCRIPT_LOGS[0]["msg"]


@pytest.mark.slow
def test_json_logs_of_wrong_manuscript():
    output = run(WRONG_MANUSCRIPT, "json", replace=True)
    have = json.loads(f"[{output}]")
    assert have == WRONG_MANUSCRIPT_LOGS


@pytest.mark.slow
def test_plain_logs_of_wrong_manuscript():
    have = run(WRONG_MANUSCRIPT, "plain", split=True)
    assert have == [r["msg"] for r in WRONG_MANUSCRIPT_LOGS]


@pytest.mark.parametrize("option", ["handrails", "strict", "loglevel"])
def test_lint_rejects_options_that_it_does_not_use(option):
    import rsm

    with pytest.raises(TypeError):
        rsm.lint("# Title\n", **{option: True})


def test_linter_app_rejects_loglevel():
    from rsm.app import LinterApp

    with pytest.raises(TypeError):
        LinterApp(plain="# Title\n", loglevel=10)
