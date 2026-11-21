"""The :tabs: environment: a group of :tab: blocks, of which the reader sees one at
a time. Switching happens in CSS (a radio input per tab); onload.js only selects
the tab that holds the target of a link."""

import re

import pytest
from bs4 import BeautifulSoup

import rsm
from rsm import nodes, tsparser
from rsm.app import ProcessorApp
from rsm.transformer import RSMTransformerError

SRC = """\
## Sec

:tabs: {:label: tabs-turan}

  :tab: {:title: Sketch, :label: tab-sketch}

    :sketch: Make $G$ complete multipartite. ::

  ::

  :tab: {:title: Proof of $T(n, r)$}

    :figure: {:label: fig-a, :path: a.png}

      :caption: First.

    ::

    :figure: {:label: fig-b, :path: b.png}

      :caption: Second.

    ::

    See :ref:tab-sketch:: and :ref:fig-b::.

  ::

::
"""


def _parse(src):
    return tsparser.TSParser().parse(src)


def _transform(src):
    app = ProcessorApp(plain=src, handrails=True)
    app.pop_task()
    return app.run()


def _html(src, handrails=True):
    return BeautifulSoup(
        rsm.build(source=src, handrails=handrails, strict=False), "html.parser"
    )


def test_tabs_parse_into_tabs_and_tab_nodes():
    tree = _parse(SRC)
    (group,) = tree.traverse(nodeclass=nodes.Tabs)
    assert group.label == "tabs-turan"
    tabs = list(group.children)
    assert [type(t) for t in tabs] == [nodes.Tab, nodes.Tab]
    assert tabs[0].title == "Sketch"
    assert tabs[0].label == "tab-sketch"
    assert isinstance(tabs[0].children[0], nodes.Sketch)


def test_a_tab_title_can_hold_math():
    tree = _parse(SRC)
    tab = list(tree.traverse(nodeclass=nodes.Tab))[1]
    assert any(isinstance(n, nodes.Math) for n in tab.title_nodes)


def test_a_tab_holds_any_number_of_blocks():
    tree = _parse(SRC)
    tab = list(tree.traverse(nodeclass=nodes.Tab))[1]
    kinds = [type(c) for c in tab.children]
    assert kinds.count(nodes.Figure) == 2
    assert nodes.Paragraph in kinds


def test_tabs_hold_only_tabs():
    with pytest.raises(nodes.RSMNodeError, match="Tabs"):
        _parse(":tabs:\n\n  Some text.\n\n::\n")


def test_a_tab_sits_only_in_tabs():
    with pytest.raises(nodes.RSMNodeError, match="Tab"):
        _parse(":tab: {:title: A}\n\n  Some text.\n\n::\n")


def test_a_tab_cannot_hold_a_step():
    src = ":proof:\n\n  :tabs:\n\n    :tab: {:title: A}\n\n      :step: X. ::\n\n    ::\n\n  ::\n\n::\n"
    with pytest.raises(nodes.RSMNodeError, match="Step"):
        _parse(src)


def test_a_tab_needs_a_title():
    with pytest.raises(RSMTransformerError, match=":title:"):
        _transform(":tabs:\n\n  :tab:\n\n    Text.\n\n  ::\n\n::\n")


def test_tabs_cannot_nest():
    src = (
        ":tabs:\n\n  :tab: {:title: A}\n\n"
        "    :remark:\n\n      :tabs:\n\n        :tab: {:title: B}\n\n          X.\n\n"
        "        ::\n\n      ::\n\n    ::\n\n  ::\n\n::\n"
    )
    with pytest.raises(RSMTransformerError, match="inside another"):
        _transform(src)


def test_figures_in_tabs_keep_their_numbers():
    tree = _transform(SRC)
    figs = list(tree.traverse(nodeclass=nodes.Figure))
    assert [f.full_number for f in figs] == ["1.1", "1.2"]


@pytest.mark.parametrize("handrails", [True, False])
def test_html_has_one_radio_label_and_panel_per_tab(handrails):
    soup = _html(SRC, handrails)
    group = soup.select_one("div.tabs")
    assert group["id"] == "tabs-turan"
    kids = [c for c in group.children if getattr(c, "name", None)]
    # input, label, panel for each tab, in that order: the CSS relies on it.
    assert [c.name for c in kids] == ["input", "label", "div"] * 2
    radios = group.select(":scope > input")
    assert all(r["type"] == "radio" and "tab-input" in r["class"] for r in radios)
    assert len({r["name"] for r in radios}) == 1
    assert radios[0].has_attr("checked") and not radios[1].has_attr("checked")
    labels = group.select(":scope > label.tab-label")
    assert [lab["for"] for lab in labels] == [r["id"] for r in radios]
    panels = group.select(":scope > div.tab")
    assert [p["data-tab"] for p in panels] == [r["id"] for r in radios]
    assert panels[0]["id"] == "tab-sketch"


def test_html_tab_label_renders_title_markup():
    soup = _html(SRC)
    labels = soup.select("label.tab-label")
    assert labels[0].get_text(strip=True) == "Sketch"
    assert labels[1].select_one(".math") is not None


def test_html_radio_ids_are_unique_across_groups():
    src = (
        SRC
        + "\n"
        + SRC.replace("## Sec\n", "")
        .replace("tabs-turan", "tabs-2")
        .replace("tab-sketch", "tab-sketch-2")
        .replace("fig-a", "fig-c")
        .replace("fig-b", "fig-d")
    )
    soup = _html(src)
    ids = [r["id"] for r in soup.select("input.tab-input")]
    names = {r["name"] for r in soup.select("input.tab-input")}
    assert len(ids) == len(set(ids)) == 4
    assert len(names) == 2


def test_html_tab_groups_have_no_handrail():
    soup = _html(SRC)
    group = soup.select_one("div.tabs")
    assert "hr" not in group.get("class", [])
    assert all("hr" not in p.get("class", []) for p in group.select(":scope > div.tab"))


def test_reference_to_a_tab_prints_its_title_and_links_to_the_panel():
    soup = _html(SRC)
    ref = soup.find("a", href="#tab-sketch")
    assert ref is not None
    assert re.sub(r"\s+", " ", ref.get_text()).strip() == "Sketch"
