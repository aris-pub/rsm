"""axe scrollable-region-focusable on wide display math (rsm-dvb)."""

from pathlib import Path

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page

FIXTURE = Path(__file__).parent.parent / "interactive" / "fixtures" / "wide-narrow-math.rsm"


@pytest.mark.accessibility
@pytest.mark.parametrize("width", [320, 1280])
@pytest.mark.parametrize("dark", [False, True], ids=["light", "dark"])
def test_wide_math_scrollable_region_focusable(
    serve_rsm_a11y: callable, page: Page, width: int, dark: bool
) -> None:
    page.set_viewport_size({"width": width, "height": 800})
    page = serve_rsm_a11y(FIXTURE.read_text(), dark_theme=dark)
    page.evaluate(
        "async () => { await window.rsm.mathIdle();"
        " await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); }"
    )
    if width == 320:
        overflowing = page.evaluate(
            "() => [...document.querySelectorAll('.mathblock > .hr-content-zone')]"
            ".filter(z => z.scrollWidth > z.clientWidth).length"
        )
        assert overflowing > 0, "fixture: some equation must overflow at 320px"

    results = Axe().run(
        page, options={"runOnly": {"type": "rule", "values": ["scrollable-region-focusable"]}}
    )
    violations = results.response["violations"]
    assert not violations, [n["target"] for v in violations for n in v["nodes"]]
