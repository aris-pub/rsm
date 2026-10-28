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


def test_definition_renders_in_place_with_its_number():
    html = render(
        """\
        Before. :note:my-note::

        :note: {:label: my-note} this is the note's contents ::

        After.
        """
    )
    ((tag, attrs),) = tags_with_class(html, "note")
    assert tag == "div"
    assert attrs["id"] == "my-note"
    assert attrs["data-note-number"] == "1"
    assert attrs["data-note-kind"] == "note"
    assert '<span class="note__number">1</span>' in html
    assert "this is the note's contents" in html
    # in place: after the calling paragraph, before the next one
    assert html.index("Before.") < html.index('id="my-note"') < html.index("After.")


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
