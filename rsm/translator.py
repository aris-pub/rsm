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

import logging
import re
import textwrap
import uuid
from abc import ABC, abstractmethod
from collections import namedtuple
from collections.abc import Callable, Iterable
from typing import Any, Literal

from . import nodes
from .util import highlight_code

logger = logging.getLogger("RSM").getChild("tlate")

# Tabler icons (hierarchy-3, list-details) for the proof rail's Map/State tabs.
_RAIL_MAP_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M12 5m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/>'
    '<path d="M6 19m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/>'
    '<path d="M18 19m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/>'
    '<path d="M6 17v-2a6 6 0 0 1 12 0v2"/><path d="M12 7v4"/></svg>'
)
_RAIL_STATE_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M13 5h8"/><path d="M13 9h5"/><path d="M13 15h8"/><path d="M13 19h5"/>'
    '<path d="M3 4m0 1a1 1 0 0 1 1 -1h2a1 1 0 0 1 1 1v2a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1z"/>'
    '<path d="M3 14m0 1a1 1 0 0 1 1 -1h2a1 1 0 0 1 1 1v2a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1z"/></svg>'
)
_RAIL_NOTATION_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M20 17v-12c0 -1.121 -.879 -2 -2 -2s-2 .879 -2 2v12l2 2l2 -2z"/>'
    '<path d="M16 7h4"/>'
    '<path d="M18 19h-13a2 2 0 1 1 0 -4h4a2 2 0 1 0 0 -4h-3"/></svg>'
)
_RAIL_SIDEBAR_COLLAPSE_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M4 4m0 2a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2z"/>'
    '<path d="M9 4v16"/><path d="M15 10l-2 2l2 2"/></svg>'
)
_RAIL_SIDEBAR_EXPAND_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M4 4m0 2a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2z"/>'
    '<path d="M9 4v16"/><path d="M14 10l2 2l-2 2"/></svg>'
)


def _reject_html_wrapper(path: str) -> None:
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
    external_scripts = []

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


def _make_tag(
    tag: str,
    id_: str,
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
        classes: list = None,
        newline_inner: bool = True,
        newline_outer: bool = True,
        is_selectable: bool = False,
        **kwargs,
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
        classes: list = None,
        newline_inner: bool = True,
        newline_outer: bool = True,
        is_selectable: bool = False,
        **kwargs,
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

    def close_command(self):
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
        **kwargs,
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
        kwargs = {"nodeid": node.nodeid}
        if extra_attrs:
            kwargs.update(extra_attrs)
        if isinstance(node, nodes.Asset) and node.static:
            static_src = self._resolve_image_src(node.static) if hasattr(self, '_resolve_image_src') else str(node.static)
            kwargs["data-static"] = static_src
        if include_source and manuscript_source and hasattr(node.start_point, "row"):
            source_lines = manuscript_source.split("\n")
            start_row = node.start_point.row
            start_col = node.start_point.column
            end_row = node.end_point.row
            end_col = node.end_point.column

            if start_row < len(source_lines) and end_row < len(source_lines):
                # Compute character offsets into the full source string
                start_offset = sum(len(source_lines[r]) + 1 for r in range(start_row)) + start_col
                end_offset = sum(len(source_lines[r]) + 1 for r in range(end_row)) + end_col
                kwargs["data-source-start"] = str(start_offset)
                kwargs["data-source-end"] = str(end_offset)

        id_ = node.label
        if not id_ and isinstance(node, nodes.Section) and node.full_number:
            id_ = f"sec-{node.full_number}"

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
        classes: list = None,
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
        classes: list = None,
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
        classes: list = None,
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
        classes: list = None,
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
    def __init__(self, root: nodes.Node, handrails: bool = False):
        super().__init__()
        self.root = root
        self.cls = HandrailsTranslator if handrails else Translator

    def make_text(self) -> str:
        return self.cls(quiet=True).translate(self.root)


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


def auto_leave_deferred(leave_method):
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

    def wrapper(self, node):
        # Get the base leave_node batch (handles deferred cleanup)
        base_batch = self.leave_node(node)

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

    def __init__(self, quiet: bool = False, asset_resolver=None, standalone: bool = False, add_source: bool = False):
        self.tree: nodes.Manuscript = None
        self.body: str = ""
        self.standalone = standalone
        self.add_source = add_source
        # Default to disk-based asset resolver if none provided
        if asset_resolver is None:
            from .asset_resolver import AssetResolverFromDisk

            asset_resolver = AssetResolverFromDisk()
        self.asset_resolver = asset_resolver
        self.deferred: list[EditCommand] = []
        self.quiet = quiet

    def _node_tag(self, node, tag="div", **kwargs):
        """Create an AppendNodeTag with source offsets if add_source is enabled."""
        return AppendNodeTag(
            node,
            tag,
            include_source=self.add_source,
            manuscript_source=getattr(self.tree, "src", "") or "",
            **kwargs,
        )

    @staticmethod
    def _icon_ref(name: str) -> str:
        """Emit an SVG <use> reference to a symbol in the defs block."""
        return f'<div class="icon {name}"><svg overflow="visible"><use href="#hr-icon-{name}" width="100%" height="100%"/></svg></div>'

    @classmethod
    def get_action_method(cls, node: nodes.Node, action: str) -> Callable:
        nodeclass = node.__class__
        method = f"{action}_{nodeclass.__name__.lower()}"
        while not hasattr(cls, method):
            nodeclass = nodeclass.__bases__[0]
            method = f"{action}_{nodeclass.__name__.lower()}"
        # if action == "visit" and ogclass is not nodeclass:
        #     logger.debug(f"Using {method} for node of class {ogclass}")
        return getattr(cls, method)

    def push_visit(self, stack, node: nodes.Node) -> None:
        stack.append(self.Action(node, "visit", self.get_action_method(node, "visit")))

    def push_leave(self, stack, node: nodes.Node) -> None:
        stack.append(self.Action(node, "leave", self.get_action_method(node, "leave")))

    def translate(self, tree: nodes.Manuscript, new: bool = True) -> str:
        if not self.quiet:
            logger.info("Translating...")
        if new:
            self.body = ""
        self.tree = tree

        if self.deferred:
            raise RSMTranslatorError("Something went wrong")

        stack = []
        self.push_visit(stack, tree)
        while stack:
            node, action, method = stack.pop()
            command = method(self, node)
            if action == "visit":
                if command.defers:
                    self.push_leave(stack, node)
                for child in reversed(node.children):
                    self.push_visit(stack, child)
            command.execute(self)

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

    def visit_manuscript(self, node: nodes.Manuscript) -> EditCommand:
        accent = getattr(node, 'accent', 'blue')
        lang = getattr(node, 'lang', 'en')
        typography = getattr(node, 'typography', 'sans-serif')
        batch = AppendBatchAndDefer(
            [
                AppendOpenTag("body", **{"data-accent": accent, "data-lang": lang, "data-typography": typography}),
                AppendOpenTag("main", classes=["manuscriptwrapper"]),
                AppendNodeTag(node),
                AppendOpenTag("section", classes=["level-1"]),
            ]
        )
        if node.title:
            batch.items.append(AppendHeading(1, node.title))

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
            batch.items.append(AppendParagraph(date_str, classes=["manuscript-date"]))

        return batch

    def leave_manuscript(self, node: nodes.Manuscript) -> EditCommand:
        return self.leave_node(node)

    def visit_author(self, node: nodes.Author) -> EditCommand:
        return AppendText("")

    def leave_author(self, node: nodes.Author) -> EditCommand:
        return AppendText("")

    def visit_authorblock(self, node: nodes.AuthorBlock) -> EditCommand:
        authors = [c for c in node.children if isinstance(c, nodes.Author)]
        total_affiliations = getattr(self.tree, 'total_unique_affiliations', 0)
        total_notes = getattr(self.tree, 'total_unique_notes', 0)

        # Build reverse maps for tooltips
        notes_node = next(
            (c for c in node.children if isinstance(c, nodes.AuthorNotes)), None
        )
        aff_by_num: dict[int, str] = {}
        if notes_node:
            aff_by_num = {v: k for k, v in notes_node.affiliation_map.items()}

        name_parts = []
        for author in authors:
            if not author.name:
                continue
            name_html = author.name
            sup_parts = []
            if author.affiliation_number is not None and total_affiliations > 1:
                tooltip = aff_by_num.get(author.affiliation_number, "")
                sup_parts.append(
                    f'<sup data-tooltip="{tooltip}">{author.affiliation_number}</sup>'
                )
            if author.note_symbol and total_notes > 1:
                sup_parts.append(
                    f'<sup data-tooltip="{author.author_note}">{author.note_symbol}</sup>'
                )
            name_html += ''.join(sup_parts)
            name_parts.append(name_html)

        names_line = ', '.join(name_parts) if name_parts else ''

        # Build the full block content: names + details
        html = f'\n<p class="author-names">{names_line}</p>\n' if names_line else ''
        html += self._make_authornotes_html(notes_node)

        return AppendBatchAndDefer([
            AppendOpenTag("div", classes=["author-block"], newline_inner=False),
            AppendText(html),
        ])

    def leave_authorblock(self, node: nodes.AuthorBlock) -> EditCommand:
        return self.leave_node(node)

    def visit_authornotes(self, node: nodes.AuthorNotes) -> EditCommand:
        return AppendText('')

    def leave_authornotes(self, node: nodes.AuthorNotes) -> EditCommand:
        return AppendText('')

    def _make_authornotes_html(self, node: nodes.AuthorNotes | None) -> str:
        if not node:
            return ''
        has_content = node.affiliation_map or node.note_map or node.emails or node.orcids
        if not has_content:
            return ''

        total_affiliations = len(node.affiliation_map)
        total_notes = len(node.note_map)

        html = '<details class="author-details">\n'
        html += f'<summary>{self._icon_ref("chevron-down")}Affiliations</summary>\n'

        if node.affiliation_map:
            html += '<ol class="author-affiliations">\n'
            if total_affiliations > 1:
                for aff_text, aff_num in node.affiliation_map.items():
                    html += f'<li value="{aff_num}"><sup>{aff_num}</sup>{aff_text}</li>\n'
            else:
                for aff_text in node.affiliation_map:
                    html += f'<li>{aff_text}</li>\n'
            html += '</ol>\n'

        if node.note_map:
            if total_notes > 1:
                for note_text, note_sym in node.note_map.items():
                    html += f'<p class="author-note"><sup>{note_sym}</sup>{note_text}</p>\n'
            else:
                for note_text in node.note_map:
                    html += f'<p class="author-note">{note_text}</p>\n'

        if node.emails:
            email_links = ', '.join(
                f'<a href="mailto:{email}">{email}</a>' for _, email in node.emails
            )
            html += f'<p class="author-correspondence">Correspondence: {email_links}</p>\n'

        if node.orcids:
            for name, orcid in node.orcids:
                html += f'<p class="author-orcid">{name}: {orcid}</p>\n'

        html += '</details>\n'
        return html

    def visit_abstract(self, node: nodes.Abstract) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node),
                AppendHeading(3, "Abstract"),
            ]
        )

    def leave_abstract(self, node: nodes.Abstract) -> EditCommand:
        batch = AppendBatch([])

        if node.keywords:
            text = ", ".join(node.keywords)
            batch.items.append(
                AppendParagraph(f"Keywords: {text}", classes=["keywords"])
            )
        if node.msc:
            text = ", ".join(node.msc)
            batch.items.append(AppendParagraph(f"MSC: {text}", classes=["msc"]))

        # For documentation: if a visit_* method returns a command with defers = True,
        # then the corresponding leave_* method MUST MUST MUST call leave_node(node) and
        # add it to the returned batch!!!
        batch.items.append(self.leave_node(node))
        return batch

    def visit_paragraph(self, node: nodes.Paragraph) -> EditCommand:
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
        items: list[EditCommand] = [AppendNodeTag(node, "div")]  #
        if node.first_of_type(nodes.MathBlock) or node.first_of_type(nodes.CodeBlock):
            items.append(AppendOpenTagManualClose(tag="p", newline_inner=False))
        else:
            items.append(AppendOpenTag(tag="p", newline_inner=False))

        # Now we're inside the <p> tag in the appropriate way, make sure to add the
        # title, if it exists.
        if node.title:
            items.append(
                AppendOpenCloseTag(
                    tag="span", content=f"{node.title}.", classes=["pg-label"]
                )
            )

        return AppendBatchAndDefer(items)

    def visit_step(self, node: nodes.Step) -> EditCommand:
        return AppendNodeTag(node)

    def visit_section(self, node: nodes.Section) -> EditCommand:
        node.classes.insert(0, f"level-{node.level}")
        heading = (
            f"{node.full_number}. {node.title}" if not node.nonum else f"{node.title}"
        )
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, "section"),
                AppendHeading(node.level, heading),
            ]
        )

    def visit_enumerate(self, node: nodes.Enumerate) -> EditCommand:
        return AppendNodeTag(node, "ol")

    def visit_itemize(self, node: nodes.Itemize) -> EditCommand:
        return AppendNodeTag(node, "ul")

    def visit_item(self, node: nodes.Item) -> EditCommand:
        return AppendNodeTag(node, "li")

    def visit_contents(self, node: nodes.Contents) -> EditCommand:
        toc_classes = ["toc"] + (["tree"] if node.view == "tree" else [])
        return AppendBatchAndDefer(
            [
                AppendOpenTag(classes=toc_classes),
                AppendHeading(3, "Table of Contents"),
                AppendOpenTag(classes=["toc-wrapper"]),
                AppendText(text=self._toc_tree_svg(node)),
                AppendNodeTag(node, "ul"),
            ]
        )

    def _toc_tree_svg(self, node: nodes.Contents) -> str:
        return self._build_tree_svg(
            node.tree_nodes, node.toc_edges, node.tree_root_title,
            "Section dependency graph",
        )

    def _build_tree_svg(
        self, tree_nodes: list[dict], ref_edges: list[dict],
        root_title: str, aria_label: str, orient: str = "vertical",
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

        from .toc_layout import ROOT_LABEL, layout_tree

        secs = tree_nodes
        if not secs:
            return '<svg class="toc-tree" aria-hidden="true"></svg>'

        root_idx = len(secs)
        root = {"num": "", "title": root_title, "label": "", "depth": 0}
        struct = []
        for i, sec in enumerate(secs):
            if sec["depth"] == 1:
                parent = root_idx
            else:
                parent = root_idx
                for j in range(i - 1, -1, -1):
                    if secs[j]["depth"] < sec["depth"]:
                        parent = j
                        break
            struct.append({"src": i, "dst": parent, "count": 1, "kind": "struct"})

        layout = layout_tree(secs + [root], ref_edges + struct, orient)
        if layout is None:
            return '<svg class="toc-tree" aria-hidden="true"></svg>'
        horizontal = orient == "horizontal"

        pad = 12
        w = layout["width"] + 2 * pad
        h = layout["height"] + 2 * pad
        parts = [
            f'<svg class="toc-tree" width="{w:.0f}" height="{h:.0f}" '
            f'viewBox="{-pad} {-pad} {w:.0f} {h:.0f}" role="group" '
            f'aria-label="{escape(aria_label)}">',
            '<defs>'
            '<marker id="toc-arr-dep" viewBox="0 0 10 8" refX="8.5" refY="4" '
            'markerWidth="8" markerHeight="6.5" markerUnits="userSpaceOnUse" '
            'orient="auto-start-reverse">'
            '<path d="M0,0 L10,4 L0,8 z" class="toc-arrowhead dep"/></marker>'
            '<marker id="toc-arr-fwd" viewBox="0 0 10 8" refX="8.5" refY="4" '
            'markerWidth="8" markerHeight="6.5" markerUnits="userSpaceOnUse" '
            'orient="auto-start-reverse">'
            '<path d="M0,0 L10,4 L0,8 z" class="toc-arrowhead fwd"/></marker>'
            '</defs>',
            '<g class="toc-edges-layer">',
        ]
        for e in layout["edges"]:
            x1, y1, x2, y2 = e["x1"], e["y1"], e["x2"], e["y2"]
            if horizontal:  # curve bends along x so left-to-right edges read cleanly
                mx = (x1 + x2) / 2
                d = f'M {x1:.1f} {y1:.1f} C {mx:.1f} {y1:.1f}, {mx:.1f} {y2:.1f}, {x2:.1f} {y2:.1f}'
            else:
                my = (y1 + y2) / 2
                d = f'M {x1:.1f} {y1:.1f} C {x1:.1f} {my:.1f}, {x2:.1f} {my:.1f}, {x2:.1f} {y2:.1f}'
            if e["kind"] == "struct":
                sw, marker = 1.0, ""
            else:
                sw = 1.1 + e["count"] * 0.7
                marker = f' marker-end="url(#toc-arr-{e["kind"]})"'
            parts.append(
                f'<path class="toc-edge {e["kind"]}" d="{d}" '
                f'stroke-width="{sw:.1f}" data-from="{e["src"]}" '
                f'data-to="{e["dst"]}"{marker}></path>'
            )
        parts.append('</g><g class="toc-nodes-layer">')
        for n in layout["nodes"]:
            href = f'#{n["label"]}' if n["label"] else "#"
            cx = n["x"] + n["w"] / 2
            cy = n["y"] + n["h"] / 2
            full = (f'{n["num"]}. {n["title"]}' if n["num"] else n["title"])
            # The compact horizontal-rail root shows a short "Goal" marker; its
            # full statement is on hover. Other nodes show their number/title.
            if horizontal and n["depth"] == 0:
                inner = escape(ROOT_LABEL)
            else:
                inner = escape(n["num"]) + "." if n["num"] else escape(n["title"])
            parts.append(
                f'<a href="{escape(href)}" class="toc-node level-{n["depth"]}" '
                f'data-idx="{n["idx"]}" data-title="{escape(full)}">'
                f'<rect x="{n["x"]:.1f}" y="{n["y"]:.1f}" width="{n["w"]}" '
                f'height="{n["h"]}" rx="6"></rect>'
                f'<text class="toc-secnum" x="{cx:.1f}" y="{cy:.1f}" '
                f'text-anchor="middle" dominant-baseline="central">{inner}</text></a>'
            )
        parts.append('</g>')
        parts.append(
            '<g class="toc-hover-label" style="display:none">'
            '<rect rx="7"></rect><text></text></g>'
        )
        parts.append('</svg>')
        return "".join(parts)

    def visit_note(self, node: nodes.Note) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendOpenTag("span", classes=["note"]),
                AppendOpenCloseTag(
                    "sup",
                    content=f'<a class="note__link">{node.full_number}</a>',
                    classes=["note__number"],
                    newline_inner=False,
                ),
                AppendOpenTag(
                    "span",
                    id=node.label,
                    classes=["note__content"],
                    newline_inner=False,
                ),
            ]
        )

    def visit_math(self, node: nodes.Math) -> EditCommand:
        # \( ... \) are the standard TeX inline-math delimiters read by the client renderer
        if node.preamble:
            node.classes.append("math-preamble")
        return AppendBatchAndDefer(
            [
                self._node_tag(node, "span", newline_inner=False, newline_outer=False),
                AppendTextAndDefer(r"\(", r"\)"),
            ]
        )

    def visit_mathblock(self, node: nodes.MathBlock) -> EditCommand:
        commands = []
        if isinstance(node.parent, nodes.Paragraph):
            # A paragraph that contains a mathblock cannot _start_ with a mathblock,
            # so this mathblock must always contain some previous siblings that must
            # be enclosed in <p> tags.  (See comment in visit_paragraph().)
            commands.append(AppendText("</p>"))
        if node.preamble:
            node.classes.append("math-preamble")
        commands.append(AppendNodeTag(node, "div"))
        commands.append(AppendTextAndDefer("$$\n", "\n$$"))
        return AppendBatchAndDefer(commands)

    def leave_mathblock(self, node: nodes.MathBlock) -> EditCommand:
        # See also the comment in visit_paragraph().
        batch = self.leave_node(node)

        # The paragraph-specific logic only applies when the parent is a BaseParagraph
        # With grammar changes, MathBlocks can now have other types of parents
        if not isinstance(node.parent, nodes.BaseParagraph):
            return batch

        # In case this mathblock is the last child of the paragraph, there is nothing
        # special to do since visit_mathblock() already handled the remaining </p> tag.
        if not node.next_sibling():
            return batch

        # If there are more children, we need to close this mathblock, start a new <p>
        # tag, and defer its closing.  This tag must close at the time that we leave the
        # parent paragraph.  The least hacky way I found to control the parent node's
        # deferred commands was to use a special attribute.
        else:
            node.parent._must_close_p_tag = True
            batch.items.append(AppendText("<p>"))
            return AppendBatch(batch.items)

    def leave_paragraph(self, node: nodes.Paragraph) -> EditCommand:
        batch = self.leave_node(node)
        if getattr(node, "_must_close_p_tag", False):
            batch.items.insert(0, AppendText("</p>"))
        return batch

    def visit_sourcecode(self, node: nodes.SourceCode) -> EditCommand:
        classes = []
        if node.lang:
            classes = ["highlight", node.lang]
            code = highlight_code(node.text, node.lang)
        else:
            code = node.text
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
        return self._node_tag(node, tag="span", newline_inner=False, newline_outer=False)

    def visit_codeblock(self, node: nodes.CodeBlock) -> EditCommand:
        items = []
        if isinstance(node.parent, nodes.BaseParagraph):
            items.append(AppendText("</p>"))
        items += [
            AppendNodeTag(node, "div", newline_inner=True, newline_outer=True),
            AppendOpenTag("pre"),
        ]
        return AppendBatchAndDefer(items)

    def leave_codeblock(self, node: nodes.CodeBlock) -> EditCommand:
        batch = self.leave_node(node)
        if not isinstance(node.parent, nodes.BaseParagraph):
            return batch
        if not node.next_sibling():
            return batch
        node.parent._must_close_p_tag = True
        batch.items.append(AppendText("<p>"))
        return AppendBatch(batch.items)

    def visit_algorithm(self, node: nodes.Algorithm) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendOpenTag(id=node.label, classes=["algorithm"]),
                AppendOpenTag("pre", classes=["pseudocode"]),
            ]
        )

    def visit_notation(self, node: nodes.Notation) -> EditCommand:
        # Emit the rebindable-notation entries as data for the frontend, which
        # defines the macros from the defaults and lets the reader reskin them.
        import json
        data = json.dumps(node.entries).replace("</", "<\\/")
        return AppendText(
            f'<script type="application/json" class="rsm-notation">{data}</script>'
        )

    def visit_text(self, node: nodes.Text) -> EditCommand:
        return AppendText(node.text)

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
                self._node_tag(node, tag="span", newline_inner=False, newline_outer=False),
                *commands,
            ]
        )

    def visit_construct(self, node: nodes.Construct) -> EditCommand:
        return self._node_tag(node, tag="span", newline_inner=False, newline_outer=False)

    def _make_ahref_tag_text(
        self,
        node: nodes.BaseReference | nodes.Cite,
        target: nodes.Node,
        href_text: str,
        label: str = "",
        id_: str = "",
        additional_classes: None | list[str] = None,
    ) -> str:
        if not target:
            raise RSMTranslatorError(f"Found a {node.__class__} without a target")
        tgt = target
        if hasattr(node, "overwrite_reftext") and node.overwrite_reftext:
            reftext = node.overwrite_reftext
        else:
            reftext = getattr(tgt, "reftext", tgt)
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
            # Internal reference (existing behavior)
            tag_text = self._make_ahref_tag_text(
                node, node.target, f"#{node.target.label}"
            )

        # Wrap ref + trailing punctuation to prevent line break between them.
        # Also pull in a preceding opening bracket if present.
        sib = node.next_sibling()
        if isinstance(sib, nodes.Text) and sib.text and sib.text[0] in self._TRAILING_PUNCT:
            punct = sib.text[0]
            sib.text = sib.text[1:]
            escaped = punct.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

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
        self, label: str, desc: str = "", classes: list = None
    ) -> nodes.Node:
        if classes is None:
            classes = ["hr-label"]
        para = nodes.Paragraph(classes=classes)
        if label:
            span = nodes.Span(classes=["label"])
            span.append(nodes.Text(text=label))
            para.append(span)
        if desc:
            span = nodes.Span(classes=["desc"])
            span.append(nodes.Text(text=desc))
            para.append(span)
        return para

    def visit_theorem(self, node: nodes.Theorem) -> EditCommand:
        classname = node.__class__.__name__.lower()
        title = self._make_title_node(
            label=f"{classname.capitalize()}"
            + (f" {node.full_number}" if not node.nonum and node.number else "")
            + (": " if node.title else "."),
            desc=node.title or "",
        )
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, additional_classes=["theorem"]),
                AppendExternalTree(title),
            ]
        )

    def visit_statement(self, node: nodes.Statement) -> EditCommand:
        return AppendNodeTag(node)

    def visit_subproof(self, node: nodes.Subproof) -> EditCommand:
        node.__class__.__name__.lower()
        return AppendBatchAndDefer([AppendNodeTag(node)])

    def visit_sketch(self, node: nodes.Sketch) -> EditCommand:
        title = self._make_title_node(label="Proof sketch.")
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node),
                AppendExternalTree(title),
            ]
        )

    def visit_proof(self, node: nodes.Proof) -> EditCommandBatch:
        last = node.last_of_type(nodes.Step)
        if last:
            last.classes.append("last")

        classname = node.__class__.__name__.lower()
        title = self._make_title_node(label=f"{classname.capitalize()}.")
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node),
                AppendExternalTree(title),
            ]
        )

    @auto_leave_deferred
    def leave_proof(self, node: nodes.Proof, base_batch) -> EditCommand:
        base_batch.items.insert(-1, AppendHalmos())
        return AppendBatch(base_batch.items)

    def visit_cite(self, node: nodes.Cite) -> EditCommand:
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
                    text = f'{first} {middle}, {last}'
                else:
                    text = f'{first} {last}'
                text = f'<span id="{node.label}">{text}</span>'
                return AppendText(text)
            text = f'<span id="{node.label}">{text}</span>'
        return AppendText(f'<span class="nowrap">[{text}]</span>')

    def visit_bibliography(self, node: nodes.Bibliography) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendOpenTag("section", classes=["level-2"]),
                AppendHeading(2, "References"),
                AppendNodeTag(node, "ol"),
            ]
        )

    def visit_bibitem(self, node: nodes.Bibitem) -> EditCommand:
        items = [node.author, f'"{node.title}"']
        if node.number:
            items.insert(0, f"{node.number}.")
        if node.kind == "article":
            if node.journal:
                items.append(node.journal)
            else:
                logger.warning(f"Bibitem {node.label} has no journal")
        elif node.kind == "book":
            if node.publisher:
                items.append(node.publisher)
            else:
                logger.warning(f"Bibitem {node.label} has no publisher")
        elif node.kind in ("inproceedings", "conference"):
            if node.booktitle:
                items.append(f"In {node.booktitle}")
        elif node.kind == "incollection":
            if node.booktitle:
                items.append(f"In {node.booktitle}")
            if node.publisher:
                items.append(node.publisher)
        elif node.kind in ("phdthesis", "mastersthesis"):
            kind_label = "PhD thesis" if node.kind == "phdthesis" else "Master's thesis"
            items.append(kind_label)
            if node.school:
                items.append(node.school)
        elif node.kind == "techreport":
            items.append("Technical report")
            if node.institution:
                items.append(node.institution)
        elif node.kind == "misc":
            if node.howpublished:
                items.append(node.howpublished)
        if node.year:
            items.append(node.year)
        else:
            logger.warning(f"Bibitem {node.label} has no year")
        text = ". ".join([i.strip(".") for i in items]) + "."
        if node.doi:
            a_tag = _make_tag(
                "a",
                id_=f"{node.label}-doi",
                classes=["bibitem-doi"],
                href=f"https://doi.org/{node.doi}",
                target="_blank",
            )
            text = f"{text} {a_tag}[link]</a>"
        elif node.url:
            a_tag = _make_tag(
                "a",
                id_=f"{node.label}-url",
                classes=["bibitem-url"],
                href=node.url,
                target="_blank",
            )
            text = f"{text} {a_tag}[link]</a>"
        else:
            logger.warning(f"Bibitem {node.label} has no DOI")

        if node.backlinks:
            text += "<br />"
            backs = [
                _make_tag(
                    "a",
                    id_="",
                    classes=["reference", "backlink"],
                    href=f"#{link_lbl}",
                )
                + f"↖{idx}"
                + "</a>"
                for idx, link_lbl in enumerate(node.backlinks, start=1)
            ]
            text += "[" + ",".join(backs) + "]"

        return AppendBatchAndDefer([AppendNodeTag(node, "li"), AppendText(text)])

    def visit_draft(self, node: nodes.Draft) -> EditCommand:
        return AppendBatchAndDefer(
            [AppendNodeTag(node, "span"), AppendTextAndDefer("[ ", " ]")]
        )

    def _resolve_html_content(self, path) -> str:
        """Resolve an HTML asset file and return processed content."""
        content = self.asset_resolver.resolve_asset(str(path))
        if content is None:
            return f'<div class="html-error">Unable to load HTML asset: {path}</div>'

        is_full_html_doc = content.strip().lower().startswith(
            "<html"
        ) or content.strip().lower().startswith("<!doctype")

        if is_full_html_doc:
            _reject_html_wrapper(path)
        return content

    def _resolve_image_src(self, path) -> str:
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
        if isinstance(resolved, str) and (resolved.startswith("/") or resolved.startswith("http")):
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
        alt_text = node.alt if node.alt else f"{node.__class__.__name__} {node.full_number}."
        src = self._resolve_image_src(node.path)
        img = _make_tag(
            "img",
            id_=node.label,
            classes=[],
            src=src,
            alt=alt_text,
            onload="" if node.scale == 1.0 else f"this.width*={node.scale};",
        )
        if node.dark:
            dark_src = self._resolve_image_src(node.dark)
            source = f'<source media="(prefers-color-scheme: dark)" srcset="{dark_src}">'
            return f"<picture>\n{source}\n{img}\n</picture>"
        return img

    def _detect_content_type_and_render(self, node: nodes.Asset) -> str:
        """Detect content type from path and return appropriate HTML."""
        path_str = str(node.path).lower()

        # An asset with no real path (e.g. an inline :html: block whose markup
        # is carried by its own children) has nothing to render here, and must
        # not fall through to the image branch, which would emit <img src=".">.
        if not path_str or path_str == ".":
            return ""

        # Image files
        if any(
            path_str.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg"]
        ):
            return self._render_image(node)

        # Video files
        elif any(path_str.endswith(ext) for ext in [".mp4", ".webm", ".avi", ".mov"]):
            return (
                _make_tag(
                    "video",
                    id_=node.label,
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
                    id_=node.label,
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

    def _static_fallback_img(self, node: nodes.Asset) -> str:
        if not node.static:
            return ""
        src = self._resolve_image_src(node.static)
        alt = f"Static fallback for {node.__class__.__name__} {node.full_number}."
        return f'<img class="static-fallback" src="{src}" alt="{alt}" style="display:none">'

    def visit_figure(self, node: nodes.Figure) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, "figure"),
                AppendText(self._detect_content_type_and_render(node)),
                AppendText(self._static_fallback_img(node)),
            ]
        )

    def visit_video(self, node: nodes.Video) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, "figure"),
                AppendText(self._detect_content_type_and_render(node)),
            ]
        )

    def visit_html(self, node: nodes.Html) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, "figure"),
                AppendText(self._detect_content_type_and_render(node)),
                AppendText(self._static_fallback_img(node)),
            ]
        )

    def visit_caption(self, node: nodes.Caption) -> EditCommand:
        parent = node.parent
        caption = AppendOpenCloseTag(
            tag="span",
            content=f"{parent.classreftext.format(nodeclass=parent.__class__.__name__, number=parent.full_number)}. ",
            classes=["label"],
            newline_inner=False,
            newline_outer=False,
        )
        # Tables use figcaption outside <table> (inside table-wrapper) so the caption
        # doesn't participate in the table's intrinsic width calculation.
        use_figcaption = isinstance(parent, (nodes.Asset, nodes.Table))
        items = []
        if isinstance(parent, nodes.Table):
            items.append(AppendText("\n</table>\n"))
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

    def visit_table(self, node: nodes.Table) -> EditCommand:
        table_tag = AppendNodeTag(node, "table")
        manual_table = AppendOpenTagManualClose(
            tag="table",
            id=table_tag.id,
            classes=table_tag.classes,
            **{k: v for k, v in table_tag.custom_attrs.items()},
        )
        return AppendBatchAndDefer(
            [
                AppendOpenTag("div", classes=["table-wrapper"]),
                manual_table,
            ]
        )

    def leave_table(self, node: nodes.Table) -> EditCommand:
        has_caption = any(isinstance(c, nodes.Caption) for c in node.children)
        batch = self.leave_node(node)
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
        "collapse": """<svg width="8" height="14" viewBox="0 0 8 14" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
        <path d="M1 1L7 7L1 13" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>""",
        "collapse-all": """<svg width="9" height="9" viewBox="5 5 14 14" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
        <path d="M7 7l5 5l-5 5" />
        <path d="M13 7l5 5l-5 5" />
      </svg>""",
        "chevron-down": """<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
<path d="M6 9l6 6l6 -6" />
</svg>""",
        "expand": """<svg width="14" height="8" viewBox="0 0 14 8" fill="none" stroke="#3C4952" xmlns="http://www.w3.org/2000/svg">
<path d="M1 1L7 7L13 1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
        "expand-all": """<svg width="9" height="9" viewBox="5 5 14 14" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
<path d="M7 7l5 5l5 -5" />
<path d="M7 13l5 5l5 -5" />
</svg>""",
        "dots": """<svg width="24" height="24" viewBox="10 3 4 18" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
<path stroke="none" d="M0 0h24v24H0z" fill="none"/>
<path d="M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
<path d="M12 19m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
<path d="M12 5m-1 0a1 1 0 1 0 2 0a1 1 0 1 0 -2 0" />
</svg>""",
        "ext": """<svg width="15" height="15" viewBox="3 3 18 18" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
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
    }

    def __init__(
        self,
        quiet: bool = False,
        add_source: bool = True,
        asset_resolver=None,
        standalone: bool = False,
    ):
        super().__init__(quiet, asset_resolver, standalone, add_source=add_source)

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
    ) -> EditCommand:
        classes = (classes or []) + ["hr"] + (["hr-offset"] if depth > 0 else [])
        classes = list(dict.fromkeys(classes))  # deletes duplicates AND preserves order

        # Add source data if node is provided
        kwargs = {}
        if extra_attrs:
            kwargs.update(extra_attrs)
        if (
            self.add_source
            and node
            and self.tree
            and self.tree.src
            and hasattr(node.start_point, "row")
        ):
            source_lines = self.tree.src.split("\n")
            start_row = node.start_point.row
            start_col = node.start_point.column
            end_row = node.end_point.row
            end_col = node.end_point.column

            if start_row < len(source_lines) and end_row < len(source_lines):
                start_offset = sum(len(source_lines[r]) + 1 for r in range(start_row)) + start_col
                end_offset = sum(len(source_lines[r]) + 1 for r in range(end_row)) + end_col
                kwargs["data-source-start"] = str(start_offset)
                kwargs["data-source-end"] = str(end_offset)

        return (
            AppendOpenTag(classes=classes, is_selectable=True, **kwargs)
            if include_content
            else AppendOpenTagManualClose(classes=classes, is_selectable=True, **kwargs)
        )

    def _hr_collapse_zone(self, collapsible: bool) -> AppendOpenCloseTag:
        if collapsible:
            content = f"""
            <div class="hr-collapse">
              {self._icon_ref("collapse")}
            </div>
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
            attrs["data-menu-collapse"] = "disabled" if collapse == "disabled" else "true"
        if collapse_all:
            attrs["data-menu-collapse-all"] = "disabled" if collapse_all == "disabled" else "true"
        if link:
            attrs["data-menu-link"] = "disabled" if link == "disabled" else "true"
        if code:
            attrs["data-menu-code"] = "disabled" if code == "disabled" else "true"
        if static_toggle:
            attrs["data-menu-static-toggle"] = "disabled" if static_toggle == "disabled" else "true"
        if toc_view:
            attrs["data-menu-toc-view"] = "disabled" if toc_view == "disabled" else "true"
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

    def _hr_content_zone(self, include_content) -> EditCommand:
        return (
            AppendOpenTag(classes=["hr-content-zone"])
            if include_content
            else AppendOpenTagManualClose(classes=["hr-content-zone"])
        )

    def _hr_info_zone_icon(self, icon) -> AppendOpenCloseTag:
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

    def _hr_info_zone_number(
        self, number: int | str, style: Literal["eqn", "step"]
    ) -> AppendOpenCloseTag:
        start = """<div class="hr-info">"""
        middle = ""
        if number is not None:
            if style == "step":
                middle = f"""<div class="step-number"><p>⟨{number}⟩</p></div>"""
            elif style == "eqn":
                middle = f"""<div class="eqn-number"><p>({number})</p></div>"""
        end = "</div>"
        return AppendOpenCloseTag(
            tag="div",
            content=start + middle + end,
            classes=["hr-info-zone"],
        )

    def _hr_from_node(
        self,
        node: nodes.NodeSubType,
        additional_classes: None | list[str] = None,
        is_selectable: bool = True,
        extra_attrs: dict | None = None,
    ):
        classes = (
            (node.classes or [])
            + ["hr"]
            + (["hr-hidden"] if node.handrail_depth == 2 else [])
            + (["hr-offset"] if node.handrail_depth > 0 else [])
            + (additional_classes or [])
        )
        classes = list(dict.fromkeys(classes))  # deletes duplicates AND preserves order
        return AppendNodeTag(
            node,
            additional_classes=classes,
            is_selectable=is_selectable,
            include_source=self.add_source,
            manuscript_source=self.tree.src if self.tree else "",
            extra_attrs=extra_attrs,
        )

    def _replace_node_with_handrails(
        self,
        node,
        *,
        additional_classes: None | list[str] = None,
        menu_label: str = "",
        collapse_in_hr: bool = True,
        collapse_in_menu: bool = False,
        collapse_all_in_menu: bool = False,
    ):
        menu_zone, menu_attrs = self._hr_menu_zone(
            label=menu_label or node.reftext,
            collapse=collapse_in_menu,
            collapse_all=collapse_all_in_menu,
            link=(True if node.label else "disabled"),
        )
        handrail = self._hr_from_node(node, additional_classes, extra_attrs=menu_attrs)
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
                label=node.reftext, collapse="disabled", collapse_all="disabled", link=link,
            )
        elif sub and sub.first_of_type(nodes.Step) is None:
            menu_zone, menu_attrs = self._hr_menu_zone(
                label=node.reftext, collapse=True, collapse_all="disabled", link=link,
            )
        else:
            menu_zone, menu_attrs = self._hr_menu_zone(
                label=node.reftext, collapse=True, collapse_all=True, link=link,
            )
        newitems = [
            self._hr_from_node(node, extra_attrs=menu_attrs),
            self._hr_collapse_zone(False),
            menu_zone,
            self._hr_border_zone(),
            self._hr_spacer_zone(),
            self._hr_content_zone(True),
        ]
        return AppendBatchAndDefer(newitems)

    def _wrap_item_with_handrails(
        self,
        index: int,
        items: list,
        cls,
        *,
        classes: list[str] | None = None,
        include_content: bool = False,
        icon=None,
        collapse_in_hr: bool = True,
        depth: int = 0,
        menu_label: str = "",
        link: bool | Literal["disabled"] = True,
        toc_view: bool | Literal["disabled"] = False,
        node: nodes.Node | None = None,
    ):
        menu_zone, menu_attrs = self._hr_menu_zone(
            label=menu_label, link=link, toc_view=toc_view
        )
        handrail = self._hr(include_content, depth, classes, node=node, extra_attrs=menu_attrs)
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
            newitems += [
                hr_content_zone.close_command(),
                self._hr_info_zone_icon(icon),
                handrail.close_command(),
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
        batch: EditCommandBatch,
        *,
        include_content: bool = False,
        icon=None,
        collapse_in_hr: bool = True,
        depth: int = 0,
        classes: list[str] | None = None,
        menu_label: str = "",
        link: bool | Literal["disabled"] = True,
        toc_view: bool | Literal["disabled"] = False,
        node: nodes.Node | None = None,
    ):
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
        cmd,
        *,
        include_content=False,
        icon=None,
        collapse_in_hr=True,
        depth=0,
        classes=None,
        link: bool | Literal["disabled"] = True,
    ):
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

    def _make_singleton_menu(self):
        """Emit the single shared menu template with all possible items."""
        html = '<div id="hr-menu-singleton" style="display:none">\n'
        html += '<div class="hr-menu">\n'
        html += f'  <div class="hr-menu-label"><span class="hr-menu-item-text" data-role="label"></span></div>\n'
        html += '  <div class="hr-menu-separator" data-role="label-sep"></div>\n'
        html += f'  <div class="hr-menu-item collapse-subproof" data-role="collapse">\n'
        html += f'    {self._icon_ref("collapse")}\n'
        html += '    <span class="hr-menu-item-text">Collapse</span>\n'
        html += '  </div>\n'
        html += f'  <div class="hr-menu-item collapse-steps" data-role="collapse-all">\n'
        html += f'    {self._icon_ref("collapse-all")}\n'
        html += '    <span class="hr-menu-item-text">Collapse all</span>\n'
        html += '  </div>\n'
        html += '  <div class="hr-menu-separator" data-role="collapse-sep"></div>\n'
        html += f'  <div class="hr-menu-item link" data-role="link">\n'
        html += f'    {self._icon_ref("link")}\n'
        html += '    <span class="hr-menu-item-text">Copy link</span>\n'
        html += '  </div>\n'
        html += f'  <div class="hr-menu-item" data-role="code">\n'
        html += f'    {self._icon_ref("code")}\n'
        html += '    <span class="hr-menu-item-text">Source</span>\n'
        html += '  </div>\n'
        html += '  <div class="hr-menu-separator" data-role="static-sep"></div>\n'
        html += f'  <div class="hr-menu-item" data-role="static-toggle">\n'
        html += f'    {self._icon_ref("image")}\n'
        html += '    <span class="hr-menu-item-text">Static</span>\n'
        html += '  </div>\n'
        html += '  <div class="hr-menu-separator" data-role="toc-view-sep"></div>\n'
        html += f'  <div class="hr-menu-item toc-view" data-role="toc-view">\n'
        html += f'    {self._icon_ref("tree")}\n'
        html += '    <span class="hr-menu-item-text">View as tree</span>\n'
        html += '  </div>\n'
        html += '</div>\n</div>'
        return AppendText(text=html)

    def _make_source_div(self):
        return AppendText(text=f'<div class="rsm-source hide">{self.tree.src}</div>')

    def _make_proof_rail(self):
        """A document-level container holding one pre-rendered step-tree SVG per
        proof, tagged by proof nodeid. prooftree.js floats it on the left and
        shows the tree of whichever proof is in view as the reader scrolls."""
        # The floating proof-tree rail is part of the graph-navigation
        # experience opted into by `:toc: {:view: tree}`; without it the
        # document's HTML is unchanged.
        toc = next(iter(self.tree.traverse(nodeclass=nodes.Contents)), None)
        if toc is None or getattr(toc, "view", "list") != "tree":
            return AppendText(text="")

        # Document scope: the whole-document TOC tree, plus a notation pane when
        # the author declared rebindable notation.
        doc_panels = []
        if toc.tree_nodes:
            doc_panels.append(
                f'<div class="rail-panel rail-doc-map">{self._toc_tree_svg(toc)}</div>'
            )
        has_notation = (
            next(iter(self.tree.traverse(nodeclass=nodes.Notation)), None) is not None
        )
        if has_notation:
            doc_panels.append('<div class="rail-panel rail-notation"></div>')

        # Proof scope: one pre-rendered step-tree (and its state) per proof,
        # auto-followed by prooftree.js as the reader scrolls.
        proof_items = []
        for proof in self.tree.traverse(nodeclass=nodes.Proof):
            if not proof.tree_nodes:
                continue
            svg = self._build_tree_svg(
                proof.tree_nodes, proof.tree_edges, proof.tree_root_title,
                "Proof step dependency graph", orient="horizontal",
            )
            proof_items.append(
                self._rail_item(str(proof.nodeid), svg, proof.step_state)
            )

        if not doc_panels and not proof_items:
            return AppendText(text="")

        scopes = (
            '<div class="rail-scopes">'
            '<button class="rail-scope active" data-scope="document" '
            'aria-pressed="true" '
            'data-tooltip="Document: structure and notation for the whole paper">'
            "Document</button>"
            '<button class="rail-scope" data-scope="proof" aria-pressed="false" '
            "data-tooltip=\"Proof: the dependency graph and live state of the proof "
            'you are reading">Proof</button>'
            "</div>"
        )

        # Document sub-tabs: the TOC map, and Notation when present.
        doc_tabs = [
            '<button class="rail-tab active" data-view="doc-map" '
            'aria-pressed="true" data-tooltip="Map of the document\'s structure">'
            + _RAIL_MAP_ICON + "<span>TOC</span></button>"
        ]
        if has_notation:
            doc_tabs.append(
                '<button class="rail-tab" data-view="notation" '
                'aria-pressed="false" data-tooltip="Rename the symbols used in this paper">'
                + _RAIL_NOTATION_ICON + "<span>Notation</span></button>"
            )
        doc_subtabs = (
            '<div class="rail-subtabs rail-subtabs-document">'
            + "".join(doc_tabs) + "</div>"
        )

        # Proof sub-tabs: Map (where you are) and State (what you must show).
        proof_subtabs = (
            '<div class="rail-subtabs rail-subtabs-proof">'
            '<button class="rail-tab active" data-view="proof-map" '
            'aria-pressed="true" '
            'data-tooltip="Map: where you are in the proof\'s dependency structure">'
            + _RAIL_MAP_ICON + "<span>Proof</span></button>"
            '<button class="rail-tab" data-view="state" aria-pressed="false" '
            'data-tooltip="State: the hypotheses in force and the goal you must show">'
            + _RAIL_STATE_ICON + "<span>State</span></button>"
            "</div>"
        )

        collapse = (
            '<button class="rail-collapse" data-tooltip="Collapse" '
            'aria-label="Collapse sidebar">'
            '<span class="rail-collapse-collapse">'
            + _RAIL_SIDEBAR_COLLAPSE_ICON + "</span>"
            '<span class="rail-collapse-expand">'
            + _RAIL_SIDEBAR_EXPAND_ICON + "</span></button>"
        )
        document_section = (
            '<div class="rail-section rail-document">' + "".join(doc_panels) + "</div>"
        )
        proof_section = (
            '<div class="rail-section rail-proof">'
            '<div class="rail-proof-empty">'
            "Scroll into a proof to see its map and state.</div>"
            + "".join(proof_items) + "</div>"
        )

        return AppendText(
            text='<div class="proof-rail scope-document doc-view-map '
            'proof-view-map" role="complementary" aria-label="Document and '
            'proof navigation">'
            + '<div class="rail-header">' + scopes + collapse + "</div>"
            + doc_subtabs + proof_subtabs
            + document_section + proof_section + "</div>"
        )

    def _rail_item(self, key: str, svg: str, step_state) -> str:
        data = ""
        if step_state is not None:
            import json
            data = (
                '<script type="application/json" class="rail-state-data">'
                + json.dumps(step_state) + "</script>"
            )
        return (
            f'<div class="proof-rail-item" data-proof="{key}">'
            f'<div class="rail-panel rail-map">{svg}</div>'
            f'<div class="rail-panel rail-state"></div>'
            f"{data}</div>"
        )

    def _make_svg_defs(self):
        """Emit a single <svg> block with <symbol> definitions for all icons."""
        symbols = []
        for name, svg_str in self.svg.items():
            # Extract the inner content (paths) and viewBox from the SVG string
            import re
            # Extract presentation attributes from the <svg> tag
            svg_tag = re.match(r'<svg([^>]*)>', svg_str)
            attrs_str = svg_tag.group(1) if svg_tag else ""
            vb_match = re.search(r'viewBox="([^"]*)"', attrs_str)
            viewBox = vb_match.group(1) if vb_match else "0 0 18 18"
            # Preserve fill, stroke, stroke-width, stroke-linecap, stroke-linejoin
            pres_attrs = ""
            for attr in ("fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin"):
                m = re.search(rf'{attr}="([^"]*)"', attrs_str)
                if m:
                    pres_attrs += f' {attr}="{m.group(1)}"'
            # Extract child elements (paths etc.)
            inner = re.sub(r'<svg[^>]*>', '', svg_str)
            inner = re.sub(r'</svg>', '', inner).strip()
            symbols.append(
                f'<symbol id="hr-icon-{name}" viewBox="{viewBox}"{pres_attrs}>{inner}</symbol>'
            )
        defs_html = '<svg id="hr-icon-defs" style="display:none"><defs id="hr-icon-defs">' + "\n".join(symbols) + "</defs></svg>"
        return AppendText(text=defs_html)

    def visit_manuscript(self, node: nodes.Manuscript) -> EditCommand:
        batch = super().visit_manuscript(node)
        if node.title:
            batch = self._wrap_batch_item_with_handrails(
                4, batch, classes=["heading"], menu_label="Title", link=True, node=node
            )
        batch.items.insert(2, self._make_svg_defs())
        batch.items.insert(3, self._make_singleton_menu())
        batch.items.insert(3, self._make_proof_rail())
        if self.add_source:
            batch.items.insert(3, self._make_source_div())
        return batch

    def visit_author(self, node: nodes.Author) -> EditCommand:
        return super().visit_author(node)

    def leave_author(self, node: nodes.Author) -> EditCommand:
        return super().leave_author(node)

    def visit_authorblock(self, node: nodes.AuthorBlock) -> EditCommand:
        batch = super().visit_authorblock(node)
        batch = self._wrap_batch_item_with_handrails(
            1,
            batch,
            classes=["heading", "hr-hidden"],
            link="disabled",
            node=node,
        )
        return batch

    def leave_authorblock(self, node: nodes.AuthorBlock) -> EditCommand:
        return super().leave_authorblock(node)

    def visit_section(self, node: nodes.Section) -> EditCommand:
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

    def visit_abstract(self, node: nodes.Abstract) -> EditCommand:
        batch = super().visit_abstract(node)
        return self._wrap_batch_item_with_handrails(
            1,
            batch,
            classes=["heading"],
            menu_label=node.reftext,
            link=True if node.label else "disabled",
            node=node,
        )

    def visit_contents(self, node: nodes.Contents) -> EditCommand:
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

    def visit_bibliography(self, node: nodes.Bibliography) -> EditCommand:
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

    def visit_paragraph(self, node: nodes.Paragraph) -> EditCommand:
        cmd = super().visit_paragraph(node)
        batch = self._replace_node_with_handrails(node, collapse_in_hr=False)
        if "hr-hidden" not in batch.items[0].classes:
            batch.items[0].classes.append("hr-hidden")
        batch = AppendBatchAndDefer([*batch.items, *cmd.items[1:]])
        return batch

    def leave_paragraph(self, node: nodes.Paragraph) -> EditCommand:
        # For documentation: if a visit_* method returns a command with defers = True,
        # then the corresponding leave_* method MUST MUST MUST call leave_node(node) and
        # add it to the returned batch!!!
        batch = super().leave_paragraph(node)
        batch.items.insert(-1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        return batch

    def visit_enumerate(self, node: nodes.Enumerate) -> EditCommand:
        batch = self._replace_node_with_handrails(node, collapse_in_hr=False)
        if "hr-hidden" not in batch.items[0].classes:
            batch.items[0].classes.append("hr-hidden")
        batch.items.append(super().visit_enumerate(node))
        return batch

    def leave_enumerate(self, node: nodes.Enumerate) -> EditCommand:
        batch = super().leave_node(node)
        batch.items.insert(-1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        return batch

    def visit_itemize(self, node: nodes.Itemize) -> EditCommand:
        # Don't add handrails to itemize lists inside Contents (TOC)
        if isinstance(node, nodes.Contents):
            return super().visit_itemize(node)
        # Check if any parent is a Contents node
        current = node.parent
        while current is not None:
            if isinstance(current, nodes.Contents):
                return super().visit_itemize(node)
            current = current.parent
        batch = self._replace_node_with_handrails(node, collapse_in_hr=False)
        if "hr-hidden" not in batch.items[0].classes:
            batch.items[0].classes.append("hr-hidden")
        batch.items.append(super().visit_itemize(node))
        return batch

    def leave_itemize(self, node: nodes.Itemize) -> EditCommand:
        # Don't add handrails to itemize lists inside Contents (TOC)
        if isinstance(node, nodes.Contents):
            return super().leave_node(node)
        # Check if any parent is a Contents node
        current = node.parent
        while current is not None:
            if isinstance(current, nodes.Contents):
                return super().leave_node(node)
            current = current.parent
        batch = super().leave_node(node)
        batch.items.insert(-1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        return batch

    def visit_caption(self, node: nodes.Caption) -> EditCommand:
        parent = node.parent
        caption_label = AppendOpenCloseTag(
            tag="span",
            content=f"{parent.classreftext.format(nodeclass=parent.__class__.__name__, number=parent.full_number)}. ",
            classes=["label"],
            newline_inner=False,
            newline_outer=False,
        )

        # Create figcaption with handrail classes
        figcaption_classes = ["hr", "hr-hidden"]
        additional_classes = (["hr-hidden"] if node.handrail_depth == 2 else []) + (
            ["hr-offset"] if node.handrail_depth > 0 else []
        )
        figcaption_classes.extend(additional_classes)

        use_figcaption = isinstance(parent, (nodes.Asset, nodes.Table))
        items = []
        if isinstance(parent, nodes.Table):
            items.append(AppendText("\n</table>\n"))
        has_static = isinstance(parent, nodes.Asset) and parent.static
        menu_zone, menu_attrs = self._hr_menu_zone(
            label="Caption",
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
        batch = self.leave_node(node)
        # Close hr-content-zone, add hr-info-zone, then close figcaption
        batch.items = [
            AppendText("</div>"),  # Close hr-content-zone
            self._hr_info_zone_icon(getattr(node, "icon", None)),
            *batch.items,  # This includes the closing figcaption tag
        ]
        return batch

    def visit_codeblock(self, node: nodes.CodeBlock) -> EditCommand:
        batch = self._replace_node_with_handrails(node, collapse_in_hr=False)
        handrail_idx = 0
        if isinstance(node.parent, nodes.Paragraph):
            batch.items.insert(0, AppendText("</p>"))
            handrail_idx = 1
        offset_class = ["hr-offset"] if isinstance(node.parent, nodes.Paragraph) else []
        batch.items[handrail_idx].classes += ["hr-hidden"] + offset_class
        batch.items.append(AppendOpenTag("pre"))
        return AppendBatchAndDefer(batch.items)

    @auto_leave_deferred
    def leave_codeblock(self, node: nodes.CodeBlock, base_batch) -> EditCommand:
        base_batch.items.insert(
            -1, self._hr_info_zone_icon(getattr(node, "icon", None))
        )
        return base_batch

    def visit_algorithm(self, node: nodes.Algorithm) -> EditCommand:
        cmd = super().visit_algorithm(node)
        batch = self._replace_node_with_handrails(node, collapse_in_hr=False)
        if "hr-hidden" not in batch.items[0].classes:
            batch.items[0].classes.append("hr-hidden")
        batch = AppendBatchAndDefer([*batch.items, *cmd.items[1:]])
        return batch

    @auto_leave_deferred
    def leave_algorithm(self, node: nodes.Algorithm, base_batch) -> EditCommand:
        base_batch.items.insert(
            -1, self._hr_info_zone_icon(getattr(node, "icon", None))
        )
        return base_batch

    def visit_theorem(self, node: nodes.Theorem) -> EditCommand:
        batch = super().visit_theorem(node)
        hr = self._replace_node_with_handrails(node, additional_classes=["hr-labeled"])
        hr.items += batch.items[1:]
        return hr

    @auto_leave_deferred
    def leave_theorem(self, node: nodes.Theorem, base_batch) -> EditCommand:
        base_batch.items.insert(1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        return AppendBatch(base_batch.items)

    def visit_sketch(self, node: nodes.Sketch) -> EditCommand:
        batch = super().visit_sketch(node)
        hr = self._replace_node_with_handrails(node, additional_classes=["hr-labeled"])
        hr.items += batch.items[1:]
        return hr

    def leave_sketch(self, node: nodes.Sketch) -> EditCommand:
        batch = self.leave_node(node)
        batch.items.insert(1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        batch = AppendBatch(batch.items)
        return batch

    def visit_proof(self, node: nodes.Proof) -> EditCommand:
        batch = super().visit_proof(node)
        hr = self._replace_node_with_handrails(
            node, additional_classes=["hr-labeled"], collapse_all_in_menu=True
        )
        hr.items += batch.items[1:]
        return hr

    @auto_leave_deferred
    def leave_proof(self, node: nodes.Proof, base_batch) -> EditCommand:
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
        batch = self.leave_node(node)
        batch.items.insert(1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        batch = AppendBatch(batch.items)
        return batch

    def visit_step(self, node: nodes.Step) -> EditCommand:
        hr = self._step_handrails(node)
        return hr

    def leave_step(self, node: nodes.Step) -> EditCommand:
        batch = self.leave_node(node)
        batch.items.insert(1, self._hr_info_zone_number(node.full_number, style="step"))
        batch = AppendBatch(batch.items)
        return batch

    def visit_math(self, node: nodes.Math) -> EditCommand:
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
                newline_outer=False,
            ),
        )
        sib.text = sib.text[1:]
        return batch

    def leave_math(self, node: nodes.Math) -> EditCommand:
        batch = self.leave_node(node)
        punct = getattr(node, "_trailing_punct", None)
        if not punct:
            return batch
        escaped = punct.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        batch.items.extend([AppendText(f"<span>{escaped}</span>"), AppendText("</span>")])
        return batch

    def visit_mathblock(self, node: nodes.MathBlock) -> EditCommand:
        # Preamble mathblocks are invisible — skip handrails, just emit hidden div
        if node.preamble:
            return super().visit_mathblock(node)

        batch = self._replace_node_with_handrails(
            node,
            collapse_in_hr=False,
            menu_label="Equation" if node.nonum else node.long_reftext,
        )
        handrail_idx = 0
        if isinstance(node.parent, nodes.Paragraph):
            batch.items.insert(0, AppendText("</p>"))
            handrail_idx = 1
        batch.items.append(AppendTextAndDefer("$$\n", "\n$$"))
        offset_class = ["hr-offset"] if isinstance(node.parent, nodes.Paragraph) else []
        batch.items[handrail_idx].classes += ["hr-hidden"] + offset_class
        return batch

    def leave_mathblock(self, node: nodes.MathBlock) -> EditCommand:
        batch = super().leave_mathblock(node)
        batch.items.insert(2, self._hr_info_zone_number(node.full_number, style="eqn"))
        return batch

    def visit_bibitem(self, node: nodes.Bibitem) -> EditCommand:
        batch = super().visit_bibitem(node)
        batch.items[0] = AppendNodeTag(node, "div")
        hr = self._wrap_batch_item_with_handrails(
            1,
            batch,
            include_content=False,
            classes=["hr-hidden"],
            icon="ext" if (node.doi or node.url) else None,
            collapse_in_hr=False,
            link=False,
            node=node,
        )

        # get the <a> tag already there...
        text = batch.items[1]._text
        pat = r'(<a.*?class="bibitem-(?:doi|url)".*?>).*?</a>'
        mobj = re.search(pat, text)
        if mobj is None:
            logger.warning("Unable to extract link from {node}")
            return hr

        # ...remove it from the content zone...
        left, right = mobj.span()
        hr.items[-4]._text = text[:left] + text[right:]

        # ...and add it to the info zone. The link is icon-only, so give it an
        # accessible name (WCAG link-name).
        opening = mobj.group(1)
        label = "DOI" if "bibitem-doi" in opening else "Link"
        opening = opening.replace(">", f' aria-label="{label}">', 1)
        hr.items[-2].content = (
            '<div class="hr-info">\n'
            + opening
            + "\n"
            + hr.items[-2].content[22:-6].strip()
            + "</a>\n</div>"
        )

        hr.items.insert(7, AppendText("<p>"))
        hr.items.insert(9, AppendText("</p>"))
        return hr
