from pathlib import Path

from rsm.bibextract import cited_keys, extract_references
from rsm.pandoc import PandocImporter


def _write(p: Path, text: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


# --- cited_keys ---


def test_cited_keys_variants():
    tex = r"""
    Prose \cite{a}, more \citep{b,c}, \citet[see][p.1]{d}, \nocite{e}.
    """
    assert cited_keys(tex) == {"a", "b", "c", "d", "e"}


def test_cited_keys_nocite_star():
    assert "*" in cited_keys(r"\nocite{*}")


def test_cited_keys_none():
    assert cited_keys("no citations here") == set()


# --- inline thebibliography extraction ---


def test_extract_inline(tmp_path):
    tex = r"""
    We cite \cite{knuth} and \cite{torres}.
    \begin{thebibliography}{9}
    \bibitem{knuth} Donald E. Knuth. The Art of Computer Programming. 1968.
    \bibitem{torres} Leo Torres et al. Nonbacktracking eigenvalues. 2021.
    \end{thebibliography}
    """
    refs = extract_references(tex, tmp_path, cited_keys(tex))
    assert [r.key for r in refs] == ["knuth", "torres"]
    assert all(r.source == "inline" for r in refs)
    assert "Art of Computer Programming" in refs[0].raw
    assert "\\bibitem" not in refs[0].raw


def test_extract_inline_cuts_to_cited(tmp_path):
    tex = r"""
    We cite \cite{knuth}.
    \begin{thebibliography}{9}
    \bibitem{knuth} Knuth. 1968.
    \bibitem{uncited} Nobody. 1999.
    \end{thebibliography}
    """
    refs = extract_references(tex, tmp_path, cited_keys(tex))
    assert [r.key for r in refs] == ["knuth"]


# --- .bbl extraction ---


def test_extract_bbl(tmp_path):
    _write(
        tmp_path / "paper.bbl",
        r"""
        \begin{thebibliography}{1}
        \bibitem{smith} J. Smith. A title. Journal, 2020.
        \end{thebibliography}
        """,
    )
    tex = r"We cite \cite{smith}. \bibliography{paper}"
    refs = extract_references(tex, tmp_path, cited_keys(tex))
    assert [r.key for r in refs] == ["smith"]
    assert refs[0].source == "bbl"
    assert "J. Smith" in refs[0].raw


# --- .bib extraction ---


def test_extract_bib_brace_matching(tmp_path):
    _write(
        tmp_path / "refs.bib",
        r"""
        @book{knuth,
          title = {The Art of {Computer} Programming},
          author = {Knuth, Donald E.},
          year = {1968}
        }
        @article{uncited,
          title = {Unused},
          author = {Nobody}
        }
        """,
    )
    tex = r"We cite \cite{knuth}. \bibliography{refs}"
    refs = extract_references(tex, tmp_path, cited_keys(tex))
    assert [r.key for r in refs] == ["knuth"]
    assert refs[0].source == "bib"
    # Nested braces preserved, whole entry kept as-is.
    assert "{Computer}" in refs[0].raw
    assert refs[0].raw.strip().startswith("@book{knuth")


def test_bib_precedence_over_bbl_and_inline(tmp_path):
    _write(tmp_path / "refs.bib", "@book{k, title={From Bib}, author={A}}")
    _write(
        tmp_path / "paper.bbl",
        r"\begin{thebibliography}{1}\bibitem{k} From Bbl.\end{thebibliography}",
    )
    tex = r"\cite{k} \bibliography{refs} \begin{thebibliography}{1}\bibitem{k} Inline.\end{thebibliography}"
    refs = extract_references(tex, tmp_path, cited_keys(tex))
    assert refs[0].source == "bib"
    assert "From Bib" in refs[0].raw


def test_no_bibliography_found(tmp_path):
    refs = extract_references(r"just \cite{x} with no bibliography", tmp_path, {"x"})
    assert refs == []


def test_keep_all_when_no_citations(tmp_path):
    tex = r"""
    \begin{thebibliography}{9}
    \bibitem{a} First.
    \bibitem{b} Second.
    \end{thebibliography}
    """
    refs = extract_references(tex, tmp_path, cited_keys(tex))
    assert {r.key for r in refs} == {"a", "b"}


# --- suppression of pandoc's collapsed bibliography in the import translator ---


def test_importer_drops_thebibliography_div():
    # pandoc wraps a LaTeX bibliography in a Div with this class; the importer
    # must drop it so its collapsed, keyless copy does not reach the RSM output.
    ast = {
        "blocks": [
            {"t": "Para", "c": [{"t": "Str", "c": "Body."}]},
            {
                "t": "Div",
                "c": [
                    ["", ["thebibliography"], []],
                    [{"t": "Para", "c": [{"t": "Str", "c": "Knuth1968collapsed"}]}],
                ],
            },
        ]
    }
    out = PandocImporter().from_json(ast)
    assert "Body." in out
    assert "Knuth1968collapsed" not in out
    assert "thebibliography" not in out


def test_stray_bib_falls_through_to_inline(tmp_path):
    # A .bib exists but has none of the cited keys (it belongs to another paper
    # in a shared directory). The inline bibliography must still be used instead
    # of the search ending at the unrelated .bib.
    _write(tmp_path / "other.bib", "@book{unrelated, title={Other}, author={Z}}")
    tex = r"""
    We cite \cite{knuth}.
    \begin{thebibliography}{9}
    \bibitem{knuth} Knuth. 1968.
    \end{thebibliography}
    """
    refs = extract_references(tex, tmp_path, cited_keys(tex))
    assert [r.key for r in refs] == ["knuth"]
    assert refs[0].source == "inline"


def test_bbl_latex_markup_stripped(tmp_path):
    tex = (
        "\\cite{a}\n"
        "\\begin{thebibliography}{9}\n"
        "\\bibitem{a} \\newblock Y.~Bengio. {\\em Neural networks}. \\newblock IEEE, 1994.\n"
        "\\end{thebibliography}"
    )
    raw = extract_references(tex, tmp_path, cited_keys(tex))[0].raw
    assert "\\newblock" not in raw
    assert "\\em" not in raw
    assert "~" not in raw
    assert "{" not in raw and "}" not in raw
    assert "Y. Bengio" in raw
    assert "Neural networks" in raw


def test_cited_keys_ignores_comments():
    assert cited_keys("% \\cite{ignored}\n\\cite{real}") == {"real"}
    assert cited_keys("100\\% done, see \\cite{x}") == {"x"}


def test_apacite_style_bibitem_key(tmp_path):
    # apacite wraps the key with % line comments: \bibitem[...]{%\nKey}, so the
    # key was coming out as "%\nKey" and never matching the cited key.
    bbl = (
        "\\begin{thebibliography}{}\n"
        "\\bibitem[\\protect\\citeauthoryear{%\nAuthor%\n}{%\nAuthor%\n}{%\n1999}]{%\n"
        "AuthKey}\n"
        "Author, A. A title. 1999.\n"
        "\\end{thebibliography}"
    )
    _write(tmp_path / "p.bbl", bbl)
    refs = extract_references(r"\cite{AuthKey} \bibliography{p}", tmp_path, {"AuthKey"})
    assert [r.key for r in refs] == ["AuthKey"]


def test_key_in_two_bib_files_is_kept_once(tmp_path):
    # Seen in bead rsm-v1yn: the same entry in two .bib files under the root
    # was written twice into :references:.
    _write(tmp_path / "a.bib", "@book{k, title={First}, author={A}}")
    _write(tmp_path / "sub" / "b.bib", "@book{k, title={Second}, author={B}}")
    refs = extract_references(r"\cite{k}", tmp_path, {"k"})
    assert [r.key for r in refs] == ["k"]
    assert "First" in refs[0].raw


def test_bibitem_key_given_twice_is_kept_once(tmp_path):
    tex = (
        r"\cite{k} \begin{thebibliography}{1}\bibitem{k} One. \bibitem{k} Two."
        r"\end{thebibliography}"
    )
    refs = extract_references(tex, tmp_path, cited_keys(tex))
    assert [r.key for r in refs] == ["k"]
