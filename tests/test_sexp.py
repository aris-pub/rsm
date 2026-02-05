from textwrap import dedent

from rsm.app import ProcessorApp

src = """# My Title

## My Section

foo :cite:foo:: bar baz

### My Subsection

Foobar.

## Another section
{:nonum:}

$2+2=4$

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
    (Manuscript { :numbering: section, :reftext: Manuscript, :title: My Title }
      (Section { :class: ['level-2'], :reftext: Section 1, :title: My Section }
        (Paragraph { :reftext: Paragraph }
          (Text { :reftext: Text })
          (Cite { :class: ['reference'], :label: cite-0, :reftext: Cite })
          (Text { :reftext: Text }))
        (Subsection { :class: ['level-3'], :reftext: Section 1.1, :title: My Subsection }
          (Paragraph { :reftext: Paragraph }
            (Text { :reftext: Text }))))
      (Section { :class: ['level-2'], :nonum: True, :reftext: Section None, :title: Another section }
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
    (Manuscript { :numbering: section, :title: My Title }
      (Section { :class: ['level-2'], :title: My Section }
        (Paragraph {  }
          (Text {  })
          (Cite { :class: ['reference'], :label: cite-0 })
          (Text {  }))
        (Subsection { :class: ['level-3'], :title: My Subsection }
          (Paragraph {  }
            (Text {  }))))
      (Section { :class: ['level-2'], :nonum: True, :title: Another section }
        (Paragraph {  }
          (Math {  }
            (Text {  })))))
    """
    want = dedent(want).strip()
    assert have == want
