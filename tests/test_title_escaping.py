"""Titles and reference text are plain text, so `<` and `&` in them must be
escaped wherever they are written into the HTML (rsm-05m)."""

import pytest

import rsm

SRC = """# Doc a<b & c

:toc: ::

## Sec a<b & c
  {:label: s1}

:paragraph: {:title: Par a<b & c} Body. ::

See :ref:s1,R a<b & c::.

"""


@pytest.mark.parametrize("handrails", [False, True])
@pytest.mark.parametrize("prefix", ["Doc", "Sec", "Par", "R"])
def test_title_text_is_escaped(handrails, prefix):
    html = rsm.render(SRC, handrails=handrails)
    assert f"{prefix} a<b & c" not in html
    assert f"{prefix} a&lt;b &amp; c" in html


def test_toc_entry_and_heading_are_escaped():
    html = rsm.render(SRC, handrails=True)
    assert '<a class="reference" href="#s1">1. Sec a&lt;b &amp; c</a>' in html
    assert "1. Sec a&lt;b &amp; c</h2>" in html
