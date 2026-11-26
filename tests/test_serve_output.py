"""rsm serve without a file rebuilds each .rsm file into the folder that it serves."""

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


def _serve(monkeypatch, tmp_path, *options):
    server = FakeServer()
    monkeypatch.setattr(cli.livereload, "Server", lambda: server)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["rsm", "serve", "--no-browser", *options])
    assert cli.main() == 0
    return server


@pytest.mark.slow
def test_rebuild_writes_into_served_folder(monkeypatch, tmp_path):
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "paper.rsm").write_text("# Paper\n\nHello.\n")
    server = _serve(monkeypatch, tmp_path, "-o", "out/")

    server.watched["out/paper.rsm"]()

    assert server.root == "out"
    assert (tmp_path / "out" / "paper.html").exists()
    assert not (tmp_path / "paper.html").exists()


@pytest.mark.slow
def test_css_rebuild_writes_into_served_folder(monkeypatch, tmp_path):
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "paper.rsm").write_text("# Paper\n\nHello.\n")
    (tmp_path / "style.css").write_text("body { color: red; }\n")
    server = _serve(monkeypatch, tmp_path, "-o", "out/", "--css", "style.css")

    server.watched["style.css"]()

    assert (tmp_path / "out" / "paper.html").exists()
    assert not (tmp_path / "paper.html").exists()
