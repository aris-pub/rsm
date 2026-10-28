"""Tests for the :orientation: option of the :toc: tree view."""

import logging
import re

import pytest

import rsm
import rsm.nodes as nodes
from rsm import app
from rsm.tsparser import RSMParserError, TSParser

BODY = """
## One
  {:label: s1}

:theorem: {:label: t1} X. ::

## Two
  {:label: s2}

See :ref:t1::.

### Twosub
  {:label: s2a}

Again :ref:s1::.

## Three
  {:label: s3}

Done.
"""


def _src(meta):
    # Block meta takes one key per line.
    lines = "".join(f"  {m.strip()}\n" for m in meta.split(","))
    return f"# My Paper\n\n:toc: {{\n{lines}}}\n::\n" + BODY


def _toc(src):
    a = app.ProcessorApp(plain=src)
    a.run()
    return next(iter(a.translator.tree.traverse(nodeclass=nodes.Contents)))


def _text_toc(html):
    return re.search(r'<nav class="toc[^"]*".*?</nav>', html, re.S).group(0)


def _svgs(fragment):
    return re.findall(r'<svg class="toc-tree[^"]*".*?</svg>', fragment, re.S)


def _edges(svg):
    out = []
    for d in re.findall(r'class="toc-edge [^"]*" d="([^"]+)"', svg):
        nums = [float(v) for v in re.findall(r"-?[\d.]+", d)]
        out.append((nums[0], nums[1], nums[-2], nums[-1]))
    return out


def _root_dot(svg):
    m = re.search(r'<circle class="toc-root-dot" cx="([\d.-]+)" cy="([\d.-]+)"', svg)
    return float(m.group(1)), float(m.group(2))


def test_orientation_parsed():
    assert _toc(_src(":view: tree, :orientation: horizontal")).orientation == "horizontal"
    assert _toc(_src(":view: tree, :orientation: vertical")).orientation == "vertical"


def test_orientation_defaults_to_vertical():
    assert _toc(_src(":view: tree")).orientation == "vertical"
    html = rsm.render(_src(":view: tree"), handrails=False)
    svgs = _svgs(_text_toc(html))
    assert len(svgs) == 1
    assert svgs[0].startswith('<svg class="toc-tree" ')


def test_explicit_vertical_matches_default():
    default = rsm.render(_src(":view: tree"), handrails=False)
    vertical = rsm.render(_src(":view: tree, :orientation: vertical"), handrails=False)
    assert _svgs(_text_toc(default)) == _svgs(_text_toc(vertical))


def test_horizontal_emits_both_layouts_in_the_text():
    # The left-to-right graph is for wide windows. Phones fall back to the
    # vertical one, so both are in the page and CSS shows one of them.
    html = rsm.render(_src(":view: tree, :orientation: horizontal"), handrails=False)
    svgs = _svgs(_text_toc(html))
    assert len(svgs) == 2
    classes = sorted(re.match(r'<svg class="([^"]+)"', s).group(1) for s in svgs)
    assert classes == ["toc-tree toc-tree-h", "toc-tree toc-tree-v"]


def test_horizontal_graph_runs_left_to_right():
    html = rsm.render(_src(":view: tree, :orientation: horizontal"), handrails=False)
    h = next(s for s in _svgs(_text_toc(html)) if "toc-tree-h" in s[:40])
    v = next(s for s in _svgs(_text_toc(html)) if "toc-tree-v" in s[:40])
    # A section and its subsection sit side by side in the horizontal graph and
    # one above the other in the vertical one.
    def pos(svg, idx):
        m = re.search(rf'data-idx="{idx}".*?<rect x="([\d.]+)" y="([\d.]+)"', svg, re.S)
        return float(m.group(1)), float(m.group(2))

    # Rows: One=0, t1 is not a TOC row, Two=1, Twosub=2, Three=3.
    hx2, hy2 = pos(h, 1)
    hx3, hy3 = pos(h, 2)
    assert hx3 != hx2
    vx2, vy2 = pos(v, 1)
    vx3, vy3 = pos(v, 2)
    assert vy3 != vy2
    w = lambda s: float(re.search(r'width="([\d.]+)"', s).group(1))  # noqa: E731
    hgt = lambda s: float(re.search(r'height="([\d.]+)"', s).group(1))  # noqa: E731
    assert w(h) / hgt(h) > w(v) / hgt(v)


def test_horizontal_root_dot_sits_where_edges_meet():
    html = rsm.render(_src(":view: tree, :orientation: horizontal"), handrails=False)
    h = next(s for s in _svgs(_text_toc(html)) if "toc-tree-h" in s[:40])
    root_idx = re.search(r'class="toc-node level-0" data-idx="(\d+)"', h).group(1)
    ends = set()
    for d, f, t in re.findall(
        r'class="toc-edge[^"]*" d="([^"]+)"[^>]*data-from="(\d+)" data-to="(\d+)"', h
    ):
        nums = re.findall(r"-?[\d.]+", d)
        if f == root_idx:
            ends.add((float(nums[0]), float(nums[1])))
        if t == root_idx:
            ends.add((float(nums[-2]), float(nums[-1])))
    assert ends == {_root_dot(h)}
    # The root leads at the left: no node lies to its left.
    xs = [float(x) for x in re.findall(r'<rect x="([\d.-]+)"', h)]
    assert _root_dot(h)[0] <= min(xs)


def test_horizontal_marker_ids_are_unique():
    # A marker referenced from an svg must not resolve to a copy inside a hidden
    # svg, so each copy in the text TOC has its own arrowhead ids.
    html = rsm.render(
        _src(":view: tree, :orientation: horizontal"), handrails=True, sidebar=True
    )
    ids = re.findall(r'<marker id="([^"]+)"', html)
    toc_ids = [i for i in ids if i.startswith("toc-h-") or i.startswith("toc-v-")]
    assert sorted(toc_ids) == [
        "toc-h-arr-dep", "toc-h-arr-fwd", "toc-v-arr-dep", "toc-v-arr-fwd",
    ]
    h, v = (s for s in _svgs(_text_toc(html)))
    for svg in (h, v):
        own = set(re.findall(r'<marker id="([^"]+)"', svg))
        used = set(re.findall(r'marker-end="url\(#([^)]+)\)"', svg))
        assert used and used <= own


def test_sidebar_copy_stays_vertical():
    html = rsm.render(
        _src(":view: tree, :orientation: horizontal"), handrails=True, sidebar=True
    )
    m = re.search(r'<div class="rail-panel rail-doc-map">(.*?)</div>', html, re.S)
    rail = _svgs(m.group(1))
    assert len(rail) == 1
    assert rail[0].startswith('<svg class="toc-tree" ')
    default = rsm.render(_src(":view: tree"), handrails=True, sidebar=True)
    m2 = re.search(r'<div class="rail-panel rail-doc-map">(.*?)</div>', default, re.S)
    assert _svgs(m2.group(1)) == rail


def test_orientation_independent_of_view():
    # :orientation: is kept on a list view too, so switching to the graph from
    # the handrail menu shows the chosen layout.
    html = rsm.render(_src(":orientation: horizontal"), handrails=False)
    nav = _text_toc(html)
    assert nav.startswith('<nav class="toc"')
    assert len(_svgs(nav)) == 2


@pytest.mark.parametrize("bad", ["diagonal", "Horizontal", "left-to-right"])
def test_invalid_orientation_errors(bad):
    with pytest.raises(RSMParserError, match=r"Invalid :toc: orientation value: " + bad):
        TSParser().parse(_src(f":view: tree, :orientation: {bad}"))


def test_invalid_orientation_message_names_the_choices(caplog):
    with pytest.raises(RSMParserError, match="Must be one of: horizontal, vertical"):
        TSParser().parse(_src(":orientation: sideways"))
    # The build stops with the message, as for the other invalid meta values.
    with caplog.at_level(logging.ERROR, logger="RSM"):
        html = rsm.render(_src(":orientation: sideways"), handrails=False)
    assert html == ""
    assert "Invalid :toc: orientation value: sideways" in caplog.text
