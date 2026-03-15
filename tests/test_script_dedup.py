"""Tests for script tag deduplication in the builder.

When multiple Html widgets reference the same external script (e.g. Plotly), the builder
should deduplicate <script src="..."> tags so each unique URL is loaded only once.
"""

from rsm.builder import HTMLBuilder


def _build_body(body_content: str) -> str:
    """Build HTML from a body string using HTMLBuilder and return the full HTML."""
    builder = HTMLBuilder(theme_toggle=False)
    builder.body = body_content
    builder.web = None
    # We only need the deduplication step, so call it directly
    return builder.deduplicate_scripts(body_content)


class TestScriptDeduplication:
    """Test that duplicate <script src="..."> tags are removed from the body."""

    def test_no_scripts_unchanged(self):
        body = '<body><div>Hello world</div></body>'
        result = _build_body(body)
        assert result == body

    def test_single_script_unchanged(self):
        body = '<body><script src="https://cdn.plot.ly/plotly-3.4.0.min.js"></script><div>content</div></body>'
        result = _build_body(body)
        assert result.count('src="https://cdn.plot.ly/plotly-3.4.0.min.js"') == 1

    def test_duplicate_scripts_deduplicated(self):
        body = (
            '<body>'
            '<div><script src="https://cdn.plot.ly/plotly-3.4.0.min.js"></script>'
            '<div id="fig1">chart1</div></div>'
            '<div><script src="https://cdn.plot.ly/plotly-3.4.0.min.js"></script>'
            '<div id="fig2">chart2</div></div>'
            '</body>'
        )
        result = _build_body(body)
        assert result.count('src="https://cdn.plot.ly/plotly-3.4.0.min.js"') == 1

    def test_three_duplicates_reduced_to_one(self):
        script = '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'
        body = f'<body><div>{script}fig1</div><div>{script}fig2</div><div>{script}fig3</div></body>'
        result = _build_body(body)
        assert result.count('src="https://cdn.plot.ly/plotly-2.35.2.min.js"') == 1

    def test_different_scripts_both_kept(self):
        body = (
            '<body>'
            '<script src="https://cdn.plot.ly/plotly-3.4.0.min.js"></script>'
            '<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>'
            '</body>'
        )
        result = _build_body(body)
        assert result.count('src="https://cdn.plot.ly/plotly-3.4.0.min.js"') == 1
        assert result.count('src="https://cdn.jsdelivr.net/npm/d3@7"') == 1

    def test_different_versions_both_kept(self):
        body = (
            '<body>'
            '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'
            '<script src="https://cdn.plot.ly/plotly-3.4.0.min.js"></script>'
            '</body>'
        )
        result = _build_body(body)
        assert result.count('src="https://cdn.plot.ly/plotly-2.35.2.min.js"') == 1
        assert result.count('src="https://cdn.plot.ly/plotly-3.4.0.min.js"') == 1

    def test_first_occurrence_kept(self):
        """The first occurrence of a duplicated script should be the one that remains."""
        body = (
            '<body>'
            '<div id="first"><script src="https://example.com/lib.js"></script>A</div>'
            '<div id="second"><script src="https://example.com/lib.js"></script>B</div>'
            '</body>'
        )
        result = _build_body(body)
        assert 'src="https://example.com/lib.js"' in result
        pos = result.index('src="https://example.com/lib.js"')
        assert result.index('id="first"') < pos

    def test_inline_scripts_not_touched(self):
        """Inline <script>...</script> blocks (no src) should never be removed."""
        body = (
            '<body>'
            '<script>var x = 1;</script>'
            '<script>var y = 2;</script>'
            '<script>var x = 1;</script>'
            '</body>'
        )
        result = _build_body(body)
        assert result.count('<script>var x = 1;</script>') == 2
        assert result.count('<script>var y = 2;</script>') == 1

    def test_mixed_inline_and_src_scripts(self):
        """Inline scripts preserved, src scripts deduplicated."""
        body = (
            '<body>'
            '<script src="https://example.com/lib.js"></script>'
            '<script>Plotly.newPlot("fig1", data1)</script>'
            '<script src="https://example.com/lib.js"></script>'
            '<script>Plotly.newPlot("fig2", data2)</script>'
            '</body>'
        )
        result = _build_body(body)
        assert result.count('src="https://example.com/lib.js"') == 1
        assert 'Plotly.newPlot("fig1", data1)' in result
        assert 'Plotly.newPlot("fig2", data2)' in result

    def test_script_with_attributes_deduplicated(self):
        """Scripts with extra attributes (integrity, crossorigin) should deduplicate by src."""
        script1 = '<script charset="utf-8" src="https://cdn.plot.ly/plotly-3.4.0.min.js" integrity="sha256-abc" crossorigin="anonymous"></script>'
        script2 = '<script src="https://cdn.plot.ly/plotly-3.4.0.min.js"></script>'
        body = f'<body>{script1}{script2}</body>'
        result = _build_body(body)
        assert result.count('cdn.plot.ly/plotly-3.4.0.min.js') == 1

    def test_whitespace_variations(self):
        """Scripts with different whitespace around them should still deduplicate."""
        body = (
            '<body>\n'
            '  <script src="https://example.com/lib.js"></script>\n'
            '  <div>content</div>\n'
            '  <script src="https://example.com/lib.js"></script>\n'
            '</body>'
        )
        result = _build_body(body)
        assert result.count('src="https://example.com/lib.js"') == 1

    def test_plotly_config_inline_scripts_preserved(self):
        """The PlotlyConfig inline scripts that accompany each chart must all be kept."""
        body = (
            '<body>'
            '<div><script>window.PlotlyConfig = {MathJaxConfig: "local"};</script>'
            '<script src="https://cdn.plot.ly/plotly-3.4.0.min.js"></script>'
            '<script>Plotly.newPlot("fig1", [])</script></div>'
            '<div><script>window.PlotlyConfig = {MathJaxConfig: "local"};</script>'
            '<script src="https://cdn.plot.ly/plotly-3.4.0.min.js"></script>'
            '<script>Plotly.newPlot("fig2", [])</script></div>'
            '</body>'
        )
        result = _build_body(body)
        # CDN script deduplicated
        assert result.count('src="https://cdn.plot.ly/plotly-3.4.0.min.js"') == 1
        # Both inline PlotlyConfig scripts preserved
        assert result.count('window.PlotlyConfig') == 2
        # Both newPlot calls preserved
        assert result.count('Plotly.newPlot') == 2

    def test_realistic_glee_pattern(self):
        """Simulate the actual GLEE paper pattern: multiple widgets with plotly."""
        widgets = []
        for i in range(4):
            widgets.append(
                f'<div><script>window.PlotlyConfig = {{MathJaxConfig: "local"}};</script>'
                f'<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'
                f'<div id="fig-{i}"></div>'
                f'<script>Plotly.newPlot("fig-{i}", [{{x:[1,2],y:[{i},{i+1}]}}])</script></div>'
            )
        for i in range(5):
            widgets.append(
                f'<div><script>window.PlotlyConfig = {{MathJaxConfig: "local"}};</script>'
                f'<script src="https://cdn.plot.ly/plotly-3.4.0.min.js"></script>'
                f'<div id="fig-v3-{i}"></div>'
                f'<script>Plotly.newPlot("fig-v3-{i}", [{{x:[1,2],y:[{i},{i+1}]}}])</script></div>'
            )
        body = '<body>' + ''.join(widgets) + '</body>'
        result = _build_body(body)

        # 9 CDN loads reduced to 2 (one per version)
        assert result.count('src="https://cdn.plot.ly/plotly-2.35.2.min.js"') == 1
        assert result.count('src="https://cdn.plot.ly/plotly-3.4.0.min.js"') == 1

        # All 9 inline PlotlyConfig scripts preserved
        assert result.count('window.PlotlyConfig') == 9
        # All 9 newPlot calls preserved
        assert result.count('Plotly.newPlot') == 9

    def test_empty_body(self):
        result = _build_body('')
        assert result == ''

    def test_script_src_with_single_quotes_ignored(self):
        """Only double-quoted src attributes are standard HTML; single quotes handled too."""
        body = (
            "<body>"
            "<script src='https://example.com/lib.js'></script>"
            "<script src='https://example.com/lib.js'></script>"
            "</body>"
        )
        result = _build_body(body)
        assert result.count("src='https://example.com/lib.js'") == 1
