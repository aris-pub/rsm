"""A math block, code block or algorithm that stands on its own is put in a
paragraph that holds only it, as a list is. The page looks as it did before the
wrapping: the paragraph adds no tag, no handrail and no node id of its own."""

import logging
from pathlib import Path

import pytest

import rsm
from rsm import nodes, transformer
from rsm.transformer import Transformer
from rsm.tsparser import TSParser

PROBE = """\
# Probe

## Display math

A paragraph before the equation.

$$ {:label: eq-a}
a^2 + b^2 = c^2
$$

A paragraph after the equation, which refers to :ref:eq-a::.

$$ {:nonum:}
x = y
$$

## Code and algorithm

Text before the code.

:codeblock: {:label: code-a}
def f(x):
    return x
::

:codeblock: {:label: code-b}
  print(1)
  :caption: A captioned code block.
::

Text before the algorithm.

:algorithm: {:label: alg-a}
\\begin{algorithm}
\\caption{Euclid}
\\begin{algorithmic}
\\PROCEDURE{Euclid}{$a, b$}
    \\RETURN $a$
\\ENDPROCEDURE
\\end{algorithmic}
\\end{algorithm}
::

See :ref:code-a:: and :ref:alg-a::.

## In a theorem

:theorem: {:label: thm-a}
Every $x$ satisfies

$$ {:label: eq-b}
x^2 \\geq 0.
$$

::

:proof:

:step: {:label: st-1}
$$ {:label: eq-s}
x \\cdot x = x^2.
$$
::

:step: The rest, by :ref:eq-b:: and :ref:eq-s::.
::

::
"""

KINDS = (nodes.MathBlock, nodes.CodeBlock, nodes.Algorithm)


def _tree(src: str) -> nodes.Manuscript:
    return Transformer().transform(TSParser().parse(src))


def test_standalone_blocks_are_wrapped():
    tree = _tree(PROBE)
    blocks = [n for n in tree.traverse() if isinstance(n, KINDS)]
    assert {type(b) for b in blocks} == set(KINDS)
    for block in blocks:
        par = block.parent
        # A step is a paragraph. The proof steps later move the start of a step
        # into its Statement, which holds the text of the step.
        assert isinstance(par, (nodes.Paragraph, nodes.Statement)), block
        if type(par) is nodes.Paragraph and par.wraps_block:
            assert list(par.children) == [block]


def test_block_inside_a_paragraph_is_not_wrapped_again():
    tree = _tree("# T\n\nText before\n$$\na\n$$\ntext after.\n")
    (block,) = tree.traverse(nodeclass=nodes.MathBlock)
    assert not block.parent.wraps_block
    assert len(block.parent.children) == 3


def test_preamble_is_not_wrapped():
    tree = _tree("# T\n\n$$ {:preamble:}\n\\newcommand{\\R}{\\mathbb{R}}\n$$\n")
    (block,) = tree.traverse(nodeclass=nodes.MathBlock)
    assert not isinstance(block.parent, nodes.Paragraph)


def test_wrapper_paragraph_has_no_node_id():
    tree = _tree("# T\n\n$$\na\n$$\n")
    (block,) = tree.traverse(nodeclass=nodes.MathBlock)
    assert block.parent.nodeid is None
    assert block.nodeid is not None


def _lists_only(self):
    self._wrap_standalone((nodes.Itemize, nodes.Enumerate))


@pytest.mark.parametrize("handrails", [True, False])
def test_page_is_the_same_as_without_wrapping(monkeypatch, handrails):
    wrapped = rsm.render(PROBE, handrails=handrails)
    monkeypatch.setattr(transformer.Transformer, "wrap_standalone_blocks", _lists_only)
    unwrapped = rsm.render(PROBE, handrails=handrails)
    assert wrapped == unwrapped


def test_check_does_not_flag_a_standalone_block(tmp_path: Path, caplog):
    path = tmp_path / "doc.rsm"
    path.write_text(PROBE)
    caplog.set_level(logging.DEBUG, logger="RSM")
    rsm.lint(path=str(path))
    assert not [r for r in caplog.records if "Paragraph" in r.getMessage()]
