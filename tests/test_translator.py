import rsm


def test_translator_starts_anew_each_time():
    text = rsm.nodes.Text("foo")
    tr = rsm.translator.Translator()
    assert tr.translate(text) == "foo"
    assert tr.translate(text) == "foo"


def test_mathblock_outside_paragraph_gets_hr_hidden():
    """Mathblocks directly in a section (not inside a paragraph) must have hr-hidden."""
    src = "## Section\n\n$$\n  x = 1\n$$\n"
    html = rsm.build(src)
    assert 'class="mathblock hr hr-hidden' in html, (
        "Mathblock outside paragraph should have hr-hidden class"
    )
