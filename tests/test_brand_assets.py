"""Tests for brand asset fetching with fallback."""

import urllib.request
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestBrandAssetFetching:
    """Test brand asset fetching for Sphinx docs."""

    def test_fetch_brand_assets_success(self, tmp_path):
        """Test successful fetch of brand assets from GitHub."""
        static_dir = tmp_path / "_static"
        static_dir.mkdir()

        # Mock successful URL retrieval
        with patch("urllib.request.urlretrieve") as mock_retrieve:
            from rsm.brand_assets import update_brand_assets_if_online

            update_brand_assets_if_online(static_dir)

            # Should attempt to fetch both assets
            assert mock_retrieve.call_count == 2
            calls = [call[0] for call in mock_retrieve.call_args_list]

            # Check URLs
            urls = [call[0] for call in calls]
            assert any("logo.svg" in url for url in urls)
            assert any("favicon.ico" in url for url in urls)

            # Check destinations
            dests = [call[1] for call in calls]
            assert any(str(dest).endswith("logo.svg") for dest in dests)
            assert any(str(dest).endswith("favicon.ico") for dest in dests)

    def test_fetch_brand_assets_network_failure(self, tmp_path):
        """Test fallback when network fetch fails."""
        static_dir = tmp_path / "_static"
        static_dir.mkdir()

        # Create committed fallback files
        (static_dir / "logo.svg").write_text("<svg>logo</svg>")
        (static_dir / "favicon.ico").write_bytes(b"fake-ico")

        # Mock network failure
        with patch(
            "urllib.request.urlretrieve", side_effect=urllib.error.URLError("No internet")
        ):
            from rsm.brand_assets import update_brand_assets_if_online

            # Should not raise, just fall back silently
            update_brand_assets_if_online(static_dir)

            # Committed files should still exist
            assert (static_dir / "logo.svg").exists()
            assert (static_dir / "favicon.ico").exists()
            assert (static_dir / "logo.svg").read_text() == "<svg>logo</svg>"

    def test_fetch_brand_assets_partial_failure(self, tmp_path):
        """Test when one asset fetches successfully but another fails."""
        static_dir = tmp_path / "_static"
        static_dir.mkdir()

        # Create committed fallback files
        (static_dir / "logo.svg").write_text("<svg>old-logo</svg>")
        (static_dir / "favicon.ico").write_bytes(b"old-ico")

        # Mock partial failure - logo succeeds, favicon fails
        def mock_retrieve(url, dest):
            if "logo.svg" in url:
                Path(dest).write_text("<svg>new-logo</svg>")
            else:
                raise urllib.error.URLError("Failed")

        with patch("urllib.request.urlretrieve", side_effect=mock_retrieve):
            from rsm.brand_assets import update_brand_assets_if_online

            update_brand_assets_if_online(static_dir)

            # Logo should be updated
            assert (static_dir / "logo.svg").read_text() == "<svg>new-logo</svg>"
            # Favicon should keep old version
            assert (static_dir / "favicon.ico").read_bytes() == b"old-ico"


class TestCLIBrandAssetFetching:
    """Test brand asset fetching for CLI init command."""

    def test_fetch_aris_logo_success(self, tmp_path):
        """Test that fetch_aris_logo_if_online succeeds when online."""
        from rsm.brand_assets import fetch_aris_logo_if_online

        dest = tmp_path / "aris-logo.svg"

        # Mock successful fetch
        def mock_retrieve(url, dest_path):
            Path(dest_path).write_text("<svg>latest-aris-logo</svg>")

        with patch("urllib.request.urlretrieve", side_effect=mock_retrieve):
            result = fetch_aris_logo_if_online(dest)

            assert result is True
            assert dest.exists()
            assert dest.read_text() == "<svg>latest-aris-logo</svg>"

    def test_fetch_aris_logo_failure(self, tmp_path):
        """Test that fetch_aris_logo_if_online returns False when offline."""
        from rsm.brand_assets import fetch_aris_logo_if_online

        dest = tmp_path / "aris-logo.svg"

        # Mock network failure
        with patch(
            "urllib.request.urlretrieve", side_effect=urllib.error.URLError("No internet")
        ):
            result = fetch_aris_logo_if_online(dest)

            assert result is False
            assert not dest.exists()  # File should not be created on failure


class TestBrandAssetIntegration:
    """Integration tests for brand assets in real scenarios."""

    def test_sphinx_conf_loads_without_error(self):
        """Test that Sphinx conf.py loads without errors."""
        conf_path = Path(__file__).parent.parent / "docs" / "source" / "conf.py"

        # Should be able to import conf without errors
        # (This will trigger the fetch-with-fallback logic)
        import sys
        import importlib.util

        spec = importlib.util.spec_from_file_location("conf", conf_path)
        conf = importlib.util.module_from_spec(spec)

        # Should not raise even if network is unavailable
        try:
            spec.loader.exec_module(conf)
        except Exception as e:
            pytest.fail(f"conf.py should load without errors: {e}")

        # Check that logo and favicon paths are set
        assert hasattr(conf, "html_logo")
        assert hasattr(conf, "html_favicon")
        assert "logo.svg" in conf.html_logo
        assert "favicon.ico" in conf.html_favicon
