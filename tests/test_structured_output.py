"""Tests for structured output functionality in rsm.make()."""

import rsm


def test_make_structured_returns_dict():
    """Test that structured=True returns a dictionary."""
    source = ":rsm: Hello world! ::"
    result = rsm.make(source, structured=True)

    assert isinstance(result, dict)
    assert set(result.keys()) == {"head", "body", "init_script"}


def test_make_structured_false_returns_string():
    """Test that structured=False returns HTML string (backward compatibility)."""
    source = ":rsm: Hello world! ::"
    result = rsm.make(source, structured=False)

    assert isinstance(result, str)
    assert "<html>" in result
    assert "<head>" in result
    assert "<body>" in result


def test_make_default_structured_returns_string():
    """Test that default (no structured param) returns HTML string."""
    source = ":rsm: Hello world! ::"
    result = rsm.make(source)

    assert isinstance(result, str)
    assert "<html>" in result


def test_structured_head_contains_dependencies():
    """Test that structured head contains tooltip dependencies."""
    source = ":rsm: Hello world! ::"
    result = rsm.make(source, structured=True)

    head = result["head"]
    assert "jquery-3.6.0.js" in head
    assert "tooltipster.bundle.js" in head
    assert "tooltipster.bundle.css" in head
    assert "rsm.css" in head


def test_structured_body_contains_content():
    """Test that structured body contains manuscript content."""
    source = ":rsm: Hello world! ::"
    result = rsm.make(source, structured=True)

    body = result["body"]
    assert "manuscriptwrapper" in body
    assert "Hello world!" in body


def test_structured_init_script_empty_without_assets():
    """Test that init_script is empty for content without HTML assets."""
    source = ":rsm: Hello world! ::"
    result = rsm.make(source, structured=True)

    # No HTML assets means no execution scripts to extract
    assert result["init_script"] == ""


def test_structured_with_asset_resolver():
    """Test structured output with custom asset resolver."""
    from rsm.asset_resolver import AssetResolverFromDisk

    source = ":rsm: Hello world! ::"
    resolver = AssetResolverFromDisk()
    result = rsm.make(source, structured=True, asset_resolver=resolver)

    assert isinstance(result, dict)
    assert "head" in result
    assert "body" in result
    assert "init_script" in result


def test_structured_vs_regular_same_content():
    """Test that structured and regular output contain same essential content."""
    source = ":rsm: Hello world! ::"

    regular = rsm.make(source, structured=False)
    structured = rsm.make(source, structured=True)

    # Extract head and body from regular HTML
    import re

    regular_head_match = re.search(r"<head>(.*?)</head>", regular, re.DOTALL)
    regular_body_match = re.search(r"<body[^>]*>(.*?)</body>", regular, re.DOTALL)

    assert regular_head_match is not None
    assert regular_body_match is not None

    # Compare essential content (allowing for whitespace differences)
    regular_head = regular_head_match.group(1).strip()
    regular_body = regular_body_match.group(1).strip()

    assert structured["head"].strip() == regular_head
    assert structured["body"].strip() == regular_body


def test_structured_handrails_parameter():
    """Test structured output with handrails parameter."""
    source = ":rsm: Hello world! ::"

    result_with_handrails = rsm.make(source, structured=True, handrails=True)
    result_without_handrails = rsm.make(source, structured=True, handrails=False)

    # Both should be dictionaries with same structure
    assert isinstance(result_with_handrails, dict)
    assert isinstance(result_without_handrails, dict)
    assert set(result_with_handrails.keys()) == {"head", "body", "init_script"}
    assert set(result_without_handrails.keys()) == {"head", "body", "init_script"}


# =============================================================================
# Tests for _parse_html_to_structured IIFE extraction
# =============================================================================

from rsm.app import _parse_html_to_structured


class TestParseHtmlToStructuredIIFE:
    """Tests for IIFE extraction in _parse_html_to_structured."""

    def test_extracts_iife_from_post_html_script(self):
        """Test that IIFE content after </html> is extracted to init_script."""
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div id="chart"></div></body></html>
<script>
(function() {
    console.log("Hello from IIFE");
})();
</script>"""

        result = _parse_html_to_structured(html)

        assert "(function()" in result["init_script"]
        assert 'console.log("Hello from IIFE")' in result["init_script"]

    def test_extracts_cdn_urls_to_head(self):
        """Test that CDN script URLs from IIFE are added to head."""
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div id="chart"></div></body></html>
<script>
(function() {
    var script_abc = document.createElement('script');
    script_abc.src = 'https://cdn.plot.ly/plotly-latest.min.js';
    document.head.appendChild(script_abc);
})();
</script>"""

        result = _parse_html_to_structured(html)

        assert (
            '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>'
            in result["head"]
        )

    def test_extracts_multiple_cdn_urls(self):
        """Test extraction of multiple CDN URLs from IIFE."""
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div id="chart"></div></body></html>
<script>
(function() {
    var script_1 = document.createElement('script');
    script_1.src = 'https://d3js.org/d3.v7.min.js';
    var script_2 = document.createElement('script');
    script_2.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    document.head.appendChild(script_1);
    document.head.appendChild(script_2);
})();
</script>"""

        result = _parse_html_to_structured(html)

        assert '<script src="https://d3js.org/d3.v7.min.js"></script>' in result["head"]
        assert (
            '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
            in result["head"]
        )

    def test_preserves_inline_script_execution_code(self):
        """Test that inline script execution code is preserved in init_script."""
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div id="chart"></div></body></html>
<script>
(function() {
    var inlineScripts = [function() { Plotly.newPlot('chart', data); }];
    function executeInlineScripts() {
        inlineScripts.forEach(function(fn) { fn(); });
    }
    executeInlineScripts();
})();
</script>"""

        result = _parse_html_to_structured(html)

        assert "inlineScripts" in result["init_script"]
        assert "Plotly.newPlot" in result["init_script"]
        assert "executeInlineScripts" in result["init_script"]

    def test_no_scripts_returns_empty_init_script(self):
        """Test that HTML without post-html scripts returns empty init_script."""
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div>Hello World</div></body></html>"""

        result = _parse_html_to_structured(html)

        assert result["init_script"] == ""

    def test_ignores_relative_script_urls(self):
        """Test that relative script URLs are not added to head."""
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div id="chart"></div></body></html>
<script>
(function() {
    var script_abc = document.createElement('script');
    script_abc.src = '/local/script.js';
    document.head.appendChild(script_abc);
})();
</script>"""

        result = _parse_html_to_structured(html)

        # Relative URL should not be in head
        assert "/local/script.js" not in result["head"]

    def test_handles_protocol_relative_urls(self):
        """Test that protocol-relative URLs (//cdn.example.com) are extracted."""
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div id="chart"></div></body></html>
<script>
(function() {
    var script_abc = document.createElement('script');
    script_abc.src = '//cdn.example.com/lib.js';
    document.head.appendChild(script_abc);
})();
</script>"""

        result = _parse_html_to_structured(html)

        assert '<script src="//cdn.example.com/lib.js"></script>' in result["head"]

    def test_body_content_unchanged(self):
        """Test that body content is not affected by IIFE extraction."""
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div id="chart" class="plotly-graph"></div></body></html>
<script>(function() { console.log("test"); })();</script>"""

        result = _parse_html_to_structured(html)

        assert '<div id="chart" class="plotly-graph"></div>' in result["body"]

    def test_multiple_post_html_scripts(self):
        """Test handling of multiple script tags after </html>."""
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><div id="chart"></div></body></html>
<script>
(function() { console.log("first"); })();
</script>
<script>
(function() { console.log("second"); })();
</script>"""

        result = _parse_html_to_structured(html)

        assert 'console.log("first")' in result["init_script"]
        assert 'console.log("second")' in result["init_script"]

    def test_realistic_plotly_iife(self):
        """Test extraction of a realistic Plotly IIFE structure."""
        html = """<!DOCTYPE html>
<html><head><title>Chart</title></head>
<body><div id="plotly-chart"></div></body></html>
<script>
(function() {
    var scriptsLoaded = 0;
    var totalExternalScripts = 1;
    var inlineScripts = [function() { try {
        Plotly.newPlot('plotly-chart', [{x: [1,2,3], y: [4,5,6], type: 'scatter'}]);
    } catch (e) { console.warn("RSM: Error:", e); } }];

    function executeInlineScripts() {
        if (scriptsLoaded >= totalExternalScripts) {
            inlineScripts.forEach(function(scriptFunc) {
                try { scriptFunc(); } catch (e) { console.warn(e); }
            });
        }
    }

    function onScriptLoad() {
        scriptsLoaded++;
        executeInlineScripts();
    }

    var script_plotly = document.createElement('script');
    script_plotly.src = 'https://cdn.plot.ly/plotly-2.27.0.min.js';
    script_plotly.onload = onScriptLoad;
    script_plotly.onerror = onScriptLoad;
    document.head.appendChild(script_plotly);

    if (totalExternalScripts === 0) {
        executeInlineScripts();
    }
})();
</script>"""

        result = _parse_html_to_structured(html)

        # CDN should be in head
        assert (
            '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'
            in result["head"]
        )

        # IIFE structure should be preserved
        assert "scriptsLoaded" in result["init_script"]
        assert "totalExternalScripts" in result["init_script"]
        assert "inlineScripts" in result["init_script"]
        assert "executeInlineScripts" in result["init_script"]
        assert "onScriptLoad" in result["init_script"]
        assert "Plotly.newPlot" in result["init_script"]

    def test_d3_chart_iife(self):
        """Test extraction of a D3.js chart IIFE."""
        html = """<!DOCTYPE html>
<html><head><title>D3 Chart</title></head>
<body><svg id="d3-chart"></svg></body></html>
<script>
(function() {
    var scriptsLoaded = 0;
    var totalExternalScripts = 1;
    var inlineScripts = [function() {
        d3.select('#d3-chart')
          .append('circle')
          .attr('r', 50);
    }];

    function onScriptLoad() { scriptsLoaded++; }

    var script_d3 = document.createElement('script');
    script_d3.src = 'https://d3js.org/d3.v7.min.js';
    script_d3.onload = onScriptLoad;
    document.head.appendChild(script_d3);
})();
</script>"""

        result = _parse_html_to_structured(html)

        assert '<script src="https://d3js.org/d3.v7.min.js"></script>' in result["head"]
        assert "d3.select" in result["init_script"]

    def test_content_after_chart_preserved(self):
        """Test that content after an interactive chart is preserved in body.

        Regression test: content was being cut off after charts in Studio.
        """
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body>
<h1>Introduction</h1>
<p>Content before the chart.</p>
<div id="chart"></div>
<h2>Section After Chart</h2>
<p>This content must appear after the chart.</p>
<h2>Conclusion</h2>
<p>Final paragraph of the document.</p>
</body></html>
<script>
(function() {
    var script = document.createElement('script');
    script.src = 'https://cdn.plot.ly/plotly.min.js';
    script.onload = function() {
        Plotly.newPlot('chart', [{x: [1,2], y: [1,2]}]);
    };
    document.head.appendChild(script);
})();
</script>"""

        result = _parse_html_to_structured(html)

        # All content must be preserved in body
        assert "Introduction" in result["body"]
        assert "Content before the chart" in result["body"]
        assert "Section After Chart" in result["body"]
        assert "This content must appear after the chart" in result["body"]
        assert "Conclusion" in result["body"]
        assert "Final paragraph of the document" in result["body"]

        # Chart container must be present
        assert 'id="chart"' in result["body"]

    def test_embedded_html_with_body_tags_does_not_truncate(self):
        """Test that embedded HTML containing </body> tags doesn't truncate content.

        Regression test: Plotly exports include full HTML documents with </body>
        tags. The regex was matching the FIRST </body> (from embedded content)
        instead of the LAST (document's actual closing tag).
        """
        # Simulates a Plotly chart embedded in a document with content after
        html = """<!DOCTYPE html>
<html><head><title>Document</title></head>
<body>
<h1>Before Chart</h1>
<div class="figure">
<!-- Embedded Plotly HTML starts here -->
<html>
<head><meta charset="utf-8" /></head>
<body>
<div id="plotly-chart"></div>
<script>Plotly.newPlot('chart', data);</script>
</body>
</html>
<!-- Embedded Plotly HTML ends here -->
</div>
<h2>After Chart Section</h2>
<p>This content comes after the embedded chart and MUST be preserved.</p>
<h2>Conclusion</h2>
<p>Final content of the document.</p>
</body></html>"""

        result = _parse_html_to_structured(html)

        # Content AFTER the embedded chart must be preserved
        assert "After Chart Section" in result["body"], (
            "Content after embedded chart was truncated!"
        )
        assert "This content comes after the embedded chart" in result["body"]
        assert "Conclusion" in result["body"]
        assert "Final content of the document" in result["body"]

        # Content before chart must also be present
        assert "Before Chart" in result["body"]

        # The embedded chart div must be present
        assert 'id="plotly-chart"' in result["body"]
