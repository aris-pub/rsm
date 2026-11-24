"""
rsm_directive.py
----------------

Highlight and render RSM code blocks.

"""

import hashlib
import re
import shutil
from html import escape
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive, directives

import rsm
import tree_sitter
import tree_sitter_rsm


# ── Syntax highlighting via tree-sitter ──────────────────────────────────────

# The colours come from the grammar's own highlight query, which editors and
# the RSM language server also use. The query is read from the submodule,
# because an editable install of tree-sitter-rsm does not ship the queries.
_HIGHLIGHTS_SCM = (
    Path(__file__).resolve().parents[2] / "tree-sitter-rsm" / "queries" / "highlights.scm"
)

# Capture names in highlights.scm, mapped to the tok-* classes in custom.css.
# The language server has the same table (packages/rsm-lsp/src/layer1/
# semanticTokens.ts).
_CAPTURE_TO_CLASS = {
    "keyword": "tok-keyword", "keyword.function": "tok-keyword",
    "keyword.directive": "tok-keyword", "keyword.modifier": "tok-modifier",
    "function": "tok-function", "function.builtin": "tok-function",
    "type": "tok-type", "property": "tok-property",
    "string": "tok-string", "string.special": "tok-string",
    "number": "tok-number", "comment": "tok-comment", "operator": "tok-operator",
    "constant": "tok-enumMember", "constant.builtin": "tok-enumMember",
    "markup.heading": "tok-namespace", "markup.heading.1": "tok-namespace",
    "markup.heading.2": "tok-namespace", "markup.heading.3": "tok-namespace",
    "markup.heading.4": "tok-namespace", "markup.math": "tok-macro",
    "markup.raw": "tok-string", "markup.raw.block": "tok-string",
    "markup.link.url": "tok-string",
    "punctuation.bracket": "tok-operator", "punctuation.delimiter": "tok-operator",
    "punctuation.special": "tok-operator",
}

_TS_LANG = tree_sitter.Language(tree_sitter_rsm.language())
_TS_PARSER = tree_sitter.Parser(_TS_LANG)
_TS_QUERY = tree_sitter.Query(_TS_LANG, _HIGHLIGHTS_SCM.read_text())


def highlight_rsm(source: str) -> str:
    """Return HTML with tok-* spans for RSM source code."""
    src = source.encode()
    tree = _TS_PARSER.parse(src)
    # Where captures overlap, as for a block and the tag inside it, the
    # shortest one colours the text, and among equal ones the earliest pattern
    # in the query, as in tree-sitter's own highlighter.
    best = [None] * len(src)
    for pattern, captures in tree_sitter.QueryCursor(_TS_QUERY).matches(tree.root_node):
        for name, capnodes in captures.items():
            css = _CAPTURE_TO_CLASS.get(name)
            if css is None:
                continue
            for node in capnodes:
                rank = (node.end_byte - node.start_byte, pattern)
                for i in range(node.start_byte, node.end_byte):
                    if best[i] is None or rank < best[i][0]:
                        best[i] = (rank, css)

    parts = []
    i = 0
    while i < len(src):
        css = best[i][1] if best[i] else None
        j = i
        while j < len(src) and (best[j][1] if best[j] else None) == css:
            j += 1
        text = escape(src[i:j].decode())
        parts.append(f'<span class="{css}">{text}</span>' if css else text)
        i = j
    return "".join(parts)


# ── Asset resolver ───────────────────────────────────────────────────────────

class SourceDirAssetResolver:
    """Asset resolver that resolves paths relative to the source directory."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def resolve_asset(self, path: str) -> str | None:
        """Resolve asset paths relative to source directory."""
        asset_path = self.base_dir / path
        try:
            return asset_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"Asset file not found: {asset_path}")
            return None
        except (OSError, UnicodeDecodeError) as e:
            print(f"Error reading asset file {asset_path}: {e}")
            return None


# ── Docutils nodes ───────────────────────────────────────────────────────────

class rsm_example(nodes.Element):
    pass


class rsm_iframe(nodes.Element):
    def __init__(self, path, height=None):
        super().__init__()
        self.path = path
        self.height = height


class rsm_highlighted_code(nodes.Element):
    """A code block with tree-sitter syntax highlighting."""
    def __init__(self, html, classes=None):
        super().__init__()
        self.html = html
        self.extra_classes = classes or []


# ── Directive ────────────────────────────────────────────────────────────────

class RSMDirective(Directive):
    has_content = True
    option_spec = {
        # Side by side when the page is wide enough, else stacked. "stacked"
        # stacks the source above the result at every width.
        'layout': lambda x: directives.choice(x, ('side-by-side', 'stacked')),
        'custom-css': lambda x: x.strip() if x else None,
        'source-only': lambda x: True,
        'sidebar': directives.flag,
        # A fixed height in pixels: the example scrolls inside its frame and
        # shows the minimap, instead of growing to its full length.
        'height': directives.positive_int,
    }

    def _validate(self, content):
        """Parse with strict mode to catch syntax errors, discard the result."""
        try:
            rsm.render(content, strict=True, handrails=False)
        except Exception as e:
            source_file = self.state.document.current_source
            raise type(e)(f"Error in {source_file}:\n{e}") from e

    def run(self):
        content = "\n".join(self.content)
        env = self.state.document.settings.env
        app = env.app
        custom_css = self.options.get('custom-css', None)
        source_only = 'source-only' in self.options

        n1 = rsm_highlighted_code(
            highlight_rsm(content),
            classes=["rsm-example-code"] if not source_only else ["rsm-source-only"],
        )

        if source_only:
            self._validate(content)
            return [n1]

        # A folder build, not a standalone one: every example page loads RSM's
        # static files from the docs' _static/ (see add_rsm_static_files),
        # instead of inlining 2.5 MB of script each.
        source_dir = Path(__file__).parent
        asset_resolver = SourceDirAssetResolver(source_dir)

        # Build with optional custom CSS
        build_kwargs = {
            'source': content,
            'asset_resolver': asset_resolver,
            'handrails': True,
            'standalone': False,
            'theme_toggle': False,
            'menu_position': 'right',
            'strict': True,
            'sidebar': 'sidebar' in self.options,
        }
        if custom_css:
            custom_css_path = source_dir / custom_css
            if custom_css_path.exists():
                build_kwargs['custom_css'] = str(custom_css_path)

        try:
            html_output = rsm.build(**build_kwargs)
        except Exception as e:
            source_file = self.state.document.current_source
            raise type(e)(f"Error in {source_file}:\n{e}") from e
        html_output = html_output.replace('class="manuscriptwrapper"', 'class="manuscriptwrapper embedded"')
        # The example's base size is the docs' own text size (see braiid.css).
        html_output = html_output.replace(
            "</head>", "<style>:root { --embedded-font-size: 16px; }</style>\n</head>", 1
        )
        html_output = re.sub(r"([\"'(])(?:\./)?static/", r"\1../_static/", html_output)
        # An example's frame grows to fit it and never scrolls, so the minimap
        # (which stands in for the scrollbar) is off, as with :no-minimap:,
        # except in a frame of fixed height.
        height = self.options.get('height')
        if not height:
            html_output = html_output.replace("<body ", '<body data-minimap="false" ', 1)

        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        example_dir = Path(app.outdir) / "_examples"
        example_dir.mkdir(parents=True, exist_ok=True)
        (example_dir / f"{content_hash}.html").write_text(html_output)
        # The folder build points figures at assets/<path>, so copy them there.
        # A custom stylesheet is linked by its file name alone.
        sources = {Path(custom_css).name: source_dir / custom_css} if custom_css else {}
        for ref in set(re.findall(r'(?:src|href)="assets/([^"]+)"', html_output)):
            dest = example_dir / "assets" / ref
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(sources.get(ref, source_dir / ref), dest)
        # The frame's path is relative to the page, which can sit at any depth.
        depth = self.state.document.settings.env.docname.count("/")
        n2 = rsm_iframe(f"{'../' * depth}_examples/{content_hash}.html", height)

        rsm_node = rsm_example()
        rsm_node['classes'] = ['stacked'] if self.options.get('layout') == 'stacked' else []
        rsm_node.append(n1)
        rsm_node.append(n2)
        return [rsm_node]


# ── Node visitors ────────────────────────────────────────────────────────────

def visit_rsm_highlighted_code_node(self, node):
    classes = " ".join(["highlight", "rsm-highlight"] + node.extra_classes)
    self.body.append(f'<div class="{classes}"><pre>{node.html}</pre></div>')


def depart_rsm_highlighted_code_node(self, node):
    pass


def visit_rsm_iframe_node(self, node):
    if node.height:
        self.body.append(f'''
    <div class="rsm-iframe-wrap">
      <div class="rsm-viewswitch">
        <div class="rsm-switch" role="group" aria-label="Width of the page">
          <button type="button" data-width="wide" aria-pressed="false">Wide</button>
          <button type="button" data-width="narrow" aria-pressed="false">Narrow</button>
        </div>
        <div class="rsm-switch" role="group" aria-label="Pointer of the page">
          <button type="button" data-input="mouse" aria-pressed="true">Mouse</button>
          <button type="button" data-input="touch" aria-pressed="false">Touch</button>
        </div>
      </div>
      <div class="rsm-iframe-spinner"></div>
      <iframe class="rsm-example-iframe"
              src="{node.path}"
              sandbox="allow-scripts allow-same-origin"
              onload="this.parentNode.classList.add('loaded')"
              style="height: {node.height}px;">
      </iframe>
    </div>
    ''')
        return
    iframe_html = f'''
    <div class="rsm-iframe-wrap">
      <div class="rsm-viewswitch">
        <div class="rsm-switch" role="group" aria-label="Width of the page">
          <button type="button" data-width="wide" aria-pressed="false">Wide</button>
          <button type="button" data-width="narrow" aria-pressed="false">Narrow</button>
        </div>
        <div class="rsm-switch" role="group" aria-label="Pointer of the page">
          <button type="button" data-input="mouse" aria-pressed="true">Mouse</button>
          <button type="button" data-input="touch" aria-pressed="false">Touch</button>
        </div>
      </div>
      <div class="rsm-iframe-spinner"></div>
      <iframe class="rsm-example-iframe"
              src="{node.path}"
              sandbox="allow-scripts allow-same-origin"
              scrolling="no"
              onload="var f=this;f.parentNode.classList.add('loaded');if(!f.contentWindow.document.querySelector('.manuscriptwrapper'))return;function r(){{if(f.parentNode.classList.contains('device-view'))return;var h=f.contentWindow.document.body.scrollHeight+8,c=h>640;f.style.height=(c?640:h)+'px';f.setAttribute('scrolling',c?'yes':'no');f.style.overflow=c?'auto':'hidden'}};f._fit=r;r();new ResizeObserver(r).observe(f.contentWindow.document.body);"
              style="overflow: hidden;">
      </iframe>
    </div>
    '''
    self.body.append(iframe_html)


def depart_rsm_iframe_node(self, node):
    pass


def visit_rsm_example_node(self, node):
    classes = " ".join(["rsm-example"] + node.get("classes", []))
    self.body.append(f'<div class="{classes}">')


def depart_rsm_example_node(self, node):
    self.body.append("</div>")


# ── Sphinx setup ─────────────────────────────────────────────────────────────

def add_rsm_static_files(app):
    cfg = app.config

    parent = Path(__file__).parent
    doc_static_dir = parent / "_static"
    rsm_static_dir = parent.parent.parent / "rsm" / "static"
    braiid_css = parent.parent.parent / "braiid" / "braiid.css"
    cfg.html_static_path.append(str(doc_static_dir.absolute()))
    cfg.html_static_path.append(str(rsm_static_dir.absolute()))
    cfg.html_static_path.append(str(braiid_css.absolute()))


def strip_object_from_bases(app, name, obj, options, bases):
    if object in bases:
        bases.remove(object)
    if not bases:
        bases.append(None)


def setup(app):
    app.connect("builder-inited", add_rsm_static_files)
    app.connect("autodoc-process-bases", strip_object_from_bases)
    app.add_directive("rsm", RSMDirective)
    app.add_node(rsm_example, html=(visit_rsm_example_node, depart_rsm_example_node))
    app.add_node(rsm_iframe, html=(visit_rsm_iframe_node, depart_rsm_iframe_node))
    app.add_node(
        rsm_highlighted_code,
        html=(visit_rsm_highlighted_code_node, depart_rsm_highlighted_code_node),
    )
