"""Emit an RSM :references: block from extracted references (bead rsm-ddx.5.6).

This ties the bibliography pipeline together: locate and extract the references
(rsm.bibextract), structure the prose ones (rsm.anystyle), then write them as
the RSM bibliography RSM already knows how to render.

A .bib entry is already the bibtex subset RSM accepts, so it is passed through
unchanged. A structured reference is written as an @kind entry with the fields
AnyStyle found. A reference that could not be structured is written as an @misc
entry carrying its original text in the verbatim field.
"""

from __future__ import annotations

import re
from pathlib import Path

from rsm import anystyle, bibtools
from rsm.bibextract import _find_bib_files, cited_keys, extract_references, sanitize_key

# AnyStyle's CSL type to the RSM bibitem kind. Anything else becomes misc.
_RSM_KIND = {
    "article-journal": "article",
    "paper-conference": "inproceedings",
    "chapter": "incollection",
    "thesis": "phdthesis",
    "report": "techreport",
    "book": "book",
    "webpage": "webpage",
}

# RSM bibitem kinds, and the aliases a bibtex entry type might use for a webpage.
_BIB_KINDS = {
    "article", "book", "inproceedings", "conference", "incollection",
    "phdthesis", "mastersthesis", "techreport", "misc", "unpublished", "software",
}
_BIB_KIND_ALIAS = {"online": "webpage", "electronic": "webpage", "www": "webpage"}

# The field keys RSM's bibitem grammar accepts. Any other bibtex field is dropped
# so it cannot produce a parse error.
_RSM_FIELDS = (
    "author", "title", "journal", "booktitle", "publisher", "institution",
    "school", "series", "edition", "volume", "number", "pages", "year", "month",
    "doi", "url", "howpublished", "note", "editor", "address", "organization",
)


def references_block(tex: str, root) -> str:
    """Build the full :references: block for a project, or "" if it has none."""
    refs = extract_references(tex, root, cited_keys(tex))
    if not refs:
        return ""

    # extract_references returns a single source, so all refs share a kind.
    if refs[0].source == "bib":
        entries = _emit_bib(tex, Path(root), refs)
    else:
        structured = {s.key: s for s in anystyle.structure(refs)}
        entries = []
        for ref in refs:
            s = structured[ref.key]
            if s.fields is not None:
                entries.append(_emit_structured(ref.key, s.fields))
            else:
                entries.append(_emit_verbatim(ref.key, s.text))

    return ":references:\n" + "\n\n".join(entries) + "\n::\n"


def _emit_bib(tex: str, root: Path, refs: list) -> list[str]:
    """Emit the cited .bib entries, parsing real bibtex with the Ruby helper.

    A .bib is not the brace-only subset RSM accepts, so the raw entries cannot be
    passed through. bibtex-ruby resolves quotes, bare values, and @string into
    clean fields. Without the helper, a Python best-effort parse pulls the brace-
    and quote-delimited fields, which still never emits anything RSM cannot read.
    """
    parsed = bibtools.parse_bib(_find_bib_files(tex, root))
    by_key = {e["key"]: e for e in parsed} if parsed else {}
    entries: list[str] = []
    for ref in refs:
        entry = by_key.get(ref.key)
        if entry is not None:
            entries.append(_emit_bibtex_fields(entry["type"], ref.key, entry["fields"]))
        else:
            btype, fields = _bib_fields_fallback(ref.raw)
            entries.append(_emit_bibtex_fields(btype, ref.key, fields))
    return entries


def _emit_structured(key: str, fields: dict) -> str:
    kind = _RSM_KIND.get(fields.get("type", ""), "misc")
    pairs: list[tuple[str, str]] = []

    authors = _authors(fields.get("author") or [])
    if authors:
        pairs.append(("author", authors))

    title = _clean(" ".join(fields.get("title") or []))
    if title:
        pairs.append(("title", title))

    container = _clean(" ".join(fields.get("container-title") or []))
    if container:
        if kind == "article":
            pairs.append(("journal", container))
        elif kind in ("inproceedings", "incollection"):
            pairs.append(("booktitle", container))

    publisher = _clean(" ".join(fields.get("publisher") or []))
    if publisher:
        pairs.append(("publisher", publisher))

    year = _year(fields.get("date") or [])
    if year:
        pairs.append(("year", year))

    doi = _clean(" ".join(fields.get("doi") or []))
    if doi:
        pairs.append(("doi", doi))

    url = _clean(" ".join(fields.get("url") or []))
    if url:
        pairs.append(("url", url))

    return _entry(kind, key, pairs)


def _emit_verbatim(key: str, text: str) -> str:
    return _entry("misc", key, [("verbatim", _clean(text))])


def _bibtex_kind(btype: str) -> str:
    btype = (btype or "").lower()
    if btype in _BIB_KINDS:
        return btype
    return _BIB_KIND_ALIAS.get(btype, "misc")


def _emit_bibtex_fields(btype: str, key: str, fields: dict) -> str:
    kind = _bibtex_kind(btype)
    pairs = [
        (name, _clean(str(fields.get(name, "")))) for name in _RSM_FIELDS
    ]
    pairs = [(name, value) for name, value in pairs if value]
    return _entry(kind, key, pairs)


def _bib_fields_fallback(raw: str) -> tuple[str, dict]:
    """Pull brace- or quote-delimited fields from a raw entry, without Ruby.

    Bare and @string values are skipped rather than passed through, so the result
    is always something RSM can read, just less complete.
    """
    m = re.match(r"\s*@(\w+)\s*\{", raw)
    btype = m.group(1).lower() if m else "misc"
    fields: dict = {}
    pattern = re.compile(r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\")")
    for fm in pattern.finditer(raw):
        fields[fm.group(1).lower()] = fm.group(2)[1:-1]
    return btype, fields


def _entry(kind: str, key: str, pairs: list[tuple[str, str]]) -> str:
    lines = [f"@{kind}{{{sanitize_key(key)},"]
    lines += [f"  {field}={{{value}}}," for field, value in pairs]
    lines.append("}")
    return "\n".join(lines)


def _authors(csl_authors: list[dict]) -> str:
    """Format CSL author objects as the bibtex-style "Family, Given and ..." string."""
    names: list[str] = []
    for a in csl_authors:
        if a.get("literal"):
            names.append(_clean(a["literal"]))
            continue
        family = _clean(a.get("family", ""))
        given = _clean(a.get("given", ""))
        if family and given:
            names.append(f"{family}, {given}")
        elif family:
            names.append(family)
        elif given:
            names.append(given)
    return " and ".join(names)


def _year(date_values: list[str]) -> str:
    for value in date_values:
        m = re.search(r"\d{4}", str(value))
        if m:
            return m.group(0)
    return ""


def _clean(value: str) -> str:
    # RSM uses braces to delimit field values, so strip any that would break the
    # entry. Field values from AnyStyle rarely contain them.
    return value.replace("{", "").replace("}", "").strip()
