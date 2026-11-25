""":toc-depth: in the :config: block limits the table of contents.

1 shows sections only, 2 adds subsections, 3 adds subsubsections, in the list
and in the graph. Without the key every level is shown. An arrow of the graph
that starts or ends at a hidden section is moved to its nearest visible
ancestor section. The sidebar keeps every level. A value that is not a whole
number from 1 to 3 is logged as an error and every level is shown.
"""

import logging
import re

import pytest

import rsm
import rsm.nodes as nodes
from rsm import app

ALL = ["#sec-1", "#sec-1.1", "#sec-1.1.1", "#sec-1.2", "#sec-2", "#sec-2.1"]


def _src(config="", toc=":toc: ::"):
    head = f":config: {{\n{config}}}\n::\n\n" if config else ""
    return (
        f"# Doc\n\n{head}{toc}\n\n"
        "## One\n\nText.\n\n"
        "### Sub A\n\nText.\n\n"
        "#### Subsub\n\nText.\n\n"
        "### Sub B\n\nText.\n\n"
        "## Two\n\nText.\n\n"
        "### Sub C\n\nText.\n"
    )


def _render(src, **kwargs):
    return rsm.render(src, handrails=False, source_offsets=False, **kwargs)


def _toc_hrefs(html):
    nav = re.search(r'<nav class="toc[^"]*".*?</nav>', html, re.DOTALL)
    assert nav, "no table of contents found"
    return re.findall(r'<a class="reference" href="([^"]*)"', nav.group(0))


@pytest.mark.parametrize(
    "depth, expected",
    [
        (1, ["#sec-1", "#sec-2"]),
        (2, ["#sec-1", "#sec-1.1", "#sec-1.2", "#sec-2", "#sec-2.1"]),
        (3, ALL),
    ],
)
def test_toc_depth_limits_the_levels_listed(depth, expected):
    html = _render(_src(f"  :toc-depth: {depth}\n"))
    assert _toc_hrefs(html) == expected


def test_without_toc_depth_every_level_is_listed():
    assert _toc_hrefs(_render(_src())) == ALL


def test_toc_depth_one_leaves_no_empty_nested_list():
    html = _render(_src("  :toc-depth: 1\n"))
    nav = re.search(r'<nav class="toc[^"]*".*?</nav>', html, re.DOTALL).group(0)
    assert 'class="itemize"' not in nav


@pytest.mark.parametrize(
    "toc",
    [":toc: {:view: tree}\n::", ":toc: {:orientation: horizontal}\n::"],
    ids=["view-tree", "orientation-horizontal"],
)
def test_toc_depth_limits_the_list_whatever_the_view(toc):
    html = _render(_src("  :toc-depth: 2\n", toc=toc))
    assert _toc_hrefs(html) == [
        "#sec-1",
        "#sec-1.1",
        "#sec-1.2",
        "#sec-2",
        "#sec-2.1",
    ]


def test_toc_depth_leaves_the_sidebar_contents_list_alone():
    html = _render(_src("  :toc-depth: 1\n"), sidebar=True)
    rail = re.search(
        r'<div class="rail-panel rail-doc-map.*?(<ul class="contents">.*?)</div>',
        html,
        re.DOTALL,
    )
    assert rail, "no sidebar contents list found"
    assert re.findall(r'href="([^"]*)"', rail.group(1)) == ALL


@pytest.mark.parametrize("bad", ["0", "4", "2.5", "two"])
def test_bad_toc_depth_is_an_error_and_every_level_is_listed(caplog, bad):
    html = _render(_src(f"  :toc-depth: {bad}\n"))
    records = [
        r
        for r in caplog.records
        if r.levelno == logging.ERROR
        and "Invalid value for :toc-depth:" in r.getMessage()
    ]
    assert len(records) == 1, caplog.text
    msg = records[0].getMessage()
    assert bad in msg and "a whole number from 1 to 3" in msg, msg
    assert _toc_hrefs(html) == ALL


# Rows of the full graph, in document order: One=0, One sub=1, Two=2,
# Two sub=3, Two subsub=4, Three=5.
GRAPH_SRC = """:toc: {:view: tree}
::

## One
  {:label: sec-one}

:theorem: {:label: thm-a} Something. ::

### One sub

Back to :ref:sec-one::.

## Two

See :ref:thm-a::.

### Two sub

See :ref:thm-a::.

#### Two subsub
  {:label: sec-twosubsub}

See :ref:sec-three::.

## Three
  {:label: sec-three}

Back to :ref:sec-twosubsub::.
"""

FULL_EDGES = {(1, 0): 1, (2, 0): 1, (3, 0): 1, (4, 5): 1, (5, 4): 1}


def _with_depth(depth):
    return f":config: {{\n  :toc-depth: {depth}\n}}\n::\n\n{GRAPH_SRC}"


def _tree(src):
    a = app.ProcessorApp(plain=src)
    a.run()
    return a.translator.tree


def _graph(src):
    return next(iter(_tree(src).traverse(nodeclass=nodes.Contents)))


def _edges(contents):
    return {(e["src"], e["dst"]): e["count"] for e in contents.toc_edges}


def _kinds(contents):
    return {(e["src"], e["dst"]): e["kind"] for e in contents.toc_edges}


@pytest.mark.parametrize(
    "depth, nums",
    [
        (1, ["1", "2", "3"]),
        (2, ["1", "1.1", "2", "2.1", "3"]),
        (3, ["1", "1.1", "2", "2.1", "2.1.1", "3"]),
    ],
)
def test_toc_depth_limits_the_graph_boxes(depth, nums):
    src = _with_depth(depth)
    assert [n["num"] for n in _graph(src).tree_nodes] == nums
    nav = re.search(r'<nav class="toc[^"]*".*?</nav>', _render(src), re.DOTALL)
    # One box per section plus the root dot.
    assert nav.group(0).count('class="toc-node level-') == len(nums) + 1


def test_without_toc_depth_the_graph_has_every_level():
    graph = _graph(GRAPH_SRC)
    assert len(graph.tree_nodes) == 6
    assert _edges(graph) == FULL_EDGES


def test_toc_depth_two_moves_arrows_to_the_visible_subsection():
    # Rows: One=0, One sub=1, Two=2, Two sub=3, Three=4.
    graph = _graph(_with_depth(2))
    assert _edges(graph) == {(1, 0): 1, (2, 0): 1, (3, 0): 1, (3, 4): 1, (4, 3): 1}
    assert _kinds(graph)[(3, 4)] == "fwd"
    assert _kinds(graph)[(4, 3)] == "dep"


def test_toc_depth_one_merges_and_drops_arrows():
    # Rows: One=0, Two=1, Three=2. The arrow from One sub to One has both ends
    # in One and is dropped. Two to One and Two sub to One merge into one arrow.
    graph = _graph(_with_depth(1))
    assert _edges(graph) == {(1, 0): 2, (1, 2): 1, (2, 1): 1}
    assert _kinds(graph) == {(1, 0): "dep", (1, 2): "fwd", (2, 1): "dep"}


def test_toc_depth_leaves_the_sidebar_graph_alone():
    src = _with_depth(1)
    graph = _tree(src).section_graph
    assert len(graph.tree_nodes) == 6
    assert _edges(graph) == FULL_EDGES
    rail = re.search(
        r'<div class="rail-panel rail-doc-map.*?(<svg.*?</svg>)',
        _render(src, sidebar=True),
        re.DOTALL,
    )
    assert rail, "no sidebar graph found"
    assert rail.group(1).count('class="toc-node level-') == 7
