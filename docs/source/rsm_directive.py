"""
rsm_directive.py
----------------

Highlight and render RSM code blocks.

"""

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


class RSMDirective(Directive):
    has_content = True

    def run(self):
        content = "\n".join(self.content)
        n1 = nodes.literal_block(content, content)
        n1["language"] = "text"
        n1["classes"].append("rsm-example-code")
        print(f"\n{'='*60}\nRSM DIRECTIVE RENDERING:\n{repr(content)}\n{'='*60}\n")
        n2 = rsm_body(rsm.render(content, handrails=True))
        rsm_node = rsm_example()
        rsm_node.append(n1)
        rsm_node.append(n2)
        return [rsm_node]


def visit_rsm_body_node(self, node):
    # strip the enclosing <body> tag
    from_idx = node.body.index(startstr := "<body>") + len(startstr)
    upto_idx = node.body.rindex(finalstr := "</body>")
    body = node.body[from_idx:upto_idx]
    body = body.replace(
        'class="manuscriptwrapper"', 'class="manuscriptwrapper embedded"'
    )
    self.body.append(body)


def depart_rsm_body_node(self, node):
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

    # main styles are applied to the manuscripts rendered by the .. rsm:: directive
    app.add_css_file("rsm.css")

    # make sure tooltipster is available
    app.add_css_file("tooltipster.bundle.css")
    app.add_js_file("tooltipster.bundle.js")

    # open in live editor button
    app.add_js_file("openlive.js")

    # this adds a <script type="module">...</script> tag to each page
    app.add_js_file(
        None,
        type="module",
        body="""\
        import { onload } from '../_static/onload.js';
        window.addEventListener('load', (ev)=>{onload('"""
        + (cfg.rsm_static_path_prod if cfg.rsm_build_prod else cfg.rsm_static_path_dev)
        + "')});\n",
    )


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
