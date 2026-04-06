"""Codeblock inside a paragraph must have hr-offset, same as mathblock."""

import rsm


def test_codeblock_in_paragraph_has_hr_offset():
    html = rsm.render(
        "## Section\n\nSome text:\n\n:codeblock: {:lang: python}\nx = 1\n::\n",
        handrails=True,
    )
    assert "codeblock hr hr-hidden hr-offset" in html


def test_mathblock_in_paragraph_has_hr_offset():
    html = rsm.render(
        "## Section\n\nSome text:\n\n:mathblock:\nx^2\n::\n",
        handrails=True,
    )
    assert "mathblock hr hr-hidden hr-offset" in html
