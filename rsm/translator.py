"""Input: abstract syntax tree -- Output: HTML body.

The translator takes the finished abstract manuscript tree and translates its content to
HTML.

Two main classes handle this process: :class:`Translator` and :class:`EditCommand`.
:class:`Translator` traverses the manuscript tree in depth-first order and implements a
generic visitor pattern.  That is, when a node ``n`` of class ``cls`` is visited, the
method ``visit_cls(n)`` is called.  Then, all of ``n``'s children are visited in order.
Finally, the method ``leave_cls(n)`` is called.

Each ``visit_*`` and ``leave_*`` method returns an object of type :class:`EditCommand`.
This class implements a command pattern whose sole purpose is to append text to the
underlying HTML string that is being built.  The simplest example is :class:`AppendText`
which simply appends an arbitrary string to the underlying HTML.  For example,
:meth:`~rsm.translator.Translator.visit_node` returns an :class:`AppendText` instance
which adds some basic information about the node to the HTML output.

The visit method ``visit_cls`` returns the HTML markup that needs to appear *before* the
node's children's markup, while ``leave_cls`` returns the HTML markup that appears
*after* all its children.

Suppose a new kind of node is created, called ``NewNodeClass``.  To implement the
translation step for this new class of node, implement a new method in
:class:`Translator` with signature

.. code-block:: python

   def visit_newnodeclass(self, node: NewNodeClass) -> EditCommand: ...

Optionally, also implement a leave method with signature

.. code-block:: python

   def leave_newnodeclass(self, node: NewNodeClass) -> EditCommand: ...

If a method of the appropriate name is not found, :class:`Translator` will look up the
inheritance tree of ``NewNodeClass`` until it finds a class with an existing method.
For example, if ``NewNodeClass`` inherits directly from :class:`~rsm.nodes.Span`, and a
``visit_newnodeclass`` method is not found, then ``visit_span`` will be called with the
visited instance of ``NewNodeClass``.  Since all nodes must subclass
:class:`~rsm.nodes.Node`, this process will ultimately end up calling
:meth:`~rsm.translator.Translator.visit_node` if no other bases of ``NewNodeClass`` have
a ``visit_*`` method.  The same is true for ``leave_*`` methods.

Since HTML has both opening and closing tags, the vast majority of which must be kept
balanced, care must be taken that the method ``leave_cls`` always closes any tags that
were left open in the corresponding ``visit_cls`` method.  RSM handles this
automatically in the following way.  Besides the basic :class:`AppendText` class, there
are other :class:`EditCommand` subclasses that accept some text that should be
*deferred* until the coresponding ``leave_*`` method is called on the same node.  This
deferred text is then automatically appended to the generated HTML *unless this process
is overridden* (see below).

For example, suppose nodes of class ``NewNodeClass`` should be translated to HTML by
wrapping their text contents in a ``div`` of class ``"wrapper"``.  We need only
implement a single method, namely

.. code-block:: python

   def visit_newnodeclass(self, node: NewNodeClass) -> EditCommand:
       content = f'<div class="wrapper">{node.text}'
       return AppendTextAndDefer(content, "</div>")

This tells the translator that when visiting a ``NewNodeClass`` node, the text ``"<div
class="wrapper">"``, followed by the text contents of the node, should be appended to
the generated HTML immediately, while the text ``"</div>"`` should be deferred and
appended only when ``leave_newnodeclass`` is called on that same node.  This will, as
usual, happen after the node's children have each been visited and exited.  Note there
is no need to manually implement a ``leave_newnodeclass`` method that will close the
``div`` tag.  In this way, all opening and closing HTMl tags may be specified in the
same method, and there is no need to manually coordinate the ``visit_*`` and ``leave_*``
methods of the same node class.  For this reason, most node classes do not implement a
``leave_*`` class at all.

If a ``leave_*`` method is implemented, this process will no longer work and manual
coordination must take place.  In the example above, if the node has some extra metadata
that needs to appear after its children's content, say in ``node.metadata``, then one
may implement a ``leave_*`` method such as

.. code-block:: python

   def leave_newnodeclass(self, node: NewNodeClass) -> EditCommand:
       return AppendText(f'{node.metadata}\\n</div>')

Note the need to manually close the ``</div>`` tag that was left open.

This example which manually specifies the text to be deferred (``</div>``) is for
illustration purposes only.  In reality, there exist subclasses of :class:`EditCommand`
that handle this automatically.  In fact, the example above where only the wrapper div
is necessary necessary (i.e. there is no ``node.text`` nor ``node.metadata``), could
instead be implemented simply as

.. code-block:: python

   def visit_newnodeclass(self, node: NewNodeClass) -> EditCommand:
       return AppendNodeTag(node, additional_classes="wrapper")

with no need of a ``leave`` method.  :class:`AppendNodeTag` knows to use the node's
attributes to generate the ``div``, as well as to defer its closing.  Indeed,
:class:`AppendNodeTag` is a sublcass of :class:`AppendTextAndDefer`.

There are two translator classes in this module.  The base translator
:class:`Translator` implements the visit and leave methods necessary to generate a
simple human-readable HTML output.  It is the translator class used by ``rsm-render``.
:class:`HandrailsTranslator` is a subclass of :class:`Translator` and overrides some
visit and leave methods to add handrails to the output.  It is the translator class used
by ``rsm-build``.

"""

import copy
import logging
import re
import textwrap
import uuid
from abc import ABC, abstractmethod
from collections import namedtuple
from collections.abc import Callable, Iterable
from html import escape as html_escape
from html import unescape as html_unescape
from pathlib import Path
from typing import Any, Literal, TypeVar, cast, overload

from . import nodes
from . import proof as proofmodel
from .asset_resolver import AssetResolver
from .util import highlight_code

logger = logging.getLogger("RSM").getChild("tlate")


def _tabler(paths: str, filled: bool = False) -> str:
    """A Tabler icon (24px grid) as inline SVG; *paths* is its inner markup."""
    if filled:
        attrs = 'fill="currentColor"'
    else:
        attrs = (
            'fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"'
        )
    return f'<svg viewBox="0 0 24 24" {attrs} aria-hidden="true">{paths}</svg>'


# Sidebar icons, all Tabler: hierarchy-3 (contents), writing-sign (notation),
# binary-tree-2 (proof steps), list-details (proof state), pin, typography
# (reading), link (copy a link to this view).
_RAIL_CONTENTS_ICON = _tabler(
    '<path d="M12 5m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/>'
    '<path d="M8 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/>'
    '<path d="M12 19m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/>'
    '<path d="M20 19m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/>'
    '<path d="M4 19m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/>'
    '<path d="M16 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/>'
    '<path d="M5 17l2 -3"/><path d="M9 10l2 -3"/><path d="M13 7l2 3"/>'
    '<path d="M17 14l2 3"/><path d="M15 14l-2 3"/><path d="M9 14l2 3"/>'
)
# Tabler list: the list button of the table of contents' list/graph switch.
_TOC_LIST_ICON = _tabler(
    '<path d="M9 6l11 0"/><path d="M9 12l11 0"/><path d="M9 18l11 0"/>'
    '<path d="M5 6l0 .01"/><path d="M5 12l0 .01"/><path d="M5 18l0 .01"/>'
)


def _toc_switch(tree: bool, extra_class: str = "") -> str:
    """The list/graph buttons of a table of contents. *tree* is the view shown
    first. braiid.css hides the page's buttons until html.has-toc-switch is
    set, since they only work with scripting on."""
    buttons = []
    for view, label, icon in (
        ("list", "Show as list", _TOC_LIST_ICON),
        ("tree", "Show as graph", _RAIL_CONTENTS_ICON),
    ):
        pressed = "true" if (view == "tree") == tree else "false"
        buttons.append(
            f'<button type="button" class="toc-switch-btn" data-toc-view="{view}" '
            f'title="{label}" aria-label="{label}" aria-pressed="{pressed}">{icon}</button>'
        )
    classes = "toc-switch" + (f" {extra_class}" if extra_class else "")
    return f'<div class="{classes}">' + "".join(buttons) + "</div>"


_RAIL_NOTATION_ICON = _tabler(
    '<path d="M3 19c3.333 -2 5 -4 5 -6c0 -3 -1 -3 -2 -3s-2.032 1.085 -2 3c.034 '
    "2.048 1.658 2.877 2.5 4c1.5 2 2.5 2.5 3.5 1c.667 -1 1.167 -1.833 1.5 -2.5c1 "
    '2.333 2.333 3.5 4 3.5h2.5"/>'
    '<path d="M20 17v-12c0 -1.121 -.879 -2 -2 -2s-2 .879 -2 2v12l2 2l2 -2z"/>'
    '<path d="M16 7h4"/>'
)
_RAIL_STEPS_ICON = _tabler(
    '<path d="M14 6a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z"/>'
    '<path d="M7 14a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z"/>'
    '<path d="M21 14a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z"/>'
    '<path d="M14 18a2 2 0 1 0 -4 0a2 2 0 0 0 4 0z"/>'
    '<path d="M12 8v8"/><path d="M6.316 12.496l4.368 -4.992"/>'
    '<path d="M17.684 12.496l-4.366 -4.99"/>'
)
_RAIL_STATE_ICON = _tabler(
    '<path d="M13 5h8"/><path d="M13 9h5"/><path d="M13 15h8"/><path d="M13 19h5"/>'
    '<path d="M3 4m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z"/>'
    '<path d="M3 14m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z"/>'
)
_RAIL_PIN_ICON = _tabler(
    '<path d="M15 4.5l-4 4l-4 1.5l-1.5 1.5l7 7l1.5 -1.5l1.5 -4l4 -4"/>'
    '<path d="M9 15l-4.5 4.5"/><path d="M14.5 4l5.5 5.5"/>'
)
_RAIL_READING_ICON = _tabler(
    '<path d="M4 20l3 0"/><path d="M14 20l7 0"/><path d="M6.9 15l6.9 0"/>'
    '<path d="M10.2 6.3l5.8 13.7"/><path d="M5 20l6 -16l2 0l7 16"/>'
)
_RAIL_SHARE_ICON = _tabler(
    '<path d="M9 15l6 -6"/>'
    '<path d="M11 6l.463 -.536a5 5 0 0 1 7.071 7.072l-.534 .464"/>'
    '<path d="M13 18l-.397 .534a5.068 5.068 0 0 1 -7.127 0a4.972 4.972 0 0 1 0 -7.071l.524 -.463"/>'
)
# Reader type controls in the sidebar's Reading view. Each row toggles a root
# data-reading-* attribute the stylesheet keys on (overriding a CSS variable);
# the default value carries no attribute, so an untouched reader inherits the
# author's build defaults. Theme sets .dark-theme / .light-theme, or neither
# for System (follow the operating system). Every option is a small preview
# tile; its name is the button's accessible name and interface tooltip.
_READING_CONTROLS = [
    (
        "typeface",
        "Typeface",
        [("sans", "Sans"), ("serif", "Serif"), ("legible", "Legible")],
        "sans",
    ),
    (
        "size",
        "Size",
        [("1", "Small"), ("2", "Default"), ("3", "Large"), ("4", "Larger")],
        "2",
    ),
    (
        "leading",
        "Line height",
        [("tight", "Tight"), ("normal", "Normal"), ("loose", "Loose")],
        "normal",
    ),
    (
        "measure",
        "Width",
        [("narrow", "Narrow"), ("normal", "Normal"), ("wide", "Wide")],
        "normal",
    ),
    (
        "theme",
        "Theme",
        [("system", "System"), ("light", "Light"), ("dark", "Dark")],
        "system",
    ),
    # The document map at the right edge (minimap.js watches the attribute).
    # Left out when the author turned the map off with :no-minimap:.
    (
        "minimap",
        "Map",
        [("on", "Show the document map"), ("off", "Hide the document map")],
        "on",
    ),
]


def _lines_glyph(ys: tuple, x0: float = 5, x1: float = 19, last: float = 14) -> str:
    """Text lines drawn on the Tabler grid: a preview of line height or width."""
    d = "".join(
        f"M{x0} {y}h{(last if i == len(ys) - 1 else x1) - x0}" for i, y in enumerate(ys)
    )
    return _tabler(f'<path d="{d}"/>')


_READING_TILES = {
    ("leading", "tight"): _lines_glyph((8, 11, 14, 17)),
    ("leading", "normal"): _lines_glyph((6, 10, 14, 18)),
    ("leading", "loose"): _lines_glyph((4, 9.33, 14.67, 20)),
    ("measure", "narrow"): _tabler('<path d="M3 4v16M21 4v16M9 8h6M9 12h6M9 16h4"/>'),
    ("measure", "normal"): _tabler('<path d="M3 4v16M21 4v16M7 8h10M7 12h10M7 16h6"/>'),
    ("measure", "wide"): _tabler(
        '<path d="M3 4v16M21 4v16M5.5 8h13M5.5 12h13M5.5 16h8"/>'
    ),
    ("theme", "system"): _tabler(
        '<path d="M3 5a1 1 0 0 1 1 -1h16a1 1 0 0 1 1 1v10a1 1 0 0 1 -1 1h-16a1 1 0 0 1 -1 -1v-10z"/>'
        '<path d="M7 20h10"/><path d="M9 16v4"/><path d="M15 16v4"/>'
    ),
    ("theme", "light"): _tabler(
        '<path d="M12 12m-4 0a4 4 0 1 0 8 0a4 4 0 1 0 -8 0"/>'
        '<path d="M3 12h1m8 -9v1m8 8h1m-9 8v1m-6.4 -15.4l.7 .7m12.1 -.7l-.7 .7m0 '
        '11.4l.7 .7m-12.1 -.7l-.7 .7"/>'
    ),
    ("theme", "dark"): _tabler(
        '<path d="M12 3c.132 0 .263 0 .393 0a7.5 7.5 0 0 0 7.92 12.446a9 9 0 1 1 '
        '-8.313 -12.454z"/>'
    ),
    # A page with the map strip and its marks at the right edge, and the same
    # page without it.
    ("minimap", "on"): _tabler(
        '<path d="M4 4h16v16h-16z"/><path d="M15 4v16"/>'
        '<path d="M7 8h5M7 12h5M7 16h3M17 8h1M17 13h1"/>'
    ),
    ("minimap", "off"): _tabler(
        '<path d="M4 4h16v16h-16z"/><path d="M7 8h10M7 12h10M7 16h6"/>'
    ),
}


def _reading_tile(control: str, value: str) -> str:
    if control == "typeface":
        return (
            f'<span class="reading-ag" data-face="{value}" aria-hidden="true">Ag</span>'
        )
    if control == "size":
        return (
            f'<span class="reading-a" data-size="{value}" aria-hidden="true">A</span>'
        )
    return _READING_TILES[(control, value)]


def minimap_enabled(tree: Any) -> bool:
    """False when the author wrote :config: { :no-minimap: }."""
    return not getattr(tree, "no_minimap", False)


def _make_reading_panel(typeface_default: str = "sans", minimap: bool = True) -> str:
    from html import escape

    rows = []
    for control, label, options, default in _READING_CONTROLS:
        if control == "minimap" and not minimap:
            continue
        # The Typeface row's resting tile is the manuscript's built-in
        # typography, not a fixed constant, so a serif document opens with Serif
        # pressed. Mirrors how the Theme row rests on System.
        if control == "typeface":
            default = typeface_default
        opts = []
        for value, name in options:
            active = " active" if value == default else ""
            pressed = "true" if value == default else "false"
            opts.append(
                f'<button type="button" class="reading-opt{active}" data-value="{value}" '
                f'aria-pressed="{pressed}" aria-label="{escape(name)}" '
                f'data-tip="{escape(name)}">{_reading_tile(control, value)}</button>'
            )
        rows.append(
            f'<div class="reading-row" data-control="{control}">'
            f'<span class="reading-label">{escape(label)}</span>'
            f'<div class="reading-opts" role="group" aria-label="{escape(label)}">'
            + "".join(opts)
            + "</div></div>"
        )
    return (
        '<div class="rail-section rail-reading">'
        '<div class="rail-reading-panel">' + "".join(rows) + "</div></div>"
    )


def _reject_html_wrapper(path: str | Path) -> None:
    """Raise if an embedded HTML asset contains document-level wrapper tags."""
    raise RSMTranslatorError(
        f"HTML asset '{path}' contains <!DOCTYPE>, <html>, or <body> tags. "
        f"Embedded HTML figures must be fragments, not full documents. "
        f"Remove the document wrapper and keep only the content."
    )


def _process_html_with_scripts(html_content: str) -> str:
    """Process HTML content to ensure JavaScript executes when dynamically inserted.

    When HTML content is inserted via innerHTML or v-html, script tags don't execute
    automatically. This function processes all scripts to ensure proper execution order,
    especially handling dependencies between external and inline scripts.

    Parameters
    ----------
    html_content : str
        Raw HTML content that may contain script tags

    Returns
    -------
    str
        Processed HTML with scripts that will execute when inserted
    """
    if not html_content or "<script" not in html_content.lower():
        return html_content

    # Find all script tags and process them in order
    script_pattern = re.compile(
        r"<script([^>]*)>(.*?)</script>", re.DOTALL | re.IGNORECASE
    )

    scripts = list(script_pattern.finditer(html_content))
    if not scripts:
        return html_content

    # Build a queue of scripts to execute in order
    processed_scripts = []
    external_scripts: list[dict[str, Any]] = []

    for _i, match in enumerate(scripts):
        attributes = match.group(1)
        script_content = match.group(2)

        if "src=" in attributes.lower():
            # External script - extract URL and add to queue
            src_match = re.search(r'src=["\']([^"\']+)["\']', attributes, re.IGNORECASE)
            if src_match:
                src_url = src_match.group(1)
                script_id = f"rsm_script_{uuid.uuid4().hex[:8]}"
                external_scripts.append(
                    {
                        "url": src_url,
                        "id": script_id,
                        "async": "async" in attributes.lower(),
                        "defer": "defer" in attributes.lower(),
                    }
                )
        else:
            # Inline script - add to execution queue
            if script_content.strip():
                escaped_content = script_content.replace("</script>", "<\\/script>")
                processed_scripts.append(escaped_content)

    if not processed_scripts and not external_scripts:
        return html_content

    # Generate execution script that handles dependencies
    execution_script = (
        """<script>
(function() {
    var scriptsLoaded = 0;
    var totalExternalScripts = """
        + str(len(external_scripts))
        + """;
    var inlineScripts = ["""
        + ",\n        ".join(
            f'function() {{ try {{ {script} }} catch (e) {{ console.warn("RSM: Error executing script:", e); }} }}'
            for script in processed_scripts
        )
        + """];

    function executeInlineScripts() {
        if (scriptsLoaded >= totalExternalScripts) {
            inlineScripts.forEach(function(scriptFunc, index) {
                try {
                    scriptFunc();
                } catch (e) {
                    console.warn('RSM: Error executing inline script ' + index + ':', e);
                }
            });
        }
    }

    function onScriptLoad() {
        scriptsLoaded++;
        executeInlineScripts();
    }
"""
    )

    # Add external script loading
    for script in external_scripts:
        execution_script += f"""
    // Load external script: {script["url"]}
    var script_{script["id"]} = document.createElement('script');
    script_{script["id"]}.src = '{script["url"]}';
    script_{script["id"]}.id = '{script["id"]}';
    {("script_" + script["id"] + ".async = true;" if script["async"] else "")}
    {("script_" + script["id"] + ".defer = true;" if script["defer"] else "")}
    script_{script["id"]}.onload = onScriptLoad;
    script_{script["id"]}.onerror = onScriptLoad; // Continue even if script fails
    document.head.appendChild(script_{script["id"]});
"""

    execution_script += """

    // If no external scripts, execute inline scripts immediately
    if (totalExternalScripts === 0) {
        executeInlineScripts();
    }
})();
</script>"""

    # Replace all original script tags with our execution script
    result = script_pattern.sub("", html_content)
    result += execution_script

    return result


class RSMTranslatorError(Exception):
    pass


_DOI_RESOLVER_PREFIXES = (
    "https://doi.org/",
    "http://doi.org/",
    "https://dx.doi.org/",
    "http://dx.doi.org/",
)


def _normalize_doi(doi: str) -> str:
    # A DOI may be written bare (10.1234/x) or as a resolver URL. Strip a known
    # resolver prefix so a single correct link gets built, never a doubled one.
    doi = doi.strip()
    lowered = doi.lower()
    for prefix in _DOI_RESOLVER_PREFIXES:
        if lowered.startswith(prefix):
            return doi[len(prefix) :]
    return doi


def _tex_token(latex: str, i: int) -> int:
    """The index just past the TeX token that starts at i: a control word
    (\\name), a control symbol (\\ and one character) or one character."""
    if latex[i] != "\\" or i + 1 == len(latex):
        return i + 1
    j = i + 1
    while j < len(latex) and latex[j].isalpha():
        j += 1
    return j if j > i + 1 else i + 2


def _tex_argument(latex: str, i: int) -> tuple[str, int] | None:
    """The undelimited TeX argument at i, read as TeX reads it: spaces are
    skipped, then a braced group (without its braces) or one token. None when
    the argument is missing or its braces do not close."""
    while i < len(latex) and latex[i].isspace():
        i += 1
    if i == len(latex) or latex[i] == "}":
        return None
    if latex[i] != "{":
        j = _tex_token(latex, i)
        return latex[i:j], j
    depth, j = 0, i
    while j < len(latex):
        if latex[j] == "\\":
            j = _tex_token(latex, j)
            continue
        if latex[j] == "{":
            depth += 1
        elif latex[j] == "}":
            depth -= 1
            if depth == 0:
                return latex[i + 1 : j], j + 1
        j += 1
    return None


# A default that calls itself would expand forever; MathJax stops with an error,
# and here the call is left as written.
_NOTATION_MAX_DEPTH = 32


def expand_notation(latex: str, macros: dict[str, str], _depth: int = 0) -> str:
    """Replace each call to a notation macro in latex with the macro's default,
    filling #1..#9 from the call's arguments, and expand the result again."""
    if _depth > _NOTATION_MAX_DEPTH:
        return latex
    out, i = [], 0
    while i < len(latex):
        j = _tex_token(latex, i)
        name = latex[i:j]
        body = macros.get(name)
        if body is None:
            out.append(name)
            i = j
            continue
        params = re.findall(r"#([1-9])", body)
        args = []
        for _ in range(max(map(int, params), default=0)):
            arg = _tex_argument(latex, j)
            if arg is None:
                break
            args.append(arg[0])
            j = arg[1]
        else:

            def _arg(m: re.Match[str], args: list[str] = args) -> str:
                return args[int(m.group(1)) - 1]

            body = re.sub(r"#([1-9])", _arg, body)
            out.append(expand_notation(body, macros, _depth + 1))
            i = j
            continue
        out.append(name)
        i += len(name)
    return "".join(out)


def _make_tag(
    tag: str,
    id_: str | None,
    classes: Iterable,
    is_selectable: bool = False,
    nodeid: int | None = None,
    **kwargs: Any,
) -> str:
    text = f"<{tag}"
    if id_:
        text += f' id="{id_}"'
    if classes:
        classes = " ".join(classes)
        text += f' class="{classes}"'
    tabindex = 0 if is_selectable else None
    items = []
    if kwargs or tabindex is not None:
        if kwargs:
            for k, v in kwargs.items():
                if v is True:
                    items += [k]  # Boolean attribute without value
                elif v:
                    items += [f'{k}="{v}"']  # Regular attribute with value
        if tabindex is not None:
            items += [f"tabindex={tabindex}"]
    if nodeid is not None:
        items += [f'data-nodeid="{nodeid}"']
    if items:
        text += " "
    text += " ".join(items)
    text += ">"
    return text


# Browsers may break a line right after a hyphen, so each hyphenated word goes
# in a span that braiid.css styles with white-space: nowrap (rsm-69h). A span,
# not a word joiner or a non-breaking hyphen, because copying the page then
# gives the plain source text.
_HYPHENATED_OPEN = '<span class="hyphenated">'
_HYPHENATED_CLOSE = "</span>"

# The keyboard hyphen, the Unicode hyphen and the en dash. Not the minus sign.
_HYPHEN = re.compile("[-\u2010\u2013]")

# Inline nodes that are part of a word when they touch it, as $K$ is in
# $K$-theory.
_WORD_PIECES = (
    nodes.Math,
    nodes.Span,
    nodes.Code,
    nodes.BaseReference,
    nodes.Cite,
    nodes.NoteCall,
    nodes.RawHtml,
)

# Text under these nodes is not prose: math source, code, preformatted text and
# notation data.
_NOT_PROSE = (
    nodes.Math,
    nodes.MathBlock,
    nodes.Code,
    nodes.CodeBlock,
    nodes.Algorithm,
    nodes.Notation,
)


def _wrap_hyphenated_words(html: str) -> str:
    """Wrap each hyphenated word of *html* in a no-wrap span. Tags are left
    alone, and a word ends at a tag."""
    return re.sub(
        r"<[^>]*>|[^\s<]+",
        lambda m: f"{_HYPHENATED_OPEN}{m.group()}{_HYPHENATED_CLOSE}"
        if _HYPHEN.search(m.group()) and not m.group().startswith("<")
        else m.group(),
        html,
    )


def unwrap_hyphenated_words(html: str) -> str:
    """Remove the spans that wrap hyphenated words."""
    out, pos = [], 0
    stack: list[bool] = []
    for m in re.finditer(r"<span\b[^>]*>|</span>", html):
        if m.group() == _HYPHENATED_CLOSE:
            # Raw HTML may close a span that it did not open.
            drop = stack.pop() if stack else False
        else:
            drop = m.group() == _HYPHENATED_OPEN
            stack.append(drop)
        if drop:
            out.append(html[pos : m.start()])
            pos = m.end()
    out.append(html[pos:])
    return "".join(out)


def _visible_text(html: str) -> str:
    return html_unescape(re.sub(r"<[^>]*>", "", html))


def _shown_prose(node: nodes.Node, html: str) -> tuple[str, bool]:
    """The text that *node* shows, written as *html*, and whether a hyphen in
    it is prose. Math and code inside it count as one letter each, so that
    their source neither adds spaces nor hyphens."""
    if isinstance(node, nodes.RawHtml):
        return _visible_text(node.html), False
    if isinstance(node, (nodes.Math, nodes.Code)):
        return "x", False
    html = re.sub(r'<span class="math"[^>]*>[^<]*</span>', "x", html)
    html = re.sub(r"<code\b[^>]*>.*?</code>", "x", html, flags=re.S)
    bare_url = isinstance(node, nodes.URL) and not (
        getattr(node, "reftext_nodes", None) or node.overwrite_reftext
    )
    return _visible_text(html), not bare_url


def _section_anchor_id(section: "nodes.Section") -> str:
    """The id the table of contents and deep links use to reach a section.

    A labelled section keeps its label. An unlabelled section still needs a
    stable anchor so the table of contents can link to it: a numbered section
    uses its section number, and an unnumbered one (:nonum:) falls back to its
    build-time node id. Without this fallback such a section has no anchor and
    its TOC entry links to "#", which goes nowhere.
    """
    if section.label:
        return section.label
    if section.full_number:
        return f"sec-{section.full_number}"
    if section.nodeid is not None:
        return f"sec-n{section.nodeid}"
    return ""


def _step_anchor_id(step: "nodes.Step") -> str:
    """Return the id of a proof step, for the step itself and for :prev: links to it.

    A :prev: can point at a step that has no label, so an unlabelled step gets
    "n" plus its node id in all output, with or without handrails. Handrails
    give other unlabelled blocks the same kind of id.
    """
    if step.label:
        return step.label
    if step.nodeid is not None:
        return f"n{step.nodeid}"
    return ""


# FOR DOCUMENTATION: Classes that inherit from EditCommand are meant to encapsulate
# _reusable_ operations that convert a node into HTML text.  If an operation is not
# reusable on multiple node classes and is particular to just one node class, it should
# go into the visit_* method corresponding to that class.
class EditCommand(ABC):
    defers = False

    @abstractmethod
    def make_text(self) -> Any:
        pass

    @abstractmethod
    def execute(self, translator: "Translator") -> None:
        pass

    def _edit_command_repr(self, members: Iterable[str]) -> str:
        start = f"{self.__class__.__name__}("
        middles = []
        for key in members:
            s = f"{key}="
            value = getattr(self, key, None)
            if isinstance(value, str):
                value = repr(textwrap.shorten(value.strip(), 60))
            s += f"{value}"
            middles.append(s)
        middle = ", ".join(middles)
        end = ")"
        return start + middle + end

    def __repr__(self) -> str:
        return self._edit_command_repr([])


class AppendTextAndDefer(EditCommand):
    defers = True

    def __init__(self, text: str = "", deferred_text: str = ""):
        self._text = text
        self._deferred_text = deferred_text

    def __repr__(self) -> str:
        return self._edit_command_repr(["text", "deferred_text"])

    def execute(self, translator: "Translator") -> None:
        translator.body += self.make_text()
        translator.deferred.append(AppendText(self.make_deferred_text()))

    def make_text(self) -> str:
        return self._text

    def make_deferred_text(self) -> str:
        return self._deferred_text


class AppendText(EditCommand):
    def __init__(self, text: str = ""):
        self._text = text

    def __repr__(self) -> str:
        return self._edit_command_repr(["_text"])

    def execute(self, translator: "Translator") -> None:
        translator.body += self.make_text()

    def make_text(self) -> str:
        return self._text


class AppendOpenCloseTag(AppendText):
    def __init__(
        self,
        tag: str = "div",
        content: str = "",
        *,
        id: str = "",
        classes: list | None = None,
        newline_inner: bool = True,
        newline_outer: bool = True,
        is_selectable: bool = False,
        **kwargs: Any,
    ):
        self.tag = tag
        self.content = content
        self.id = id
        self.classes = classes if classes else []
        self.newline_inner = newline_inner
        self.newline_outer = newline_outer
        self.is_selectable = is_selectable
        self.custom_attrs = kwargs
        super().__init__()

    def make_text(self) -> str:
        outer = "\n" if self.newline_outer else ""
        inner = "\n" if self.newline_inner else ""
        tag = _make_tag(
            self.tag, self.id, self.classes, self.is_selectable, **self.custom_attrs
        )
        return outer + tag + inner + self.content + inner + f"</{self.tag}>" + outer

    def __repr__(self) -> str:
        return self._edit_command_repr(["tag", "content", "id", "classes"])


class AppendOpenTagManualClose(AppendText):
    def __init__(
        self,
        tag: str = "div",
        content: str = "",
        *,
        id: str = "",
        classes: list | None = None,
        newline_inner: bool = True,
        newline_outer: bool = True,
        is_selectable: bool = False,
        **kwargs: Any,
    ):
        self.tag = tag
        self.content = content
        self.id = id
        self.classes = classes if classes else []
        self.newline_inner = newline_inner
        self.newline_outer = newline_outer
        self.is_selectable = is_selectable
        self.custom_attrs = kwargs
        super().__init__()

    def make_text(self) -> str:
        outer = "\n" if self.newline_outer else ""
        inner = "\n" if self.newline_inner else ""
        tag = _make_tag(
            self.tag, self.id, self.classes, self.is_selectable, **self.custom_attrs
        )
        return outer + tag + inner + self.content

    def __repr__(self) -> str:
        return self._edit_command_repr(["tag", "content", "id", "classes"])

    def close_command(self) -> AppendText:
        return AppendText(
            ("\n" if self.newline_inner else "")
            + f"</{self.tag}>"
            + ("\n" if self.newline_outer else "")
        )


class AppendOpenTag(AppendTextAndDefer):
    def __init__(
        self,
        tag: str = "div",
        *,
        id: str = "",
        classes: list | None = None,
        newline_inner: bool = True,
        newline_outer: bool = True,
        is_selectable: bool = False,
        **kwargs: Any,
    ):
        self.tag = tag
        self.id = id
        self.classes = classes if classes else []
        self.newline_inner = newline_inner
        self.newline_outer = newline_outer
        self.is_selectable = is_selectable
        self.custom_attrs = kwargs
        super().__init__()

    def make_text(self) -> str:
        outer = "\n" if self.newline_outer else ""
        inner = "\n" if self.newline_inner else ""
        tag = _make_tag(
            self.tag, self.id, self.classes, self.is_selectable, **self.custom_attrs
        )
        return outer + tag + inner

    def make_deferred_text(self) -> str:
        return (
            ("\n" if self.newline_inner else "")
            + f"</{self.tag}>"
            + ("\n" if self.newline_outer else "")
        )

    def __repr__(self) -> str:
        return self._edit_command_repr(["tag", "id", "classes", "newline_inner"])


def _caption_name(parent: nodes.Node) -> str:
    """The name in a caption's label, "Figure 1". A block with no number (:nonum:, or
    numbering turned off) keeps the name without the number, "Figure", not "Figure None"."""
    return parent.classreftext.format(
        nodeclass=parent.kindname, number=parent.full_number or ""
    ).strip()


def _caption_label(parent: nodes.Node, translator: "Translator") -> AppendOpenCloseTag:
    """A caption's label, "Figure 1. "."""
    markup = parent.kindname_markup(parent.classreftext)
    if markup:
        name = translator._render_inline_nodes(markup)
    else:
        name = html_escape(_caption_name(parent), quote=False)
    return AppendOpenCloseTag(
        tag="span",
        content=f"{name}. ",
        classes=["label"],
        newline_inner=False,
        newline_outer=False,
    )


def _has_caption(node: nodes.Node) -> bool:
    return any(isinstance(c, nodes.Caption) for c in getattr(node, "children", ()))


def _figure_number(node: nodes.Node) -> str | None:
    """The number of a :figure:, :html: or :video: block, or None when it has none."""
    if not isinstance(node, nodes.Asset):
        return None
    if node.nonum or not getattr(node, "number", None):
        return None
    return node.full_number


def _asset_classes(node: nodes.Asset) -> list[str]:
    """Extra classes of an asset's <figure>. braiid.css caps the content of an
    :as-paragraph: asset at the width of the column by this class. A figure that
    shows HTML is marked "html": reference previews swap it for its still image
    or its alt text (tooltips.js), as a copy of live HTML would be a second live
    copy."""
    classes = ["as-paragraph"] if node.as_paragraph else []
    if isinstance(node, nodes.Figure) and node.holds_html:
        classes.append("html")
    return classes


def _wraps_block(node: nodes.Node | None) -> bool:
    """Whether node is a paragraph that the transformer made to hold a math block,
    code block or algorithm that stands on its own. The page has no tag for it."""
    return isinstance(node, nodes.Paragraph) and node.wraps_block


def _in_paragraph_asset(node: nodes.Node) -> bool:
    """Whether node is the body of an :as-paragraph: asset, which sits inside
    the asset's own paragraph handrail and so gets none."""
    return isinstance(node.parent, nodes.Asset) and node.parent.as_paragraph


class AppendNodeTag(AppendOpenTag):
    def __init__(
        self,
        node: nodes.Node,
        tag: str = "div",
        *,
        additional_classes: list[str] | None = None,
        newline_inner: bool = True,
        newline_outer: bool = True,
        is_selectable: bool = False,
        include_source: bool = False,
        manuscript_source: str = "",
        extra_attrs: dict | None = None,
    ):
        self.node = node
        classes = [node.__class__.__name__.lower()] + [str(t) for t in node.classes]
        classes = list(dict.fromkeys(classes + (additional_classes or [])))

        # Extract node source if requested
        kwargs: dict[str, int | str | None] = {"nodeid": node.nodeid}
        if extra_attrs:
            kwargs.update(extra_attrs)
        if isinstance(node, nodes.Asset) and node.static:
            static_src = (
                self._resolve_image_src(node.static)
                if hasattr(self, "_resolve_image_src")
                else str(node.static)
            )
            kwargs["data-static"] = static_src
        elif isinstance(node, nodes.Figure) and node.holds_html and node.alt:
            # Without a still image the alt text appears nowhere else in the
            # page, and a reference preview of the figure shows it instead.
            kwargs["data-alt"] = html_escape(node.alt, quote=True)
        # Figures and videos carry their number, so the minimap can
        # label one that has no caption (and so no visible "Figure 4.3" label).
        figure_number = _figure_number(node)
        if figure_number:
            kwargs["data-number"] = figure_number
        # tree-sitter 0.26.0's Point.row/.column getters over-decref the returned
        # int and corrupt memory (py-tree-sitter #472); read row/column by index
        # instead. A default (-1, -1) point means no source position, so skip it.
        if include_source and manuscript_source and node.start_point[0] >= 0:
            source_lines = manuscript_source.split("\n")
            start_row, start_col = node.start_point[0], node.start_point[1]
            end_row, end_col = node.end_point[0], node.end_point[1]

            if start_row < len(source_lines) and end_row < len(source_lines):
                # Compute character offsets into the full source string
                start_offset = (
                    sum(len(source_lines[r]) + 1 for r in range(start_row)) + start_col
                )
                end_offset = (
                    sum(len(source_lines[r]) + 1 for r in range(end_row)) + end_col
                )
                kwargs["data-source-start"] = str(start_offset)
                kwargs["data-source-end"] = str(end_offset)

        id_ = node.label
        if not id_ and isinstance(node, nodes.Section):
            id_ = _section_anchor_id(node)
        if not id_ and isinstance(node, nodes.Step):
            id_ = _step_anchor_id(node)
        if not id_ and node.nodeid is not None and "hr" in classes:
            # Synthetic id so every HANDRAIL BLOCK is hash-addressable: the rail
            # and keyboard jumps navigate by location.hash and ride the native
            # browser Back button. Scoped to handrail blocks (the jump targets)
            # via the "hr" class, so inline spans (Span/Math/Code, which are not
            # jump targets) don't get ids. Stable within a built artifact;
            # labeled blocks keep the semantic id set above.
            id_ = f"n{node.nodeid}"

        super().__init__(
            tag=tag,
            id=id_,
            classes=classes,
            newline_inner=newline_inner,
            newline_outer=newline_outer,
            is_selectable=is_selectable,
            **kwargs,
        )

    def __repr__(self) -> str:
        return self._edit_command_repr(["tag", "node"])


class AppendParagraph(AppendOpenCloseTag):
    def __init__(
        self,
        content: str = "",
        *,
        id: str = "",
        classes: list | None = None,
        newline_inner: bool = False,
        newline_outer: bool = True,
    ):
        super().__init__(
            tag="p",
            content=content,
            id=id,
            classes=classes,
            newline_inner=newline_inner,
            newline_outer=newline_outer,
        )

    def __repr__(self) -> str:
        return self._edit_command_repr(["content", "id", "classes"])


class AppendHeading(AppendOpenCloseTag):
    def __init__(
        self,
        level: int,
        content: str = "",
        *,
        id: str = "",
        classes: list | None = None,
        newline_inner: bool = False,
        newline_outer: bool = True,
    ):
        self.level = level
        super().__init__(
            tag=f"h{self.level}",
            content=content,
            id=id,
            classes=classes,
            newline_inner=newline_inner,
            newline_outer=newline_outer,
        )

    def __repr__(self) -> str:
        return self._edit_command_repr(["level", "content", "id", "classes"])


class AppendKeyword(AppendOpenCloseTag):
    def __init__(
        self,
        keyword: str,
        *,
        id: str = "",
        classes: list | None = None,
        newline_inner: bool = False,
        newline_outer: bool = False,
    ):
        classes = ["keyword"] + (classes or [])
        super().__init__(
            tag="span",
            content=keyword,
            id=id,
            classes=classes,
            newline_inner=newline_inner,
            newline_outer=newline_outer,
        )

    def __repr__(self) -> str:
        return self._edit_command_repr(["level", "content", "id", "classes"])


class AppendHalmos(AppendOpenCloseTag):
    def __init__(
        self,
        *,
        id: str = "",
        classes: list | None = None,
    ):
        super().__init__(
            tag="div",
            content="",
            id=id,
            classes=["halmos"] + (classes or []),
            newline_inner=False,
            newline_outer=True,
        )

    def __repr__(self) -> str:
        return self._edit_command_repr(["classes"])


class AppendExternalTree(AppendText):
    """Translate a node that is not in the tree, such as a block's title."""

    def __init__(self, root: nodes.Node, translator: "Translator"):
        super().__init__()
        self.root = root
        self.translator = translator

    def make_text(self) -> str:
        # The new translator reads the document's notation and settings (such
        # as the citation style) from the tree that the main one translates.
        other = Translator(quiet=True)
        other.tree = self.translator.tree
        other._notation = self.translator._notation
        return other._walk(self.root)


class EditCommandBatch(EditCommand):
    def __init__(self, items: Iterable):
        self.items = list(items)

    def __len__(self) -> int:
        return len(self.items)

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f"{classname}({repr(self.items)})"

    def make_text(self) -> str:
        raise RSMTranslatorError("Why are we here?")


_BatchT = TypeVar("_BatchT", bound=EditCommandBatch)


class AppendBatchAndDefer(EditCommandBatch):
    defers = True

    def execute(self, translator: "Translator") -> None:
        deferred: list[EditCommand] = []
        for item in self.items:
            if isinstance(item, AppendTextAndDefer):
                deferred.append(AppendText(item.make_deferred_text()))
            AppendText(item.make_text()).execute(translator)

        batch = AppendBatch(reversed(deferred))
        translator.deferred.append(batch)


class AppendBatch(EditCommandBatch):
    def execute(self, translator: "Translator") -> None:
        for item in self.items:
            item.execute(translator)


_TranslatorT = TypeVar("_TranslatorT", bound="Translator")
_NodeT = TypeVar("_NodeT", bound=nodes.Node)


def auto_leave_deferred(
    leave_method: Callable[[_TranslatorT, _NodeT, "EditCommandBatch"], EditCommand],
) -> Callable[[_TranslatorT, _NodeT], EditCommand]:
    """
    Decorator for leave_* methods whose corresponding visit_* method returns
    a command with defers=True (like AppendBatchAndDefer).

    Automatically calls leave_node(node) to get the base batch, then passes
    it to the decorated method for node-specific modifications.

    MUST be used if the corresponding visit_* method returns AppendBatchAndDefer
    or any other command with defers=True.

    The decorated method will receive (self, node, base_batch) and should
    modify and return the base_batch.
    """

    def wrapper(self: _TranslatorT, node: _NodeT) -> EditCommand:
        # Get the base leave_node batch (handles deferred cleanup). The visit
        # method returned a batch that defers, so the deferred command is the
        # AppendBatch made by AppendBatchAndDefer.execute.
        base_batch = cast(EditCommandBatch, self.leave_node(node))

        # Call the decorated method with the base batch for modification
        return leave_method(self, node, base_batch)

    return wrapper


class Translator:
    """Translate an abstract syntax tree into HTML.

    Examples
    --------
    This is an example doctest.

    >>> [1, 2, 3]
    [1, 2, 3]

    """

    _TRAILING_PUNCT = set(".,;:!?)]}\"'")
    _OPENING_BRACKETS = set("([{")

    class Action(namedtuple("Action", "node action method")):
        def __repr__(self) -> str:
            classname = self.node.__class__.__name__
            return f'Action(node={classname}(), action="{self.action}")'

    def __init__(
        self,
        quiet: bool = False,
        asset_resolver: AssetResolver | None = None,
        standalone: bool = False,
        source_offsets: bool = False,
        copy_source: bool = False,
    ) -> None:
        self.tree: nodes.Manuscript | None = None
        self.body: str = ""
        self.standalone = standalone
        self.source_offsets = source_offsets
        self.copy_source = copy_source
        # Default to disk-based asset resolver if none provided
        if asset_resolver is None:
            from .asset_resolver import AssetResolverFromDisk

            asset_resolver = AssetResolverFromDisk()
        self.asset_resolver = asset_resolver
        self.deferred: list[EditCommand] = []
        self.quiet = quiet

    def _node_tag(
        self, node: nodes.Node, tag: str = "div", **kwargs: Any
    ) -> AppendNodeTag:
        """Create an AppendNodeTag with source offsets if source_offsets is enabled."""
        return AppendNodeTag(
            node,
            tag,
            include_source=self.source_offsets,
            manuscript_source=getattr(self.tree, "src", "") or "",
            **kwargs,
        )

    @staticmethod
    def _icon_ref(name: str) -> str:
        """Emit an SVG <use> reference to a symbol in the defs block."""
        return f'<div class="icon {name}"><svg overflow="visible"><use href="#hr-icon-{name}" width="100%" height="100%"/></svg></div>'

    def _inline_icon(self, name: str) -> str:
        """An icon inside a line of text, where a div is not allowed."""
        return f'<span class="icon {name}" aria-hidden="true"><svg overflow="visible"><use href="#hr-icon-{name}" width="100%" height="100%"/></svg></span>'

    @classmethod
    def get_action_method(cls, node: nodes.Node, action: str) -> Callable:
        nodeclass = node.__class__
        method = f"{action}_{nodeclass.__name__.lower()}"
        while not hasattr(cls, method):
            nodeclass = nodeclass.__bases__[0]
            method = f"{action}_{nodeclass.__name__.lower()}"
        # if action == "visit" and ogclass is not nodeclass:
        #     logger.debug(f"Using {method} for node of class {ogclass}")
        action_method: Callable = getattr(cls, method)
        return action_method

    # Set by FullBuildApp: a built page loads behind a spinner (rsm-hc8).
    loading_spinner = False

    def _spinner_after(self, tree: nodes.Manuscript) -> nodes.Node:
        """The node that the loading spinner follows: the last author block or
        abstract before the first section, or else the manuscript itself, whose
        visit writes the title."""
        after: nodes.Node = tree
        for child in tree.children:
            if isinstance(child, nodes.Section):
                break
            if isinstance(child, (nodes.AuthorBlock, nodes.Abstract)):
                after = child
        return after

    def push_visit(self, stack: list["Translator.Action"], node: nodes.Node) -> None:
        stack.append(self.Action(node, "visit", self.get_action_method(node, "visit")))

    def push_leave(self, stack: list["Translator.Action"], node: nodes.Node) -> None:
        stack.append(self.Action(node, "leave", self.get_action_method(node, "leave")))

    def push_children(
        self, stack: list["Translator.Action"], children: list[nodes.Node]
    ) -> None:
        """Push the visits of *children*, and after them the step that wraps
        their hyphenated words."""
        if any(type(c) is nodes.Text for c in children):
            stack.append(
                self.Action(children, "words", Translator._wrap_hyphenated_words_of)
            )
        for child in reversed(children):
            self.push_visit(stack, child)

    def _wrap_hyphenated_words_of(self, children: list[nodes.Node]) -> EditCommand:
        """Wrap each hyphenated word among *children*, which are already written.

        A word may run over several children ($K$-theory is a math node and then
        text), so this works on the HTML that the children wrote, which starts
        at the _body_start of the first one and runs to the end of the body.
        """
        up = children[0].parent
        while up is not None:
            if isinstance(up, _NOT_PROSE):
                return AppendText("")
            up = up.parent

        starts = [c._body_start for c in children] + [len(self.body)]
        words: list[tuple[int, int]] = []
        # The word being read: where it starts and ends, whether a hyphen in
        # it counts so far, and whether it must be wrapped already. A piece
        # whose shown text has a space is wrapped whole when a hyphenated
        # word touches it, so nothing inside it breaks either. Its last word
        # counts only if text after the piece touches it.
        word: list[int] = []
        hyphen = must_wrap = after_spaced = False

        def end_word() -> None:
            nonlocal hyphen, must_wrap, after_spaced
            if word and (must_wrap or (hyphen and not after_spaced)):
                words.append((word[0], word[1]))
            word.clear()
            hyphen = must_wrap = after_spaced = False

        def add(start: int, end: int, has_hyphen: bool) -> None:
            nonlocal hyphen, must_wrap, after_spaced
            if after_spaced:
                must_wrap = must_wrap or hyphen
            word[:] = [word[0] if word else start, end]
            hyphen = hyphen or has_hyphen
            after_spaced = False

        def add_spaced(start: int, end: int, shown: str, prose: bool) -> None:
            nonlocal hyphen, must_wrap, after_spaced
            if shown[0].isspace():
                end_word()
            parts = shown.split()
            first = prose and bool(parts) and bool(_HYPHEN.search(parts[0]))
            last = prose and bool(parts) and bool(_HYPHEN.search(parts[-1]))
            if word:
                must_wrap = must_wrap or hyphen or first
            word[:] = [word[0] if word else start, end]
            hyphen, after_spaced = last, True
            if shown[-1].isspace():
                end_word()

        for child, start, end in zip(children, starts, starts[1:], strict=False):
            html = self.body[start:end]
            if type(child) is nodes.Text:
                for m in re.finditer(r"\s+|\S+", html):
                    if m.group()[0].isspace():
                        end_word()
                    else:
                        add(
                            start + m.start(),
                            start + m.end(),
                            bool(_HYPHEN.search(m.group())),
                        )
            elif isinstance(child, _WORD_PIECES):
                shown, prose = _shown_prose(child, html)
                if re.search(r"\s", shown):
                    add_spaced(start, end, shown, prose)
                else:
                    add(start, end, prose and bool(_HYPHEN.search(shown)))
            else:
                end_word()
        end_word()

        if words:
            out, pos = [], starts[0]
            for start, end in words:
                out += [
                    self.body[pos:start],
                    _HYPHENATED_OPEN,
                    unwrap_hyphenated_words(self.body[start:end]),
                    _HYPHENATED_CLOSE,
                ]
                pos = end
            out.append(self.body[pos:])
            self.body = self.body[: starts[0]] + "".join(out)
        return AppendText("")

    def translate(self, tree: nodes.Manuscript, new: bool = True) -> str:
        if not self.quiet:
            logger.info("Translating...")
        if new:
            self.body = ""
        self.tree = tree
        self._notation = {
            e["macro"]: e["default"]
            for n in tree.traverse(nodeclass=nodes.Notation)
            for e in n.entries
        }
        spinner_after = self._spinner_after(tree) if self.loading_spinner else None
        return self._walk(tree, spinner_after)

    def _walk(self, root: nodes.Node, spinner_after: nodes.Node | None = None) -> str:
        if self.deferred:
            raise RSMTranslatorError("Something went wrong")

        spinner_action = "visit" if spinner_after is root else "leave"
        stack: list[Translator.Action] = []
        self.push_visit(stack, root)
        while stack:
            node, action, method = stack.pop()
            command = method(self, node)
            if action == "visit":
                node._body_start = len(self.body)
                if command.defers:
                    self.push_leave(stack, node)
                self.push_children(stack, node.children)
            command.execute(self)
            if node is spinner_after and action == spinner_action:
                self.body += (
                    '\n<div class="rsm-loading-spinner" aria-hidden="true"></div>\n'
                )

        if self.deferred:
            raise RSMTranslatorError("Something went wrong")

        return self.body

    def visit_node(self, node: nodes.Node) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendOpenTag(classes=["node-with-no-class"]),
                AppendText(str(node) + "\n"),
            ]
        )

    def leave_node(self, node: nodes.Node) -> EditCommand:
        try:
            return self.deferred.pop()
        except IndexError as ex:
            raise RSMTranslatorError(
                "Cannot finish translation; did you forget to write "
                "a visit_* or leave_* method?"
            ) from ex

    @staticmethod
    def _terminal_block_in_p(node: nodes.TerminalBlock) -> bool:
        """Whether a terminal block sits in a <p> opened by its parent.

        Paragraphs and note and aside definitions open a <p>. Captions and list
        items are paragraphs in the tree but open no <p> of their own.
        """
        return (
            isinstance(node.parent, (nodes.Paragraph, nodes.Note))
            and not isinstance(node.parent, nodes.Caption)
            and not _wraps_block(node.parent)
        )

    def _close_p_before(self, node: nodes.TerminalBlock) -> list[EditCommand]:
        """Commands that close the parent's <p> before a terminal block.

        A paragraph never starts with a terminal block, so text always comes
        before it and the <p> is open. See visit_paragraph().
        """
        if not self._terminal_block_in_p(node) or self._starts_paragraph(node):
            return []
        return [AppendText("</p>")]

    @staticmethod
    def _starts_paragraph(node: nodes.Node) -> bool:
        """Whether a list is the first thing in its paragraph, which then opens no
        <p> before it. A list after a blank line is a paragraph of its own."""
        parent = node.parent
        return (
            isinstance(node, (nodes.Itemize, nodes.Enumerate))
            and isinstance(parent, nodes.Paragraph)
            and not parent.title
            and bool(parent.children)
            and parent.children[0] is node
        )

    @overload
    def _reopen_p_after(
        self, node: nodes.TerminalBlock, closing: EditCommandBatch
    ) -> EditCommandBatch: ...

    @overload
    def _reopen_p_after(
        self, node: nodes.TerminalBlock, closing: EditCommand
    ) -> EditCommand: ...

    def _reopen_p_after(
        self, node: nodes.TerminalBlock, closing: EditCommand
    ) -> EditCommand:
        """Open a new <p> after a terminal block when more of the paragraph follows.

        ``closing`` holds the block's own closing commands. Asides moved to the end
        of the paragraph do not count as more content: they go after it. The new
        <p> is closed when the parent is left (leave_paragraph, leave_note).
        """
        if not self._terminal_block_in_p(node):
            return closing
        nxt = node.next_sibling()
        if not nxt or isinstance(nxt, nodes.Aside):
            return closing
        # _terminal_block_in_p checked that the parent is a Paragraph or Note.
        assert node.parent is not None
        node.parent._must_close_p_tag = True
        items = closing.items if isinstance(closing, EditCommandBatch) else [closing]
        return AppendBatch([*items, AppendText("<p>")])

    def visit_manuscript(self, node: nodes.Manuscript) -> AppendBatchAndDefer:
        accent = getattr(node, "accent", "blue")
        lang = getattr(node, "lang", "en")
        typography = getattr(node, "typography", "sans-serif")
        body_attrs: dict[str, Any] = {
            "data-accent": accent,
            "data-lang": lang,
            "data-typography": typography,
        }
        if not minimap_enabled(node):
            body_attrs["data-minimap"] = "false"
        batch = AppendBatchAndDefer(
            [
                AppendOpenTag("body", **body_attrs),
                AppendOpenTag("main", classes=["manuscriptwrapper"]),
                AppendNodeTag(node),
                AppendOpenTag("section", classes=["level-1"]),
            ]
        )
        if node.eyebrow:
            batch.items.append(
                AppendParagraph(
                    self._meta_html(node.eyebrow, node.eyebrow_nodes),
                    classes=["manuscript-eyebrow"],
                )
            )

        if node.title:
            batch.items.append(AppendHeading(1, self._title_html(node)))

        if node.date:
            from datetime import datetime

            if isinstance(node.date, str):
                for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y"]:
                    try:
                        date_obj = datetime.strptime(node.date, fmt)
                        date_str = date_obj.strftime("%B %d, %Y")
                        break
                    except ValueError:
                        continue
                else:
                    date_str = node.date
            else:
                date_str = node.date.strftime("%B %d, %Y")
            batch.items.append(
                AppendParagraph(
                    _wrap_hyphenated_words(date_str), classes=["manuscript-date"]
                )
            )

        return batch

    def leave_manuscript(self, node: nodes.Manuscript) -> EditCommand:
        return self.leave_node(node)

    def visit_author(self, node: nodes.Author) -> EditCommand:
        return AppendText("")

    def leave_author(self, node: nodes.Author) -> EditCommand:
        return AppendText("")

    def visit_authorblock(self, node: nodes.AuthorBlock) -> AppendBatchAndDefer:
        authors = [c for c in node.children if isinstance(c, nodes.Author)]
        total_affiliations = getattr(self.tree, "total_unique_affiliations", 0)
        total_notes = getattr(self.tree, "total_unique_notes", 0)

        notes_node = next(
            (c for c in node.children if isinstance(c, nodes.AuthorNotes)), None
        )

        name_parts = []
        for author in authors:
            if not author.name:
                continue
            # tooltips.js copies the name's tooltip from the details that these
            # attributes point at, so that no HTML is read from an attribute.
            tip_attrs = ""
            if author.affiliation and author.affiliation_number is not None:
                tip_attrs += f' data-affiliation="{author.affiliation_number}"'
            if author.author_note and author.note_symbol:
                tip_attrs += f' data-note="{author.note_symbol}"'
            name_html = (
                f'<span class="author-name-text"{tip_attrs}>'
                f"{self._meta_html(author.name, author.name_nodes)}</span>"
            )
            sup_parts = []
            if author.affiliation_number is not None and total_affiliations > 1:
                num = author.affiliation_number
                sup_parts.append(f'<sup data-affiliation="{num}">{num}</sup>')
            if author.note_symbol and total_notes > 1:
                sym = author.note_symbol
                sup_parts.append(f'<sup data-note="{sym}">{sym}</sup>')
            name_html += "".join(sup_parts)
            name_attr = html_escape(author.name, quote=True)
            if author.email:
                email = html_escape(author.email, quote=True)
                name_html += (
                    f'<a class="author-contact" href="mailto:{email}" '
                    f'aria-label="Email {name_attr}" data-tip="Email {name_attr}">'
                    f'{self._inline_icon("mail")}</a>'
                )
            if author.orcid:
                orcid = html_escape(author.orcid, quote=True)
                name_html += (
                    f'<a class="author-contact" href="https://orcid.org/{orcid}" '
                    f'aria-label="ORCID record of {name_attr}" '
                    f'data-tip="ORCID record of {name_attr}">{self._inline_icon("orcid")}</a>'
                )
            name_parts.append(f'<span class="author-name">{name_html}</span>')

        names_line = self._author_names_line(name_parts)

        details = self._make_authornotes_html(notes_node)
        # Whether the block has anything to open: hidden names or details.
        self._author_block_opens = bool(details) or "author-hidden-names" in names_line
        html = f'\n<p class="author-names">{names_line}</p>\n' if names_line else ""
        html += details

        return AppendBatchAndDefer(
            [
                AppendOpenTag("div", classes=["author-block"], newline_inner=False),
                AppendText(html),
            ]
        )

    def leave_authorblock(self, node: nodes.AuthorBlock) -> EditCommand:
        return self.leave_node(node)

    def _author_names_line(self, name_parts: list[str]) -> str:
        """Join the names, wrapping the middle ones when the list is shortened.

        Every name stays in the HTML, so readers without JavaScript and search
        engines get the full list. The "N more" pill sits where the hidden
        names start and the "Show fewer" pill where they end. Both start out
        hidden, and the stylesheet shows one of them once the page script sets
        the block's state.
        """
        first = getattr(self.tree, "author_display_first", 0)
        last = getattr(self.tree, "author_display_last", 0)
        # The parser keeps a rejected value as None.
        if first is None or last is None:
            return ", ".join(name_parts)
        first, last = int(first), int(last)
        if (first == 0 and last == 0) or first + last >= len(name_parts):
            return ", ".join(name_parts)
        hidden = len(name_parts) - first - last
        # Each separator sits in the same span as the name after it, so the
        # commas are right whether the hidden names show or not.
        sep = [", " if i else "" for i in range(len(name_parts))]
        head = "".join(s + n for s, n in zip(sep[:first], name_parts[:first]))
        middle = "".join(
            s + n
            for s, n in zip(sep[first : first + hidden], name_parts[first:])
        )
        tail = "".join(
            s + n
            for s, n in zip(sep[first + hidden :], name_parts[first + hidden :])
        )
        noun = "author" if hidden == 1 else "authors"
        more = (
            f'<button type="button" class="author-more-button" aria-expanded="false" '
            f'aria-label="Show {hidden} more {noun}">{hidden} more</button>'
        )
        fewer = (
            '<button type="button" class="author-more-button" aria-expanded="true" '
            'aria-label="Show fewer authors">Show fewer</button>'
        )
        return (
            f'{head}<span class="author-more" hidden>{sep[first]}{more}</span>'
            f'<span class="author-hidden-names">{middle}'
            f'<span class="author-fewer" hidden> {fewer}</span></span>{tail}'
        )

    def visit_authornotes(self, node: nodes.AuthorNotes) -> EditCommand:
        return AppendText("")

    def leave_authornotes(self, node: nodes.AuthorNotes) -> EditCommand:
        return AppendText("")

    def _make_authornotes_html(self, node: nodes.AuthorNotes | None) -> str:
        if not node:
            return ""
        has_content = (
            node.affiliation_map or node.note_map or node.emails or node.orcids
        )
        if not has_content:
            return ""

        total_affiliations = len(node.affiliation_map)
        total_notes = len(node.note_map)
        # The details list each value once, so they take the markup of the first
        # author who has it.
        siblings = node.parent.children if node.parent else ()
        aff_nodes: dict[str, list[nodes.Node]] = {}
        note_nodes: dict[str, list[nodes.Node]] = {}
        name_nodes: dict[str, list[nodes.Node]] = {}
        for a in siblings:
            if isinstance(a, nodes.Author):
                aff_nodes.setdefault(a.affiliation, a.affiliation_nodes)
                note_nodes.setdefault(a.author_note, a.author_note_nodes)
                name_nodes.setdefault(a.name, a.name_nodes)

        # The summary label counts what the details hold. It starts out hidden,
        # and the stylesheet shows it while the page script has the block closed.
        counts = [
            (len(node.affiliation_map), "affiliation", "affiliations"),
            (len(node.emails), "email", "emails"),
            (len(node.orcids), "ORCID", "ORCIDs"),
            (len(node.note_map), "note", "notes"),
        ]
        label = '<span aria-hidden="true"> · </span>'.join(
            f"{n} {one if n == 1 else many}" for n, one, many in counts if n
        )
        html = (
            '<button type="button" class="author-summary" aria-expanded="false" '
            f"hidden>{label}</button>\n"
        )
        html += '<div class="author-details">\n'

        if node.affiliation_map:
            html += '<ol class="author-affiliations">\n'
            for aff_text, aff_num in node.affiliation_map.items():
                text = self._meta_html(aff_text, aff_nodes.get(aff_text, []))
                if total_affiliations > 1:
                    html += (
                        f'<li value="{aff_num}" data-affiliation="{aff_num}">'
                        f"<sup>{aff_num}</sup>{text}</li>\n"
                    )
                else:
                    html += f'<li data-affiliation="{aff_num}">{text}</li>\n'
            html += "</ol>\n"

        if node.note_map:
            for note_text, note_sym in node.note_map.items():
                text = self._meta_html(note_text, note_nodes.get(note_text, []))
                sup = f"<sup>{note_sym}</sup>" if total_notes > 1 else ""
                html += (
                    f'<p class="author-note" data-note="{note_sym}">{sup}{text}</p>\n'
                )

        if node.emails:
            email_links = ", ".join(
                f'<a href="mailto:{html_escape(email, quote=True)}">'
                f"{html_escape(email, quote=False)}</a>"
                for _, email in node.emails
            )
            html += (
                f'<p class="author-correspondence">Correspondence: {email_links}</p>\n'
            )

        if node.orcids:
            for name, orcid in node.orcids:
                name_html = self._meta_html(name, name_nodes.get(name, []))
                html += (
                    f'<p class="author-orcid">{name_html}: '
                    f"{_wrap_hyphenated_words(html_escape(orcid, quote=False))}</p>\n"
                )

        html += "</div>\n"
        return html

    def visit_abstract(self, node: nodes.Abstract) -> AppendBatchAndDefer:
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node),
                # Level 2, not 3: the abstract is front matter sitting between the
                # h1 title and the first numbered section (also h2), so emitting it
                # at h3 skips a level and trips WCAG 1.3.1 heading-order. Its
                # front-matter look is set in braiid.css, decoupled from the level.
                AppendHeading(2, "Abstract"),
            ]
        )

    def leave_abstract(self, node: nodes.Abstract) -> EditCommand:
        batch = AppendBatch([])

        if node.keywords:
            text = ", ".join(node.keywords)
            batch.items.append(
                AppendParagraph(
                    _wrap_hyphenated_words(f"Keywords: {text}"), classes=["keywords"]
                )
            )
        if node.msc:
            text = ", ".join(node.msc)
            batch.items.append(
                AppendParagraph(_wrap_hyphenated_words(f"MSC: {text}"), classes=["msc"])
            )

        # For documentation: if a visit_* method returns a command with defers = True,
        # then the corresponding leave_* method MUST MUST MUST call leave_node(node) and
        # add it to the returned batch!!!
        batch.items.append(self.leave_node(node))
        return batch

    def visit_paragraph(self, node: nodes.Paragraph) -> AppendBatchAndDefer:
        # There are three kinds of paragraphs, depending on whether the paragraph
        # contains a mathblock, and if so, where it is located.  In the simplest case,
        # the paragraph does not contain a mathblock.  In this case, we simply want to
        # append
        #
        # <div class="paragraph"><p>...paragraph contents...</p></div>
        #
        # In the second case, the paragraph contains a mathblock and this is the last
        # child of the paragraph.  In this case, we want to append
        #
        # <div class="paragraph">
        #   <p>...paragraph contents...</p>
        #   <div class="mathblock">...math contents...</div>
        # </div>
        #
        # In the third case, the mathblock is not the last child of the paragraph, and
        # in this case we need to append
        #
        # <div class="paragraph">
        #   <p>...paragraph contents...</p>
        #   <div class="mathblock">...math contents...</div>
        #   <p>...more paragraph contents...</p>
        # </div>
        #
        # Importantly, all cases start with two opening tags `<div><p>` but only the
        # first case ends with the coresponding closing `</p></div>` tags.  Note the
        # third case finishes in a similar way but the closing </p> tag in that case
        # does not correspond to the tag opened at the start of the paragraph.
        #
        # A paragraph cannot start with a mathblock.
        if node.wraps_block:
            return AppendBatchAndDefer([])
        # A labelled block's title paragraph carries the block's fold label, set
        # by the handrails translator.
        fold_label = getattr(node, "fold_label", "")
        items: list[EditCommand] = [
            AppendNodeTag(
                node,
                "div",
                extra_attrs={"data-fold-label": fold_label} if fold_label else None,
            )
        ]
        # An aside at the end of the paragraph closes the <p> itself, see
        # visit_aside().
        if node.children and self._starts_paragraph(node.children[0]):
            pass
        elif node.first_of_type(nodes.TerminalBlock) or node.first_of_type(nodes.Aside):
            items.append(AppendOpenTagManualClose(tag="p", newline_inner=False))
        else:
            items.append(AppendOpenTag(tag="p", newline_inner=False))

        # Now we're inside the <p> tag in the appropriate way, make sure to add the
        # title, if it exists.
        if node.title:
            items.append(
                AppendOpenCloseTag(
                    tag="span",
                    content=f"{self._title_html(node)}.",
                    classes=["pg-label"],
                )
            )

        return AppendBatchAndDefer(items)

    def visit_step(self, node: nodes.Step) -> EditCommand:
        return AppendNodeTag(node)

    def visit_section(self, node: nodes.Section) -> AppendBatchAndDefer:
        node.classes.insert(0, f"level-{node.level}")
        heading = self._title_html(node)
        if not node.nonum:
            heading = f"{node.full_number}. {heading}"
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, "section"),
                AppendHeading(node.level, heading),
            ]
        )

    def visit_enumerate(self, node: nodes.Enumerate) -> EditCommand:
        return AppendBatchAndDefer(
            [*self._close_p_before(node), AppendNodeTag(node, "ol")]
        )

    def leave_enumerate(self, node: nodes.Enumerate) -> EditCommand:
        return self._reopen_p_after(node, self.leave_node(node))

    def visit_itemize(self, node: nodes.Itemize) -> EditCommand:
        return AppendBatchAndDefer(
            [*self._close_p_before(node), AppendNodeTag(node, "ul")]
        )

    def leave_itemize(self, node: nodes.Itemize) -> EditCommand:
        return self._reopen_p_after(node, self.leave_node(node))

    def visit_item(self, node: nodes.Item) -> EditCommand:
        return AppendNodeTag(node, "li")

    def visit_contents(self, node: nodes.Contents) -> AppendBatchAndDefer:
        toc_classes = ["toc"] + (["tree"] if node.view == "tree" else [])
        return AppendBatchAndDefer(
            [
                # <nav> (not a bare div): the table of contents is a list of
                # section links, the textbook navigation landmark, so screen
                # readers can jump to it. aria-label names the landmark since the
                # rail is a separate (complementary) landmark.
                AppendOpenTag(
                    tag="nav",
                    classes=toc_classes,
                    **{"aria-label": "Table of contents"},  # type: ignore[arg-type]  # these keys go to **kwargs, but mypy checks the values against the named parameters too
                ),
                # Level 2 for the same heading-order reason as the abstract: the
                # table of contents is front matter between the h1 and the first
                # numbered h2. Front-matter styling lives in braiid.css.
                # The heading and the list/graph switch share one row, which
                # is placed by braiid.css. The switch stays outside the h2 so
                # its button names are not read as part of the heading.
                AppendText(
                    text='<div class="toc-head"><h2>Table of Contents</h2>'
                    + _toc_switch(node.view == "tree")
                    + "</div>"
                ),
                AppendOpenTag(classes=["toc-wrapper"]),
                AppendText(text=self._text_toc_tree_svg(node)),
                AppendNodeTag(node, "ul"),
            ]
        )

    def _text_toc_tree_svg(self, node: nodes.Contents) -> str:
        if node.orientation != "horizontal":
            return self._toc_tree_svg(node)
        # A left-to-right graph is too wide for a phone, so the page carries
        # both layouts and braiid.css shows the horizontal one from 768px.
        # Each copy has its own arrowhead ids: a marker found inside the hidden
        # copy would not be drawn.
        vertical = self._toc_tree_svg(
            node, svg_class="toc-tree toc-tree-v", marker_id="toc-v-arr"
        )
        horizontal = self._toc_tree_svg(
            node,
            orient="horizontal",
            svg_class="toc-tree toc-tree-h",
            marker_id="toc-h-arr",
        )
        return vertical + horizontal

    def _toc_tree_svg(
        self,
        node: nodes.Contents,
        orient: str = "vertical",
        svg_class: str = "toc-tree",
        marker_id: str = "toc-arr",
    ) -> str:
        # The TOC graph root stands in for the title/abstract and is drawn as a
        # small muted dot with no label, so the manuscript title no longer sizes
        # or overflows the drawing. The full title stays the dot's accessible name
        # and hover tooltip.
        return self._build_tree_svg(
            node.tree_nodes,
            node.toc_edges,
            node.tree_root_title,
            "Section dependency graph",
            orient=orient,
            svg_class=svg_class,
            marker_id=marker_id,
        )

    def _build_tree_svg(
        self,
        tree_nodes: list[dict],
        ref_edges: list[dict],
        root_title: str,
        aria_label: str,
        orient: str = "vertical",
        bracket_nums: bool = False,
        root_label: str | None = None,
        svg_class: str = "toc-tree",
        marker_id: str = "toc-arr",
    ) -> str:
        """Pre-rendered dependency-graph SVG, shared by the TOC and proof trees.

        Layout is computed here at build time (grandalf), so no layout library
        ships to the browser; the hover/focus JS works on the static SVG. A
        synthetic root node holds `root_title`; every node hangs from its
        outline parent (depth-1 nodes from the root), reconstructed from the
        depth sequence, so the graph is one connected tree with no isolated
        nodes. Containment edges are drawn subtly; reference edges stay
        prominent.
        """
        from html import escape

        from .toc_layout import ROOT_DOT_R, layout_tree

        secs = tree_nodes
        if not secs:
            return '<svg class="toc-tree" aria-hidden="true"></svg>'

        root_idx = len(secs)
        root = {"num": "", "title": root_title, "label": "", "depth": 0}
        struct = []
        for i, sec in enumerate(secs):
            if sec.get("type") == "result":
                continue  # result nodes hang off their dependency edge, not the outline
            if sec["depth"] == 1:
                parent = root_idx
            else:
                parent = root_idx
                for j in range(i - 1, -1, -1):
                    if secs[j]["depth"] < sec["depth"]:
                        parent = j
                        break
            struct.append({"src": i, "dst": parent, "count": 1, "kind": "struct"})

        layout = layout_tree(
            secs + [root], ref_edges + struct, orient, root_label=root_label
        )
        if layout is None:
            return '<svg class="toc-tree" aria-hidden="true"></svg>'
        horizontal = orient == "horizontal"

        pad = 16
        pad_x = 40
        w = layout["width"] + 2 * pad_x
        h = layout["height"] + 2 * pad
        parts = [
            f'<svg class="{svg_class}" width="{w:.0f}" height="{h:.0f}" '
            f'viewBox="{-pad_x} {-pad} {w:.0f} {h:.0f}" role="group" '
            f'aria-label="{escape(aria_label)}">',
            "<defs>"
            f'<marker id="{marker_id}-dep" viewBox="0 0 10 8" refX="8.5" refY="4" '
            'markerWidth="8" markerHeight="6.5" markerUnits="userSpaceOnUse" '
            'orient="auto-start-reverse">'
            '<path d="M0,0 L10,4 L0,8 z" class="toc-arrowhead dep"/></marker>'
            f'<marker id="{marker_id}-fwd" viewBox="0 0 10 8" refX="8.5" refY="4" '
            'markerWidth="8" markerHeight="6.5" markerUnits="userSpaceOnUse" '
            'orient="auto-start-reverse">'
            '<path d="M0,0 L10,4 L0,8 z" class="toc-arrowhead fwd"/></marker>'
            "</defs>",
            '<g class="toc-edges-layer">',
        ]
        for e in layout["edges"]:
            x1, y1, x2, y2 = e["x1"], e["y1"], e["x2"], e["y2"]
            if horizontal:  # curve bends along x so left-to-right edges read cleanly
                mx = (x1 + x2) / 2
                d = f"M {x1:.1f} {y1:.1f} C {mx:.1f} {y1:.1f}, {mx:.1f} {y2:.1f}, {x2:.1f} {y2:.1f}"
            else:
                my = (y1 + y2) / 2
                d = f"M {x1:.1f} {y1:.1f} C {x1:.1f} {my:.1f}, {x2:.1f} {my:.1f}, {x2:.1f} {y2:.1f}"
            if e["kind"] == "struct":
                sw, marker = 1.0, ""
            else:
                sw = 1.1 + e["count"] * 0.7
                marker = f' marker-end="url(#{marker_id}-{e["kind"]})"'
            parts.append(
                f'<path class="toc-edge {e["kind"]}" d="{d}" '
                f'stroke-width="{sw:.1f}" data-from="{e["src"]}" '
                f'data-to="{e["dst"]}"{marker}></path>'
            )
        parts.append('</g><g class="toc-nodes-layer">')
        for n in layout["nodes"]:
            href = f"#{n['label']}" if n["label"] else "#"
            cx = n["x"] + n["w"] / 2
            cy = n["y"] + n["h"] / 2
            full = f"{n['num']}. {n['title']}" if n["num"] else n["title"]
            ncls = "toc-node level-{}".format(n["depth"])
            if n.get("type") == "result":
                ncls += " toc-node-result"
            # aria-label gives the link its full "num. title" accessible name;
            # without it the only name is the visible secnum text ("2."), so a
            # screen reader cannot tell the section links apart. The root's name
            # is the manuscript title.
            open_a = (
                f'<a href="{escape(href)}" class="{ncls}" '
                f'data-idx="{n["idx"]}" data-tooltip="{escape(full)}" '
                f'aria-label="{escape(full)}">'
            )
            if n["depth"] == 0 and not root_label:
                # The TOC root is a small muted dot, not a box with a label. It is
                # drawn at the point where the structural edges meet it (the face
                # of its slot that points into the graph: the bottom when the root
                # leads at the top, the right side when it leads at the left), so
                # the edges touch the dot instead of ending in empty space.
                if horizontal:
                    dx, dy = n["x"] + n["w"], cy
                else:
                    dx, dy = cx, n["y"] + n["h"]
                parts.append(
                    f'{open_a}<circle class="toc-root-dot" cx="{dx:.1f}" '
                    f'cy="{dy:.1f}" r="{ROOT_DOT_R:.0f}"></circle></a>'
                )
                continue
            # The compact horizontal-rail root shows a short "Goal" marker; its
            # full statement is on hover. Other nodes show their number/title.
            if root_label and n["depth"] == 0:
                inner = escape(root_label)
            elif n["num"]:
                # Match the State panel's step markers: ⟨X.Y⟩ for the proof DAG,
                # the bare number for the document TOC.
                inner = f"⟨{escape(n['num'])}⟩" if bracket_nums else escape(n["num"])
            else:
                inner = escape(n["title"])
            parts.append(
                f"{open_a}"
                f'<rect x="{n["x"]:.1f}" y="{n["y"]:.1f}" width="{n["w"]}" '
                f'height="{n["h"]}" rx="6"></rect>'
                f'<text class="toc-secnum" x="{cx:.1f}" y="{cy:.1f}" '
                f'text-anchor="middle" dominant-baseline="central">{inner}</text></a>'
            )
        parts.append("</g>")
        parts.append("</svg>")
        return "".join(parts)

    def visit_notecall(self, node: nodes.NoteCall) -> EditCommand:
        if node.kind == "aside":
            # The phrase itself is the link. The hidden word tells a screen
            # reader that the link is about an aside, since nothing else says so.
            tag = _make_tag(
                "a",
                id_=f"call-{node.target}",
                classes=["aside-phrase"],
                href=f"#{node.target}",
                **{"data-note-kind": "aside"},  # type: ignore[arg-type]  # these keys go to **kwargs, but mypy checks the values against the named parameters too
            )
            return AppendTextAndDefer(
                tag, '<span class="visually-hidden"> (aside)</span></a>'
            )
        tag = _make_tag(
            "a",
            id_=f"call-{node.target}",
            classes=["note-marker"],
            href=f"#{node.target}",
            role="doc-noteref",
            **{"data-note-number": node.number, "data-note-kind": node.kind},  # type: ignore[arg-type]  # these keys go to **kwargs, but mypy checks the values against the named parameters too
        )
        return AppendText(f"{tag}{node.number}</a>")

    def visit_noteslist(self, node: nodes.NotesList) -> AppendBatchAndDefer:
        return AppendBatchAndDefer(
            [
                AppendOpenTag("section", classes=["level-2"]),
                AppendHeading(2, "Notes"),
                AppendNodeTag(node, "ol"),
            ]
        )

    def visit_note(self, node: nodes.Note) -> AppendBatchAndDefer:
        # A footnote is an entry of the notes list and starts with its number. An
        # aside sits below the block that calls it and has no number. Both are a
        # paragraph. The terminal block visitors close and reopen the <p> as they
        # do inside an ordinary paragraph.
        is_aside = isinstance(node, nodes.Aside)
        attrs: dict = {"data-note-kind": node.kind}
        if not is_aside:
            attrs["data-note-number"] = node.number
        in_list = isinstance(node.parent, nodes.NotesList)
        if in_list:
            # The value attribute keeps the numbers right when the list is read
            # without CSS, which hides the list's own numbers.
            attrs["value"] = node.number
        items: list[EditCommand] = [
            AppendNodeTag(node, "li" if in_list else "div", extra_attrs=attrs)
        ]
        if node.first_of_type(nodes.TerminalBlock):
            items.append(AppendOpenTagManualClose(tag="p", newline_inner=False))
        else:
            items.append(AppendOpenTag(tag="p", newline_inner=False))
        if not is_aside:
            items.append(
                AppendText(f'<span class="note__number">{node.number}</span> ')
            )
        return AppendBatchAndDefer(items)

    def visit_aside(self, node: nodes.Aside) -> EditCommand:
        # The transformer moves an aside to the end of the paragraph or list item
        # that calls it. In a paragraph, the first aside closes the paragraph's
        # open <p>, unless a terminal block just before it already did.
        cmd = Translator.visit_note(self, node)
        parent = node.parent
        if not isinstance(parent, nodes.Paragraph):
            return cmd
        prev = node.prev_sibling()
        if isinstance(prev, (nodes.Aside, nodes.TerminalBlock)):
            return cmd
        parent._must_close_p_tag = False
        return AppendBatchAndDefer([AppendText("</p>"), *cmd.items])

    def leave_note(self, node: nodes.Note) -> EditCommand:
        # The visit method deferred a batch, so leave_node returns one.
        batch = cast(EditCommandBatch, self.leave_node(node))
        if getattr(node, "_must_close_p_tag", False):
            batch.items.insert(0, AppendText("</p>"))
        if isinstance(node.parent, nodes.NotesList) and node.call is not None:
            # The bibliography's backlink classes give it the same look and the
            # same preview of the text it points back to.
            backlink = _make_tag(
                "a",
                id_="",
                classes=["reference", "backlink", "note-backlink"],
                href=f"#call-{node.label}",
                role="doc-backlink",
                **{"aria-label": f"Back to the text of note {node.number}"},  # type: ignore[arg-type]  # these keys go to **kwargs, but mypy checks the values against the named parameters too
            )
            batch.items.insert(0, AppendText(f" {backlink}↖</a>"))
        return batch

    def _notation_source(
        self, node: nodes.Math | nodes.MathBlock, prefix: str = ""
    ) -> dict:
        """With JS off the math source is all a reader sees, and notation macro
        names mean nothing to a reader, so the source text gets the macros'
        defaults. notation.js needs the macro calls to rebind them, so the
        original source goes in data-latex, where libraries.js reads it."""
        if not self._notation:
            return {}
        texts = [c for c in node.children if isinstance(c, nodes.Text)]
        src = "".join(t.text for t in texts)
        if expand_notation(src, self._notation) == src:
            return {}
        for t in texts:
            t._nojs_text = expand_notation(t.text, self._notation)
        latex = prefix + src if isinstance(node, nodes.Math) else src.strip()
        return {"data-latex": html_escape(latex, quote=True)}

    def visit_math(self, node: nodes.Math) -> AppendBatchAndDefer:
        # \( ... \) are the standard TeX inline-math delimiters read by the client renderer
        if node.preamble:
            node.classes.append("math-preamble")
        # A calc relation sits on its own row like display math, so it takes
        # display size while staying left-aligned in the row.
        prefix = r"\displaystyle " if self._is_calc_relation(node) else ""
        opening = r"\(" + prefix
        return AppendBatchAndDefer(
            [
                self._node_tag(
                    node,
                    "span",
                    newline_inner=False,
                    newline_outer=False,
                    extra_attrs=self._notation_source(node, prefix),
                ),
                AppendTextAndDefer(opening, r"\)"),
            ]
        )

    def visit_mathblock(self, node: nodes.MathBlock) -> AppendBatchAndDefer:
        commands = self._close_p_before(node)
        if node.preamble:
            node.classes.append("math-preamble")
        commands.append(
            AppendNodeTag(node, "div", extra_attrs=self._notation_source(node))
        )
        commands.append(AppendTextAndDefer("$$\n", "\n$$"))
        return AppendBatchAndDefer(commands)

    def leave_mathblock(self, node: nodes.MathBlock) -> EditCommandBatch:
        # visit_mathblock deferred a batch, so leave_node returns one.
        return self._reopen_p_after(node, cast(EditCommandBatch, self.leave_node(node)))

    def leave_paragraph(self, node: nodes.Paragraph) -> EditCommandBatch:
        # The visit method deferred a batch, so leave_node returns one.
        batch = cast(EditCommandBatch, self.leave_node(node))
        if getattr(node, "_must_close_p_tag", False):
            batch.items.insert(0, AppendText("</p>"))
        return batch

    def visit_sourcecode(self, node: nodes.SourceCode) -> EditCommand:
        classes = []
        if node.lang:
            classes = ["highlight", node.lang]
            code = highlight_code(node.text, node.lang)
        else:
            # highlight_code emits HTML-safe markup; plain code must be escaped
            # here so a < in the source does not open a tag.
            code = (
                node.text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
        return AppendBatchAndDefer(
            [
                AppendOpenTag(
                    "code",
                    classes=classes,
                    newline_outer=False,
                    newline_inner=False,
                ),
                AppendText(code),
            ]
        )

    def visit_code(self, node: nodes.Code) -> EditCommand:
        return self._node_tag(
            node, tag="span", newline_inner=False, newline_outer=False
        )

    def visit_rawhtml(self, node: nodes.RawHtml) -> AppendBatchAndDefer:
        # The fallback (the children) goes first and hidden, and the HTML last,
        # so that HTML that does not close its own tags cannot swallow the
        # fallback. Copies of the page swap the fallback in (rawhtml.js).
        items: list[EditCommand] = [
            self._node_tag(node, "span", newline_inner=False, newline_outer=False)
        ]
        if node.children:
            items.append(
                AppendTextAndDefer(
                    '<span class="rawhtml-alt" hidden>', "</span>" + node.html
                )
            )
        else:
            items.append(AppendTextAndDefer("", node.html))
        return AppendBatchAndDefer(items)

    def _htmlblock_html(self, node: nodes.HtmlBlock) -> str:
        """An :htmlblock: as one string, as visit_htmlblock writes it."""
        alt = ""
        if node.children:
            alt = f'<div class="rawhtml-alt" hidden>{self._render_inline_nodes(list(node.children))}</div>'
        return f'<div class="htmlblock rawhtml">{alt}{node.html}</div>'

    def visit_htmlblock(self, node: nodes.HtmlBlock) -> EditCommand:
        # Written as an inline :html: is (see visit_rawhtml), in a div. The
        # "rawhtml" class lets copies of the page swap in the fallback.
        items: list[EditCommand] = [
            AppendNodeTag(node, "div", additional_classes=["rawhtml"])
        ]
        if node.children:
            items.append(
                AppendTextAndDefer(
                    '<div class="rawhtml-alt" hidden>', "</div>" + node.html
                )
            )
        else:
            items.append(AppendTextAndDefer("", node.html))
        return AppendBatchAndDefer(items)

    def visit_codeblock(self, node: nodes.CodeBlock) -> AppendBatchAndDefer:
        items = self._close_p_before(node)
        if _has_caption(node):
            # As in a figure, the caption follows the code inside a <figure>, so
            # visit_caption closes the <pre>.
            items += [AppendNodeTag(node, "figure"), AppendText("<pre>")]
            return AppendBatchAndDefer(items)
        items += [
            AppendNodeTag(node, "div", newline_inner=True, newline_outer=True),
            AppendOpenTag("pre"),
        ]
        return AppendBatchAndDefer(items)

    def leave_codeblock(self, node: nodes.CodeBlock) -> EditCommand:
        return self._reopen_p_after(node, self.leave_node(node))

    def visit_algorithm(self, node: nodes.Algorithm) -> AppendBatchAndDefer:
        return AppendBatchAndDefer(
            [
                *self._close_p_before(node),
                AppendOpenTag(
                    id=node.label,
                    classes=["algorithm"],
                    **{"data-caption-name": _caption_name(node)},  # type: ignore[arg-type]  # these keys go to **kwargs, but mypy checks the values against the named parameters too
                ),
                AppendOpenTag("pre", classes=["pseudocode"]),
            ]
        )

    def leave_algorithm(self, node: nodes.Algorithm) -> EditCommand:
        return self._reopen_p_after(node, self.leave_node(node))

    def visit_notation(self, node: nodes.Notation) -> EditCommand:
        # Emit the rebindable-notation entries as data for the frontend, which
        # defines the macros from the defaults and lets the reader reskin them.
        import json

        data = json.dumps(node.entries).replace("</", "<\\/")
        return AppendText(
            f'<script type="application/json" class="rsm-notation">{data}</script>'
        )

    def visit_text(self, node: nodes.Text) -> EditCommand:
        # Text (math source especially, but also prose) is HTML-escaped so a <,
        # > or & cannot open a tag; the client math renderer reads the DOM text
        # content, which the browser decodes back to the original characters.
        # Raw HTML is not text: it is kept on RawHtml and HtmlBlock nodes.
        text = getattr(node, "_nojs_text", node.text)
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return AppendText(text)

    def visit_error(self, node: nodes.Error) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, "span", newline_inner=False, newline_outer=False),
                AppendText(node.text),
            ]
        )

    def visit_span(self, node: nodes.Span) -> EditCommand:
        commands = [
            AppendOpenTag(tag, newline_inner=False, newline_outer=False)
            for attr, tag in nodes.Span.attr_to_tag.items()
            if getattr(node, attr)
        ]
        return AppendBatchAndDefer(
            [
                self._node_tag(
                    node, tag="span", newline_inner=False, newline_outer=False
                ),
                *commands,
            ]
        )

    def visit_construct(self, node: nodes.Construct) -> EditCommand:
        return self._node_tag(
            node, tag="span", newline_inner=False, newline_outer=False
        )

    def _meta_html(self, value: str, value_nodes: list[nodes.Node]) -> str:
        """The HTML of a meta value: its inline nodes when it holds markup, or
        its escaped text."""
        if value_nodes:
            # A copy, because rendering changes the nodes (math takes the
            # punctuation after it), and a value may be shown more than once.
            return self._render_inline_nodes(copy.deepcopy(value_nodes))
        return _wrap_hyphenated_words(html_escape(value, quote=False))

    def _title_html(self, node: nodes.Heading) -> str:
        if node.title_nodes:
            return self._render_inline_nodes(node.title_nodes)
        return _wrap_hyphenated_words(html_escape(node.title, quote=False))

    def _render_inline_nodes(self, inline_nodes: list[nodes.Node]) -> str:
        """Render a list of inline nodes to an HTML string using this
        translator's own visit methods, so markup inside a link's reftext comes
        out exactly as it would in body text. Runs the normal visit/leave loop
        against a scratch body and restores the real one afterwards."""
        saved_body, saved_deferred = self.body, self.deferred
        self.body, self.deferred = "", []
        try:
            stack: list = []
            self.push_children(stack, inline_nodes)
            while stack:
                node, action, method = stack.pop()
                command = method(self, node)
                if action == "visit":
                    node._body_start = len(self.body)
                    if command.defers:
                        self.push_leave(stack, node)
                    self.push_children(stack, node.children)
                command.execute(self)
            return self.body
        finally:
            self.body, self.deferred = saved_body, saved_deferred

    def _make_ahref_tag_text(
        self,
        node: nodes.BaseReference | nodes.Cite,
        target: str | nodes.Node | None,
        href_text: str,
        label: str = "",
        id_: str = "",
        additional_classes: None | list[str] = None,
    ) -> str:
        if not target:
            raise RSMTranslatorError(f"Found a {node.__class__} without a target")
        tgt = target
        reftext_nodes = getattr(node, "reftext_nodes", None)
        if reftext_nodes:
            # The reftext carries inline markup (emphasis, math, code, span).
            # Render those nodes as the link's inner HTML. overwrite_reftext still
            # holds the plain-text flattening for any bare-string context. strip()
            # drops the space the grammar keeps after the comma, matching the
            # plain-reftext path.
            reftext = self._render_inline_nodes(reftext_nodes).strip()
        elif hasattr(node, "overwrite_reftext") and node.overwrite_reftext:
            reftext = _wrap_hyphenated_words(
                html_escape(node.overwrite_reftext, quote=False)
            )
        elif isinstance(tgt, nodes.Node) and tgt.reftext_markup():
            reftext = self._render_inline_nodes(tgt.reftext_markup()).strip()
        else:
            reftext = html_escape(str(getattr(tgt, "reftext", tgt)), quote=False)
            # The text of a bare URL is the URL, which is not prose.
            if not isinstance(node, nodes.URL):
                reftext = _wrap_hyphenated_words(reftext)
        classes = node.classes
        if not isinstance(node, nodes.URL) and "reference" not in classes:
            classes.insert(0, "reference")
        tag = (
            _make_tag(
                "a",
                id_=id_,
                classes=classes + (additional_classes or []),
                href=href_text,
            )
            + reftext
            + "</a>"
        )
        return tag

    def visit_reference(self, node: nodes.Reference) -> EditCommand:
        # Handle external references
        if node.external_file:
            # Convert .rsm extension to .html
            html_path = node.external_file.replace(".rsm", ".html")
            href = f"{html_path}#{node.target.label}"

            # Add 'external' to types
            if "external" not in node.classes:
                node.classes.append("external")

            # For labeled external refs, prefix reftext with manuscript title
            if (
                node.external_manuscript
                and node.external_manuscript.title
                and not node.overwrite_reftext
                and not isinstance(node.target, nodes.Manuscript)
            ):
                local_reftext = getattr(node.target, "reftext", "")
                node.overwrite_reftext = (
                    f"{node.external_manuscript.title}, {local_reftext}"
                )

            tag_text = self._make_ahref_tag_text(node, node.target, href)
        else:
            # Internal reference. A section target may have no explicit label
            # (an unnumbered one in particular), so resolve it to the section's
            # generated anchor instead of the empty label, which would make the
            # table of contents link it to "#".
            if isinstance(node.target, nodes.Section):
                href = f"#{_section_anchor_id(node.target)}"
            elif isinstance(node.target, nodes.Step):
                href = f"#{_step_anchor_id(node.target)}"
            else:
                href = f"#{node.target.label}"
            tag_text = self._make_ahref_tag_text(node, node.target, href)

        # Wrap ref + trailing punctuation to prevent line break between them.
        # Also pull in a preceding opening bracket if present.
        sib = node.next_sibling()
        if (
            isinstance(sib, nodes.Text)
            and sib.text
            and sib.text[0] in self._TRAILING_PUNCT
        ):
            punct = sib.text[0]
            sib.text = sib.text[1:]
            escaped = (
                punct.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )

            # Check if previous sibling ends with an opening bracket.
            # The previous text is already in self.body — remove it from there.
            prefix = ""
            if self.body and self.body[-1] in self._OPENING_BRACKETS:
                prefix = self.body[-1]
                self.body = self.body[:-1]

            return AppendText(
                f'<span class="inline-wrapper">{prefix}{tag_text}<span>{escaped}</span></span>'
            )
        return AppendText(tag_text)

    def visit_url(self, node: nodes.URL) -> EditCommand:
        return AppendText(
            self._make_ahref_tag_text(node, node.target, f"{node.target}")
        )

    def visit_claimblock(self, node: nodes.ClaimBlock) -> EditCommand:
        return AppendNodeTag(node)

    def _make_title_node(
        self,
        label: str,
        desc: str = "",
        classes: list | None = None,
        desc_nodes: list[nodes.Node] | None = None,
        label_nodes: list[nodes.Node] | None = None,
    ) -> nodes.Paragraph:
        if classes is None:
            classes = ["hr-label"]
        para = nodes.Paragraph(classes=classes)
        if label_nodes:
            span = nodes.Span(classes=["label"])
            for n in label_nodes:
                n.parent = None
                span.append(n)
            para.append(span)
        elif label:
            span = nodes.Span(classes=["label"])
            span.append(nodes.Text(text=label))
            para.append(span)
        if desc_nodes:
            span = nodes.Span(classes=["desc"])
            for n in desc_nodes:
                n.parent = None
                span.append(n)
            para.append(span)
        elif desc:
            span = nodes.Span(classes=["desc"])
            span.append(nodes.Text(text=desc))
            para.append(span)
        return para

    def visit_theorem(self, node: nodes.Theorem) -> AppendBatchAndDefer:
        suffix = (f" {node.full_number}" if not node.nonum and node.number else "") + (
            ": " if node.title else "."
        )
        title = self._make_title_node(
            label=node.kindname + suffix,
            label_nodes=(
                copy.deepcopy(node.blockname_nodes) + [nodes.Text(suffix)]
                if node.blockname_nodes
                else None
            ),
            desc=node.title or "",
            # A copy, because the title nodes stay in their holder, where the
            # plain-text uses of the title read them.
            desc_nodes=copy.deepcopy(node.title_nodes) if node.title_nodes else None,
        )
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, additional_classes=["theorem"]),
                AppendExternalTree(title, self),
            ]
        )

    def visit_statement(self, node: nodes.Statement) -> EditCommand:
        return AppendNodeTag(node)

    def visit_subproof(self, node: nodes.Subproof) -> EditCommand:
        node.__class__.__name__.lower()
        return AppendBatchAndDefer([AppendNodeTag(node)])

    def visit_tabs(self, node: nodes.Tabs) -> EditCommand:
        return AppendBatchAndDefer([AppendNodeTag(node)])

    def visit_tab(self, node: nodes.Tab) -> EditCommand:
        # Each tab is a radio input, its label and its panel, in that order:
        # braiid.css shows the panel that follows a checked input and puts the
        # labels in one row above the panels. All radios of a group share one
        # name, so the browser keeps exactly one checked.
        radio_id = f"tab-{node.nodeid}"
        # A tab is always inside its tabs block.
        assert node.parent is not None
        first = node.parent.children[0] is node
        radio = (
            f'\n<input type="radio" class="tab-input" name="tabs-{node.parent.nodeid}"'
            f' id="{radio_id}"{" checked" if first else ""}>'
        )
        label = AppendOpenCloseTag(
            "label",
            self._title_html(node),
            classes=["tab-label"],
            newline_inner=False,
            **{"for": radio_id},  # type: ignore[arg-type]  # these keys go to **kwargs, but mypy checks the values against the named parameters too
        )
        panel = AppendNodeTag(node, extra_attrs={"data-tab": radio_id})
        return AppendBatchAndDefer([AppendText(radio), label, panel])

    def visit_sketch(self, node: nodes.Sketch) -> AppendBatchAndDefer:
        title = self._make_title_node(label="Proof sketch.")
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node),
                AppendExternalTree(title, self),
            ]
        )

    def visit_proof(self, node: nodes.Proof) -> AppendBatchAndDefer:
        last = node.last_of_type(nodes.Step)
        if last:
            last.classes.append("last")

        proves = getattr(node, "proves", None)
        if proves is not None:
            # "Proof of <linked result>." The reference renders like any :ref:.
            title = nodes.Paragraph(classes=["hr-label"])
            span = nodes.Span(classes=["label"])
            span.append(nodes.Text(text="Proof of "))
            span.append(nodes.Reference(target=proves))
            span.append(nodes.Text(text="."))
            title.append(span)
        else:
            classname = node.__class__.__name__.lower()
            title = self._make_title_node(label=f"{classname.capitalize()}.")

        extra_attrs = None
        if node.num_steps:
            extra_attrs = {"data-steps": str(node.num_steps)}

        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, extra_attrs=extra_attrs),
                AppendExternalTree(title, self),
            ]
        )

    @auto_leave_deferred
    def leave_proof(
        self, node: nodes.Proof, base_batch: EditCommandBatch
    ) -> EditCommand:
        base_batch.items.insert(-1, AppendHalmos())
        return AppendBatch(base_batch.items)

    @staticmethod
    def _fold_calc_rows(node: nodes.Calc) -> None:
        # Each relation step starts collapsed: a collapsed step shows its claim
        # (here the relation) and hides its proof (here the justification), so the
        # chain reads as the bare relations with each "why" disclosed on demand.
        # Subtractive (data-start-collapsed): JS off renders it fully open, the
        # complete written proof.
        for step in node.children:
            step.collapsed = True

    def visit_calc(self, node: nodes.Calc) -> AppendBatchAndDefer:
        self._fold_calc_rows(node)
        return AppendBatchAndDefer([AppendNodeTag(node)])

    @auto_leave_deferred
    def leave_calc(self, node: nodes.Calc, base_batch: EditCommandBatch) -> EditCommand:
        # Inside a proof the chain reads as one step and closes with its own
        # tombstone. Outside a proof it is a display equation and has none.
        if node.first_ancestor_of_type(nodes.Proof) is not None:
            base_batch.items.insert(-1, AppendHalmos())
        return AppendBatch(base_batch.items)

    @staticmethod
    def _is_calc_relation(node: nodes.Math) -> bool:
        """Whether this math is the relation of a calc row, not part of its reason."""
        anc = node.parent
        while anc is not None:
            if isinstance(anc, nodes.Subproof):
                return False
            if isinstance(anc, nodes.Step) and anc.in_calc:
                return True
            anc = anc.parent
        return False

    def visit_cite(self, node: nodes.Cite) -> EditCommand:
        style = getattr(self.tree, "citation_style", "numeric")
        if style in ("parens-author-year", "author-parens-year"):
            return self._visit_cite_author_year(node, style)
        classes = ["cite"]
        if len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(node.targets[0], nodes.UnknownBibitem):
                classes.append("unknown")
            text = self._make_ahref_tag_text(
                node,
                t,
                f"#{t.label}",
                id_=node.label,
                additional_classes=classes,
            )
        else:
            tags = [
                self._make_ahref_tag_text(
                    node,
                    t,
                    f"#{t.label}",
                    id_=f"{node.label}-{idx}",
                    additional_classes=classes,
                )
                for idx, t in enumerate(node.targets)
            ]
            if len(tags) == 1:
                text = tags[0]
            else:
                first = f'<span class="nowrap">[{tags[0]},</span>'
                middle = ", ".join(tags[1:-1])
                last = f'<span class="nowrap">{tags[-1]}]</span>'
                if middle:
                    text = f"{first} {middle}, {last}"
                else:
                    text = f"{first} {last}"
                text = f'<span id="{node.label}">{text}</span>'
                return AppendText(text)
            text = f'<span id="{node.label}">{text}</span>'
        return AppendText(f'<span class="nowrap">[{text}]</span>')

    @staticmethod
    def _author_year_parts(bibitem: nodes.Bibitem) -> tuple[str, str]:
        """The author display and the (possibly suffixed) year for an
        author-year citation. The year carries the a/b/c suffix assigned during
        transform when another cited work shares this author and year. An
        unknown citation (no author) shows "?" so the link is not blank
        (rsm-3ez)."""
        name = bibitem.short_author() or "?"
        year = str(bibitem.year or "")
        suffix = getattr(bibitem, "year_suffix", "")
        return name, (f"{year}{suffix}" if year else year)

    def _visit_cite_author_year(self, node: nodes.Cite, style: str) -> EditCommand:
        # parens-author-year keeps one outer paren around all keys (the author
        # and year sit bare inside the link); author-parens-year puts the year
        # in parens inside each link and joins the keys with commas.
        #
        # A non-breaking space keeps each year glued to its author so the pair
        # never splits across a line. The parens and the inter-citation
        # separators carry no adjacent space on their binding side, so they
        # glue to their citation on their own. The author list and the gaps
        # between citations stay breakable, so a long multi-author citation
        # wraps instead of overflowing a narrow column. This is the care the
        # numeric style gives its brackets, adapted so a spelled-out author
        # list cannot force a horizontal overflow.
        nbsp = " "
        multiple = len(node.targets) > 1
        parts = []
        for idx, target in enumerate(node.targets):
            classes = ["cite"]
            if isinstance(target, nodes.UnknownBibitem):
                classes.append("unknown")
            name, year = self._author_year_parts(target)
            if style == "parens-author-year":
                inner = f"{name},{nbsp}{year}" if year else name
            else:
                inner = f"{name}{nbsp}({year})" if year else name
            node.overwrite_reftext = inner
            id_ = f"{node.label}-{idx}" if multiple else node.label
            parts.append(
                self._make_ahref_tag_text(
                    node,
                    target,
                    f"#{target.label}",
                    id_=id_,
                    additional_classes=classes,
                )
            )
        if style == "parens-author-year":
            text = "(" + "; ".join(parts) + ")"
        else:
            text = ", ".join(parts)
        if multiple:
            text = f'<span id="{node.label}">{text}</span>'
        return AppendText(text)

    def visit_bibliography(self, node: nodes.Bibliography) -> AppendBatchAndDefer:
        # Author-year bibliographies are unnumbered (the citation carries the
        # author and year), so they use an unordered list; numeric stays an <ol>.
        style = getattr(self.tree, "citation_style", "numeric")
        list_tag = (
            "ul" if style in ("parens-author-year", "author-parens-year") else "ol"
        )
        return AppendBatchAndDefer(
            [
                AppendOpenTag("section", classes=["level-2"]),
                AppendHeading(2, "References"),
                AppendNodeTag(node, list_tag),
            ]
        )

    def visit_bibitem(self, node: nodes.Bibitem) -> AppendBatchAndDefer:
        # An entry is a card: authors and year with the DOI, title, venue with
        # the links back to each citation. Author-year bibliographies are
        # unnumbered and the year carries the a/b/c suffix assigned during
        # transform; numeric ones show the number in a pill beside the card.
        style = getattr(self.tree, "citation_style", "numeric")
        ay = style in ("parens-author-year", "author-parens-year")
        year_text = (
            f"{node.year}{node.year_suffix}" if (ay and node.year) else node.year
        )

        link = ""
        if node.doi:
            doi = _normalize_doi(node.doi)
            link = (
                _make_tag(
                    "a",
                    id_=f"{node.label}-doi",
                    classes=["bibitem-doi"],
                    href=f"https://doi.org/{doi}",
                    target="_blank",
                    title=f"doi.org/{doi}",
                )
                + "DOI ↗</a>"
            )
        elif node.url:
            shown = re.sub(r"^https?://(www\.)?", "", node.url).rstrip("/")
            link = (
                _make_tag(
                    "a",
                    id_=f"{node.label}-url",
                    classes=["bibitem-url"],
                    href=node.url,
                    target="_blank",
                    title=shown,
                )
                + "Link ↗</a>"
            )
        elif not node.verbatim:
            logger.warning(f"Bibitem {node.label} has no DOI")

        cited = ""
        if node.backlinks:
            many = len(node.backlinks) > 1
            backs = [
                _make_tag(
                    "a",
                    id_="",
                    classes=["reference", "backlink"],
                    href=f"#{link_lbl}",
                    **{  # type: ignore[arg-type]  # these keys go to **kwargs, but mypy checks the values against the named parameters too
                        "aria-label": f"Back to citation {idx}"
                        if many
                        else "Back to the citation"
                    },
                )
                + "↖"
                + (f"<sup>{idx}</sup>" if many else "")
                + "</a>"
                for idx, link_lbl in enumerate(node.backlinks, start=1)
            ]
            cited = '<span class="bib-cited">cited ' + " ".join(backs) + "</span>"

        # The DOI sits in the top right corner and the back links at the end of
        # the venue line, so the card needs no row of its own for them.
        def line(main: str, side: str) -> str:
            return f'<div class="bib-line">{main}{side}</div>'

        lines = []
        if node.verbatim:
            # A verbatim reference is unstructured, so render its text as-is and
            # warn once here instead of emitting the per-field warnings below.
            logger.warning(f"Bibitem {node.label} is a verbatim (unparsed) reference")
            verbatim = _wrap_hyphenated_words(node.verbatim)
            lines.append(
                line(f'<div class="bib-verbatim">{verbatim}</div>', link + cited)
            )
        else:
            who = str(node.author or "").strip()
            if node.year:
                who = f"{who} ({year_text})" if who else f"({year_text})"
            else:
                logger.warning(f"Bibitem {node.label} has no year")
            lines.append(
                line(f'<div class="bib-who">{_wrap_hyphenated_words(who)}</div>', link)
            )
            title = _wrap_hyphenated_words(str(node.title or "").strip().rstrip("."))
            venue = _wrap_hyphenated_words(self._bib_venue(node))
            lines.append(f'<div class="bib-title">{title}</div>')
            lines.append(line(f'<div class="bib-venue">{venue}</div>', cited))

        body = '<div class="bib-body">' + "".join(lines) + "</div>"
        num = ""
        if node.number and not ay:
            num = f'<span class="bib-num">{node.number}</span>'
        text = f'<div class="bib-card">{num}{body}</div>'
        return AppendBatchAndDefer([AppendNodeTag(node, "li"), AppendText(text)])

    def _bib_venue(self, node: nodes.Bibitem) -> str:
        """Where the work appeared: journal and volume, publisher, proceedings,
        school or institution, depending on the entry type."""
        parts = []
        if node.kind == "article":
            if node.journal:
                # Journal, volume and issue are one clause: "Journal 52(3)".
                journal_part = str(node.journal)
                if node.volume:
                    journal_part += f" {node.volume}"
                    # The issue number only makes sense beside a volume.
                    if node.issue:
                        journal_part += f"({node.issue})"
                parts.append(journal_part)
            else:
                logger.warning(f"Bibitem {node.label} has no journal")
        elif node.kind == "book":
            if node.publisher:
                parts.append(node.publisher)
            else:
                logger.warning(f"Bibitem {node.label} has no publisher")
        elif node.kind in ("inproceedings", "conference"):
            if node.booktitle:
                parts.append(f"In {node.booktitle}")
        elif node.kind == "incollection":
            if node.booktitle:
                parts.append(f"In {node.booktitle}")
            if node.publisher:
                parts.append(node.publisher)
        elif node.kind in ("phdthesis", "mastersthesis"):
            parts.append(
                "PhD thesis" if node.kind == "phdthesis" else "Master's thesis"
            )
            if node.school:
                parts.append(node.school)
        elif node.kind == "techreport":
            parts.append("Technical report")
            if node.institution:
                parts.append(node.institution)
        elif node.kind in ("misc", "webpage"):
            if node.howpublished:
                parts.append(node.howpublished)
        return ", ".join(str(x).strip() for x in parts if str(x).strip())

    def visit_draft(self, node: nodes.Draft) -> EditCommand:
        return AppendBatchAndDefer(
            [AppendNodeTag(node, "span"), AppendTextAndDefer("[ ", " ]")]
        )

    def _resolve_html_content(self, path: str | Path) -> str:
        """Resolve an HTML asset file and return processed content."""
        content = self.asset_resolver.resolve_asset(str(path))
        if isinstance(content, bytes):
            logger.error(f"HTML asset {path} is not UTF-8 text")
            content = None
        if content is None:
            return f'<div class="html-error">Unable to load HTML asset: {path}</div>'

        is_full_html_doc = content.strip().lower().startswith(
            "<html"
        ) or content.strip().lower().startswith("<!doctype")

        if is_full_html_doc:
            _reject_html_wrapper(path)
        return content

    def _resolve_image_src(self, path: str | Path) -> str:
        """Resolve an image asset to a src attribute value.

        Delegates to the asset resolver, which returns either a URL path
        (for server-rendered previews) or file content (for standalone
        export, which gets base64-encoded into a data URI).
        """
        resolved = self.asset_resolver.resolve_asset(str(path))
        if resolved is None:
            return str(path)

        # If the resolver returned a string that looks like a URL/path
        # (not raw content), use it directly.
        if isinstance(resolved, str) and (
            resolved.startswith("/") or resolved.startswith("http")
        ):
            return resolved

        if not self.standalone:
            return str(path)

        import base64
        import mimetypes

        mime = mimetypes.guess_type(str(path))[0] or "image/png"
        if isinstance(resolved, bytes):
            encoded = base64.b64encode(resolved).decode("ascii")
        else:
            encoded = base64.b64encode(resolved.encode("utf-8")).decode("ascii")
        return f"data:{mime};base64,{encoded}"

    def _render_image(self, node: nodes.Asset) -> str:
        if node.alt:
            alt_text = node.alt
        elif node.full_number:
            alt_text = f"{node.__class__.__name__} {node.full_number}."
        else:
            # An unnumbered asset has no "Figure N." to name it by (it showed "Figure None.").
            alt_text = node.__class__.__name__
        src = self._resolve_image_src(node.path)
        # No id on the <img>: the asset's label already becomes the id on the
        # enclosing <figure> (via AppendNodeTag), and putting it here too gave
        # the document two elements with the same id. Every call to this method
        # renders inside that figure wrapper, so the figure keeps the id.
        img = _make_tag(
            "img",
            id_=None,
            classes=[],
            src=src,
            alt=alt_text,
            onload="" if node.scale == 1.0 else f"this.width*={node.scale};",
        )
        if node.dark:
            dark_src = self._resolve_image_src(node.dark)
            source = (
                f'<source media="(prefers-color-scheme: dark)" srcset="{dark_src}">'
            )
            return f"<picture>\n{source}\n{img}\n</picture>"
        return img

    def _detect_content_type_and_render(self, node: nodes.Asset) -> str:
        """Detect content type from path and return appropriate HTML."""
        path_str = str(node.path).lower()

        if isinstance(node, nodes.Figure) and node.htmlblock is not None:
            return self._htmlblock_html(node.htmlblock)

        # An asset with no real path has nothing to render here, and must not
        # fall through to the image branch, which would emit <img src=".">.
        if not path_str or path_str == ".":
            return ""

        # Image files
        if any(
            path_str.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg"]
        ):
            return self._render_image(node)

        # Video files. As with <img>, the label's id goes on the enclosing
        # <figure> only, so the <video> gets none.
        elif any(path_str.endswith(ext) for ext in [".mp4", ".webm", ".avi", ".mov"]):
            return (
                _make_tag(
                    "video",
                    id_=None,
                    classes=[],
                    controls=True,
                    src=node.path,
                )
                + "Your browser does not support the video tag.</video>"
            )

        # YouTube URLs - treat as videos but note the URL
        elif "youtube.com/watch" in path_str or "youtu.be/" in path_str:
            return (
                _make_tag(
                    "video",
                    id_=None,
                    classes=[],
                    controls=True,
                    src=node.path,
                )
                + f"YouTube video: {node.path}</video>"
            )

        # HTML files
        elif path_str.endswith(".html"):
            return self._resolve_html_content(node.path)

        # Default to image behavior
        else:
            return self._render_image(node)

    def _fallback_alt(self, node: nodes.Asset) -> str:
        """Alt text for a static fallback image: the author's :alt:, else the
        caption's plain text, else empty. The old generated "Static fallback for
        Figure N." named the mechanism, not the picture. :static: without :alt:
        warns once, naming the asset."""
        if node.alt:
            return node.alt
        ident = node.label or (
            f"figure {node.full_number}" if node.full_number else "an asset"
        )
        logger.warning(f"Static fallback for {ident} has :static: but no :alt:")
        caption = next((c for c in node.children if isinstance(c, nodes.Caption)), None)
        if caption is not None:
            text = "".join(
                t.text for t in caption.traverse(nodeclass=nodes.Text)
            ).strip()
            if text:
                return text
        return ""

    def _static_fallback_img(self, node: nodes.Asset) -> str:
        if not node.static:
            return ""
        src = self._resolve_image_src(node.static)
        alt = self._fallback_alt(node)

        if node.dark:
            dark_src = self._resolve_image_src(node.dark)
            # The dark variant is gated by CSS (.static-fallback-dark) under both
            # the .dark-theme class and prefers-color-scheme: dark; the light
            # variant is the default and is hidden by the same CSS in dark mode.
            inner = (
                f'<img class="static-fallback-light" src="{src}" alt="{alt}">'
                f'<img class="static-fallback-dark" src="{dark_src}" alt="{alt}">'
            )
        else:
            inner = f'<img src="{src}" alt="{alt}">'

        # Two copies of the same static content:
        #   * the .static-fallback element, hidden inline and revealed by the JS
        #     static-toggle (toggleStaticView), and
        #   * a <noscript> copy that browsers render only when JS is disabled,
        #     so the static still appears with scripting off or when printing.
        # The inline display:none must stay off the noscript copy: CSS cannot
        # override it, which is exactly why the JS path needs it and the no-JS
        # path must not have it.
        toggleable = (
            f'<span class="static-fallback" style="display:none">{inner}</span>'
        )
        noscript = f"<noscript>{inner}</noscript>"
        return toggleable + noscript

    def visit_figure(self, node: nodes.Figure) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, "figure", additional_classes=_asset_classes(node)),
                AppendText(self._detect_content_type_and_render(node)),
                AppendText(self._static_fallback_img(node)),
            ]
        )

    def visit_video(self, node: nodes.Video) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, "figure", additional_classes=_asset_classes(node)),
                AppendText(self._detect_content_type_and_render(node)),
            ]
        )

    def visit_caption(self, node: nodes.Caption) -> EditCommand:
        parent = node.parent
        # A caption is always inside the block that it captions.
        assert parent is not None
        caption = _caption_label(parent, self)
        # Tables use figcaption outside <table> (inside table-wrapper) so the caption
        # doesn't participate in the table's intrinsic width calculation.
        use_figcaption = isinstance(parent, (nodes.Asset, nodes.Table, nodes.CodeBlock))
        items: list[EditCommand] = []
        if isinstance(parent, nodes.Table):
            items.append(AppendText("\n</table>\n"))
        if isinstance(parent, nodes.CodeBlock):
            items.append(AppendText("</pre>\n"))
        items.extend(
            [
                AppendOpenTag("figcaption" if use_figcaption else "caption"),
                caption,
            ]
        )
        return AppendBatchAndDefer(items)

    def visit_appendix(self, node: nodes.Appendix) -> EditCommand:
        # Appendix nodes are used during the transform phase, but do not apear in the
        # output in any way.
        return AppendText("")

    def visit_table(self, node: nodes.Table) -> AppendBatchAndDefer:
        table_tag = AppendNodeTag(node, "table")
        manual_table = AppendOpenTagManualClose(
            tag="table",
            id=table_tag.id,
            classes=table_tag.classes,
            **table_tag.custom_attrs,
        )
        return AppendBatchAndDefer(
            [
                AppendOpenTag("div", classes=["table-wrapper"]),
                manual_table,
            ]
        )

    def leave_table(self, node: nodes.Table) -> EditCommand:
        has_caption = any(isinstance(c, nodes.Caption) for c in node.children)
        # The visit method deferred a batch, so leave_node returns one.
        batch = cast(EditCommandBatch, self.leave_node(node))
        if not has_caption:
            batch.items.insert(0, AppendText("\n</table>\n"))
        return batch

    def visit_tablehead(self, node: nodes.TableHead) -> EditCommand:
        return AppendNodeTag(node, "thead")

    def visit_tablebody(self, node: nodes.TableBody) -> EditCommand:
        return AppendNodeTag(node, "tbody")

    def visit_tablerow(self, node: nodes.TableRow) -> EditCommand:
        return AppendNodeTag(node, "tr")

    def visit_tabledatum(self, node: nodes.TableDatum) -> EditCommand:
        return AppendNodeTag(node, "td", newline_inner=False)


class HandrailsTranslator(Translator):
    svg = {
        "link": """<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
        <path d="M6 12.0003L12 6.00031M8 3.00031L8.463 2.46431C9.40081 1.52663 10.6727 0.999906 11.9989 1C13.325 1.00009 14.5968 1.527 15.5345 2.46481C16.4722 3.40261 16.9989 4.6745 16.9988 6.00066C16.9987 7.32682 16.4718 8.59863 15.534 9.53631L15 10.0003M10.0001 15.0003L9.60314 15.5343C8.65439 16.4725 7.37393 16.9987 6.03964 16.9987C4.70535 16.9987 3.42489 16.4725 2.47614 15.5343C2.0085 15.0719 1.63724 14.5213 1.38385 13.9144C1.13047 13.3076 1 12.6565 1 11.9988C1 11.3412 1.13047 10.69 1.38385 10.0832C1.63724 9.47628 2.0085 8.92571 2.47614 8.46331L3.00014 8.00031" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>""",
        "tree": """<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
        <path d="M3.57525 14.0448L6.00051 10.36M7.78824 7.64238L10.211 3.95918M7.79153 10.364L10.2134 14.044M12.0004 3.96001L14.4265 7.64801M4.36842 15.4C4.36842 14.9757 4.19098 14.5687 3.87513 14.2686C3.55928 13.9686 3.13089 13.8 2.68421 13.8C2.23753 13.8 1.80914 13.9686 1.49329 14.2686C1.17744 14.5687 1 14.9757 1 15.4C1 15.8243 1.17744 16.2313 1.49329 16.5314C1.80914 16.8314 2.23753 17 2.68421 17C3.13089 17 3.55928 16.8314 3.87513 16.5314C4.19098 16.2313 4.36842 15.8243 4.36842 15.4ZM12.7895 2.6C12.7895 2.17565 12.612 1.76869 12.2962 1.46863C11.9803 1.16857 11.5519 1 11.1053 1C10.6586 1 10.2302 1.16857 9.91435 1.46863C9.5985 1.76869 9.42105 2.17565 9.42105 2.6C9.42105 3.02435 9.5985 3.43131 9.91435 3.73137C10.2302 4.03143 10.6586 4.2 11.1053 4.2C11.5519 4.2 11.9803 4.03143 12.2962 3.73137C12.612 3.43131 12.7895 3.02435 12.7895 2.6ZM12.7895 15.4C12.7895 14.9757 12.612 14.5687 12.2962 14.2686C11.9803 13.9686 11.5519 13.8 11.1053 13.8C10.6586 13.8 10.2302 13.9686 9.91435 14.2686C9.5985 14.5687 9.42105 14.9757 9.42105 15.4C9.42105 15.8243 9.5985 16.2313 9.91435 16.5314C10.2302 16.8314 10.6586 17 11.1053 17C11.5519 17 11.9803 16.8314 12.2962 16.5314C12.612 16.2313 12.7895 15.8243 12.7895 15.4ZM8.57895 9C8.57895 8.57565 8.4015 8.16869 8.08565 7.86863C7.7698 7.56857 7.34142 7.4 6.89474 7.4C6.44806 7.4 6.01967 7.56857 5.70382 7.86863C5.38797 8.16869 5.21053 8.57565 5.21053 9C5.21053 9.42435 5.38797 9.83131 5.70382 10.1314C6.01967 10.4314 6.44806 10.6 6.89474 10.6C7.34142 10.6 7.7698 10.4314 8.08565 10.1314C8.4015 9.83131 8.57895 9.42435 8.57895 9ZM17 9C17 8.57565 16.8226 8.16869 16.5067 7.86863C16.1909 7.56857 15.7625 7.4 15.3158 7.4C14.8691 7.4 14.4407 7.56857 14.1249 7.86863C13.809 8.16869 13.6316 8.57565 13.6316 9C13.6316 9.42435 13.809 9.83131 14.1249 10.1314C14.4407 10.4314 14.8691 10.6 15.3158 10.6C15.7625 10.6 16.1909 10.4314 16.5067 10.1314C16.8226 9.83131 17 9.42435 17 9Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>""",
        "code": """<svg width="18" height="16" viewBox="0 0 18 16" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
        <path d="M4.55556 4.5L1 8L4.55556 11.5M13.4444 4.5L17 8L13.4444 11.5M10.7778 1L7.22222 15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>""",
        "bookmark": """<svg width="14" height="18" viewBox="0 0 14 18" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
        <path d="M13 4.55556V17L7 13.4444L1 17V4.55556C1 3.61256 1.42143 2.70819 2.17157 2.0414C2.92172 1.3746 3.93913 1 5 1H9C10.0609 1 11.0783 1.3746 11.8284 2.0414C12.5786 2.70819 13 3.61256 13 4.55556Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>""",
        "success": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="2 2 20 20" fill="#3C4952" stroke-width="0" >
        <path d="M17 3.34a10 10 0 1 1 -14.995 8.984l-.005 -.324l.005 -.324a10 10 0 0 1 14.995 -8.336zm-1.293 5.953a1 1 0 0 0 -1.32 -.083l-.094 .083l-3.293 3.292l-1.293 -1.292l-.094 -.083a1 1 0 0 0 -1.403 1.403l.083 .094l2 2l.094 .083a1 1 0 0 0 1.226 0l.094 -.083l4 -4l.083 -.094a1 1 0 0 0 -.083 -1.32z" />
        </svg>""",
        "alert": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="1.1 1 22 22" fill="#3C4952" stroke-width="0" >
        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
        <path d="M12 1.67c.955 0 1.845 .467 2.39 1.247l.105 .16l8.114 13.548a2.914 2.914 0 0 1 -2.307 4.363l-.195 .008h-16.225a2.914 2.914 0 0 1 -2.582 -4.2l.099 -.185l8.11 -13.538a2.914 2.914 0 0 1 2.491 -1.403zm.01 13.33l-.127 .007a1 1 0 0 0 0 1.986l.117 .007l.127 -.007a1 1 0 0 0 0 -1.986l-.117 -.007zm-.01 -7a1 1 0 0 0 -.993 .883l-.007 .117v4l.007 .117a1 1 0 0 0 1.986 0l.007 -.117v-4l-.007 -.117a1 1 0 0 0 -.993 -.883z" />
        </svg>""",
        "question": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#3C4952" stroke-width="0" >
        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
        <path d="M10.425 1.414a3.33 3.33 0 0 1 3.026 -.097l.19 .097l6.775 3.995l.096 .063l.092 .077l.107 .075a3.224 3.224 0 0 1 1.266 2.188l.018 .202l.005 .204v7.284c0 1.106 -.57 2.129 -1.454 2.693l-.17 .1l-6.803 4.302c-.918 .504 -2.019 .535 -3.004 .068l-.196 -.1l-6.695 -4.237a3.225 3.225 0 0 1 -1.671 -2.619l-.007 -.207v-7.285c0 -1.106 .57 -2.128 1.476 -2.705l6.95 -4.098zm1.575 13.586a1 1 0 0 0 -.993 .883l-.007 .117l.007 .127a1 1 0 0 0 1.986 0l.007 -.117l-.007 -.127a1 1 0 0 0 -.993 -.883zm1.368 -6.673a2.98 2.98 0 0 0 -3.631 .728a1 1 0 0 0 1.44 1.383l.171 -.18a.98 .98 0 0 1 1.11 -.15a1 1 0 0 1 -.34 1.886l-.232 .012a1 1 0 0 0 .111 1.994a3 3 0 0 0 1.371 -5.673z" />
        </svg>""",
        "heart": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="1 1 22 22" fill="#3C4952" >
        <path stroke="none" d="M0 0h24v24H0z" fill="none" />
        <path d="M6.979 3.074a6 6 0 0 1 4.988 1.425l.037 .033l.034 -.03a6 6 0 0 1 4.733 -1.44l.246 .036a6 6 0 0 1 3.364 10.008l-.18 .185l-.048 .041l-7.45 7.379a1 1 0 0 1 -1.313 .082l-.094 -.082l-7.493 -7.422a6 6 0 0 1 3.176 -10.215z" />
        </svg>""",
        "star": """<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
        <path d="M9.00561 14.2664L4.06109 17L5.00561 11.2101L1 7.11004L6.52774 6.26763L9 1L11.4723 6.26763L17 7.11004L12.9944 11.2101L13.9389 17L9.00561 14.2664Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>""",
        "collapse": """<svg width="8" height="14" viewBox="0 0 8 14" fill="none" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path d="M1 1L7 7L1 13" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>""",
        "collapse-all": """<svg width="9" height="9" viewBox="5 5 14 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
        <path d="M7 7l5 5l-5 5" />
        <path d="M13 7l5 5l-5 5" />
      </svg>""",
        "chevron-down": """<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
<path d="M6 9l6 6l6 -6" />
</svg>""",
        # Tabler's "mail" icon.
        "mail": """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
<path d="M3 7a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v10a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2v-10z" />
<path d="M3 7l9 6l9 -6" />
</svg>""",
        # ORCID's own iD icon (orcid.org/assets/vectors/orcid.logo.icon.svg).
        # Tabler has none (tabler/tabler-icons#1163).
        "orcid": """<svg width="14" height="14" viewBox="0 0 72 72" xmlns="http://www.w3.org/2000/svg">
<path fill="#A6CE39" d="M72,36 C72,55.884375 55.884375,72 36,72 C16.115625,72 0,55.884375 0,36 C0,16.115625 16.115625,0 36,0 C55.884375,0 72,16.115625 72,36 Z" />
<g transform="translate(18.868966 12.910345)" fill="#FFFFFF">
<polygon points="5.03734929 39.1250878 0.695429861 39.1250878 0.695429861 9.14431787 5.03734929 9.14431787 5.03734929 22.6930505 5.03734929 39.1250878" />
<path d="M11.409257,9.14431787 L23.1380784,9.14431787 C34.303014,9.14431787 39.2088191,17.0664074 39.2088191,24.1486995 C39.2088191,31.846843 33.1470485,39.1530811 23.1944669,39.1530811 L11.409257,39.1530811 L11.409257,9.14431787 Z M15.7511765,35.2620194 L22.6587756,35.2620194 C32.49858,35.2620194 34.7541226,27.8438084 34.7541226,24.1486995 C34.7541226,18.1301509 30.8915059,13.0353795 22.4332213,13.0353795 L15.7511765,13.0353795 L15.7511765,35.2620194 Z" />
<path d="M5.71401206,2.90182329 C5.71401206,4.441452 4.44526937,5.72914146 2.86638958,5.72914146 C1.28750978,5.72914146 0.0187670918,4.441452 0.0187670918,2.90182329 C0.0187670918,1.33420133 1.28750978,0.0745051096 2.86638958,0.0745051096 C4.44526937,0.0745051096 5.71401206,1.36219458 5.71401206,2.90182329 Z" />
</g>
</svg>""",
        "expand": """<svg width="14" height="8" viewBox="0 0 14 8" fill="none" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M1 1L7 7L13 1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
        "expand-all": """<svg width="9" height="9" viewBox="5 5 14 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
<path d="M7 7l5 5l5 -5" />
<path d="M7 13l5 5l5 -5" />
</svg>""",
        "dots": """<svg width="24" height="24" viewBox="10 3 4 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
<path stroke="none" d="M0 0h24v24H0z" fill="none"/>
<path d="M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
<path d="M12 19m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
<path d="M12 5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
</svg>""",
        "ext": """<svg width="15" height="15" viewBox="3 3 18 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M12 6h-6a2 2 0 0 0 -2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-6" />
          <path d="M11 13l9 -9" />
          <path d="M15 4h5v5" />
        </svg>""",
        "image": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M15 8h.01" />
          <path d="M3 6a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v12a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3v-12" />
          <path d="M3 16l5 -5c.928 -.893 2.072 -.893 3 0l5 5" />
          <path d="M14 14l1 -1c.928 -.893 2.072 -.893 3 0l3 3" />
        </svg>""",
        "play": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M7 4v16l13 -8l-13 -8" />
        </svg>""",
        "reorder": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M3 9l4 -4l4 4m-4 -4v14" />
          <path d="M21 15l-4 4l-4 -4m4 4v-14" />
        </svg>""",
        "pin": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
          <path d="M15 4.5l-4 4l-4 1.5l-1.5 1.5l7 7l1.5 -1.5l1.5 -4l4 -4" />
          <path d="M9 15l-4.5 4.5" />
          <path d="M14.5 4l5.5 5.5" />
        </svg>""",
        # The pin crossed out by a bar from (3,3) to (21,21). The mask cuts a gap
        # in the pin along the bar, so the bar stays readable where they cross.
        "unpin": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
          <mask id="hr-icon-unpin-cut" maskUnits="userSpaceOnUse" x="0" y="0" width="24" height="24">
            <rect width="24" height="24" fill="white" />
            <path d="M3 3l18 18" stroke="black" stroke-width="5" />
          </mask>
          <g mask="url(#hr-icon-unpin-cut)">
            <path d="M15 4.5l-4 4l-4 1.5l-1.5 1.5l7 7l1.5 -1.5l1.5 -4l4 -4" />
            <path d="M9 15l-4.5 4.5" />
            <path d="M14.5 4l5.5 5.5" />
          </g>
          <path d="M3 3l18 18" />
        </svg>""",
        "focus-2": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
          <path d="M12 12m-5 0a5 5 0 1 0 10 0a5 5 0 1 0 -10 0" />
          <path d="M12 3l0 2" />
          <path d="M3 12l2 0" />
          <path d="M12 19l0 2" />
          <path d="M19 12l2 0" />
        </svg>""",
        "deplens-up": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M12 4l0 10" />
          <path d="M12 14l4 -4" />
          <path d="M12 14l-4 -4" />
          <path d="M4 20l16 0" />
        </svg>""",
        "deplens-down": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
          <path stroke="none" d="M0 0h24v24H0z" fill="none" />
          <path d="M4 4l16 0" />
          <path d="M12 10l0 10" />
          <path d="M12 10l4 4" />
          <path d="M12 10l-4 4" />
        </svg>""",
    }

    def __init__(
        self,
        quiet: bool = False,
        source_offsets: bool = True,
        copy_source: bool = True,
        asset_resolver: AssetResolver | None = None,
        standalone: bool = False,
        sidebar: bool = False,
    ) -> None:
        super().__init__(
            quiet,
            asset_resolver,
            standalone,
            source_offsets=source_offsets,
            copy_source=copy_source,
        )
        # The reader sidebar is a build option (`rsm build --sidebar`),
        # independent of whether the author wrote :toc:.
        self.sidebar = sidebar

    @staticmethod
    def _make_option_tag(name: str, svg: str) -> AppendOpenCloseTag:
        return AppendOpenCloseTag(
            "span",
            svg,
            classes=["option", f"option__{name}"],
            newline_inner=False,
        )

    def _hr(
        self,
        include_content: bool,
        depth: int,
        classes: list[str] | None = None,
        node: nodes.Node | None = None,
        extra_attrs: dict | None = None,
    ) -> AppendOpenTag | AppendOpenTagManualClose:
        classes = (classes or []) + ["hr"] + (["hr-offset"] if depth > 0 else [])
        classes = list(dict.fromkeys(classes))  # deletes duplicates AND preserves order

        # Add source data if node is provided
        kwargs = {}
        if extra_attrs:
            kwargs.update(extra_attrs)
        if node is not None and getattr(node, "collapsed", False):
            # Marker only: JS collapses on load, so JS-off keeps the block open.
            kwargs["data-start-collapsed"] = "true"
        # tree-sitter 0.26.0's Point.row/.column getters corrupt memory
        # (py-tree-sitter #472); read row/column by index instead.
        if (
            self.source_offsets
            and node
            and self.tree
            and self.tree.src
            and node.start_point[0] >= 0
        ):
            source_lines = self.tree.src.split("\n")
            start_row, start_col = node.start_point[0], node.start_point[1]
            end_row, end_col = node.end_point[0], node.end_point[1]

            if start_row < len(source_lines) and end_row < len(source_lines):
                start_offset = (
                    sum(len(source_lines[r]) + 1 for r in range(start_row)) + start_col
                )
                end_offset = (
                    sum(len(source_lines[r]) + 1 for r in range(end_row)) + end_col
                )
                kwargs["data-source-start"] = str(start_offset)
                kwargs["data-source-end"] = str(end_offset)

        return (
            AppendOpenTag(classes=classes, is_selectable=True, **kwargs)
            if include_content
            else AppendOpenTagManualClose(classes=classes, is_selectable=True, **kwargs)
        )

    def _hr_collapse_zone(self, collapsible: bool) -> AppendOpenCloseTag:
        if collapsible:
            # A real button so the fold can be worked from the keyboard (Enter or
            # Space when focused) and named for assistive tech, in any build. The
            # standalone build never loads the single-key shortcuts, so this is
            # the only keyboard path to the fold there. The static name is a
            # generic fallback; handrails.js replaces it with the block's own
            # "Show X" / "Hide X" and sets aria-expanded and aria-controls from
            # the live state (it also gives the content zone an id to point at).
            content = f"""
            <button type="button" class="hr-collapse" aria-expanded="true" aria-label="Show or hide this block">
              {self._icon_ref("collapse")}
            </button>
"""
        else:
            content = """<div class="hr-spacer"></div>"""
        return AppendOpenCloseTag(
            tag="div",
            content=content,
            classes=["hr-collapse-zone"],
        )

    def _hr_menu_label(self, label: str) -> str:
        return f"""
  <div class="hr-menu-label">
    <span class="hr-menu-item-text">{label}</span>
  </div>"""

    def _make_menu_item(self, classes: list[str], icon: str, text: str) -> str:
        if classes:
            classes_str = " " + " ".join(classes)
        else:
            classes_str = ""
        return f"""
  <div class="hr-menu-item{classes_str}">
    {self._icon_ref(icon)}
    <span class="hr-menu-item-text">{text}</span>
  </div>"""

    def _hr_menu_sep(self) -> str:
        return '\n\n  <div class="hr-menu-separator"></div>'

    def _hr_menu_item_collapse(self, disabled: bool = False) -> str:
        classes = ["collapse-subproof"] + (["disabled"] if disabled else [])
        return self._make_menu_item(classes, "collapse", "Collapse")

    def _hr_menu_item_collapse_all(self, disabled: bool = False) -> str:
        classes = ["collapse-steps"] + (["disabled"] if disabled else [])
        return self._make_menu_item(classes, "collapse-all", "Collapse all")

    def _hr_menu_item_link(self, disabled: bool = False) -> str:
        classes = ["link"] + (["disabled"] if disabled else [])
        return self._make_menu_item(classes=classes, icon="link", text="Copy link")

    def _hr_menu_item_code(self, disabled: bool = False) -> str:
        return self._make_menu_item(
            classes=(["disabled"] if disabled else []), icon="code", text="Source"
        )

    @staticmethod
    def _menu_data_attrs(
        label: str = "",
        collapse: bool | Literal["disabled"] = False,
        collapse_all: bool | Literal["disabled"] = False,
        link: bool | Literal["disabled"] = True,
        code: bool | Literal["disabled"] = True,
        static_toggle: bool | Literal["disabled"] = False,
        toc_view: bool | Literal["disabled"] = False,
    ) -> dict:
        """Return data attributes encoding the menu configuration."""
        attrs = {}
        if label:
            attrs["data-menu-label"] = label
        if collapse:
            attrs["data-menu-collapse"] = (
                "disabled" if collapse == "disabled" else "true"
            )
        if collapse_all:
            attrs["data-menu-collapse-all"] = (
                "disabled" if collapse_all == "disabled" else "true"
            )
        if link:
            attrs["data-menu-link"] = "disabled" if link == "disabled" else "true"
        if code:
            attrs["data-menu-code"] = "disabled" if code == "disabled" else "true"
        if static_toggle:
            attrs["data-menu-static-toggle"] = (
                "disabled" if static_toggle == "disabled" else "true"
            )
        if toc_view:
            attrs["data-menu-toc-view"] = (
                "disabled" if toc_view == "disabled" else "true"
            )
        return attrs

    def _hr_menu_zone(
        self,
        label: str = "",
        collapse: bool | Literal["disabled"] = False,
        collapse_all: bool | Literal["disabled"] = False,
        link: bool | Literal["disabled"] = True,
        code: bool | Literal["disabled"] = True,
        static_toggle: bool | Literal["disabled"] = False,
        toc_view: bool | Literal["disabled"] = False,
    ) -> tuple[AppendOpenCloseTag, dict]:
        """Return an empty menu zone and data attributes for the singleton menu."""
        attrs = self._menu_data_attrs(
            label, collapse, collapse_all, link, code, static_toggle, toc_view
        )
        zone = AppendOpenCloseTag(tag="div", content="", classes=["hr-menu-zone"])
        return zone, attrs

    def _hr_menu_zone_empty(self) -> AppendOpenCloseTag:
        return AppendOpenCloseTag(tag="div", content="", classes=["hr-menu-zone"])

    def _hr_border_zone(self) -> AppendOpenCloseTag:
        return AppendOpenCloseTag(
            tag="div",
            content=f"""
                <div class="hr-border-dots">
                  {self._icon_ref("dots")}
                </div>
                <div class="hr-border-rect">
                </div>
""",
            classes=["hr-border-zone"],
        )

    def _hr_border_zone_empty(self) -> AppendOpenCloseTag:
        return AppendOpenCloseTag(
            tag="div",
            content='<div class="hr-border-rect"></div>',
            classes=["hr-border-zone"],
        )

    def _hr_spacer_zone(self) -> AppendOpenCloseTag:
        return AppendOpenCloseTag(
            tag="div",
            content="""<div class="hr-spacer"></div>""",
            classes=["hr-spacer-zone"],
        )

    def _hr_content_zone(
        self, include_content: bool, fold_label: str = ""
    ) -> AppendOpenTag | AppendOpenTagManualClose:
        attrs: dict[str, Any] = {"data-fold-label": fold_label} if fold_label else {}
        return (
            AppendOpenTag(classes=["hr-content-zone"], **attrs)
            if include_content
            else AppendOpenTagManualClose(classes=["hr-content-zone"], **attrs)
        )

    @staticmethod
    def _fold_label(node: nodes.Node) -> str:
        """How many steps a folded block hides, as shown at the foot of its handrail.

        A step counts the direct steps in its subproof, any other block its own
        direct steps. Empty when there are none: when the whole body folds away,
        the header and the folded rail already show it.
        """
        body: nodes.Node | None
        if isinstance(node, nodes.Step):
            # Calc rows start folded, so a label under every relation is noise.
            if node.first_ancestor_of_type(nodes.Calc) is not None:
                return ""
            body = node.first_of_type(nodes.Subproof)
            if body is None:
                return ""
        else:
            body = node
        count = sum(isinstance(c, nodes.Step) for c in body.children)
        if not count:
            return ""
        return "1 step hidden" if count == 1 else f"{count} steps hidden"

    def _label_head_with_fold(self, batch: EditCommandBatch, node: nodes.Node) -> None:
        # Labelled blocks show the fold label from their title paragraph, not the
        # content zone: a proof's content-zone ::after already draws its tombstone.
        for item in batch.items:
            if isinstance(item, AppendExternalTree):
                item.root.fold_label = self._fold_label(node)
                return

    def _hr_info_zone_icon(self, icon: str | None) -> AppendOpenCloseTag:
        hr_info_start = """<div class="hr-info">"""
        hr_info_middle = ""
        hr_info_end = "</div>"
        if icon is not None:
            hr_info_middle = f"""
                {self._icon_ref(icon)}
                """
        return AppendOpenCloseTag(
            tag="div",
            content=hr_info_start + hr_info_middle + hr_info_end,
            classes=["hr-info-zone"],
        )

    @staticmethod
    def _info_number(number: int | str | None, style: Literal["eqn", "step"]) -> str:
        if number is None:
            return ""
        if style == "step":
            return f"""<div class="step-number"><p>⟨{number}⟩</p></div>"""
        return f"""<div class="eqn-number"><p>({number})</p></div>"""

    @staticmethod
    def _hr_info_zone(*items: str) -> AppendOpenCloseTag:
        """An info zone holding one cell. Two or more items in one cell stack
        vertically, centred in the column, so nothing on that line overlaps."""
        items = tuple(i for i in items if i)
        classes = "hr-info hr-info-stack" if len(items) > 1 else "hr-info"
        return AppendOpenCloseTag(
            tag="div",
            content=f'<div class="{classes}">{"".join(items)}</div>',
            classes=["hr-info-zone"],
        )

    def _hr_info_zone_number(
        self, number: int | str | None, style: Literal["eqn", "step"]
    ) -> AppendOpenCloseTag:
        return self._hr_info_zone(self._info_number(number, style))

    def _hr_info_zone_disclosure(self, above: str = "") -> AppendOpenCloseTag:
        # A calc relation discloses its justification from the info-zone -- the
        # right-margin, per-row-aligned slot where an equation number would sit --
        # instead of the left gutter. The control is a real .hr-collapse inside a
        # .hr-collapse-zone, so the delegated collapse handler wires it (it resolves
        # the enclosing step via .closest('.hr')); CSS reglyphs it as the because-
        # sign. Presentation choice only; the collapse mechanism is unchanged.
        control = self._hr_collapse_zone(True).make_text()
        return self._hr_info_zone(above, control)

    @staticmethod
    def _leading_mathblock(step: nodes.Step) -> nodes.MathBlock | None:
        """The numbered display equation a step starts with, if any.

        Its number shares the step's info cell, stacked under the step number,
        because both would otherwise sit on the same line of the column.
        """
        statement = step.children[0] if step.children else None
        if not isinstance(statement, nodes.Statement) or not statement.children:
            return None
        first = statement.children[0]
        if (
            isinstance(first, nodes.MathBlock)
            and not first.preamble
            and not first.nonum
        ):
            return first
        return None

    def _hr_from_node(
        self,
        node: nodes.NodeSubType,
        additional_classes: None | list[str] = None,
        is_selectable: bool = True,
        extra_attrs: dict | None = None,
        tag: str = "div",
    ) -> AppendNodeTag:
        classes = (
            (node.classes or [])
            + ["hr"]
            + (["hr-hidden"] if node.handrail_depth == 2 else [])
            + (["hr-offset"] if node.handrail_depth > 0 else [])
            + (additional_classes or [])
        )
        classes = list(dict.fromkeys(classes))  # deletes duplicates AND preserves order
        if getattr(node, "collapsed", False):
            # Marker only: JS collapses on load, so JS-off keeps the block open.
            extra_attrs = {**(extra_attrs or {}), "data-start-collapsed": "true"}
        return AppendNodeTag(
            node,
            tag,
            additional_classes=classes,
            is_selectable=is_selectable,
            include_source=self.source_offsets,
            manuscript_source=self.tree.src if self.tree else "",
            extra_attrs=extra_attrs,
        )

    def _replace_node_with_handrails(
        self,
        node: nodes.Node,
        *,
        additional_classes: None | list[str] = None,
        menu_label: str = "",
        collapse_in_hr: bool = True,
        collapse_in_menu: bool = False,
        collapse_all_in_menu: bool = False,
        extra_attrs: dict | None = None,
    ) -> AppendBatchAndDefer:
        menu_zone, menu_attrs = self._hr_menu_zone(
            label=menu_label or node.reftext,
            collapse=collapse_in_menu,
            collapse_all=collapse_all_in_menu,
            link=(True if node.label else "disabled"),
        )
        merged_attrs = {**menu_attrs, **(extra_attrs or {})}
        handrail = self._hr_from_node(
            node, additional_classes, extra_attrs=merged_attrs
        )
        hr_content_zone = self._hr_content_zone(True)
        newitems = [
            handrail,
            self._hr_collapse_zone(collapse_in_hr),
            menu_zone,
            self._hr_border_zone(),
            self._hr_spacer_zone(),
            hr_content_zone,
        ]
        return AppendBatchAndDefer(newitems)

    def _subproof_handrails(self, node: nodes.Subproof) -> AppendBatchAndDefer:
        newitems = [
            self._hr_from_node(node, ["hr-shift-1"], is_selectable=False),
            self._hr_collapse_zone(False),
            self._hr_menu_zone_empty(),
            self._hr_border_zone_empty(),
            self._hr_spacer_zone(),
            self._hr_content_zone(True),
        ]
        return AppendBatchAndDefer(newitems)

    def _step_handrails(self, node: nodes.Step) -> AppendBatchAndDefer:
        sub: nodes.Subproof | None = node.first_of_type(nodes.Subproof)
        link: bool | Literal["disabled"] = True if node.label else "disabled"
        if sub is None:
            menu_zone, menu_attrs = self._hr_menu_zone(
                label=node.reftext,
                collapse="disabled",
                collapse_all="disabled",
                link=link,
            )
        elif sub and sub.first_of_type(nodes.Step) is None:
            menu_zone, menu_attrs = self._hr_menu_zone(
                label=node.reftext,
                collapse=True,
                collapse_all="disabled",
                link=link,
            )
        else:
            menu_zone, menu_attrs = self._hr_menu_zone(
                label=node.reftext,
                collapse=True,
                collapse_all=True,
                link=link,
            )
        newitems = [
            self._hr_from_node(node, extra_attrs=menu_attrs),
            self._hr_collapse_zone(False),
            menu_zone,
            self._hr_border_zone(),
            self._hr_spacer_zone(),
            self._hr_content_zone(True, fold_label=self._fold_label(node)),
        ]
        return AppendBatchAndDefer(newitems)

    def _wrap_item_with_handrails(
        self,
        index: int,
        items: list,
        cls: type[_BatchT],
        *,
        classes: list[str] | None = None,
        include_content: bool = False,
        icon: str | None = None,
        collapse_in_hr: bool = True,
        depth: int = 0,
        menu_label: str = "",
        link: bool | Literal["disabled"] = True,
        toc_view: bool | Literal["disabled"] = False,
        node: nodes.Node | None = None,
    ) -> _BatchT:
        menu_zone, menu_attrs = self._hr_menu_zone(
            label=menu_label, link=link, toc_view=toc_view
        )
        handrail = self._hr(
            include_content, depth, classes, node=node, extra_attrs=menu_attrs
        )
        hr_content_zone = self._hr_content_zone(include_content)

        newitems = [
            handrail,
            self._hr_collapse_zone(collapse_in_hr),
            menu_zone,
            self._hr_border_zone(),
            self._hr_spacer_zone(),
            hr_content_zone,
            items[index],
        ]

        if not include_content:
            # Without content, _hr and _hr_content_zone return the tags that
            # are closed by hand.
            newitems += [
                cast(AppendOpenTagManualClose, hr_content_zone).close_command(),
                self._hr_info_zone_icon(icon),
                cast(AppendOpenTagManualClose, handrail).close_command(),
            ]
        else:
            # Nothing to do since in this case, everything will close by itself and/or
            # be handlded in the corresponding leave_* method.
            pass

        newitems = items[:index] + newitems + items[index + 1 :]
        return cls(newitems)

    def _wrap_batch_item_with_handrails(
        self,
        index: int,
        batch: _BatchT,
        *,
        include_content: bool = False,
        icon: str | None = None,
        collapse_in_hr: bool = True,
        depth: int = 0,
        classes: list[str] | None = None,
        menu_label: str = "",
        link: bool | Literal["disabled"] = True,
        toc_view: bool | Literal["disabled"] = False,
        node: nodes.Node | None = None,
    ) -> _BatchT:
        return self._wrap_item_with_handrails(
            index,
            batch.items,
            batch.__class__,
            classes=classes,
            include_content=include_content,
            icon=icon,
            collapse_in_hr=collapse_in_hr,
            depth=depth,
            menu_label=menu_label,
            link=link,
            toc_view=toc_view,
            node=node,
        )

    def _wrap_cmd_with_handrails(
        self,
        cmd: EditCommand,
        *,
        include_content: bool = False,
        icon: str | None = None,
        collapse_in_hr: bool = True,
        depth: int = 0,
        classes: list[str] | None = None,
        link: bool | Literal["disabled"] = True,
    ) -> AppendBatchAndDefer:
        return self._wrap_item_with_handrails(
            0,
            [cmd],
            AppendBatchAndDefer,
            classes=classes,
            include_content=include_content,
            icon=icon,
            collapse_in_hr=collapse_in_hr,
            depth=depth,
            link=link,
        )

    def _make_singleton_menu(self) -> AppendText:
        """Emit the single shared menu template with all possible items."""
        html = '<div id="hr-menu-singleton" style="display:none">\n'
        html += '<div class="hr-menu">\n'
        html += '  <div class="hr-menu-label"><span class="hr-menu-item-text" data-role="label"></span></div>\n'
        html += '  <div class="hr-menu-separator" data-role="label-sep"></div>\n'
        html += '  <div class="hr-menu-item collapse-subproof" data-role="collapse">\n'
        html += f"    {self._icon_ref('collapse')}\n"
        html += '    <span class="hr-menu-item-text">Collapse</span>\n'
        html += "  </div>\n"
        html += '  <div class="hr-menu-item collapse-steps" data-role="collapse-all">\n'
        html += f"    {self._icon_ref('collapse-all')}\n"
        html += '    <span class="hr-menu-item-text">Collapse all</span>\n'
        html += "  </div>\n"
        html += '  <div class="hr-menu-separator" data-role="collapse-sep"></div>\n'
        # Keep a block open in the sidebar's Pinned view (only with --sidebar;
        # handrails.js shows it on pinnable blocks).
        html += '  <div class="hr-menu-item pin" data-role="pin">\n'
        html += f"    {self._icon_ref('pin')}\n"
        html += '    <span class="hr-menu-item-text">Pin</span>\n'
        html += "  </div>\n"
        html += '  <div class="hr-menu-item link" data-role="link">\n'
        html += f"    {self._icon_ref('link')}\n"
        html += '    <span class="hr-menu-item-text">Copy link</span>\n'
        html += "  </div>\n"
        html += '  <div class="hr-menu-item" data-role="code">\n'
        html += f"    {self._icon_ref('code')}\n"
        html += '    <span class="hr-menu-item-text">Source</span>\n'
        html += "  </div>\n"
        html += '  <div class="hr-menu-separator" data-role="static-sep"></div>\n'
        html += '  <div class="hr-menu-item" data-role="static-toggle">\n'
        html += f"    {self._icon_ref('image')}\n"
        html += '    <span class="hr-menu-item-text">Static</span>\n'
        html += "  </div>\n"
        html += '  <div class="hr-menu-separator" data-role="toc-view-sep"></div>\n'
        html += '  <div class="hr-menu-item toc-view" data-role="toc-view">\n'
        html += f"    {self._icon_ref('tree')}\n"
        html += '    <span class="hr-menu-item-text">View as tree</span>\n'
        html += "  </div>\n"
        html += '  <div class="hr-menu-separator" data-role="reorder-sep"></div>\n'
        html += '  <div class="hr-menu-item reorder" data-role="reorder" role="button" aria-pressed="false">\n'
        html += f"    {self._icon_ref('reorder')}\n"
        html += '    <span class="hr-menu-item-text">Reorder</span>\n'
        html += "  </div>\n"
        html += '  <div class="hr-menu-separator" data-role="focus-sep"></div>\n'
        html += '  <div class="hr-menu-item focus" data-role="focus" role="button">\n'
        html += f"    {self._icon_ref('focus-2')}\n"
        html += '    <span class="hr-menu-item-text">Focus this step</span>\n'
        html += "  </div>\n"
        html += '  <div class="hr-menu-separator" data-role="deplens-sep"></div>\n'
        html += '  <div class="hr-menu-item deplens-up" data-role="deplens-up" role="button">\n'
        html += f"    {self._icon_ref('deplens-up')}\n"
        html += '    <span class="hr-menu-item-text">Depends on</span>\n'
        html += "  </div>\n"
        html += '  <div class="hr-menu-item deplens-down" data-role="deplens-down" role="button">\n'
        html += f"    {self._icon_ref('deplens-down')}\n"
        html += '    <span class="hr-menu-item-text">Used by</span>\n'
        html += "  </div>\n"
        html += "</div>\n</div>"
        return AppendText(text=html)

    def _make_source_div(self) -> AppendText:
        # Escaped, or any HTML in the source (an :html: or :htmlblock: body)
        # would become live elements in the page a second time. The
        # Source menu item reads the div's textContent, which is the source.
        # Called while translating, after translate() has set self.tree.
        assert self.tree is not None
        src = html_escape(self.tree.src, quote=False)
        return AppendText(text=f'<div class="rsm-source hide">{src}</div>')

    # The sidebar's views: (id, name, scope, sub-tab, hint). The scope and
    # sub-tab select the rail's panel (prooftree.js keys its classes off them);
    # the hint says what the view shows.
    # Each hint fits one line in the 17rem desktop panel.
    _RAIL_VIEWS = {
        "contents": ("Contents", "document", "doc-map", ""),
        "notation": (
            "Notation",
            "document",
            "notation",
            "Rename a symbol to change it everywhere.",
        ),
        "steps": (
            "Proof steps",
            "proof",
            "proof-map",
            "Each step and the earlier steps it uses.",
        ),
        "state": (
            "Proof state",
            "proof",
            "state",
            "Assumed and left to prove at this step.",
        ),
        "pinned": ("Pinned", "pinned", "", "A pinned block, kept beside the text."),
        "reading": (
            "Reading",
            "reading",
            "",
            "Typeface, size, spacing, theme and the map.",
        ),
    }

    def _rail_toc_list(self) -> str:
        """The sidebar's Contents list: the same entries, links and markup as
        the list in the page's :toc:, built from the sections directly since
        the document may have no :toc:."""
        children: dict[int | None, list[nodes.Section]] = {}
        # Called while translating, after translate() has set self.tree.
        assert self.tree is not None
        for sec in self.tree.traverse(nodeclass=nodes.Section):
            parent = sec.parent
            while parent is not None and not isinstance(parent, nodes.Section):
                parent = parent.parent
            children.setdefault(id(parent) if parent else None, []).append(sec)

        def items(key: int | None) -> str:
            out = []
            for sec in children.get(key, []):
                text = sec.title if sec.nonum else f"{sec.full_number}. {sec.title}"
                nested = (
                    f'<ul class="itemize">{items(id(sec))}</ul>'
                    if id(sec) in children
                    else ""
                )
                out.append(
                    '<li class="item"><a class="reference" '
                    f'href="#{html_escape(_section_anchor_id(sec))}">'
                    f"{_wrap_hyphenated_words(html_escape(text, quote=False))}</a>{nested}</li>"
                )
            return "".join(out)

        return f'<ul class="contents">{items(None)}</ul>'

    def _make_proof_rail(self) -> AppendText:
        """The reader sidebar: an icon strip in the left margin and the panel it
        opens. The panel holds the section graph and Notation (Document scope),
        one pre-rendered step graph and state per proof (Proof scope, followed by
        prooftree.js as the reader scrolls), a pinned excerpt, and the Reading
        settings.

        The sidebar is a build option (`rsm build --sidebar`), independent of
        :toc:. On wide windows the strip holds one icon per view; on phones it
        becomes a bottom bar with one button per scope, and a scope with two
        views switches between them with text tabs.
        """
        if not getattr(self, "sidebar", False):
            return AppendText(text="")
        from html import escape

        # Called while translating, after translate() has set self.tree.
        assert self.tree is not None
        graph = getattr(self.tree, "section_graph", None)
        has_contents = bool(graph is not None and graph.tree_nodes)
        has_notation = (
            next(iter(self.tree.traverse(nodeclass=nodes.Notation)), None) is not None
        )

        # The sidebar starts in the author's :toc: view, or as a graph when the
        # document has no :toc:. prooftree.js restores the reader's own choice.
        toc = next(iter(self.tree.traverse(nodeclass=nodes.Contents)), None)
        rail_tree = toc is None or toc.view == "tree"
        doc_panels = []
        if has_contents:
            # has_contents is true only when graph is set.
            assert graph is not None
            doc_panels.append(
                f'<div class="rail-panel rail-doc-map{" tree" if rail_tree else ""}">'
                f"{self._toc_tree_svg(graph)}{self._rail_toc_list()}</div>"
            )
        if has_notation:
            doc_panels.append('<div class="rail-panel rail-notation"></div>')

        # Proof scope: one pre-rendered step-tree (and its state) per proof,
        # auto-followed by prooftree.js as the reader scrolls.
        proof_items = []
        proof_links = []
        for proof in self.tree.traverse(nodeclass=nodes.Proof):
            if not proof.tree_nodes:
                continue
            proof_links.append(self._rail_proof_link(proof))
            svg = self._build_tree_svg(
                proof.tree_nodes,
                proof.tree_edges,
                proof.tree_root_title,
                "Proof step dependency graph",
                orient="horizontal",
                bracket_nums=True,
                root_label="Goal",
            )
            proof_items.append(
                self._rail_item(
                    str(proof.nodeid),
                    svg,
                    proofmodel.serialize_state(proof),
                    proof.tree_root_title,
                    len(proof.tree_nodes),
                )
            )
        has_proofs = bool(proof_items)

        # ---- the strip ----
        def strip_btn(view: str, icon: str, mode: str, name: str | None = None) -> str:
            name = name or self._RAIL_VIEWS[view][0]
            hint = self._RAIL_VIEWS[view][3] if view in self._RAIL_VIEWS else ""
            hint_attr = f' data-hint="{escape(hint)}"' if hint else ""
            return (
                f'<button type="button" class="rail-strip-btn" data-view="{view}" '
                f'data-mode="{mode}" aria-pressed="false" aria-controls="rsm-sidebar" '
                f'aria-label="{escape(name)}" data-tip="{escape(name)}"{hint_attr}>{icon}'
                f'<span class="rail-strip-label" aria-hidden="true">{escape(name)}</span>'
                "</button>"
            )

        sep = (
            '<span class="rail-strip-sep" data-mode="split" aria-hidden="true"></span>'
        )
        groups = []
        doc_btns = []
        if has_contents:
            doc_btns.append(strip_btn("contents", _RAIL_CONTENTS_ICON, "split"))
        if has_notation:
            doc_btns.append(strip_btn("notation", _RAIL_NOTATION_ICON, "split"))
        if doc_btns:
            doc_btns.append(
                strip_btn(
                    "document",
                    _RAIL_CONTENTS_ICON if has_contents else _RAIL_NOTATION_ICON,
                    "grouped",
                    "Document",
                )
            )
            groups.append("".join(doc_btns))
        if has_proofs:
            groups.append(
                strip_btn("steps", _RAIL_STEPS_ICON, "split")
                + strip_btn("state", _RAIL_STATE_ICON, "split")
                + strip_btn("proof", _RAIL_STEPS_ICON, "grouped", "Proof")
            )
        else:
            # Shown but disabled, so a reader learns the sidebar has a Proof view
            # and why it is unavailable here. No data-view, so sidebar.js treats
            # it as absent (never opens it, never restores it).
            tip = "This document has no structured proofs"
            groups.append(
                "".join(
                    f'<button type="button" class="rail-strip-btn" data-mode="{mode}" '
                    f'aria-disabled="true" aria-label="{escape(name)}: {tip}" '
                    f'data-tip="{tip}">{icon}'
                    f'<span class="rail-strip-label" aria-hidden="true">{escape(name)}</span>'
                    "</button>"
                    for name, icon, mode in (
                        (self._RAIL_VIEWS["steps"][0], _RAIL_STEPS_ICON, "split"),
                        (self._RAIL_VIEWS["state"][0], _RAIL_STATE_ICON, "split"),
                        ("Proof", _RAIL_STEPS_ICON, "grouped"),
                    )
                )
            )
        groups.append(
            strip_btn("pinned", _RAIL_PIN_ICON, "both")
            + strip_btn("reading", _RAIL_READING_ICON, "both")
        )
        # A document-global action: copy a link that reopens the manuscript with
        # the reader's current view (folds, reorder, ...). Distinct from the
        # per-block "Copy link" anchor; shareview.js binds .rail-share-view.
        share = (
            '<button type="button" class="rail-strip-btn rail-strip-action rail-share-view" '
            'data-mode="both" aria-label="Copy a link to this view" '
            'data-tip="Copy a link to this view">'
            + _RAIL_SHARE_ICON
            + '<span class="rail-strip-label" aria-hidden="true">Copy link</span></button>'
        )
        groups.append(share)
        # The strip's buttons are the first tab stops on the page, before any
        # text. A skip link, hidden until focused, is placed ahead of them so a
        # keyboard reader can jump straight to the manuscript (WCAG 2.4.1). It
        # targets the content wrapper (id rsm-content, tabindex=-1), which sits
        # after the strip, so focus lands in the text. Works with scripting off.
        skip = '<a class="rsm-skip-link" href="#rsm-content">Skip to the text</a>'
        strip = (
            skip
            + '<nav class="rail-strip" aria-label="Sidebar">'
            + sep.join(groups)
            + "</nav>"
        )

        # ---- the panel ----
        def subtabs(scope: str, views: list[str], labels: list[str]) -> str:
            if len(views) < 2:
                return ""
            tabs = []
            for i, (view, label) in enumerate(zip(views, labels, strict=True)):
                tab = self._RAIL_VIEWS[view][2]
                hint = self._RAIL_VIEWS[view][3]
                on = "true" if i == 0 else "false"
                tabs.append(
                    f'<button type="button" role="tab" class="rail-tab{" active" if i == 0 else ""}" '
                    f'data-view="{tab}" aria-selected="{on}" tabindex="{0 if i == 0 else -1}" '
                    f'data-hint="{escape(hint)}">{escape(label)}</button>'
                )
            return (
                f'<div class="rail-subtabs rail-subtabs-{scope}" role="tablist" '
                f'aria-label="{scope.capitalize()}">' + "".join(tabs) + "</div>"
            )

        doc_views = (["contents"] if has_contents else []) + (
            ["notation"] if has_notation else []
        )
        head = (
            '<div class="rail-head">'
            + subtabs(
                "document", doc_views, [self._RAIL_VIEWS[v][0] for v in doc_views]
            )
            + (
                subtabs("proof", ["steps", "state"], ["Steps", "State"])
                if has_proofs
                else ""
            )
            + '<p class="rail-title" role="heading" aria-level="2"></p>'
            + (_toc_switch(rail_tree, "rail-toc-switch") if has_contents else "")
            + '<p class="rail-hint"></p></div>'
        )
        document_section = (
            '<div class="rail-section rail-document">' + "".join(doc_panels) + "</div>"
        )
        proof_section = (
            '<div class="rail-section rail-proof">'
            '<div class="rail-proof-empty">'
            '<p class="rail-proof-empty-hint">No proof selected.</p>'
            '<p class="rail-proof-list-head">Proofs in this document</p>'
            '<ul class="rail-proof-list">'
            + "".join(proof_links)
            + "</ul></div>"
            + "".join(proof_items)
            + "</div>"
        )
        # Holds the pinned blocks, newest first (filled by prooftree.js from a
        # reference preview's pin, or a block's handrail menu). Empty when built.
        pinned_section = (
            '<div class="rail-section rail-pinned">'
            '<div class="rail-pinned-empty">'
            "Nothing pinned yet.</div>"
            '<div class="rail-pinned-body"></div>'
            "</div>"
        )
        doc_view = "map" if has_contents else "notation"
        scope = "document" if doc_panels else ("proof" if has_proofs else "reading")
        panel = (
            f'<div id="rsm-sidebar" class="proof-rail scope-{scope} doc-view-{doc_view} '
            f'proof-view-map{"" if has_proofs else " no-proofs"}" role="complementary" '
            'aria-label="Sidebar">'
            + head
            + document_section
            + proof_section
            + pinned_section
            + _make_reading_panel(
                "serif"
                if getattr(self.tree, "typography", "sans-serif") == "serif"
                else "sans",
                minimap=minimap_enabled(self.tree),
            )
            + "</div>"
        )
        return AppendText(text=strip + panel)

    @staticmethod
    def _rail_proof_link(proof: nodes.Proof) -> str:
        """One row of the Proof panel's list: the proof's name, section and steps."""
        from html import escape

        target = proof.label or f"n{proof.nodeid}"
        anc = proof.parent
        while anc is not None and not isinstance(anc, nodes.Section):
            anc = anc.parent
        where = (
            f"\u00a7{anc.full_number}" if anc is not None and anc.full_number else ""
        )
        n = proof.num_steps
        steps = f"{n} step{'' if n == 1 else 's'}" if n else ""
        meta = " \u00b7 ".join(x for x in (where, steps) if x)
        return (
            f'<li><a class="rail-proof-link" href="#{escape(target)}" '
            f'data-proof="{proof.nodeid}">'
            f'<span class="rail-proof-name">Proof of {escape(proof.tree_root_title)}</span>'
            + (f'<span class="rail-proof-meta">{meta}</span>' if meta else "")
            + "</a></li>"
        )

    def _rail_item(
        self,
        key: str,
        svg: str,
        step_state: list[dict[str, Any]] | None,
        root_title: str,
        step_count: int,
    ) -> str:
        from html import escape

        data = ""
        if step_state is not None:
            import json

            data = (
                '<script type="application/json" class="rail-state-data">'
                + json.dumps(step_state)
                + "</script>"
            )
        # Shown by prooftree.js when the followed proof is collapsed: a single
        # node standing for the proof, so the rail never asserts a step graph the
        # body is hiding. The card itself expands the proof in the body.
        plural = "" if step_count == 1 else "s"
        collapsed_card = (
            f'<button class="rail-panel rail-collapsed-card rail-expand-proof" '
            f'type="button" data-proof="{key}" aria-expanded="false" '
            f'data-tip="Expand this proof to navigate its steps">'
            f'<span class="rail-collapsed-title">{escape(root_title)}</span>'
            f'<span class="rail-collapsed-meta">{step_count} step{plural} hidden</span>'
            f'<span class="rail-collapsed-cue">Expand to navigate</span>'
            "</button>"
        )
        return (
            f'<div class="proof-rail-item" data-proof="{key}">'
            f'<div class="rail-panel rail-map">{svg}</div>'
            f'<div class="rail-panel rail-state"></div>'
            f"{collapsed_card}{data}</div>"
        )

    def _make_svg_defs(self) -> AppendText:
        """Emit a single <svg> block with <symbol> definitions for all icons."""
        symbols = []
        for name, svg_str in self.svg.items():
            # Extract the inner content (paths) and viewBox from the SVG string
            import re

            # Extract presentation attributes from the <svg> tag
            svg_tag = re.match(r"<svg([^>]*)>", svg_str)
            attrs_str = svg_tag.group(1) if svg_tag else ""
            vb_match = re.search(r'viewBox="([^"]*)"', attrs_str)
            viewBox = vb_match.group(1) if vb_match else "0 0 18 18"
            # Preserve fill, stroke, stroke-width, stroke-linecap, stroke-linejoin
            pres_attrs = ""
            for attr in (
                "fill",
                "stroke",
                "stroke-width",
                "stroke-linecap",
                "stroke-linejoin",
            ):
                m = re.search(rf'{attr}="([^"]*)"', attrs_str)
                if m:
                    pres_attrs += f' {attr}="{m.group(1)}"'
            # Extract child elements (paths etc.)
            inner = re.sub(r"<svg[^>]*>", "", svg_str)
            inner = re.sub(r"</svg>", "", inner).strip()
            symbols.append(
                f'<symbol id="hr-icon-{name}" viewBox="{viewBox}"{pres_attrs}>{inner}</symbol>'
            )
        defs_html = (
            '<svg id="hr-icon-defs" style="display:none"><defs id="hr-icon-defs">'
            + "\n".join(symbols)
            + "</defs></svg>"
        )
        return AppendText(text=defs_html)

    def visit_manuscript(self, node: nodes.Manuscript) -> AppendBatchAndDefer:
        batch = super().visit_manuscript(node)
        if node.title:
            # The title follows the eyebrow, when there is one.
            title_index = 5 if node.eyebrow else 4
            batch = self._wrap_batch_item_with_handrails(
                title_index,
                batch,
                classes=["heading"],
                menu_label="Title",
                link=True,
                node=node,
            )
        if getattr(self, "sidebar", False):
            # The skip link (emitted by _make_proof_rail, before the strip) lands
            # the reader here, past the strip's buttons. tabindex=-1 lets focus
            # move to this wrapper without adding it to the tab order.
            content_tag = batch.items[2]
            content_tag.id = "rsm-content"
            content_tag.custom_attrs["tabindex"] = "-1"
        batch.items.insert(2, self._make_svg_defs())
        batch.items.insert(3, self._make_singleton_menu())
        batch.items.insert(3, self._make_proof_rail())
        if self.copy_source:
            batch.items.insert(3, self._make_source_div())
        return batch

    def visit_author(self, node: nodes.Author) -> EditCommand:
        return super().visit_author(node)

    def leave_author(self, node: nodes.Author) -> EditCommand:
        return super().leave_author(node)

    def visit_authorblock(self, node: nodes.AuthorBlock) -> AppendBatchAndDefer:
        batch = super().visit_authorblock(node)
        # With no hidden names and no details there is nothing to open, so the
        # block gets no chevron.
        batch = self._wrap_batch_item_with_handrails(
            1,
            batch,
            classes=["heading", "hr-hidden"],
            link="disabled",
            node=node,
            collapse_in_hr=self._author_block_opens,
        )
        return batch

    def leave_authorblock(self, node: nodes.AuthorBlock) -> EditCommand:
        return super().leave_authorblock(node)

    def visit_section(self, node: nodes.Section) -> AppendBatchAndDefer:
        batch = super().visit_section(node)
        return self._wrap_batch_item_with_handrails(
            1,
            batch,
            icon=getattr(node, "icon", None),
            classes=["heading"],
            menu_label=node.reftext,
            link=True if node.label else "disabled",
            node=node,
        )

    def visit_abstract(self, node: nodes.Abstract) -> AppendBatchAndDefer:
        batch = super().visit_abstract(node)
        return self._wrap_batch_item_with_handrails(
            1,
            batch,
            classes=["heading"],
            menu_label=node.reftext,
            link=True if node.label else "disabled",
            node=node,
        )

    def visit_contents(self, node: nodes.Contents) -> AppendBatchAndDefer:
        batch = super().visit_contents(node)
        batch = self._wrap_batch_item_with_handrails(
            1,
            batch,
            classes=["heading"],
            menu_label=node.reftext,
            link=True if node.label else "disabled",
            toc_view=True,
            node=node,
        )
        return batch

    def visit_bibliography(self, node: nodes.Bibliography) -> AppendBatchAndDefer:
        batch = super().visit_bibliography(node)
        batch.items[2] = AppendNodeTag(node, "div")
        return self._wrap_batch_item_with_handrails(
            1,
            batch,
            classes=["heading"],
            menu_label=node.reftext,
            link=True if node.label else "disabled",
            node=node,
        )

    def visit_noteslist(self, node: nodes.NotesList) -> AppendBatchAndDefer:
        batch = super().visit_noteslist(node)
        return self._wrap_batch_item_with_handrails(
            1,
            batch,
            classes=["heading"],
            menu_label="Notes",
            link="disabled",
            node=node,
        )

    def visit_paragraph(self, node: nodes.Paragraph) -> AppendBatchAndDefer:
        cmd = super().visit_paragraph(node)
        if _in_paragraph_asset(node) or node.wraps_block:
            return cmd
        batch = self._replace_node_with_handrails(node, collapse_in_hr=False)
        if "hr-hidden" not in batch.items[0].classes:
            batch.items[0].classes.append("hr-hidden")
        batch = AppendBatchAndDefer([*batch.items, *cmd.items[1:]])
        return batch

    def leave_paragraph(self, node: nodes.Paragraph) -> EditCommandBatch:
        # For documentation: if a visit_* method returns a command with defers = True,
        # then the corresponding leave_* method MUST MUST MUST call leave_node(node) and
        # add it to the returned batch!!!
        batch = super().leave_paragraph(node)
        if _in_paragraph_asset(node) or node.wraps_block:
            return batch
        batch.items.insert(-1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        return batch

    def visit_aside(self, node: nodes.Aside) -> EditCommand:
        # An aside inside the block that calls it is covered by that block's
        # handrail and needs no alignment wrapper.
        if isinstance(node.parent, (nodes.Paragraph, nodes.Item)):
            return super().visit_aside(node)
        return self.visit_note(node)

    def visit_note(self, node: nodes.Note) -> AppendBatchAndDefer:
        # A note or aside definition gets no handrail of its own. It sits inside a
        # chromeless alignment handrail (as asset bodies do) so its text lines up
        # with the paragraphs around it.
        cmd = super().visit_note(node)
        bare = "hr hr-bare" + (" hr-offset" if node.handrail_depth > 0 else "")
        wrapper = AppendTextAndDefer(
            f'<div class="{bare}">'
            + self._hr_collapse_zone(collapsible=False).make_text()
            + self._hr_menu_zone_empty().make_text()
            + self._hr_border_zone_empty().make_text()
            + self._hr_spacer_zone().make_text()
            + '<div class="hr-content-zone">',
            "</div>" + self._hr_info_zone_icon(None).make_text() + "</div>",
        )
        return AppendBatchAndDefer([cmd.items[0], wrapper, *cmd.items[1:]])

    def _asset_handrails(
        self, node: nodes.Asset, with_fallback: bool = True
    ) -> AppendBatchAndDefer:
        if node.as_paragraph:
            return self._paragraph_asset_handrails(node, with_fallback)
        # A plain <figure> holds the asset body wrapped in a chromeless alignment
        # handrail (no menu, no visible bar, no info zone, not focusable) so the
        # body lines up with the reading column. The caption is a sibling child
        # that keeps its own on-hover handrail at the same depth, so the two align.
        # The body handrail is literal HTML so it closes before the caption while
        # the <figure> stays open (deferred) to receive the caption.
        body_classes = "hr hr-bare" + (" hr-offset" if node.handrail_depth > 0 else "")
        inner = self._detect_content_type_and_render(node)
        if with_fallback:
            inner += self._static_fallback_img(node)
        body = (
            f'<div class="{body_classes}">'
            + self._hr_collapse_zone(collapsible=False).make_text()
            + self._hr_menu_zone_empty().make_text()
            + self._hr_border_zone_empty().make_text()
            + self._hr_spacer_zone().make_text()
            + '<div class="hr-content-zone">'
            + inner
            + "</div>"
            # Empty info zone so the body reserves the right gutter exactly like a
            # paragraph, aligning the asset with prose and its caption on the right.
            + self._hr_info_zone_icon(None).make_text()
            + "</div>"
        )
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, "figure", additional_classes=_asset_classes(node)),
                AppendText(body),
            ]
        )

    def _paragraph_asset_handrails(
        self, node: nodes.Asset, with_fallback: bool
    ) -> AppendBatchAndDefer:
        # The <figure> is itself the handrail, with the classes a paragraph at the
        # same depth gets, because it has no caption to carry the menu. Its
        # rendered content and any body (such as an :htmlblock:) share the one
        # content zone, which is where the static toggle swaps them for the
        # fallback.
        menu_zone, menu_attrs = self._hr_menu_zone(
            label=node.kindname,
            link=(True if node.label else "disabled"),
            static_toggle=(True if with_fallback and node.static else "disabled"),
        )
        inner = self._detect_content_type_and_render(node)
        if with_fallback:
            inner += self._static_fallback_img(node)
        return AppendBatchAndDefer(
            [
                self._hr_from_node(
                    node,
                    ["hr-hidden", *_asset_classes(node)],
                    extra_attrs=menu_attrs,
                    tag="figure",
                ),
                self._hr_collapse_zone(False),
                menu_zone,
                self._hr_border_zone(),
                self._hr_spacer_zone(),
                self._hr_content_zone(True),
                AppendText(inner),
            ]
        )

    def _leave_asset(self, node: nodes.Asset) -> EditCommand:
        # The visit method deferred a batch, so leave_node returns one.
        batch = cast(EditCommandBatch, self.leave_node(node))
        if node.as_paragraph:
            batch.items.insert(-1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        return batch

    def visit_figure(self, node: nodes.Figure) -> EditCommand:
        return self._asset_handrails(node)

    def leave_figure(self, node: nodes.Figure) -> EditCommand:
        return self._leave_asset(node)

    def visit_video(self, node: nodes.Video) -> EditCommand:
        return self._asset_handrails(node, with_fallback=False)

    def leave_video(self, node: nodes.Video) -> EditCommand:
        return self._leave_asset(node)

    def visit_caption(self, node: nodes.Caption) -> EditCommand:
        parent = node.parent
        # A caption is always inside the block that it captions.
        assert parent is not None
        caption_label = _caption_label(parent, self)

        # Create figcaption with handrail classes
        figcaption_classes = ["hr", "hr-hidden"]
        additional_classes = (["hr-hidden"] if node.handrail_depth == 2 else []) + (
            ["hr-offset"] if node.handrail_depth > 0 else []
        )
        figcaption_classes.extend(additional_classes)

        use_figcaption = isinstance(parent, (nodes.Asset, nodes.Table, nodes.CodeBlock))
        items: list[EditCommand] = []
        if isinstance(parent, nodes.Table):
            items.append(AppendText("\n</table>\n"))
        if isinstance(parent, nodes.CodeBlock):
            # Close the code's bare handrail, opened in visit_codeblock.
            items.append(
                AppendText(
                    "</pre>\n</div>\n"
                    + self._hr_info_zone_icon(None).make_text()
                    + "</div>\n"
                )
            )
            if self._terminal_block_in_p(parent):
                figcaption_classes.append("hr-offset")
        has_static = isinstance(parent, nodes.Asset) and parent.static
        # The rail names the captioned block ("Figure", "Video", "Table"), the
        # same word the caption's own label starts with.
        kind = parent.classreftext.format(nodeclass=parent.kindname, number="").strip()
        menu_zone, menu_attrs = self._hr_menu_zone(
            label=kind,
            link=(True if node.label else "disabled"),
            static_toggle=(True if has_static else "disabled"),
        )
        items.extend(
            [
                AppendOpenTag(
                    "figcaption" if use_figcaption else "caption",
                    classes=figcaption_classes,
                    is_selectable=True,
                    tabindex=0,
                    **menu_attrs,
                ),
                self._hr_collapse_zone(collapsible=False),
                menu_zone,
                self._hr_border_zone(),
                self._hr_spacer_zone(),
                AppendOpenTagManualClose("div", classes=["hr-content-zone"]),
                caption_label,
            ]
        )
        return AppendBatchAndDefer(items)

    def leave_caption(self, node: nodes.Caption) -> EditCommand:
        # The visit method deferred a batch, so leave_node returns one.
        batch = cast(EditCommandBatch, self.leave_node(node))
        # Close hr-content-zone, add hr-info-zone, then close figcaption
        batch.items = [
            AppendText("</div>"),  # Close hr-content-zone
            self._hr_info_zone_icon(getattr(node, "icon", None)),
            *batch.items,  # This includes the closing figcaption tag
        ]
        return batch

    def visit_codeblock(self, node: nodes.CodeBlock) -> AppendBatchAndDefer:
        if _has_caption(node):
            return self._captioned_codeblock_handrails(node)
        # The menu names the kind of block, as a caption's menu does.
        batch = self._replace_node_with_handrails(
            node, collapse_in_hr=False, menu_label=node.kindname
        )
        close_p = self._close_p_before(node)
        batch.items[:0] = close_p
        handrail_idx = len(close_p)
        offset_class = (
            ["hr-offset"]
            if isinstance(node.parent, (nodes.Paragraph, nodes.Note))
            and not _wraps_block(node.parent)
            else []
        )
        batch.items[handrail_idx].classes += ["hr-hidden"] + offset_class
        batch.items.append(AppendOpenTag("pre"))
        return AppendBatchAndDefer(batch.items)

    def _captioned_codeblock_handrails(
        self, node: nodes.CodeBlock
    ) -> AppendBatchAndDefer:
        # Laid out as a figure (see _asset_handrails): a plain <figure> holds the
        # code in a bare handrail, and the caption after it carries the menu.
        # visit_caption closes the bare handrail.
        offset = self._terminal_block_in_p(node)
        body_classes = "hr hr-bare" + (" hr-offset" if offset else "")
        body = (
            f'<div class="{body_classes}">'
            + self._hr_collapse_zone(collapsible=False).make_text()
            + self._hr_menu_zone_empty().make_text()
            + self._hr_border_zone_empty().make_text()
            + self._hr_spacer_zone().make_text()
            + '<div class="hr-content-zone">\n<pre>'
        )
        return AppendBatchAndDefer(
            [
                *self._close_p_before(node),
                AppendNodeTag(node, "figure"),
                AppendText(body),
            ]
        )

    @auto_leave_deferred
    def leave_codeblock(
        self, node: nodes.CodeBlock, base_batch: EditCommandBatch
    ) -> EditCommand:
        if not _has_caption(node):
            base_batch.items.insert(
                -1, self._hr_info_zone_icon(getattr(node, "icon", None))
            )
        return self._reopen_p_after(node, base_batch)

    def visit_algorithm(self, node: nodes.Algorithm) -> AppendBatchAndDefer:
        batch = self._replace_node_with_handrails(
            node,
            collapse_in_hr=False,
            extra_attrs={"data-caption-name": _caption_name(node)},
        )
        if "hr-hidden" not in batch.items[0].classes:
            batch.items[0].classes.append("hr-hidden")
        # Inside a paragraph, an algorithm gets the same offset as display math.
        if (
            self._terminal_block_in_p(node)
            and "hr-offset" not in batch.items[0].classes
        ):
            batch.items[0].classes.append("hr-offset")
        return AppendBatchAndDefer(
            [
                *self._close_p_before(node),
                *batch.items,
                AppendOpenTag("pre", classes=["pseudocode"]),
            ]
        )

    @auto_leave_deferred
    def leave_algorithm(
        self, node: nodes.Algorithm, base_batch: EditCommandBatch
    ) -> EditCommand:
        base_batch.items.insert(
            -1, self._hr_info_zone_icon(getattr(node, "icon", None))
        )
        return self._reopen_p_after(node, base_batch)

    def visit_theorem(self, node: nodes.Theorem) -> AppendBatchAndDefer:
        batch = super().visit_theorem(node)
        self._label_head_with_fold(batch, node)
        hr = self._replace_node_with_handrails(node, additional_classes=["hr-labeled"])
        hr.items += batch.items[1:]
        return hr

    @auto_leave_deferred
    def leave_theorem(
        self, node: nodes.Theorem, base_batch: EditCommandBatch
    ) -> EditCommand:
        base_batch.items.insert(1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        return AppendBatch(base_batch.items)

    def visit_sketch(self, node: nodes.Sketch) -> AppendBatchAndDefer:
        batch = super().visit_sketch(node)
        self._label_head_with_fold(batch, node)
        hr = self._replace_node_with_handrails(node, additional_classes=["hr-labeled"])
        hr.items += batch.items[1:]
        return hr

    def leave_sketch(self, node: nodes.Sketch) -> EditCommand:
        # The visit method deferred a batch, so leave_node returns one.
        batch = cast(EditCommandBatch, self.leave_node(node))
        batch.items.insert(1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        batch = AppendBatch(batch.items)
        return batch

    def visit_proof(self, node: nodes.Proof) -> AppendBatchAndDefer:
        batch = super().visit_proof(node)
        self._label_head_with_fold(batch, node)
        # Stamp the proof with the label of the result it proves, so the reader's
        # dependency lens can aggregate a result-level graph (which result rests
        # on which) from the per-proof citation graphs. Uses the same association
        # the proof model uses: an explicit :of:, else the nearest preceding
        # theorem-like sibling. Distinct from the "Proof of ..." title, which
        # still keys only off an explicit :of: and is left unchanged.
        of_label = self._proved_result_label(node)
        extra_attrs = {}
        if of_label:
            extra_attrs["data-of"] = of_label
        # The folded step count lives on the handrail box here. The base tag it
        # would otherwise ride is dropped when handrails wrap the node.
        if node.num_steps:
            extra_attrs["data-steps"] = str(node.num_steps)
        hr = self._replace_node_with_handrails(
            node,
            additional_classes=["hr-labeled"],
            collapse_all_in_menu=True,
            extra_attrs=extra_attrs or None,
        )
        hr.items += batch.items[1:]
        return hr

    @staticmethod
    def _proved_result_label(proof: nodes.Proof) -> str:
        declared = getattr(proof, "proves", None)
        if declared is not None:
            return declared.label or ""
        theorem_types = (
            nodes.Theorem,
            nodes.Lemma,
            nodes.Corollary,
            nodes.Proposition,
            nodes.Statement,
        )
        sib = proof.prev_sibling()
        while sib is not None:
            if isinstance(sib, theorem_types):
                return sib.label or ""
            sib = sib.prev_sibling()
        return ""

    @auto_leave_deferred
    def leave_proof(
        self, node: nodes.Proof, base_batch: EditCommandBatch
    ) -> EditCommand:
        base_batch.items.insert(1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        return AppendBatch(base_batch.items)

    def visit_subproof(self, node: nodes.Subproof) -> EditCommand:
        hr = self._subproof_handrails(node)
        try:
            hr.items[0].classes.remove("hr-hidden")
        except ValueError:
            pass
        return hr

    def leave_subproof(self, node: nodes.Subproof) -> EditCommand:
        # The visit method deferred a batch, so leave_node returns one.
        batch = cast(EditCommandBatch, self.leave_node(node))
        batch.items.insert(1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        batch = AppendBatch(batch.items)
        return batch

    def visit_calc(self, node: nodes.Calc) -> AppendBatchAndDefer:
        # The chain gets a handrail of its own, like a display equation. At the
        # top level that puts it on the text column. Inside a proof its depth
        # makes it an offset handrail, which keeps its place among the steps.
        self._fold_calc_rows(node)
        batch = self._replace_node_with_handrails(
            node,
            collapse_in_hr=False,
            menu_label="Equation" if node.nonum else node.long_reftext,
        )
        batch.items[0].classes.append("hr-hidden")
        return batch

    @auto_leave_deferred
    def leave_calc(self, node: nodes.Calc, base_batch: EditCommandBatch) -> EditCommand:
        if node.first_ancestor_of_type(nodes.Proof) is not None:
            base_batch.items.insert(0, AppendHalmos())
            idx = 2
        else:
            idx = 1
        # The chain's number is shown in its first row's info cell (leave_step),
        # so the chain's own cell stays empty.
        base_batch.items.insert(idx, self._hr_info_zone())
        return AppendBatch(base_batch.items)

    def visit_step(self, node: nodes.Step) -> EditCommand:
        if mathblock := self._leading_mathblock(node):
            mathblock._number_in_step = True
        hr = self._step_handrails(node)
        return hr

    def leave_step(self, node: nodes.Step) -> EditCommand:
        # The visit method deferred a batch, so leave_node returns one.
        batch = cast(EditCommandBatch, self.leave_node(node))
        if node.first_ancestor_of_type(nodes.Calc) is not None:
            calc = node.parent
            # The step has a Calc ancestor, so it has a parent.
            assert calc is not None
            above = ""
            if node.in_calc and not calc.nonum and calc.children[0] is node:
                above = self._info_number(calc.full_number, "eqn")
            info = self._hr_info_zone_disclosure(above)
        else:
            mathblock = self._leading_mathblock(node)
            info = self._hr_info_zone(
                self._info_number(node.full_number, "step"),
                self._info_number(mathblock.full_number, "eqn") if mathblock else "",
            )
        batch.items.insert(1, info)
        batch = AppendBatch(batch.items)
        return batch

    def visit_math(self, node: nodes.Math) -> AppendBatchAndDefer:
        batch = super().visit_math(node)
        sib = node.next_sibling()
        if not isinstance(sib, nodes.Text):
            return batch
        if not sib.text or sib.text[0] not in self._TRAILING_PUNCT:
            return batch

        # Wrap the math and the trailing punctuation character in a span so the
        # browser cannot break the line between them.
        node._trailing_punct = sib.text[0]
        batch.items.insert(
            0,
            AppendOpenTagManualClose(
                tag="span",
                classes=["inline-wrapper"],
                newline_inner=False,
                newline_outer=False,
            ),
        )
        sib.text = sib.text[1:]
        return batch

    def leave_math(self, node: nodes.Math) -> EditCommand:
        # The visit method deferred a batch, so leave_node returns one.
        batch = cast(EditCommandBatch, self.leave_node(node))
        punct = getattr(node, "_trailing_punct", None)
        if not punct:
            return batch
        escaped = punct.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        batch.items.extend(
            [AppendText(f"<span>{escaped}</span>"), AppendText("</span>")]
        )
        return batch

    def visit_rawhtml(self, node: nodes.RawHtml) -> AppendBatchAndDefer:
        # Raw HTML often stands for a symbol in a sentence, so it keeps its
        # trailing punctuation on the same line, as inline math does.
        batch = super().visit_rawhtml(node)
        sib = node.next_sibling()
        if (
            not isinstance(sib, nodes.Text)
            or not sib.text
            or sib.text[0] not in self._TRAILING_PUNCT
        ):
            return batch
        node._trailing_punct = sib.text[0]
        sib.text = sib.text[1:]
        return AppendBatchAndDefer(
            [
                AppendOpenTagManualClose(
                    tag="span",
                    classes=["inline-wrapper"],
                    newline_inner=False,
                    newline_outer=False,
                ),
                *batch.items,
            ]
        )

    def leave_rawhtml(self, node: nodes.RawHtml) -> EditCommand:
        # The visit method deferred a batch, so leave_node returns one.
        batch = cast(EditCommandBatch, self.leave_node(node))
        punct = getattr(node, "_trailing_punct", None)
        if not punct:
            return batch
        escaped = punct.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        batch.items.extend(
            [AppendText(f"<span>{escaped}</span>"), AppendText("</span>")]
        )
        return batch

    def visit_mathblock(self, node: nodes.MathBlock) -> AppendBatchAndDefer:
        # Preamble mathblocks are invisible — skip handrails, just emit hidden div
        if node.preamble:
            return super().visit_mathblock(node)

        batch = self._replace_node_with_handrails(
            node,
            collapse_in_hr=False,
            menu_label="Equation" if node.nonum else node.long_reftext,
            extra_attrs=self._notation_source(node),
        )
        close_p = self._close_p_before(node)
        batch.items[:0] = close_p
        handrail_idx = len(close_p)
        batch.items.append(AppendTextAndDefer("$$\n", "\n$$"))
        offset_class = (
            ["hr-offset"]
            if isinstance(node.parent, (nodes.Paragraph, nodes.Note))
            and not _wraps_block(node.parent)
            else []
        )
        batch.items[handrail_idx].classes += ["hr-hidden"] + offset_class
        return batch

    def leave_mathblock(self, node: nodes.MathBlock) -> EditCommandBatch:
        batch = super().leave_mathblock(node)
        if node.preamble:
            return batch
        # A step that starts with this equation shows its number (leave_step).
        number = None if getattr(node, "_number_in_step", False) else node.full_number
        batch.items.insert(2, self._hr_info_zone_number(number, style="eqn"))
        return batch

    def visit_bibitem(self, node: nodes.Bibitem) -> AppendBatchAndDefer:
        # The DOI and the back links are part of the card, so the handrail adds
        # no link icon of its own.
        batch = super().visit_bibitem(node)
        batch.items[0] = AppendNodeTag(node, "div")
        return self._wrap_batch_item_with_handrails(
            1,
            batch,
            include_content=False,
            classes=["hr-hidden"],
            icon=None,
            collapse_in_hr=False,
            link=False,
            node=node,
        )
