"""
rsm_directive.py
----------------

Highlight and render RSM code blocks.

"""

import hashlib
import html
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive

import rsm


class rsm_example(nodes.Element):
    pass


class rsm_body(nodes.Element):
    def __init__(self, body):
        super().__init__()
        self.body = body


class rsm_file_ref(nodes.Element):
    def __init__(self, path):
        super().__init__()
        self.path = path


class RSMDirective(Directive):
    has_content = True

    def run(self):
        content = "\n".join(self.content)
        env = self.state.document.settings.env
        app = env.app

        n1 = nodes.literal_block(content, content)
        n1["language"] = "text"
        n1["classes"].append("rsm-example-code")
        print(f"\n{'='*60}\nRSM DIRECTIVE RENDERING:\n{repr(content)}\n{'='*60}\n")

        # Use standalone mode but we need to inline RSM CSS since CDN @import doesn't work in iframes
        html_output = rsm.build(source=content, handrails=True, standalone=True, theme_toggle=False, menu_position="right")
        html_output = html_output.replace('class="manuscriptwrapper"', 'class="manuscriptwrapper embedded"')

        # Replace CDN CSS links with inlined CSS to ensure Pygments works
        rsm_css_path = Path(__file__).parent.parent.parent / "rsm" / "static" / "rsm.css"
        pygments_css_path = Path(__file__).parent.parent.parent / "rsm" / "static" / "pygments.css"

        if rsm_css_path.exists() and pygments_css_path.exists():
            rsm_css = rsm_css_path.read_text()
            pygments_css = pygments_css_path.read_text()

            # Remove the @import for pygments since we're inlining it directly
            rsm_css = rsm_css.replace("@import url('pygments.css') layer(base);", "")

            inlined_css = f"""<style>
{pygments_css}
{rsm_css}
</style>"""

            # Replace the CDN link with inlined CSS
            html_output = html_output.replace(
                '<link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/gh/aris-pub/rsm@main/rsm/static/rsm.css" />',
                inlined_css
            )

        if app.config.rsm_build_prod:
            # Production: Inline via srcdoc for complete isolation
            n2 = rsm_body(html_output)
        else:
            # Development: Save to file for easier debugging
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            example_dir = Path(app.outdir) / "_examples"
            example_dir.mkdir(parents=True, exist_ok=True)
            (example_dir / f"{content_hash}.html").write_text(html_output)
            n2 = rsm_file_ref(f"/_examples/{content_hash}.html")

        rsm_node = rsm_example()
        rsm_node.append(n1)
        rsm_node.append(n2)
        return [rsm_node]


def visit_rsm_body_node(self, node):
    # Use the full HTML document in an iframe for complete isolation
    # Escape HTML for srcdoc attribute
    escaped_html = html.escape(node.body, quote=True)

    # Create iframe with auto-resize script
    iframe_html = f'''
    <iframe class="rsm-example-iframe"
            srcdoc="{escaped_html}"
            sandbox="allow-scripts allow-same-origin"
            onload="this.style.height = (this.contentWindow.document.documentElement.scrollHeight + 8) + 'px';"
            style="width: 100%; border: 1px solid var(--pst-color-border); border-radius: 4px; background: white;">
    </iframe>
    '''

    self.body.append(iframe_html)


def depart_rsm_body_node(self, node):
    pass


def visit_rsm_file_ref_node(self, node):
    # File-based iframe for development mode
    # Height is set via postMessage from iframe after RSM onload completes
    iframe_html = f'''
    <iframe class="rsm-example-iframe"
            src="{node.path}"
            sandbox="allow-scripts allow-same-origin"
            style="width: 100%; border: 1px solid var(--pst-color-border); border-radius: 4px; background: white;">
    </iframe>
    '''
    self.body.append(iframe_html)


def depart_rsm_file_ref_node(self, node):
    pass


def visit_rsm_example_node(self, node):
    self.body.append('<div class="rsm-example">')


def depart_rsm_example_node(self, node):
    self.body.append("</div>")


def add_rsm_static_files(app):
    cfg = app.config

    # paths
    parent = Path(__file__).parent
    doc_static_dir = parent / "_static"
    rsm_static_dir = parent.parent.parent / "rsm" / "static"
    cfg.html_static_path.append(str(doc_static_dir.absolute()))
    cfg.html_static_path.append(str(rsm_static_dir.absolute()))

    # No longer needed - each iframe contains its own complete HTML with all assets
    # The rsm.render() output includes all CSS/JS needed for the manuscript


def strip_object_from_bases(app, name, obj, options, bases):
    if object in bases:
        bases.remove(object)
    if not bases:
        bases.append(None)


def setup(app):
    app.connect("builder-inited", add_rsm_static_files)
    app.connect("autodoc-process-bases", strip_object_from_bases)
    app.add_config_value("rsm_static_path_dev", "/_static/", "html")
    app.add_config_value("rsm_static_path_prod", "/en/latest/_static/", "html")
    app.add_config_value("rsm_build_prod", False, "html")
    app.add_directive("rsm", RSMDirective)
    app.add_node(rsm_example, html=(visit_rsm_example_node, depart_rsm_example_node))
    app.add_node(rsm_body, html=(visit_rsm_body_node, depart_rsm_body_node))
    app.add_node(rsm_file_ref, html=(visit_rsm_file_ref_node, depart_rsm_file_ref_node))
