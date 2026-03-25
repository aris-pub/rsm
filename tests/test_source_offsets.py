"""Tests for source offset attributes replacing inline data-rsm-source."""

import re
from textwrap import dedent

import rsm


def test_no_data_rsm_source_attributes():
    """Handrail elements should NOT have data-rsm-source attributes."""
    src = "This is a test paragraph.\n"
    html = rsm.render(src, handrails=True, add_source=True)
    assert "data-rsm-source=" not in html


def test_source_offset_attributes_present():
    """Handrail elements should have data-source-start and data-source-end."""
    src = "This is a test paragraph.\n"
    html = rsm.render(src, handrails=True, add_source=True)
    assert "data-source-start=" in html
    assert "data-source-end=" in html


def test_source_offsets_are_integers():
    """Source offset attributes should be integer character positions."""
    src = "This is a test paragraph.\n"
    html = rsm.render(src, handrails=True, add_source=True)
    starts = re.findall(r'data-source-start="(\d+)"', html)
    ends = re.findall(r'data-source-end="(\d+)"', html)
    assert len(starts) > 0, "No data-source-start attributes found"
    assert len(ends) > 0, "No data-source-end attributes found"
    for s in starts:
        assert s.isdigit()
    for e in ends:
        assert e.isdigit()


def test_source_offsets_slice_correctly():
    """Slicing the original source with the offsets should produce the block's source."""
    src = dedent("""\
    # My Heading

    This is a paragraph.
    """)
    html = rsm.render(src, handrails=True, add_source=True)

    # Find the paragraph's offsets
    match = re.search(
        r'class="paragraph hr[^"]*"[^>]*data-source-start="(\d+)"[^>]*data-source-end="(\d+)"',
        html,
    )
    assert match, "Paragraph should have source offset attributes"
    start, end = int(match.group(1)), int(match.group(2))
    sliced = src[start:end]
    assert "This is a paragraph." in sliced


def test_source_offsets_on_heading():
    """Heading handrails should have correct source offsets."""
    src = dedent("""\
    ## Section Title

    Content here.
    """)
    html = rsm.render(src, handrails=True, add_source=True)

    match = re.search(
        r'class="heading hr"[^>]*data-source-start="(\d+)"[^>]*data-source-end="(\d+)"',
        html,
    )
    assert match, "Heading should have source offset attributes"
    start, end = int(match.group(1)), int(match.group(2))
    sliced = src[start:end]
    assert "## Section Title" in sliced


def test_rsm_source_div_still_present():
    """The full source div should still be emitted for the JS to slice from."""
    src = "A paragraph.\n"
    html = rsm.render(src, handrails=True, add_source=True)
    assert '<div class="rsm-source hide">' in html


def test_no_source_attrs_when_add_source_false():
    """When add_source=False, no source offsets should be present."""
    src = "A paragraph.\n"
    html = rsm.render(src, handrails=True, add_source=False)
    assert "data-source-start=" not in html
    assert "data-source-end=" not in html
