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

# Map CST node types to tok-* CSS classes.
# Mirrors the capture-to-token mapping in highlights.scm / the LSP.
_NODE_TYPE_TO_CLASS = {
    # Block tags (keywords)
    "theorem": "tok-keyword", "lemma": "tok-keyword", "corollary": "tok-keyword",
    "proposition": "tok-keyword", "definition": "tok-keyword", "remark": "tok-keyword",
    "example": "tok-keyword", "exercise": "tok-keyword", "problem": "tok-keyword",
    "porism": "tok-keyword",
    # Proof environments
    "proof": "tok-keyword", "sketch": "tok-keyword", "subproof": "tok-keyword",
    "calc": "tok-keyword",
    # Proof constructs
    "assume": "tok-keyword", "case": "tok-keyword", "claim": "tok-keyword",
    "define": "tok-keyword", "let": "tok-keyword", "new": "tok-keyword",
    "pick": "tok-keyword", "prove": "tok-keyword", "st": "tok-keyword",
    "suffices": "tok-keyword", "suppose": "tok-keyword", "then": "tok-keyword",
    "wlog": "tok-keyword", "write": "tok-keyword",
    "step": "tok-modifier", "qed": "tok-enumMember",
    # Document structure
    "abstract": "tok-keyword", "author": "tok-keyword", "config": "tok-keyword",
    "figure": "tok-keyword", "video": "tok-keyword", "html": "tok-keyword",
    "enumerate": "tok-keyword", "itemize": "tok-keyword",
    "appendix": "tok-keyword", "toc": "tok-keyword",
    "table": "tok-keyword", "thead": "tok-keyword", "tbody": "tok-keyword",
    "tr": "tok-keyword", "td": "tok-keyword", "caption": "tok-keyword",
    # Inline tags
    "draft": "tok-modifier", "note": "tok-modifier", "span": "tok-modifier",
    # Special inlines
    "math": "tok-operator", "code": "tok-operator",
    "ref": "tok-function", "cite": "tok-function", "url": "tok-function",
    "previous": "tok-function", "prev": "tok-function",
    "prev2": "tok-function", "prev3": "tok-function",
    "spanemphas": "tok-operator", "spanstrong": "tok-operator",
    # Math/code content
    "asis_text": "tok-macro",
    # Meta
    "name": "tok-property", "affiliation": "tok-property", "email": "tok-property",
    "label": "tok-property", "title": "tok-property", "reftext": "tok-property",
    "orcid": "tok-property", "author_note": "tok-property",
    "emphas": "tok-property", "strong": "tok-property", "nonum": "tok-property",
    "isclaim": "tok-property", "keywords": "tok-property", "msc": "tok-property",
    "class": "tok-property", "icon": "tok-property", "alt": "tok-property",
    "goal": "tok-property", "lang": "tok-property", "path": "tok-property",
    "accent": "tok-property", "typography": "tok-property",
    "numbering": "tok-property", "override_date": "tok-property",
    "toc_depth": "tok-property", "scale": "tok-property",
    "static": "tok-property", "theme": "tok-property", "dark": "tok-property",
    "author_display_first": "tok-property", "author_display_last": "tok-property",
    "metaval_text": "tok-string", "metaval_list": "tok-string",
    # Bibliography
    "kind": "tok-type", "key": "tok-property", "value": "tok-string",
    # Delimiters
    "::": "tok-operator", "{": "tok-operator", "}": "tok-operator",
    ":-:": "tok-operator", "@": "tok-operator",
    # Comments
    "comment": "tok-comment",
}

_TS_LANG = tree_sitter.Language(tree_sitter_rsm.language())
_TS_PARSER = tree_sitter.Parser(_TS_LANG)


def _collect_leaf_spans(node, spans):
    """Walk the CST and collect (start_byte, end_byte, css_class) for leaf nodes."""
    css = _NODE_TYPE_TO_CLASS.get(node.type)
    if css and node.child_count == 0:
        spans.append((node.start_byte, node.end_byte, css))
    elif node.type == "asis_text":
        # asis_text may have children but we want to highlight the whole thing
        spans.append((node.start_byte, node.end_byte, "tok-macro"))
    else:
        # Check if this is a heading text node (title field of source_file or section)
        if node.type == "text" and node.parent:
            parent_type = node.parent.type
            if parent_type in ("source_file", "section", "subsection", "subsubsection"):
                spans.append((node.start_byte, node.end_byte, "tok-namespace"))
                return
        for child in node.children:
            _collect_leaf_spans(child, spans)


def highlight_rsm(source: str) -> str:
    """Return HTML with tok-* spans for RSM source code."""
    tree = _TS_PARSER.parse(source.encode())
    spans = []
    _collect_leaf_spans(tree.root_node, spans)
    spans.sort(key=lambda s: (s[0], -s[1]))

    src_bytes = source.encode()
    parts = []
    pos = 0
    for start, end, css in spans:
        if start < pos:
            continue
        if start > pos:
            parts.append(escape(src_bytes[pos:start].decode()))
        parts.append(f'<span class="{css}">')
        parts.append(escape(src_bytes[start:end].decode()))
        parts.append("</span>")
        pos = end
    if pos < len(src_bytes):
        parts.append(escape(src_bytes[pos:].decode()))

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
    def __init__(self, path):
        super().__init__()
        self.path = path


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
            'strict': True
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
        html_output = re.sub(r"([\"'(])(?:\./)?static/", r"\1../_static/", html_output)
        # An example's frame grows to fit it and never scrolls, so the minimap
        # (which stands in for the scrollbar) is off, as with :no-minimap:.
        html_output = html_output.replace("<body ", '<body data-minimap="false" ', 1)
        html_output = html_output.replace(
            "</head>", '<link rel="stylesheet" href="../_static/docs-frame.css">\n</head>', 1
        )

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
        n2 = rsm_iframe(f"../_examples/{content_hash}.html")

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
    iframe_html = f'''
    <div class="rsm-iframe-wrap">
      <div class="rsm-iframe-spinner"></div>
      <iframe class="rsm-example-iframe"
              src="{node.path}"
              sandbox="allow-scripts allow-same-origin"
              scrolling="no"
              onload="var f=this;function r(){{f.style.height=(f.contentWindow.document.documentElement.scrollHeight+8)+'px'}};r();f.parentNode.classList.add('loaded');new ResizeObserver(r).observe(f.contentWindow.document.documentElement);"
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
