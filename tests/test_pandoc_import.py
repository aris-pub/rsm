"""Unit tests for the pandoc AST to RSM import translator (PandocImporter)."""

from rsm.pandoc import PandocImporter


def test_figure_with_caption_does_not_crash():
    # Regression: a pandoc Figure caption is a list [short-caption, [blocks]],
    # not a node with a "c" key. _block_figure called .get on it and crashed on
    # any captioned figure, which is most real papers.
    ast = {
        "blocks": [
            {
                "t": "Figure",
                "c": [
                    ["", [], []],
                    [
                        None,
                        [
                            {
                                "t": "Para",
                                "c": [
                                    {"t": "Str", "c": "A"},
                                    {"t": "Space"},
                                    {"t": "Str", "c": "caption"},
                                ],
                            }
                        ],
                    ],
                    [
                        {
                            "t": "Plain",
                            "c": [
                                {
                                    "t": "Image",
                                    "c": [["", [], []], [], ["fig.png", ""]],
                                }
                            ],
                        }
                    ],
                ],
            }
        ]
    }
    out = PandocImporter().from_json(ast)
    assert ":figure:" in out
    assert "fig.png" in out
    assert "A caption" in out
    # The image path must sit in a block meta that actually parses as a figure.
    import rsm

    html = rsm.render("# T\n\n" + out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out


def test_figure_empty_path_degrades_to_caption_only():
    # pandoc sometimes yields a Figure whose image has no resolvable path (the
    # PDF subfigures in real papers). An empty {:path: } fails to parse, so the
    # importer must drop the path meta and keep the figure as caption-only.
    ast = {
        "blocks": [
            {
                "t": "Figure",
                "c": [
                    ["", [], []],
                    [
                        None,
                        [
                            {
                                "t": "Para",
                                "c": [
                                    {"t": "Str", "c": "A"},
                                    {"t": "Space"},
                                    {"t": "Str", "c": "caption"},
                                ],
                            }
                        ],
                    ],
                    [
                        {
                            "t": "Plain",
                            "c": [{"t": "Image", "c": [["", [], []], [], ["", ""]]}],
                        }
                    ],
                ],
            }
        ]
    }
    out = PandocImporter().from_json(ast)
    assert ":figure:" in out
    assert "{:path: }" not in out
    assert ":path:" not in out
    assert "A caption" in out
    import rsm

    html = rsm.render("# T\n\n" + out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out


def test_author_name_drops_thanks_footnote_and_parses():
    # pandoc renders a \thanks footnote as a Note inline inside the author's
    # MetaInlines. Rendered into :name: it produces an invalid multi-line value.
    # The name must be just the plain text before the footnote.
    ast = {
        "meta": {
            "title": {"t": "MetaInlines", "c": [{"t": "Str", "c": "T"}]},
            "author": {
                "t": "MetaList",
                "c": [
                    {
                        "t": "MetaInlines",
                        "c": [
                            {"t": "Str", "c": "Ashish"},
                            {"t": "Space"},
                            {"t": "Str", "c": "Vaswani"},
                            {
                                "t": "Note",
                                "c": [
                                    {
                                        "t": "Para",
                                        "c": [
                                            {"t": "Str", "c": "Equal"},
                                            {"t": "Space"},
                                            {"t": "Str", "c": "contribution."},
                                        ],
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "t": "MetaInlines",
                        "c": [
                            {"t": "Str", "c": "Noam"},
                            {"t": "Space"},
                            {"t": "Str", "c": "Shazeer"},
                        ],
                    },
                ],
            },
        },
        "blocks": [],
    }
    out = PandocImporter().from_json(ast)
    assert ":name: Ashish Vaswani" in out
    assert ":name: Noam Shazeer" in out
    assert ":note:" not in out
    assert "Equal contribution" not in out
    import rsm

    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html, out


def _words(*words):
    inlines = []
    for i, w in enumerate(words):
        if i:
            inlines.append({"t": "Space"})
        inlines.append({"t": "Str", "c": w})
    return inlines


def _note(*paras):
    return {"t": "Note", "c": [{"t": "Para", "c": _words(*p.split())} for p in paras]}


def test_footnote_becomes_call_and_definition_after_the_paragraph():
    import rsm

    ast = {
        "blocks": [
            {
                "t": "Para",
                "c": [
                    *_words("Some", "text."),
                    _note("The note."),
                    {"t": "Space"},
                    *_words("More", "text."),
                ],
            },
            {"t": "Para", "c": _words("Next", "paragraph.")},
        ]
    }
    out = PandocImporter().from_json(ast)
    assert "text. :note:note-1:: More text." in out
    definition = ":note: {:label: note-1} The note. ::"
    assert definition in out
    assert (
        out.index("More text.") < out.index(definition) < out.index("Next paragraph.")
    )

    tree = rsm.transformer.Transformer().transform(rsm.tsparser.TSParser().parse(out))
    (call,) = tree.traverse(nodeclass=rsm.nodes.NoteCall)
    assert call.definition is not None
    assert call.number == 1


def test_footnotes_get_distinct_labels():
    ast = {
        "blocks": [
            {
                "t": "Para",
                "c": [
                    *_words("A."),
                    _note("one"),
                    {"t": "Space"},
                    *_words("B."),
                    _note("two"),
                ],
            },
        ]
    }
    out = PandocImporter().from_json(ast)
    assert ":note:note-1::" in out and ":note:note-2::" in out
    assert ":note: {:label: note-1} one ::" in out
    assert ":note: {:label: note-2} two ::" in out


def test_footnote_with_two_paragraphs_stays_one_definition():
    import rsm

    ast = {"blocks": [{"t": "Para", "c": [*_words("A."), _note("First.", "Second.")]}]}
    out = PandocImporter().from_json(ast)
    tree = rsm.tsparser.TSParser().parse(out)
    assert not list(tree.traverse(nodeclass=rsm.nodes.Error)), out
    (note,) = tree.traverse(nodeclass=rsm.nodes.Note)
    assert note.label == "note-1"


def test_footnote_inside_a_list_item_is_defined_after_the_list():
    import rsm

    ast = {
        "blocks": [
            {
                "t": "BulletList",
                "c": [[{"t": "Plain", "c": [*_words("Item."), _note("In a list.")]}]],
            },
        ]
    }
    out = PandocImporter().from_json(ast)
    tree = rsm.transformer.Transformer().transform(rsm.tsparser.TSParser().parse(out))
    assert not list(tree.traverse(nodeclass=rsm.nodes.Error)), out
    (call,) = tree.traverse(nodeclass=rsm.nodes.NoteCall)
    assert call.definition is not None


def _parse_without_errors(out):
    import rsm

    tree = rsm.transformer.Transformer().transform(rsm.tsparser.TSParser().parse(out))
    assert not list(tree.traverse(nodeclass=rsm.nodes.Error)), out
    return tree


def _render(out):
    import rsm

    return rsm.render("# T\n\n" + out, handrails=False, source_offsets=False)


def test_rawblock_html_becomes_htmlblock():
    import rsm

    raw = '<div id="a">\n<input type="range" min="1">\n</div>'
    out = PandocImporter().from_json(
        {"blocks": [{"t": "RawBlock", "c": ["html", raw]}]}
    )
    assert out == f":htmlblock:\n{raw}\n::\n\n"
    tree = _parse_without_errors(out)
    assert len(list(tree.traverse(nodeclass=rsm.nodes.HtmlBlock))) == 1
    assert raw in _render(out)


def _para_with_raw(raw):
    return {
        "blocks": [
            {
                "t": "Para",
                "c": [
                    *_words("a"),
                    {"t": "Space"},
                    {"t": "RawInline", "c": ["html", raw]},
                    {"t": "Space"},
                    *_words("b"),
                ],
            }
        ]
    }


def test_whole_rawinline_html_becomes_html():
    import rsm

    pieces = [
        "<br>",
        "<HR>",
        "<wbr>",
        '<img src="a.png">',
        '<img src="a.png"/>',
        '<circle r="1" />',
        '<mtp-display model="x"></mtp-display>',
        "<b>bold <i>x</i></b>",
    ]
    for raw in pieces:
        out = PandocImporter().from_json(_para_with_raw(raw))
        assert f":html: {raw} ::" in out, out
        tree = _parse_without_errors(out)
        assert len(list(tree.traverse(nodeclass=rsm.nodes.RawHtml))) == 1, out
        assert raw in _render(out), raw


def test_split_rawinline_html_is_dropped_with_warning(caplog):
    for raw in ("<span>", "</span>", '<a href="x">', "<b>x", "<b>x</i>"):
        caplog.clear()
        out = PandocImporter().from_json(_para_with_raw(raw))
        assert raw not in out, out
        assert "skipping RawInline with format 'html'" in caplog.text, raw


def _rawblock(raw):
    return {"blocks": [{"t": "RawBlock", "c": ["html", raw]}]}


def test_html_comments_are_dropped_silently(caplog):
    for ast in (_para_with_raw("<!-- c -->"), _rawblock("<!-- a\nblock comment -->")):
        caplog.clear()
        out = PandocImporter().from_json(ast)
        assert "<!--" not in out, out
        assert ":html" not in out, out
        assert caplog.text == ""


def test_raw_html_with_double_colon_is_dropped_with_warning(caplog):
    for ast in (
        _para_with_raw('<span title="a::b"></span>'),
        _rawblock("<script>\nx = a::b;\n</script>"),
    ):
        caplog.clear()
        out = PandocImporter().from_json(ast)
        assert "a::b" not in out, out
        assert ":html" not in out, out
        assert "'::'" in caplog.text
        assert "end of the tag" in caplog.text


def _para_with_link(text_inlines: list, url: str) -> dict:
    return {
        "blocks": [
            {
                "t": "Para",
                "c": [
                    {"t": "Str", "c": "See"},
                    {"t": "Space"},
                    {"t": "Link", "c": [["", [], []], text_inlines, [url, ""]]},
                ],
            }
        ]
    }


def test_link_keeps_its_text():
    # A Markdown link [the book](https://example.org) lost "the book".
    text = [{"t": "Str", "c": "the"}, {"t": "Space"}, {"t": "Str", "c": "book"}]
    out = PandocImporter().from_json(_para_with_link(text, "https://example.org"))
    assert ":url:https://example.org, the book::" in out


def test_link_whose_text_is_its_address_has_no_text():
    text = [{"t": "Str", "c": "https://example.org"}]
    out = PandocImporter().from_json(_para_with_link(text, "https://example.org"))
    assert ":url:https://example.org::" in out
