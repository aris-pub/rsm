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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

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

        </main>

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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section id="sec-1" class="section level-2" data-nodeid="1">

        <h2>1. Some section</h2>

        <div class="paragraph" data-nodeid="2">

        <p>Lorem ipsum - Foo bar.</p>

        </div>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_nested_itemize_renders_nested():
    import rsm

    src = "## S\n\n:itemize:\n\n  :-: One\n\n  :--: Two\n\n::\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert 'class="error"' not in h, h
    one = h.index("One")
    rest = h[one:]
    # The level-2 item must nest: a <ul> opens inside One's <li>, before it closes.
    assert "<ul" in rest and rest.index("<ul") < rest.index("</li>"), h
    assert "Two" in h


def test_nested_enumerate_renders_nested():
    import rsm

    src = "## S\n\n:enumerate:\n\n  :-: A\n\n  :--: B\n\n::\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert 'class="error"' not in h, h
    rest = h[h.index("A"):]
    assert "<ol" in rest and rest.index("<ol") < rest.index("</li>"), h


def test_three_level_nesting():
    import rsm

    src = "## S\n\n:itemize:\n\n  :-: A\n\n  :--: B\n\n  :---: C\n\n  :-: D\n\n::\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert 'class="error"' not in h, h
    assert h.count("<ul") == 3  # outer plus two nested levels


def test_nesting_down_then_up():
    import rsm

    src = "## S\n\n:itemize:\n\n  :-: A\n\n  :--: B\n\n  :-: C\n\n::\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert 'class="error"' not in h, h
    assert h.count("<ul") == 2  # outer plus one nested; C is a top-level sibling


def test_depth_jump_is_error_node():
    import rsm

    src = "## S\n\n:itemize:\n\n  :-: A\n\n  :---: C\n\n::\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert 'class="error"' in h and "skips the level above" in h
    assert "A" in h and "C" in h  # the rest of the document still renders


def test_list_starting_deep_is_error():
    import rsm

    src = "## S\n\n:itemize:\n\n  :--: B\n\n::\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert 'class="error"' in h  # level 2 with no level-1 parent


def test_four_dashes_is_not_an_item():
    import rsm

    src = "## S\n\n:itemize:\n\n  :----: X\n\n::\n"
    h = rsm.render(src, handrails=False, source_offsets=False)
    assert 'class="error"' in h  # 3-level cap: :----: is flagged, not silent
