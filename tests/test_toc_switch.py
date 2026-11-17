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
    nav = html[html.index('<nav class="toc'):]
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
    head = re.search(r'<div class="toc-head">(.*?)<div class="toc-switch"', html, re.DOTALL)
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
