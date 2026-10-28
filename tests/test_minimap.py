"""The document minimap's build-time switches.

The strip itself is drawn by rsm/static/minimap.js (covered by
tests/interactive/test_minimap.py). At build time the translator carries the
author's :config: { :minimap: false } as body[data-minimap="false"], which the
script reads to stay off, and leaves the reader's Map toggle out of the
sidebar's Reading view, since there is nothing to toggle.
"""

import re

import pytest

import rsm
from rsm.translator import HandrailsTranslator, minimap_enabled

SRC = """\
# Map

## One

Text.
"""


def _translate(minimap=None, sidebar=True) -> str:
    tree = rsm.app.ParserApp(plain=SRC).run()
    if minimap is not None:
        tree.minimap = minimap
    return HandrailsTranslator(sidebar=sidebar).translate(tree)


def _body_tag(html: str) -> str:
    return re.search(r"<body[^>]*>", html).group(0)


def test_minimap_is_on_by_default():
    html = _translate()
    assert "data-minimap" not in _body_tag(html)


@pytest.mark.parametrize("value", ["false", "False", " off ", "no", False])
def test_author_can_turn_the_minimap_off(value):
    html = _translate(minimap=value)
    assert 'data-minimap="false"' in _body_tag(html)


@pytest.mark.parametrize("value", ["true", "on", True])
def test_other_values_keep_the_minimap_on(value):
    html = _translate(minimap=value)
    assert "data-minimap" not in _body_tag(html)


def test_plain_translator_carries_the_flag_too():
    tree = rsm.app.ParserApp(plain=SRC).run()
    tree.minimap = "false"
    html = rsm.translator.Translator().translate(tree)
    assert 'data-minimap="false"' in _body_tag(html)


def test_reading_view_has_a_map_toggle():
    html = _translate()
    row = re.search(r'<div class="reading-row" data-control="minimap">.*?</div></div>', html)
    assert row, "the Reading view should have a Map row"
    row = row.group(0)
    assert 'data-value="on"' in row and 'data-value="off"' in row
    # On is the resting choice.
    assert re.search(r'class="reading-opt active" data-value="on" aria-pressed="true"', row)
    assert 'aria-label="Show the document map"' in row
    assert 'aria-label="Hide the document map"' in row


def test_reading_view_drops_the_toggle_when_the_author_turned_the_map_off():
    html = _translate(minimap="false")
    assert 'data-control="minimap"' not in html
    # The other rows stay.
    assert 'data-control="theme"' in html


def test_minimap_enabled_helper():
    class T:
        pass

    t = T()
    assert minimap_enabled(t)
    t.minimap = "false"
    assert not minimap_enabled(t)
    t.minimap = "true"
    assert minimap_enabled(t)


FIGURES_SRC = """\
# Map

:figure: {
  :label: fig-top
  :path: missing.png
}
::

## One

:figure: {
  :label: fig-cap
  :path: missing.png
}
:caption: A caption.
::

:html: {
  :label: wid-bare
  :path: missing.html
}
::

:html: {
  :label: wid-orn
  :path: missing.html
  :nonum:
}
::

:video: {
  :label: vid-a
}
::
"""


@pytest.mark.parametrize("sidebar", [True, False], ids=["handrails", "plain"])
def test_figure_counter_blocks_carry_their_number(sidebar):
    tree = rsm.app.ParserApp(plain=FIGURES_SRC).run()
    tr = HandrailsTranslator(sidebar=True) if sidebar else rsm.translator.Translator()
    html = tr.translate(tree)

    def tag(id_):
        return re.search(rf'<figure id="{id_}"[^>]*>', html).group(0)

    # Figures and widgets share one counter, captioned or not.
    assert 'data-number="1.1"' in tag("fig-cap")
    assert 'data-number="1.2"' in tag("wid-bare")
    # Outside any section the bare number is used.
    assert 'data-number="1"' in tag("fig-top")
    # Videos have their own counter.
    assert 'data-number="1.1"' in tag("vid-a")
    # An unnumbered block (an ornament) has none.
    assert "data-number" not in tag("wid-orn")


@pytest.mark.skip(
    reason="rsm-3am: :minimap: is not yet a meta key in the tree-sitter-rsm grammar "
    "(metakey_any). Enable once the grammar change lands."
)
def test_config_block_turns_the_minimap_off():
    src = ":config: { :minimap: false }\n\n" + SRC
    html = rsm.render(src, handrails=True, sidebar=True, strict=True)
    assert 'data-minimap="false"' in _body_tag(html)
    assert 'data-control="minimap"' not in html
