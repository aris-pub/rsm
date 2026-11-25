"""Each subcommand accepts only the options that change its result.

The tests replace the command handlers, so they check argument parsing only.
"""

import pytest

from rsm import cli

HANDLERS = {
    "build": "_cmd_build",
    "render": "_cmd_render",
    "check": "_cmd_check",
    "parse": "_cmd_parse",
    "export": "_cmd_export",
    "serve": "_cmd_serve",
}

KEPT = {
    "build": [
        ["-c"],
        ["--string"],
        ["--css", "x.css"],
        ["--menu-right"],
        ["-v"],
        ["--verbose"],
        ["--log-no-timestamps"],
        ["--log-no-lineno"],
        ["--log-format", "json"],
        ["--strict"],
        ["--standalone"],
        ["-o", "out"],
        ["-p"],
        ["--no-theme-toggle"],
        ["--sidebar"],
    ],
    "render": [
        ["-c"],
        ["-r"],
        ["--handrails"],
        ["-v"],
        ["--log-no-timestamps"],
        ["--log-no-lineno"],
        ["--log-format", "json"],
        ["--strict"],
        ["-s"],
        ["--sidebar"],
    ],
    "check": [
        ["-c"],
        ["--log-no-timestamps"],
        ["--log-no-lineno"],
        ["--log-format", "json"],
    ],
    "parse": [
        ["-c"],
        ["-v"],
        ["--log-no-timestamps"],
        ["--log-no-lineno"],
        ["--log-format", "json"],
        ["--strict"],
        ["--pretty"],
    ],
    "export": [
        ["-c"],
        ["-v"],
        ["--log-no-timestamps"],
        ["--log-no-lineno"],
        ["--log-format", "json"],
        ["--strict"],
        ["--to", "markdown"],
        ["-o", "out.tex"],
    ],
    "serve": [
        ["-c"],
        ["--css", "x.css"],
        ["--menu-right"],
        ["--standalone"],
        ["-o", "out"],
        ["-p"],
        ["--port", "5600"],
        ["--no-browser"],
        ["--sidebar"],
        ["--no-theme-toggle"],
        ["-v"],
        ["--log-no-timestamps"],
        ["--log-no-lineno"],
        ["--log-format", "json"],
        ["--strict"],
    ],
}

REMOVED = {
    "build": [["-r"], ["--handrails"]],
    "render": [["--css", "x.css"], ["--menu-right"]],
    "check": [
        ["-r"],
        ["--handrails"],
        ["--css", "x.css"],
        ["--menu-right"],
        ["--strict"],
        ["-v"],
        ["--verbose"],
    ],
    "parse": [["-r"], ["--handrails"], ["--css", "x.css"], ["--menu-right"]],
    "export": [["-r"], ["--handrails"], ["--css", "x.css"], ["--menu-right"]],
    "serve": [["-r"], ["--handrails"]],
}


def _parse(monkeypatch, command, option):
    calls = []
    monkeypatch.setattr(cli, HANDLERS[command], lambda args: calls.append(args) or 0)
    monkeypatch.setattr("sys.argv", ["rsm", command, "paper.rsm", *option])
    status = cli.main()
    return status, calls


@pytest.mark.parametrize(
    "command,option",
    [(cmd, opt) for cmd, opts in KEPT.items() for opt in opts],
    ids=lambda v: " ".join(v) if isinstance(v, list) else v,
)
def test_kept_option_is_accepted(monkeypatch, command, option):
    status, calls = _parse(monkeypatch, command, option)
    assert status == 0
    assert len(calls) == 1


@pytest.mark.parametrize(
    "command,option",
    [(cmd, opt) for cmd, opts in REMOVED.items() for opt in opts],
    ids=lambda v: " ".join(v) if isinstance(v, list) else v,
)
def test_removed_option_is_rejected(monkeypatch, capsys, command, option):
    with pytest.raises(SystemExit) as exc:
        _parse(monkeypatch, command, option)
    assert exc.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err
