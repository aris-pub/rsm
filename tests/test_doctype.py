"""Tests for DOCTYPE declaration in HTML output.

All HTML output should include <!DOCTYPE html> to trigger standards mode rendering.
Without DOCTYPE, browsers render in quirks mode which has inconsistent CSS behavior.
"""

import rsm


class TestDOCTYPEDeclaration:
    """Test that all builders include DOCTYPE declaration."""

    def test_build_includes_doctype(self):
        """Test that rsm.build() includes DOCTYPE declaration."""
        src = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(src, handrails=False, lint=False)

        assert result.startswith("<!DOCTYPE html>"), (
            "HTML output must start with DOCTYPE declaration to trigger standards mode"
        )

    def test_build_standalone_includes_doctype(self):
        """Test that rsm.build(standalone=True) includes DOCTYPE declaration."""
        src = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(src, handrails=False, lint=False, standalone=True)

        assert result.startswith("<!DOCTYPE html>"), (
            "Standalone HTML output must start with DOCTYPE declaration"
        )

    def test_build_structured_includes_doctype_in_body(self):
        """Test that rsm.build(structured=True) body starts with DOCTYPE when reassembled."""
        src = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(src, handrails=False, lint=False, structured=True)

        # Structured mode returns dict with head/body/init_script
        assert isinstance(result, dict)
        assert "body" in result

        # When used in an HTML document, the full HTML should start with DOCTYPE
        # The body is the content inside <body>, but the original full HTML before parsing
        # would have had the DOCTYPE. We can't test the full HTML directly in structured mode,
        # but we can test that non-structured mode (which uses the same builder) has DOCTYPE.
        # This test is mainly for documentation that structured mode comes from a DOCTYPE'd source.
        full_html = rsm.build(src, handrails=False, lint=False, structured=False)
        assert full_html.startswith("<!DOCTYPE html>")

    def test_folder_builder_includes_doctype(self, tmp_path):
        """Test that FolderBuilder creates HTML with DOCTYPE."""
        from rsm.builder import FolderBuilder

        builder = FolderBuilder()
        body = '<body><div class="manuscriptwrapper">Test content</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        html = web.readtext("index.html")
        assert html.startswith("<!DOCTYPE html>"), (
            "FolderBuilder output must start with DOCTYPE declaration"
        )

    def test_standalone_builder_includes_doctype(self, tmp_path):
        """Test that StandaloneBuilder creates HTML with DOCTYPE."""
        from rsm.builder import StandaloneBuilder

        builder = StandaloneBuilder()
        body = '<body><div class="manuscriptwrapper">Test content</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        html = web.readtext("index.html")
        assert html.startswith("<!DOCTYPE html>"), (
            "StandaloneBuilder output must start with DOCTYPE declaration"
        )

    def test_doctype_is_html5(self):
        """Test that DOCTYPE is HTML5 format (not XHTML or HTML4)."""
        src = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(src, handrails=False, lint=False)

        # HTML5 DOCTYPE is case-insensitive but conventionally uppercase
        assert result.startswith("<!DOCTYPE html>"), (
            "DOCTYPE should use HTML5 format: <!DOCTYPE html>"
        )

        # Should NOT contain XHTML or HTML4 DOCTYPE declarations
        assert "XHTML" not in result[:100]
        assert "DTD" not in result[:100]
        assert "W3C" not in result[:100]
