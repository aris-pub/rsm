"""Inline raw HTML, :rawhtml:{:alt: fallback} <html> ::.

The body is written into the HTML page as is, in place. The :alt: (text and
inline math) is the fallback: RSM writes it next to the body, hidden, so that
the copies the page makes of its own content (reference previews, the pinned
excerpt, the proof State view) show the fallback instead of a second live copy
of the raw HTML (tests/interactive/test_rawhtml.py). Everything that reads text
out of the tree sees only the fallback, never the raw markup.
"""

import logging
from textwrap import dedent

import pytest

import rsm
from conftest import compare_have_want
from rsm import nodes
from rsm.app import ParserApp
from rsm.pandoc import PandocTranslator

WIDGET = '<mtp-display model="pappus" name="c0"></mtp-display>'


def _render(src: str, handrails: bool = False) -> str:
    return rsm.render(dedent(src).lstrip(), handrails=handrails, source_offsets=False)


def _tree(src: str) -> nodes.Manuscript:
    return ParserApp(plain=dedent(src).lstrip()).run()


def _raws(tree: nodes.Manuscript) -> list:
    return list(tree.traverse(nodeclass=nodes.RawHtml))


# ── Tree ─────────────────────────────────────────────────────────────────────


def test_body_is_kept_verbatim_and_alt_becomes_children():
    tree = _tree(f"Consider :rawhtml:{{:alt: the circle $C_0$}} {WIDGET} ::, more.\n")
    (raw,) = _raws(tree)
    assert raw.html == WIDGET
    assert raw.alt == "the circle $C_0$"
    text, math = raw.children
    assert isinstance(text, nodes.Text) and text.text == "the circle "
    assert isinstance(math, nodes.Math)
    assert math.children[0].text == "C_0"


def test_body_keeps_newlines_and_rsm_delimiters():
    body = '<span title="a: b">$x$ *y* **z** `w` &amp; \'q\' < > "r"</span>\n<br>'
    tree = _tree(f":rawhtml: {body} ::\n")
    (raw,) = _raws(tree)
    assert raw.html == body
    # Nothing in the body was parsed as RSM.
    assert not raw.children
    assert not list(tree.traverse(nodeclass=nodes.Math))
    assert not list(tree.traverse(nodeclass=nodes.Code))
    assert not list(tree.traverse(nodeclass=nodes.Span))


def test_meta_without_alt_has_no_fallback():
    tree = _tree(":rawhtml:{:label: r1} <b>x</b> ::\n")
    (raw,) = _raws(tree)
    assert raw.label == "r1"
    assert raw.alt == ""
    assert not raw.children


def test_alt_with_unmatched_dollar_is_text():
    (raw,) = _raws(_tree(":rawhtml:{:alt: costs $5} <b>x</b> ::\n"))
    assert [type(c) for c in raw.children] == [nodes.Text]
    assert raw.children[0].text == "costs $5"


def test_to_dict_carries_the_body_and_the_alt():
    (raw,) = _raws(_tree(":rawhtml:{:alt: a dial} <x-dial></x-dial> ::\n"))
    d = raw.to_dict()
    assert d["nodeclass"] == "RawHtml"
    assert d["html"] == "<x-dial></x-dial>"
    assert d["alt"] == "a dial"


@pytest.mark.parametrize(
    "src",
    [
        ":span: a :rawhtml: <i>x</i> :: b ::\n",
        "**a :rawhtml: <i>x</i> :: b**\n",
        "*a :rawhtml: <i>x</i> :: b*\n",
        ":theorem:\n  A :rawhtml: <i>x</i> :: b.\n::\n",
        ":itemize:\n  :-: A :rawhtml: <i>x</i> :: b.\n::\n",
        ":figure: {\n  :path: a.png\n}\n  :caption: A :rawhtml: <i>x</i> :: b.\n::\n",
        ":table:\n  :tbody:\n    :tr: :td: A :rawhtml: <i>x</i> :: b. :: ::\n  ::\n::\n",
    ],
    ids=["span", "strong", "emphas", "theorem", "item", "caption", "table-cell"],
)
def test_allowed_in_inline_contexts(src):
    tree = _tree(src)
    (raw,) = _raws(tree)
    assert raw.html == "<i>x</i>"
    for handrails in (False, True):
        html = _render(src, handrails=handrails)
        assert html.count("<i>x</i>") == 1, html
        assert "&lt;i&gt;" not in html


# ── HTML output ──────────────────────────────────────────────────────────────


def test_html_output_without_alt():
    compare_have_want(
        have="""\
        A :rawhtml: <b>bold</b> :: B.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>A <span class="rawhtml" data-nodeid="3"><b>bold</b></span> B.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_html_output_with_alt_writes_hidden_fallback_before_body():
    compare_have_want(
        have=f"""\
        Consider :rawhtml:{{:alt: the circle $C_0$}} {WIDGET} ::, more.
        """,
        want=f"""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Consider <span class="rawhtml" data-nodeid="3"><span class="rawhtml-alt" hidden>the circle <span class="math" data-nodeid="5">\\(C_0\\)</span></span>{WIDGET}</span>, more.</p>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


@pytest.mark.parametrize("handrails", [False, True])
def test_body_is_not_escaped_and_whitespace_inside_is_kept(handrails):
    body = '<span title="a: b">$x$ *y* **z** `w` &amp; \'q\' "r"</span>\n  <br>'
    html = _render(f"Text :rawhtml: {body} :: end.\n", handrails=handrails)
    assert body in html
    assert "<strong>" not in html and 'class="math"' not in html


@pytest.mark.parametrize("handrails", [False, True])
def test_alt_is_escaped_as_text(handrails):
    html = _render(
        ':rawhtml:{:alt: a < b & "c"} <b>x</b> ::\n', handrails=handrails
    )
    assert '<span class="rawhtml-alt" hidden>a &lt; b &amp; "c"</span><b>x</b>' in html


def test_alt_is_escaped_inside_an_html_block():
    """Text inside an :html: block is written as is, but the fallback of a
    :rawhtml: in its caption is text and is escaped."""
    html = _render(
        """\
        :html: {
          :alt: A widget.
        }

        <div>live</div>

          :caption: See :rawhtml:{:alt: a <dial>} <x-dial></x-dial> ::.

        ::
        """
    )
    assert "a &lt;dial&gt;" in html
    assert html.count("<x-dial></x-dial>") == 1


def test_space_between_math_and_raw_html_is_kept():
    html = _render("$x$ :rawhtml: <b>y</b> :: z\n")
    assert '\\)</span> <span class="rawhtml"' in html


def test_no_js_page_has_the_body_in_place_and_the_fallback_hidden():
    """Without JavaScript the reader sees what the author wrote: the body sits
    in the paragraph and the fallback carries the hidden attribute."""
    html = rsm.build(
        f"# T\n\nConsider :rawhtml:{{:alt: the circle}} {WIDGET} ::.\n",
        handrails=True,
        lint=False,
    )
    assert html.count(WIDGET) == 1
    assert '<span class="rawhtml-alt" hidden>the circle</span>' in html


def test_missing_alt_warns(caplog):
    with caplog.at_level(logging.WARNING):
        _render("A :rawhtml: <b>x</b> :: b.\n")
    assert any(":rawhtml:" in r.message and ":alt:" in r.message for r in caplog.records)


def test_alt_does_not_warn(caplog):
    with caplog.at_level(logging.WARNING):
        _render("A :rawhtml:{:alt: x} <b>x</b> :: b.\n")
    assert not any(":rawhtml:" in r.message for r in caplog.records)


# ── Links ────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "src",
    [
        ":theorem: {:label: thm} T. ::\n\nSee :ref:thm, **a :rawhtml:{:alt: dial} <x-dial></x-dial> ::**::.\n",
        "See :url:https://example.com, *a :rawhtml:{:alt: dial} <x-dial></x-dial> ::*::.\n",
    ],
    ids=["ref", "url"],
)
def test_link_text_shows_the_fallback(src, caplog):
    """The grammar keeps :rawhtml: out of a link's text, but a span in the
    link text can still hold one. A link cannot hold live HTML, so the
    fallback takes its place, with a warning."""
    with caplog.at_level(logging.WARNING):
        html = _render(src)
    assert "<x-dial>" not in html
    assert "dial" in html
    assert any("link" in r.message and ":rawhtml:" in r.message for r in caplog.records)


def test_aside_phrase_shows_the_fallback(caplog):
    src = (
        "A :aside:a1,*the :rawhtml:{:alt: dial} <x-dial></x-dial> ::*:: here.\n\n"
        ":aside: {:label: a1} About it. ::\n"
    )
    with caplog.at_level(logging.WARNING):
        html = _render(src)
    assert "<x-dial>" not in html
    assert "dial" in html
    assert any(":rawhtml:" in r.message for r in caplog.records)


# ── Headings and titles ──────────────────────────────────────────────────────


def test_not_part_of_a_heading_or_title():
    """A heading holds plain text only. An inline tag after the title text
    starts the section's first paragraph (as :code: does), so the raw HTML
    never reaches the heading, the table of contents or <title>."""
    src = dedent(
        """\
        # Doc :rawhtml:{:alt: d} <b>m</b> ::

        :toc: ::

        ## Sec :rawhtml:{:alt: s} <b>s</b> ::

        Text.
        """
    )
    tree = _tree(src)
    assert tree.title == "Doc"
    sec = tree.first_of_type(nodes.Section)
    assert sec.title == "Sec"
    html = rsm.build(src, handrails=True, lint=False)
    assert "<title>Doc</title>" in html
    assert html.count("<b>s</b>") == 1
    assert html.count("<b>m</b>") == 1
    assert "rawhtml" not in html.split("<h1>")[1].split("</h1>")[0]


# ── Plain text read out of the tree ──────────────────────────────────────────


def test_static_fallback_alt_from_caption_uses_the_fallback():
    """A figure's still image without :alt: takes its alt from the caption's
    text, which holds the :rawhtml: fallback and not the markup."""
    html = _render(
        """\
        :figure: {
          :path: assets/interactive.svg
          :static: assets/interactive-static.png
        }
          :caption: The :rawhtml:{:alt: dial} <x-dial></x-dial> :: turns. ::
        ::
        """
    )
    assert 'alt="The dial turns."' in html


def test_proof_tree_step_title_uses_the_fallback():
    tree = _tree(
        """\
        :theorem: {:label: thm} T. ::

        :proof:
          :step: Take :rawhtml:{:alt: the dial} <x-dial></x-dial> :: now. ::
          :step: :qed: Done. ::
        ::
        """
    )
    proof = tree.first_of_type(nodes.Proof)
    titles = [n["title"] for n in proof.tree_nodes]
    assert titles[0] == "Take the dial now."
    assert not any("x-dial" in t for t in titles)


def test_pandoc_export_uses_the_fallback():
    tree = _tree("A :rawhtml:{:alt: circle $C_0$} <x-dial></x-dial> :: b.\n")
    ast = PandocTranslator().translate(tree)
    inlines = ast["blocks"][0]["c"]
    assert {"t": "Str", "c": "circle"} in inlines
    assert {"t": "Math", "c": [{"t": "InlineMath"}, "C_0"]} in inlines
    assert "x-dial" not in repr(ast)


def test_pandoc_export_without_alt_emits_nothing():
    tree = _tree("A :rawhtml: <x-dial></x-dial> :: b.\n")
    ast = PandocTranslator().translate(tree)
    assert "x-dial" not in repr(ast)


def test_embedded_source_is_escaped():
    """The page keeps the RSM source in a hidden div for the Source menu item.
    Written unescaped, the raw HTML in it became a second live copy of every
    :rawhtml: body (and of every inline :html: block)."""
    src = "# T\n\nA :rawhtml:{:alt: x} <x-dial a=\"1\"></x-dial> :: &amp; b.\n"
    html = rsm.render(src, handrails=True, copy_source=True)
    div = html.split('<div class="rsm-source hide">')[1].split("</div>")[0]
    assert "<x-dial" not in div
    assert div == src.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    assert html.count("<x-dial") == 1
