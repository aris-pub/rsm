"""Tests for figure/html static toggle feature."""

import rsm


class TestDataStaticAttribute:
    """data-static should be set on figure elements when :static: is present."""

    def test_html_node_has_data_static(self):
        html = rsm.render(
            "## S\n\n:html: {\n  :path: widget.html\n  :static: fallback.png\n}\n::\n",
            handrails=False,
        )
        assert 'data-static=' in html

    def test_figure_node_has_data_static(self):
        html = rsm.render(
            "## S\n\n:figure: {\n  :path: photo.png\n  :static: photo-lowres.png\n}\n::\n",
            handrails=False,
        )
        assert 'data-static=' in html

    def test_no_data_static_when_not_set(self):
        html = rsm.render(
            "## S\n\n:figure: {\n  :path: photo.png\n}\n::\n",
            handrails=False,
        )
        assert 'data-static' not in html

    def test_data_static_on_html_without_static(self):
        html = rsm.render(
            "## S\n\n:html: {\n  :path: widget.html\n}\n::\n",
            handrails=False,
        )
        assert 'data-static' not in html


class TestStaticFallbackImage:
    """A hidden static fallback img should be emitted inside the figure."""

    def test_html_node_has_fallback_img(self):
        html = rsm.render(
            "## S\n\n:html: {\n  :path: widget.html\n  :static: fallback.png\n}\n::\n",
            handrails=False,
        )
        assert 'class="static-fallback"' in html
        assert 'style="display:none"' in html

    def test_figure_node_has_fallback_img(self):
        html = rsm.render(
            "## S\n\n:figure: {\n  :path: photo.png\n  :static: photo-lowres.png\n}\n::\n",
            handrails=False,
        )
        assert 'class="static-fallback"' in html

    def test_no_fallback_img_when_no_static(self):
        html = rsm.render(
            "## S\n\n:figure: {\n  :path: photo.png\n}\n::\n",
            handrails=False,
        )
        assert 'static-fallback' not in html


class TestStaticToggleMenuItem:
    """The caption handrail menu should have a static toggle item."""

    def test_menu_item_enabled_with_static(self):
        html = rsm.render(
            "## S\n\n:html: {\n  :path: widget.html\n  :static: fallback.png\n}\n:caption: Widget.\n::\n",
            handrails=True,
        )
        assert 'data-menu-static-toggle="true"' in html

    def test_menu_item_disabled_without_static(self):
        html = rsm.render(
            "## S\n\n:html: {\n  :path: widget.html\n}\n:caption: Widget.\n::\n",
            handrails=True,
        )
        assert 'data-menu-static-toggle="disabled"' in html

    def test_menu_item_on_figure_with_static(self):
        html = rsm.render(
            "## S\n\n:figure: {\n  :path: photo.png\n  :static: photo-lowres.png\n}\n:caption: Photo.\n::\n",
            handrails=True,
        )
        assert 'data-menu-static-toggle="true"' in html
