"""Tests for the TOC list view: every listed section must be a live link.

The list view of :toc: renders one <a> per section. A section the author did
not label must still be reachable, so its entry links to the section's
generated anchor rather than to "#". A :ref: to a label that does not exist is
a real broken reference and keeps the error style.
"""

import re

import rsm


def _toc_list_anchors(html):
    """Return the <a> tags inside the TOC list <ul class="contents">."""
    ul = re.search(r'<ul[^>]*class="contents".*?</ul>', html, re.DOTALL)
    assert ul, "no TOC list found"
    return re.findall(r"<a [^>]*>[^<]*</a>", ul.group(0))


def _anchor_for(html, text):
    for a in _toc_list_anchors(html):
        if text in a:
            return a
    raise AssertionError(f"no TOC entry containing {text!r}")


def test_nonum_unlabeled_section_links_to_section():
    html = rsm.render(
        ":toc: ::\n\n## Introduction {:nonum:}\n\nHello.\n\n"
        "## Methods {:label: sec-methods}\n\nMore.\n",
        handrails=False,
        source_offsets=False,
    )
    anchor = _anchor_for(html, ">Introduction<")
    href = re.search(r'href="([^"]*)"', anchor).group(1)
    assert href != "#", "unlabeled section TOC entry is a dead link"
    assert href.startswith("#")
    # The link target must actually exist in the document.
    assert f'<section id="{href[1:]}"' in html


def test_numbered_unlabeled_section_links_to_section():
    html = rsm.render(
        ":toc: ::\n\n## First\n\nText.\n\n## Second\n\nMore.\n",
        handrails=False,
        source_offsets=False,
    )
    anchor = _anchor_for(html, "First")
    href = re.search(r'href="([^"]*)"', anchor).group(1)
    assert href == "#sec-1"
    assert '<section id="sec-1"' in html


def test_nonum_unlabeled_section_entry_has_no_error_style():
    html = rsm.render(
        ":toc: ::\n\n## Introduction {:nonum:}\n\nHello.\n",
        handrails=False,
        source_offsets=False,
    )
    anchor = _anchor_for(html, ">Introduction<")
    assert "error" not in anchor


def test_missing_ref_keeps_error_style():
    html = rsm.render(
        ":toc: ::\n\n## Intro {:label: sec-intro}\n\nSee :ref:nope::.\n",
        handrails=False,
        source_offsets=False,
    )
    assert '<span class="error"' in html
    assert '[unknown label "nope"]' in html
