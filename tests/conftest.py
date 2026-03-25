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


def _strip_svg_defs(html: str) -> str:
    """Remove the SVG icon defs block for cleaner test comparison."""
    import re
    return re.sub(r'<svg id="hr-icon-defs"[^>]*>.*?</svg>\n', '', html, flags=re.DOTALL)


def compare_have_want(have, want, handrails=False):
    """Compare obtained output (have) against the desired output (want)."""
    want = dedent(want).lstrip()
    have = dedent(have).lstrip()
    have = rsm.render(have, handrails=handrails, add_source=False).lstrip()
    have = _strip_svg_defs(have)

    try:
        assert have == want
    except AssertionError:
        assert "".join(have.split()) == "".join(want.split()), "Difference in content"


def compare_have_want_handrails(have, want):
    """Same as compare_have_want but generates a manuscript with handrails."""
    return compare_have_want(have, want, True)
