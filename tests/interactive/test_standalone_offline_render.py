"""Interactive test: a standalone build renders with the network hard-cut.

Regression cover for rsm-nyg. A standalone file inlines every library and
embeds the brand fonts and math font as data URIs, so it must render fully with
no network at all. This builds such a file (inline + display math and a custom
:notation: macro), opens it from file:// in an OFFLINE browser context with
every http(s) request aborted, and asserts the page needs nothing external: no
request is attempted, an embedded brand font actually applies (not a bare system
font), the math renders to MathML, the notation macro expands, and the console
is clean.
"""
from pathlib import Path

import pytest
from playwright.sync_api import Browser

import rsm

pytestmark = pytest.mark.interactive

# Inline math ($\eig$, $x^2 + 1$), a display block, and a reader-defined \eig
# notation macro that must expand to lambda.
SOURCE = """\
# Offline Render Check

:notation:
  \\eig $\\lambda$ general eigenvalue
::

Body text with inline math $\\eig$ and $x^2 + 1$.

$$
\\eig + 1 = \\sum_{i=1}^{n} a_i
$$
"""


def _build_standalone(tmp_path: Path) -> str:
    """Build the standalone HTML and return a file:// URL for it."""
    rsm.build(
        source=SOURCE,
        write_output=True,
        output_dir=str(tmp_path),
        output_filename="offline.html",
        handrails=True,
        standalone=True,
        lint=False,
    )
    return (tmp_path / "offline.html").as_uri()


def test_standalone_renders_offline(browser: Browser, tmp_path: Path):
    url = _build_standalone(tmp_path)

    external_requests: list[str] = []
    console_errors: list[str] = []

    # offline=True cuts the network; the route handler additionally aborts and
    # RECORDS any http(s) request so we can assert none was even attempted.
    context = browser.new_context(offline=True)
    try:
        page = context.new_page()

        def _route(route):
            u = route.request.url
            if u.startswith(("http://", "https://")):
                external_requests.append(u)
                route.abort()
            else:
                route.continue_()

        context.route("**/*", _route)
        page.on(
            "console",
            lambda m: console_errors.append(m.text) if m.type == "error" else None,
        )
        page.on("pageerror", lambda e: console_errors.append(str(e)))

        page.goto(url, wait_until="load")
        # temml renders math client-side during RSM.onload.
        page.wait_for_selector("math", timeout=15_000)
        page.evaluate("async () => { await document.fonts.ready; }")

        # 1. Nothing external was even attempted.
        assert external_requests == [], f"unexpected external requests: {external_requests}"

        # 2. An embedded brand font actually applies. The h1 resolves to
        #    Montserrat via the CSS stack, and -- the real proof of embedding --
        #    an actual Montserrat face and Source Sans 3 body face are LOADED.
        #    With the network cut, a loaded brand face can only come from the
        #    embedded woff2. (document.fonts.check is deliberately not used: it
        #    returns true even when the family is undefined, so it proves
        #    nothing.) The heading uses Montserrat and the body Source Sans 3, so
        #    both faces are requested and, when embedded, load.
        h1_font = page.evaluate(
            "() => getComputedStyle(document.querySelector('h1')).fontFamily"
        )
        assert h1_font.startswith("Montserrat"), h1_font
        loaded_brand_faces = page.evaluate(
            """() => [...document.fonts]
                .filter(f => f.status === 'loaded')
                .map(f => f.family)"""
        )
        assert "Montserrat" in loaded_brand_faces, loaded_brand_faces
        assert "Source Sans 3" in loaded_brand_faces, loaded_brand_faces

        # 3. Math rendered to MathML: inline + display, so at least two nodes.
        assert page.evaluate("() => document.querySelectorAll('math').length") >= 2

        # 4. The \\eig macro expanded to lambda in the rendered math, and no raw
        #    macro leaked into any rendered math element.
        math_texts = page.evaluate(
            "() => [...document.querySelectorAll('math')].map(m => m.textContent)"
        )
        assert any("λ" in t for t in math_texts), math_texts
        assert all("\\eig" not in t for t in math_texts), math_texts

        # 5. Clean console.
        assert console_errors == [], f"console errors: {console_errors}"
    finally:
        context.close()
