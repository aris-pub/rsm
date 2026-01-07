from textwrap import dedent

from rsm.app import ProcessorApp

src = """:rsm:
:title: My Title

## My Section

foo :cite:foo:: bar baz

### My Subsection

Foobar.

## Another section
:nonum:

$2+2=4$

::
"""


def test_no_meta():
    app = ProcessorApp(plain=src)
    app.run()
    tree = app.transformer.tree
    have = tree.sexp(meta=False).strip()
    want = """
    (Manuscript
      (Section
        (Paragraph
          (Text)
          (Cite)
          (Text))
        (Subsection
          (Paragraph
            (Text))))
      (Section
        (Paragraph
          (Math
            (Text)))))
    """
    want = dedent(want).strip()
    assert have == want


def test_with_meta():
    app = ProcessorApp(plain=src)
    app.run()
    tree = app.transformer.tree
    have = tree.sexp(meta=True).strip()
    want = """
    (Manuscript { :reftext: Manuscript, :title: My Title }
      (Section { :reftext: Section 1, :title: My Section, :types: ['level-2'] }
        (Paragraph { :reftext: Paragraph }
          (Text { :reftext: Text })
          (Cite { :label: cite-0, :reftext: Cite, :types: ['reference'] })
          (Text { :reftext: Text }))
        (Subsection { :reftext: Section 1.1, :title: My Subsection, :types: ['level-3'] }
          (Paragraph { :reftext: Paragraph }
            (Text { :reftext: Text }))))
      (Section { :nonum: True, :reftext: Section None, :title: Another section, :types: ['level-2'] }
        (Paragraph { :reftext: Paragraph }
          (Math { :reftext: Math }
            (Text { :reftext: Text })))))
    """
    want = dedent(want).strip()
    assert have == want


def test_with_meta_ignore_reftext():
    app = ProcessorApp(plain=src)
    app.run()
    tree = app.transformer.tree
    have = tree.sexp(meta=True, ignore_meta_keys=["reftext"]).strip()
    want = """
    (Manuscript { :title: My Title }
      (Section { :title: My Section, :types: ['level-2'] }
        (Paragraph {  }
          (Text {  })
          (Cite { :label: cite-0, :types: ['reference'] })
          (Text {  }))
        (Subsection { :title: My Subsection, :types: ['level-3'] }
          (Paragraph {  }
            (Text {  }))))
      (Section { :nonum: True, :title: Another section, :types: ['level-2'] }
        (Paragraph {  }
          (Math {  }
            (Text {  })))))
    """
    want = dedent(want).strip()
    assert have == want
