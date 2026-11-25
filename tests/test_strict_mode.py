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


def test_strict_build_fails_on_a_note_call_right_after_a_word():
    with pytest.raises(RSMTransformerError, match="Put a space before :note:"):
        rsm.build(
            source="A fact:note:n1:: and.\n\n:note: {:label: n1} The note. ::\n",
            strict=True,
            handrails=False,
            lint=False,
        )


# Positions in the strict error list count lines and columns from 1, as the log
# and the page do (rsm-n0k8).


def _strict_error(source: str) -> str:
    with pytest.raises(RSMTransformerError) as info:
        rsm.build(source=source, strict=True, handrails=False, lint=False)
    return str(info.value)


def test_strict_error_list_counts_positions_from_1():
    assert "  - (3, 1) - (3, 3): ::" in _strict_error("A.\n\n::\n")


def test_strict_error_list_counts_missing_node_positions_from_1():
    message = _strict_error(":theorem:\n\nA theorem.\n")
    assert "  - (4, 1) - (4, 1): missing ::" in message


def test_strict_error_list_counts_note_call_after_a_word_positions_from_1():
    message = _strict_error(
        "A fact:note:n1:: and.\n\n:note: {:label: n1} The note. ::\n"
    )
    assert "  - (1, 7) - (1, 17): A footnote call must come after a space." in message


def test_strict_build_lists_only_the_call_when_its_halmos_closes_a_block():
    message = _strict_error(
        ":theorem:\n\nA fact:note:n1:: and.\n\n::\n\n:note: {:label: n1} The note. ::\n"
    )
    lines = [line for line in message.split("\n") if line.startswith("  - ")]
    assert lines == [
        "  - (3, 7) - (3, 17): A footnote call must come after a space. Put a "
        "space before :note:, as in 'fact :note:n1::'"
    ]


def test_strict_build_fails_on_an_aside_call_right_after_a_word():
    message = _strict_error(
        "A phrase:aside:a,words:: and.\n\n:aside: {:label: a} The aside. ::\n"
    )
    lines = [line for line in message.split("\n") if line.startswith("  - ")]
    assert lines == [
        "  - (1, 9) - (1, 25): An aside call must come after a space. Put a "
        "space before :aside:, as in 'phrase :aside:a,words::'"
    ]
