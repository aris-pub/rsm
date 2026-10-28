"""Asides: where a definition goes and how it is marked up (rsm-zvn.2, .3, .4).

An aside belongs to the block that holds its call: the paragraph, list item or
proof step paragraph. The transformer moves the definition to the end of that
block, in call order, so the HTML has the aside right below the text that calls
it. That is where a reader without scripts sees it, where a narrow screen opens
it, and where the block's handrail already reaches. On wide screens the scripts
move it into the right-hand column.
"""

from html.parser import HTMLParser
from textwrap import dedent

import pytest

import rsm
from rsm import nodes


def parse(src: str) -> nodes.Manuscript:
    return rsm.tsparser.TSParser().parse(dedent(src).lstrip())


def transform(src: str) -> nodes.Manuscript:
    return rsm.transformer.Transformer().transform(parse(src))


def render(src: str, handrails: bool = True) -> str:
    return rsm.render(dedent(src).lstrip(), handrails=handrails, source_offsets=False)


def asides(tree: nodes.Node) -> list[nodes.Aside]:
    return list(tree.traverse(nodeclass=nodes.Aside))


class _Tree(HTMLParser):
    """Parse HTML into a light element tree, checking that tags nest properly."""

    VOID = {"br", "img", "hr", "input", "meta", "link", "source", "use", "path", "col"}

    def __init__(self) -> None:
        super().__init__()
        self.root = {"tag": "#root", "attrs": {}, "children": [], "parent": None}
        self.cur = self.root
        self.problems: list[str] = []

    def handle_starttag(self, tag, attrs):
        el = {"tag": tag, "attrs": dict(attrs), "children": [], "parent": self.cur}
        if tag in {"div", "p", "ul", "ol", "figure"} and self._inside("p"):
            self.problems.append(f"<{tag}> opened inside <p>")
        self.cur["children"].append(el)
        if tag not in self.VOID:
            self.cur = el

    def handle_startendtag(self, tag, attrs):
        self.cur["children"].append(
            {"tag": tag, "attrs": dict(attrs), "children": [], "parent": self.cur}
        )

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if self.cur["tag"] != tag:
            self.problems.append(f"</{tag}> closes <{self.cur['tag']}>")
            return
        self.cur = self.cur["parent"]

    def handle_data(self, data):
        self.cur["children"].append(data)

    def _inside(self, tag):
        el = self.cur
        while el is not None:
            if el["tag"] == tag:
                return True
            el = el["parent"]
        return False


def tree_of(html: str) -> _Tree:
    t = _Tree()
    t.feed(html)
    return t


def find_all(el, pred) -> list:
    out = []
    for c in el["children"]:
        if isinstance(c, dict):
            if pred(c):
                out.append(c)
            out.extend(find_all(c, pred))
    return out


def by_id(t: _Tree, id_: str):
    (el,) = find_all(t.root, lambda e: e["attrs"].get("id") == id_)
    return el


def classes(el) -> list[str]:
    return (el["attrs"].get("class") or "").split()


def ancestors(el):
    el = el["parent"]
    while el is not None:
        yield el
        el = el["parent"]


def text_of(el) -> str:
    return "".join(c if isinstance(c, str) else text_of(c) for c in el["children"])


def element_children(el) -> list:
    return [c for c in el["children"] if isinstance(c, dict)]


ONE = """\
First paragraph with an aside :aside:a1:: here. And more text.

:aside: {:label: a1} the aside text ::

After.
"""


# ---------------------------------------------------------------------------
# Transformer: the definition moves to the end of the block that calls it
# ---------------------------------------------------------------------------


def test_definition_moves_into_the_calling_paragraph():
    tree = transform(ONE)
    (aside,) = asides(tree)
    para = aside.call.first_ancestor_of_type(nodes.Paragraph)
    assert aside.parent is para
    assert para.children[-1] is aside


def test_definition_written_before_its_call_also_moves():
    tree = transform(
        """\
        :aside: {:label: a1} defined first ::

        Then called :aside:a1:: here.
        """
    )
    (aside,) = asides(tree)
    assert isinstance(aside.parent, nodes.Paragraph)
    assert aside.call.parent is aside.parent


def test_several_asides_of_one_paragraph_follow_call_order():
    tree = transform(
        """\
        One :aside:b:: two :aside:a:: three :aside:c::.

        :aside: {:label: a} a ::

        :aside: {:label: c} c ::

        :aside: {:label: b} b ::
        """
    )
    para = next(tree.traverse(nodeclass=nodes.Paragraph))
    tail = [c for c in para.children if isinstance(c, nodes.Aside)]
    assert [a.label for a in tail] == ["b", "a", "c"]
    assert [a.number for a in tail] == [1, 2, 3]
    assert list(para.children[-3:]) == tail


def test_aside_in_a_list_item_moves_into_the_item():
    tree = transform(
        """\
        :itemize:

          :-: An item :aside:a1:: here.

          :-: Second.

        ::

        :aside: {:label: a1} the aside ::
        """
    )
    (aside,) = asides(tree)
    assert isinstance(aside.parent, nodes.Item)
    assert aside.parent.children[-1] is aside


def test_aside_in_a_proof_step_moves_into_the_step_paragraph():
    tree = transform(
        """\
        :theorem: {:label: thm} A theorem. ::

        :proof:

          :step: A step :aside:a1:: here.

          :step: Another step.

        ::

        :aside: {:label: a1} the aside ::
        """
    )
    (aside,) = asides(tree)
    assert type(aside.parent) is nodes.Paragraph
    assert aside.parent.first_ancestor_of_type(nodes.Step) is not None


def test_notes_stay_where_they_are():
    tree = transform(
        """\
        Text :note:n1:: here.

        :note: {:label: n1} a footnote ::
        """
    )
    (note,) = tree.traverse(nodeclass=nodes.Note)
    assert not isinstance(note.parent, nodes.Paragraph)


def test_aside_called_from_inside_a_note_stays_in_place():
    tree = transform(
        """\
        Text :note:n1:: here.

        :note: {:label: n1} a footnote with an aside :aside:a1:: ::

        :aside: {:label: a1} the aside ::
        """
    )
    (aside,) = asides(tree)
    assert not isinstance(aside.parent, (nodes.Paragraph, nodes.Item, nodes.Note))


# ---------------------------------------------------------------------------
# Translator: the aside sits below the paragraph's text, inside its block
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("handrails", [True, False])
def test_markup_is_well_formed(handrails):
    t = tree_of(render(ONE, handrails=handrails))
    assert not t.problems


def test_aside_follows_the_paragraph_text_inside_its_handrail():
    t = tree_of(render(ONE))
    aside = by_id(t, "a1")
    assert aside["tag"] == "div"
    assert "aside" in classes(aside)
    zone = aside["parent"]
    assert "hr-content-zone" in classes(zone)
    para = zone["parent"]
    assert "paragraph" in classes(para) and "hr" in classes(para)
    kids = element_children(zone)
    assert [k["tag"] for k in kids] == ["p", "div"]
    assert "And more text." in text_of(kids[0])
    assert "After." not in text_of(para)


def test_aside_has_no_handrail_and_no_alignment_wrapper():
    t = tree_of(render(ONE))
    aside = by_id(t, "a1")
    assert not find_all(aside, lambda e: "hr" in classes(e))
    assert "hr" not in classes(aside)


def test_aside_markup():
    t = tree_of(render(ONE))
    aside = by_id(t, "a1")
    assert aside["attrs"]["data-note-number"] == "1"
    assert aside["attrs"]["data-note-kind"] == "aside"
    (p,) = element_children(aside)
    assert p["tag"] == "p"
    (num,) = find_all(p, lambda e: "note__number" in classes(e))
    assert text_of(num) == "1"
    assert text_of(p).strip() == "1 the aside text"


def test_marker_points_at_the_aside():
    t = tree_of(render(ONE))
    (marker,) = find_all(t.root, lambda e: "note-marker" in classes(e))
    assert marker["attrs"]["href"] == "#a1"
    assert marker["attrs"]["id"] == "call-a1"


def test_several_asides_stack_below_the_paragraph_in_marker_order():
    t = tree_of(
        render(
            """\
            One :aside:b:: two :aside:a::.

            :aside: {:label: a} a ::

            :aside: {:label: b} b ::
            """
        )
    )
    assert not t.problems
    zone = by_id(t, "a")["parent"]
    kids = element_children(zone)
    assert [k["tag"] for k in kids] == ["p", "div", "div"]
    assert [k["attrs"].get("id") for k in kids[1:]] == ["b", "a"]


@pytest.mark.parametrize("handrails", [True, False])
def test_paragraph_with_display_math_in_the_middle(handrails):
    t = tree_of(
        render(
            """\
            Before :aside:a1:: the math
            $$
            x = 1
            $$
            and after it.

            :aside: {:label: a1} the aside ::
            """,
            handrails=handrails,
        )
    )
    assert not t.problems
    aside = by_id(t, "a1")
    siblings = element_children(aside["parent"])
    assert siblings[-1] is aside
    assert "and after it." in text_of(siblings[-2])


@pytest.mark.parametrize("handrails", [True, False])
def test_paragraph_ending_in_display_math(handrails):
    t = tree_of(
        render(
            """\
            Before :aside:a1:: the math
            $$
            x = 1
            $$

            :aside: {:label: a1} the aside ::
            """,
            handrails=handrails,
        )
    )
    assert not t.problems
    aside = by_id(t, "a1")
    siblings = element_children(aside["parent"])
    assert siblings[-1] is aside
    assert "mathblock" in classes(siblings[-2])


def test_aside_with_display_math_of_its_own():
    t = tree_of(
        render(
            """\
            Text :aside:a1:: here.

            :aside: {:label: a1}
              Before
              $$
              x = 1
              $$
              after.
            ::
            """
        )
    )
    assert not t.problems
    aside = by_id(t, "a1")
    assert find_all(aside, lambda e: "mathblock" in classes(e))


def test_aside_in_a_list_item_sits_inside_the_item():
    t = tree_of(
        render(
            """\
            :itemize:

              :-: An item :aside:a1:: here.

              :-: Second.

            ::

            :aside: {:label: a1} the aside ::
            """
        )
    )
    assert not t.problems
    aside = by_id(t, "a1")
    assert aside["parent"]["tag"] == "li"


def test_aside_in_a_proof_step_sits_below_the_step_text():
    t = tree_of(
        render(
            """\
            :theorem: {:label: thm} A theorem. ::

            :proof:

              :step: A step :aside:a1:: here.

              :step: Another step.

            ::

            :aside: {:label: a1} the aside ::
            """
        )
    )
    assert not t.problems
    aside = by_id(t, "a1")
    assert any("step" in classes(a) for a in ancestors(aside))
    assert "Another step" not in text_of(aside["parent"])


def test_paragraph_with_title_keeps_its_label():
    html = render(
        """\
        :paragraph: {:title: Remark} Text :aside:a1:: here. ::

        :aside: {:label: a1} the aside ::
        """
    )
    t = tree_of(html)
    assert not t.problems
    assert "pg-label" in html


# ---------------------------------------------------------------------------
# Builder: a pre-paint class tells the CSS that the aside scripts will run
# ---------------------------------------------------------------------------


def build_html(src: str, tmp_path, **kw) -> str:
    path = tmp_path / "doc.rsm"
    path.write_text(dedent(src).lstrip())
    rsm.build(
        path=str(path),
        output_dir=str(tmp_path),
        output_filename="doc.html",
        write_output=True,
        handrails=True,
        **kw,
    )
    return (tmp_path / "doc.html").read_text()


@pytest.mark.parametrize("standalone", [False, True])
def test_prepaint_script_marks_pages_with_asides(tmp_path, standalone):
    html = build_html(ONE, tmp_path, standalone=standalone)
    head = html[: html.index("</head>")]
    assert "classList.add('has-asides')" in head


def test_no_prepaint_script_without_asides(tmp_path):
    html = build_html(
        """\
        Text :note:n1:: here.

        :note: {:label: n1} a footnote ::
        """,
        tmp_path,
    )
    assert "has-asides" not in html[: html.index("</head>")]


def test_step_summary_in_the_sidebar_leaves_out_the_aside(tmp_path):
    html = build_html(
        """\
        :theorem: {:label: thm} A theorem. ::

        :proof:
          :step: A step :aside:a1:: here.::
          :step: Another step.::
        ::

        :aside: {:label: a1} the aside text ::
        """,
        tmp_path,
        sidebar=True,
    )
    assert 'data-tooltip="1. A step here."' in html
