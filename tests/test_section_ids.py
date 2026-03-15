"""Tests for automatic section id attributes in HTML output.

Sections without explicit labels should get auto-generated id="sec-{full_number}"
so they are deep-linkable. Sections with explicit labels keep their user-defined id.
"""

import rsm


def _render(src):
    return rsm.render(src.strip(), handrails=False, add_source=False)


def test_unlabeled_section_gets_auto_id():
    html = _render("""
    ## My Section

    Some text.
    """)
    assert 'id="sec-1"' in html


def test_labeled_section_keeps_user_id():
    html = _render("""
    ## My Section
    {:label: my-sec}

    Some text.
    """)
    assert 'id="my-sec"' in html
    assert 'id="sec-1"' not in html


def test_nested_subsection_gets_auto_id():
    html = _render("""
    ## Parent

    Text.

    ### Child

    More text.
    """)
    assert 'id="sec-1"' in html
    assert 'id="sec-1.1"' in html


def test_multiple_sections_get_distinct_ids():
    html = _render("""
    ## First

    Text.

    ## Second

    More text.
    """)
    assert 'id="sec-1"' in html
    assert 'id="sec-2"' in html


def test_labeled_and_unlabeled_siblings():
    html = _render("""
    ## First
    {:label: intro}

    Text.

    ## Second

    More text.
    """)
    assert 'id="intro"' in html
    assert 'id="sec-2"' in html
    assert 'id="sec-1"' not in html


def test_subsubsection_gets_auto_id():
    html = _render("""
    ## A

    Text.

    ### B

    Text.

    #### C

    Text.
    """)
    assert 'id="sec-1"' in html
    assert 'id="sec-1.1"' in html
    assert 'id="sec-1.1.1"' in html


def test_auto_id_appears_on_section_tag():
    """The id should be on the <section> element, not the heading."""
    html = _render("""
    ## Intro

    Text.
    """)
    assert '<section id="sec-1"' in html


def test_unlabeled_section_with_handrails():
    """Auto ids should also work with handrails enabled."""
    html = rsm.render("## Intro\n\nText.\n", handrails=True, add_source=False)
    assert 'id="sec-1"' in html
