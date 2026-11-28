"""A handrail block without a label carries data-hash, a short hash of its own
source text. The reader saves folds under the label of a block, or under this
hash for a block without a label, so that a saved fold stays with its block when
other blocks are added, removed or moved.
"""

import re

import rsm

SRC = """# Title

:theorem:

  An unlabelled claim.

::

:theorem: {:label: thm-a}

  A labelled claim.

::

## A section

Text.
"""


def _hashes(html: str, cls: str) -> list[str]:
    tags = re.findall(rf'<div[^>]*class="{cls}[ "][^>]*>', html)
    return [
        m.group(1) if (m := re.search(r'data-hash="([0-9a-f]+)"', t)) else ""
        for t in tags
    ]


def _render(src: str) -> str:
    return rsm.render(src, handrails=True)


def test_unlabelled_block_has_a_hash():
    html = _render(SRC)
    assert re.fullmatch(r"[0-9a-f]{8}", _hashes(html, "theorem")[0])


def test_labelled_block_has_no_hash():
    html = _render(SRC)
    tag = re.search(r'<div id="thm-a"[^>]*>', html).group(0)
    assert "data-hash" not in tag


def test_unlabelled_section_heading_has_a_hash():
    html = _render(SRC)
    assert all(_hashes(html, "heading"))


def test_hash_does_not_depend_on_position():
    moved = SRC.replace("# Title\n", "# Title\n\nA new first paragraph.\n")
    assert _hashes(_render(SRC), "theorem")[0] == _hashes(_render(moved), "theorem")[0]


def test_hash_changes_with_the_block_text():
    edited = SRC.replace("An unlabelled claim.", "An edited claim.")
    assert _hashes(_render(SRC), "theorem")[0] != _hashes(_render(edited), "theorem")[0]


def test_generated_blocks_name_their_type():
    # The notes list and a bibliography made from citations have no source text.
    # A page has only one of each, so the type is enough to find them again.
    src = """# Title

Text.:note:fn:: It cites :cite:knuth::.

:note: {:label: fn} A note. ::

:references:
  @book{knuth, title={Art}, author={Knuth, Donald E}, year={2014}}
::
"""
    html = _render(src)
    assert 'data-block="noteslist"' in html
    assert 'data-block="bibliography"' in html
