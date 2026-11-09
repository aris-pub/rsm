""":as-paragraph: on :figure:, :html: and :video: blocks.

    :figure: {
      :as-paragraph:
      :path: figs/pappus-images.png
    }
    ::

The asset sits at the level of a paragraph: it takes no number, a caption given to it
is ignored with a warning, and it gets a handrail like a paragraph's, labeled with its
kind name.
"""

import logging
import re
from textwrap import dedent

import pytest

import rsm
import rsm.nodes as nodes
from rsm import app

BODIES = {
    "figure": ":figure: {{\n  :label: x\n  :path: assets/a.png{meta}\n}}\n\n{caption}::\n",
    "html": ":html: {{\n  :label: x{meta}\n}}\n\n<div>live</div>\n\n{caption}::\n",
    "video": ":video: {{\n  :label: x\n  :path: assets/demo.mp4{meta}\n}}\n\n{caption}::\n",
}
CLASS = {"figure": nodes.Figure, "html": nodes.Html, "video": nodes.Video}
KIND = {"figure": "Figure", "html": "Widget", "video": "Video"}
KINDS = list(BODIES)
ASP = "\n  :as-paragraph:"


def _block(kind: str, meta: str = ASP, caption: str = "") -> str:
    caption = f":caption: {caption}\n\n" if caption else ""
    return BODIES[kind].format(meta=meta, caption=caption)


def _src(kind: str, meta: str = ASP, caption: str = "") -> str:
    return "# Doc\n\n## Sec\n\n" + _block(kind, meta, caption) + "\nSee :ref:x::.\n"


def _in_remark(kind: str, meta: str = ASP) -> str:
    body = "\n".join(
        ("  " + line) if line else "" for line in _block(kind, meta).splitlines()
    )
    return (
        "# Doc\n\n## Sec\n\n:remark:\n\n  Some text.\n\n" + body + "\n\n::\n"
    )


def _tree(src: str) -> nodes.Manuscript:
    a = app.ProcessorApp(plain=src)
    a.run()
    return a.translator.tree


def _node(src: str, cls: type) -> nodes.Node:
    return next(iter(_tree(src).traverse(nodeclass=cls)))


def _open_tag(html: str, nodeid_class: str) -> str:
    """The opening tag of the <figure> whose class list starts with nodeid_class."""
    match = re.search(rf'<figure[^>]*class="{nodeid_class}[^"]*"[^>]*>', html)
    assert match, html
    return match.group(0)


@pytest.mark.parametrize("kind", KINDS)
def test_parses_into_the_node(kind):
    assert _node(_src(kind), CLASS[kind]).as_paragraph is True


@pytest.mark.parametrize("kind", KINDS)
def test_default_is_false(kind):
    assert CLASS[kind]().as_paragraph is False
    assert _node(_src(kind, meta=""), CLASS[kind]).as_paragraph is False


@pytest.mark.parametrize("kind", KINDS)
def test_is_a_meta_key(kind):
    assert "as_paragraph" in CLASS[kind].metakeys()


@pytest.mark.parametrize("kind", KINDS)
def test_no_number(kind):
    node = _node(_src(kind), CLASS[kind])
    assert node.number is None
    assert node.reftext == KIND[kind]
    html = rsm.render(_src(kind), handrails=True)
    assert "data-number=" not in _open_tag(html, kind)


@pytest.mark.parametrize("kind", KINDS)
def test_counter_unaffected(kind):
    """The next numbered asset of the same counter is numbered as if the
    as-paragraph one were not there."""
    src = dedent(
        """\
        # Doc

        ## Sec

        """
    ) + _block(kind).replace(":label: x", ":label: p") + "\n" + _block(
        kind, meta=""
    ).replace(":label: x", ":label: n") + "\n"
    tree = _tree(src)
    first, second = list(tree.traverse(nodeclass=CLASS[kind]))
    assert first.number is None
    assert second.number == 1
    assert second.reftext == f"{KIND[kind]} 1.1"


def test_shared_counter_unaffected():
    """Html shares the figure counter; an as-paragraph widget does not use it."""
    src = dedent(
        """\
        # Doc

        ## Sec

        :figure: {
          :label: a
          :path: assets/a.png
        }
        ::

        :html: {
          :label: b
          :as-paragraph:
        }

        <div>live</div>

        ::

        :figure: {
          :label: c
          :path: assets/a.png
        }
        ::
        """
    )
    assets = list(_tree(src).traverse(nodeclass=nodes.Asset))
    assert [n.reftext for n in assets] == ["Figure 1.1", "Widget", "Figure 1.2"]


@pytest.mark.parametrize("kind", KINDS)
def test_caption_ignored_with_warning(kind, caplog):
    with caplog.at_level(logging.WARNING, logger="RSM"):
        html = rsm.render(_src(kind, caption="Not shown."), handrails=True)
        node = _node(_src(kind, caption="Not shown."), CLASS[kind])
    assert "Not shown." not in html
    assert "<figcaption" not in html
    assert not any(isinstance(c, nodes.Caption) for c in node.children)
    assert any(
        "as-paragraph" in r.getMessage() and "caption" in r.getMessage()
        for r in caplog.records
    ), [r.getMessage() for r in caplog.records]


@pytest.mark.parametrize("kind", KINDS)
def test_no_warning_without_caption(kind, caplog):
    with caplog.at_level(logging.WARNING, logger="RSM"):
        rsm.render(_src(kind), handrails=True)
    assert not any("caption" in r.getMessage() for r in caplog.records)


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("handrails", [False, True], ids=["plain", "handrails"])
def test_width_cap_class(kind, handrails):
    html = rsm.render(_src(kind), handrails=handrails)
    assert "as-paragraph" in _open_tag(html, kind).split('class="')[1].split('"')[0]


@pytest.mark.parametrize("kind", KINDS)
def test_paragraph_handrail(kind):
    """The <figure> itself carries a handrail like a paragraph's, with its kind
    name as menu label, and no chromeless body handrail inside it."""
    html = rsm.render(_src(kind), handrails=True)
    tag = _open_tag(html, kind)
    classes = tag.split('class="')[1].split('"')[0].split()
    assert {"hr", "hr-hidden", "as-paragraph"} <= set(classes)
    assert f'data-menu-label="{KIND[kind]}"' in tag
    assert 'data-menu-link="true"' in tag
    assert "tabindex=0" in tag
    figure = html[html.index(tag) : html.index("</figure>", html.index(tag))]
    assert "hr-bare" not in figure
    assert 'class="hr-content-zone"' in figure
    assert 'class="hr-info-zone"' in figure


@pytest.mark.parametrize("kind", KINDS)
def test_menu_label_is_blockname(kind):
    html = rsm.render(_src(kind, meta=ASP + "\n  :blockname: Demo"), handrails=True)
    assert 'data-menu-label="Demo"' in _open_tag(html, kind)


@pytest.mark.parametrize("kind", KINDS)
def test_nested_classes_match_a_paragraph(kind):
    """Inside a theorem-like block the asset's handrail has exactly the classes of
    a paragraph at the same depth (so hr-offset, which keeps it aligned with the
    text around it), plus its own."""
    html = rsm.render(_in_remark(kind), handrails=True)
    para = re.search(r'<div id="n\d+" class="paragraph ([^"]*)"', html).group(1)
    tag = _open_tag(html, kind)
    classes = tag.split('class="')[1].split('"')[0].split()
    assert para.split() == [c for c in classes if c not in {kind, "as-paragraph"}]
    assert "hr-offset" in classes


@pytest.mark.parametrize("kind", KINDS)
def test_label_and_ref(kind):
    html = rsm.render(_src(kind), handrails=True)
    assert 'id="x"' in _open_tag(html, kind)
    assert f'<a class="reference" href="#x">{KIND[kind]}</a>' in html


@pytest.mark.parametrize("kind", KINDS)
def test_ref_with_text(kind):
    src = _src(kind).replace("See :ref:x::.", "See :ref:x,this one::.")
    html = rsm.render(src)
    assert '<a class="reference" href="#x">this one</a>' in html


@pytest.mark.parametrize("kind", KINDS)
def test_reftext_meta(kind):
    node = _node(_src(kind, meta=ASP + "\n  :reftext: Picture"), CLASS[kind])
    assert node.reftext == "Picture"


@pytest.mark.parametrize("kind", KINDS)
def test_keeps_common_meta(kind):
    src = _src(kind, meta=ASP + "\n  :class: {wide, x}\n  :collapsed:")
    html = rsm.render(src, handrails=True)
    tag = _open_tag(html, kind)
    assert "wide" in tag and 'data-start-collapsed="true"' in tag


def test_figure_keeps_asset_meta():
    src = dedent(
        """\
        :figure: {
          :as-paragraph:
          :path: assets/a.png
          :dark: assets/a-dark.png
          :static: assets/a-static.png
          :alt: The chain.
          :scale: 0.2
        }
        ::
        """
    )
    html = rsm.render(src, handrails=True)
    assert 'alt="The chain."' in html
    assert 'onload="this.width*=0.2;"' in html
    assert 'srcset="assets/a-dark.png"' in html
    assert 'class="static-fallback"' in html
    assert 'data-menu-static-toggle="true"' in _open_tag(html, "figure")


def test_html_keeps_static_fallback():
    src = dedent(
        """\
        :html: {
          :as-paragraph:
          :static: assets/w.png
          :alt: A widget.
        }

        <div>live</div>

        ::
        """
    )
    for handrails in (False, True):
        html = rsm.render(src, handrails=handrails)
        tag = _open_tag(html, "html")
        assert 'data-static="assets/w.png"' in tag
        assert 'class="static-fallback"' in html
        assert "<noscript>" in html
        assert "<div>live</div>" in html
    assert 'data-menu-static-toggle="true"' in tag
    # The live body and the fallback share the content zone the static toggle
    # swaps between.
    figure = html[html.index(tag) : html.index("</figure>", html.index(tag))]
    assert figure.count('class="hr-content-zone"') == 1
    zone = figure.split('<div class="hr-content-zone">', 1)[1].split('class="hr-info-zone"')[0]
    assert "<div>live</div>" in zone and 'class="static-fallback"' in zone


def test_html_alt_kept_for_preview():
    src = ":html: {\n  :as-paragraph:\n  :alt: A widget.\n}\n\n<div>live</div>\n\n::\n"
    html = rsm.render(src, handrails=True)
    assert 'data-alt="A widget."' in _open_tag(html, "html")


def test_html_body_has_no_handrail_of_its_own():
    """The widget's body is inside the asset's paragraph handrail, so it does
    not get a second paragraph handrail."""
    html = rsm.render(_src("html"), handrails=True)
    tag = _open_tag(html, "html")
    figure = html[html.index(tag) : html.index("</figure>", html.index(tag))]
    assert figure.count('class="hr-content-zone"') == 1
    assert 'data-menu-label="Paragraph"' not in figure
    assert "<div>live</div>" in figure


@pytest.mark.parametrize("handrails", [False, True], ids=["plain", "handrails"])
def test_video_keeps_controls(handrails):
    html = rsm.render(_src("video"), handrails=handrails)
    assert re.search(r'<video[^>]*controls[^>]*src="assets/demo.mp4"', html)


@pytest.mark.parametrize(
    "parent",
    [
        ":theorem:\n\n{body}\n\n::\n",
        ":proof:\n\n{body}\n\n::\n",
        ":proof:\n\n:step: Claim.\n\n{body}\n\n::\n\n::\n",
        ":section:\n  :title: S\n\n{body}\n\n::\n",
        ":remark: {{\n  :blockname: Hint\n}}\n\n  Text.\n\n{body}\n\n::\n",
    ],
    ids=["theorem", "proof", "step", "section", "remark"],
)
def test_allowed_where_a_paragraph_is(parent):
    body = "\n".join("  " + line for line in _block("figure").splitlines())
    src = "# Doc\n\n" + parent.format(body=body)
    html = rsm.render(src, handrails=True)
    assert "as-paragraph" in _open_tag(html, "figure")


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("handrails", [False, True], ids=["plain", "handrails"])
def test_output_unchanged_without_the_key(kind, handrails):
    html = rsm.render(_src(kind, meta="", caption="A caption."), handrails=handrails)
    assert "as-paragraph" not in html
    assert f'<span class="label">{KIND[kind]} 1.1. </span>' in html
    assert "<figcaption" in html
    if handrails:
        assert 'class="hr hr-bare"' in html
