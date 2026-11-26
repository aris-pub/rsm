"""rsm serve without a file watches the .rsm files of the current folder and
rebuilds each one into the -o folder, which it serves."""

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


def _serve(monkeypatch, folder, *options):
    server = FakeServer()
    monkeypatch.setattr(cli.livereload, "Server", lambda: server)
    monkeypatch.chdir(folder)
    monkeypatch.setattr("sys.argv", ["rsm", "serve", "--no-browser", *options])
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


def test_watches_rsm_files_of_current_folder(monkeypatch, folder):
    (folder / "out dir" / "old.rsm").write_text("# Old\n\nHello.\n")
    _record_shell(monkeypatch)
    server = _serve(monkeypatch, folder, "-o", "out dir/")

    assert "my paper.rsm" in server.watched
    assert not any("old.rsm" in path for path in server.watched)
    assert server.root == "out dir"


def test_rebuild_command_keeps_paths_with_spaces(monkeypatch, folder):
    commands = _record_shell(monkeypatch)
    server = _serve(monkeypatch, folder, "-o", "out dir/")

    server.watched["my paper.rsm"]()

    assert commands == [
        ["rsm", "build", "my paper.rsm", "-o", "out dir/my paper"],
    ]


def test_css_rebuild_command_keeps_paths_with_spaces(monkeypatch, folder):
    (folder / "my style.css").write_text("body { color: red; }\n")
    commands = _record_shell(monkeypatch)
    server = _serve(monkeypatch, folder, "-o", "out dir/", "--css", "my style.css")

    server.watched["my style.css"]()

    assert commands == [
        [
            "rsm",
            "build",
            "my paper.rsm",
            "-o",
            "out dir/my paper",
            "--css",
            "my style.css",
        ],
    ]


def test_rebuild_command_with_file_keeps_paths_with_spaces(monkeypatch, folder):
    commands = _record_shell(monkeypatch)
    server = _serve(monkeypatch, folder, "my paper.rsm", "-o", "out dir/")

    assert server.watched["my paper.rsm"] is not None
    assert commands[0][:5] == ["rsm", "build", "my paper.rsm", "-o", "out dir/"]


@pytest.mark.slow
def test_rebuild_writes_into_served_folder(monkeypatch, folder):
    server = _serve(monkeypatch, folder, "-o", "out dir/")

    server.watched["my paper.rsm"]()

    assert server.root == "out dir"
    assert (folder / "out dir" / "my paper.html").exists()
    assert not (folder / "my paper.html").exists()


@pytest.mark.slow
def test_css_rebuild_writes_into_served_folder(monkeypatch, folder):
    (folder / "my style.css").write_text("body { color: red; }\n")
    server = _serve(monkeypatch, folder, "-o", "out dir/", "--css", "my style.css")

    server.watched["my style.css"]()

    assert (folder / "out dir" / "my paper.html").exists()
    assert not (folder / "my paper.html").exists()
