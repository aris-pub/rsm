"""Resolve a LaTeX project to a single flattened .tex source (bead rsm-ddx.5.3).

`rsm import` accepts a .tex file, a project folder, or an archive
(tar/tar.gz/tgz/zip). This module turns any of those into one flattened .tex
string for the pandoc importer: it safely unpacks an archive, finds the main
.tex, and inlines \\input and \\include targets.

The extraction guards are the security boundary. An archive is untrusted input,
so extraction rejects absolute paths, parent-directory traversal, and symlinks,
and caps the total extracted size, so a crafted archive cannot write outside the
scratch directory or exhaust the disk.
"""

from __future__ import annotations

import gzip
import io
import logging
import re
import tarfile
import tempfile
import zipfile
from pathlib import Path

logger = logging.getLogger("RSM").getChild("import")

# Total uncompressed bytes an archive may expand to. The rsmify scratch tmpfs is
# small, and a local import has no reason to be larger.
_MAX_EXTRACTED = 100 * 1024 * 1024

# \input and \include pull another source file into the main document.
_INPUT = re.compile(r"\\(?:input|include)\{([^}]+)\}")

# When several files declare \documentclass, prefer these stems, in this order.
_CONVENTIONAL_STEMS = ("main", "ms", "paper")

_ARCHIVE_SUFFIXES = (".zip", ".tar", ".tgz", ".tar.gz", ".tar.bz2", ".tbz2", ".gz")


class ImporterError(Exception):
    """A project could not be resolved to a main .tex source.

    The message is user-facing. rsmify maps it to an HTTP error page.
    """


def resolve_source(input_path: str | Path, main: str | None = None) -> str:
    """Return the flattened .tex source for a file, folder, or archive."""
    return resolve_project(input_path, main)[0]


def resolve_project(
    input_path: str | Path, main: str | None = None
) -> tuple[str, Path]:
    """Return the flattened .tex source and the project root directory.

    The root is where the other project files live (figures, .bib, .bbl), which
    the bibliography extractor needs. `main` names the main .tex relative to the
    root and overrides auto-detection. For a single .tex file it defaults to
    that file.
    """
    p = Path(input_path)
    if not p.exists():
        raise ImporterError(f"input not found: {input_path}")

    if p.is_dir():
        root = p
    elif is_archive(p):
        root = Path(tempfile.mkdtemp(prefix="rsm-import-"))
        safe_extract(p, root)
    elif p.suffix == ".tex":
        root = p.parent
        if main is None:
            main = p.name
    else:
        raise ImporterError(
            f"unsupported input {input_path!r}: expected a .tex file, a folder, "
            "or a tar/zip archive"
        )

    root = Path(root).resolve()
    main_tex = find_main_tex(root, override=main)
    return flatten(main_tex, root), root


def is_archive(path: Path) -> bool:
    name = path.name.lower()
    return any(name.endswith(suffix) for suffix in _ARCHIVE_SUFFIXES)


def safe_extract(archive: Path, dest: Path) -> None:
    """Unpack a tar or zip archive into dest, refusing unsafe members.

    Detection is by content, not suffix, so a mislabeled archive still unpacks.
    """
    if zipfile.is_zipfile(archive):
        _extract_zip(archive, dest)
    elif tarfile.is_tarfile(archive):
        _extract_tar(archive, dest)
    elif _is_gzip(archive):
        # A single gzipped file, not a tar: an arXiv e-print with one source
        # file arrives this way. Decompress it as the project's main .tex.
        _extract_gzip_member(archive, dest)
    else:
        raise ImporterError(
            f"{archive.name} is not a readable tar, zip, or gzip archive"
        )


def _is_gzip(archive: Path) -> bool:
    with open(archive, "rb") as fh:
        return fh.read(2) == b"\x1f\x8b"


def _extract_gzip_member(archive: Path, dest: Path) -> None:
    with gzip.open(archive, "rb") as gz:
        data = gz.read(_MAX_EXTRACTED + 1)
    if len(data) > _MAX_EXTRACTED:
        raise ImporterError(
            f"{archive.name} expands to an unusually large size, so extraction "
            "was stopped"
        )
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "main.tex").write_bytes(data)


def _extract_tar(archive: Path, dest: Path) -> None:
    with tarfile.open(archive, mode="r:*") as tar:
        members = tar.getmembers()
        if sum(m.size for m in members) > _MAX_EXTRACTED:
            raise ImporterError(
                f"{archive.name} expands to an unusually large size, so extraction "
                "was stopped"
            )
        try:
            # filter="data" rejects absolute paths, parent traversal, and links
            # that point outside dest (CVE-2007-4559).
            tar.extractall(dest, filter="data")
        except tarfile.TarError as exc:
            raise ImporterError(
                f"{archive.name} contains an unsafe or broken member: {exc}"
            ) from exc


def _extract_zip(archive: Path, dest: Path) -> None:
    dest = dest.resolve()
    with zipfile.ZipFile(archive) as zf:
        infos = zf.infolist()
        if sum(info.file_size for info in infos) > _MAX_EXTRACTED:
            raise ImporterError(
                f"{archive.name} expands to an unusually large size, so extraction "
                "was stopped"
            )
        for info in infos:
            name = info.filename
            # A symlink is encoded in the unix mode in the top bits of the
            # external attributes; refuse it rather than follow it.
            mode = info.external_attr >> 16
            if (mode & 0o170000) == 0o120000:
                raise ImporterError(
                    f"{archive.name} contains a symlink ({name}), which is refused"
                )
            target = (dest / name).resolve()
            if not _within(target, dest):
                raise ImporterError(
                    f"{archive.name} contains a member that escapes the output "
                    f"directory ({name}), which is refused"
                )
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as out:
                _copy_capped(src, out, _MAX_EXTRACTED)


def _copy_capped(src: io.BufferedReader, out: io.BufferedWriter, cap: int) -> None:
    """Copy src to out, raising if more than cap bytes are read (zip-bomb guard)."""
    remaining = cap
    while True:
        chunk = src.read(1024 * 1024)
        if not chunk:
            return
        remaining -= len(chunk)
        if remaining < 0:
            raise ImporterError(
                "an archive member expands beyond the size cap, so extraction "
                "was stopped"
            )
        out.write(chunk)


def _within(target: Path, root: Path) -> bool:
    return target == root or target.is_relative_to(root)


def find_main_tex(root: str | Path, override: str | None = None) -> Path:
    """Return the project's main .tex file.

    With `override`, use that file (relative to root, or absolute inside root).
    Otherwise prefer the files declaring \\documentclass: one match wins, several
    are broken by conventional stem (main, ms, paper), and a remaining tie stops
    with an error listing the candidates.
    """
    root = Path(root).resolve()

    if override:
        cand = Path(override)
        cand = cand.resolve() if cand.is_absolute() else (root / cand).resolve()
        if not _within(cand, root):
            raise ImporterError(f"--main {override!r} is outside the project")
        if not cand.exists():
            raise ImporterError(f"--main {override!r} does not exist")
        if cand.suffix != ".tex":
            raise ImporterError(f"--main {override!r} is not a .tex file")
        return cand

    texs = sorted(root.rglob("*.tex"))
    if not texs:
        raise ImporterError("no LaTeX source (.tex) found in the project")

    candidates = [t for t in texs if _declares_documentclass(t)] or texs
    if len(candidates) == 1:
        return candidates[0]

    for stem in _CONVENTIONAL_STEMS:
        named = [c for c in candidates if c.stem.lower() == stem]
        if len(named) == 1:
            logger.info(
                "several files declare documentclass, picked %s by conventional name",
                named[0].relative_to(root),
            )
            return named[0]
        if len(named) > 1:
            break

    listing = ", ".join(str(c.relative_to(root)) for c in candidates)
    raise ImporterError(
        f"several possible main .tex files, pass --main to choose: {listing}"
    )


def _declares_documentclass(tex: Path) -> bool:
    try:
        return "\\documentclass" in tex.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def flatten(main_tex: str | Path, root: str | Path, seen: set[Path] | None = None) -> str:
    """Inline \\input and \\include targets recursively, within root, guarding cycles."""
    seen = set() if seen is None else seen
    path = Path(main_tex).resolve()
    root = Path(root).resolve()
    if path in seen:
        return ""
    seen.add(path)
    base = path.parent
    text = path.read_text(encoding="utf-8", errors="replace")

    def repl(match: re.Match[str]) -> str:
        name = match.group(1).strip()
        child = (base / name).resolve()
        if not child.suffix:
            child = child.with_suffix(".tex")
        # An \input target must stay inside the project, so \input{../../secret}
        # is left as-is rather than inlined.
        if _within(child, root) and child.exists():
            return flatten(child, root, seen)
        return match.group(0)

    return _INPUT.sub(repl, text)


_MACRO_DEF = re.compile(r"\\(newcommand|renewcommand|providecommand|DeclareMathOperator|def)\b")


def preamble_macros(tex: str) -> list[str]:
    """Extract macro definitions from the LaTeX preamble (bead rsm-ddx.2).

    pandoc discards the preamble and expands most macros, but some survive into
    the math, so carrying the definitions lets MathJax expand them. Best-effort:
    handles \\newcommand, \\renewcommand, \\providecommand (keeping argument
    specs), \\DeclareMathOperator (translated to a MathJax-safe \\newcommand with
    \\operatorname), and \\def. Anything trickier is left to the LLM host pass.
    """
    doc = re.search(r"\\begin\{document\}", tex)
    preamble = tex[: doc.start()] if doc else tex
    out: list[str] = []
    for mo in _MACRO_DEF.finditer(preamble):
        kind = mo.group(1)
        j = mo.end()
        star = ""
        if j < len(preamble) and preamble[j] == "*":
            star, j = "*", j + 1
        j = _skip_ws(preamble, j)
        name = _read_macro_name(preamble, j)
        if name is None:
            continue
        macroname, j = name
        j = _skip_ws(preamble, j)
        if kind == "def":
            body = _brace_group(preamble, j)
            if body is not None:
                out.append(f"\\def{macroname}{{{body[0]}}}")
            continue
        if kind == "DeclareMathOperator":
            body = _brace_group(preamble, j)
            if body is not None:
                out.append(
                    f"\\newcommand{{{macroname}}}{{\\operatorname{star}{{{body[0]}}}}}"
                )
            continue
        brackets = ""
        while j < len(preamble) and preamble[j] == "[":
            k = preamble.find("]", j)
            if k == -1:
                break
            brackets += preamble[j : k + 1]
            j = _skip_ws(preamble, k + 1)
        body = _brace_group(preamble, j)
        if body is not None:
            out.append(f"\\{kind}{{{macroname}}}{brackets}{{{body[0]}}}")
    return out


def _read_macro_name(s: str, i: int) -> tuple[str, int] | None:
    """Read a macro name at i: either {\\foo} or \\foo. Return (name, end) or None."""
    if i < len(s) and s[i] == "{":
        g = _brace_group(s, i)
        return (g[0].strip(), g[1]) if g is not None else None
    m = re.match(r"\\[a-zA-Z@]+", s[i:])
    return (m.group(0), i + m.end()) if m else None


def _skip_ws(s: str, i: int) -> int:
    while i < len(s) and s[i] in " \t\r\n":
        i += 1
    return i


def _brace_group(s: str, i: int) -> tuple[str, int] | None:
    """s[i] must be '{'; return (inner content, index after the closing brace)."""
    if i >= len(s) or s[i] != "{":
        return None
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1 : j], j + 1
    return None
