# conftest.py
#
# Global pytest configuration and fixtures.
#
# NOTE: the definitions here are only visible to tests within this directory and its
# children dirs.  In particular, for pytest to run doctests (or other tests) in the
# source directory (../rsm/), there needs to be a different conftest.py file in that
# directory.

import sys
from textwrap import dedent

import rsm

# ic.disable()


# The rsm renderer walks document trees recursively, so tests cap the recursion
# limit to surface runaway recursion early. Apply it only once collection is done:
# setting it at import time also constrains pytest's assertion-rewrite import hook,
# which under xdist imports test modules on a much deeper (execnet) call stack and
# overflows a limit of 100 during collection (RecursionError on Python 3.13, where
# the pathlib import path is deeper than on the 3.12 CI runners). See potf-icn.
def pytest_collection_finish(session):
    sys.setrecursionlimit(100)

# Several tests use an empty manuscript.
EMPTY_WANT = """\
<body data-accent="blue" data-lang="en" data-typography="sans-serif">

<main class="manuscriptwrapper">

<div class="manuscript" data-nodeid="0">

<section class="level-1">

</section>

</div>

</main>

</body>
"""


def _strip_generated_blocks(html: str) -> str:
    """Remove generated singleton blocks, data-menu attrs, and menu zone content for test comparison."""
    import re
    html = re.sub(r'<svg id="hr-icon-defs"[^>]*>.*?</svg>\n?', '', html, flags=re.DOTALL)
    html = re.sub(r'<div id="hr-menu-singleton"[^>]*>.*?</div>\n</div>\n</div>\n?', '', html, flags=re.DOTALL)
    html = re.sub(r'\s*data-menu-[\w-]+="[^"]*"', '', html)
    # Synthetic block ids (id="n42") are generated per build so every block is
    # hash-addressable; ignore them in structural comparisons. Semantic ids
    # (id="thm-x", id="sec-intro") do not match and are still asserted. Emission
    # of the synthetic ids is covered by tests/test_block_ids.py.
    html = re.sub(r'\s*id="n\d+"', '', html)
    # Normalize menu zones: strip any content inside hr-menu-zone divs
    html = re.sub(
        r'<div class="hr-menu-zone">\s*(?:<div class="hr-menu">.*?</div>\s*)*</div>',
        '<div class="hr-menu-zone">\n</div>',
        html,
        flags=re.DOTALL,
    )
    return html


def compare_have_want(have, want, handrails=False):
    """Compare obtained output (have) against the desired output (want)."""
    want = dedent(want).lstrip()
    have = dedent(have).lstrip()
    have = rsm.render(have, handrails=handrails, add_source=False).lstrip()
    have = _strip_generated_blocks(have)
    want = _strip_generated_blocks(want)

    try:
        assert have == want
    except AssertionError:
        assert "".join(have.split()) == "".join(want.split()), "Difference in content"


def compare_have_want_handrails(have, want):
    """Same as compare_have_want but generates a manuscript with handrails."""
    return compare_have_want(have, want, True)
