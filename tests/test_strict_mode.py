"""Tests for strict mode CST error detection."""

import pytest

import rsm
from rsm.transformer import RSMTransformerError


class TestStrictModeRaises:
    """strict=True must raise when the CST contains parse errors."""

    def test_render_raises_on_cst_error(self):
        with pytest.raises(RSMTransformerError, match="CST errors"):
            rsm.render(
                ":enumerate:\n:-: A\n:-: B\n::\n",
                strict=True,
                handrails=False,
            )

    def test_build_raises_on_cst_error(self):
        with pytest.raises(RSMTransformerError, match="CST errors"):
            rsm.build(
                source=":enumerate:\n:-: A\n:-: B\n::\n",
                strict=True,
                handrails=False,
                lint=False,
            )

    def test_render_no_raise_without_strict(self):
        result = rsm.render(
            ":enumerate:\n:-: A\n:-: B\n::\n",
            strict=False,
            handrails=False,
        )
        assert isinstance(result, str)

    def test_render_no_raise_on_valid_input(self):
        result = rsm.render(
            "## Section\n\nHello world.\n",
            strict=True,
            handrails=False,
        )
        assert isinstance(result, str)
        assert "CST error" not in result
