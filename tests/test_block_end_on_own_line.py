"""Blocks whose content is taken as is end only at a :: on a line of its own (rsm-ytxt).

These are :codeblock:, :mathblock:, :algorithm:, :htmlblock: and :notation:. A ::
inside a line of their content, as in std::vector or a::b, is content.
"""

import rsm
from rsm import nodes


def _manuscript(src):
    return rsm.transformer.Transformer().transform(rsm.tsparser.TSParser().parse(src))


def _of_type(manuscript, cls):
    return [n for n in manuscript.traverse() if isinstance(n, cls)]


def _code(block):
    return "".join(n.text for n in block.traverse() if isinstance(n, nodes.SourceCode))


def _paragraph_text(manuscript):
    return [
        "".join(t.text for t in p.traverse() if type(t) is nodes.Text).strip()
        for p in _of_type(manuscript, nodes.Paragraph)
        if not isinstance(p, nodes.Caption)
    ]


def test_codeblock_keeps_double_colon_inside_a_line():
    m = _manuscript(
        ":codeblock: {:lang: cpp}\n"
        "  std::vector<int> v;\n"
        "  v.push_back(1);\n"
        "::\n"
        "\n"
        "After the code.\n"
    )
    assert not _of_type(m, nodes.Error)
    (block,) = _of_type(m, nodes.CodeBlock)
    code = _code(block)
    assert "std::vector<int> v;" in code
    assert "v.push_back(1);" in code
    assert _paragraph_text(m) == ["After the code."]


def test_codeblock_keeps_a_line_that_starts_with_double_colon():
    m = _manuscript(":codeblock:\n  f\n    :: Int -> Int\n  f x = x\n::\n")
    assert not _of_type(m, nodes.Error)
    (block,) = _of_type(m, nodes.CodeBlock)
    assert ":: Int -> Int" in _code(block)
    assert "f x = x" in _code(block)


def test_codeblock_with_caption_and_double_colon():
    m = _manuscript(
        ":codeblock: {:label: cb}\n"
        "  std::vector<int> v;\n"
        "  :caption: A C++ vector.\n"
        "::\n"
    )
    assert not _of_type(m, nodes.Error)
    (block,) = _of_type(m, nodes.CodeBlock)
    assert "std::vector<int> v;" in _code(block)
    (caption,) = _of_type(m, nodes.Caption)
    assert "A C++ vector." in "".join(
        t.text for t in caption.traverse() if isinstance(t, nodes.Text)
    )


def test_codeblock_closing_with_spaces_before_it():
    m = _manuscript(":codeblock:\n  x = a::b\n   ::\nAfter the code.\n")
    assert not _of_type(m, nodes.Error)
    (block,) = _of_type(m, nodes.CodeBlock)
    assert _code(block).strip() == "x = a::b"
    assert _paragraph_text(m) == ["After the code."]


def test_codeblock_closing_with_spaces_after_it():
    m = _manuscript(":codeblock:\n  x = a::b\n::  \n")
    assert not _of_type(m, nodes.Error)
    (block,) = _of_type(m, nodes.CodeBlock)
    assert _code(block).strip() == "x = a::b"


def test_codeblock_closing_at_end_of_file():
    m = _manuscript(":codeblock:\n  std::string s;\n::")
    assert not _of_type(m, nodes.Error)
    (block,) = _of_type(m, nodes.CodeBlock)
    assert _code(block).strip() == "std::string s;"


def test_codeblock_normal_forms():
    m = _manuscript(
        ":codeblock:\n  x = 1\n::\n\n"
        "```\nstd::vector<int> w;\n```\n\n"
        ":codeblock:\n  y = 2\n  :caption: Second.\n::\n"
    )
    assert not _of_type(m, nodes.Error)
    blocks = _of_type(m, nodes.CodeBlock)
    assert [_code(b).strip() for b in blocks] == ["x = 1", "std::vector<int> w;", "y = 2"]


def test_mathblock_keeps_double_colon_inside_a_line():
    src = ":mathblock:\n  a::b = c\n::\n\nAfter the math.\n"
    m = _manuscript(src)
    assert not _of_type(m, nodes.Error)
    assert len(_of_type(m, nodes.MathBlock)) == 1
    assert _paragraph_text(m) == ["After the math."]
    assert "a::b = c" in rsm.render(src, handrails=False)


def test_mathblock_closing_with_spaces_before_it():
    html = rsm.render(
        ":mathblock: {:label: eq}\n  f :: A \\to B\n   ::\nAfter the math.\n",
        handrails=False,
    )
    assert "CST error" not in html
    assert "f :: A \\to B" in html
    assert "After the math." in html


def test_mathblock_normal_forms():
    m = _manuscript(":mathblock:\n  2+2=4\n::\n\n$$\na::b\n$$\n")
    assert not _of_type(m, nodes.Error)
    assert len(_of_type(m, nodes.MathBlock)) == 2


def test_algorithm_keeps_double_colon_inside_a_line():
    m = _manuscript(
        ":algorithm:\n"
        "\\begin{algorithm}\n"
        "\\State $xs \\gets x::xs$\n"
        "\\end{algorithm}\n"
        "  ::\n"
        "\n"
        "After.\n"
    )
    assert not _of_type(m, nodes.Error)
    (block,) = _of_type(m, nodes.Algorithm)
    text = "".join(n.text for n in block.traverse() if isinstance(n, nodes.Text))
    assert "x::xs" in text
    assert text.rstrip().endswith("\\end{algorithm}")
    assert _paragraph_text(m) == ["After."]


def test_htmlblock_keeps_double_colon_inside_a_line():
    m = _manuscript(
        ":htmlblock:\n"
        '<style>p::before { content: "a::b"; }</style>\n'
        "<p>x</p>\n"
        "::\n"
        "\n"
        "After.\n"
    )
    assert not _of_type(m, nodes.Error)
    (block,) = _of_type(m, nodes.HtmlBlock)
    assert 'p::before { content: "a::b"; }' in block.html
    assert "<p>x</p>" in block.html
    assert _paragraph_text(m) == ["After."]


def test_htmlblock_in_a_figure_keeps_double_colon():
    m = _manuscript(
        ':figure:\n\n  :htmlblock:\n  <style>p::after { content: "x"; }</style>\n  ::\n\n::\n'
    )
    assert not _of_type(m, nodes.Error)
    (figure,) = _of_type(m, nodes.Figure)
    assert figure.htmlblock.html.strip() == '<style>p::after { content: "x"; }</style>'


def test_notation_keeps_double_colon_inside_a_line():
    m = _manuscript(
        "# T\n\n"
        ":notation:\n"
        "  \\cons $a::b$ list with head a and tail b\n"
        "  \\eig $\\lambda$ general eigenvalue\n"
        "::\n"
    )
    assert not _of_type(m, nodes.Error)
    (block,) = _of_type(m, nodes.Notation)
    assert block.entries == [
        {"macro": "\\cons", "default": "a::b", "label": "list with head a and tail b"},
        {"macro": "\\eig", "default": "\\lambda", "label": "general eigenvalue"},
    ]


def test_inline_tags_still_end_at_the_first_double_colon():
    m = _manuscript("Run :code: x = 1 :: and :math: y :: now.\n")
    assert not _of_type(m, nodes.Error)
    (code,) = _of_type(m, nodes.Code)
    (math,) = _of_type(m, nodes.Math)
    assert _code(code).strip() == "x = 1"
    assert "".join(t.text for t in math.traverse() if type(t) is nodes.Text).strip() == "y"
    assert _paragraph_text(m) == ["Run  and y now."]
