"""Every block carries an id so rail/keyboard jumps can navigate by URL hash
(riding the native browser Back button). Labeled blocks keep their semantic id;
unlabeled blocks get a synthetic n<nodeid> id (stable within a built artifact).
"""

import re

import rsm

SRC = """# Title

An unlabeled paragraph.

:theorem: {:label: thm-a}
  A labeled claim.
::
"""


def test_labeled_block_keeps_semantic_id():
    html = rsm.render(SRC, handrails=True, add_source=False)
    assert 'id="thm-a"' in html


def test_unlabeled_block_gets_synthetic_id():
    html = rsm.render(SRC, handrails=True, add_source=False)
    # The unlabeled paragraph block should be hash-addressable via n<nodeid>.
    assert re.search(r'class="paragraph[^"]*"[^>]*id="n\d+"|id="n\d+"[^>]*class="paragraph', html), (
        "expected a synthetic n<nodeid> id on the unlabeled paragraph block"
    )


def test_synthetic_ids_are_unique():
    html = rsm.render(SRC, handrails=True, add_source=False)
    syn = re.findall(r'id="(n\d+)"', html)
    assert len(syn) == len(set(syn)), f"synthetic ids must be unique: {syn}"
