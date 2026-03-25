"""Tests for RSM source modal functionality — offset-based."""

import re
from textwrap import dedent

import rsm


def test_source_offsets_on_paragraph():
    """Paragraphs should have data-source-start/end, not data-rsm-source."""
    src = "This is a test paragraph.\n"
    html = rsm.render(dedent(src).lstrip(), handrails=True, add_source=True)

    assert "data-rsm-source=" not in html
    match = re.search(
        r'class="paragraph hr[^"]*"[^>]*data-source-start="(\d+)"[^>]*data-source-end="(\d+)"',
        html,
    )
    assert match, "Paragraph should have source offset attributes"
    start, end = int(match.group(1)), int(match.group(2))
    sliced = src[start:end]
    assert "This is a test paragraph." in sliced


def test_source_offsets_on_heading():
    """Headings should have source offset attributes."""
    src = dedent("""\
    # Test Heading

    Some content.
    """)
    html = rsm.render(src, handrails=True, add_source=True)

    match = re.search(
        r'class="heading hr"[^>]*data-source-start="(\d+)"[^>]*data-source-end="(\d+)"',
        html,
    )
    assert match, "Heading should have source offset attributes"
    start, end = int(match.group(1)), int(match.group(2))
    sliced = src[start:end]
    assert "# Test Heading" in sliced


def test_source_offsets_on_section():
    """Section headings should have source offset attributes."""
    src = dedent("""\
    ## Section Title

    Section content.
    """)
    html = rsm.render(src, handrails=True, add_source=True)

    match = re.search(
        r'class="heading hr"[^>]*data-source-start="(\d+)"[^>]*data-source-end="(\d+)"',
        html,
    )
    assert match, "Section should have source offset attributes"
    start, end = int(match.group(1)), int(match.group(2))
    sliced = src[start:end]
    assert "## Section Title" in sliced


def test_tree_button_removed():
    """Tree button should not be present in handrail menu."""
    src = "This is a paragraph.\n"
    html = rsm.render(src, handrails=True, add_source=True)
    assert 'hr-menu-item-text">Tree<' not in html


def test_source_button_present():
    """Source button should be present in handrail menu with SVG use reference."""
    src = "This is a paragraph.\n"
    html = rsm.render(src, handrails=True, add_source=True)
    assert 'hr-menu-item-text">Source<' in html
    assert 'href="#hr-icon-code"' in html


def test_source_offsets_multiline():
    """Multiline source should produce correct offsets."""
    src = dedent("""\
    This is a paragraph
    with multiple lines
    of text.
    """)
    html = rsm.render(src, handrails=True, add_source=True)

    match = re.search(
        r'class="paragraph hr[^"]*"[^>]*data-source-start="(\d+)"[^>]*data-source-end="(\d+)"',
        html,
    )
    assert match, "Paragraph should have source offset attributes"
    start, end = int(match.group(1)), int(match.group(2))
    sliced = src[start:end]
    assert "This is a paragraph" in sliced
    assert "with multiple lines" in sliced
    assert "of text." in sliced


def test_copy_link_still_present():
    """Copy link button should still be present with SVG use reference."""
    src = "This is a paragraph.\n"
    html = rsm.render(src, handrails=True, add_source=True)
    assert 'hr-menu-item-text">Copy link<' in html
    assert 'href="#hr-icon-link"' in html


def test_source_not_on_special_nodes():
    """Special nodes like Draft should not have source attributes."""
    src = dedent("""\
    :draft:
    This is draft content.
    ::
    """)
    html = rsm.render(src, handrails=True, add_source=True)
    assert "data-rsm-source=" not in html
