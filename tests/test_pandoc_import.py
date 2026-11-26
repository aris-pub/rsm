"""Unit tests for the pandoc AST to RSM import translator (PandocImporter)."""

import shutil

import pytest

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


# The dicts below copy what pandoc 3's LaTeX reader writes for amsthm theorems,
# proofs and \ref (bead rsm-v1yn).


def _thm_heading(name, number):
    return [
        {"t": "Strong", "c": [*_words(name), {"t": "Space"}, *_words(number)]},
        {"t": "Str", "c": "."},
        {"t": "Space"},
        {"t": "Space"},
    ]


def _emph(*inlines):
    return {"t": "Emph", "c": list(inlines)}


def _div(ident, cls, blocks):
    return {"t": "Div", "c": [[ident, [cls], []], blocks]}


def _ref(target, text="1", kind="ref"):
    return {
        "t": "Link",
        "c": [
            ["", [], [["reference-type", kind], ["reference", target]]],
            [{"t": "Str", "c": text}],
            ["#" + target, ""],
        ],
    }


def _body(out, tag):
    start = out.index(f":{tag}:")
    end = out.index("\n::", start)
    return out[start:end]


def test_theorem_heading_and_italic_style_are_dropped():
    statement = _emph(
        *_words("A", "graph"),
        {"t": "Space"},
        _emph(*_words("has")),
        {"t": "Space"},
        *_words("edges."),
    )
    ast = {
        "blocks": [
            _div(
                "thm:a",
                "theorem",
                [
                    {"t": "Para", "c": [*_thm_heading("Theorem", "1"), statement]},
                    {"t": "Para", "c": [_emph(*_words("Second", "para."))]},
                ],
            )
        ]
    }
    out = PandocImporter().from_json(ast)
    body = _body(out, "theorem")
    assert "Theorem 1" not in body, out
    assert "A graph *has* edges." in body, out
    assert "\n\nSecond para." in body, out
    _parse_without_errors(out)


def test_upright_theorem_keeps_its_body():
    heading = _thm_heading("Lemma", "2")
    ast = {
        "blocks": [
            _div("", "lemma", [{"t": "Para", "c": [*heading, *_words("A", "lemma.")]}])
        ]
    }
    body = _body(PandocImporter().from_json(ast), "lemma")
    assert "Lemma 2" not in body
    assert "A lemma." in body


def test_theorem_italics_are_dropped_inside_lists():
    ast = {
        "blocks": [
            _div(
                "",
                "lemma",
                [
                    {"t": "Para", "c": _thm_heading("Lemma", "1")},
                    {
                        "t": "OrderedList",
                        "c": [
                            [1, {"t": "DefaultStyle"}, {"t": "DefaultDelim"}],
                            [[{"t": "Para", "c": [_emph(*_words("x"))]}]],
                        ],
                    },
                ],
            )
        ]
    }
    out = PandocImporter().from_json(ast)
    body = _body(out, "lemma")
    assert "Lemma 1" not in body, out
    assert "*" not in body, out
    _parse_without_errors(out)


def test_display_math_in_italic_theorem_becomes_a_mathblock():
    math = {"t": "Math", "c": [{"t": "DisplayMath"}, "a=b"]}
    statement = _emph(
        *_words("X."), {"t": "SoftBreak"}, math, {"t": "SoftBreak"}, *_words("Y.")
    )
    ast = {
        "blocks": [
            _div(
                "",
                "theorem",
                [{"t": "Para", "c": [*_thm_heading("Theorem", "1"), statement]}],
            )
        ]
    }
    out = PandocImporter().from_json(ast)
    assert ":mathblock:" in out, out
    assert "*" not in _body(out, "theorem"), out


def test_proof_heading_and_tombstone_are_dropped():
    ast = {
        "blocks": [
            _div(
                "",
                "proof",
                [
                    {
                        "t": "Para",
                        "c": [
                            _emph(*_words("Proof.")),
                            {"t": "Space"},
                            *_words("By", "magic."),
                            {"t": "Str", "c": " ◻"},
                        ],
                    }
                ],
            )
        ]
    }
    out = PandocImporter().from_json(ast)
    body = _body(out, "proof")
    assert "Proof." not in body, out
    assert "◻" not in out, out
    assert body.rstrip().endswith("By magic."), out


def test_proof_tombstone_in_its_own_paragraph_is_dropped():
    first = [_emph(*_words("Proof.")), {"t": "Space"}, *_words("A.")]
    ast = {
        "blocks": [
            _div(
                "",
                "proof",
                [
                    {"t": "Para", "c": first},
                    {"t": "BulletList", "c": [[{"t": "Para", "c": _words("z")}]]},
                    {"t": "Para", "c": [{"t": "Str", "c": " ◻"}]},
                ],
            )
        ]
    }
    out = PandocImporter().from_json(ast)
    assert "◻" not in out, out
    _parse_without_errors(out)


def _ref_ast(before, target_block, target):
    return {
        "blocks": [
            target_block,
            {"t": "Para", "c": [*before, _ref(target), {"t": "Str", "c": "."}]},
        ]
    }


def _last_line(out):
    return out.rstrip().splitlines()[-1]


_THM = _div("thm:a", "theorem", [{"t": "Para", "c": _words("X.")}])
_SEC = {"t": "Header", "c": [1, ["sec:a", [], []], _words("Intro")]}
_FIG = {
    "t": "Figure",
    "c": [["fig:a", [], []], [None, []], [{"t": "Plain", "c": []}]],
}


def test_kind_word_before_a_ref_to_that_kind_is_dropped():
    cases = [
        ([{"t": "Str", "c": "Theorem "}], _THM, "thm:a", "thm-1"),
        ([*_words("theorem"), {"t": "Space"}], _THM, "thm:a", "thm-1"),
        ([{"t": "Str", "c": "Section "}], _SEC, "sec:a", "sec-1"),
        ([*_words("By", "section"), {"t": "Space"}], _SEC, "sec:a", "sec-1"),
        ([{"t": "Str", "c": "Figure "}], _FIG, "fig:a", "fig-1"),
    ]
    for before, block, target, label in cases:
        line = _last_line(PandocImporter().from_json(_ref_ast(before, block, target)))
        assert line in (f":ref:{label}::.", f"By :ref:{label}::."), line


def test_kind_word_after_an_open_paren_is_dropped():
    out = PandocImporter().from_json(
        _ref_ast([{"t": "Str", "c": "(Theorem "}], _THM, "thm:a")
    )
    assert _last_line(out) == "(:ref:thm-1::.", out


def test_words_that_do_not_match_the_target_kind_are_kept():
    for word in ("Lemma", "Section", "Subtheorem"):
        before = [{"t": "Str", "c": word + " "}]
        out = PandocImporter().from_json(_ref_ast(before, _THM, "thm:a"))
        assert _last_line(out) == f"{word} :ref:thm-1::.", out


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")
def test_latex_import_of_theorem_proof_and_ref():
    import rsm
    from rsm.app import pandoc_import

    src = r"""\documentclass{article}
\usepackage{amsthm}
\newtheorem{theorem}{Theorem}
\begin{document}
\section{Results}
\begin{theorem}\label{thm:mantel}
A triangle-free graph has at most $n^2/4$ edges.
\end{theorem}
\begin{proof}
By Theorem~\ref{thm:mantel} we are done.
\end{proof}
\end{document}
"""
    out = pandoc_import(source=src, from_format="latex")
    assert "A triangle-free graph has at most $n^2/4$ edges." in out, out
    assert "*A triangle" not in out, out
    assert "**Theorem" not in out, out
    assert "Proof." not in out, out
    assert "◻" not in out, out
    assert "By :ref:thm-1:: we are done." in out, out
    html = rsm.render(out, handrails=False, source_offsets=False)
    assert 'class="error"' not in html
    assert "Theorem Theorem" not in html


def test_titled_theorem_moves_its_title_into_meta():
    import rsm

    math = {"t": "Math", "c": [{"t": "InlineMath"}, "K_3"]}
    heading = [
        {"t": "Strong", "c": _words("Theorem", "1")},
        {"t": "Space"},
        {"t": "Str", "c": "(Mantel,"},
        {"t": "Space"},
        math,
        {"t": "Str", "c": "-free)."},
        {"t": "Space"},
        {"t": "Space"},
    ]
    statement = _emph(*_words("X"), {"t": "Space"}, _emph(*_words("y")))
    ast = {
        "blocks": [
            _div("thm:a", "theorem", [{"t": "Para", "c": [*heading, statement]}])
        ]
    }
    out = PandocImporter().from_json(ast)
    assert ":theorem: {:label: thm-1, :title: Mantel, $K_3$-free}" in out, out
    body = _body(out, "theorem")
    assert "**Theorem" not in body, out
    assert "\n\nX *y*\n" in body + "\n", out
    tree = _parse_without_errors(out)
    (thm,) = tree.traverse(nodeclass=rsm.nodes.Theorem)
    assert thm.label == "thm-1"
    assert thm.title


def test_titled_theorem_without_a_source_label_gets_a_title():
    heading = [
        {"t": "Strong", "c": _words("Lemma", "2")},
        {"t": "Space"},
        {"t": "Str", "c": "(Key)."},
        {"t": "Space"},
        {"t": "Space"},
    ]
    para = {"t": "Para", "c": [*heading, *_words("Z.")]}
    out = PandocImporter().from_json({"blocks": [_div("", "lemma", [para])]})
    assert ":lemma: {:label: thm-1, :title: Key}" in out, out
    assert "Key)." not in _body(out, "lemma"), out
