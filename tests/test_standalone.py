"""Tests for standalone HTML output mode.

When standalone=True, the RSM builder produces a single self-contained HTML file
that can be opened directly in a browser with no web server and no network. Every
third-party library (temml, jQuery, Tooltipster, pseudocode) and the RSM bundle
are inlined from pinned copies vendored under static/, and the math font is
embedded as a data URI (see rsm-nyg). MathJax is the one exception: it stays a
CDN fallback in the bundle as dead code, unreachable once temml is always present.
"""

import re
from pathlib import Path

import rsm


def loaded_external_urls(html: str) -> list[str]:
    """URLs the page would actually fetch: link/script tags with an http(s) src.

    This ignores http(s) strings that merely sit inside inlined JS/CSS (e.g. the
    dead MathJax fallback URL), which never cause a network request.
    """
    return re.findall(r'<(?:link|script)\b[^>]*\b(?:href|src)="(https?://[^"]+)"', html)


BUNDLE = Path(__file__).parent.parent / "rsm" / "static" / "rsm-standalone.js"


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

        assert 'href="/static/braiid.css"' in result
        assert 'href="/static/tooltipster.bundle.css"' in result
        assert 'src="/static/jquery-3.6.0.js"' in result
        assert 'src="/static/tooltipster.bundle.js"' in result

    def test_standalone_true_inlines_jquery(self):
        """Test that standalone=True inlines jQuery instead of linking a CDN."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # jQuery source is present inline (its banner names the version)...
        assert "jQuery v3.6.0" in result
        # ...and there is no CDN link or /static/ path to fetch it.
        assert 'src="https://cdn.jsdelivr.net/npm/jquery' not in result
        assert 'src="/static/jquery-3.6.0.js"' not in result

    def test_standalone_true_inlines_tooltipster(self):
        """Test that standalone=True inlines Tooltipster instead of linking a CDN."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # Tooltipster source is present inline (its banner names the version)...
        assert "tooltipster v4.2.8" in result
        # ...and there is no CDN link or /static/ path to fetch it.
        assert 'href="https://cdn.jsdelivr.net/npm/tooltipster' not in result
        assert 'href="/static/tooltipster.bundle.css"' not in result
        assert 'src="/static/tooltipster.bundle.js"' not in result

    def test_standalone_true_uses_studio_url_for_rsm_assets(self):
        """Test that standalone=True uses Studio backend URL for RSM assets."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # RSM CSS should point to Studio backend (or be inlined)
        # The exact URL format will be determined by implementation
        assert 'href="/static/braiid.css"' not in result
        # Should have some form of braiid.css reference (either CDN or inline)
        assert "braiid.css" in result or "<style" in result

    def test_standalone_true_inlines_math_renderer(self):
        """Test that standalone=True inlines temml for math rendering."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # temml is the primary renderer and is inlined; the katex alias script
        # lets pseudocode reuse it without the on-demand loader.
        assert "temml" in result.lower()
        assert "window.katex = window.katex || window.temml;" in result

    def test_standalone_true_inlines_pseudocode(self):
        """Test that standalone=True inlines pseudocode instead of linking a CDN."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        assert "pseudocode" in result.lower()
        # The KaTeX CSS @import that pseudocode.min.css ships is stripped: temml
        # renders MathML, not KaTeX spans, so it would only be a dead fetch.
        assert "cdnjs.cloudflare.com" not in result

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
        assert 'href="/static/braiid.css"' in result


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
        body = '<body><div class="manuscript">Test</main></body>'
        web = standalone_builder.build(body)

        # Should only create index.html, no static directory
        files = list(web.listdir("/"))
        assert "index.html" in files
        assert "static" not in files


class TestStandaloneVendoredVersions:
    """Test that the inlined libraries are the pinned, vendored versions."""

    def test_jquery_version_is_3_6_0(self):
        """Test the inlined jQuery is exactly 3.6.0 (matches the bundle)."""
        source = ":rsm:\n\nTest.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        assert "jQuery v3.6.0" in result

    def test_tooltipster_version_matches_bundled(self):
        """Test the inlined Tooltipster is the pinned 4.2.8."""
        source = ":rsm:\n\nTest.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        assert "tooltipster v4.2.8" in result


class TestStandaloneSelfContained:
    """Regression tests for rsm-nyg: standalone output loads nothing external.

    A standalone file must render offline. These assert on assets the page would
    actually fetch (link/script tags with an http(s) src), not on http(s) strings
    that merely sit inside inlined JS or CSS.
    """

    def test_no_externally_loaded_assets(self):
        source = ":rsm:\n\n# T\n\nLet $x = 1$.\n\n::"
        result = rsm.build(source, handrails=True, lint=False, standalone=True)

        assert loaded_external_urls(result) == []

    def test_math_font_is_embedded(self):
        source = ":rsm:\n\nLet $x = 1$.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # The temml CSS carries its font as a data URI, so no woff2 is fetched.
        assert "data:font/woff2;base64," in result

    def test_google_fonts_import_stripped(self):
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, standalone=True)

        # braiid.css @imports Google Fonts; that would fetch over the network.
        assert "fonts.googleapis.com" not in result


class TestStandaloneFontEmbedding:
    """A standalone build always embeds the brand fonts.

    It carries the five brand families braiid uses (Montserrat, Source Sans 3,
    Source Serif 4, Atkinson Hyperlegible, Source Code Pro) as subsetted woff2
    data URIs, so it renders in the intended fonts offline, plus a metric-matched
    fallback stack as the floor. The file loads nothing external either way.
    """

    SRC = ":rsm:\n\n# T\n\nHello world.\n\n::"

    def test_brand_fonts_embedded(self):
        result = rsm.build(self.SRC, handrails=False, lint=False, standalone=True)

        # Each brand family is its own @font-face (the trailing "';" distinguishes
        # it from the "<brand> fallback" families and the --font-* stacks).
        assert "font-family: 'Montserrat';" in result
        assert "font-family: 'Source Sans 3';" in result
        assert "font-family: 'Source Serif 4';" in result
        assert "font-family: 'Source Code Pro';" in result
        assert "font-family: 'Atkinson Hyperlegible';" in result
        # Embedded as data URIs (12 brand faces), not fetched.
        assert result.count("data:font/woff2;base64,") >= 12

    def test_metric_fallback_floor_present(self):
        result = rsm.build(self.SRC, handrails=False, lint=False, standalone=True)

        assert "font-family: 'Montserrat fallback';" in result
        assert "font-family: 'Source Serif 4 fallback';" in result
        assert "size-adjust:" in result
        # The metric fallback sits right after the brand family in the stack.
        assert "'Montserrat', 'Montserrat fallback', sans-serif" in result

    def test_embedded_fonts_are_self_contained(self):
        result = rsm.build(self.SRC, handrails=True, lint=False, standalone=True)
        assert loaded_external_urls(result) == []
        assert "fonts.googleapis.com" not in result


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
        body = '<body><div class="manuscript">Test</main></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        # Should copy custom.css to static/ folder
        assert web.exists("static/custom.css")
        custom_css_in_static = web.readtext("static/custom.css")
        assert custom_css_content in custom_css_in_static

        # Should add link tag in HTML
        html = web.readtext("index.html")
        assert (
            '<link rel="stylesheet" type="text/css" href="/static/custom.css"' in html
        )

    def test_standalone_builder_with_custom_css(self, tmp_path):
        """Test StandaloneBuilder inlines custom CSS in <style> tag."""
        from rsm.builder import StandaloneBuilder

        # Create custom CSS file
        custom_css_file = tmp_path / "custom.css"
        custom_css_content = ".mytype { color: blue; }"
        custom_css_file.write_text(custom_css_content)

        # Create builder with custom_css
        builder = StandaloneBuilder(custom_css=str(custom_css_file))
        body = '<body><div class="manuscript">Test</main></body>'
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
        body = '<body><div class="manuscript">Test</main></body>'
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
        body = '<body><div class="manuscript">Test</main></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        # Should still build successfully
        assert web.exists("index.html")

        # Should NOT have custom.css in static/
        assert not web.exists("static/nonexistent.css")


class TestJSBundle:
    """Regression tests for rsm-standalone.js bundle format.

    The bundle must be an IIFE that assigns to window.RSM. If it is accidentally
    regenerated as an ES module (e.g. with --format=esm), standalone mode breaks
    silently because RSM.onload() is called in the template but the global is never set.
    """

    def test_bundle_is_iife(self):
        src = BUNDLE.read_text()
        assert src.startswith("var RSM = (() => {"), (
            "rsm-standalone.js must be an IIFE (var RSM = (() => { ... })()). "
            "Run `just js-bundle` to rebuild with the correct format."
        )

    def test_bundle_is_not_esm(self):
        src = BUNDLE.read_text()
        assert "export {" not in src, (
            "rsm-standalone.js must not use ES module exports. "
            "Run `just js-bundle` to rebuild with --format=iife --global-name=RSM."
        )

    def test_bundle_exposes_rsm_global(self):
        src = BUNDLE.read_text()
        assert "return __toCommonJS(onload_exports);" in src, (
            "rsm-standalone.js does not look like a valid IIFE bundle. "
            "Run `just js-bundle` to rebuild."
        )
