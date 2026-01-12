import pytest

import rsm
from conftest import compare_have_want


def test_simple():
    compare_have_want(
        have="""\
        # My Title

        :enumerate:
          {:label: enm-foo}

          :-: {:label: itm-1} Foo bar.

          :-: {:label: itm-2} Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem
            ipsum dolor sit amet.

          :-: {:label: itm-3}
          Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem
          ipsum dolor sit amet.

        ::

        :itemize:
          {:label: itm-foo}

          :-: {:label: itm-4} Foo bar.

          :-: {:label: itm-5} Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem
            ipsum dolor sit amet.

          :-: {:label: itm-6}
          Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem
          ipsum dolor sit amet.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <ol id="enm-foo" class="enumerate" data-nodeid="1">

        <li id="itm-1" class="item" data-nodeid="2">
        Foo bar.
        </li>

        <li id="itm-2" class="item" data-nodeid="4">
        Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet.
        </li>

        <li id="itm-3" class="item" data-nodeid="6">
        Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet.
        </li>

        </ol>

        <ul id="itm-foo" class="itemize" data-nodeid="8">

        <li id="itm-4" class="item" data-nodeid="9">
        Foo bar.
        </li>

        <li id="itm-5" class="item" data-nodeid="11">
        Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet.
        </li>

        <li id="itm-6" class="item" data-nodeid="13">
        Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet.
        </li>

        </ul>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_item_with_wrong_parent():
    with pytest.raises(rsm.nodes.RSMNodeError):
        compare_have_want(
            have="""\
            :-: Foo bar.
            """,
            want="XXX",
        )

    with pytest.raises(rsm.nodes.RSMNodeError):
        compare_have_want(
            have="""\
            # Some section

            :-: Foo bar.
            """,
            want="XXX",
        )

    compare_have_want(
        have="""\
        ## Some section

        Lorem ipsum - Foo bar.
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. Some section</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Lorem ipsum - Foo bar.</p>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )
