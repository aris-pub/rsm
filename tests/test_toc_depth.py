""":toc-depth: in the :config: block limits the list of the table of contents.

1 lists sections only, 2 adds subsections, 3 adds subsubsections. Without the
key every level is listed. A value that is not a whole number from 1 to 3 is
logged as an error and every level is listed.
"""

import logging
import re

import pytest

import rsm

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
