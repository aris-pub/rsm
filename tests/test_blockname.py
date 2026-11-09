""":blockname: sets the name a theorem-like block is called by, in place of its type's name.

    :remark: {
      :blockname: Hint
    }

The header reads "Hint 1.", a :ref: to it reads "Hint 1", and so do the handrail
menu and the proof views. Numbering, CSS classes and
everything else a theme hooks onto by type are unchanged. Blocks that are not
theorem-like do not accept the key, and treat it like any other key they do not
accept.
"""

import logging
import re
import shutil
from textwrap import dedent

import pytest

import rsm
import rsm.nodes as nodes
from rsm import app
from rsm.app import ParserApp, pandoc_export
from rsm.pandoc import PandocTranslator


def _src(meta: str = ":blockname: Hint", body: str = "", kind: str = "remark") -> str:
    return dedent(
        f"""\
        # Doc

        ## Sec

        :{kind}: {{
          :label: hint
          {meta}
        }}

          What does inversion make of two tangent circles?

        ::

        {body}
        """
    )


def _tree(src: str) -> nodes.Manuscript:
    a = app.ProcessorApp(plain=src)
    a.run()
    return a.translator.tree


def _remark(tree: nodes.Manuscript) -> nodes.Theorem:
    return next(iter(tree.traverse(nodeclass=nodes.Remark)))


def test_parses_into_the_node():
    assert _remark(_tree(_src())).blockname == "Hint"


def test_default_is_empty():
    assert nodes.Remark().blockname == ""


def test_header_uses_blockname():
    html = rsm.render(_src())
    assert '<span class="span label">Hint 1.1.</span>' in html
    assert "Remark" not in html


def test_header_without_number():
    html = rsm.render(_src(":blockname: Hint\n  :nonum:"))
    assert '<span class="span label">Hint.</span>' in html


def test_header_with_title():
    html = rsm.render(_src(":blockname: Hint\n  :title: Tangent circles"))
    assert '<span class="span label">Hint 1.1: </span>' in html
    assert '<span class="span desc">Tangent circles</span>' in html


@pytest.mark.parametrize("name", ["hint", "hINT", "Key idea", "FAQ"])
def test_header_keeps_capitalization(name):
    html = rsm.render(_src(f":blockname: {name}\n  :nonum:"))
    assert f'<span class="span label">{name}.</span>' in html


def test_reftext():
    assert _remark(_tree(_src())).reftext == "Hint 1.1"


def test_reftext_without_number():
    assert _remark(_tree(_src(":blockname: Hint\n  :nonum:"))).reftext == "Hint"


def test_reftext_node_level():
    assert nodes.Remark(blockname="Hint").reftext == "Hint"
    assert nodes.Remark().reftext == "Remark"


def test_explicit_reftext_still_wins():
    tree = _tree(_src(":blockname: Hint\n  :reftext: The hint"))
    assert _remark(tree).reftext == "The hint"


def test_ref_reads_blockname():
    html = rsm.render(_src(body="See :ref:hint::."))
    assert ">Hint 1.1</a>" in html


def test_ref_without_number_reads_blockname():
    html = rsm.render(_src(":blockname: Hint\n  :nonum:", body="See :ref:hint::."))
    assert ">Hint</a>" in html


def test_handrail_menu_label():
    html = rsm.render(_src(), handrails=True)
    assert 'data-menu-label="Hint 1.1"' in html
    assert 'data-menu-label="Remark' not in html


def test_no_fold_label():
    html = rsm.render(_src(":blockname: Hint\n  :collapsed:"), handrails=True)
    assert "data-fold-label" not in html


def test_numbering_unchanged():
    src = dedent(
        """\
        # Doc

        ## Sec

        :theorem: {:label: a}
          A.
        ::

        :remark: {:label: b, :blockname: Hint}
          B.
        ::

        :remark: {:label: c}
          C.
        ::
        """
    )
    tree = _tree(src)
    thm, hint, rem = tree.traverse(nodeclass=nodes.Theorem)
    assert (thm.reftext, hint.reftext, rem.reftext) == (
        "Theorem 1.1",
        "Hint 1.2",
        "Remark 1.3",
    )


def test_css_classes_unchanged():
    html = rsm.render(_src())
    assert re.search(r'<div id="hint" class="remark theorem"', html)


def test_proof_of_lead_and_tree_root():
    src = _src(
        kind="theorem",
        body=dedent(
            """\
            :proof: {:of: hint}

              :step: It is so. ::

            ::
            """
        ),
    )
    tree = _tree(src)
    proof = next(iter(tree.traverse(nodeclass=nodes.Proof)))
    assert proof.tree_root_title == "Hint 1.1"
    html = rsm.render(src, handrails=True)
    assert ">Hint 1.1</a>" in html


@pytest.mark.parametrize("kind", ["theorem", "lemma", "definition", "example", "remark"])
def test_any_theorem_like_block(kind):
    html = rsm.render(_src(kind=kind))
    assert '<span class="span label">Hint 1.1.</span>' in html


def _pandoc_div(src: str) -> dict:
    tree = ParserApp(plain=src).run()
    blocks = PandocTranslator().translate(tree)["blocks"]
    return next(b for b in blocks if b["t"] == "Div")


def test_pandoc_export_carries_blockname():
    div = _pandoc_div(_src())
    _, classes, kvs = div["c"][0]
    assert "remark" in classes
    assert dict(kvs).get("blockname") == "Hint"


def test_pandoc_export_without_blockname():
    _, _, kvs = _pandoc_div(_src(meta=""))["c"][0]
    assert "blockname" not in dict(kvs)


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")
def test_typst_export_heading_uses_blockname():
    out = pandoc_export(source=_src(), to_format="typst")
    assert "#strong[Hint]" in out
    assert "Remark" not in out


# Blocks that are not theorem-like do not accept :blockname:. RSM does not check meta
# keys against a block's accepted keys: it neither errors nor warns, and the key has
# no effect on the output. :blockname: behaves the same way as any other such key.

PARAGRAPH = """\
# Doc

## Sec

:paragraph: {{:label: p{meta}}} Some text.

See :ref:p::.
"""

SECTION = """\
# Doc

## Sec {{
  :label: s{meta}
}}

Some text. See :ref:s::.
"""


@pytest.mark.parametrize("template", [PARAGRAPH, SECTION], ids=["paragraph", "section"])
@pytest.mark.parametrize(
    "meta",
    [", :blockname: Hint", ", :eyebrow: Hint", ", :of: Hint"],
    ids=["blockname", "eyebrow", "of"],
)
def test_not_accepted_outside_theorems(template, meta, caplog):
    if template is SECTION:
        meta = meta.replace(", ", "\n  ")
    with caplog.at_level(logging.WARNING, logger="RSM"):
        html = rsm.render(template.format(meta=meta), handrails=True)
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
    assert html == rsm.render(template.format(meta=""), handrails=True)
    assert "Hint" not in html
