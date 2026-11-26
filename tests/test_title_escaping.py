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


@pytest.mark.parametrize("brace", ["{", "}"])
def test_escaped_brace_in_a_title_shows_the_brace(brace):
    # A title with \{ or \} shows the brace alone, as in "Sets {a, b}".
    src = f"# T\n\n:theorem: {{:title: Sets \\{brace} here}}\nBody.\n::\n"
    html = rsm.render(src, handrails=True)
    assert f"Sets {brace} here" in html
    assert f"\\{brace}" not in html


def test_escaped_close_brace_in_text_shows_the_brace():
    html = rsm.render("# T\n\nA set \\{a, b\\} here.\n", handrails=False)
    assert "A set {a, b} here." in html
