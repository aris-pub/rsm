"""Tests for standalone HTML output mode.

When standalone=True, the RSM builder produces a single HTML file that can be
opened directly in a browser without requiring a web server. This is achieved by:
1. Using CDN URLs for third-party libraries (jQuery, Tooltipster)
2. Using absolute URLs to the Studio backend for RSM-specific assets
"""

import rsm


class TestStandaloneMode:
    """Test standalone=True produces self-contained HTML."""

    def test_make_accepts_standalone_parameter(self):
        """Test that rsm.build() accepts standalone parameter."""
        source = ":rsm:\n\nHello world.\n\n::"
        # Should not raise
        result = rsm.build(source, handrails=False, lint=False, standalone=True)
        assert "<html" in result.lower()

    def test_standalone_false_uses_absolute_paths(self):
        """Test that standalone=False (default) uses /static/ paths."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=False)

        assert 'href="/static/rsm.css"' in result
        assert 'href="/static/tooltipster.bundle.css"' in result
        assert 'src="/static/jquery-3.6.0.js"' in result
        assert 'src="/static/tooltipster.bundle.js"' in result

    def test_standalone_true_uses_cdn_for_jquery(self):
        """Test that standalone=True uses CDN URL for jQuery."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # Should use jsdelivr CDN for jQuery 3.6.0
        assert "cdn.jsdelivr.net/npm/jquery@3.6.0" in result
        # Should NOT use /static/ path
        assert 'src="/static/jquery-3.6.0.js"' not in result

    def test_standalone_true_uses_cdn_for_tooltipster(self):
        """Test that standalone=True uses CDN URL for Tooltipster."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # Should use CDN for tooltipster CSS and JS
        assert "cdn.jsdelivr.net/npm/tooltipster@4" in result
        # Should NOT use /static/ paths
        assert 'href="/static/tooltipster.bundle.css"' not in result
        assert 'src="/static/tooltipster.bundle.js"' not in result

    def test_standalone_true_uses_studio_url_for_rsm_assets(self):
        """Test that standalone=True uses Studio backend URL for RSM assets."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # RSM CSS should point to Studio backend (or be inlined)
        # The exact URL format will be determined by implementation
        assert 'href="/static/rsm.css"' not in result
        # Should have some form of rsm.css reference (either CDN or inline)
        assert "rsm.css" in result or "<style" in result

    def test_standalone_true_uses_cdn_for_mathjax(self):
        """Test that standalone=True preserves MathJax CDN URL."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # MathJax should still use CDN (it already does)
        # This test ensures we don't accidentally break it
        assert "mathjax" in result.lower() or "cdn.jsdelivr.net" in result

    def test_standalone_true_uses_cdn_for_pseudocode(self):
        """Test that standalone=True preserves pseudocode.js CDN URL."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # Pseudocode CSS should use CDN
        assert "pseudocode" in result.lower()

    def test_standalone_output_is_valid_html(self):
        """Test that standalone output is a complete, valid HTML document."""
        source = ":rsm:\n\n# Test Title\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # Must have all required HTML structure
        assert "<html" in result.lower()
        assert "<head" in result.lower()
        assert "<body" in result.lower()
        assert "</html>" in result.lower()
        assert "<title>" in result.lower()

    def test_standalone_default_is_false(self):
        """Test that standalone defaults to False for backwards compatibility."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False)

        # Default behavior should use /static/ paths
        assert 'href="/static/rsm.css"' in result


class TestStandaloneBuilder:
    """Test the StandaloneBuilder class directly."""

    def test_standalone_builder_exists(self):
        """Test that StandaloneBuilder class exists."""
        from rsm.builder import StandaloneBuilder

        assert StandaloneBuilder is not None

    def test_standalone_builder_inherits_from_html_builder(self):
        """Test that StandaloneBuilder inherits from HTMLBuilder."""
        from rsm.builder import HTMLBuilder, StandaloneBuilder

        assert issubclass(StandaloneBuilder, HTMLBuilder)

    def test_standalone_builder_produces_single_file(self):
        """Test that StandaloneBuilder produces exactly one file."""
        from rsm.builder import StandaloneBuilder

        standalone_builder = StandaloneBuilder()
        body = '<body><div class="manuscript">Test</div></body>'
        web = standalone_builder.build(body)

        # Should only create index.html, no static directory
        files = list(web.listdir("/"))
        assert "index.html" in files
        assert "static" not in files


class TestStandaloneCDNVersions:
    """Test that CDN URLs use correct library versions."""

    def test_jquery_version_is_3_6_0(self):
        """Test jQuery CDN uses exact version 3.6.0 to match bundled version."""
        source = ":rsm:\n\nTest.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # Must be exact version, not "latest"
        assert "jquery@3.6.0" in result

    def test_tooltipster_version_matches_bundled(self):
        """Test Tooltipster CDN uses version compatible with bundled version."""
        source = ":rsm:\n\nTest.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # Tooltipster 4.x series
        assert "tooltipster@4" in result


class TestCustomCSS:
    """Test custom CSS support in builders."""

    def test_folder_builder_with_custom_css(self, tmp_path):
        """Test FolderBuilder copies custom CSS to static/ folder."""
        from rsm.builder import FolderBuilder

        # Create custom CSS file
        custom_css_file = tmp_path / "custom.css"
        custom_css_content = ".mytype { color: red; }"
        custom_css_file.write_text(custom_css_content)

        # Create builder with custom_css
        builder = FolderBuilder(custom_css=str(custom_css_file))
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        # Should copy custom.css to static/ folder
        assert web.exists("static/custom.css")
        custom_css_in_static = web.readtext("static/custom.css")
        assert custom_css_content in custom_css_in_static

        # Should add link tag in HTML
        html = web.readtext("index.html")
        assert '<link rel="stylesheet" type="text/css" href="/static/custom.css"' in html

    def test_standalone_builder_with_custom_css(self, tmp_path):
        """Test StandaloneBuilder inlines custom CSS in <style> tag."""
        from rsm.builder import StandaloneBuilder

        # Create custom CSS file
        custom_css_file = tmp_path / "custom.css"
        custom_css_content = ".mytype { color: blue; }"
        custom_css_file.write_text(custom_css_content)

        # Create builder with custom_css
        builder = StandaloneBuilder(custom_css=str(custom_css_file))
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        # Should inline custom CSS in <style> tag
        html = web.readtext("index.html")
        assert "<style>" in html
        assert custom_css_content in html

        # Should NOT create static/ folder
        files = list(web.listdir("/"))
        assert "static" not in files

    def test_builder_without_custom_css(self, tmp_path):
        """Test builders work normally when custom_css=None."""
        from rsm.builder import FolderBuilder

        # Create builder WITHOUT custom_css
        builder = FolderBuilder()
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        # Should work normally
        assert web.exists("index.html")
        html = web.readtext("index.html")
        assert "Test" in html

        # Should NOT have custom.css link
        assert "custom.css" not in html

    def test_builder_custom_css_nonexistent_file(self, tmp_path):
        """Test builder handles nonexistent custom CSS gracefully."""
        from rsm.builder import FolderBuilder

        # Create builder with nonexistent CSS file
        builder = FolderBuilder(custom_css="nonexistent.css")
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        # Should still build successfully
        assert web.exists("index.html")

        # Should NOT have custom.css in static/
        assert not web.exists("static/nonexistent.css")
