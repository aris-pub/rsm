"""Commands that need a parsed document print nothing on stdout and exit with
code 1 when the source cannot be parsed. The parser logs the error."""

import pytest

from rsm import app, cli

BROKEN = "# Doc\n\n:theorem: {:label: t\n"


def _main(monkeypatch, *argv: str) -> int:
    monkeypatch.setattr("sys.argv", ["rsm", *argv])
    return cli.main()


@pytest.mark.parametrize("command", ["parse", "export"])
def test_command_exits_with_1_on_a_parse_error(monkeypatch, capsys, command):
    assert _main(monkeypatch, command, "-c", BROKEN) == 1
    assert capsys.readouterr().out == ""


def test_parser_app_returns_none_on_a_parse_error():
    assert app.ParserApp(plain=BROKEN).run() is None


def test_render_returns_an_empty_string_on_a_parse_error():
    assert app.render(BROKEN) == ""
