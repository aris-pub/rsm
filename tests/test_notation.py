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
