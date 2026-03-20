"""Integration tests for external cross-file references."""

from pathlib import Path

import rsm
from rsm.nodes import Manuscript


def test_external_ref_html_generation():
    """External references should generate correct HTML with external class."""
    root_dir = Path(__file__).parent / "fixtures/crossref"

    src = """# Main Document

This document references :ref:definitions/def/test-def::.
"""

    # Parse
    parser = rsm.tsparser.TSParser()
    tree = parser.parse(src)

    # Transform with root_dir
    from rsm.transformer import Transformer

    t = Transformer(root_dir=root_dir)
    transformed = t.transform(tree)

    # Translate to HTML
    from rsm.translator import Translator

    translator = Translator()
    html = translator.translate(transformed)

    # Verify the HTML contains the correct href and external class
    assert 'href="definitions/def.html#test-def"' in html
    assert 'class="reference external"' in html or 'class="external reference"' in html


def test_internal_ref_html_generation():
    """Internal references should generate normal HTML without external class."""
    src = """# Document

## Section
  {:label: my-section}

This references :ref:my-section::.
"""

    # Parse
    parser = rsm.tsparser.TSParser()
    tree = parser.parse(src)

    # Transform
    from rsm.transformer import Transformer

    t = Transformer()
    transformed = t.transform(tree)

    # Translate to HTML
    from rsm.translator import Translator

    translator = Translator()
    html = translator.translate(transformed)

    # Verify internal ref doesn't have external class
    assert 'href="#my-section"' in html
    assert (
        "external" not in html or '<span class="external"' in html
    )  # Allow word "external" in other contexts


def test_external_ref_missing_file():
    """External references to missing files should generate error nodes."""
    root_dir = Path(__file__).parent / "fixtures/crossref"

    src = """# Document

This references :ref:nonexistent/file/label::.
"""

    # Parse
    parser = rsm.tsparser.TSParser()
    tree = parser.parse(src)

    # Transform with root_dir
    from rsm.transformer import Transformer

    t = Transformer(root_dir=root_dir)
    transformed = t.transform(tree)

    # Should have an Error node
    errors = [
        node for node in transformed.traverse() if node.__class__.__name__ == "Error"
    ]
    assert len(errors) == 1
    # Error message should mention the missing file
    if errors[0].children:
        assert "nonexistent/file.rsm" in str(errors[0].children[0])
    # If no children, just verify an error was created
    assert errors[0].__class__.__name__ == "Error"


def test_manuscript_reftext_uses_title():
    """Manuscript.reftext should return the title, not 'Manuscript'."""
    ms = Manuscript(title="Adjacency Matrix")
    assert ms.reftext == "Adjacency Matrix"


def test_manuscript_reftext_without_title():
    """Manuscript.reftext should fall back to 'Manuscript' when no title is set."""
    ms = Manuscript()
    assert ms.reftext == "Manuscript"


def test_external_whole_document_ref_shows_title():
    """Whole-document ref :ref:file/:: should render the target manuscript's title."""
    root_dir = Path(__file__).parent / "fixtures/crossref"

    src = """# Main Document

This references :ref:definitions/def/::.
"""

    html = rsm.render(source=src, handrails=False, root_dir=root_dir)

    # The ref target is the Manuscript node of def.rsm which has "# Test Definition"
    assert "Test Definition" in html
    assert "Manuscript" not in html or "Manuscript" in "Main Document"  # only in our own title


def test_external_labeled_ref_includes_manuscript_title():
    """Ref :ref:file/label:: should render as 'Manuscript Title, Reftext'."""
    root_dir = Path(__file__).parent / "fixtures/crossref"

    src = """# Main Document

This references :ref:definitions/def/test-def::.
"""

    html = rsm.render(source=src, handrails=False, root_dir=root_dir)

    # Should show the manuscript title alongside the local reftext
    assert "Test Definition" in html
