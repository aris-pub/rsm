"""Code blocks are numbered and captioned the way figures and tables are (rsm-hbhi).

Every code block is numbered within its section, with its own counter, and the
numbering follows :nonum: and :numbering:. A code block takes a :caption: after
its code, as a table does, and the caption starts with the label "Code Block
2.1.". A code block without a caption has no label, as a figure or table without
a caption has none. A reference reads "Code Block 2.1", or the :reftext:.
"""

import re

import pytest

import rsm


def _transform(src):
    return rsm.transformer.Transformer().transform(rsm.tsparser.TSParser().parse(src))


CODEBLOCKS = r"""# T

{config}{section_one}:table: {{:label: tab1}}
:tbody:
:tr: :td:a:: ::
::
:caption: First table.
::

:codeblock: {{:lang: python, :label: cb1}}
x = 1
:caption: First code.
::

{section_two}:codeblock: {{:label: cb2}}
y = 2
:caption: Second code.
::

```{{:label: cb3}}
z = 3
```

See :ref:tab1::, :ref:cb1::, :ref:cb2:: and :ref:cb3::.
"""


def _render(config="", sections=True, handrails=True):
    src = CODEBLOCKS.format(
        config=config,
        section_one="## One\n\n" if sections else "",
        section_two="## Two\n\n" if sections else "",
    )
    return rsm.render(src, handrails=handrails)


def _labels(html):
    return re.findall(r'<span class="label">([^<]*)</span>', html)


def _references(html):
    return re.findall(r'<a class="reference"[^>]*>([^<]*)</a>', html)


def _config(numbering):
    return ":config: {\n  :numbering: " + numbering + "\n}\n::\n\n"


@pytest.mark.parametrize("handrails", [True, False])
def test_code_blocks_are_numbered_within_their_section(handrails):
    html = _render(handrails=handrails)
    assert _labels(html) == ["Table 1.1. ", "Code Block 1.1. ", "Code Block 2.1. "]
    assert _references(html) == [
        "Table 1.1",
        "Code Block 1.1",
        "Code Block 2.1",
        "Code Block 2.2",
    ]


def test_code_blocks_without_sections_are_numbered_through_the_document():
    html = _render(sections=False)
    assert _labels(html) == ["Table 1. ", "Code Block 1. ", "Code Block 2. "]
    assert _references(html) == [
        "Table 1",
        "Code Block 1",
        "Code Block 2",
        "Code Block 3",
    ]


def test_numbering_document_numbers_code_blocks_through_the_document():
    html = _render(config=_config("document"))
    assert _labels(html) == ["Table 1. ", "Code Block 1. ", "Code Block 2. "]
    assert _references(html) == [
        "Table 1",
        "Code Block 1",
        "Code Block 2",
        "Code Block 3",
    ]


def test_numbering_none_leaves_code_blocks_without_numbers():
    html = _render(config=_config("none"))
    assert _labels(html) == ["Table. ", "Code Block. ", "Code Block. "]
    assert _references(html) == ["Table", "Code Block", "Code Block", "Code Block"]
    assert "None" not in html


def test_nonum_code_block_has_no_number():
    src = """# T

## One

:codeblock: {:label: cb1}
x = 1
::

:codeblock: {:label: cb2, :nonum:}
y = 2
:caption: Unnumbered.
::

:codeblock: {:label: cb3}
z = 3
::

See :ref:cb1::, :ref:cb2:: and :ref:cb3::.
"""
    html = rsm.render(src, handrails=True)
    assert _labels(html) == ["Code Block. "]
    assert _references(html) == ["Code Block 1.1", "Code Block", "Code Block 1.2"]
    assert "None" not in html


def test_code_block_reftext():
    src = """# T

## One

:codeblock: {:label: cb, :reftext: the sorting code}
x = 1
::

See :ref:cb::.
"""
    assert _references(rsm.render(src)) == ["the sorting code"]


def test_code_block_blockname():
    src = """# T

## One

:codeblock: {:label: cb, :blockname: Listing}
x = 1
:caption: A listing.
::

See :ref:cb::.
"""
    html = rsm.render(src, handrails=True)
    assert _labels(html) == ["Listing 1.1. "]
    assert _references(html) == ["Listing 1.1"]
    assert 'data-menu-label="Listing"' in html


def test_code_block_node_numbers():
    src = """# T

## One

:codeblock:
a
::

## Two

:codeblock:
b
::

:codeblock:
c
::
"""
    tree = _transform(src)
    blocks = list(tree.traverse(nodeclass=rsm.nodes.CodeBlock))
    assert [b.full_number for b in blocks] == ["1.1", "2.1", "2.2"]


CAPTIONED = """# T

## One

The function below sorts a list in place.

:codeblock: {:lang: python, :label: code-sort}
def sort(xs):
    return sorted(xs)
:caption: Sorting a list.
::

It takes quadratic time in the worst case.
"""


@pytest.mark.parametrize("handrails", [True, False])
def test_caption_goes_under_the_code_in_a_figure(handrails):
    html = rsm.render(CAPTIONED, handrails=handrails)
    fig = re.search(
        r'<figure id="code-sort" class="codeblock[^"]*".*?</figure>', html, re.S
    )
    assert fig
    fig = fig.group(0)
    # The code comes first, then the caption with its label, then the caption text.
    pre = fig.index("<pre>")
    cap = fig.index("<figcaption")
    assert pre < fig.index("</pre>") < cap
    assert re.search(
        r'<span class="label">Code Block 1.1. </span>Sorting a list.', fig
    ), fig
    # The caption text is not part of the code.
    code = fig[pre : fig.index("</pre>")]
    assert "caption" not in code
    assert "Sorting a list" not in code


def test_captioned_code_block_has_its_menu_on_the_caption():
    """As for a figure, the caption carries the rail and its menu, labelled with
    the kind of block, and the code sits in a bare handrail."""
    html = rsm.render(CAPTIONED, handrails=True)
    fig = re.search(r'<figure id="code-sort".*?</figure>', html, re.S).group(0)
    assert re.search(r'<figcaption class="hr[^"]*" data-menu-label="Code Block"', fig)
    assert '<div class="hr hr-bare">' in fig
    assert fig.count("data-menu-label") == 1


def test_code_block_without_caption_has_no_label():
    src = """# T

## One

:codeblock: {:label: cb}
x = 1
::

See :ref:cb::.
"""
    html = rsm.render(src, handrails=True)
    assert _labels(html) == []
    assert "<figcaption" not in html
    assert _references(html) == ["Code Block 1.1"]
    assert re.search(
        r'<div id="cb" class="codeblock hr[^"]*" data-menu-label="Code Block"', html
    )


def test_captioned_code_text_keeps_its_lines():
    tree = _transform(CAPTIONED)
    block = next(tree.traverse(nodeclass=rsm.nodes.CodeBlock))
    source = next(c for c in block.children if isinstance(c, rsm.nodes.SourceCode))
    assert source.text.strip() == "def sort(xs):\n    return sorted(xs)"
    captions = [c for c in block.children if isinstance(c, rsm.nodes.Caption)]
    assert len(captions) == 1


def test_code_line_that_mentions_caption_is_code():
    """Only a line that starts with :caption: begins the caption."""
    src = """# T

:codeblock:
s = "a :caption: inside a line"
::
"""
    html = rsm.render(src)
    assert "<figcaption" not in html
    assert ":caption: inside a line" in html


def test_captioned_code_block_inside_a_paragraph():
    src = """# T

## One

Some text:
:codeblock: {:label: cb}
x = 1
:caption: In a paragraph.
::
and more text.
"""
    html = rsm.render(src, handrails=True)
    assert _labels(html) == ["Code Block 1.1. "]
    assert "In a paragraph." in html
    assert "and more text." in html
