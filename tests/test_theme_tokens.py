"""Guard for the light-dark() theming migration (rsm-944 / rsm-fv2).

braiid.css used to carry two full color sets: a light set on :root and a dark
set duplicated under .dark-theme. The migration folds each color into a single
light-dark() definition so nothing is duplicated and the dark theme applies from
the OS setting with no JavaScript.

theme_token_baseline.json records every token's pre-migration light and dark
value, captured from the .dark-theme block before conversion. This test asserts
the migration preserved each value exactly and left no duplicated token block,
and it fails if a future edit reintroduces a .dark-theme token override or
changes a paired value by hand.
"""

import json
import re
from pathlib import Path

CSS = Path(__file__).parent.parent / "braiid" / "braiid.css"
BASELINE = json.loads((Path(__file__).parent / "theme_token_baseline.json").read_text())


def _block_vars(lines, start_idx):
    """{var: value} for the brace-matched block whose opening '{' is on
    start_idx. --decls must end with ';' on their own line, which every token
    definition in braiid.css does."""
    depth = 0
    out: dict[str, str] = {}
    started = False
    for i in range(start_idx, len(lines)):
        line = lines[i]
        depth += line.count("{") - line.count("}")
        started = started or "{" in line
        m = re.search(r"(--[\w-]+)\s*:\s*([^;]+);", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
        if started and depth <= 0:
            break
    return out


def _root_and_dark():
    lines = CSS.read_text().splitlines()
    root: dict[str, str] = {}
    dark: dict[str, str] = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.fullmatch(r":root\s*\{", stripped):
            # Merge every bare :root block (later definitions win in the cascade).
            root.update(_block_vars(lines, i))
        elif re.fullmatch(r"\.dark-theme\s*\{", stripped):
            # Only a bare `.dark-theme {` token block, not `.dark-theme .foo {`.
            dark.update(_block_vars(lines, i))
    return root, dark


def _split_light_dark(value: str):
    m = re.fullmatch(r"light-dark\(\s*(.+?)\s*,\s*(.+?)\s*\)", value)
    return (m.group(1), m.group(2)) if m else None


def test_no_duplicated_dark_token_block():
    """The .dark-theme selector must not redefine any theme color token: the
    duplication the migration removes must stay removed."""
    _, dark = _root_and_dark()
    leaked = sorted(k for k in BASELINE if k in dark)
    assert not leaked, f".dark-theme still redefines theme tokens: {leaked}"


def test_every_token_keeps_its_pairing():
    root, _ = _root_and_dark()
    problems = []
    for key, rec in BASELINE.items():
        if key not in root:
            problems.append(f"{key}: missing from :root")
            continue
        value = root[key]
        cat = rec["category"]
        if cat in ("raw-pair", "ref-pair"):
            ld = _split_light_dark(value)
            if ld is None:
                problems.append(f"{key}: expected light-dark(), got {value!r}")
            elif [ld[0], ld[1]] != [rec["light"], rec["dark"]]:
                problems.append(
                    f"{key}: light-dark halves {ld} != baseline "
                    f"({rec['light']!r}, {rec['dark']!r})"
                )
        elif cat == "redundant":
            # Same value in both themes: resolves through its base token, so the
            # dark override is dropped and :root keeps the original reference.
            if value != rec["light"]:
                problems.append(f"{key}: redundant ref changed {value!r} != {rec['light']!r}")
        elif cat == "dark-only":
            # No light counterpart (only consumed in the dark half of another
            # token), so it stays a single plain value on :root.
            if value != rec["dark"]:
                problems.append(f"{key}: dark-only value {value!r} != {rec['dark']!r}")
    assert not problems, "token pairing drifted:\n" + "\n".join(problems)
