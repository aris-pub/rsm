"""source_offsets and copy_source are independent.

These two behaviours used to be bundled under a single add_source flag:
  - source_offsets stamps data-source-start / data-source-end on elements.
  - copy_source emits the hidden <div class="rsm-source hide"> that the
    copy-source modal reads.
A consumer (RSM Studio) needs the offsets for annotation anchoring but not the
embedded source div, so the two are now separate flags.
"""

import rsm

SRC = "# Heading\n\nA paragraph with *emphasis* and math $x^2$ inside it.\n"

SOURCE_DIV = '<div class="rsm-source hide">'


def test_source_offsets_only_stamps_attributes_without_div():
    html = rsm.render(SRC, handrails=True, source_offsets=True, copy_source=False)
    assert "data-source-start=" in html
    assert "data-source-end=" in html
    assert SOURCE_DIV not in html


def test_copy_source_only_emits_div_without_offsets():
    html = rsm.render(SRC, handrails=True, source_offsets=False, copy_source=True)
    assert SOURCE_DIV in html
    assert "data-source-start=" not in html
    assert "data-source-end=" not in html


def test_both_flags_emit_both():
    html = rsm.render(SRC, handrails=True, source_offsets=True, copy_source=True)
    assert "data-source-start=" in html
    assert SOURCE_DIV in html


def test_render_defaults_emit_neither():
    html = rsm.render(SRC, handrails=True)
    assert "data-source-start=" not in html
    assert SOURCE_DIV not in html
