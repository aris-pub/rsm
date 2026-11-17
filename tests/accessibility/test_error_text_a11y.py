"""CST error text is red and meets WCAG AA contrast in both themes (rsm-d2v)."""

import pytest
from axe_playwright_python.sync_playwright import Axe

pytestmark = pytest.mark.accessibility

SRC = """\
# Error text

Some text :bogus: more text.

:html: {
  :path: widget.html
}
:caption: Some text :bogus: more text.
::
"""


@pytest.mark.parametrize("dark_theme", [False, True], ids=["light", "dark"])
def test_error_text_is_red_with_aa_contrast(serve_rsm_a11y, tmp_path, dark_theme):
    (tmp_path / "widget.html").write_text("<div>Widget content</div>")
    page = serve_rsm_a11y(SRC, dark_theme=dark_theme, strict=False)

    errors = page.locator(".manuscriptwrapper .error")
    assert errors.count() == 2
    assert page.locator("figcaption .error").count() == 1

    body_color = page.locator(".manuscriptwrapper p").first.evaluate(
        "el => getComputedStyle(el).color"
    )
    for i in range(errors.count()):
        rgb = errors.nth(i).evaluate("el => getComputedStyle(el).color")
        assert rgb != body_color, rgb
        r, g, b = (int(x) for x in rgb[rgb.find("(") + 1 : rgb.find(")")].split(",")[:3])
        assert r > g and r > b, rgb

    results = Axe().run(
        page,
        context={"include": [[".manuscriptwrapper .error"]]},
        options={"runOnly": {"type": "rule", "values": ["color-contrast"]}},
    )
    assert results.response["violations"] == [], results.response["violations"]
    checked = [
        n
        for rule in results.response["passes"]
        if rule["id"] == "color-contrast"
        for n in rule["nodes"]
    ]
    assert len(checked) == 2, results.response["passes"]
