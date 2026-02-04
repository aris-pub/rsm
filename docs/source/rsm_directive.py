"""
rsm_directive.py
----------------

Highlight and render RSM code blocks.

"""

import hashlib
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive

import rsm


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


class rsm_example(nodes.Element):
    pass


class rsm_iframe(nodes.Element):
    def __init__(self, path):
        super().__init__()
        self.path = path


class RSMDirective(Directive):
    has_content = True
    option_spec = {
        'layout': lambda x: x.strip().lower() if x else 'horizontal',
        'custom-css': lambda x: x.strip() if x else None
    }

    def run(self):
        content = "\n".join(self.content)
        env = self.state.document.settings.env
        app = env.app
        layout = self.options.get('layout', 'horizontal')
        custom_css = self.options.get('custom-css', None)

        n1 = nodes.literal_block(content, content)
        n1["language"] = "text"
        n1["classes"].append("rsm-example-code")

        # Use standalone mode - it uses CDN for CSS and inlines JavaScript
        # Use custom asset resolver to resolve paths relative to source directory
        source_dir = Path(__file__).parent
        asset_resolver = SourceDirAssetResolver(source_dir)

        # Build with optional custom CSS
        build_kwargs = {
            'source': content,
            'asset_resolver': asset_resolver,
            'handrails': True,
            'standalone': True,
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

        # Fix relative paths to _static to work from _examples/ directory
        # Go up one level from _examples/ to reach _static/
        html_output = html_output.replace('src="_static/', 'src="../_static/')

        # Save to file and reference via iframe src
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        example_dir = Path(app.outdir) / "_examples"
        example_dir.mkdir(parents=True, exist_ok=True)
        (example_dir / f"{content_hash}.html").write_text(html_output)
        n2 = rsm_iframe(f"../_examples/{content_hash}.html")

        rsm_node = rsm_example()
        rsm_node['classes'] = []
        if layout == 'vertical':
            rsm_node['classes'].append('vertical')
        rsm_node.append(n1)
        rsm_node.append(n2)
        return [rsm_node]


def visit_rsm_iframe_node(self, node):
    # Iframe loads from file, height is set via onload to match content height
    iframe_html = f'''
    <iframe class="rsm-example-iframe"
            src="{node.path}"
            sandbox="allow-scripts allow-same-origin"
            onload="this.style.height = (this.contentWindow.document.documentElement.scrollHeight + 8) + 'px';"
            style="width: 100%; border: 1px solid var(--pst-color-border); border-radius: 4px; background: white;">
    </iframe>
    '''
    self.body.append(iframe_html)


def depart_rsm_iframe_node(self, node):
    pass


def visit_rsm_example_node(self, node):
    classes = ['rsm-example']
    if 'vertical' in node.get('classes', []):
        classes.append('vertical')
    self.body.append(f'<div class="{" ".join(classes)}">')


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
    app.add_directive("rsm", RSMDirective)
    app.add_node(rsm_example, html=(visit_rsm_example_node, depart_rsm_example_node))
    app.add_node(rsm_iframe, html=(visit_rsm_iframe_node, depart_rsm_iframe_node))
