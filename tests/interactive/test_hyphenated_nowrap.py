"""A heading never breaks a line right after the hyphen in "K-theory" (rsm-69h).

Chromium and Firefox allow a line break after a hyphen, which left "theory"
alone on the next line of the heading "Floor, ceiling, slopes, and K-theory" at
some widths. RSM wraps each hyphenated word in a no-wrap span, so the word moves
to the next line whole. The math case ($K$-theory) is a math element followed by
the text "-theory", and must stay whole too, as must **K**-theory.
"""

import pytest
from playwright.sync_api import Page

import rsm

pytestmark = pytest.mark.interactive

HEADING = "Floor, ceiling, slopes, and {}"

# Where "K" and "theory" sit, and how many lines the heading fills.
MEASURE = """() => {
    const h = document.querySelector('.manuscriptwrapper h2');
    const walker = document.createTreeWalker(h, NodeFilter.SHOW_TEXT);
    let theory = null, plainK = null;
    while (walker.nextNode()) {
        const n = walker.currentNode;
        if (n.parentElement.closest('.math, strong')) continue;
        const i = n.data.indexOf('theory');
        if (i >= 0) theory = [n, i];
        const k = n.data.search(/K[-\u2013]/);
        if (k >= 0) plainK = [n, k];
    }
    const rectOf = ([n, i], len) => {
        const r = document.createRange();
        r.setStart(n, i);
        r.setEnd(n, i + len);
        return r.getClientRects()[0];
    };
    const piece = h.querySelector('.math, strong');
    const k = piece ? piece.getBoundingClientRect() : rectOf(plainK, 1);
    const t = rectOf(theory, 6);
    const lineHeight = parseFloat(getComputedStyle(h).lineHeight);
    return {
        kBottom: k.bottom,
        theoryBottom: t.bottom,
        lines: Math.round(h.getBoundingClientRect().height / lineHeight),
    };
}"""


def _build(word: str, tmp_path) -> str:
    src = f"# T\n\n## {HEADING.format(word)}\n\nSome text.\n"
    html = rsm.build(src, handrails=True, lint=False, standalone=True)
    out = tmp_path / "hyphenated.html"
    out.write_text(html)
    return out.as_uri()


@pytest.mark.parametrize(
    "word",
    ["K-theory", "$K$-theory", "**K**-theory", "**graded K**-theory", "K\u2013theory"],
    ids=["plain", "math", "bold", "bold-with-space", "en-dash"],
)
def test_heading_does_not_break_after_hyphen(page: Page, tmp_path, word):
    page.set_viewport_size({"width": 800, "height": 900})
    page.goto(_build(word, tmp_path), wait_until="load")
    if "$" in word:
        page.wait_for_selector("h2 span.math mjx-container", state="attached", timeout=15_000)
    page.wait_for_timeout(300)

    wrapped = False
    for width in range(260, 801, 5):
        page.set_viewport_size({"width": width, "height": 900})
        m = page.evaluate(MEASURE)
        wrapped = wrapped or m["lines"] > 1
        assert abs(m["kBottom"] - m["theoryBottom"]) < 8, (width, m)
    # The heading must wrap at some of these widths, or the test checks nothing.
    assert wrapped
