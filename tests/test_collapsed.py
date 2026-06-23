"""The :collapsed: metakey marks a handrailed block to start collapsed.

The collapse is applied by JS on load (a ``data-start-collapsed`` marker), never
baked into the static HTML, so that with scripting off the block renders fully
open and the document stays a complete, readable paper.
"""

import re

import rsm

PROOF = """# T

## S
  {{:label: s}}

Some prose.

:proof:{flag}
  :step: x ::
::
"""


def test_collapsed_emits_marker_on_the_handrail():
    html = rsm.render(PROOF.format(flag=" {:collapsed:}"), handrails=True)
    assert 'data-start-collapsed="true"' in html
    # The marker rides on the proof's own handrail element.
    assert 'class="proof hr' in html


def test_marker_absent_by_default():
    html = rsm.render(PROOF.format(flag=""), handrails=True)
    assert "data-start-collapsed" not in html


def test_collapse_is_subtractive_not_baked_into_html():
    # The static markup must NOT carry hr-collapsed (that would hide the content
    # with JS off). The hr-collapsed class is added by JS on load instead.
    html = rsm.render(PROOF.format(flag=" {:collapsed:}"), handrails=True)
    # id-agnostic: handrail blocks now carry a synthetic id before class.
    m = re.search(r'<div [^>]*class="([^"]*)"[^>]*data-start-collapsed="true"', html)
    assert m is not None
    assert "hr-collapsed" not in m.group(1)
