"""Tests for source offset attributes on inline elements."""

import re
from textwrap import dedent

import rsm


def _render(src):
    return rsm.render(src, handrails=True, add_source=True)


def _find_source_attrs(html, tag_pattern):
    """Find data-source-start/end on elements matching a regex pattern."""
    pattern = rf'<{tag_pattern}[^>]*?data-source-start="(\d+)"[^>]*?data-source-end="(\d+)"'
    matches = re.findall(pattern, html)
    if not matches:
        pattern = rf'<{tag_pattern}[^>]*?data-source-end="(\d+)"[^>]*?data-source-start="(\d+)"'
        matches = [(b, a) for a, b in re.findall(pattern, html)]
    return [(int(s), int(e)) for s, e in matches]


class TestEmphasisSourceOffsets:
    def test_emph_span_has_source_offsets(self):
        src = "The *spectral signatures* of hub structure.\n"
        html = _render(src)
        offsets = _find_source_attrs(html, 'span class="span"')
        assert len(offsets) > 0, "Emphasis span should have source offset attributes"

    def test_emph_offsets_slice_to_source(self):
        src = "The *spectral signatures* of hub structure.\n"
        html = _render(src)
        offsets = _find_source_attrs(html, 'span class="span"')
        found = False
        for start, end in offsets:
            sliced = src[start:end]
            if "spectral" in sliced:
                assert "*spectral signatures*" in sliced or "spectral signatures" in sliced
                found = True
        assert found, f"No span slices to emphasis content. Offsets: {offsets}"


class TestMathSourceOffsets:
    def test_inline_math_has_source_offsets(self):
        src = "The value $x^2 + y^2$ is important.\n"
        html = _render(src)
        offsets = _find_source_attrs(html, 'span class="[^"]*math')
        assert len(offsets) > 0, "Math span should have source offset attributes"

    def test_inline_math_offsets_slice_to_latex(self):
        src = "The value $x^2 + y^2$ is important.\n"
        html = _render(src)
        offsets = _find_source_attrs(html, 'span class="[^"]*math')
        found = False
        for start, end in offsets:
            sliced = src[start:end]
            if "x^2" in sliced:
                found = True
        assert found, f"No math span slices to LaTeX. Offsets: {offsets}"


class TestCodeSourceOffsets:
    def test_inline_code_has_source_offsets(self):
        src = "Use the `print()` function.\n"
        html = _render(src)
        offsets = _find_source_attrs(html, 'span class="[^"]*code')
        assert len(offsets) > 0, "Code span should have source offset attributes"


class TestNoSourceOffsetsWhenDisabled:
    def test_inline_no_source_when_disabled(self):
        src = "The *spectral signatures* here.\n"
        html = rsm.render(src, handrails=True, add_source=False)
        offsets = _find_source_attrs(html, 'span class="span"')
        assert len(offsets) == 0


class TestMultipleInlineElements:
    def test_multiple_inlines_each_have_offsets(self):
        src = "Start *first* middle *second* end.\n"
        html = _render(src)
        offsets = _find_source_attrs(html, 'span class="span"')
        assert len(offsets) >= 2, f"Expected >= 2 offsets, got {len(offsets)}"

    def test_inline_offsets_dont_overlap(self):
        src = "Start *first* middle *second* end.\n"
        html = _render(src)
        offsets = _find_source_attrs(html, 'span class="span"')
        sorted_offsets = sorted(offsets)
        for i in range(len(sorted_offsets) - 1):
            assert sorted_offsets[i][1] <= sorted_offsets[i + 1][0], (
                f"Overlapping: {sorted_offsets[i]} and {sorted_offsets[i + 1]}"
            )
