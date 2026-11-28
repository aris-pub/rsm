"""With handrails, math or raw HTML followed by punctuation sits in an
inline-wrapper span. A newline right after the opening tag of that span
rendered as a gap of about 3 px before the math, as in 'f($x$)' (rsm-7fy)."""

import pytest
from playwright.sync_api import Page

import rsm

pytestmark = pytest.mark.interactive

# The distance from the right edge of the last character before the wrapper
# that is not a space to the left edge of the first element inside the wrapper.
MEASURE = """() => {
    const w = document.querySelector('.manuscriptwrapper p .inline-wrapper');
    const before = w.previousSibling;
    const end = before.data.trimEnd().length;
    const r = document.createRange();
    r.setStart(before, end - 1);
    r.setEnd(before, end);
    const rects = r.getClientRects();
    const left = rects[rects.length - 1].right;
    return w.firstElementChild.getBoundingClientRect().left - left;
}"""


def _gap(page: Page, tmp_path, line: str) -> float:
    html = rsm.build(f"# T\n\n{line}\n", handrails=True, lint=False, standalone=True)
    out = tmp_path / "gap.html"
    out.write_text(html)
    page.goto(out.as_uri(), wait_until="load")
    if "$" in line:
        page.wait_for_selector(
            "p span.math mjx-container", state="attached", timeout=15_000
        )
    page.wait_for_timeout(300)
    return page.evaluate(MEASURE)


@pytest.mark.parametrize(
    "line",
    [
        "Take f($x$) now.",
        "Then 1-$K$. Done.",
        "Take f(:html:{:alt: x} <b>x</b> ::) now.",
    ],
    ids=["math-paren", "math-hyphen", "rawhtml-paren"],
)
def test_no_gap_before_wrapped_math(page: Page, tmp_path, line):
    assert abs(_gap(page, tmp_path, line)) < 0.5


def test_space_before_wrapped_math_is_kept(page: Page, tmp_path):
    assert _gap(page, tmp_path, "Word $x$. Done.") > 2
