"""Tests for the :notation: block (reader-rebindable notation macros)."""

import re

import rsm
import rsm.nodes as nodes
from rsm import app

SRC = """\
# T

:notation:
  \\eig $\\lambda$ general eigenvalue
  \\specrad $\\lambda_1$ spectral radius
  \\field $\\mathbb{R}$ scalar field
::
"""


def _notation(src):
    a = app.ProcessorApp(plain=src)
    a.run()
    return next(iter(a.transformer.tree.traverse(nodeclass=nodes.Notation)))


def test_entries_parsed():
    assert _notation(SRC).entries == [
        {"macro": "\\eig", "default": "\\lambda", "label": "general eigenvalue"},
        {"macro": "\\specrad", "default": "\\lambda_1", "label": "spectral radius"},
        {"macro": "\\field", "default": "\\mathbb{R}", "label": "scalar field"},
    ]


def test_default_with_braces():
    # the $...$ delimiters give the default a hard boundary, so braces are fine
    n = _notation("# T\n\n:notation:\n  \\field $\\mathbb{R}$ the scalars\n::\n")
    assert n.entries[0]["default"] == "\\mathbb{R}"


def test_label_is_multiword():
    n = _notation("# T\n\n:notation:\n  \\eig $\\lambda$ a general eigenvalue\n::\n")
    assert n.entries[0]["label"] == "a general eigenvalue"


def test_malformed_line_skipped():
    # a line without a $...$ default is not a valid entry; it is dropped
    n = _notation("# T\n\n:notation:\n  \\eig $\\lambda$ ok\n  garbage line\n::\n")
    assert [e["macro"] for e in n.entries] == ["\\eig"]


def test_data_emitted_to_frontend():
    html = rsm.render(SRC, handrails=False)
    m = re.search(r'class="rsm-notation">(.*?)</script>', html)
    assert m, "notation data script not emitted"
    assert '"macro": "\\\\eig"' in m.group(1)
    assert '"label": "spectral radius"' in m.group(1)


def test_raw_lines_not_rendered():
    # the author's raw lines must not appear as literal text in the output
    html = rsm.render(SRC, handrails=False)
    assert "\\eig $\\lambda$ general eigenvalue" not in html


def test_absent_when_no_block():
    html = rsm.render("# T\n\nNo notation here.\n", handrails=False)
    assert "rsm-notation" not in html


DEFAULTS_SRC = """\
# T

:notation:
  \\emb $F$ the embedding
  \\dst $D$ the distortion
  \\rad $\\rho_{#1}$ the radius at scale j
::

The map $\\emb(x)$ has distortion $\\dst(n)$ at radius $\\rad{j-1}$.

$$
\\emb(x) \\le \\dst(n) \\rad{j-1}
$$
"""


def _page_text(html):
    body = html[html.find("<body") :]
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    return re.sub(r"<[^>]+>", "", body)


def test_nojs_math_source_uses_defaults():
    for handrails in (False, True):
        text = _page_text(rsm.render(DEFAULTS_SRC, handrails=handrails))
        for name in ("\\emb", "\\dst", "\\rad"):
            assert name not in text, (handrails, name)
        assert "\\(F(x)\\)" in text
        assert "\\(D(n)\\)" in text
        assert "\\(\\rho_{j-1}\\)" in text
        assert "F(x) \\le D(n) \\rho_{j-1}" in text


def test_js_source_keeps_macro_calls():
    for handrails in (False, True):
        html = rsm.render(DEFAULTS_SRC, handrails=handrails)
        latex = re.findall(r'data-latex="([^"]*)"', html)
        assert "\\emb(x)" in latex
        assert "\\rad{j-1}" in latex
        assert "\\emb(x) \\le \\dst(n) \\rad{j-1}" in latex


def test_math_without_notation_has_no_data_latex():
    html = rsm.render("# T\n\nPlain $x+1$.\n", handrails=False)
    assert "data-latex" not in html


def _expand(latex, macros):
    from rsm.translator import expand_notation

    return expand_notation(latex, macros)


def test_expand_parameters():
    m = {"\\rad": "\\rho_{#1}", "\\pair": "(#1, #2)"}
    assert _expand("\\rad{j-1}", m) == "\\rho_{j-1}"
    assert _expand("\\pair{a}{b}", m) == "(a, b)"
    # TeX reads an unbraced argument as one token
    assert _expand("\\rad j", m) == "\\rho_{j}"
    assert _expand("\\rad\\alpha", m) == "\\rho_{\\alpha}"


def test_expand_matches_whole_control_word():
    m = {"\\emb": "F"}
    assert _expand("\\embed + \\emb", m) == "\\embed + F"
    # \\ is a line break, so the letters after it are not a macro call
    assert _expand("a \\\\emb", m) == "a \\\\emb"


def test_expand_keeps_space_after_macro():
    # removing the space would turn "\eig x" into the unknown "\lambdax"
    assert _expand("\\eig x", {"\\eig": "\\lambda"}) == "\\lambda x"


def test_expand_default_that_uses_another_macro():
    m = {"\\emb": "F", "\\embsq": "\\emb^2"}
    assert _expand("\\embsq", m) == "F^2"


def test_expand_leaves_call_with_missing_argument():
    m = {"\\rad": "\\rho_{#1}", "\\pair": "(#1, #2)"}
    assert _expand("\\rad", m) == "\\rad"
    assert _expand("{\\rad}", m) == "{\\rad}"
    assert _expand("\\pair{a}", m) == "\\pair{a}"


def test_expand_stops_on_self_reference():
    # each level adds one "'", so the count shows where expansion stopped
    out = _expand("\\emb", {"\\emb": "\\emb'"})
    assert out == "\\emb" + "'" * 33


def test_later_duplicate_declaration_wins():
    src = (
        "# T\n\n:notation:\n  \\emb $F$ first\n::\n\n"
        ":notation:\n  \\emb $G$ second\n::\n\nSee $\\emb(x)$.\n"
    )
    text = _page_text(rsm.render(src, handrails=False))
    assert "\\(G(x)\\)" in text


def test_theorem_title_math_uses_the_notation():
    src = (
        "# T\n\n:notation:\n  \\emb $F$ the embedding\n::\n\n"
        ":theorem: {:title: On $\\emb(x)$}\n  Body.\n::\n"
    )
    for handrails in (False, True):
        html = rsm.render(src, handrails=handrails)
        assert "\\emb" not in _page_text(html), handrails
        assert "\\(F(x)\\)" in _page_text(html), handrails
        assert re.findall(r'data-latex="([^"]*)"', html) == ["\\emb(x)"], handrails
