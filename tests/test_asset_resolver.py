"""Tests for AssetResolver Protocol and implementations."""

from rsm.asset_resolver import AssetResolverFromDisk


class MockAssetResolver:
    """Mock asset resolver for testing."""

    def __init__(self, assets: dict[str, str]):
        self.assets = assets

    def resolve_asset(self, path: str) -> str | None:
        return self.assets.get(path)


def test_protocol_compliance():
    """Test that mock resolver follows AssetResolver protocol."""
    # This test will verify protocol compliance once we define the Protocol
    mock = MockAssetResolver({"test.html": "<div>test</div>"})
    assert mock.resolve_asset("test.html") == "<div>test</div>"
    assert mock.resolve_asset("missing.html") is None


def test_disk_resolver_reads_existing_file(tmp_path):
    """Test that AssetResolverFromDisk reads existing files."""
    test_file = tmp_path / "test.html"
    test_content = "<div>test content</div>"
    test_file.write_text(test_content)

    resolver = AssetResolverFromDisk()
    result = resolver.resolve_asset(str(test_file))
    assert result == test_content


def test_disk_resolver_returns_none_for_missing_file():
    """Test that AssetResolverFromDisk returns None for missing files."""
    resolver = AssetResolverFromDisk()
    result = resolver.resolve_asset("nonexistent_file.html")
    assert result is None


def test_disk_resolver_handles_unicode_decode_error(tmp_path):
    """Test that AssetResolverFromDisk returns None for binary files."""
    binary_file = tmp_path / "test.bin"
    binary_file.write_bytes(b"\xff\xfe\x00\x01")  # Invalid UTF-8

    resolver = AssetResolverFromDisk()
    result = resolver.resolve_asset(str(binary_file))
    assert result is None


def test_custom_resolver_integration():
    """Test that custom resolvers can provide assets from memory."""
    assets = {
        "chart.html": "<div class='chart'>Chart content</div>",
        "video.mp4": "fake-video-content",
        "image.png": "fake-image-data",
    }

    mock = MockAssetResolver(assets)

    # Test various asset types
    assert mock.resolve_asset("chart.html") == "<div class='chart'>Chart content</div>"
    assert mock.resolve_asset("video.mp4") == "fake-video-content"
    assert mock.resolve_asset("image.png") == "fake-image-data"
    assert mock.resolve_asset("missing.txt") is None


def test_translator_with_custom_resolver(tmp_path):
    """Test that translator uses custom asset resolver."""
    from rsm import transformer, tsparser
    from rsm.translator import Translator

    # Create custom resolver with test HTML
    test_html = "<div class='custom-content'>Mock HTML content</div>"
    mock_resolver = MockAssetResolver({"test.html": test_html})

    # Create translator with custom resolver
    translator = Translator(asset_resolver=mock_resolver)

    # Parse RSM source with HTML asset
    source = """
    :rsm:
    
    :html:
      :path: test.html
      :caption: Test HTML asset.
    ::
    
    ::
    """

    parser = tsparser.TSParser()
    tree = parser.parse(source)
    transformer_obj = transformer.Transformer()
    manuscript = transformer_obj.transform(tree)

    # Translate to HTML
    result = translator.translate(manuscript)

    # Verify custom resolver content is used
    assert test_html in result
    assert "Mock HTML content" in result


def test_render_with_custom_resolver():
    """Test that render function works with custom asset resolver."""
    import rsm

    # Create custom resolver
    test_html = "<p>Custom resolver HTML</p>"
    mock_resolver = MockAssetResolver({"custom.html": test_html})

    # RSM source with HTML asset
    source = """
    :rsm:
    
    :html:
      :path: custom.html
      :caption: Custom HTML.
    ::
    
    ::
    """

    # Render with custom resolver
    result = rsm.render(source, asset_resolver=mock_resolver)

    # Verify custom content is used
    assert test_html in result
    assert "Custom resolver HTML" in result
