"""Nodes that make up the manuscript tree.

The manuscript tree semantically represents each element in the manuscript such as
sections, paragraphs, special regions, figures, etc.

This is opposed to the syntax tree output by tree-sitter whose nodes represent elements
with syntactic meaning such as tags, delimiters, etc.

There are two main classes of interest: :class:`Node` and :class:`NodeWithChildren`.
They implement 95% of the entire API of this module.  Other classes are mostly dummy
subclasses whose only purpose is to differentiate themselves from others via their type.

"""

import logging
import textwrap
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import (
    Any,
    Callable,
    ClassVar,
    Generator,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

from icecream import ic

logger = logging.getLogger("RSM").getChild("nodes")

NodeSubType = TypeVar("NodeSubType", bound="Node")


class RSMNodeError(Exception):
    pass


class Node:
    """A node in the manuscript tree.

    A node represents a semantically meaningful element of the manuscript.

    Parameters
    ----------
    label
        Unique identifier for this node.
    types
        Types of this node.
    number
        Node number.
    nonum
        Whether this node should be automatically given a number.
    reftext_template
        If not empty, replaces :attr:`classreftext`.

    See Also
    --------
    :class:`Manuscript` : The class of the root node of a manuscript tree.
    :class:`NodeWithChildren` : Subclass that implements methods to handle children.

    Notes
    -----
    An instance of Node cannot have children.  Only instances of (subclasses) of
    :class:`NodeWithChildren` may have them.  However, for the sake of having a uniform
    API, Node implements the property :attr:`children`, which always returns an empty
    tuple.

    """

    classreftext: ClassVar[str] = "{nodeclass} {number}"

    possible_parents: ClassVar[set[Type["NodeWithChildren"]]] = set()
    """Allowed types of parent Nodes.

    When setting the parent of a Node, this attribute is checked to see whether the
    intended parent has an admissible type.

    Examples
    --------
    This is a class variable

    >>> nodes.Item.possible_parents == {nodes.Itemize, nodes.Enumerate, nodes.Contents}
    True

    This variable is checked when setting the parent directly.

    >>> it = nodes.Item()
    >>> it.parent = nodes.Paragraph()
    Traceback (most recent call last):
    rsm.nodes.RSMNodeError: Node of type <class 'rsm.nodes.Item'> cannot have parent of type <class 'rsm.nodes.Paragraph'>

    This is also used when setting the parent in some other indirect way, for example
    when calling :meth:`~NodeWithChildren.append` on the desired parent.

    >>> nodes.Paragraph().append(it)
    Traceback (most recent call last):
    rsm.nodes.RSMNodeError: Node of type <class 'rsm.nodes.Item'> cannot have parent of type <class 'rsm.nodes.Paragraph'>

    Allowed parents proceed without raising.

    >>> nodes.Itemize().append(it)
    Itemize(parent=None, [Item])

    """

    autonumber: ClassVar[bool] = False
    """Whether to automatically assign a number to this node during transform step.

    Examples
    --------
    >>> msc, thm1, thm2 = nodes.Manuscript(), nodes.Theorem(), nodes.Theorem()
    >>> (thm1.number, thm2.number) == (None, None)
    True
    >>> tform = rsm.transformer.Transformer()
    >>> tform.transform(msc.append([thm1, thm2]))  # doctest: +IGNORE_RESULT
    >>> thm1.number, thm2.number
    (1, 2)

    """

    _number_within: ClassVar[Optional[Type["Node"]]] = None
    # see property number_within for documentation

    _number_as: ClassVar[Optional[Type["Node"]]] = None
    # see property number_as for documentation

    newmetakeys: ClassVar[set] = {"label", "types", "nonum", "reftext"}
    """Meta keys to add to those of the parent class.

    .. important::
       Only use this when defining a new Node subclass.  When dealing with Node
       isntances, do not access this attribute directly neither for reading nor writing.
       Always use :meth:`metakeys` in that case.

    See Also
    --------
    :meth:`metakeys`

    Examples
    --------
    The keys in `newmetakeys` are added to the meta keys of the parent class.

    >>> nodes.Heading.newmetakeys
    {'title'}
    >>> nodes.Heading.metakeys() == nodes.Node.metakeys() | {"title"}
    True

    The intended use, and only supported use, of `newmetakeys` is at the time of class
    definition.

    >>> class NewNode(nodes.Node):
    ...     newmetakeys = {"newkey"}
    >>> NewNode.metakeys() == nodes.Node.metakeys() | {"newkey"}
    True

    """

    has_handrail: ClassVar[bool] = False
    """Whether nodes of this class are rendered with a handrail."""

    def __init__(
        self,
        label: str = "",
        types: Optional[list[str]] = None,
        number: Optional[int] = None,
        nonum: bool = False,
        reftext_template: str = "",
        start_point: tuple[int, int] = (-1, -1),
        end_point: tuple[int, int] = (-1, -1),
    ) -> None:
        self.nodeid: str | None = None
        """Node id - always exists (unlike label), automatically assigned, unique within the tree."""
        self.label: str = label
        """Unique identifier."""
        self.types: list[str] = types or []
        """Types of this node."""
        self.handrail_depth = 0
        """The number of ancestors of this node that have a handrail."""
        self.number: Optional[int] = number
        """Node number."""
        self.nonum: bool = nonum
        """Whether this node should be automatically given a number."""
        self.reftext_template: str = reftext_template or self.classreftext
        """Reftext template, or "" to use :attr:`classreftext`."""
        self.start_point: tuple[int, int] = start_point
        """The start point of the corresponding concrete syntax tree node."""
        self.end_point: tuple[int, int] = end_point
        """The end point of the corresponding concrete syntax tree node."""
        self._parent: Optional["NodeWithChildren"] = None

    def _attrs_for_repr_and_eq(self) -> list[str]:
        return ["label", "types", "nonum", "number", "parent"]

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        d = {
            att: getattr(self, att)
            for att in self._attrs_for_repr_and_eq()
            if att != "children"
        }
        d["parent"] = (
            "None" if self.parent is None else f"{self.parent.__class__.__name__}"
        )
        d_str = ", ".join(f"{k}={v}" for k, v in d.items() if v)
        return f"{cls}({d_str})"

    def __eq__(self, other: Any) -> bool:
        attrs = self._attrs_for_repr_and_eq()
        try:
            return all(
                (mine is getattr(other, a))
                if isinstance(mine := getattr(self, a), Node)
                else (mine == getattr(other, a))
                for a in attrs
            )
        except AttributeError:
            return False

    def sexp(
        self,
        tab_width: int = 2,
        meta: bool = False,
        ignore_meta_keys: Optional[set] = None,
    ) -> str:
        """Represent this node as an S expression.

        Parameters
        ----------
        tab_width
            How many spaces of indentation at each depth level.
        meta
            Whether to include meta in the output.
        ignore_meta_keys
            When `meta` is ``True``, this controls which meta keys to include.

        Returns
        -------
        A string representation of the Node and its descendents.

        See Also
        --------
        :meth:`traverse`

        Examples
        --------
        >>> p1, p2, p3, p4 = [nodes.Paragraph().append(nodes.Text()) for _ in range(4)]
        >>> msc = nodes.Manuscript().append(
        ...     [
        ...         nodes.Section().append(p1),
        ...         nodes.Section().append([nodes.Subsection().append([p2, p3])]),
        ...         nodes.Section().append(p4),
        ...     ]
        ... )

        By default, meta keys are not included in the output.

        >>> print(msc.sexp())
        (Manuscript
          (Section
            (Paragraph
              (Text)))
          (Section
            (Subsection
              (Paragraph
                (Text))
              (Paragraph
                (Text))))
          (Section
            (Paragraph
              (Text))))

        :meth:`sexp` is useful when transforming the tree.

        >>> p3.replace_self(nodes.Paragraph().append(nodes.Span(strong=True).append(nodes.Text())))
        >>> print(msc.sexp())
        (Manuscript
          (Section
            (Paragraph
              (Text)))
          (Section
            (Subsection
              (Paragraph
                (Text))
              (Paragraph
                (Span
                  (Text)))))
          (Section
            (Paragraph
              (Text))))

        Output meta for even more debugging information.

        >>> print(msc.sexp(meta=True))
        (Manuscript { :reftext: Manuscript }
          (Section { :reftext: Section }
            (Paragraph { :reftext: Paragraph }
              (Text { :reftext: Text })))
          (Section { :reftext: Section }
            (Subsection { :reftext: Section }
              (Paragraph { :reftext: Paragraph }
                (Text { :reftext: Text }))
              (Paragraph { :reftext: Paragraph }
                (Span { :reftext: Span, :strong: True }
                  (Text { :reftext: Text })))))
          (Section { :reftext: Section }
            (Paragraph { :reftext: Paragraph }
              (Text { :reftext: Text }))))

        Use `ignore_meta_keys` for a less verbose output.

        >>> print(msc.sexp(meta=True, ignore_meta_keys={"reftext"}))
        (Manuscript {  }
          (Section {  }
            (Paragraph {  }
              (Text {  })))
          (Section {  }
            (Subsection {  }
              (Paragraph {  }
                (Text {  }))
              (Paragraph {  }
                (Span { :strong: True }
                  (Text {  })))))
          (Section {  }
            (Paragraph {  }
              (Text {  }))))

        """
        ignore_meta_keys = set() if ignore_meta_keys is None else set(ignore_meta_keys)
        exp = ""
        stack = [(0, self)]
        while stack:
            indent, node = stack.pop()
            if node is None:
                exp += ")"
                continue
            spaces = " " * indent
            exp += f"\n{spaces}({node.__class__.__name__}"
            if meta:
                meta_str = (
                    "{ "
                    + ", ".join(
                        [
                            f":{key}: {val}"
                            for key in sorted(node.metakeys())
                            if key not in ignore_meta_keys
                            and (val := getattr(node, key))
                        ]
                    )
                    + " }"
                )
                exp += f" {meta_str}"
            stack.append((None, None))
            if node.children:
                stack += [(indent + tab_width, c) for c in reversed(node.children)]
        return exp[1:]  # get rid of an extra newline at the start

    @classmethod
    def metakeys(cls: Type["Node"]) -> set[str]:
        """The valid meta keys of the given class.

        Returns
        -------
        The valid meta keys.

        Examples
        --------
        >>> all_nodes_meta = {"label", "types", "nonum", "reftext"}
        >>> nodes.Node.metakeys() == all_nodes_meta
        True
        >>> nodes.Span.metakeys() - all_nodes_meta == {"strong", "emphas", "little", "insert", "delete"}
        True
        >>> nodes.Author.metakeys()  - all_nodes_meta == {"name", "affiliation", "email"}
        True

        """
        return cls.newmetakeys.union(
            *[b.metakeys() for b in cls.__bases__ if hasattr(b, "metakeys")]
        )

    @property
    def parent(self) -> Optional["NodeWithChildren"]:
        """The parent of this Node, or None."""
        return self._parent

    @parent.setter
    def parent(self, node: Optional["NodeWithChildren"]) -> None:
        if node is None:
            self._parent = None
        elif not self.__class__.possible_parents:
            self._parent = node
        else:
            possible_parents = self.__class__.possible_parents
            if possible_parents and type(node) not in possible_parents:
                raise RSMNodeError(
                    f"Node of type {type(self)} cannot have parent of type {type(node)}"
                )
            self._parent = node

    @property
    def children(self) -> tuple:
        """Tuple with this Node's children."""
        return tuple()  # necessary for methods such as Nodes.traverse

    @property
    def number_within(self) -> Type["Node"]:
        return self.__class__._number_within or Manuscript

    @property
    def number_as(self) -> Type["Node"]:
        return self._number_as or self.__class__

    @property
    def full_number(self) -> str | None:
        if self.nonum:
            return None
        ancestor = self.first_ancestor_of_type(self.number_within)
        if not ancestor:
            logger.warning(
                f"{self.__class__.__name__} numbered within "
                f"{self.number_within} but no such ancestor was found; "
                "using root node instead"
            )
            ancestor = self.first_ancestor_of_type(Manuscript)
        if ancestor and ancestor.full_number:
            return f"{ancestor.full_number}.{self.number}"
        return f"{self.number}" if self.number else ""

    @property
    def reftext(self) -> str:
        return self.reftext_template.format(
            nodeclass=self.__class__.__name__, number=self.full_number
        ).strip()

    def traverse(
        self,
        *,
        condition: Optional[Callable[["Node"], bool]] = None,
        nodeclass: Optional[type["Node"]] = None,
    ) -> Generator[NodeSubType, None, None]:
        """Generate the descendents of this Node in depth-first order.

        By default, yield this node and then every descendent in depth-first order.  If
        `condition` is given, yield only those Nodes that satisfy the condition.  If
        `nodeclass` is given, it overrides `condition` and only those descendents of the
        specified type are yielded.

        Parameters
        ----------
        condition
            Callable that receives a single argument, a descendent Node, and returns
            whether it should be yielded.
        nodeclass
            A Node subclass of the desired yielded descendent Nodes.  If not None,
            `condition` is ignored.

        Yields
        -------
        :class:`Node`

        See Also
        --------
        :meth:`sexp`

        Notes
        -----
        Passing ``nodeclass=<NodeSubType>`` is equivalent to passing ``condition=lambda
        n: isinstance(n, <NodeSubType>)``.

        Examples
        --------
        >>> p1, p2, p3, p4 = [nodes.Paragraph().append(nodes.Text()) for _ in range(4)]
        >>> msc = nodes.Manuscript().append(
        ...     [
        ...         nodes.Section().append(p1),
        ...         nodes.Section().append([nodes.Subsection().append([p2, p3])]),
        ...         nodes.Section().append(p4),
        ...     ]
        ... )

        Visit every descendent, including self.

        >>> for n in msc.traverse(): print(n)
        Manuscript(parent=None, [Section, Section, Section])
        Section(parent=Manuscript, [Paragraph])
        Paragraph(parent=Section, [Text])
        Text("")
        Section(parent=Manuscript, [Subsection])
        Subsection(parent=Section, [Paragraph, Paragraph])
        Paragraph(parent=Subsection, [Text])
        Text("")
        Paragraph(parent=Subsection, [Text])
        Text("")
        Section(parent=Manuscript, [Paragraph])
        Paragraph(parent=Section, [Text])
        Text("")

        Use `nodeclass` to yield only nodes of a specified type.  Note that subclasses
        are also yielded.

        >>> for n in msc.traverse(nodeclass=nodes.Section): print(n)
        Section(parent=Manuscript, [Paragraph])
        Section(parent=Manuscript, [Subsection])
        Subsection(parent=Section, [Paragraph, Paragraph])
        Section(parent=Manuscript, [Paragraph])

        Yield only nodes satisfying an arbitrary condition

        >>> msc.children[1].nonum = True
        >>> for n in msc.traverse(condition=lambda n: n.nonum): print(n)
        Section(nonum=True, parent=Manuscript, [Subsection])

        """
        if condition is None:
            condition = lambda n: True
        if nodeclass is not None:
            if issubclass(nodeclass, Node):
                condition = lambda n: isinstance(n, nodeclass)
            else:
                raise RSMNodeError("nodeclass must inherit from Node")

        stack = [self]
        while stack:
            node = stack.pop()
            if condition(node):
                yield cast(NodeSubType, node)
            stack += node.children[::-1]

    def first_of_type(
        self, cls: Union[Type["Node"], tuple[Type["Node"]]], return_idx: bool = False
    ) -> Union[Optional["Node"], tuple[Optional["Node"], Optional[int]]]:
        """First child of the specified type.

        Parameters
        ----------
        cls
            Desired class of the child.
        return_idx
            Whether to return the index of the child among this node's children.

        Returns
        -------
        Node
            The first child of the specified type, or None.
        Node, int
            If `return_idx` is True, return (child, index), or (None, None).


        See Also
        --------
        :meth:`last_of_type`
        :meth:`first_ancestor_of_type`

        Examples
        --------
        >>> p = nodes.Paragraph().append([nodes.Text("one"), nodes.Text("two")])
        >>> p.first_of_type(nodes.Text)
        Text("one")
        >>> p.first_of_type(nodes.Text, return_idx=True)
        (Text("one"), 0)

        The index counts all existing children.

        >>> p.prepend(nodes.Span())
        Paragraph(parent=None, [Span, Text, Text])
        >>> p.first_of_type(nodes.Text, return_idx=True)
        (Text("one"), 1)

        """
        for idx, child in enumerate(self.children):
            if isinstance(child, cls):
                return (child, idx) if return_idx else child
        return (None, None) if return_idx else None

    def last_of_type(
        self, cls: Union[Type["Node"], tuple[Type["Node"]]], return_idx: bool = False
    ) -> Union[Optional["Node"], tuple[Optional["Node"], Optional[int]]]:
        """Last child of the specified type.

        For details, see :meth:`first_of_type`.

        Examples
        --------
        >>> p = nodes.Paragraph().append([nodes.Span(), nodes.Text("one"), nodes.Text("two")])
        >>> p.last_of_type(nodes.Text, return_idx=True)
        (Text("two"), 2)

        """
        for idx, child in enumerate(reversed(self.children)):
            if isinstance(child, cls):
                return (child, len(self.children) - idx - 1) if return_idx else child
        return (None, None) if return_idx else None

    def prev_sibling(
        self, cls: Union[Type["Node"], str, None] = None
    ) -> Optional["Node"]:
        """The previous sibling, optionally of a specified type.

        Parameters
        ----------
        cls
            The type of the desired sibling.  If ``"self"``, search for the previous
            sibling with the same type as this node.  If ``None``, return the
            immediately preceding sibling, regardless of its type.

        Returns
        -------
            The desired sibling, or None.

        See Also
        --------
        :meth:`first_ancestor_of_type`
        :meth:`next_sibling`

        Examples
        --------
        >>> p, s, t1, t2 = nodes.Paragraph(), nodes.Span(), nodes.Text("one"), nodes.Text("two")
        >>> p.append([t1, s, t2])  # doctest: +IGNORE_RESULT
        >>> t2.prev_sibling()
        Span(parent=Paragraph)
        >>> t2.prev_sibling(nodes.Text)
        Text("one")
        >>> t1.prev_sibling() is None
        True

        Use ``"self"`` to find nodes of the same type.

        >>> s2 = nodes.Span()
        >>> p.append(s2)
        Paragraph(parent=None, [Text, Span, Text, Span])
        >>> s2.prev_sibling() is t2
        True
        >>> s2.prev_sibling("self") is s
        True

        """
        if self.parent is None:
            return None

        ids = [id(c) for c in self.parent.children]
        index = ids.index(id(self))

        if cls is None and index:
            return self.parent.children[index - 1]

        if cls == "self":
            cls = self.__class__
        cls = cast(Type["Node"], cls)

        prev_sibs = self.parent.children[:index]
        for node in reversed(prev_sibs):
            if isinstance(node, cls):
                return node
        return None

    def next_sibling(self, cls: Optional[Type["Node"]] = None) -> Optional["Node"]:
        """The next sibling, optionally of a specified type.

        For details, see :meth:`prev_sibling`.

        See Also
        --------
        :meth:`prev_sibling`

        """
        if self.parent is None:
            return None

        ids = [id(c) for c in self.parent.children]
        index = ids.index(id(self))

        if cls is None and index < len(self.parent.children) - 1:
            return self.parent.children[index + 1]

        if cls == "self":
            cls = self.__class__
        cls = cast(Type["Node"], cls)

        next_sibs = self.parent.children[index + 1 :]
        for node in next_sibs:
            if isinstance(node, cls):
                return node
        return None

    def first_ancestor_of_type(
        self, cls: Union[Type["Node"], tuple[Type["Node"]]]
    ) -> Optional["Node"]:
        """First ancestor of the specified type.

        Parameters
        ----------
        cls
            Desired class of the ancestor.

        Returns
        -------
        The first ancestor of the specified type, or None.

        See Also
        --------
        :attr:`parent`
        :meth:`first_of_type`

        Examples
        --------
        Given the tree

        >>> t = nodes.Text("Hello")
        >>> p = nodes.Paragraph().append(nodes.Span().append(t))
        >>> print(p.sexp())
        (Paragraph
          (Span
            (Text)))

        Find an ancestor of a desired type.

        >>> t.first_ancestor_of_type(nodes.Paragraph)
        Paragraph(parent=None, [Span])

        Always check the return value against ``None``.

        >>> t.first_ancestor_of_type(nodes.Manuscript) is None
        True

        """
        ancestor = self.parent
        # We use `type is not cls` instead of the recommended `isinstance()` because we
        # are looking for an exact type, not a subtype.  For example, we may want to
        # find the enclosing Section of a Theorem, bypassing any Subsections that may
        # lie in between.
        while ancestor and (
            all(type(ancestor) is not c for c in cls)
            if isinstance(cls, tuple)
            else (type(ancestor) is not cls)
        ):
            ancestor = ancestor.parent
        return ancestor  # the root node has parent None

    def get_child_by_id(self, nodeid: int) -> Optional["Node"]:
        for node in self.traverse(condition=lambda n: n.nodeid == nodeid):
            return node
        else:
            return None

    def replace_self(self, replacement: Union["Node", Iterable["Node"]]) -> None:
        """Replace this node in its parent's children.

        This is mostly useful during the transform step.

        Parameters
        ----------
        replacement
            The Node or Nodes to replace this with.

        Raises
        ------
        RSMNodeError
            If this Node's parent is None.

        See Also
        --------
        :meth:`remove_self`

        Examples
        --------
        Wrap a Text in a strong Span to render it in bold face.

        >>> p, t = nodes.Paragraph(), nodes.Text("one")
        >>> p.append(t)         # doctest: +IGNORE_RESULT
        >>> print(p.sexp())
        (Paragraph
          (Text))
        >>> s = nodes.Span(strong=True)
        >>> t.replace_self(s)
        >>> s.append(t)         # doctest: +IGNORE_RESULT
        >>> print(p.sexp())
        (Paragraph
          (Span
            (Text)))

        Note the call to :meth:`replace_self` must happen *before* the Text is added to
        the Span.

        May also replace with a list of Nodes.

        >>> t.replace_self([nodes.Text("new one"), nodes.Text("two")])
        >>> print(p.sexp())
        (Paragraph
          (Span
            (Text)
            (Text)))

        The following recipe uses the above example to wrap every Text within ``root``
        in a strong Span.  Note this is done to each Text descendent of ``root``,
        regardless of depth, and without any reference to their original immediate
        parents.

        >>> root = nodes.Manuscript().append(...)    # doctest: +SKIP
        >>> for t in root.traverse(nodeclass=Text):  # doctest: +SKIP
        ...     s = nodes.Span(strong=True)
        ...     t.replace_self(s)
        ...     s.append(t)

        """
        if not self.parent:
            raise RSMNodeError("Can only call replace_self on a node with parent")
        ids = [id(c) for c in self.parent.children]
        index = ids.index(id(self))
        parent = self.parent
        self.parent.remove(self)
        if not isinstance(replacement, Node):
            for idx, rep in enumerate(replacement):
                parent._children.insert(index + idx, rep)
                rep.parent = parent
        else:
            parent._children.insert(index, replacement)
            replacement.parent = parent

    def remove_self(self) -> None:
        """Remove this Node from its parent's children.

        See Also
        --------
        :meth:`replace_self`

        Examples
        --------
        >>> t = nodes.Text("remove me")
        >>> p = nodes.Paragraph().append(t)
        >>> p.children
        (Text("remove me"),)
        >>> t.remove_self()
        >>> p.children
        ()

        """
        if self.parent is not None:
            self.parent.remove(self)
            self.parent = None

    def ingest_dict_as_meta(self, meta: dict) -> None:
        if "reftext" in meta:
            meta["reftext_template"] = meta["reftext"]
            del meta["reftext"]
        for key, value in meta.items():
            setattr(self, str(key), value)


class NodeWithChildren(Node):
    """A :class:`Node` that may have children Nodes."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._children: list[Node] = []

    def _attrs_for_repr_and_eq(self) -> list[str]:
        return super()._attrs_for_repr_and_eq() + ["children"]

    def __repr__(self) -> str:
        if not self._children:
            return super().__repr__()
        children_repr = ", ".join(f"{c.__class__.__name__}" for c in self._children)
        children_repr = "[" + children_repr + "]"
        ret = super().__repr__()
        return ret[:-1] + ", " + children_repr + ")"

    @property
    def children(self) -> tuple[Node, ...]:
        """Tuple with this Node's children."""
        return tuple(self._children)

    def clear(self) -> None:
        """Remove all children."""
        for c in self._children:
            c.parent = None
        self._children = []

    def append(self, child: Union[Node, Iterable[Node]]) -> "NodeWithChildren":
        """Add a child or children after all current children.

        Parameters
        ----------
        child
            Node or iterable or nodes to append.

        Returns
        -------
        self

        Raises
        ------
        RSMNodeError
            When attempting to add as a child a node that already has a parent.

        See Also
        --------
        :meth:`prepend`

        Examples
        --------

        Append one or many children.

        >>> p, t1, t2, t3 = nodes.Paragraph(), nodes.Text("one"), nodes.Text("two"), nodes.Text("three")
        >>> p.append(t1)        # doctest: +IGNORE_RESULT
        >>> p.append([t2, t3])  # doctest: +IGNORE_RESULT
        >>> p.children
        (Text("one"), Text("two"), Text("three"))

        Calls can be chained.

        >>> p, t1, t2, t3 = nodes.Paragraph(), nodes.Text("one"), nodes.Text("two"), nodes.Text("three")
        >>> p.append(t1).append([t2, t3])  # doctest: +IGNORE_RESULT
        >>> p.children
        (Text("one"), Text("two"), Text("three"))

        Will raise when trying to append a node that already has a parent.

        >>> p2 = nodes.Paragraph()
        >>> p2.append(t1)
        Traceback (most recent call last):
        rsm.nodes.RSMNodeError: Attempting to append child to a new parent

        This is the case even when appending to the same parent.

        >>> t4 = nodes.Text("four")
        >>> p2.append(t4)       # doctest: +IGNORE_RESULT
        >>> p2.append(t4)
        Traceback (most recent call last):
        rsm.nodes.RSMNodeError: Attempting to append child to a new parent

        """
        if isinstance(child, Iterable):
            for c in child:
                self.append(c)
        elif isinstance(child, Node):
            if child.parent:
                raise RSMNodeError("Attempting to append child to a new parent")
            self._children.append(child)
            child.parent = self
        else:
            raise TypeError("Can only append a Node or iterable of Nodes as children")
        return self

    def prepend(self, child: Union[Node, Iterable[Node]]) -> "NodeWithChildren":
        """Add a child or children before all current children.

        For details, see :meth:`append`.

        See Also
        --------
        :meth:`append`

        """
        if isinstance(child, list):
            for c in reversed(child):
                self.prepend(c)
        elif isinstance(child, Node):
            if child.parent and child.parent is not self:
                raise RSMNodeError("Attempting to prepend child to a different parent")
            self._children.insert(0, child)
            child.parent = self
        else:
            raise TypeError("Can only prepend a Node or iterable of Nodes as children")
        return self

    def remove(self, child: "Node") -> None:
        """Remove child."""
        ids = [id(c) for c in self._children]
        index = ids.index(id(child))
        del self._children[index]
        child.parent = None


class Text(Node):
    """Plain text node.  Cannot contain children."""

    def __init__(self, text: str = "", asis: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.asis = asis

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{textwrap.shorten(self.text, 60)}")'


class Error(Text):
    """Error node.

    Notes
    -----
    When the parser encounters an error, this node is created at the location where the
    error is found.  Note this inherits from :class:`Text`; the text contents of this
    Node should indicate where in the source file the error occurred.

    """


class Span(NodeWithChildren):
    newmetakeys: ClassVar[set] = {"strong", "emphas", "little", "insert", "delete"}
    attr_to_tag: ClassVar[dict] = {
        "strong": "strong",
        "emphas": "em",
        "little": "small",
        "insert": "ins",
        "delete": "del",
    }

    def __init__(
        self,
        strong: bool = False,
        emphas: bool = False,
        little: bool = False,
        insert: bool = False,
        delete: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.strong = strong
        self.emphas = emphas
        self.little = little
        self.insert = insert
        self.delete = delete


class Heading(NodeWithChildren):
    newmetakeys: ClassVar[set] = {"title"}

    def __init__(self, title: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.title = title


class Manuscript(Heading):
    newmetakeys: ClassVar[set] = {"date"}
    nonum = True

    def __init__(
        self, src: str = "", date: Optional[datetime] = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.src = src
        self.date = date

    @property
    def full_number(self) -> str:
        return ""


class Author(Node):
    """An author of the manuscript.

    Notes
    -----
    A Manuscript may have more than one Author node.

    Examples
    --------
    .. rsm::

       :rsm:

          :author:
            :name: Melvin J. Noir
            :affiliation: ACME University
            :email: mel@acme.edu
          ::

       ::

    """

    newmetakeys: ClassVar[set] = {"name", "affiliation", "email"}

    def __init__(
        self, name: str = "", affiliation: str = "", email: str = "", **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.name: str = name
        """Full name of the author."""
        self.affiliation: str = affiliation
        """Institutional affiliation."""
        self.email: str = email
        """Contact information."""


class Abstract(NodeWithChildren):
    """Manuscript abstract.

    Notes
    -----
    By convention, abstracts contain only paragraphs and not other blocks.  This
    convention is not enforced, but it may be assumed to be the case during the
    translation step.

    Examples
    --------
    .. rsm::

       :rsm:

       :abstract:
         :keywords: {cosmology, general relativity, black holes}

         Black holes emit radiation.

       ::

       ::

    """

    newmetakeys: ClassVar[set] = {"keywords", "msc"}

    def __init__(
        self,
        keywords: Optional[list[str]] = None,
        msc: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.keywords = keywords or []
        """Manuscript keywords."""
        self.msc = msc or []
        """Mathematics Subject Classification (MSC) codes."""


class Section(Heading):
    autonumber = True
    level: ClassVar[int] = 2


class Subsection(Section):
    _number_within = Section
    level: ClassVar[int] = 3
    classreftext: ClassVar[str] = "Section {number}"


class Subsubsection(Section):
    _number_within = Subsection
    level: ClassVar[int] = 4
    classreftext: ClassVar[str] = "Section {number}"


class BaseParagraph(Heading):
    """Foo."""


class Paragraph(BaseParagraph):
    pass


class Note(BaseParagraph):
    pass


class Enumerate(NodeWithChildren):
    pass


class Itemize(NodeWithChildren):
    pass


class Keyword(Span):
    pass


class Construct(NodeWithChildren):
    kind_to_keyword: dict[str, str] = {
        "let": "LET",
        "define": "DEFINE",
        "write": "WRITE",
        "case": "CASE",
        "then": "THEN",
        "new": "NEW",
        "assume": "ASSUME",
        "prove": "PROVE",
        "pick": "PICK",
        "suffices": "SUFFICES",
        "claim": "⊢",
        "claimblock": "⊢",
        "qed": "QED",
        "st": "SUCH THAT",
    }

    def __init__(self, kind: str = "", **kwargs: Any):
        super().__init__(**kwargs)
        self.kind = kind

    @property
    def keyword(self):
        return self.kind_to_keyword[self.kind]


class ClaimBlock(Construct):
    def __init__(self, **kwargs: Any):
        super().__init__(kind="claimblock", **kwargs)


class Math(NodeWithChildren):
    pass


class MathBlock(NodeWithChildren):
    autonumber = True
    _number_within = Section
    classreftext: ClassVar[str] = "({number})"
    newmetakeys: ClassVar[set] = {"isclaim"}

    def __init__(self, isclaim: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.isclaim = isclaim

    @property
    def long_reftext(self) -> str:
        return f"Equation {self.reftext}".strip()


class SourceCode(Text):
    def __init__(self, text: str = "", lang: str = "", **kwargs: Any) -> None:
        kwargs.pop("asis", None)
        super().__init__(text, asis=True, **kwargs)
        self.lang = lang

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{textwrap.shorten(self.text, 60)}", lang="{self.lang}")'


class Code(NodeWithChildren):
    newmetakeys: ClassVar[set] = {"lang"}

    def __init__(self, source: str = "", lang: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.lang = lang
        self.source = SourceCode(source, lang)


class CodeBlock(NodeWithChildren):
    classreftext: ClassVar[str] = "Code Block {number}"
    newmetakeys: ClassVar[set] = {"lang"}

    def __init__(self, source: str = "", lang: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.lang = lang
        self.source = SourceCode(source, lang)


class Algorithm(NodeWithChildren):
    r"""Algorithm pseudocode.

    Notes
    -----
    The contents of an Algorithm node are not RSM markup.  They must be written in
    LaTeX-style notation using the `algorithmic` [1]_ environment.


    RSM uses `pseudocode.js` [2]_ to render algorithms in the frontend.

    References
    ----------
    .. [1] https://www.overleaf.com/learn/latex/Algorithms#The_algpseudocode_and_algorithm_packages
    .. [2] https://saswat.padhi.me/pseudocode.js/

    Examples
    --------
    .. rsm::

       :rsm:

       :algorithm:
         \begin{algorithm}
         \caption{Quicksort}
         \begin{algorithmic}
         \PROCEDURE{Quicksort}{$A, p, r$}
             \IF{$p < r$}
                 \STATE $q = $ \CALL{Partition}{$A, p, r$}
                 \STATE \CALL{Quicksort}{$A, p, q - 1$}
                 \STATE \CALL{Quicksort}{$A, q + 1, r$}
             \ENDIF
         \ENDPROCEDURE
         \PROCEDURE{Partition}{$A, p, r$}
             \STATE $x = A[r]$
             \STATE $i = p - 1$
             \FOR{$j = p$ \TO $r - 1$}
                 \IF{$A[j] < x$}
                     \STATE $i = i + 1$
                     \STATE exchange
                     $A[i]$ with $A[j]$
                 \ENDIF
                 \STATE exchange $A[i]$ with $A[r]$
             \ENDFOR
         \ENDPROCEDURE
         \end{algorithmic}
         \end{algorithm}
       ::

       ::
    """

    autonumber = True


class Appendix(Node):
    """Mark the start of the Appendix sections.

    The Appendix node currently has no visible output in the manuscript.  Instead, it
    affects how subsequent sections are numbered.

    Notes
    -----
    The Appendix must not contain children.  In fact, its parent subclass is
    :class:`Node`, not :class:`NodeWithChildren`.  Sections "in" the Appendix should
    simply appear after an Appendix node.

    Examples
    --------
    In RSM markup, the Appendix is a stamp, i.e. it does not need a closing Halmos.

    .. code-block:: text

       :rsm:

       # Before Appendix
       ::

       # Before Appendix

       ## Subsec
       ::

       ::

       :appendix:

       # After Appendix
       ::

       ::


    The above source is parsed into a Manuscript tree equivalent to the following.

    >>> msc = nodes.Manuscript().append(
    ...     [
    ...         nodes.Section(title="Before Appendix"),
    ...         nodes.Section(title="Before Appendix").append(nodes.Subsection(title="Subsec")),
    ...         nodes.Appendix(),
    ...         nodes.Section(title="After Appendix"),
    ...     ]
    ... )
    >>> print(msc.sexp())
    (Manuscript
      (Section)
      (Section
        (Subsection))
      (Appendix)
      (Section))

    Run the transform step on this Manuscript so the Sections will be autonumbered.

    >>> tform = rsm.transformer.Transformer()
    >>> tform.transform(msc)
    Manuscript(parent=None, [Section, Section, Appendix, Section])

    By default, Sections appearing after the Appendix receive letter numerals.

    >>> for sec in msc.traverse(nodeclass=nodes.Section):
    ...     print(f'{sec.full_number}. {sec.title}')
    1. Before Appendix
    2. Before Appendix
    2.1. Subsec
    A. After Appendix

    """


class BaseReference(Node):
    def __init__(
        self,
        target: Union[str, Node, None] = None,
        overwrite_reftext: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.overwrite_reftext = overwrite_reftext
        self.target = target

    def _attrs_for_repr_and_eq(self) -> list[str]:
        return super()._attrs_for_repr_and_eq() + ["target", "overwrite_reftext"]


class PendingReference(BaseReference):
    def __init__(self, target: str = "", **kwargs: Any) -> None:
        super().__init__(target, **kwargs)

    @property
    def external_file(self) -> Optional[str]:
        """Extract external file path from target, or None if internal reference."""
        if '#' in str(self.target):
            return str(self.target).split('#', 1)[0]
        return None

    @property
    def target_label(self) -> str:
        """Extract label from target."""
        if '#' in str(self.target):
            return str(self.target).split('#', 1)[1]
        return str(self.target)


class Reference(BaseReference):
    def __init__(
        self,
        target: Optional[Node] = None,
        external_file: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(target, **kwargs)
        self.external_file = external_file


class PendingPrev(BaseReference):
    def __init__(self, target: str = "", **kwargs: Any) -> None:
        super().__init__(target, **kwargs)


class URL(BaseReference):
    def __init__(self, target: str = "", **kwargs: Any) -> None:
        super().__init__(target, **kwargs)


class PendingCite(Node):
    def __init__(self, targetlabels: Optional[list[str]] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.targetlabels = targetlabels or []


class Cite(Node):
    def __init__(self, targets: Optional[list[Node]] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.targets = targets or []


class Statement(NodeWithChildren):
    pass


class Proof(NodeWithChildren):
    has_handrail = True


class Subproof(NodeWithChildren):  # importantly, NOT a subclass of Proof!
    pass


class Sketch(NodeWithChildren):
    has_handrail = True


class Step(Paragraph):
    autonumber = True
    classreftext: ClassVar[str] = "Step ⟨{number}⟩"
    possible_parents: ClassVar[set[Type["NodeWithChildren"]]] = {Proof, Subproof}
    has_handrail = True


Step.possible_parents.add(Step)
Step._number_within = (Proof, Step)


class Theorem(Heading):
    autonumber = True
    title = ""
    _number_within = Section
    newmetakeys: ClassVar[set] = {"title", "goals", "stars", "clocks"}
    has_handrail = True

    def __init__(
        self,
        title: str = "",
        goals: Optional[list[BaseReference]] = None,
        stars: int = 0,
        clocks: int = 0,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.title = title
        self.goals = goals or []
        self.stars = stars
        self.clocks = clocks


class Lemma(Theorem):
    _number_as = Theorem


class Corollary(Theorem):
    _number_as = Theorem


class Example(Theorem):
    _number_as = Theorem


class Exercise(Theorem):
    _number_as = Theorem


class Proposition(Theorem):
    _number_as = Theorem


class Problem(Theorem):
    _number_as = Theorem


class Porism(Theorem):
    _number_as = Theorem


class Remark(Theorem):
    _number_as = Theorem


class Definition(Theorem):
    _number_as = Theorem


class Bibliography(NodeWithChildren):
    pass


class Bibitem(Node):
    autonumber = True
    classreftext: ClassVar[str] = "{number}"
    newmetakeys: ClassVar[set] = {
        "kind",
        "author",
        "title",
        "year",
        "journal",
        "volume",
        "number",
        "publisher",
        "doi",
    }

    def __init__(
        self,
        kind: str = "",
        author: str = "",
        title: str = "",
        year: int = -1,
        journal: str = "",
        volume: int = -1,
        number: int = -1,
        publisher: str = "",
        doi: str = "",
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.kind = kind
        self.author = author
        self.title = title
        self.year = year
        self.journal = journal
        self.volume = volume
        self.number = number
        self.publisher = publisher
        self.doi = doi
        self.backlinks = []


class UnknownBibitem(Bibitem):
    def __init__(self, number: Union[str, int] = "?", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.number = number


class Asset(NodeWithChildren):
    autonumber = True
    _number_within = Section
    newmetakeys: ClassVar[set] = {"path", "scale"}

    def __init__(
        self, path: Union[Path, str] = "", scale: float = 1.0, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.path = Path(path)
        self.scale = scale


class Figure(Asset):
    classreftext = "Figure {number}"


class Video(Asset):
    classreftext = "Video {number}"


class Html(Asset):
    classreftext = "Html {number}"


class Draft(NodeWithChildren):
    pass


class Table(NodeWithChildren):
    autonumber = True


class TableHead(NodeWithChildren):
    pass


class TableBody(NodeWithChildren):
    pass


class TableRow(NodeWithChildren):
    pass


class TableDatum(NodeWithChildren):
    pass


class Caption(Paragraph):
    possible_parents: ClassVar[set[Type["NodeWithChildren"]]] = {Figure, Video, Html, Table}


class Contents(Itemize):
    pass


class Item(BaseParagraph):
    possible_parents: ClassVar[set[Type["NodeWithChildren"]]] = {
        Itemize,
        Enumerate,
        Contents,
    }


def all_node_subtypes():
    return [
        obj
        for name, obj in globals().items()
        if type(obj) is type and issubclass(obj, Node)
    ]
