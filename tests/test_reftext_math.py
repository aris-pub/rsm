"""Math in the text of a link renders on pages with handrails (rsm-h0r).

On those pages math takes the punctuation after it into a wrapper, so it looks
at its next sibling. The nodes of a link's text are not children of the link,
which used to raise ValueError."""

import pytest

import rsm

THM = ":theorem: {:label: t}\n  X.\n::\n\n"
MATH_A = r'<span class="math"'


@pytest.mark.parametrize("handrails", [False, True])
@pytest.mark.parametrize(
    "link, text",
    [
        (":ref:t,the $a$ case::", "the "),
        (":ref:t,$a$::", ""),
        (":ref:t,the $a$, case::", "the "),
        (":url:https://a.org,the $a$ case::", "the "),
    ],
    ids=["ref-mid", "ref-only-math", "ref-math-then-comma", "url"],
)
def test_math_in_link_text(link, text, handrails):
    html = rsm.render(f"{THM}See {link}.\n", handrails=handrails)
    a = html[html.index("<a ", html.index("See")) :]
    a = a[: a.index("</a>")]
    assert MATH_A in a
    assert r"\(a\)" in a
    assert "CST error" not in html


def test_math_in_link_text_keeps_the_comma_after_it():
    html = rsm.render(f"{THM}See :ref:t,the $a$, case::.\n", handrails=True)
    a = html[html.index("<a ", html.index("See")) :]
    a = a[: a.index("</a>")]
    assert "," in a and "case" in a


def test_math_in_an_aside_phrase():
    src = "One :aside:x,the $a$ case:: two.\n\n:aside: {:label: x} An aside. ::\n"
    html = rsm.render(src, handrails=True)
    assert r"\(a\)" in html
    assert "CST error" not in html
