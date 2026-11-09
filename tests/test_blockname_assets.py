""":blockname: on :figure:, :html:, :video: and :table: blocks.

    :html: {
      :blockname: Figure
    }

The caption label reads "Figure 1.1.", a :ref: to it reads "Figure 1.1", and so does
the handrail menu label of its caption. Numbering is unchanged: an :html: block still
shares its counter with figures.
"""

from textwrap import dedent

import pytest

import rsm
import rsm.nodes as nodes
from rsm import app

BODIES = {
    "html": ":html: {{\n  :label: x{meta}\n}}\n\n<div>live</div>\n\n:caption: A caption.\n\n::\n",
    "figure": (
        ":figure: {{\n  :label: x\n  :path: assets/a.png{meta}\n}}\n\n"
        ":caption: A caption.\n\n::\n"
    ),
    "video": (
        ":video: {{\n  :label: x\n  :path: assets/demo.mp4{meta}\n}}\n\n"
        ":caption: A caption.\n\n::\n"
    ),
    "table": (
        ":table: {{\n  :label: x{meta}\n}}\n\n:tbody:\n\n:tr: :td:a:: ::\n\n::\n\n"
        ":caption: A caption.\n\n::\n"
    ),
}

DEFAULT = {"html": "Widget", "figure": "Figure", "video": "Video", "table": "Table"}
# Tables are numbered across the whole manuscript, assets within their section.
NUMBER = {"html": "1.1", "figure": "1.1", "video": "1.1", "table": "1"}
CLASS = {"html": nodes.Html, "figure": nodes.Figure, "video": nodes.Video, "table": nodes.Table}
KINDS = list(BODIES)


def _src(kind: str, name: str = "", extra: str = "") -> str:
    meta = (f"\n  :blockname: {name}" if name else "") + extra
    return "# Doc\n\n## Sec\n\n" + BODIES[kind].format(meta=meta) + "\nSee :ref:x::.\n"


def _node(src: str, cls: type) -> nodes.Node:
    a = app.ProcessorApp(plain=src)
    a.run()
    return next(iter(a.translator.tree.traverse(nodeclass=cls)))


@pytest.mark.parametrize("kind", KINDS)
def test_parses_into_the_node(kind):
    assert _node(_src(kind, "Demo"), CLASS[kind]).blockname == "Demo"


@pytest.mark.parametrize("kind", KINDS)
def test_default_is_empty(kind):
    assert CLASS[kind]().blockname == ""


@pytest.mark.parametrize("kind", KINDS)
def test_kindname(kind):
    assert CLASS[kind]().kindname == DEFAULT[kind]
    assert CLASS[kind](blockname="Demo").kindname == "Demo"


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("handrails", [False, True], ids=["plain", "handrails"])
def test_caption_label(kind, handrails):
    html = rsm.render(_src(kind, "Demo"), handrails=handrails)
    assert f'<span class="label">Demo {NUMBER[kind]}. </span>' in html
    assert f'<span class="label">{DEFAULT[kind]}' not in html


@pytest.mark.parametrize("kind", KINDS)
def test_caption_label_without_number(kind):
    html = rsm.render(_src(kind, "Demo", "\n  :nonum:"))
    assert '<span class="label">Demo. </span>' in html


@pytest.mark.parametrize("kind", KINDS)
def test_reftext(kind):
    assert _node(_src(kind, "Demo"), CLASS[kind]).reftext == f"Demo {NUMBER[kind]}"


@pytest.mark.parametrize("kind", KINDS)
def test_ref_reads_blockname(kind):
    html = rsm.render(_src(kind, "Demo"))
    assert f">Demo {NUMBER[kind]}</a>" in html


@pytest.mark.parametrize("kind", KINDS)
def test_handrail_menu_label(kind):
    html = rsm.render(_src(kind, "Demo"), handrails=True)
    assert 'data-menu-label="Demo"' in html
    assert f'data-menu-label="{DEFAULT[kind]}"' not in html


def test_html_called_figure():
    html = rsm.render(_src("html", "Figure"), handrails=True)
    assert '<span class="label">Figure 1.1. </span>' in html
    assert ">Figure 1.1</a>" in html
    assert 'data-menu-label="Figure"' in html
    assert "Widget" not in html


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("name", ["demo", "dEMO", "Live demo", "FAQ"])
def test_keeps_capitalization(kind, name):
    html = rsm.render(_src(kind, name))
    assert f'<span class="label">{name} {NUMBER[kind]}. </span>' in html
    assert f">{name} {NUMBER[kind]}</a>" in html


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("handrails", [False, True], ids=["plain", "handrails"])
def test_output_without_blockname(kind, handrails):
    html = rsm.render(_src(kind), handrails=handrails)
    word, number = DEFAULT[kind], NUMBER[kind]
    assert f'<span class="label">{word} {number}. </span>' in html
    assert f">{word} {number}</a>" in html
    if handrails:
        assert f'data-menu-label="{word}"' in html


@pytest.mark.parametrize("kind", KINDS)
def test_css_classes_unchanged(kind):
    with_name = rsm.render(_src(kind, "Demo"), handrails=True)
    without = rsm.render(_src(kind), handrails=True)
    assert with_name.replace("Demo", DEFAULT[kind]) == without


def test_numbering_unchanged():
    src = dedent(
        """\
        # Doc

        ## Sec

        :figure: {
          :label: a
          :path: assets/a.png
        }
        ::

        :html: {:label: b, :blockname: Figure}

        <div>live</div>

        ::

        :html: {:label: c}

        <div>live</div>

        ::

        :figure: {
          :label: d
          :path: assets/a.png
          :blockname: Diagram
        }
        ::

        :table: {:label: t1, :blockname: Data}

        :tbody:

        :tr: :td:a:: ::

        ::

        ::

        :table: {:label: t2}

        :tbody:

        :tr: :td:a:: ::

        ::

        ::
        """
    )
    a = app.ProcessorApp(plain=src)
    a.run()
    tree = a.translator.tree
    assets = list(tree.traverse(nodeclass=nodes.Asset))
    tables = list(tree.traverse(nodeclass=nodes.Table))
    assert [n.reftext for n in assets] == [
        "Figure 1.1",
        "Figure 1.2",
        "Widget 1.3",
        "Diagram 1.4",
    ]
    assert [n.reftext for n in tables] == ["Data 1", "Table 2"]
