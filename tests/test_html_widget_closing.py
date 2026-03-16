"""Regression tests for HandrailsTranslator HTML tag balance.

Bug 1: leave_caption manually emitted </div> to close hr-content-zone, but the deferred
batch already contained that </div>. The duplicate </div> caused the browser to close
the <figcaption> prematurely, leaving <figure> unclosed.

Bug 2: visit_mathblock unconditionally emitted </p> without checking whether the parent
is a Paragraph. MathBlocks directly under Section/Subsection/Theorem produced stray </p>
tags that corrupted the DOM.
"""

import re
from html.parser import HTMLParser

import rsm


class MockAssetResolver:
    def __init__(self, assets: dict[str, str]):
        self.assets = assets

    def resolve_asset(self, path: str) -> str | None:
        return self.assets.get(path)


RESOLVER = MockAssetResolver({"widget.html": "<div>Widget content</div>"})

RSM_WITH_CAPTION = """\
:manuscript:

  :title: Test

  :section:
    :title: Section One

    Before the widget.

    :html: {
      :path: widget.html
    }
    :caption: This is the widget caption.
    ::

    After the widget.
"""


VOID_ELEMENTS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})


class TagBalanceChecker(HTMLParser):
    """Track open/close tag mismatches in generated HTML."""

    def __init__(self):
        super().__init__()
        self.stack: list[tuple[str, int]] = []
        self.mismatches: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_ELEMENTS:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            top = self.stack[-1][0] if self.stack else "EMPTY"
            self.mismatches.append(
                f"Line {self.getpos()[0]}: closing </{tag}> but stack top is <{top}>"
            )


def _render_handrails(source=RSM_WITH_CAPTION):
    return rsm.render(source, handrails=True, add_source=False, asset_resolver=RESOLVER)


def test_no_tag_mismatches_in_handrails_output():
    """The handrails output must have balanced HTML tags."""
    body = _render_handrails()
    checker = TagBalanceChecker()
    checker.feed(body)
    assert checker.mismatches == [], (
        "Tag mismatches found in handrails output:\n" + "\n".join(checker.mismatches)
    )


def test_figcaption_has_no_extra_closing_div():
    """leave_caption must not emit a duplicate </div> for hr-content-zone."""
    body = _render_handrails()

    # Extract the figcaption block
    fc_start = body.find("<figcaption")
    fc_end = body.find("</figcaption>")
    assert fc_start != -1, "<figcaption> not found"
    assert fc_end != -1, "</figcaption> not found"

    figcaption_block = body[fc_start : fc_end + len("</figcaption>")]

    # Count div opens and closes inside figcaption
    div_opens = len(re.findall(r"<div[\s>]", figcaption_block))
    div_closes = figcaption_block.count("</div>")
    assert div_opens == div_closes, (
        f"Mismatched divs inside <figcaption>: {div_opens} opens vs {div_closes} closes"
    )


def test_figure_closes_before_sibling_paragraph():
    body = _render_handrails()
    figure_close = body.find("</figure>")
    after_text = body.find("After the widget.")

    assert figure_close != -1, "</figure> not found in output"
    assert after_text != -1, "Sibling paragraph text not found in output"
    assert figure_close < after_text, (
        f"</figure> (pos {figure_close}) appears AFTER sibling paragraph text "
        f"(pos {after_text}); the <figure> tag is swallowing sibling content"
    )


# --- Bug 2: stray </p> from visit_mathblock on non-Paragraph parents ---

RSM_MATHBLOCK_UNDER_SECTION = """\
:manuscript:

  :title: Test

  :section:
    :title: Section One

    Text ending in an equation:

    $$
    x = 1
    $$

    $$
    y = 2
    $$

    Text after.
"""


def test_no_stray_p_close_for_mathblock_under_section():
    """visit_mathblock must not emit </p> when parent is not a Paragraph.

    When two consecutive $$ blocks appear, the second one becomes a direct child
    of Section (not Paragraph). The handrails translator must not emit </p> for it.
    """
    body = rsm.render(
        RSM_MATHBLOCK_UNDER_SECTION, handrails=True, add_source=False,
    )
    checker = TagBalanceChecker()
    checker.feed(body)
    p_mismatches = [m for m in checker.mismatches if "</p>" in m]
    assert p_mismatches == [], (
        "Stray </p> tags found:\n" + "\n".join(p_mismatches)
    )
