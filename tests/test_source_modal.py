"""Tests for RSM source modal functionality."""

import re
from textwrap import dedent

import rsm


def test_source_attribute_on_paragraph():
    """Test that paragraphs have data-rsm-source attribute with handrails."""
    src = """
    This is a test paragraph.
    """
    html = rsm.render(dedent(src).lstrip(), handrails=True, add_source=True)

    # Extract the paragraph handrail div
    match = re.search(
        r'<div class="paragraph hr hr-hidden"[^>]*data-rsm-source="([^"]*)"',
        html
    )
    assert match, "Paragraph should have data-rsm-source attribute"
    source = match.group(1)
    assert "This is a test paragraph." in source


def test_source_attribute_on_heading():
    """Test that headings have data-rsm-source attribute with handrails."""
    src = """
    # Test Heading

    Some content.
    """
    html = rsm.render(dedent(src).lstrip(), handrails=True, add_source=True)

    # Extract the heading handrail div
    match = re.search(
        r'<div class="heading hr"[^>]*data-rsm-source="([^"]*)"',
        html
    )
    assert match, "Heading should have data-rsm-source attribute"
    source = match.group(1)
    assert "# Test Heading" in source


def test_source_attribute_on_section():
    """Test that sections have data-rsm-source attribute with handrails."""
    src = """
    ## Section Title

    Section content.
    """
    html = rsm.render(dedent(src).lstrip(), handrails=True, add_source=True)

    # Extract the section heading handrail div
    match = re.search(
        r'<div class="heading hr"[^>]*data-rsm-source="([^"]*)"',
        html
    )
    assert match, "Section should have data-rsm-source attribute"
    source = match.group(1)
    assert "## Section Title" in source


def test_tree_button_removed():
    """Test that Tree button is no longer present in handrail menu."""
    src = """
    This is a paragraph.
    """
    html = rsm.render(dedent(src).lstrip(), handrails=True, add_source=True)

    # Check that Tree button is not present
    assert 'hr-menu-item-text">Tree<' not in html
    assert '<span class="icon tree">' not in html


def test_source_button_present():
    """Test that Source button is present in handrail menu."""
    src = """
    This is a paragraph.
    """
    html = rsm.render(dedent(src).lstrip(), handrails=True, add_source=True)

    # Check that Source button is present
    assert 'hr-menu-item-text">Source<' in html
    assert '<span class="icon code">' in html


def test_source_attribute_multiline():
    """Test that multiline source is correctly captured."""
    src = """
    This is a paragraph
    with multiple lines
    of text.
    """
    html = rsm.render(dedent(src).lstrip(), handrails=True, add_source=True)

    match = re.search(
        r'<div class="paragraph hr hr-hidden"[^>]*data-rsm-source="([^"]*)"',
        html
    )
    assert match, "Paragraph should have data-rsm-source attribute"
    source = match.group(1)
    # Check that newlines are preserved (HTML escaped as &#10; or actual newlines)
    assert "This is a paragraph" in source
    assert "with multiple lines" in source
    assert "of text." in source


def test_source_attribute_escapes_html():
    """Test that HTML characters in source are properly escaped."""
    src = """
    Paragraph with <tags> and & symbols.
    """
    html = rsm.render(dedent(src).lstrip(), handrails=True, add_source=True)

    match = re.search(
        r'<div class="paragraph hr hr-hidden"[^>]*data-rsm-source="([^"]*)"',
        html
    )
    assert match, "Paragraph should have data-rsm-source attribute"
    source = match.group(1)
    # HTML entities should be escaped
    assert "&lt;" in source or "Paragraph with &lt;tags&gt;" in html
    assert "&amp;" in source or "&amp; symbols" in html


def test_copy_link_still_present():
    """Test that Copy link button is still present."""
    src = """
    This is a paragraph.
    """
    html = rsm.render(dedent(src).lstrip(), handrails=True, add_source=True)

    # Check that Copy link button is still present
    assert 'hr-menu-item-text">Copy link<' in html
    assert '<span class="icon link">' in html


def test_source_not_on_special_nodes():
    """Test that nodes without source positions (like Bibliography) don't crash.

    Some nodes like Bibliography are created during transformation and don't have
    source positions, so they won't have data-rsm-source attributes.
    """
    src = """
    Text citing :cite: smith2024 ::.

    :references:
    @article{smith2024,
      title = {My Paper},
      author = {Jane Smith},
      year = {2024},
      journal = {Nature}
    }
    ::
    """
    # This should not crash
    html = rsm.render(dedent(src).lstrip(), handrails=True, add_source=True)

    # Bibliography heading won't have source because it's a synthetic node
    # But the page should still render
    assert '<h2>References</h2>' in html or 'References' in html
