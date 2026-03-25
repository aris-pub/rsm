"""Tests for singleton handrail menu architecture."""

import re
from textwrap import dedent

import rsm


def test_no_inline_menu_content():
    """Handrail menu zones should be empty — no inline menu items."""
    src = "A paragraph.\n"
    html = rsm.render(src, handrails=True)
    assert 'class="hr-menu-zone"' in html
    # Menu zones inside handrails should be empty (content only in singleton)
    import re
    zone_contents = re.findall(r'<div class="hr-menu-zone">\s*(.*?)\s*</div>', html, re.DOTALL)
    for content in zone_contents:
        assert content.strip() == "", f"Menu zone should be empty, got: {content[:50]}"


def test_menu_data_attributes_on_handrail():
    """Each handrail should have data-menu-* attributes."""
    src = "A paragraph.\n"
    html = rsm.render(src, handrails=True)
    assert 'data-menu-label=' in html
    assert 'data-menu-link=' in html
    assert 'data-menu-code=' in html


def test_menu_data_attributes_vary_by_type():
    """Different block types should have different menu configs."""
    src = dedent("""\
    :theorem:
      Statement.
    ::

    :proof:
      :step:
        Body.
      ::
    ::
    """)
    html = rsm.render(src, handrails=True)
    # Theorem should have a label
    theorem_match = re.search(r'class="[^"]*theorem[^"]*"[^>]*data-menu-label="Theorem 1"', html)
    assert theorem_match, "Theorem should have data-menu-label"
    # Step inside proof should have collapse
    step_match = re.search(r'class="[^"]*step[^"]*"[^>]*data-menu-collapse', html)
    assert step_match, "Step should have data-menu-collapse"


def test_singleton_menu_template_emitted():
    """A single menu template should exist at the manuscript level."""
    src = "A paragraph.\n"
    html = rsm.render(src, handrails=True)
    assert 'id="hr-menu-singleton"' in html


def test_singleton_menu_has_all_possible_items():
    """The singleton template should contain all possible menu items."""
    src = "A paragraph.\n"
    html = rsm.render(src, handrails=True)
    # Find the singleton
    match = re.search(r'id="hr-menu-singleton"[^>]*>(.+?)</div>\s*</div>', html, re.DOTALL)
    assert match, "Singleton menu should exist"
    menu_html = match.group(1)
    assert "Copy link" in menu_html
    assert "Source" in menu_html
    assert "Collapse" in menu_html
    assert "Collapse all" in menu_html


def test_only_one_menu_instance():
    """Multiple handrails should NOT produce multiple menu instances."""
    src = "First.\n\nSecond.\n\nThird.\n"
    html = rsm.render(src, handrails=True)
    # Count hr-menu divs (should be 0 inside handrails, 1 singleton)
    menu_count = html.count('<div class="hr-menu">')
    assert menu_count == 1, f"Expected 1 menu instance (singleton), found {menu_count}"
