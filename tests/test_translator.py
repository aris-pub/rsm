from pathlib import Path

import rsm

TOOLTIPS_JS = Path(__file__).parent.parent / "rsm" / "static" / "tooltips.js"


def test_translator_starts_anew_each_time():
    text = rsm.nodes.Text("foo")
    tr = rsm.translator.Translator()
    assert tr.translate(text) == "foo"
    assert tr.translate(text) == "foo"


def test_tooltips_js_handles_all_theorem_like_types():
    """All Theorem subclasses must appear in the tooltips.js DIV class whitelist."""
    js = TOOLTIPS_JS.read_text()
    theorem_subclasses = [
        cls.__name__.lower()
        for cls in rsm.nodes.Theorem.__subclasses__()
    ]
    for name in theorem_subclasses:
        assert f'"{name}"' in js, (
            f'Theorem subclass "{name}" missing from tooltips.js whitelist'
        )


def test_mathblock_outside_paragraph_gets_hr_hidden():
    """Mathblocks directly in a section (not inside a paragraph) must have hr-hidden."""
    src = "## Section\n\n$$\n  x = 1\n$$\n"
    html = rsm.build(src)
    assert 'class="mathblock hr hr-hidden' in html, (
        "Mathblock outside paragraph should have hr-hidden class"
    )


def _parsed_text(html):
    """The concatenated text content of HTML, via a real parser (not regex).

    With convert_charrefs, &lt; decodes back to <, so a correctly escaped math
    source round-trips here; a raw < instead opens a tag and splits the text.
    """
    from html.parser import HTMLParser

    class _Collector(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.data = []

        def handle_data(self, d):
            self.data.append(d)

    p = _Collector()
    p.feed(html)
    return "".join(p.data)


def test_math_source_is_html_escaped():
    import rsm

    h = rsm.render("# T\n\nFix $0<p\\le1$ and $a>b$ and $a \\& b$ here.\n",
                   handrails=False, source_offsets=False)
    text = _parsed_text(h)
    for want in (r"\(0<p\le1\)", r"\(a>b\)", r"\(a \& b\)"):
        assert want in text, (want, text)


def test_display_math_source_is_html_escaped():
    import rsm

    # Use a < followed by a letter (a<b), which would open a tag if not escaped.
    h = rsm.render("# T\n\n$$ a<b $$\n", handrails=False, source_offsets=False)
    assert "a<b" in _parsed_text(h), _parsed_text(h)


def test_prose_and_code_angle_brackets_are_escaped():
    import rsm

    h = rsm.render("# T\n\nProse a<b, and :code: x<y :: here.\n",
                   handrails=False, source_offsets=False)
    text = _parsed_text(h)
    assert "a<b" in text and "x<y" in text, text


def test_inline_html_asset_content_is_not_escaped():
    import rsm

    src = '# T\n\n:html:\n\n<div id="w"><b>hi</b> a<c</div>\n\n::\n'
    h = rsm.render(src, handrails=False, source_offsets=False)
    # Raw HTML in an :html: block is verbatim, not escaped like math/prose.
    assert '<div id="w"><b>hi</b> a<c</div>' in h
    assert "&lt;div" not in h
