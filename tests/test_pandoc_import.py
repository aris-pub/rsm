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
                    [None, [{"t": "Para", "c": [
                        {"t": "Str", "c": "A"}, {"t": "Space"},
                        {"t": "Str", "c": "caption"},
                    ]}]],
                    [{"t": "Plain", "c": [
                        {"t": "Image", "c": [["", [], []], [], ["", ""]]}
                    ]}],
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
            "author": {"t": "MetaList", "c": [
                {"t": "MetaInlines", "c": [
                    {"t": "Str", "c": "Ashish"}, {"t": "Space"},
                    {"t": "Str", "c": "Vaswani"},
                    {"t": "Note", "c": [{"t": "Para", "c": [
                        {"t": "Str", "c": "Equal"}, {"t": "Space"},
                        {"t": "Str", "c": "contribution."},
                    ]}]},
                ]},
                {"t": "MetaInlines", "c": [
                    {"t": "Str", "c": "Noam"}, {"t": "Space"},
                    {"t": "Str", "c": "Shazeer"},
                ]},
            ]},
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
