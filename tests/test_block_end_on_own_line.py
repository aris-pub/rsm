""":codeblock: and :mathblock: end only at a :: on a line of its own (rsm-ytxt).

A :: inside a line of code or math, as in std::vector or a::b, is content.
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
