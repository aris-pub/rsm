"""The list/graph switch on the table of contents heading line (rsm-ucv)."""

import re
from textwrap import dedent

import pytest

import rsm

LIST_SRC = """\
:toc: ::

## One
  {:label: sec-one}

Text.

## Two

See :ref:sec-one::.
"""

TREE_SRC = LIST_SRC.replace(":toc: ::", ":toc: {\n  :view: tree\n}\n::")


def _switch(html: str) -> str:
    m = re.search(r'<div class="toc-switch".*?</div>', html, re.DOTALL)
    assert m, "no list/graph switch in the table of contents"
    return m.group(0)


def _button(switch: str, view: str) -> str:
    m = re.search(rf'<button[^>]*data-toc-view="{view}"[^>]*>', switch)
    assert m, f"no {view} button in the switch"
    return m.group(0)


@pytest.mark.parametrize("handrails", [True, False])
@pytest.mark.parametrize(
    "src, pressed", [(LIST_SRC, "list"), (TREE_SRC, "tree")], ids=["list", "tree"]
)
def test_switch_buttons_follow_the_author_default(handrails, src, pressed):
    html = rsm.render(src, handrails=handrails, source_offsets=False)
    nav = html[html.index('<nav class="toc') :]
    nav = nav[: nav.index("</nav>")]
    switch = _switch(nav)
    labels = {"list": "Show as list", "tree": "Show as graph"}
    for view, label in labels.items():
        btn = _button(switch, view)
        assert 'type="button"' in btn
        assert f'aria-label="{label}"' in btn
        assert f'title="{label}"' in btn
        want = "true" if view == pressed else "false"
        assert f'aria-pressed="{want}"' in btn


@pytest.mark.parametrize("handrails", [True, False])
def test_switch_sits_on_the_heading_line(handrails):
    html = rsm.render(LIST_SRC, handrails=handrails, source_offsets=False)
    head = re.search(
        r'<div class="toc-head">(.*?)<div class="toc-switch"', html, re.DOTALL
    )
    assert head, "the switch is not in the heading row"
    assert "<h2>Table of Contents</h2>" in head.group(1)


def test_switch_is_not_inside_the_heading():
    # Buttons inside the h2 would add their names to the heading's text.
    html = rsm.render(LIST_SRC, handrails=True, source_offsets=False)
    assert "<h2>Table of Contents</h2>" in html


def _build(tmp_path, src):
    path = tmp_path / "doc.rsm"
    path.write_text(dedent(src))
    rsm.build(
        path=str(path),
        output_dir=str(tmp_path),
        output_filename="doc.html",
        write_output=True,
        handrails=True,
    )
    return (tmp_path / "doc.html").read_text()


def test_prepaint_script_marks_pages_with_the_switch(tmp_path):
    html = _build(tmp_path, LIST_SRC)
    assert "classList.add('has-toc-switch')" in html[: html.index("</head>")]


def test_no_prepaint_script_without_a_toc(tmp_path):
    html = _build(tmp_path, "## One\n\nText.\n")
    assert "has-toc-switch" not in html[: html.index("</head>")]


# ---- the sidebar's Contents view ----

SIDEBAR_SRC = """\
# Title

## One
  {:label: sec-one}

### Sub & more

Text.

## Two {:nonum:}

See :ref:sec-one::.
"""


def _sidebar(src):
    return rsm.render(src, handrails=True, sidebar=True, source_offsets=False)


def _rail_head(html):
    m = re.search(r'<div class="rail-head">(.*?)<p class="rail-hint"', html, re.DOTALL)
    assert m, "no rail head"
    return m.group(1)


def _doc_map(html):
    m = re.search(r'<div class="rail-panel rail-doc-map[^"]*">', html)
    assert m, "no Contents panel"
    return m.group(0)


@pytest.mark.parametrize(
    "src, pressed",
    [
        (SIDEBAR_SRC, "tree"),
        (":toc: ::\n\n" + SIDEBAR_SRC, "list"),
        (":toc: {\n  :view: tree\n}\n::\n\n" + SIDEBAR_SRC, "tree"),
    ],
    ids=["no-toc", "toc-list", "toc-tree"],
)
def test_sidebar_switch_follows_the_author_default(src, pressed):
    html = _sidebar(src)
    head = _rail_head(html)
    assert '<div class="toc-switch rail-toc-switch">' in head
    for view, label in (("list", "Show as list"), ("tree", "Show as graph")):
        btn = _button(head, view)
        assert f'aria-label="{label}"' in btn
        want = "true" if view == pressed else "false"
        assert f'aria-pressed="{want}"' in btn
    panel = _doc_map(html)
    assert (" tree" in panel) == (pressed == "tree")


def _rail_list(html):
    panel = html[html.index('<div class="rail-panel rail-doc-map') :]
    m = re.search(r'<ul class="contents">.*?</ul></div>', panel, re.DOTALL)
    assert m, "no list in the sidebar's Contents panel"
    return m.group(0)


def test_sidebar_list_matches_the_page_list():
    html = _sidebar(":toc: ::\n\n" + SIDEBAR_SRC)
    ul = _rail_list(html)
    links = re.findall(r'<a class="reference" href="([^"]*)">([^<]*)</a>', ul)
    assert links[:2] == [("#sec-one", "1. One"), ("#sec-1.1", "1.1. Sub &amp; more")]
    assert links[2][1] == "Two" and links[2][0].startswith("#sec-")
    assert len(links) == 3
    # The subsection sits in a nested list, as in the page.
    assert re.search(
        r'<ul class="itemize">\s*<li class="item">\s*<a[^>]*href="#sec-1.1"', ul
    )


def test_sidebar_list_built_without_a_toc():
    ul = _rail_list(_sidebar(SIDEBAR_SRC))
    assert '<a class="reference" href="#sec-one">1. One</a>' in ul


def test_contents_view_has_no_hint():
    html = _sidebar(SIDEBAR_SRC)
    btn = re.search(r'<button[^>]*data-view="contents"[^>]*>', html).group(0)
    assert "data-hint" not in btn
