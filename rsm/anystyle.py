"""Structure reference prose into fields with AnyStyle (bead rsm-ddx.5.5).

A .bbl or inline reference is formatted prose, not bibtex, so its fields have to
be recovered before RSM can emit a structured entry. AnyStyle is an optional
external command-line tool (a Ruby gem, not a pip dependency), detected on PATH.

When AnyStyle is missing, the parse fails, or the result is below the floor (a
title plus an author or a year), the reference degrades to a verbatim entry and
a warning naming the key is logged. The structured fields follow AnyStyle's
CSL-style shape (author as family/given, title, date, type, container-title),
which bead rsm-ddx.5.6 maps to the RSM field and kind set.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from rsm.bibextract import Reference

logger = logging.getLogger("RSM").getChild("import")

_TIMEOUT = 60


@dataclass
class StructuredReference:
    """A reference after structuring.

    `fields` holds AnyStyle's CSL-style fields when structuring succeeded, and is
    None when the reference degraded to verbatim. `text` is the original prose,
    used for the verbatim entry.
    """

    key: str
    text: str
    fields: dict | None = None

    @property
    def is_verbatim(self) -> bool:
        return self.fields is None


def available() -> bool:
    """True when the AnyStyle command-line tool is on PATH."""
    return shutil.which("anystyle") is not None


def structure(references: list[Reference]) -> list[StructuredReference]:
    """Structure each reference's prose into fields, or degrade to verbatim."""
    if not references:
        return []

    # When AnyStyle is missing or the whole run fails, every reference degrades,
    # so say so once rather than once per key.
    if not available():
        logger.warning(
            "AnyStyle is not installed, keeping %d reference(s) verbatim",
            len(references),
        )
        return [StructuredReference(r.key, r.raw, None) for r in references]

    parsed = _parse([ref.raw for ref in references])
    if parsed is None:
        return [StructuredReference(r.key, r.raw, None) for r in references]

    out: list[StructuredReference] = []
    for ref, fields in zip(references, parsed):
        if _meets_floor(fields):
            out.append(StructuredReference(ref.key, ref.raw, fields))
        else:
            # An individual reference fell below the floor while others parsed,
            # so name it.
            logger.warning(
                "reference %s is below the structuring floor, keeping it verbatim",
                ref.key,
            )
            out.append(StructuredReference(ref.key, ref.raw, None))
    return out


def _meets_floor(fields: dict) -> bool:
    """A structured entry needs a title plus an author or a year."""
    has_title = bool(fields.get("title"))
    has_author_or_year = bool(fields.get("author")) or bool(fields.get("date"))
    return has_title and has_author_or_year


def _parse(texts: list[str]) -> list[dict] | None:
    """Run AnyStyle on the reference lines, one object per line, or None on failure.

    Returns None (so every reference degrades) when AnyStyle is missing, exits
    non-zero, emits unreadable JSON, or returns a different number of entries
    than were sent.
    """
    anystyle = shutil.which("anystyle")
    if anystyle is None:
        return None
    with tempfile.TemporaryDirectory(prefix="rsm-anystyle-") as tmp:
        infile = Path(tmp) / "refs.txt"
        infile.write_text("\n".join(texts) + "\n", encoding="utf-8")
        try:
            proc = subprocess.run(
                [anystyle, "-f", "json", "parse", str(infile)],
                capture_output=True,
                text=True,
                timeout=_TIMEOUT,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            logger.warning(
                "AnyStyle could not be run (%s), keeping references verbatim", exc
            )
            return None
    if proc.returncode != 0:
        logger.warning(
            "AnyStyle exited with %d, keeping references verbatim", proc.returncode
        )
        return None
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError:
        logger.warning(
            "AnyStyle returned unreadable output, keeping references verbatim"
        )
        return None
    if not isinstance(parsed, list) or len(parsed) != len(texts):
        logger.warning(
            "AnyStyle returned %s entries for %d references, keeping them verbatim",
            len(parsed) if isinstance(parsed, list) else "non-list",
            len(texts),
        )
        return None
    return parsed
