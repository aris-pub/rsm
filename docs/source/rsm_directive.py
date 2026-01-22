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

        if app.config.rsm_build_prod:
            # Production: Use StandaloneBuilder with CDN (no cache issues, works offline)
            html_output = rsm.build(source=content, handrails=True, standalone=True, theme_toggle=False, menu_position="right")
            html_output = html_output.replace('class="manuscriptwrapper"', 'class="manuscriptwrapper embedded"')
            n2 = rsm_body(html_output)
        else:
            # Development: Use FolderBuilder with local /_static/ files (instant CSS updates)
            html_output = rsm.build(source=content, handrails=True, standalone=False, theme_toggle=False, menu_position="right")

            # Fix all static paths for Sphinx (/static/ -> /_static/)
            html_output = html_output.replace('"/static/', '"/_static/')
            html_output = html_output.replace("'/static/", "'/_static/")
            html_output = html_output.replace('class="manuscriptwrapper"', 'class="manuscriptwrapper embedded"')

            # Inject script to signal parent after content stabilizes
            resize_script = """
            <script>
              window.addEventListener('load', function() {
                let lastHeight = 0;
                let stableCount = 0;

                function checkHeight() {
                  const currentHeight = document.documentElement.scrollHeight;
                  if (currentHeight === lastHeight) {
                    stableCount++;
                    if (stableCount >= 3) {
                      window.parent.postMessage({type: 'rsm-resize', height: currentHeight + 8}, '*');
                      return;
                    }
                  } else {
                    stableCount = 0;
                    lastHeight = currentHeight;
                  }
                  setTimeout(checkHeight, 100);
                }

                setTimeout(checkHeight, 100);
              });
            </script>
            """
            html_output = html_output.replace('</body>', resize_script + '</body>')

            # Save to file with content-based hash for caching
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            example_dir = Path(app.outdir) / "_examples"
            example_dir.mkdir(parents=True, exist_ok=True)
            (example_dir / f"{content_hash}.html").write_text(html_output)

            # Create iframe pointing to the file
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
