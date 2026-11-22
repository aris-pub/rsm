"""Optional Ruby-backed bibliography tools (bead rsm-ddx.5.6 follow-up).

Real .bib is not the clean brace-delimited subset RSM's grammar accepts: it uses
quotes, bare values, and @string macros, which otherwise drop entries or crash
the renderer. Rather than widen RSM's grammar, the importer normalizes the .bib
here, and cleans LaTeX markup out of reference text, using the Ruby gems AnyStyle
already installs (bibtex-ruby, latex-decode) through rsm/bibtools.rb.

Everything degrades: when Ruby or the gems are absent, these return None and the
callers fall back to their own best effort.
"""

from __future__ import annotations

import functools
import json
import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger("RSM").getChild("import")

_HELPER = Path(__file__).parent / "bibtools.rb"
_TIMEOUT = 60


@functools.lru_cache(maxsize=1)
def available() -> bool:
    """True when Ruby and the bibtex-ruby and latex-decode gems are usable."""
    if shutil.which("ruby") is None:
        return False
    try:
        proc = subprocess.run(
            ["ruby", "-e", "require 'bibtex'; require 'latex/decode'"],
            capture_output=True,
            timeout=_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0


def parse_bib(paths: list[Path]) -> list[dict] | None:
    """Parse .bib files into [{type, key, fields}], or None if unavailable."""
    if not paths or not available():
        return None
    entries: list[dict] = []
    for path in paths:
        out = _run("bib", str(path))
        if out is None:
            return None
        try:
            entries.extend(json.loads(out))
        except json.JSONDecodeError:
            logger.warning("bibtex-ruby returned unreadable output for %s", path)
            return None
    return entries


def decode_latex(texts: list[str]) -> list[str] | None:
    """Clean LaTeX markup from each line, or None if unavailable.

    Returns a list the same length as the input, aligned to it.
    """
    if not texts or not available():
        return None
    out = _run("decode", stdin="\n".join(texts) + "\n")
    if out is None:
        return None
    lines = out.splitlines()
    if len(lines) != len(texts):
        logger.warning("latex-decode returned a different number of lines")
        return None
    return lines


def _run(*args: str, stdin: str | None = None) -> str | None:
    try:
        proc = subprocess.run(
            ["ruby", str(_HELPER), *args],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        logger.warning("ruby bibtools could not run (%s)", exc)
        return None
    if proc.returncode != 0:
        logger.warning(
            "ruby bibtools exited %d: %s", proc.returncode, proc.stderr[:200]
        )
        return None
    return proc.stdout
