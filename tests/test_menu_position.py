"""Tests for menu_position parameter.

The menu_position parameter controls whether handrail context menus open to the
left (default) or right of the handrail dots.
"""

import rsm


class TestMenuPositionParameter:
    """Test menu_position parameter in rsm.build()."""

    def test_menu_position_default_is_left(self):
        """Test that menu_position defaults to left (no CSS override)."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=True, lint=False)

        # Should not contain the right-position CSS override
        assert ".hr-menu-zone .hr-menu" not in result or "left: 32px !important" not in result

    def test_menu_position_left_no_override(self):
        """Test that menu_position='left' does not inject CSS override."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=True, lint=False, menu_position="left")

        # Should not contain the right-position CSS override
        assert "left: 32px !important" not in result
        assert "left: 16px !important" not in result

    def test_menu_position_right_injects_css(self):
        """Test that menu_position='right' injects CSS override."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(source, handrails=True, lint=False, menu_position="right")

        # Should contain the right-position CSS override
        assert ".hr-menu-zone .hr-menu" in result
        assert "left: 32px !important" in result
        # Also check for offset variant
        assert "left: 16px !important" in result

    def test_menu_position_right_with_standalone(self):
        """Test that menu_position='right' works with standalone=True."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(
            source, handrails=True, lint=False, standalone=True, menu_position="right"
        )

        # Should contain the right-position CSS override
        assert "left: 32px !important" in result
        assert "left: 16px !important" in result
        # Should still be valid standalone HTML
        assert "cdn.jsdelivr.net" in result

    def test_menu_position_works_without_handrails(self):
        """Test that menu_position doesn't break when handrails=False."""
        source = ":rsm:\n\nHello world.\n\n::"
        result = rsm.build(
            source, handrails=False, lint=False, menu_position="right"
        )

        # Should still inject the CSS (even though no menus will be present)
        assert "left: 32px !important" in result


class TestMenuPositionBuilder:
    """Test menu_position parameter at the builder level."""

    def test_folder_builder_menu_position_right(self, tmp_path):
        """Test FolderBuilder respects menu_position='right'."""
        from rsm.builder import FolderBuilder

        builder = FolderBuilder(menu_position="right")
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        html = web.readtext("index.html")
        assert "left: 32px !important" in html
        assert "left: 16px !important" in html

    def test_standalone_builder_menu_position_right(self, tmp_path):
        """Test StandaloneBuilder respects menu_position='right'."""
        from rsm.builder import StandaloneBuilder

        builder = StandaloneBuilder(menu_position="right")
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        html = web.readtext("index.html")
        assert "left: 32px !important" in html
        assert "left: 16px !important" in html

    def test_folder_builder_menu_position_default(self, tmp_path):
        """Test that FolderBuilder menu_position defaults to left."""
        from rsm.builder import FolderBuilder

        builder = FolderBuilder()
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        html = web.readtext("index.html")
        # Should not contain right-position override
        assert "left: 32px !important" not in html

    def test_standalone_builder_menu_position_default(self, tmp_path):
        """Test that StandaloneBuilder menu_position defaults to left."""
        from rsm.builder import StandaloneBuilder

        builder = StandaloneBuilder()
        body = '<body><div class="manuscript">Test</div></body>'
        web = builder.build(body, src=tmp_path / "test.rsm")

        html = web.readtext("index.html")
        # Should not contain right-position override
        assert "left: 32px !important" not in html
