"""Tests for theme_toggle parameter.

The theme_toggle parameter controls whether the dark mode toggle button and
localStorage script are included in the output HTML.
"""

import rsm


class TestThemeToggleParameter:
    """Test theme_toggle parameter in rsm.build()."""

    def test_theme_toggle_true_includes_button(self):
        """Test that theme_toggle=True includes dark mode toggle button."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, theme_toggle=True)

        assert 'class="rsm-theme-toggle"' in result
        assert "addEventListener('click'" in result
        assert "onclick=" not in result

    def test_theme_toggle_false_excludes_button(self):
        """Test that theme_toggle=False excludes dark mode toggle button."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, theme_toggle=False)

        assert 'class="rsm-theme-toggle"' not in result
        assert "addEventListener('click'" not in result

    def test_theme_toggle_true_includes_localstorage_script(self):
        """Test that theme_toggle=True includes localStorage script."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, theme_toggle=True)

        assert "localStorage.getItem" in result
        assert "rsm-theme" in result
        assert "addEventListener('click'" in result

    def test_theme_toggle_false_excludes_localstorage_script(self):
        """Test that theme_toggle=False excludes localStorage script."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False, theme_toggle=False)

        assert "addEventListener('click'" not in result

    def test_theme_toggle_default_is_true(self):
        """Test that theme_toggle defaults to True for backwards compatibility."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=False, lint=False)

        assert 'class="rsm-theme-toggle"' in result
        assert "addEventListener('click'" in result

    def test_theme_toggle_works_with_standalone(self):
        """Test that theme_toggle works with standalone=True."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(
            source, handrails=False, lint=False, standalone=True, theme_toggle=False
        )

        assert 'class="rsm-theme-toggle"' not in result
        assert "addEventListener('click'" not in result
        # Should still be valid standalone HTML
        assert "cdn.jsdelivr.net" in result


class TestThemeToggleBuilder:
    """Test theme_toggle parameter at the builder level."""

    def test_folder_builder_with_theme_toggle_false(self, tmp_path):
        """Test FolderBuilder respects theme_toggle=False."""
        from rsm.builder import FolderBuilder

        builder = FolderBuilder(theme_toggle=False)
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        html = web.readtext("index.html")
        assert 'class="rsm-theme-toggle"' not in html
        assert "addEventListener('click'" not in html

    def test_standalone_builder_with_theme_toggle_false(self, tmp_path):
        """Test StandaloneBuilder respects theme_toggle=False."""
        from rsm.builder import StandaloneBuilder

        builder = StandaloneBuilder(theme_toggle=False)
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        html = web.readtext("index.html")
        assert 'class="rsm-theme-toggle"' not in html
        assert "addEventListener('click'" not in html

    def test_builder_theme_toggle_default_is_true(self, tmp_path):
        """Test that builder theme_toggle defaults to True."""
        from rsm.builder import FolderBuilder

        builder = FolderBuilder()
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        html = web.readtext("index.html")
        assert 'class="rsm-theme-toggle"' in html
        assert "addEventListener('click'" in html
