"""Tests for the theme_toggle parameter.

theme_toggle controls whether the pre-paint boot script is emitted, the one
that applies the reader's saved theme and type preferences (from the
``rsm-reading`` localStorage key) before first paint. The interactive light/dark
control, along with the type controls, now lives in the sidebar's Reading tab,
so there is no longer a standalone chrome toggle button.
"""

import rsm


class TestThemeToggleParameter:
    """Test the theme_toggle parameter in rsm.build()."""

    def test_theme_toggle_true_emits_boot_script(self):
        source = "Hello world.\n\n"
        result = rsm.build(source, handrails=False, lint=False, theme_toggle=True)
        assert "localStorage.getItem" in result
        assert "rsm-reading" in result

    def test_theme_toggle_false_omits_boot_script(self):
        source = "Hello world.\n\n"
        result = rsm.build(source, handrails=False, lint=False, theme_toggle=False)
        assert "localStorage.getItem" not in result

    def test_no_standalone_chrome_toggle_button(self):
        """Light/dark moved to the sidebar Reading tab; no chrome button is injected."""
        source = "Hello world.\n\n"
        result = rsm.build(source, handrails=False, lint=False, theme_toggle=True)
        assert 'class="rsm-theme-toggle"' not in result
        assert "addEventListener('click'" not in result

    def test_theme_toggle_default_is_true(self):
        source = "Hello world.\n\n"
        result = rsm.build(source, handrails=False, lint=False)
        assert "localStorage.getItem" in result

    def test_theme_toggle_works_with_standalone(self):
        source = "Hello world.\n\n"
        result = rsm.build(
            source, handrails=False, lint=False, standalone=True, theme_toggle=False
        )
        # No chrome toggle button, and still valid standalone HTML. (We don't
        # assert on localStorage here: standalone inlines the bundle, whose
        # reading-control JS uses localStorage regardless of theme_toggle.)
        assert 'class="rsm-theme-toggle"' not in result
        assert "cdn.jsdelivr.net" in result


class TestThemeToggleBuilder:
    """Test the theme_toggle parameter at the builder level."""

    def test_folder_builder_with_theme_toggle_false(self, tmp_path):
        from rsm.builder import FolderBuilder

        builder = FolderBuilder(theme_toggle=False)
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")
        html = web.readtext("index.html")
        assert "localStorage.getItem" not in html

    def test_builder_theme_toggle_default_is_true(self, tmp_path):
        from rsm.builder import FolderBuilder

        builder = FolderBuilder()
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")
        html = web.readtext("index.html")
        assert "localStorage.getItem" in html
