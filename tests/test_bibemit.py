import shutil

import pytest

import rsm
from rsm import anystyle, bibtools
from rsm.anystyle import StructuredReference
from rsm.bibemit import _emit_structured, references_block


def _bibitem_count(block: str) -> int:
    html = rsm.render("# T\n\n" + block, handrails=False, source_offsets=False)
    return html.count('class="bibitem"')


HAS_ANYSTYLE = shutil.which("anystyle") is not None


def _w(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


# --- field and type mapping (pure) ---


def test_emit_structured_article():
    out = _emit_structured(
        "torres",
        {
            "type": "article-journal",
            "author": [
                {"family": "Torres", "given": "Leo"},
                {"family": "Chan", "given": "Kevin"},
            ],
            "title": ["Nonbacktracking eigenvalues"],
            "container-title": ["SIAM Journal on Mathematics of Data Science"],
            "date": ["2021"],
        },
    )
    assert out.startswith("@article{torres,")
    assert "author={Torres, Leo and Chan, Kevin}" in out
    assert "title={Nonbacktracking eigenvalues}" in out
    assert "journal={SIAM Journal on Mathematics of Data Science}" in out
    assert "year={2021}" in out
    assert out.rstrip().endswith("}")


def test_emit_structured_type_map():
    def kind(csl_type):
        return _emit_structured("k", {"type": csl_type, "title": ["T"]}).split("{")[0]

    assert kind("book") == "@book"
    assert kind("paper-conference") == "@inproceedings"
    assert kind("chapter") == "@incollection"
    assert kind("thesis") == "@phdthesis"
    assert kind("report") == "@techreport"
    assert kind("webpage") == "@webpage"
    assert kind("something-unknown") == "@misc"


def test_emit_year_extracted_from_date():
    out = _emit_structured(
        "k",
        {
            "type": "book",
            "title": ["T"],
            "author": [{"family": "A"}],
            "date": ["2020-05-01"],
        },
    )
    assert "year={2020}" in out


# --- references_block end to end ---


def test_block_bib_passthrough(tmp_path):
    _w(
        tmp_path / "refs.bib",
        "@book{knuth, title={TAOCP}, author={Knuth, D}, year={1968}}",
    )
    block = references_block(r"\cite{knuth} \bibliography{refs}", tmp_path)
    assert block.startswith(":references:")
    assert block.rstrip().endswith("::")
    assert "@book{knuth" in block
    assert "TAOCP" in block


def test_block_structured(monkeypatch, tmp_path):
    def fake_structure(refs):
        return [
            StructuredReference(
                r.key,
                r.raw,
                {
                    "type": "article-journal",
                    "title": ["T"],
                    "author": [{"family": "A"}],
                    "date": ["2021"],
                },
            )
            for r in refs
        ]

    monkeypatch.setattr(anystyle, "structure", fake_structure)
    tex = (
        "\\cite{a}\n"
        "\\begin{thebibliography}{9}\n"
        "\\bibitem{a} A. T. Journal, 2021.\n"
        "\\end{thebibliography}"
    )
    block = references_block(tex, tmp_path)
    assert "@article{a," in block
    assert "year={2021}" in block


def test_block_verbatim_fallback(monkeypatch, tmp_path):
    def fake_structure(refs):
        return [StructuredReference(r.key, r.raw, None) for r in refs]

    monkeypatch.setattr(anystyle, "structure", fake_structure)
    tex = (
        "\\cite{a}\n"
        "\\begin{thebibliography}{9}\n"
        "\\bibitem{a} Some unparseable blob.\n"
        "\\end{thebibliography}"
    )
    block = references_block(tex, tmp_path)
    assert "@misc{a," in block
    assert "verbatim={Some unparseable blob.}" in block


def test_block_empty_when_no_bibliography(tmp_path):
    assert references_block(r"just \cite{x}", tmp_path) == ""


@pytest.mark.skipif(not HAS_ANYSTYLE, reason="anystyle not installed")
def test_block_structured_real_anystyle(tmp_path):
    tex = (
        "\\cite{knuth}\n"
        "\\begin{thebibliography}{9}\n"
        "\\bibitem{knuth} Donald E. Knuth. The Art of Computer Programming. "
        "Addison-Wesley, 1968.\n"
        "\\end{thebibliography}"
    )
    block = references_block(tex, tmp_path)
    assert "knuth" in block
    assert "Knuth" in block


# --- real-world .bib that is not the brace-only subset (regressions) ---


def test_bib_quote_values_render(tmp_path):
    # Quote-delimited values used to be passed through raw and silently dropped.
    (tmp_path / "refs.bib").write_text(
        '@article{k, title = "A Quoted Title", author = "Writer, A.", year = 2001}',
        encoding="utf-8",
    )
    block = references_block(r"\cite{k} \bibliography{refs}", tmp_path)
    assert "title={A Quoted Title}" in block
    assert _bibitem_count(block) == 1


def test_bib_string_macro_renders_without_crash(tmp_path):
    # A @string macro used to crash the renderer (ValueError). It must at least
    # render now, whether or not the macro resolves.
    (tmp_path / "refs.bib").write_text(
        "@string{pub = {Springer}}\n"
        "@book{k, title = {T}, author = {A}, publisher = pub, year = {2001}}",
        encoding="utf-8",
    )
    block = references_block(r"\cite{k} \bibliography{refs}", tmp_path)
    assert _bibitem_count(block) == 1


@pytest.mark.skipif(not shutil.which("ruby"), reason="ruby not installed")
def test_bib_string_macro_resolved_with_ruby(tmp_path):
    if not bibtools.available():
        pytest.skip("bibtex-ruby not available")
    (tmp_path / "refs.bib").write_text(
        "@string{pub = {Springer}}\n"
        "@book{k, title = {T}, author = {A}, publisher = pub, year = {2001}}",
        encoding="utf-8",
    )
    block = references_block(r"\cite{k} \bibliography{refs}", tmp_path)
    assert "publisher={Springer}" in block
