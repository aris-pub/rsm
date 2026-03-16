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
