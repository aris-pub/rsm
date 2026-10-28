"""Notes and asides: calls, definitions, resolution, numbering and rendering."""

import logging
from html.parser import HTMLParser
from textwrap import dedent

import pytest

import rsm
from rsm import nodes


def parse(src: str) -> nodes.Manuscript:
    return rsm.tsparser.TSParser().parse(dedent(src).lstrip())


def transform(src: str) -> nodes.Manuscript:
    return rsm.transformer.Transformer().transform(parse(src))


def render(src: str, handrails: bool = False) -> str:
    return rsm.render(dedent(src).lstrip(), handrails=handrails, source_offsets=False)


def calls(tree: nodes.Node) -> list:
    return list(tree.traverse(nodeclass=nodes.NoteCall))


def defs(tree: nodes.Node) -> list:
    return list(tree.traverse(nodeclass=nodes.Note))


def errors(tree: nodes.Node) -> list:
    return list(tree.traverse(nodeclass=nodes.Error))


class _Collect(HTMLParser):
    """Collect the start tags of an HTML string as (tag, attrs dict) pairs."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict]] = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def tags_with_class(html: str, cls: str) -> list[tuple[str, dict]]:
    collector = _Collect()
    collector.feed(html)
    return [
        (tag, attrs)
        for tag, attrs in collector.tags
        if cls in (attrs.get("class") or "").split()
    ]


ONE_NOTE = """\
Some paragraph with a note at the end. :note:my-note::

:note: {:label: my-note} this is the note's contents ::
"""


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def test_parse_note_call():
    tree = parse("Some text. :note:my-note::\n")
    (call,) = calls(tree)
    assert call.target == "my-note"
    assert call.tag == "note"
    assert isinstance(call.parent, nodes.Paragraph)


def test_parse_aside_call():
    tree = parse("Some text :aside:a-1:: here.\n")
    (call,) = calls(tree)
    assert call.target == "a-1"
    assert call.tag == "aside"


def test_parse_note_definition():
    tree = parse(":note: {:label: my-note} this is the note's contents ::\n")
    (note,) = defs(tree)
    assert type(note) is nodes.Note
    assert note.label == "my-note"
    assert note.first_of_type(nodes.Text).text == "this is the note's contents"


def test_parse_aside_definition():
    tree = parse(":aside: {:label: my-aside} the aside ::\n")
    (aside,) = defs(tree)
    assert type(aside) is nodes.Aside
    assert aside.label == "my-aside"


def test_parse_definition_with_display_math():
    tree = parse(
        """\
        :note: {:label: m}
          Before
          $$
          x = 1
          $$
          after.
        ::
        """
    )
    (note,) = defs(tree)
    assert note.first_of_type(nodes.MathBlock) is not None


def test_old_inline_note_form_is_an_error(caplog):
    caplog.set_level(logging.WARNING, logger="RSM")
    src = "Some text :note: inline content :: and more.\n"
    (call,) = calls(parse(src))
    assert call.malformed
    tree = transform(src)
    assert not calls(tree)
    assert not defs(tree)
    (err,) = errors(tree)
    assert "malformed" in err.text
    assert any(
        r.levelno >= logging.ERROR and "only a label" in r.getMessage()
        for r in caplog.records
    )


@pytest.mark.parametrize("tag", ["note", "aside"])
def test_definition_without_meta_is_an_error(tag):
    src = f":{tag}: no label here ::\n"
    assert not defs(parse(src))
    tree = transform(src)
    assert not defs(tree)
    assert not calls(tree)
    assert errors(tree)


# ---------------------------------------------------------------------------
# Transformer: resolution and numbering
# ---------------------------------------------------------------------------


def test_call_resolves_to_definition():
    tree = transform(ONE_NOTE)
    (call,) = calls(tree)
    (note,) = defs(tree)
    assert call.definition is note
    assert note.call is call
    assert call.number == note.number == 1
    assert call.kind == "note"


def test_definition_before_its_call():
    tree = transform(
        """\
        :note: {:label: early} defined first ::

        Then called. :note:early::
        """
    )
    (call,) = calls(tree)
    (note,) = defs(tree)
    assert call.definition is note
    assert call.number == 1


def test_numbering_follows_call_order_across_notes_and_asides():
    tree = transform(
        """\
        First :note:c:: then :aside:a:: then :note:b::.

        :aside: {:label: b} b is an aside ::

        :note: {:label: a} a is a note ::

        :note: {:label: c} c is a note ::
        """
    )
    by_label = {d.label: d for d in defs(tree)}
    assert [c.number for c in calls(tree)] == [1, 2, 3]
    assert by_label["c"].number == 1
    assert by_label["a"].number == 2
    assert by_label["b"].number == 3


def test_kind_is_decided_by_the_definition():
    tree = transform(
        """\
        Called with the note tag. :note:x::

        :aside: {:label: x} but defined as an aside ::
        """
    )
    (call,) = calls(tree)
    assert call.kind == "aside"
    assert isinstance(call.definition, nodes.Aside)


def test_call_without_definition_is_an_error(caplog):
    caplog.set_level(logging.WARNING, logger="RSM")
    tree = transform("A call to nothing :note:missing::.\n")
    assert not calls(tree)
    (err,) = errors(tree)
    assert "missing" in err.text
    assert any(
        r.levelno >= logging.ERROR and "missing" in r.getMessage()
        for r in caplog.records
    )


def test_call_to_a_label_that_is_not_a_note_is_an_error(caplog):
    caplog.set_level(logging.WARNING, logger="RSM")
    tree = transform(
        """\
        :theorem: {:label: thm} A theorem. ::

        A call to a theorem :note:thm::.
        """
    )
    assert not calls(tree)
    assert any("thm" in e.text for e in errors(tree))
    assert any(r.levelno >= logging.ERROR for r in caplog.records)


def test_definition_called_twice_is_an_error(caplog):
    caplog.set_level(logging.WARNING, logger="RSM")
    tree = transform(
        """\
        Once :note:n:: and twice :note:n::.

        :note: {:label: n} the note ::
        """
    )
    (call,) = calls(tree)
    assert call.number == 1
    (err,) = errors(tree)
    assert '"n"' in err.text
    assert any(
        r.levelno >= logging.ERROR and "more than once" in r.getMessage()
        for r in caplog.records
    )


def test_numbering_skips_rejected_calls():
    tree = transform(
        """\
        Bad :note:nope:: then good :note:a:: and :note:b::.

        :note: {:label: a} a ::

        :note: {:label: b} b ::
        """
    )
    assert [c.number for c in calls(tree)] == [1, 2]


def test_aside_call_in_figure_caption_is_an_error(caplog):
    caplog.set_level(logging.WARNING, logger="RSM")
    tree = transform(
        """\
        :figure: {:label: fig}
          :caption: A caption :aside:a1::
        ::

        :aside: {:label: a1} the aside ::
        """
    )
    assert not calls(tree)
    assert errors(tree)
    assert any(
        r.levelno >= logging.ERROR and "caption" in r.getMessage()
        for r in caplog.records
    )


def test_note_call_to_an_aside_in_figure_caption_is_an_error():
    tree = transform(
        """\
        :figure: {:label: fig}
          :caption: A caption :note:a1::
        ::

        :aside: {:label: a1} the aside ::
        """
    )
    assert not calls(tree)
    assert errors(tree)


def test_note_call_in_figure_caption_is_allowed():
    tree = transform(
        """\
        :figure: {:label: fig}
          :caption: A caption :note:n1::
        ::

        :note: {:label: n1} the note ::
        """
    )
    (call,) = calls(tree)
    assert call.number == 1
    assert not errors(tree)


def test_unused_definition_warns_and_is_dropped(caplog):
    caplog.set_level(logging.WARNING, logger="RSM")
    tree = transform(
        """\
        No calls here.

        :note: {:label: lonely} never called ::
        """
    )
    assert not defs(tree)
    assert any(
        r.levelno == logging.WARNING and "lonely" in r.getMessage()
        for r in caplog.records
    )


# ---------------------------------------------------------------------------
# Translator
# ---------------------------------------------------------------------------


def test_marker_markup():
    html = render(ONE_NOTE)
    ((tag, attrs),) = tags_with_class(html, "note-marker")
    assert tag == "a"
    assert attrs["href"] == "#my-note"
    assert attrs["data-note-number"] == "1"
    assert attrs["data-note-kind"] == "note"
    assert attrs["role"] == "doc-noteref"
    assert '>1</a>' in html


def test_marker_sits_against_the_preceding_word():
    html = render(ONE_NOTE)
    assert 'at the end.<a id="call-my-note"' in html


def test_definition_ending_in_inline_math_on_one_line():
    html = render(
        """\
        Call. :note:m::

        :note: {:label: m} the value of $x$ ::
        """
    )
    ((_, attrs),) = tags_with_class(html, "note")
    assert attrs["id"] == "m"
    assert r"\(x\)" in html
    assert "error" not in html


def test_aside_marker_kind():
    html = render(
        """\
        Text. :aside:a::

        :aside: {:label: a} the aside ::
        """
    )
    ((_, attrs),) = tags_with_class(html, "note-marker")
    assert attrs["data-note-kind"] == "aside"
    assert attrs["href"] == "#a"


def test_footnote_renders_in_the_notes_list_with_its_number():
    html = render(
        """\
        Before. :note:my-note::

        :note: {:label: my-note} this is the note's contents ::

        After.
        """
    )
    ((tag, attrs),) = tags_with_class(html, "note")
    assert tag == "li"
    assert attrs["id"] == "my-note"
    assert attrs["value"] == "1"
    assert attrs["data-note-number"] == "1"
    assert attrs["data-note-kind"] == "note"
    assert '<span class="note__number">1</span>' in html
    assert "this is the note's contents" in html
    # not in place: the definition comes after all the text
    assert html.index("After.") < html.index('id="my-note"')


def test_aside_definition_stays_in_place():
    html = render(
        """\
        Before. :aside:a::

        :aside: {:label: a} the aside ::

        After.
        """
    )
    ((tag, attrs),) = tags_with_class(html, "aside")
    assert tag == "div"
    assert html.index("Before.") < html.index('id="a"') < html.index("After.")
    assert not tags_with_class(html, "noteslist")


def test_aside_definition_renders_with_aside_class():
    html = render(
        """\
        Text. :aside:a::

        :aside: {:label: a} the aside ::
        """
    )
    ((tag, attrs),) = tags_with_class(html, "aside")
    assert tag == "div"
    assert attrs["data-note-kind"] == "aside"
    assert not tags_with_class(html, "note")


def test_shared_numbers_in_rendered_markers():
    html = render(
        """\
        One :aside:x:: two :note:y::.

        :note: {:label: y} y ::

        :aside: {:label: x} x ::
        """
    )
    numbers = [a["data-note-number"] for _, a in tags_with_class(html, "note-marker")]
    assert numbers == ["1", "2"]


def test_unused_definition_is_not_rendered():
    html = render(
        """\
        No calls.

        :note: {:label: lonely} never called ::
        """
    )
    assert "never called" not in html


def test_definition_with_display_math_closes_its_paragraph():
    html = render(
        """\
        Call. :note:m::

        :note: {:label: m}
          Before
          $$
          x = 1
          $$
          after.
        ::
        """
    )
    start = html.index('id="m"')
    body = html[start:]
    assert body.index("Before") < body.index("</p>") < body.index("mathblock")


@pytest.mark.parametrize("handrails", [False, True])
def test_definition_has_no_handrail(handrails):
    html = render(ONE_NOTE, handrails=handrails)
    ((_, attrs),) = tags_with_class(html, "note")
    assert "hr" not in attrs["class"].split()


# ---------------------------------------------------------------------------
# Notes list
# ---------------------------------------------------------------------------

WITH_REFERENCES = """\
# Title

## Section

First :note:a:: then :aside:b:: then :note:c:: and a citation :cite:knuth::.

:note: {:label: a} note a ::

:aside: {:label: b} aside b ::

## Later

Called later :note:d::.

:note: {:label: d} note d ::

:note: {:label: c} note c ::

:references:
  @book{knuth,
    title={Art of computer programming},
    author={Knuth, Donald E},
    year={2014},
    publisher={Addison-Wesley Professional}
  }
::
"""


def notes_lists(tree: nodes.Node) -> list:
    return list(tree.traverse(nodeclass=nodes.NotesList))


def test_transformer_moves_footnotes_into_one_list():
    tree = transform(WITH_REFERENCES)
    (notes_list,) = notes_lists(tree)
    assert [n.label for n in notes_list.children] == ["a", "c", "d"]
    assert all(type(n) is nodes.Note for n in notes_list.children)


def test_notes_list_is_ordered_by_number_not_by_definition_order():
    tree = transform(WITH_REFERENCES)
    (notes_list,) = notes_lists(tree)
    assert [n.number for n in notes_list.children] == [1, 3, 4]


def test_asides_stay_where_they_are_written():
    tree = transform(WITH_REFERENCES)
    (aside,) = tree.traverse(nodeclass=nodes.Aside)
    assert isinstance(aside.parent, nodes.Section)
    assert aside.first_ancestor_of_type(nodes.NotesList) is None


def test_notes_list_sits_just_before_the_references():
    tree = transform(WITH_REFERENCES)
    (notes_list,) = notes_lists(tree)
    assert isinstance(notes_list.next_sibling(), nodes.Bibliography)


def test_notes_list_is_last_when_there_are_no_references():
    tree = transform(
        """\
        # Title

        ## Section

        Text :note:a::.

        :note: {:label: a} note a ::

        ## Last section

        The end.
        """
    )
    (notes_list,) = notes_lists(tree)
    assert notes_list.parent is tree
    assert notes_list is tree.children[-1]


def test_no_notes_list_without_footnotes():
    tree = transform(
        """\
        Only an aside :aside:x::.

        :aside: {:label: x} aside ::
        """
    )
    assert notes_lists(tree) == []


def test_no_notes_list_when_every_definition_is_unused():
    tree = transform(
        """\
        No calls.

        :note: {:label: lonely} never called ::
        """
    )
    assert notes_lists(tree) == []


@pytest.mark.parametrize("handrails", [False, True])
def test_rendered_list_comes_before_references(handrails):
    html = render(WITH_REFERENCES, handrails=handrails)
    notes_heading = html.index("<h2>Notes</h2>")
    refs_heading = html.index("<h2>References</h2>")
    assert html.index("Called later") < notes_heading < refs_heading
    for label in ("a", "c", "d"):
        assert notes_heading < html.index(f'id="{label}"') < refs_heading


@pytest.mark.parametrize("handrails", [False, True])
def test_rendered_list_markup(handrails):
    html = render(WITH_REFERENCES, handrails=handrails)
    ((tag, _),) = tags_with_class(html, "noteslist")
    assert tag == "ol"
    entries = tags_with_class(html, "note")
    assert [t for t, _ in entries] == ["li", "li", "li"]
    assert [a["id"] for _, a in entries] == ["a", "c", "d"]
    assert [a["value"] for _, a in entries] == ["1", "3", "4"]
    assert [a["data-note-number"] for _, a in entries] == ["1", "3", "4"]
    for number in ("1", "3", "4"):
        assert f'<span class="note__number">{number}</span>' in html
    assert '<span class="note__number">2</span>' in html  # the aside, in place


@pytest.mark.parametrize("handrails", [False, True])
def test_markers_link_to_their_list_entries(handrails):
    html = render(WITH_REFERENCES, handrails=handrails)
    markers = {
        a["id"]: a["href"]
        for _, a in tags_with_class(html, "note-marker")
        if a["data-note-kind"] == "note"
    }
    assert markers == {"call-a": "#a", "call-c": "#c", "call-d": "#d"}


@pytest.mark.parametrize("handrails", [False, True])
def test_each_entry_has_a_backlink_to_its_call(handrails):
    html = render(WITH_REFERENCES, handrails=handrails)
    backlinks = tags_with_class(html, "note-backlink")
    assert [a["href"] for _, a in backlinks] == ["#call-a", "#call-c", "#call-d"]
    for tag, attrs in backlinks:
        assert tag == "a"
        assert attrs["role"] == "doc-backlink"
        assert attrs["aria-label"]
        # the same classes as a bibliography backlink, so it gets the same preview
        assert {"reference", "backlink"} <= set(attrs["class"].split())
    # each backlink sits inside its own entry
    for label in ("a", "c", "d"):
        entry_end = html.index(">", html.index(f'id="{label}"'))
        backlink = html.index(f'href="#call-{label}"')
        assert entry_end < backlink
        assert html.find('class="note"', entry_end, backlink) == -1


@pytest.mark.parametrize("handrails", [False, True])
def test_no_rendered_list_without_footnotes(handrails):
    html = render(
        """\
        Only an aside :aside:x::.

        :aside: {:label: x} aside ::
        """,
        handrails=handrails,
    )
    assert "<h2>Notes</h2>" not in html
    assert not tags_with_class(html, "noteslist")


def test_backlink_after_display_math_stays_inside_the_entry():
    html = render(
        """\
        Call. :note:m::

        :note: {:label: m}
          Before
          $$
          x = 1
          $$
          after.
        ::
        """
    )
    body = html[html.index('id="m"'):]
    assert body.index("after.") < body.index('href="#call-m"') < body.index("</li>")


def test_backlink_after_trailing_display_math_stays_inside_the_entry():
    html = render(
        """\
        Call. :note:m::

        :note: {:label: m}
          Before
          $$
          x = 1
          $$
        ::
        """
    )
    body = html[html.index('id="m"'):]
    assert body.index("mathblock") < body.index('href="#call-m"') < body.index("</li>")


def test_notes_heading_sits_in_a_heading_handrail_like_references():
    html = render(WITH_REFERENCES, handrails=True)
    for heading in ("<h2>Notes</h2>", "<h2>References</h2>"):
        before = html[: html.index(heading)]
        hr_start = before.rindex('<div class="heading hr"')
        assert "</section>" not in before[hr_start:]


def test_notes_from_the_appendix_join_the_same_list():
    html = render(
        WITH_REFERENCES
        + dedent(
            """
            :appendix:

            ## Appendix section

            Appendix text :note:z::.

            :note: {:label: z} note z ::
            """
        )
    )
    notes_heading = html.index("<h2>Notes</h2>")
    refs_heading = html.index("<h2>References</h2>")
    assert html.count("<h2>Notes</h2>") == 1
    assert notes_heading < html.index('id="z"') < refs_heading
