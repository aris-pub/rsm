import io
import tarfile
import zipfile
from pathlib import Path

import pytest

from rsm.importer import (
    ImporterError,
    find_main_tex,
    flatten,
    resolve_source,
    safe_extract,
)


def _write(p: Path, text: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


# --- resolve_source: input shapes ---


def test_single_tex_file(tmp_path):
    tex = _write(tmp_path / "paper.tex", r"\documentclass{article}" "\nHi\n")
    assert "Hi" in resolve_source(tex)


def test_single_tex_inlines_input(tmp_path):
    _write(tmp_path / "sec.tex", "SECTION BODY")
    main = _write(
        tmp_path / "paper.tex", r"\documentclass{article}" "\n\\input{sec}\nEND"
    )
    out = resolve_source(main)
    assert "SECTION BODY" in out
    assert "\\input{sec}" not in out


def test_folder_with_main_and_include(tmp_path):
    proj = tmp_path / "proj"
    _write(proj / "chapter.tex", "CHAPTER ONE")
    _write(proj / "main.tex", r"\documentclass{book}" "\n\\include{chapter}\n")
    assert "CHAPTER ONE" in resolve_source(proj)


def test_missing_input(tmp_path):
    with pytest.raises(ImporterError):
        resolve_source(tmp_path / "nope.tex")


def test_unsupported_input(tmp_path):
    bad = _write(tmp_path / "notes.md", "# hi")
    with pytest.raises(ImporterError):
        resolve_source(bad)


def test_no_tex_in_folder(tmp_path):
    proj = tmp_path / "proj"
    _write(proj / "readme.txt", "nothing here")
    with pytest.raises(ImporterError):
        resolve_source(proj)


# --- find_main_tex: detection and disambiguation ---


def test_single_documentclass_wins(tmp_path):
    _write(tmp_path / "a.tex", "no class here")
    main = _write(tmp_path / "b.tex", r"\documentclass{article}")
    assert find_main_tex(tmp_path) == main.resolve()


def test_conventional_stem_breaks_tie(tmp_path):
    _write(tmp_path / "intro.tex", r"\documentclass{article}")
    main = _write(tmp_path / "main.tex", r"\documentclass{article}")
    assert find_main_tex(tmp_path) == main.resolve()


def test_ambiguous_mains_error_lists_candidates(tmp_path):
    _write(tmp_path / "one.tex", r"\documentclass{article}")
    _write(tmp_path / "two.tex", r"\documentclass{article}")
    with pytest.raises(ImporterError) as exc:
        find_main_tex(tmp_path)
    assert "one.tex" in str(exc.value) and "two.tex" in str(exc.value)


def test_main_override(tmp_path):
    _write(tmp_path / "main.tex", r"\documentclass{article}")
    chosen = _write(tmp_path / "alt.tex", r"\documentclass{article}")
    assert find_main_tex(tmp_path, override="alt.tex") == chosen.resolve()


def test_main_override_outside_root_refused(tmp_path):
    proj = tmp_path / "proj"
    _write(proj / "main.tex", r"\documentclass{article}")
    _write(tmp_path / "outside.tex", r"\documentclass{article}")
    with pytest.raises(ImporterError):
        find_main_tex(proj, override="../outside.tex")


# --- flatten: containment and cycles ---


def test_flatten_containment(tmp_path):
    proj = tmp_path / "proj"
    main = _write(proj / "main.tex", r"\input{../escape}")
    _write(tmp_path / "escape.tex", "SECRET")
    out = flatten(main, proj)
    assert "SECRET" not in out
    assert "\\input{../escape}" in out


def test_flatten_cycle_terminates(tmp_path):
    a = _write(tmp_path / "a.tex", "A \\input{b}")
    _write(tmp_path / "b.tex", "B \\input{a}")
    out = flatten(a, tmp_path)
    assert "A" in out and "B" in out


# --- safe_extract: archives and guards ---


def test_extract_targz_then_resolve(tmp_path):
    arc = tmp_path / "src.tar.gz"
    with tarfile.open(arc, "w:gz") as tar:
        for name, data in {
            "main.tex": r"\documentclass{article}" "\n\\input{s}",
            "s.tex": "BODY",
        }.items():
            b = data.encode()
            info = tarfile.TarInfo(name)
            info.size = len(b)
            tar.addfile(info, io.BytesIO(b))
    assert "BODY" in resolve_source(arc)


def test_extract_zip_then_resolve(tmp_path):
    arc = tmp_path / "src.zip"
    with zipfile.ZipFile(arc, "w") as zf:
        zf.writestr("main.tex", r"\documentclass{article}" "\n\\input{s}")
        zf.writestr("s.tex", "ZIPBODY")
    assert "ZIPBODY" in resolve_source(arc)


def test_zip_slip_refused(tmp_path):
    arc = tmp_path / "evil.zip"
    with zipfile.ZipFile(arc, "w") as zf:
        zf.writestr("../escape.tex", "PWNED")
    with pytest.raises(ImporterError):
        safe_extract(arc, tmp_path / "out")


def test_zip_symlink_refused(tmp_path):
    arc = tmp_path / "link.zip"
    info = zipfile.ZipInfo("link.tex")
    info.external_attr = 0o120777 << 16  # symlink mode in the unix permission bits
    with zipfile.ZipFile(arc, "w") as zf:
        zf.writestr(info, "/etc/passwd")
    with pytest.raises(ImporterError):
        safe_extract(arc, tmp_path / "out")


def test_tar_traversal_refused(tmp_path):
    arc = tmp_path / "evil.tar.gz"
    with tarfile.open(arc, "w:gz") as tar:
        data = b"PWNED"
        info = tarfile.TarInfo("../escape.tex")
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    with pytest.raises(ImporterError):
        safe_extract(arc, tmp_path / "out")


def test_extract_size_cap(tmp_path, monkeypatch):
    import rsm.importer as imp

    monkeypatch.setattr(imp, "_MAX_EXTRACTED", 4)
    arc = tmp_path / "big.zip"
    with zipfile.ZipFile(arc, "w") as zf:
        zf.writestr("main.tex", "way too much content")
    with pytest.raises(ImporterError):
        safe_extract(arc, tmp_path / "out")


def test_gzip_single_file(tmp_path):
    import gzip

    gz = tmp_path / "paper.tex.gz"
    gz.write_bytes(gzip.compress(b"\\documentclass{article}\nGZIP BODY\n"))
    assert "GZIP BODY" in resolve_source(gz)


def test_preamble_macros_extraction():
    from rsm.importer import preamble_macros

    tex = (
        "\\documentclass{article}\n"
        "\\newcommand{\\RR}{\\mathbb{R}}\n"
        "\\newcommand{\\abs}[1]{\\lvert #1 \\rvert}\n"
        "\\renewcommand{\\vv}[1]{\\mathbf{#1}}\n"
        "\\DeclareMathOperator{\\argmin}{arg\\,min}\n"
        "\\def\\foo{\\bar}\n"
        "\\begin{document}\n"
        "\\newcommand{\\notpicked}{x}\n"
        "\\end{document}\n"
    )
    macros = preamble_macros(tex)
    assert "\\newcommand{\\RR}{\\mathbb{R}}" in macros
    assert "\\newcommand{\\abs}[1]{\\lvert #1 \\rvert}" in macros
    assert "\\renewcommand{\\vv}[1]{\\mathbf{#1}}" in macros
    assert "\\newcommand{\\argmin}{\\operatorname{arg\\,min}}" in macros
    assert "\\def\\foo{\\bar}" in macros
    # definitions after \begin{document} are not in the preamble
    assert not any("notpicked" in m for m in macros)


def test_gzipped_tar(tmp_path):
    arc = tmp_path / "proj.tar.gz"
    with tarfile.open(arc, "w:gz") as tar:
        data = b"\\documentclass{article}\nTARGZ BODY\n"
        info = tarfile.TarInfo("main.tex")
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    assert "TARGZ BODY" in resolve_source(arc)
