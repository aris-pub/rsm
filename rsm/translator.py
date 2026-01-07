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
by ``rsm-make``.

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

    for i, match in enumerate(scripts):
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
            self.tag, self.id, self.classes, self.is_selectable, *self.custom_attrs
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
    ):
        self.node = node
        classes = [node.__class__.__name__.lower()] + [str(t) for t in node.types]
        classes = list(dict.fromkeys(classes + (additional_classes or [])))
        super().__init__(
            tag=tag,
            id=node.label,
            classes=classes,
            newline_inner=newline_inner,
            newline_outer=newline_outer,
            is_selectable=is_selectable,
            nodeid=node.nodeid,
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

    class Action(namedtuple("Action", "node action method")):
        def __repr__(self) -> str:
            classname = self.node.__class__.__name__
            return f'Action(node={classname}(), action="{self.action}")'

    def __init__(self, quiet: bool = False, asset_resolver=None):
        self.tree: nodes.Manuscript = None
        self.body: str = ""
        # Default to disk-based asset resolver if none provided
        if asset_resolver is None:
            from .asset_resolver import AssetResolverFromDisk

            asset_resolver = AssetResolverFromDisk()
        self.asset_resolver = asset_resolver
        self.deferred: list[EditCommand] = []
        self.quiet = quiet

    @classmethod
    def get_action_method(cls, node: nodes.Node, action: str) -> Callable:
        ogclass = node.__class__
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
        batch = AppendBatchAndDefer(
            [
                AppendOpenTag("body"),
                AppendOpenTag(classes=["manuscriptwrapper"]),
                AppendNodeTag(node),
                AppendOpenTag("section", classes=["level-1"]),
            ]
        )
        if node.title:
            batch.items.append(AppendHeading(1, node.title))
        return batch

    def visit_author(self, node: nodes.Author) -> EditCommand:
        if any([node.name, node.affiliation, node.email]):
            if node.email:
                email = (
                    _make_tag("a", id_="", classes="", href=f"mailto:{node.email}")
                    + node.email
                    + "</a>"
                )
            else:
                email = ""
            return AppendBatchAndDefer(
                [
                    AppendNodeTag(node),
                    AppendOpenTagManualClose("div", classes=["paragraph"]),
                    *[
                        AppendParagraph(str(x))
                        for x in [node.name, node.affiliation, email]
                        if x
                    ],
                    AppendText("</div>"),
                ]
            )
        else:
            return AppendNodeTag(node)

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
        if node.first_of_type(nodes.MathBlock):
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
        node.types.insert(0, f"level-{node.level}")
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
        return AppendBatchAndDefer(
            [
                AppendOpenTag(classes=["toc"]),
                AppendHeading(3, "Table of Contents"),
                AppendOpenTag(classes=["toc-wrapper"]),
                AppendNodeTag(node, "ul"),
            ]
        )

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
        # the strings r'\(' and r'\)' are MathJax's delimiters for inline math
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, "span", newline_inner=False, newline_outer=False),
                AppendTextAndDefer(r"\(", r"\)"),
            ]
        )

    def visit_mathblock(self, node: nodes.MathBlock) -> EditCommand:
        assert isinstance(node.parent, nodes.Paragraph)
        return AppendBatchAndDefer(
            [
                # A paragraph that contains a mathblock cannot _start_ with a mathblock,
                # so this mathblock must always contain some previous siblings that must
                # be enclosed in <p> tags.  (See comment in visit_paragraph().)
                AppendText("</p>"),
                # This is the actual tag corresponding to the mathblock.
                AppendNodeTag(node, "div"),
                # The contents of a mathblock must be enclosed in '$$' and '$$' due to
                # how MathJax works.
                AppendTextAndDefer("$$\n", "\n$$"),
            ]
        )

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
        return AppendNodeTag(node, tag="span", newline_inner=False)

    def visit_codeblock(self, node: nodes.CodeBlock) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, "div", newline_inner=True, newline_outer=True),
                AppendOpenTag("pre"),
            ]
        )

    def visit_algorithm(self, node: nodes.Algorithm) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendOpenTag(id=node.label, classes=["algorithm"]),
                AppendOpenTag("pre", classes=["pseudocode"]),
            ]
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
                AppendNodeTag(
                    node, tag="span", newline_inner=False, newline_outer=False
                ),
                *commands,
            ]
        )

    def visit_construct(self, node: nodes.Construct) -> EditCommand:
        return AppendNodeTag(node, tag="span", newline_inner=False, newline_outer=False)

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
        classes = node.types
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
            if "external" not in node.types:
                node.types.append("external")

            return AppendText(self._make_ahref_tag_text(node, node.target, href))
        else:
            # Internal reference (existing behavior)
            return AppendText(
                self._make_ahref_tag_text(node, node.target, f"#{node.target.label}")
            )

    def visit_url(self, node: nodes.URL) -> EditCommand:
        return AppendText(
            self._make_ahref_tag_text(node, node.target, f"{node.target}")
        )

    def visit_claimblock(self, node: nodes.ClaimBlock) -> EditCommand:
        return AppendNodeTag(node)

    def _make_title_node(
        self, label: str, desc: str = "", types: list = ["hr-label"]
    ) -> nodes.Node:
        para = nodes.Paragraph(types=types)
        if label:
            span = nodes.Span(types=["label"])
            span.append(nodes.Text(text=label))
            para.append(span)
        if desc:
            span = nodes.Span(types=["desc"])
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
        classname = node.__class__.__name__.lower()
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
            last.types.append("last")

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
            text = ", ".join(tags)
            text = f'<span id="{node.label}">{text}</span>'
        return AppendText(f"[{text}]")

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

    def _detect_content_type_and_render(self, node: nodes.Asset) -> str:
        """Detect content type from path and return appropriate HTML."""
        path_str = str(node.path).lower()

        # Image files
        if any(
            path_str.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg"]
        ):
            return _make_tag(
                "img",
                id_=node.label,
                classes=[],
                src=node.path,
                alt=f"{node.__class__.__name__} {node.full_number}.",
                onload="" if node.scale == 1.0 else f"this.width*={node.scale};",
            )

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
            content = self.asset_resolver.resolve_asset(str(node.path))
            if content is None:
                return f'<div class="html-error">Unable to load HTML asset: {node.path}</div>'

            # Check if this is a full HTML document vs simple content
            is_full_html_doc = content.strip().lower().startswith(
                "<html"
            ) or content.strip().lower().startswith("<!doctype")

            if is_full_html_doc:
                # Full HTML document - extract body content and process scripts
                processed = _process_html_with_scripts(content)
            else:
                # Simple HTML content - use as-is (for existing RSM behavior)
                processed = content

            return processed

        # Default to image behavior
        else:
            return _make_tag(
                "img",
                id_=node.label,
                classes=[],
                src=node.path,
                alt=f"{node.__class__.__name__} {node.full_number}.",
                onload="" if node.scale == 1.0 else f"this.width*={node.scale};",
            )

    def visit_figure(self, node: nodes.Figure) -> EditCommand:
        return AppendBatchAndDefer(
            [
                AppendNodeTag(node, "figure"),
                AppendText(self._detect_content_type_and_render(node)),
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
            ]
        )

    def visit_caption(self, node: nodes.Caption) -> EditCommand:
        parent = node.parent
        caption = AppendOpenCloseTag(
            tag="span",
            content=f"{parent.__class__.__name__} {parent.full_number}. ",
            classes=["label"],
            newline_inner=False,
            newline_outer=False,
        )
        return AppendBatchAndDefer(
            [
                AppendOpenTag(
                    "figcaption" if isinstance(parent, nodes.Asset) else "caption"
                ),
                caption,
            ]
        )

    def visit_appendix(self, node: nodes.Appendix) -> EditCommand:
        # Appendix nodes are used during the transform phase, but do not apear in the
        # output in any way.
        return AppendText("")

    def visit_table(self, node: nodes.Table) -> EditCommand:
        return AppendNodeTag(node, "table")

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
        "ext": """<svg width="15" height="15" viewBox="3 3 18 18" fill="none" stroke="#3C4952" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
          <path d="M12 6h-6a2 2 0 0 0 -2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-6" />
          <path d="M11 13l9 -9" />
          <path d="M15 4h5v5" />
        </svg>""",
    }

    def __init__(
        self,
        quiet: bool = False,
        add_source: bool = True,
        asset_resolver=None,
    ):
        super().__init__(quiet, asset_resolver)
        self.add_source = add_source

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
    ) -> EditCommand:
        classes = (classes or []) + ["hr"] + (["hr-offset"] if depth > 0 else [])
        classes = list(dict.fromkeys(classes))  # deletes duplicates AND preserves order
        return (
            AppendOpenTag(classes=classes, is_selectable=True)
            if include_content
            else AppendOpenTagManualClose(classes=classes, is_selectable=True)
        )

    def _hr_collapse_zone(self, collapsible: bool) -> AppendOpenCloseTag:
        if collapsible:
            content = """
            <div class="hr-collapse">
              <div class="icon collapse">
              </div>
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
    <span class="icon {icon}">
    </span>
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

    def _hr_menu_item_tree(self, disabled: bool = False) -> str:
        return self._make_menu_item(
            classes=(["disabled"] if disabled else []), icon="tree", text="Tree"
        )

    def _hr_menu_item_code(self, disabled: bool = False) -> str:
        return self._make_menu_item(
            classes=(["disabled"] if disabled else []), icon="code", text="Source"
        )

    def _hr_menu_zone(
        self,
        label: str = "",
        collapse: bool | Literal["disabled"] = False,
        collapse_all: bool | Literal["disabled"] = False,
        link: bool | Literal["disabled"] = True,
        tree: bool | Literal["disabled"] = True,
        code: bool | Literal["disabled"] = True,
    ) -> AppendOpenCloseTag:
        start, end = '\n<div class="hr-menu">', "\n</div>\n"
        middle = ""
        if label:
            middle = middle + "\n" + self._hr_menu_label(label) + self._hr_menu_sep()
        if collapse:
            middle = (
                middle
                + "\n"
                + self._hr_menu_item_collapse(disabled=collapse == "disabled")
            )
        if collapse_all:
            middle = (
                middle
                + "\n"
                + self._hr_menu_item_collapse_all(disabled=collapse_all == "disabled")
            )
        if collapse or collapse_all:
            middle = middle + self._hr_menu_sep()
        if link:
            middle = (
                middle + "\n" + self._hr_menu_item_link(disabled=link == "disabled")
            )
        if tree:
            middle = (
                middle + "\n" + self._hr_menu_item_tree(disabled=tree == "disabled")
            )
        if code:
            middle = (
                middle + "\n" + self._hr_menu_item_code(disabled=code == "disabled")
            )
        if middle.startswith("\n"):
            middle = middle[1:]
        return AppendOpenCloseTag(
            tag="div",
            content="\n".join([start, middle, end]),
            classes=["hr-menu-zone"],
        )

    def _hr_menu_zone_empty(self) -> AppendOpenCloseTag:
        return AppendOpenCloseTag(tag="div", content="", classes=["hr-menu-zone"])

    def _hr_border_zone(self) -> AppendOpenCloseTag:
        return AppendOpenCloseTag(
            tag="div",
            content="""
                <div class="hr-border-dots">
                  <div class="icon dots">
                  </div>
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
                <div class="icon {icon}">
                </div>
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
    ):
        classes = (
            (node.types or [])
            + ["hr"]
            + (["hr-hidden"] if node.handrail_depth == 2 else [])
            + (["hr-offset"] if node.handrail_depth > 0 else [])
            + (additional_classes or [])
        )
        classes = list(dict.fromkeys(classes))  # deletes duplicates AND preserves order
        return AppendNodeTag(
            node, additional_classes=classes, is_selectable=is_selectable
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
        handrail = self._hr_from_node(node, additional_classes)
        hr_content_zone = self._hr_content_zone(True)
        newitems = [
            handrail,
            self._hr_collapse_zone(collapse_in_hr),
            self._hr_menu_zone(
                label=menu_label or node.reftext,
                collapse=collapse_in_menu,
                collapse_all=collapse_all_in_menu,
                link=(True if node.label else "disabled"),
            ),
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
            menu_zone = self._hr_menu_zone(
                label=node.reftext,
                collapse="disabled",
                collapse_all="disabled",
                link=link,
            )
        elif sub and sub.first_of_type(nodes.Step) is None:
            menu_zone = self._hr_menu_zone(
                label=node.reftext, collapse=True, collapse_all="disabled", link=link
            )
        else:
            menu_zone = self._hr_menu_zone(
                label=node.reftext, collapse=True, collapse_all=True, link=link
            )
        newitems = [
            self._hr_from_node(node),
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
    ):
        handrail = self._hr(include_content, depth, classes)
        hr_content_zone = self._hr_content_zone(include_content)

        newitems = [
            handrail,
            self._hr_collapse_zone(collapse_in_hr),
            self._hr_menu_zone(label=menu_label, link=link),
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

    def _make_source_div(self):
        return AppendText(text=f'<div class="rsm-source hide">{self.tree.src}</div>')

    def _make_minimap(
        self, node: nodes.Contents, follow: str, with_ids: bool = False
    ) -> EditCommand:
        radii = {nodes.Section: 8, nodes.Subsection: 6, nodes.Subsubsection: 4}
        num = 0
        circles = []
        for ref in node.traverse(nodeclass=nodes.Reference):
            cy = 20 + (24 + 8) * num
            r = radii[type(ref.target)]
            id_ = f"mm-{ref.target.label}"
            if with_ids:
                circles.append(
                    f'<a href="#{ref.target.label}" class="reference" tabindex="-1">'
                    f'<circle id="{id_}" cx="16" cy="{cy}" r="{r}" data-pos="{cy}" />'
                )
            else:
                circles.append(f'<circle cx="16" cy="{cy}" r="{r}" data-pos="{cy}" />')
            circle = f'<circle cx="16" cy="{cy}" r="{r - 4}" fill="#FCFEFF" data-pos="{cy}" />'
            if with_ids:
                circles.append(circle + "</a>")
            else:
                circles.append(circle)
            num += 1
        height = max(num * (24 + 8) + 8, 48)
        svg_start = f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 {height}" fill="#3C4952" preserveAspectRatio="xMinYMid meet" stroke-width="0">
          <defs>

            <linearGradient id="purple-green-{follow}" x1="0%" x2="0%" y1="0%" y2="100%" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stop-color="#AD71F2" />
              <stop id="stop-follow-{follow}-1" offset="100%" stop-color="#1FB5A2" />
              <stop id="stop-follow-{follow}-2" offset="100%" stop-color="#DAE1E5" />
              <stop offset="100%" stop-color="#DAE1E5" />
            </linearGradient>

            <mask id="gradient-mask">
              <rect width="100%" height="100%" fill="url(#purple-green-{follow})" />
            </mask>

          </defs>

          <g fill="url(#purple-green-{follow})">
            <rect x="14" y="24" width="4" height="{height - 48}" />\n    """
        svg_middle = "\n    ".join(circles)
        svg_end = "</g>\n</svg>"
        svg = svg_start + svg_middle + svg_end
        minimap = AppendOpenTagManualClose(classes=["minimap"])
        batch = AppendBatch([minimap, AppendText(svg), minimap.close_command()])
        return batch

    def visit_manuscript(self, node: nodes.Manuscript) -> EditCommand:
        batch = super().visit_manuscript(node)
        if node.title:
            batch = self._wrap_batch_item_with_handrails(
                4, batch, classes=["heading"], menu_label="Title", link=True
            )
        if self.add_source:
            batch.items.insert(2, self._make_source_div())
        if toc := node.first_of_type(nodes.Contents):
            batch.items = (
                batch.items[:3]
                + [AppendText('<div class="float-minimap-wrapper">')]
                + self._make_minimap(toc, follow="scroll", with_ids=True).items
                + [AppendText("</div>")]
                + batch.items[3:]
            )
        return batch

    def visit_author(self, node: nodes.Author) -> EditCommand:
        batch = super().visit_author(node)
        hr = self._replace_node_with_handrails(
            node, additional_classes=["hr-hidden"], collapse_in_hr=False
        )
        hr.items += batch.items[2:-1]
        return hr

    def leave_author(self, node: nodes.Author) -> EditCommand:
        batch = super().leave_node(node)
        batch.items.insert(-1, self._hr_info_zone_icon(getattr(node, "icon", None)))
        return batch

    def visit_section(self, node: nodes.Section) -> EditCommand:
        batch = super().visit_section(node)
        return self._wrap_batch_item_with_handrails(
            1,
            batch,
            icon=getattr(node, "icon", None),
            classes=["heading"],
            menu_label=node.reftext,
            link=True if node.label else "disabled",
        )

    def visit_abstract(self, node: nodes.Abstract) -> EditCommand:
        batch = super().visit_abstract(node)
        return self._wrap_batch_item_with_handrails(
            1,
            batch,
            classes=["heading"],
            menu_label=node.reftext,
            link=True if node.label else "disabled",
        )

    def visit_contents(self, node: nodes.Contents) -> EditCommand:
        batch = super().visit_contents(node)
        batch = self._wrap_batch_item_with_handrails(
            1,
            batch,
            classes=["heading"],
            menu_label=node.reftext,
            link=True if node.label else "disabled",
        )
        batch.items = (
            batch.items[:-1]
            + self._make_minimap(node, follow="mouse").items
            + [batch.items[-1]]
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

    def visit_caption(self, node: nodes.Caption) -> EditCommand:
        parent = node.parent
        caption_label = AppendOpenCloseTag(
            tag="span",
            content=f"{parent.__class__.__name__} {parent.full_number}. ",
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

        return AppendBatchAndDefer(
            [
                AppendOpenTag(
                    "figcaption" if isinstance(parent, nodes.Asset) else "caption",
                    classes=figcaption_classes,
                    is_selectable=True,
                    tabindex=0,
                ),
                self._hr_collapse_zone(collapsible=False),
                self._hr_menu_zone(
                    label="Caption",
                    link=(True if node.label else "disabled"),
                ),
                self._hr_border_zone(),
                self._hr_spacer_zone(),
                AppendOpenTag("div", classes=["hr-content-zone"]),
                caption_label,
            ]
        )

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
        cmd = super().visit_codeblock(node)
        batch = self._replace_node_with_handrails(node, collapse_in_hr=False)
        if "hr-hidden" not in batch.items[0].classes:
            batch.items[0].classes.append("hr-hidden")
        batch = AppendBatchAndDefer([*batch.items, *cmd.items[1:]])
        return batch

    @auto_leave_deferred
    def leave_codeblock(self, node: nodes.CodeBlock, base_batch) -> EditCommand:
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
        if not sib.text.startswith("."):
            return batch

        # We reach this branch only if the Math node is immediately followed by Text
        # that starts with a dot "."; in this case, the math and the dot may be
        # separated if the browser's viewport is too narrow, which looks ugly.  The only
        # way to fix it is to wrap the math and the dot in a span, and remove the dot
        # from the subsequent text.  The span is then dealt with using CSS.
        node._followed_by_dot = True
        batch.items.insert(
            0,
            AppendOpenTagManualClose(
                tag="span",
                classes=["inline-math-wrapper"],
                newline_outer=False,
            ),
        )
        sib.text = sib.text[1:]
        return batch

    def leave_math(self, node: nodes.Math) -> EditCommand:
        batch = self.leave_node(node)
        if not getattr(node, "_followed_by_dot", False):
            return batch
        batch.items.extend([AppendText("<span>.</span>"), AppendText("</span>")])
        return batch

    def visit_mathblock(self, node: nodes.MathBlock) -> EditCommand:
        batch = self._replace_node_with_handrails(
            node,
            collapse_in_hr=False,
            menu_label="Equation" if node.nonum else node.long_reftext,
        )
        batch.items.insert(0, AppendText("</p>"))
        batch.items.append(AppendTextAndDefer("$$\n", "\n$$"))
        batch.items[1].classes += ["hr-hidden", "hr-offset"]
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
            icon="ext",
            collapse_in_hr=False,
            link=False,
        )

        # get the <a> tag already there...
        text = batch.items[1]._text
        pat = r'(<a.*?class="bibitem-doi".*?>).*?</a>'
        mobj = re.search(pat, text)
        if mobj is None:
            logger.warning("Unable to extract link from {node}")
            return hr

        # ...remove it from the content zone...
        left, right = mobj.span()
        hr.items[-4]._text = text[:left] + text[right:]

        # ...and add it to the info zone.
        hr.items[-2].content = (
            '<div class="hr-info">\n'
            + mobj.group(1)
            + "\n"
            + hr.items[-2].content[22:-6].strip()
            + "</a>\n</div>"
        )

        hr.items.insert(7, AppendText("<p>"))
        hr.items.insert(9, AppendText("</p>"))
        return hr
