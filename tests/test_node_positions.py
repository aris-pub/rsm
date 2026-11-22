"""Nodes store source positions as plain (row, column) tuples.

tree-sitter 0.26 rewrote its Point type in C without a way to rebuild it, so
copy.deepcopy and pickle.loads fail on it. RSM deep-copies heading titles for
the table of contents and for references, so a heading with math in it failed
to build with tree-sitter 0.26.
"""

import copy
import pickle

import rsm
from rsm import nodes

SRC = "## The case $k=2$ here\n\nBar.\n"
SRC_TOC = ":toc: ::\n\n## The case $k=2$ here\n\nBar.\n"


def _parse(src: str) -> nodes.Manuscript:
    return rsm.tsparser.TSParser().parse(src)


def test_every_position_is_a_plain_tuple():
    tree = _parse(SRC)
    for node in tree.traverse():
        assert type(node.start_point) is tuple, node
        assert type(node.end_point) is tuple, node


def test_positions_keep_their_values():
    tree = _parse(SRC)
    section = next(tree.traverse(nodeclass=nodes.Section))
    assert section.start_point == (0, 0)
    assert section.end_point[0] >= 0


def test_heading_title_can_be_copied_and_pickled():
    tree = _parse(SRC)
    section = next(tree.traverse(nodeclass=nodes.Section))
    copied = copy.deepcopy(section.title_nodes)
    assert [n.start_point for n in copied] == [
        n.start_point for n in section.title_nodes
    ]
    loaded = pickle.loads(pickle.dumps(section.title_nodes))
    assert [n.start_point for n in loaded] == [
        n.start_point for n in section.title_nodes
    ]


def test_heading_with_math_builds_with_a_toc():
    html = rsm.render(SRC_TOC, handrails=False)
    assert '<ul class="contents"' in html
