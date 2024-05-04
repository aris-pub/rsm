import re
import subprocess

import pytest
import ujson as json

EMPTY_MANUSCRIPT = ":manuscript: ::"
EMPTY_MANUSCRIPT_LOGS = [
    {
        "name": "RSM",
        "level": "LINT",
        "msg": "Manuscript with no title",
        "filename": "linter.py",
    }
]

WRONG_MANUSCRIPT = ":manuscript: * ::"
WRONG_MANUSCRIPT_LOGS = [
    {
        "name": "RSM.parse",
        "level": "WRN",
        "msg": "The CST contains errors.",
        "filename": "tsparser.py",
    },
    {
        "name": "RSM",
        "level": "LINT",
        "msg": "Manuscript with no title",
        "filename": "linter.py",
    },
]


def cmd(src: str, log_format: str, verbose: int = 0):
    args = [
        "rsm-lint",
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
    result = subprocess.run(
        cmd(src, log_format, verbose),
        check=True,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout.decode("utf-8")
    if replace:
        result = re.sub(r"}\s*{", "},{", result)
    if split:
        result = [l.strip() for l in result.strip().split("\n")]
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
