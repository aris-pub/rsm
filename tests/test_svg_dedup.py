"""Tests for SVG icon deduplication via <defs> + <use>."""

import re
from textwrap import dedent

import rsm


def test_svg_defs_block_present():
    """The rendered HTML should contain a single <defs> block with all icon symbols."""
    src = "A paragraph.\n"
    html = rsm.render(src, handrails=True)
    assert '<defs id="hr-icon-defs">' in html
    assert "</defs>" in html


def test_svg_defs_contains_icon_symbols():
    """The <defs> block should contain <symbol> elements for each icon."""
    src = "A paragraph.\n"
    html = rsm.render(src, handrails=True)
    # At minimum, the menu icons should be defined
    assert '<symbol id="hr-icon-link"' in html
    assert '<symbol id="hr-icon-code"' in html
    assert '<symbol id="hr-icon-collapse"' in html
    assert '<symbol id="hr-icon-dots"' in html


def test_icons_use_references():
    """Icon placeholders should use <svg><use href=...> instead of empty spans."""
    src = "A paragraph.\n"
    html = rsm.render(src, handrails=True)
    # Menu items should reference icons via <use>
    assert '<use href="#hr-icon-code"' in html
    assert '<use href="#hr-icon-link"' in html


def test_no_inline_svg_in_icons():
    """Icon elements should not contain full inline SVG paths."""
    src = "A paragraph.\n"
    html = rsm.render(src, handrails=True)
    # The old pattern was <span class="icon code"></span> filled by JS
    # Now it should be <svg ...><use .../></svg>
    # There should be no empty icon spans that need JS filling
    icon_spans = re.findall(r'<span class="icon \w+"></span>', html)
    assert len(icon_spans) == 0, f"Found empty icon spans that need JS: {icon_spans}"


def test_defs_block_emitted_once():
    """Only one <defs> block should exist regardless of paragraph count."""
    src = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph.\n"
    html = rsm.render(src, handrails=True)
    count = html.count('<defs id="hr-icon-defs">')
    assert count == 1, f"Expected 1 defs block, found {count}"
