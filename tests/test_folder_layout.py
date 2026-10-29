"""The standard (non-standalone) build writes index.html, static/ for RSM's own
files and assets/ for the author's files, and links all of them relative to the
page, so the folder works at any address (rsm-3wf). The math libraries are
pinned and shipped in static/ (rsm-nyg.2)."""

import re
from pathlib import Path

import rsm

SRC = """# Layout

Inline math $x + y$.

:figure: {
  :path: figs/plot.svg
  :label: fig-plot
}
:caption: A plot.
::

:html: {
  :path: figs/widget.html
  :label: fig-widget
  :static: figs/static/widget.png
  :alt: A blue square.
}

  :caption: A widget.
::

:algorithm:
\\begin{algorithm}
\\caption{Euclid}
\\begin{algorithmic}
\\PROCEDURE{Euclid}{$a, b$}
    \\RETURN $a$
\\ENDPROCEDURE
\\end{algorithmic}
\\end{algorithm}
::
"""

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="20">'
    '<rect width="40" height="20" fill="#36c"/></svg>'
)
WIDGET = '<div id="widget"><img src="figs/inner.svg" alt="inner"></div>'
CSS = ".layout-test-marker { color: rgb(1, 2, 3); }\n"
# A tiny valid PNG (1x1), so a browser can decode the static fallback.
PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360f8cfc0f01f0005000201e2213b"
    "c70000000049454e44ae426082"
)


def write_source(src_dir: Path) -> None:
    """Write the document, its figures and its CSS into src_dir."""
    (src_dir / "figs" / "static").mkdir(parents=True)
    (src_dir / "figs" / "plot.svg").write_text(SVG)
    (src_dir / "figs" / "inner.svg").write_text(SVG)
    (src_dir / "figs" / "widget.html").write_text(WIDGET)
    (src_dir / "figs" / "static" / "widget.png").write_bytes(PNG)
    (src_dir / "paper.css").write_text(CSS)
    (src_dir / "paper.rsm").write_text(SRC)


def build_folder(src_dir: Path, out_dir: Path, monkeypatch) -> Path:
    """Build paper.rsm the way `rsm build paper.rsm -o out/index.html` does."""
    write_source(src_dir)
    # Asset paths resolve from the working directory, as in the CLI.
    monkeypatch.chdir(src_dir)
    rsm.build(
        path="paper.rsm",
        output_dir=str(out_dir),
        output_filename="index.html",
        write_output=True,
        handrails=True,
        standalone=False,
        custom_css="paper.css",
    )
    return out_dir / "index.html"


def local_refs(html: str) -> list[str]:
    """Every href, src, srcset and url() target that is not external or a
    fragment, plus every JS import specifier."""
    refs = re.findall(r'\b(?:href|src|srcset)="([^"]*)"', html)
    refs += re.findall(r'url\("([^"]*)"\)', html)
    refs += re.findall(r"""\bfrom\s+['"]([^'"]+)['"]""", html)
    return [
        r for r in refs
        if r and not r.startswith(("http://", "https://", "#", "data:"))
    ]


def test_layout_is_index_static_assets(tmp_path, monkeypatch):
    out = tmp_path / "out"
    index = build_folder(tmp_path / "src", out, monkeypatch)

    assert index.exists()
    top = sorted(p.name for p in out.iterdir())
    assert top == ["assets", "index.html", "static"], top

    static = {p.name for p in (out / "static").iterdir()}
    for name in (
        "onload.js", "libraries.js", "braiid.css", "pygments.css",
        "jquery-3.6.0.js", "tooltipster.bundle.js", "tooltipster.bundle.css",
        "pseudocode-2.4.1.min.js", "pseudocode-2.4.1.min.css",
    ):
        assert name in static, name
    # MathJax keeps its own layout, so it finds its fonts beside its script.
    mathjax = out / "static" / "mathjax-3.2.2"
    assert (mathjax / "tex-chtml-full.js").exists()
    fonts = mathjax / "output" / "chtml" / "fonts" / "woff-v2"
    vendored = Path(rsm.__file__).parent / "static" / "mathjax-3.2.2" / "output" / "chtml" / "fonts" / "woff-v2"
    assert sorted(p.name for p in fonts.iterdir()) == sorted(p.name for p in vendored.iterdir())
    assert (fonts / "MathJax_Main-Regular.woff").read_bytes() == (
        vendored / "MathJax_Main-Regular.woff"
    ).read_bytes()
    # static/ is RSM's alone: no author file lands there.
    assert "paper.css" not in static
    assert not (out / "static" / "figs").exists()

    assert (out / "assets" / "paper.css").read_text() == CSS
    assert (out / "assets" / "figs" / "plot.svg").read_text() == SVG
    assert (out / "assets" / "figs" / "inner.svg").read_text() == SVG
    assert (out / "assets" / "figs" / "static" / "widget.png").read_bytes() == PNG
    assert not (out / "figs").exists()


def test_every_local_link_is_relative_and_resolves(tmp_path, monkeypatch):
    out = tmp_path / "out"
    html = build_folder(tmp_path / "src", out, monkeypatch).read_text()

    refs = local_refs(html)
    assert refs, "expected local links in the page"
    absolute = [r for r in refs if r.startswith("/")]
    assert not absolute, absolute

    for ref in (
        "static/braiid.css", "static/tooltipster.bundle.css",
        "static/pseudocode-2.4.1.min.css", "assets/paper.css",
        "static/jquery-3.6.0.js", "static/tooltipster.bundle.js",
        "./static/onload.js", "assets/figs/plot.svg", "assets/figs/inner.svg",
        "assets/figs/static/widget.png",
    ):
        assert ref in refs, ref
    for ref in refs:
        assert (out / ref).exists(), ref


def test_no_unpinned_cdn_url_in_static_js():
    """No @latest or unversioned jsDelivr npm URL in rsm/static/*.js. The bundle
    is rebuilt from these files."""
    static = Path(rsm.__file__).parent / "static"
    vendored = {"jquery-3.6.0.js", "tooltipster.bundle.js", "rsm-standalone.js"}
    bad = []
    for path in static.glob("*.js"):
        if path.name in vendored or ".min." in path.name:
            continue
        for url in re.findall(r"https://cdn\.jsdelivr\.net/npm/[^'\"`\s]+", path.read_text()):
            package = url.split("/npm/", 1)[1].split("/", 1)[0]
            if "@" not in package or package.endswith(("@latest", "@3")):
                bad.append((path.name, url))
    assert not bad, bad
    assert "@import url(" not in (static / "pseudocode-2.4.1.min.css").read_text()


def test_standalone_inlines_vendored_math_libraries():
    html = rsm.build(SRC, handrails=True, lint=False, standalone=True)
    static = Path(rsm.__file__).parent / "static"
    pseudocode = (static / "pseudocode-2.4.1.min.js").read_text()
    assert pseudocode in html
    # MathJax is inlined as a function libraries.js calls after setting its
    # config, with every font MathJax names as a data URI.
    assert "window.__rsmMathJax = function () {" in html
    assert "%%URL%%/MathJax_" not in html
    fonts = sorted((static / "mathjax-3.2.2" / "output" / "chtml" / "fonts" / "woff-v2").glob("*.woff"))
    named = [f for f in fonts if f"%%URL%%/{f.name}" in (static / "mathjax-3.2.2" / "tex-chtml-full.js").read_text()]
    assert named, "expected MathJax to name its fonts"
    assert html.count('url("data:font/woff;base64,') == len(named)
    assert "pseudocode@latest" not in html
    assert "@import url(https://cdnjs" not in html
    assert '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pseudocode' not in html
