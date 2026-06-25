"""Render-level tests for the :static: / :dark: fallback on figures and html blocks.

The static fallback must (1) be revealed without JavaScript (via <noscript>), in
addition to the existing JS-toggleable .static-fallback element, and (2) carry a
dark variant when :dark: is set so the document's dark mode swaps it.
"""

import re
from pathlib import Path
from textwrap import dedent

import rsm

BRAIID_CSS = (
    Path(__file__).resolve().parents[1] / "braiid" / "braiid.css"
).read_text()


def _render(src: str) -> str:
    return rsm.render(dedent(src).lstrip(), handrails=False, add_source=False)


def test_braiid_css_constrains_static_fallback_width():
    """The static image must not render at its natural pixel size and overflow;
    braiid.css must cap .static-fallback (and its inner media) at the container
    width."""
    # A rule whose selector mentions .static-fallback and sets max-width: 100%.
    rule = re.search(
        r"\.static-fallback[^{}]*\{[^}]*\}", BRAIID_CSS, flags=re.DOTALL
    )
    assert rule is not None, "no .static-fallback rule found in braiid.css"
    block = rule.group(0)
    assert "max-width" in block and "100%" in block
    assert "height" in block and "auto" in block


def test_static_fallback_has_noscript_copy():
    """With JS off the static must still appear, so it is also emitted inside a
    <noscript> (which only renders when scripting is disabled)."""
    html = _render(
        """
        :figure: {
          :path: assets/interactive.svg
          :static: assets/interactive-static.png
        }
        ::
        """
    )
    # The JS-toggleable element is still present.
    assert 'class="static-fallback"' in html
    # And a noscript copy that browsers render only with JS disabled.
    assert "<noscript>" in html
    noscript = html.split("<noscript>")[1].split("</noscript>")[0]
    assert "assets/interactive-static.png" in noscript


def test_static_fallback_noscript_not_inline_hidden():
    """The noscript copy must not carry an inline display:none (that cannot be
    overridden), otherwise it would stay blank even with JS off."""
    html = _render(
        """
        :figure: {
          :path: assets/interactive.svg
          :static: assets/interactive-static.png
        }
        ::
        """
    )
    noscript = html.split("<noscript>")[1].split("</noscript>")[0]
    assert "display:none" not in noscript


def test_static_fallback_dark_variant_emitted():
    """When :dark: is set, the static fallback must reference the dark image too."""
    html = _render(
        """
        :figure: {
          :path: assets/interactive.svg
          :dark: assets/interactive-dark.png
          :static: assets/interactive-static.png
        }
        ::
        """
    )
    assert "assets/interactive-static.png" in html  # light static
    assert "assets/interactive-dark.png" in html  # dark static
    # The dark static is gated for the dark theme via a dedicated class.
    assert "static-fallback-dark" in html
    # The dark variant must also be present in the no-JS path.
    noscript = html.split("<noscript>")[1].split("</noscript>")[0]
    assert "assets/interactive-dark.png" in noscript


def test_static_fallback_no_dark_when_unset():
    """No dark static class should appear when :dark: is not provided."""
    html = _render(
        """
        :figure: {
          :path: assets/interactive.svg
          :static: assets/interactive-static.png
        }
        ::
        """
    )
    assert "static-fallback-dark" not in html


def test_html_block_static_fallback_has_noscript():
    """The :html: block path uses the same fallback machinery as :figure:."""
    html = _render(
        """
        :html: {
          :static: assets/widget-static.png
        }

        <div id="widget">interactive</div>

        ::
        """
    )
    assert "<noscript>" in html
    noscript = html.split("<noscript>")[1].split("</noscript>")[0]
    assert "assets/widget-static.png" in noscript
