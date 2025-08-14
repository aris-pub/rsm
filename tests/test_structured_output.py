"""Tests for structured output functionality in rsm.make()."""

import pytest
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


def test_structured_init_script_correct():
    """Test that init_script contains correct onload call."""
    source = ":rsm: Hello world! ::"
    result = rsm.make(source, structured=True)
    
    init_script = result["init_script"]
    expected = "import { onload } from '/static/onload.js'; onload(document, { path: '/static/' });"
    assert init_script == expected


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
    regular_head_match = re.search(r'<head>(.*?)</head>', regular, re.DOTALL)
    regular_body_match = re.search(r'<body[^>]*>(.*?)</body>', regular, re.DOTALL)
    
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