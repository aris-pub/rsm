"""A long inline link must wrap between words along with the surrounding text,
not move to its own line as a single inline-block box (rsm-1ue).

Links used to be display:inline-block, which made each <a> one atomic box: a
link longer than the space left on the line jumped to its own line(s) and left
the following punctuation stranded. The fix keeps links inline and relies on
padding plus overflow-wrap for the touch target and bare-URL breaking.
"""

import pytest
from playwright.sync_api import Page

import rsm

pytestmark = pytest.mark.interactive

# The reference sentence from the bead: a long title link between a leading
# clause and a trailing citation, so both the wrap and the stranded-comma
# symptom show at a narrow width.
REF_SENTENCE = """# T

A digestion of J. Bourgain, :url:https://link.springer.com/article/10.1007/BF02776078, On the distribution of the Fourier spectrum of Boolean functions::, Israel J. Math. 52 (1985), 46-52.

A plain paragraph with no link at all, just ordinary running text long enough to span two lines so we can check nothing inflates its line spacing.
"""

LONG_URL = "https://example.com/" + "averylongunbrokenpathsegmentwithnospaces" * 4
BARE_URL_SENTENCE = f"""# T

See the source at :url:{LONG_URL}:: which is one unbreakable string.
"""


def _build(src: str, tmp_path) -> str:
    html = rsm.build(src, handrails=True, lint=False, standalone=True)
    out = tmp_path / "links.html"
    out.write_text(html)
    return out.as_uri()


def test_long_inline_link_wraps_like_text(page: Page, tmp_path):
    page.set_viewport_size({"width": 375, "height": 900})
    page.goto(_build(REF_SENTENCE, tmp_path), wait_until="load")
    page.wait_for_timeout(300)

    link = "a[href*='springer']"

    # An inline-block link is one atomic box, so getClientRects() returns a single
    # rect no matter how many lines it fills. An inline link that breaks between
    # words reports one rect per line fragment.
    rects = page.eval_on_selector(
        link,
        "e => [...e.getClientRects()].map(r => ({top: Math.round(r.top), right: Math.round(r.right)}))",
    )
    assert len(rects) >= 2, rects

    assert page.eval_on_selector(link, "e => getComputedStyle(e).display") == "inline"

    # The text right after the link (the comma) sits on the same line as the
    # link's last fragment and immediately follows it, so it is not stranded.
    follows = page.eval_on_selector(
        link,
        """e => {
            const last = [...e.getClientRects()].pop();
            const r = document.createRange();
            r.selectNodeContents(e.nextSibling);
            const nr = r.getClientRects()[0];
            return {dTop: Math.abs(nr.top - last.top), gap: nr.left - last.right};
        }""",
    )
    assert follows["dTop"] <= 4, follows
    assert -2 <= follows["gap"] <= 4, follows

    # A paragraph without links keeps the normal single line pitch: its two text
    # lines are exactly one line-height apart, with no extra spacing.
    pitch = page.evaluate(
        """() => {
            const ps = [...document.querySelectorAll('.manuscriptwrapper p')];
            const p = ps.find(el => !el.querySelector('a'));
            const r = document.createRange();
            r.selectNodeContents(p);
            const tops = [...new Set([...r.getClientRects()].map(x => Math.round(x.top)))].sort((a, b) => a - b);
            const lh = parseFloat(getComputedStyle(p).lineHeight);
            return {gap: tops[1] - tops[0], lineHeight: lh, lines: tops.length};
        }"""
    )
    assert pitch["lines"] >= 2, pitch
    assert abs(pitch["gap"] - pitch["lineHeight"]) <= 1, pitch

    assert page.evaluate(
        "() => document.documentElement.scrollWidth <= document.documentElement.clientWidth"
    )


@pytest.mark.parametrize("width", [375, 1280])
@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_bare_url_never_scrolls_horizontally(page: Page, tmp_path, width, scheme):
    page.emulate_media(color_scheme=scheme)
    page.set_viewport_size({"width": width, "height": 700})
    page.goto(_build(BARE_URL_SENTENCE, tmp_path), wait_until="load")
    page.wait_for_timeout(200)

    # overflow-wrap lets the unbreakable URL break mid-string across fragments.
    assert page.eval_on_selector("a[href*='example.com']", "e => e.getClientRects().length") >= 2
    assert page.evaluate(
        "() => document.documentElement.scrollWidth <= document.documentElement.clientWidth"
    )
