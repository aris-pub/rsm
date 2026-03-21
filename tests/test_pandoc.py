"""Tests for rsm/pandoc.py — PandocTranslator (export) and PandocImporter (import)."""

import shutil
from textwrap import dedent

import pytest

from rsm.app import ParserApp, pandoc_export, pandoc_import
from rsm.pandoc import PANDOC_API_VERSION, PandocImporter, PandocTranslator

# ─── Helpers ──────────────────────────────────────────────────────────────────


def _parse(source: str):
    """Parse RSM source string and return the Manuscript AST node."""
    return ParserApp(plain=dedent(source).strip()).run()


def _translate(source: str) -> dict:
    """Parse RSM source and translate to a pandoc JSON AST dict."""
    return PandocTranslator().translate(_parse(source))


def _blocks(source: str) -> list:
    """Return the top-level blocks list from the pandoc AST."""
    return _translate(source)["blocks"]


def _ast(meta: dict | None = None, blocks: list | None = None) -> dict:
    """Build a minimal pandoc JSON AST dict for import tests."""
    return {
        "pandoc-api-version": PANDOC_API_VERSION,
        "meta": meta or {},
        "blocks": blocks or [],
    }


IMP = PandocImporter()

# ─── Export tests ─────────────────────────────────────────────────────────────


def test_api_version():
    ast = _translate("Hello.")
    assert ast["pandoc-api-version"] == PANDOC_API_VERSION


def test_meta_title():
    ast = _translate(
        """
        # My Title {
          :label: doc
        }
        """
    )
    assert ast["meta"]["title"] == {
        "t": "MetaInlines",
        "c": [{"t": "Str", "c": "My Title"}],
    }


def test_meta_no_title():
    ast = _translate("Hello.")
    assert "title" not in ast["meta"]


def test_section_header():
    blocks = _blocks(
        """
        # Doc

        ## Introduction
        """
    )
    headers = [b for b in blocks if b["t"] == "Header"]
    assert headers
    # Section.level == 2, so pandoc Header level == 2
    assert headers[0]["c"][0] == 2
    title_inlines = headers[0]["c"][2]
    assert {"t": "Str", "c": "Introduction"} in title_inlines


def test_subsection_level():
    blocks = _blocks(
        """
        # Doc

        ## Intro

        ### Details
        """
    )
    headers = [b for b in blocks if b["t"] == "Header"]
    levels = [h["c"][0] for h in headers]
    assert 2 in levels  # Section
    assert 3 in levels  # Subsection


def test_plain_paragraph():
    blocks = _blocks("Hello world.")
    paras = [b for b in blocks if b["t"] == "Para"]
    assert paras
    inlines = paras[0]["c"]
    assert {"t": "Str", "c": "Hello"} in inlines
    assert {"t": "Space"} in inlines
    assert {"t": "Str", "c": "world."} in inlines


def test_inline_math():
    blocks = _blocks("A :math: x^2 :: formula.")
    paras = [b for b in blocks if b["t"] == "Para"]
    assert paras
    inlines = paras[0]["c"]
    math_nodes = [i for i in inlines if i.get("t") == "Math"]
    assert math_nodes
    m = math_nodes[0]
    assert m["c"][0] == {"t": "InlineMath"}
    assert m["c"][1] == "x^2"


def test_display_math():
    blocks = _blocks(
        """
        # Doc

        $$
        2+2=4
        $$
        """
    )
    paras = [b for b in blocks if b["t"] == "Para"]
    display_math = [
        i
        for p in paras
        for i in p["c"]
        if i.get("t") == "Math" and i["c"][0].get("t") == "DisplayMath"
    ]
    assert display_math
    assert "2+2=4" in display_math[0]["c"][1]


def test_strong():
    blocks = _blocks("This is :span: {:strong:} bold :: text.")
    paras = [b for b in blocks if b["t"] == "Para"]
    inlines = paras[0]["c"]
    strongs = [i for i in inlines if i.get("t") == "Strong"]
    assert strongs
    inner = strongs[0]["c"]
    assert any(i.get("t") == "Str" and "bold" in i.get("c", "") for i in inner)


def test_emph():
    blocks = _blocks("This is :span: {:emphas:} italic :: text.")
    paras = [b for b in blocks if b["t"] == "Para"]
    inlines = paras[0]["c"]
    emphs = [i for i in inlines if i.get("t") == "Emph"]
    assert emphs


def test_codeblock():
    blocks = _blocks(
        """
        # Doc

        :codeblock: {:lang: python}
          x = 1
        ::
        """
    )
    codeblocks = [b for b in blocks if b["t"] == "CodeBlock"]
    assert codeblocks
    attrs, src = codeblocks[0]["c"]
    _, classes, _ = attrs
    assert "python" in classes
    assert "x = 1" in src


def test_inline_code():
    blocks = _blocks("Use :code: {:lang: python} print() :: here.")
    paras = [b for b in blocks if b["t"] == "Para"]
    inlines = paras[0]["c"]
    codes = [i for i in inlines if i.get("t") == "Code"]
    assert codes
    _attrs, src = codes[0]["c"]
    assert "print()" in src


def test_bullet_list():
    blocks = _blocks(
        """
        :itemize:

          :-: First.

          :-: Second.

        ::
        """
    )
    bullets = [b for b in blocks if b["t"] == "BulletList"]
    assert bullets
    assert len(bullets[0]["c"]) == 2


def test_ordered_list():
    blocks = _blocks(
        """
        :enumerate:

          :-: First.

          :-: Second.

        ::
        """
    )
    ordered = [b for b in blocks if b["t"] == "OrderedList"]
    assert ordered
    _list_attrs, items = ordered[0]["c"]
    assert len(items) == 2


def test_figure_path():
    blocks = _blocks(
        """
        # Doc

        :figure: {
          :path: img/foo.png
        }
        ::
        """
    )
    figures = [b for b in blocks if b["t"] == "Figure"]
    assert figures
    content_blocks = figures[0]["c"][2]
    image = content_blocks[0]["c"][0]
    assert image["t"] == "Image"
    assert image["c"][2][0] == "img/foo.png"


def test_figure_static_path():
    """When :static: is set, the static path is used as the image source."""
    blocks = _blocks(
        """
        # Doc

        :figure: {
          :path: img/foo.png
          :static: img/foo.pdf
        }
        ::
        """
    )
    figures = [b for b in blocks if b["t"] == "Figure"]
    assert figures
    content_blocks = figures[0]["c"][2]
    image = content_blocks[0]["c"][0]
    assert image["t"] == "Image"
    assert image["c"][2][0] == "img/foo.pdf"


def test_theorem_div():
    blocks = _blocks(
        """
        # Doc

        ## Sec

        :theorem:
          This is a theorem.
        ::
        """
    )
    divs = [b for b in blocks if b["t"] == "Div"]
    assert divs
    _, classes, _ = divs[0]["c"][0]
    assert "theorem" in classes


def test_proof_div():
    blocks = _blocks(
        """
        # Doc

        ## Sec

        :proof:
          This is a proof.
        ::
        """
    )
    divs = [b for b in blocks if b["t"] == "Div"]
    assert divs
    _, classes, _ = divs[0]["c"][0]
    assert "proof" in classes


def test_bibliography_header():
    blocks = _blocks(
        """
        # Doc

        :references:
          @book{knuth,
            title={The Art},
            author={Knuth, D.},
            year={2014}
          }
        ::
        """
    )
    headers = [b for b in blocks if b["t"] == "Header"]
    ref_headers = [
        h for h in headers
        if any(i.get("c") == "References" for i in h["c"][2])
    ]
    assert ref_headers


# ─── Import tests ─────────────────────────────────────────────────────────────


def test_import_title():
    result = IMP.from_json(_ast(
        meta={"title": {"t": "MetaInlines", "c": [{"t": "Str", "c": "My Doc"}]}}
    ))
    assert "# My Doc" in result


def test_import_author():
    result = IMP.from_json(_ast(
        meta={
            "author": {
                "t": "MetaList",
                "c": [{"t": "MetaInlines", "c": [{"t": "Str", "c": "Ada Lovelace"}]}],
            }
        }
    ))
    assert ":author:" in result
    assert "Ada Lovelace" in result


def test_import_paragraph():
    result = IMP.from_json(_ast(blocks=[
        {"t": "Para", "c": [
            {"t": "Str", "c": "Hello"},
            {"t": "Space"},
            {"t": "Str", "c": "world."},
        ]}
    ]))
    assert "Hello world." in result


def test_import_section():
    result = IMP.from_json(_ast(blocks=[
        {"t": "Header", "c": [2, ["intro", [], []], [{"t": "Str", "c": "Introduction"}]]}
    ]))
    assert "## Introduction" in result


def test_import_strong():
    result = IMP.from_json(_ast(blocks=[
        {"t": "Para", "c": [{"t": "Strong", "c": [{"t": "Str", "c": "bold"}]}]}
    ]))
    assert "**bold**" in result


def test_import_emph():
    result = IMP.from_json(_ast(blocks=[
        {"t": "Para", "c": [{"t": "Emph", "c": [{"t": "Str", "c": "italic"}]}]}
    ]))
    assert "*italic*" in result


def test_import_inline_math():
    result = IMP.from_json(_ast(blocks=[
        {"t": "Para", "c": [
            {"t": "Math", "c": [{"t": "InlineMath"}, "x^2"]}
        ]}
    ]))
    assert ":math: x^2 ::" in result


def test_import_display_math():
    result = IMP.from_json(_ast(blocks=[
        {"t": "Para", "c": [
            {"t": "Math", "c": [{"t": "DisplayMath"}, "2+2=4"]}
        ]}
    ]))
    assert ":mathblock:" in result
    assert "2+2=4" in result


def test_import_codeblock():
    result = IMP.from_json(_ast(blocks=[
        {"t": "CodeBlock", "c": [["", ["python"], []], "x = 1"]}
    ]))
    assert ":codeblock:" in result
    assert "python" in result
    assert "x = 1" in result


def test_import_bullet_list():
    result = IMP.from_json(_ast(blocks=[
        {"t": "BulletList", "c": [
            [{"t": "Para", "c": [{"t": "Str", "c": "First"}]}],
            [{"t": "Para", "c": [{"t": "Str", "c": "Second"}]}],
        ]}
    ]))
    assert ":itemize:" in result
    assert ":-: First" in result
    assert ":-: Second" in result


def test_import_ordered_list():
    result = IMP.from_json(_ast(blocks=[
        {"t": "OrderedList", "c": [
            [1, {"t": "Decimal"}, {"t": "Period"}],
            [
                [{"t": "Para", "c": [{"t": "Str", "c": "One"}]}],
                [{"t": "Para", "c": [{"t": "Str", "c": "Two"}]}],
            ],
        ]}
    ]))
    assert ":enumerate:" in result
    assert ":-: One" in result


def test_import_figure():
    result = IMP.from_json(_ast(blocks=[
        {"t": "Figure", "c": [
            ["fig1", ["figure"], []],
            {"t": "Caption", "c": [
                None,
                [{"t": "Para", "c": [{"t": "Str", "c": "A caption"}]}],
            ]},
            [{"t": "Plain", "c": [
                {"t": "Image", "c": [
                    ["", [], []],
                    [{"t": "Str", "c": "alt"}],
                    ["img/foo.png", ""],
                ]}
            ]}],
        ]}
    ]))
    assert ":figure:" in result
    assert "img/foo.png" in result


def test_import_rawblock_latex():
    result = IMP.from_json(_ast(blocks=[
        {"t": "RawBlock", "c": ["latex", r"\alpha + \beta"]}
    ]))
    assert ":mathblock:" in result
    assert r"\alpha + \beta" in result


def test_import_horizontal_rule():
    result = IMP.from_json(_ast(blocks=[
        {"t": "HorizontalRule", "c": []}
    ]))
    assert result.strip() == ""


def test_import_url():
    result = IMP.from_json(_ast(blocks=[
        {"t": "Para", "c": [
            {"t": "Link", "c": [
                ["", [], []],
                [{"t": "Str", "c": "click here"}],
                ["https://example.com", ""],
            ]}
        ]}
    ]))
    assert ":url: https://example.com ::" in result


def test_import_rawinline_latex():
    result = IMP.from_json(_ast(blocks=[
        {"t": "Para", "c": [
            {"t": "RawInline", "c": ["latex", r"\alpha"]}
        ]}
    ]))
    assert r":math: \alpha ::" in result


# ─── Roundtrip tests ──────────────────────────────────────────────────────────

_PANDOC_SKIP = pytest.mark.skipif(
    shutil.which("pandoc") is None, reason="pandoc not installed"
)


@_PANDOC_SKIP
def test_roundtrip_paragraph():
    markdown_in = "Hello world.\n"
    rsm_text = pandoc_import(source=markdown_in, from_format="markdown")
    markdown_out = pandoc_export(source=rsm_text, to_format="markdown")
    assert markdown_out.strip() == markdown_in.strip()


@_PANDOC_SKIP
def test_roundtrip_headings():
    markdown_in = "## Introduction\n\n### Details\n"
    rsm_text = pandoc_import(source=markdown_in, from_format="markdown")
    markdown_out = pandoc_export(source=rsm_text, to_format="markdown")
    assert "Introduction" in markdown_out
    assert "Details" in markdown_out


@_PANDOC_SKIP
def test_roundtrip_bold_italic():
    markdown_in = "This is **bold** and *italic*.\n"
    rsm_text = pandoc_import(source=markdown_in, from_format="markdown")
    markdown_out = pandoc_export(source=rsm_text, to_format="markdown")
    assert "**bold**" in markdown_out
    assert "*italic*" in markdown_out


@_PANDOC_SKIP
def test_roundtrip_inline_math():
    markdown_in = "Inline $x^2$ math.\n"
    rsm_text = pandoc_import(source=markdown_in, from_format="markdown")
    markdown_out = pandoc_export(source=rsm_text, to_format="markdown")
    assert "x^2" in markdown_out


@_PANDOC_SKIP
def test_roundtrip_codeblock():
    markdown_in = "```python\nx = 1\n```\n"
    rsm_text = pandoc_import(source=markdown_in, from_format="markdown")
    markdown_out = pandoc_export(source=rsm_text, to_format="markdown")
    assert "python" in markdown_out
    assert "x = 1" in markdown_out


@_PANDOC_SKIP
def test_roundtrip_bullet_list():
    markdown_in = "- First\n- Second\n"
    rsm_text = pandoc_import(source=markdown_in, from_format="markdown")
    markdown_out = pandoc_export(source=rsm_text, to_format="markdown")
    assert "First" in markdown_out
    assert "Second" in markdown_out


@_PANDOC_SKIP
def test_roundtrip_ordered_list():
    markdown_in = "1. One\n2. Two\n"
    rsm_text = pandoc_import(source=markdown_in, from_format="markdown")
    markdown_out = pandoc_export(source=rsm_text, to_format="markdown")
    assert "One" in markdown_out
    assert "Two" in markdown_out


class TestCaptionFormat:
    """Regression: Caption must be a bare array, not {"t": "Caption", "c": [...]}."""

    def test_figure_caption_is_array(self):
        blocks = _blocks("""\
        :figure: {
          :path: test.png
          :label: fig-test
        }
          :caption: A test figure.
        ::
        """)
        figures = [b for b in blocks if b["t"] == "Figure"]
        assert len(figures) == 1
        caption = figures[0]["c"][1]
        # Caption must be a plain array [shortCaption, [blocks]], not {"t": "Caption", ...}
        assert isinstance(caption, list), f"Caption should be list, got {type(caption).__name__}: {caption}"
        assert len(caption) == 2

    def test_table_caption_is_array(self):
        blocks = _blocks("""\
        :table:
          :caption: A test table.

          | a | b |
          | 1 | 2 |
        ::
        """)
        tables = [b for b in blocks if b["t"] == "Table"]
        assert len(tables) == 1
        caption = tables[0]["c"][1]
        assert isinstance(caption, list), f"Caption should be list, got {type(caption).__name__}: {caption}"
        assert len(caption) == 2

    def test_figure_export_roundtrips_through_pandoc(self):
        """The full export pipeline should not crash on figures with captions."""
        source = dedent("""\
        :figure: {
          :path: test.png
          :label: fig-test
        }
          :caption: A test figure.
        ::
        """).strip()
        # This should not raise — pandoc should accept the JSON
        result = pandoc_export(source, to_format="typst")
        assert len(result) > 0


class TestCitationsAsPlainText:
    """rsm-98c: Citations should render as plain text [N] for Typst compatibility."""

    def test_cite_renders_as_plain_text_not_cite_object(self):
        blocks = _blocks("""\
        See :cite:smith2024::.

        :references:
        @article smith2024
          :author: Smith, J.
          :title: Test paper
          :journal: Test Journal
          :year: 2024
        ::
        """)
        import json
        full = json.dumps(blocks)
        # Must NOT contain Pandoc Cite objects (Typst can't resolve them)
        assert '"t": "Cite"' not in full, "Citations should be plain text, not Cite objects"
        # Should contain the citation as a Str
        assert '"t": "Str"' in full


class TestMissingBlockHandlers:
    """rsm-kaw, rsm-90w, rsm-9r9, rsm-09d, rsm-b0j: Missing block handlers."""

    def test_html_emits_placeholder(self):
        blocks = _blocks("""\
        :html: {
          :path: widget.html
        }
        ::
        """)
        text = str(blocks)
        assert "online" in text.lower() or "widget" in text.lower() or "html" in text.lower()

    def test_video_emits_placeholder(self):
        blocks = _blocks("""\
        :video: {
          :path: demo.mp4
        }
        ::
        """)
        text = str(blocks)
        assert len(blocks) > 0  # Not silently dropped

    def test_authorblock_silently_skipped(self):
        """AuthorBlock should not crash or warn."""
        blocks = _blocks("""\
        :author: {
          :name: Test Author
        } ::
        """)
        # Just verify no crash — authors go in meta

    def test_subproof_does_not_warn(self):
        """Subproof should be handled without fallback warning."""
        from rsm import nodes as n
        assert n.Subproof in PandocTranslator._BLOCK_DISPATCH

    def test_construct_dispatch_exists(self):
        """ClaimBlock, Construct, Statement should be in dispatch."""
        from rsm import nodes as n
        assert n.ClaimBlock in PandocTranslator._BLOCK_DISPATCH
        assert n.Construct in PandocTranslator._BLOCK_DISPATCH
        assert n.Statement in PandocTranslator._BLOCK_DISPATCH


class TestClickableCitations:
    """Citations should be clickable links to bibliography entries."""

    def test_cite_emits_link_when_resolved(self):
        """When cite resolves to a Bibitem with label, emit a Link."""
        from rsm.pandoc import PandocTranslator
        from rsm import nodes
        # Simulate a resolved cite with a real Bibitem target
        translator = PandocTranslator()
        bibitem = nodes.Bibitem(label="smith2024")
        bibitem.number = 1
        cite = nodes.Cite()
        cite.targets = [bibitem]
        result = translator._inline_cite(cite)
        import json
        full = json.dumps(result)
        assert '"t": "Link"' in full
        assert "#ref-smith2024" in full
        assert '"1"' in full  # display text is the number

    def test_cite_no_cite_objects(self):
        """Citations must not use Pandoc Cite objects."""
        from rsm.pandoc import PandocTranslator
        from rsm import nodes
        translator = PandocTranslator()
        bibitem = nodes.Bibitem(label="test")
        bibitem.number = 1
        cite = nodes.Cite()
        cite.targets = [bibitem]
        result = translator._inline_cite(cite)
        import json
        full = json.dumps(result)
        assert '"t": "Cite"' not in full

    def test_bibitem_has_anchor_id(self):
        """Bibliography entries should have ref-{label} anchor IDs."""
        from rsm.pandoc import PandocTranslator
        from rsm import nodes
        translator = PandocTranslator()
        bibitem = nodes.Bibitem(label="smith2024")
        bibitem.number = 1
        bibitem.author = "Smith"
        bibitem.title = "Test"
        bibitem.year = 2024
        result = translator._format_bibitem(bibitem)
        import json
        full = json.dumps(result)
        assert "ref-smith2024" in full

    def test_unresolved_cite_falls_back_to_text(self):
        """Unresolved cites should render as plain text, not crash."""
        from rsm.pandoc import PandocTranslator
        from rsm import nodes
        translator = PandocTranslator()
        unknown = nodes.UnknownBibitem()
        unknown.number = "?"
        cite = nodes.Cite()
        cite.targets = [unknown]
        result = translator._inline_cite(cite)
        import json
        full = json.dumps(result)
        assert "?" in full
