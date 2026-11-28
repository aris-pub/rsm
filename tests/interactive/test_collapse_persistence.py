"""Interactive regression: a reader's collapse choices persist across reload.

handrails.js writes each block's collapsed state to localStorage and replays it
on load. This must hold for *every* collapsible handrail, including section
headings (which carry no data-nodeid) and the unlabeled blocks (document title,
auto-generated ToC and bibliography), not just the labeled content blocks.

This lives in the interactive (behavioral) suite, not the visual one: the thing
under test is *state surviving a reload*, which a screenshot diff cannot see.
The collapsed *appearance* is already covered by the visual snapshots
(test_states / test_nesting); duplicating it here would test the wrong thing.
"""

import pytest
from playwright.sync_api import Page

import rsm

pytestmark = pytest.mark.interactive

RSM_READY = "() => window.__rsmShown === true"

# Every block the reader can collapse by clicking its chevron, in document order
# (stable for a given build), so the Nth entry before reload is the Nth after.
_COLLAPSIBLE = """
  const blocks = [...document.querySelectorAll('.hr')].filter(h =>
    !h.closest('.rsm-source') &&
    h.querySelector(':scope > .hr-collapse-zone .hr-collapse'));
"""

_COLLAPSE_ALL = (
    "() => {"
    + _COLLAPSIBLE
    + """
  for (const h of blocks) {
    if (!h.classList.contains('hr-collapsed'))
      h.querySelector(':scope > .hr-collapse-zone .hr-collapse').click();
  }
  return blocks.length;
}"""
)

_FLAGS = (
    "() => {"
    + _COLLAPSIBLE
    + r"""
  return blocks.map(h => ({
    collapsed: h.classList.contains('hr-collapsed'),
    heading: h.classList.contains('heading'),
    text: (h.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 40),
  }));
}"""
)


def _load(page: Page, server: str) -> None:
    page.goto(f"{server}/collapse-persist.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)


def test_section_heading_collapse_persists(page: Page, interactive_server: str):
    """The original bug: a section heading carries no data-nodeid, so collapsing
    a whole section did not survive a reload."""
    _load(page, interactive_server)
    heading = page.locator("section#sec-alpha > .heading.hr")
    heading.locator(":scope > .hr-collapse-zone .hr-collapse").click()
    assert page.evaluate(
        "() => document.querySelector('section#sec-alpha > .heading.hr')"
        ".classList.contains('hr-collapsed')"
    )
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    assert page.evaluate(
        "() => document.querySelector('section#sec-alpha > .heading.hr')"
        ".classList.contains('hr-collapsed')"
    ), "section heading collapse did not persist across reload"


def test_every_collapsible_block_persists(page: Page, interactive_server: str):
    """Collapse every clickable block, reload, and every one must stay collapsed."""
    _load(page, interactive_server)
    n = page.evaluate(_COLLAPSE_ALL)
    assert n > 0, "fixture exposes no collapsible blocks"
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    flags = page.evaluate(_FLAGS)
    dropped = [f for f in flags if not f["collapsed"]]
    assert not dropped, (
        f"{len(dropped)}/{len(flags)} blocks did not persist collapsed; "
        f"dropped: {[(f['heading'], f['text']) for f in dropped]}"
    )


# Three builds of one document, served one after the other at the same URL, so
# that they share one localStorage entry. V2 adds a paragraph before the
# theorems and edits the labelled theorem. V3 edits the unlabelled theorem.
_V1 = """# Folds

:theorem:

  An unlabelled theorem.

::

:theorem: {:label: thm-kept}

  A labelled theorem.

::

The last paragraph.
"""
_V2 = _V1.replace(
    ":theorem:\n\n  An", "A new first paragraph.\n\n:theorem:\n\n  An"
).replace("A labelled theorem.", "A labelled theorem, edited.")
_V3 = _V1.replace("An unlabelled theorem.", "An unlabelled theorem, edited.")

_UNLABELLED = ".theorem.hr:not(#thm-kept)"


def _serve(page: Page, server: str, source: str) -> None:
    html = rsm.build(source=source, handrails=True, standalone=False)
    page.unroute("**/fold-change.html")
    page.route(
        "**/fold-change.html",
        lambda route: route.fulfill(body=html, content_type="text/html"),
    )
    page.goto(f"{server}/fold-change.html")
    page.wait_for_function(RSM_READY, timeout=10_000)


def _fold(page: Page, selector: str) -> None:
    page.locator(f"{selector} > .hr-collapse-zone .hr-collapse").click()


def _collapsed_and_hidden(page: Page):
    return page.evaluate(
        r"""() => ({
          collapsed: [...document.querySelectorAll('.manuscript .hr-collapsed')]
            .map(h => (h.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 30)),
          hidden: [...document.querySelectorAll('.manuscript .hide')]
            .filter(el => !el.closest('.hr-collapsed'))
            .map(el => (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 30)),
        })"""
    )


class TestChangedDocument:
    def test_unlabelled_fold_stays_on_its_block(
        self, page: Page, interactive_server: str
    ):
        _serve(page, interactive_server, _V1)
        page.evaluate("() => localStorage.clear()")
        _fold(page, _UNLABELLED)
        _serve(page, interactive_server, _V2)
        state = _collapsed_and_hidden(page)
        assert len(state["collapsed"]) == 1, state
        assert page.locator(_UNLABELLED).evaluate(
            "el => el.classList.contains('hr-collapsed')"
        )
        assert state["hidden"] == [], state

    def test_labelled_fold_stays_on_its_label(
        self, page: Page, interactive_server: str
    ):
        _serve(page, interactive_server, _V1)
        page.evaluate("() => localStorage.clear()")
        _fold(page, "#thm-kept")
        _serve(page, interactive_server, _V2)
        assert page.locator("#thm-kept").evaluate(
            "el => el.classList.contains('hr-collapsed')"
        )
        assert len(_collapsed_and_hidden(page)["collapsed"]) == 1

    def test_fold_of_edited_unlabelled_block_is_dropped(
        self, page: Page, interactive_server: str
    ):
        _serve(page, interactive_server, _V1)
        page.evaluate("() => localStorage.clear()")
        _fold(page, _UNLABELLED)
        _serve(page, interactive_server, _V3)
        assert _collapsed_and_hidden(page) == {"collapsed": [], "hidden": []}

    def test_keys_that_match_no_block_are_ignored(
        self, page: Page, interactive_server: str
    ):
        _serve(page, interactive_server, _V1)
        page.evaluate(
            """() => localStorage.setItem('rsm-collapse:' + location.pathname,
                 JSON.stringify({'l:gone': true, 'h:00000000': true, 'n:1': true,
                                 'n:2': true, 'n:3': true}))"""
        )
        _serve(page, interactive_server, _V1)
        assert _collapsed_and_hidden(page) == {"collapsed": [], "hidden": []}

    def test_saved_fold_on_a_block_that_cannot_fold_is_ignored(
        self, page: Page, interactive_server: str
    ):
        _serve(page, interactive_server, _V1)
        page.evaluate(
            """() => {
              const p = [...document.querySelectorAll('.manuscript .paragraph.hr')]
                .find(el => el.textContent.includes('The last paragraph'));
              const state = {};
              if (p.dataset.hash) state['h:' + p.dataset.hash] = true;
              if (p.dataset.nodeid) state['n:' + p.dataset.nodeid] = true;
              localStorage.setItem('rsm-collapse:' + location.pathname,
                                   JSON.stringify(state));
            }"""
        )
        _serve(page, interactive_server, _V1)
        assert _collapsed_and_hidden(page) == {"collapsed": [], "hidden": []}


def test_generated_headings_persist(page: Page, interactive_server: str):
    """The notes list and the bibliography have no label and no source text."""
    page.goto(f"{interactive_server}/notes.html")
    page.wait_for_function(RSM_READY, timeout=10_000)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    folded = """() => [...document.querySelectorAll('.manuscript .heading.hr')]
      .filter(h => !h.dataset.hash)
      .map(h => h.classList.contains('hr-collapsed'))"""
    page.evaluate(
        """() => [...document.querySelectorAll('.manuscript .heading.hr')]
          .filter(h => !h.dataset.hash)
          .forEach(h => h.querySelector(':scope > .hr-collapse-zone .hr-collapse').click())"""
    )
    assert page.evaluate(folded) == [True, True]
    page.reload()
    page.wait_for_function(RSM_READY, timeout=10_000)
    assert page.evaluate(folded) == [True, True]
