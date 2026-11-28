"""rsm serve builds one source file and rebuilds it with the same rsm that
started serve."""

import pytest

from rsm import cli


class FakeServer:
    def __init__(self):
        self.watched = {}
        self.root = None

    def watch(self, path, func=None):
        self.watched[path] = func

    def serve(self, root, **kwargs):
        self.root = root


def _serve(monkeypatch, folder, *options, argv0="rsm"):
    server = FakeServer()
    monkeypatch.setattr(cli.livereload, "Server", lambda: server)
    monkeypatch.chdir(folder)
    monkeypatch.setattr("sys.argv", [argv0, "serve", "--no-browser", *options])
    assert cli.main() == 0
    return server


def _record_shell(monkeypatch):
    commands = []

    def fake_shell(cmd, **kwargs):
        commands.append(cmd)
        return lambda: None

    monkeypatch.setattr(cli.livereload, "shell", fake_shell)
    return commands


@pytest.fixture
def folder(tmp_path):
    # Spaces in both names check that the rebuild does not split the paths.
    folder = tmp_path / "my folder"
    folder.mkdir()
    (folder / "out dir").mkdir()
    (folder / "my paper.rsm").write_text("# Paper\n\nHello.\n")
    return folder


def test_serve_without_file_is_an_error(monkeypatch, capsys, folder):
    monkeypatch.setattr(cli.livereload, "Server", FakeServer)
    monkeypatch.chdir(folder)
    monkeypatch.setattr("sys.argv", ["rsm", "serve", "--no-browser"])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2
    assert "the following arguments are required: src" in capsys.readouterr().err


def test_rebuild_command_with_file_keeps_paths_with_spaces(monkeypatch, folder):
    commands = _record_shell(monkeypatch)
    server = _serve(monkeypatch, folder, "my paper.rsm", "-o", "out dir/")

    assert server.watched["my paper.rsm"] is not None
    assert commands[0][1:5] == ["build", "my paper.rsm", "-o", "out dir/"]


def test_rebuild_uses_the_rsm_that_started_serve(monkeypatch, folder):
    commands = _record_shell(monkeypatch)
    argv0 = "/some venv/bin/rsm"
    _serve(monkeypatch, folder, "my paper.rsm", "-o", "out dir/", argv0=argv0)

    assert commands[0][0] == argv0


def test_css_rebuild_uses_the_rsm_that_started_serve(monkeypatch, folder):
    (folder / "my style.css").write_text("body { color: red; }\n")
    commands = _record_shell(monkeypatch)
    argv0 = "/some venv/bin/rsm"
    server = _serve(
        monkeypatch, folder, "my paper.rsm", "--css", "my style.css", argv0=argv0
    )

    assert "my style.css" in server.watched
    assert all(cmd[0] == argv0 for cmd in commands)


def test_serve_creates_missing_output_folder(monkeypatch, folder):
    server = _serve(monkeypatch, folder, "my paper.rsm", "-o", "new out/")

    assert server.root == "new out"
    assert (folder / "new out" / "my paper.html").exists()
