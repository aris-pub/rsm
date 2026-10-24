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
    # Accent-derived tokens moved from :root onto the [data-accent] carrier
    # (rsm-mwf); the pairing invariant holds across both single-definition homes.
    tokens = {**root, **_bare_data_accent_block()}
    problems = []
    for key, rec in BASELINE.items():
        if key not in tokens:
            problems.append(f"{key}: missing from :root and [data-accent]")
            continue
        value = tokens[key]
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


# --- rsm-2sx: figure caption link contrast must meet WCAG AA in both themes ---

def _hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rel_luminance(hexc):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = _hex_to_rgb(hexc)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def _contrast(h1, h2):
    l1, l2 = _rel_luminance(h1), _rel_luminance(h2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def _split_top_commas(s):
    args, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
            cur += ch
        elif ch == ")":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            args.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        args.append(cur.strip())
    return args


def _resolve(value, theme, tokens, seen=None):
    seen = set() if seen is None else seen
    v = value.strip()
    if v.startswith("#"):
        return v
    m = re.fullmatch(r"light-dark\((.*)\)", v, re.S)
    if m:
        a = _split_top_commas(m.group(1))
        return _resolve(a[0] if theme == "light" else a[1], theme, tokens, seen)
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*(?:,.*)?\)", v, re.S)
    if m:
        name = m.group(1)
        assert name not in seen, f"token cycle at {name}"
        seen.add(name)
        return _resolve(tokens[name], theme, tokens, seen)
    raise AssertionError(f"cannot resolve color value {v!r}")


def _figcaption_background():
    text = CSS.read_text()
    m = re.search(r"figcaption > \.hr-content-zone\s*\{([^}]*)\}", text)
    assert m, "no figcaption > .hr-content-zone rule in braiid.css"
    bg = re.search(r"\bbackground\s*:\s*([^;]+);", m.group(1))
    assert bg, "figcaption content zone has no background"
    return bg.group(1).strip()


def test_caption_link_contrast_meets_wcag_aa():
    """A :ref: link inside a figure caption must clear 4.5:1 against the caption
    surface in both themes (rsm-2sx). Dark mode failed at 4.30:1 on --gray-100."""
    scope = _carrier_scope("blue")
    bg_value = _figcaption_background()
    problems = []
    for theme in ("light", "dark"):
        surface = _resolve(bg_value, theme, scope)
        link = _resolve("var(--link-default)", theme, scope)
        ratio = _contrast(surface, link)
        if ratio < 4.5:
            problems.append(
                f"{theme}: caption link {link} on {surface} is {ratio:.2f}:1 (< 4.5)"
            )
    assert not problems, "; ".join(problems)


# --- rsm-mwf: accent-derived semantic tokens must follow :accent: both themes ---

ACCENTS = ("blue", "purple", "red", "green", "yellow", "orange", "pink", "gray")


def _named_block(selector_regex):
    """{var: value} for the first top-level rule whose selector line matches."""
    lines = CSS.read_text().splitlines()
    for i, line in enumerate(lines):
        if re.fullmatch(selector_regex, line.strip()):
            return _block_vars(lines, i)
    return {}


def _accent_palette(accent):
    return _named_block(rf'\[data-accent="{accent}"\]\s*\{{')


def _bare_data_accent_block():
    """Vars from the bare `[data-accent] {` rule (not `[data-accent="x"]`)."""
    return _named_block(r"\[data-accent\]\s*\{")


def _carrier_scope(accent):
    """Tokens as resolved on the element that carries data-accent: the :root
    defaults, this accent's --primary-* palette, and any semantic tokens moved
    onto the carrier via the bare [data-accent] rule."""
    root, _ = _root_and_dark()
    return {**root, **_accent_palette(accent), **_bare_data_accent_block()}


def _accent_derived(tokens):
    """Transitive closure of token names whose value reaches a --primary-* ref."""
    derived = set()
    changed = True
    while changed:
        changed = False
        for name, value in tokens.items():
            if name in derived:
                continue
            refs = set(re.findall(r"var\(\s*(--[\w-]+)", value))
            if any(r.startswith("--primary-") for r in refs) or (refs & derived):
                derived.add(name)
                changed = True
    return derived


def _computed_on_carrier(token, accent, theme):
    """Computed value of a semantic token on the data-accent carrier. A token
    declared on the carrier (bare [data-accent]) resolves --primary-* there (the
    accent). A token declared only on :root was already computed at :root, where
    --primary-* is always blue, and the carrier only inherits that value."""
    root, _ = _root_and_dark()
    bare = _bare_data_accent_block()
    if token in bare:
        return _resolve(f"var({token})", theme, _carrier_scope(accent))
    return _resolve(f"var({token})", theme, root)


def _accent_primary(accent, level, theme):
    root, _ = _root_and_dark()
    return _resolve(_accent_palette(accent)[f"--primary-{level}"], theme, root)


def test_accent_changes_link_color_in_both_themes():
    """A :ref: link on an element carrying data-accent must take that accent's
    --primary-700, not the blue default (rsm-mwf)."""
    problems = []
    for accent in ACCENTS:
        for theme in ("light", "dark"):
            got = _computed_on_carrier("--link-default", accent, theme)
            want = _accent_primary(accent, 700, theme)
            if got != want:
                problems.append(f"{accent}/{theme}: link {got} != --primary-700 {want}")
    assert not problems, "accent not applied to links:\n" + "\n".join(problems)


def test_accent_changes_keyword_color_in_both_themes():
    """Proof keywords (SUFFICES/ASSUME/QED) use --text-keyword, which is
    --primary-700 in light and --primary-600 in dark; both must follow the
    accent (rsm-mwf)."""
    problems = []
    for accent in ACCENTS:
        for theme, level in (("light", 700), ("dark", 600)):
            got = _computed_on_carrier("--text-keyword", accent, theme)
            want = _accent_primary(accent, level, theme)
            if got != want:
                problems.append(
                    f"{accent}/{theme}: keyword {got} != --primary-{level} {want}"
                )
    assert not problems, "accent not applied to keywords:\n" + "\n".join(problems)


def test_no_accent_derived_token_stranded_on_root():
    """A token that reaches --primary-* must not live on :root, where --primary-*
    is always blue; it belongs on the [data-accent] carrier so it recomputes per
    accent. Covers the transitive case too (--handrail-active via --border-action).
    """
    root, _ = _root_and_dark()
    bare = _bare_data_accent_block()
    derived = _accent_derived({**root, **bare})
    stranded = sorted(k for k in derived if k in root and k not in bare)
    assert not stranded, f"accent-derived tokens still on :root (render blue): {stranded}"
