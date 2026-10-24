"""Locate and extract a LaTeX project's bibliography (bead rsm-ddx.5.4).

pandoc drops the \\bibitem keys and collapses the bibliography, so the keys that
match the in-text \\cite commands are lost. This module recovers them from the
source, outside pandoc, with the precedence .bib, then .bbl, then an inline
thebibliography.

The user's .tex is left untouched. pandoc's own collapsed bibliography is
dropped in the import translator instead (PandocImporter._block_div skips the
Div whose class is "thebibliography").

For a .bib file the entry text is already the bibtex subset RSM accepts, so it
is kept as-is. For a .bbl or inline list the reference is formatted prose, kept
as a key-plus-text pair for later structuring (bead rsm-ddx.5.5).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

from rsm import bibtools

logger = logging.getLogger("RSM").getChild("import")


def sanitize_key(key: str) -> str:
    # A colon is RSM's inline delimiter, so it cannot appear in a cite key or a
    # label. Replace it with a hyphen, the same way on the cite and the bibitem
    # side so the two still match (e.g. DBLP:journals/corr/X -> DBLP-journals/corr/X).
    return key.replace(":", "-")


# Any \cite-family command: \cite, \citep, \citet, \nocite, \autocite, ...
# with an optional star and up to two optional [..] arguments, then {keys}.
_CITE = re.compile(r"\\[a-zA-Z]*cite[a-zA-Z]*\*?\s*(?:\[[^\]]*\]\s*)*\{([^}]+)\}")

# \bibitem, with an optional [label], then {key}.
_BIBITEM = re.compile(r"\\bibitem\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")

_THEBIB = re.compile(
    r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", re.DOTALL
)

# Bibtex control entries that are not references.
_NON_ENTRY = {"comment", "string", "preamble"}

# LaTeX noise a .bbl or thebibliography carries inside a reference line. The
# first group is bare style switches, the second their \text... forms.
_STYLE_SWITCH = re.compile(r"\\(?:newblock|em|it|bf|sc|sl|tt|rm|sf|normalfont|upshape)\b")
_STYLE_WRAP = re.compile(r"\\(?:emph|textit|textbf|textrm|textsc|texttt)\b")


@dataclass(frozen=True)
class Reference:
    """One extracted reference.

    `source` is "bib", "bbl", or "inline". `raw` is the bibtex entry text for a
    .bib source, or the reference prose for a .bbl or inline source.
    """

    key: str
    source: str
    raw: str


def _strip_comments(text: str) -> str:
    """Remove LaTeX line comments (% to end of line), keeping escaped \\%.

    .bbl files, apacite especially, pepper keys and entries with % comments, and
    a commented-out \\cite must not count as a citation.
    """
    return re.sub(r"(?<!\\)%.*", "", text)


def cited_keys(tex: str) -> set[str]:
    """Return the set of keys cited anywhere in the source.

    A \\nocite{*} contributes the literal "*", which callers read as "keep all".
    """
    keys: set[str] = set()
    for match in _CITE.finditer(_strip_comments(tex)):
        for key in match.group(1).split(","):
            key = key.strip()
            if key:
                keys.add(key)
    return keys


def extract_references(tex: str, root: str | Path, cited: set[str]) -> list[Reference]:
    """Extract the cited references, choosing the source by precedence.

    Precedence is .bib, then .bbl, then an inline thebibliography. An empty
    `cited`, or a "*" in it, keeps every entry.
    """
    root = Path(root)
    keep_all = not cited or "*" in cited

    def keep(pairs: list[tuple[str, str]], source: str) -> list[Reference]:
        return [Reference(k, source, t) for k, t in pairs if keep_all or k in cited]

    # Try each source in order and take the first that actually yields cited
    # references. A source can be present but belong to a different paper (a
    # stray .bib in a shared directory, say), so a source that produces nothing
    # falls through to the next rather than ending the search.
    bib = keep(_bib_entries(tex, root), "bib")
    if bib:
        return bib

    bbl_file = _find_bbl(root)
    if bbl_file is not None:
        text = bbl_file.read_text(encoding="utf-8", errors="replace")
        bbl = keep(_parse_bibitems(text), "bbl")
        if bbl:
            return _clean_refs(bbl)

    inline = _THEBIB.search(tex)
    if inline is not None:
        refs = keep(_parse_bibitems(inline.group(0)), "inline")
        if refs:
            return _clean_refs(refs)

    logger.warning("no bibliography (.bib, .bbl, or thebibliography) found")
    return []


def _bib_entries(tex: str, root: Path) -> list[tuple[str, str]]:
    """Parse every entry across the project's .bib files, in file order."""
    entries: list[tuple[str, str]] = []
    for bib in _find_bib_files(tex, root):
        entries.extend(_parse_bibtex(bib.read_text(encoding="utf-8", errors="replace")))
    return entries


def _find_bib_files(tex: str, root: Path) -> list[Path]:
    """The .bib files named by \\bibliography, else every .bib under the root."""
    named: list[Path] = []
    for match in re.finditer(r"\\bibliography\s*\{([^}]*)\}", tex):
        for name in match.group(1).split(","):
            name = name.strip()
            if not name:
                continue
            stem = name[:-4] if name.endswith(".bib") else name
            named.extend(sorted(root.rglob(f"{stem}.bib")))
    if named:
        seen: set[Path] = set()
        unique = []
        for p in named:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        return unique
    return sorted(root.rglob("*.bib"))


def _parse_bibtex(text: str) -> list[tuple[str, str]]:
    """Split bibtex into (key, entry-text) pairs by brace-matching each @entry."""
    entries: list[tuple[str, str]] = []
    i = 0
    while True:
        at = text.find("@", i)
        if at == -1:
            return entries
        m = re.match(r"@([a-zA-Z]+)\s*\{", text[at:])
        if not m:
            i = at + 1
            continue
        kind = m.group(1).lower()
        open_brace = at + m.end() - 1  # index of the "{"
        close = _match_brace(text, open_brace)
        if close == -1:
            return entries
        if kind not in _NON_ENTRY:
            body = text[open_brace + 1 : close]
            key = body.split(",", 1)[0].strip()
            if key:
                entries.append((key, text[at : close + 1]))
        i = close + 1


def _match_brace(text: str, open_idx: int) -> int:
    """Index of the } matching the { at open_idx, or -1 if unbalanced."""
    depth = 0
    for j in range(open_idx, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return j
    return -1


def _find_bbl(root: Path) -> Path | None:
    bbls = sorted(root.rglob("*.bbl"))
    return bbls[0] if bbls else None


def _parse_bibitems(text: str) -> list[tuple[str, str]]:
    """Split \\bibitem blocks into (key, reference-text) pairs.

    Whitespace is collapsed but LaTeX markup is kept here. _clean_refs removes it
    afterwards in one batch.
    """
    items: list[tuple[str, str]] = []
    text = _strip_comments(text)
    matches = list(_BIBITEM.finditer(text))
    for idx, match in enumerate(matches):
        key = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        chunk = text[start:end].split("\\end{thebibliography}", 1)[0]
        ref = " ".join(chunk.split())
        if key:
            items.append((key, ref))
    return items


def _clean_refs(refs: list[Reference]) -> list[Reference]:
    """Clean LaTeX markup out of each reference's text in one batch.

    Prefers the Ruby latex-decode helper (accents, \\url, and the like), and
    falls back to the regex cleanup when it is not available.
    """
    texts = [r.raw for r in refs]
    cleaned = bibtools.decode_latex(texts) or [_clean_latex(t) for t in texts]
    return [Reference(r.key, r.source, c) for r, c in zip(refs, cleaned)]


def _clean_latex(text: str) -> str:
    """Strip the LaTeX markup a reference line carries, leaving plain prose.

    Removes \\newblock and the font-style commands, turns ~ into a space, and
    drops the grouping braces those commands leave behind, so AnyStyle and the
    verbatim fallback both see a clean reference string.
    """
    text = text.replace("~", " ")
    text = _STYLE_SWITCH.sub("", text)
    text = _STYLE_WRAP.sub("", text)
    text = text.replace("{", "").replace("}", "")
    return " ".join(text.split()).strip()
