"""Invalid input that the parser repairs with a MISSING node is reported (rsm-pn7).

tree-sitter marks some invalid input with an inserted (MISSING) token instead of
an ERROR node. These are reported as ERROR nodes are: logged with their
position, shown as a CST error in the page, and fatal with strict=True. The one
exception is a paragraph end inserted right before '::': the scanner cannot
find a paragraph end between an inline tag and '::' on the same line, so
correct text such as 'First, $x$ is real.::' gets one."""

import logging

import pytest

import rsm
from rsm.transformer import RSMTransformerError


def _render(src: str, strict: bool = False) -> str:
    return rsm.render(src, handrails=False, source_offsets=False, strict=strict)


def _errors(caplog) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.getMessage() == "The CST contains errors."]


UNCLOSED_TOC = "# Doc\n\nSome text.\n\n:toc:\n\n## One\n\nText.\n"

# The first '::' closes the :ref:, and the last one closes the :assume:, so
# the step is never closed (as in two test fixtures, fixed on 2026-11-19).
UNCLOSED_STEP = (
    ":theorem: {:label: t}\n  X.\n::\n\n"
    ":proof:\n  :step: :assume: the radius of :ref:t:: is real. ::\n::\n\nAfter the proof.\n"
)


@pytest.mark.parametrize("src", [UNCLOSED_TOC, UNCLOSED_STEP], ids=["toc", "step"])
def test_a_missing_closer_is_reported(src, caplog):
    with caplog.at_level(logging.WARNING):
        html = _render(src)
    assert "CST error" in html
    records = _errors(caplog)
    assert records, caplog.text
    assert all(r.start_row >= 1 for r in records)


@pytest.mark.parametrize("src", [UNCLOSED_TOC, UNCLOSED_STEP], ids=["toc", "step"])
def test_a_missing_closer_fails_strict_mode(src):
    with pytest.raises(RSMTransformerError, match="CST errors"):
        _render(src, strict=True)


def test_the_unclosed_toc_is_reported_where_the_closer_is_missing(caplog):
    with caplog.at_level(logging.WARNING):
        _render(UNCLOSED_TOC)
    (rec,) = _errors(caplog)
    # The parser closes the :toc: right after its tag, on line 5.
    assert rec.start_row == 5, caplog.text


@pytest.mark.parametrize(
    "src",
    [
        ":theorem: {:label: t}\n  X.\n::\n\n:proof:\n"
        "  :step: {:label: s1} First, $x$ is real.::\n"
        "  :step: :assume: $x > 0$ :: ::\n::\n\nAfter.\n",
        ":theorem: {:label: t}\n  X.\n::\n\n:proof:\n"
        "  :step: Then it holds, by :ref:t::.::\n::\n",
    ],
    ids=["math-then-halmos", "ref-then-halmos"],
)
def test_a_paragraph_end_before_a_halmos_is_not_reported(src, caplog):
    with caplog.at_level(logging.WARNING):
        html = _render(src)
    assert "CST error" not in html
    assert not _errors(caplog), caplog.text
    _render(src, strict=True)


@pytest.mark.parametrize(
    "path",
    [
        "examples-rsm/atiyah.rsm",
        "examples-rsm/indefinite.rsm",
        "tests/visual/fixtures/sidebar.rsm",
        "tests/interactive/fixtures/sidebar.rsm",
        "tests/interactive/fixtures/rawhtml.rsm",
    ],
)
def test_the_fixed_examples_and_fixtures_have_no_errors(path, caplog):
    src = open(path).read()
    with caplog.at_level(logging.WARNING):
        _render(src)
    assert not _errors(caplog), caplog.text


@pytest.mark.parametrize(
    "src",
    [
        ":theorem: {}\n  Body.\n::\n",
        ":paragraph: {} Body.\n",
        "A :span:{}word:: here.\n",
    ],
    ids=["block", "paragraph", "span"],
)
def test_an_empty_meta_is_valid(src, caplog):
    with caplog.at_level(logging.WARNING):
        html = _render(src)
    assert "CST error" not in html
    assert not _errors(caplog), caplog.text
    _render(src, strict=True)


def test_a_block_tag_in_the_middle_of_a_line_is_reported(caplog):
    src = "# T\n\nThis paragraph ends early :section: And this\nis in the section. ::\n"
    with caplog.at_level(logging.WARNING):
        _render(src)
    assert any(r.start_row == 3 for r in _errors(caplog)), caplog.text
