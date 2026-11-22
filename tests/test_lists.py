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

        <p>Lorem ipsum <span class="hyphenated">-</span> Foo bar.</p>

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
    rest = h[h.index("A") :]
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


# Lists are paragraph content: a list written between two runs of text with no
# blank line belongs to that paragraph, as display math does.


def _body(src, handrails=False):
    import re

    html = rsm.render(src, handrails=handrails, source_offsets=False, strict=True)
    body = html[html.index('<div class="manuscript"') :]
    body = re.sub(r'\s*data-nodeid="\d+"', "", body)
    return "".join(body.split())


LIST_IN_PARAGRAPH = """\
Before the list
:itemize:

  :-: one

  :-: two

::
after the list.
"""


def test_list_inside_paragraph_is_one_paragraph():
    body = _body(LIST_IN_PARAGRAPH)
    assert body.count('class="paragraph"') == 1, body
    assert (
        '<divclass="paragraph"><p>Beforethelist</p>'
        '<ulclass="itemize"><liclass="item">one</li><liclass="item">two</li></ul>'
        "<p>afterthelist.</p></div>"
    ) in body, body


def test_list_ending_paragraph():
    body = _body("Before the list\n:itemize:\n\n  :-: one\n\n::\n")
    assert (
        '<divclass="paragraph"><p>Beforethelist</p>'
        '<ulclass="itemize"><liclass="item">one</li></ul></div>'
    ) in body, body


def test_list_inside_paragraph_handrails():
    body = _body(LIST_IN_PARAGRAPH, handrails=True)
    assert body.count('class="paragraphhr') == 1, body
    par = body[body.index('class="paragraphhr') :]
    assert par.index("<p>Beforethelist</p>") < par.index('<ulclass="itemize">'), par
    assert par.index("</ul>") < par.index("<p>afterthelist.</p>"), par


def test_list_with_blank_lines_is_its_own_block():
    body = _body(
        "Before the list.\n\n:itemize:\n\n  :-: one\n\n::\n\nAfter the list.\n"
    )
    assert body.count('class="paragraph"') == 2, body
    assert '<p>Beforethelist.</p></div><ulclass="itemize">' in body, body


def test_list_inside_paragraph_in_theorem():
    src = (
        ":theorem:\n\n  If\n  :enumerate:\n\n    :-: a,\n\n    :-: b,\n\n"
        "  ::\n  then c.\n\n::\n"
    )
    body = _body(src)
    assert (
        '<divclass="paragraph"><p>If</p><olclass="enumerate">'
        '<liclass="item">a,</li><liclass="item">b,</li></ol><p>thenc.</p></div>'
    ) in body, body


def test_list_inside_paragraph_in_proof_step():
    src = (
        ":proof:\n\n  :step: Consider\n  :itemize:\n\n    :-: a,\n\n    :-: b.\n\n"
        "  ::\n  ::\n\n::\n"
    )
    body = _body(src)
    assert (
        '<divclass="paragraph"><p>Consider</p><ulclass="itemize">'
        '<liclass="item">a,</li><liclass="item">b.</li></ul></div>'
    ) in body, body


def test_list_inside_aside_definition():
    src = (
        "Call :aside:a,here::.\n\n:aside: {:label: a}\nSome text\n:itemize:\n\n"
        "  :-: one\n\n::\nmore text. ::\n"
    )
    body = _body(src)
    assert (
        '<divid="a"class="aside"data-note-kind="aside"><p>Sometext</p>'
        '<ulclass="itemize"><liclass="item">one</li></ul><p>moretext.</p></div>'
    ) in body, body


def test_standalone_nested_list_unchanged():
    body = _body(":itemize:\n\n  :-: one\n\n  :--: one point one\n\n  :-: two\n\n::\n")
    assert (
        '<divclass="manuscript"><sectionclass="level-1">'
        '<ulclass="itemize"><liclass="item">one<ulclass="itemize">'
        '<liclass="item">onepointone</li></ul></li><liclass="item">two</li></ul>'
        "</section></div>"
    ) in body, body


@pytest.mark.parametrize(
    "src",
    [
        pytest.param(
            ":itemize:\n\n  :-: one\n\n  Not an item.\n\n::\n", id="paragraph"
        ),
        pytest.param(
            ":itemize:\n\n  :-: one\n\n  :remark:\n\n    Not an item.\n\n  ::\n\n::\n",
            id="block",
        ),
        pytest.param(
            ":itemize:\n\n  :-: one\n\n  $$\n  x\n  $$\n\n::\n", id="mathblock"
        ),
        pytest.param(
            ":itemize:\n\n  :-: one\n  :itemize:\n\n    :-: two\n\n  ::\n\n::\n",
            id="list-in-item",
        ),
        pytest.param(
            ":figure: {\n  :path: a.png\n}\n\n  :caption: A caption\n  :itemize:\n\n"
            "    :-: one\n\n  ::\n\n::\n",
            id="list-in-caption",
        ),
        pytest.param(
            ":itemize:\n\n  :-: one\n  :algorithm:\n  x\n  ::\n\n::\n",
            id="algorithm-in-item",
        ),
        pytest.param(
            ":figure: {\n  :path: a.png\n}\n\n  :caption: A caption\n  :algorithm:\n"
            "  x\n  ::\n\n::\n",
            id="algorithm-in-caption",
        ),
    ],
)
def test_content_not_allowed_in_lists_is_an_error(src):
    from rsm.transformer import RSMTransformerError

    with pytest.raises(RSMTransformerError, match="CST errors"):
        rsm.render(src, handrails=False, source_offsets=False, strict=True)


def test_algorithm_inside_paragraph():
    body = _body("Before\n:algorithm:\nx\n::\nafter.\n")
    assert body.count('class="paragraph"') == 1, body
    assert (
        '<divclass="paragraph"><p>Before</p><divclass="algorithm">'
        '<preclass="pseudocode">x</pre></div><p>after.</p></div>'
    ) in body, body


def test_mathblock_and_codeblock_inside_paragraph_unchanged():
    math = _body("Before\n$$\nx\n$$\nafter.\n")
    assert (
        '<divclass="paragraph"><p>Before</p><divclass="mathblock">$$x$$</div>'
        "<p>after.</p></div>"
    ) in math, math
    code = _body("Before\n```\nx\n```\nafter.\n")
    assert (
        '<divclass="paragraph"><p>Before</p><divclass="codeblock">'
        "<pre><code>x</code></pre></div><p>after.</p></div>"
    ) in code, code


def test_codeblock_inside_paragraph_handrails_reopens_p():
    body = _body("Before\n```\nx\n```\nafter.\n", handrails=True)
    assert "<p>after.</p>" in body, body


@pytest.mark.parametrize("block", ["$$\n  x\n  $$", "```\n  x\n  ```"])
@pytest.mark.parametrize("handrails", [False, True])
def test_block_inside_item_writes_no_p(block, handrails):
    # A list item opens no <p>, so a block inside it must not close or open one.
    body = _body(f":itemize:\n\n  :-: Before\n  {block}\n  after.\n\n::\n", handrails)
    assert "Before</p>" not in body and "<p>after." not in body, body
