"""Visual guards for author-year citations (rsm-3ez).

Author-year mode renders :cite: as "(Author, Year)" in the text and an
unnumbered, author-sorted bibliography with a/b year suffixes on works that
would otherwise cite identically. These snapshots lock that appearance. The
dark twin guards the citation link colour against the page the way rsm-si1 and
rsm-3y7 established, where the light snapshot can be blind to near-white chrome.
"""

from textwrap import dedent

import pytest
from playwright.sync_api import Page

RSM_READY = "() => window.__rsmInitialized === true"

SRC = dedent(
    """\
    # Author-year citations

    :config: {
      :citation-style: parens-author-year
    }
    ::

    An embedding result :cite:bourgainA:: has a companion :cite:bourgainB::,
    beside a multi-author work :cite:arora::.

    :references:

    @article{bourgainA, title={Aaa embedding}, author={Bourgain, Jean}, year={1985}, journal={Israel J. Math.} }
    @article{bourgainB, title={Bbb embedding}, author={Bourgain, Jean}, year={1985}, journal={Israel J. Math.} }
    @article{arora, title={Expander flows}, author={Arora, Sanjeev and Lee, James R and Naor, Assaf}, year={2008}, journal={J. ACM} }

    ::
    """
)


@pytest.mark.visual
def test_author_year_citations_light(
    serve_rsm_html: callable, page: Page, assert_snapshot: callable
) -> None:
    page.set_viewport_size({"width": 1280, "height": 900})
    serve_rsm_html(SRC)
    page.wait_for_function(RSM_READY, timeout=10_000)
    assert_snapshot(page.screenshot())


@pytest.mark.visual
def test_author_year_citations_dark(
    serve_rsm_html: callable, page: Page, assert_snapshot: callable
) -> None:
    page.set_viewport_size({"width": 1280, "height": 900})
    serve_rsm_html(SRC)
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.eval_on_selector("html", "h => h.classList.add('dark-theme')")
    page.wait_for_timeout(100)
    assert_snapshot(page.screenshot())
