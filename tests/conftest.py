# conftest.py
#
# Global pytest configuration and fixtures.
#
# NOTE: the definitions here are only visible to tests within this directory and its
# children dirs.  In particular, for pytest to run doctests (or other tests) in the
# source directory (../rsm/), there needs to be a different conftest.py file in that
# directory.

import rsm
import pytest
from textwrap import dedent
import sys
from icecream import ic

# ic.disable()

sys.setrecursionlimit(100)

# Several tests use an empty manuscript.
EMPTY_WANT = """\
<body>

<div class="manuscriptwrapper">

<div class="manuscript">

<section class="level-1">

</section>

</div>

</div>

</body>
"""


def compare_have_want(have, want, handrails=False):
    """Compare obtained output (have) against the desired output (want)."""
    want = dedent(want).lstrip()
    have = dedent(have).lstrip()
    have = rsm.render(have, handrails=handrails).lstrip()

    try:
        assert have == want
    except AssertionError as with_space:
        try:
            assert "".join(have.split()) == "".join(want.split())
        except AssertionError:
            raise AssertionError("Difference in content") from with_space
        raise AssertionError("Difference in whitespace only") from with_space


def compare_have_want_handrails(have, want):
    """Same as compare_have_want but generates a manuscript with handrails."""
    return compare_have_want(have, want, True)
