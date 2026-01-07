"""Input: RSM source string -- Output: abstract syntax tree.

Produce a manuscript tree (a.k.a. abstract manuscript tree, a.k.a. abstract syntax tree)
from the RSM source string.

The process occurs in two stages:

1. Parsing: The first step parses the RSM source string into a *concrete syntax tree*
   using the tree-sitter parser written in C.  The grammar and parser definitions can be
   found in the `tree-sitter-rsm <https://github.com/leotrs/tree-sitter-rsm>`_
   repository.  This step uses `py-tree-sitter
   <https://github.com/tree-sitter/py-tree-sitter>`_, the python bindings of tree
   sitter.  Thus, the concrete syntax tree is composed of nodes defined by
   py-tree-sitter and the RSM package has little control over what these nodes look
   like.  The concrete syntax tree contains a node for each *syntactically-relevant*
   token in the source file, including but not limited to tags (``:tag-name:``),
   delimiters (``{``, ``}``), Halmoses (``::``), and other special characters (``/``,
   ``*``, ``$``, etc).

2. Abstractifying: The second step takes the concrete syntax tree output by the
   tree-sitter parser and builds an *abstract syntax tree*.  This latter tree contains a
   node for each *semantically-relevant* piece of the manuscript, and no longer contains
   nodes for delimiters or special characters.  This step is carried out by this module
   in pure python.

Both steps are handled by :class:`TSParser`.  The rest of this module contains auxiliary
functions (mostly private ones) that are useful during the parsing process.

"""

import logging
import re
from collections.abc import Callable
from itertools import groupby
from typing import Any

import tree_sitter
import tree_sitter_rsm
from tree_sitter import Node as TSNode
from tree_sitter import Tree as TSTree

from rsm import nodes

from .util import EscapedString

logger = logging.getLogger("RSM").getChild("parse")


class RSMParserError(Exception):
    """Raised when there is an irrecoverable error during parser.

    Note that the parser will try to generate an abstract manuscript tree even if there
    are error nodes in the concrete syntax tree.  This is possible due to the excellent
    error tolerance of tree-sitter parsers.

    """

    def __init__(self, pos: int | None = None, msg: str | None = None) -> None:
        self.pos = pos
        self.msg = f"Parser error at position {self.pos}" if msg is None else msg
        super().__init__(self.msg)


DELIMS = ":%$`*{#"
PUSH_THESE_TYPES = {
    "ERROR",
    "appendix",
    "bibitem",
    "bibtex",
    "block",
    "caption",
    "construct",
    "inline",
    "keyword",
    "mathblock",
    "paragraph",
    "section",
    "subsection",
    "subsubsection",
    "specialblock",
    "specialconstruct",
    "specialinline",
    "table",
    "tbody",
    "td",
    "tdcontent",
    "text",
    "thead",
    "tr",
    "trshort",
}


class TSParser:
    """Parse RSM source into an abstract syntax tree.

    Examples
    --------
    >>> src = \"\"\"
    ... :rsm:
    ... Hello, RSM!
    ... ::
    ... \"\"\"

    The abstractify step is run by default.

    >>> parser = rsm.tsparser.TSParser()
    >>> ast = parser.parse(src)
    >>> print(ast.sexp())
    (Manuscript
      (Paragraph
        (Text)))

    The concrete syntax tree is also available.

    >>> cst = parser.parse(src, abstractify=False)
    >>> rsm.tsparser.print_cst(cst)
    (source_file Point(row=1, column=0) - Point(row=4, column=0)
      (:rsm: Point(row=1, column=0) - Point(row=1, column=5))
      (paragraph Point(row=2, column=0) - Point(row=3, column=0)
        (text Point(row=2, column=0) - Point(row=2, column=11) "Hello, RSM!")
        (paragraph_end Point(row=3, column=0) - Point(row=3, column=0)))
      (:: Point(row=3, column=0) - Point(row=3, column=2)))
    """

    def __init__(self) -> None:
        # Execute these two lines only if we need to compile the parser on the fly.
        #
        # tree_sitter.Language.build_library("languages.so", ["tree-sitter-rsm"])
        # self._lang = tree_sitter.Language("languages.so", "rsm")
        #

        # The Language class receives an absolute path.  If given a single file name
        # instead of a path, it will look for the file in the current directory and, if
        # not found there, in the path given by the environment variable
        # $LD_LIBRARY_PATH.  In this latter case, $LD_LIBRARY_PATH must be set BEFORE
        # the current python interpreter session starts, i.e. it must be set at the
        # command line.  At least on linux, trying to set $LD_LIBRARY_PATH
        # programatically *will not work*.
        #
        # The code below always gives an absolute path so the problem pointed out above
        # should never happen in any platform.  However, it does assume that the build
        # system has compiled the rsm.so (or rsm.dll) file and placed it in the
        # directory where this module lies.
        #
        self._lang = tree_sitter.Language(tree_sitter_rsm.language())
        self._parser = tree_sitter.Parser(self._lang)
        self.cst: TSTree | None = None
        """The concrete syntax tree generated from the source."""
        self.ast: nodes.Manuscript | None = None
        """The abstract manuscript tree generated from the concrete syntax tree."""

    def parse(self, src: str, abstractify: bool = True) -> TSTree | nodes.Manuscript:
        """Parse RSM source into a syntax tree.

        For examples see class docstring.

        Parameters
        ----------
        src
            String containing RSM source.
        abstractify
            Whether to run the abstractify step.

        Returns
        -------
        tree
            Either an abstract syntax tree (if *abstractify* is ``True``) or a concrete
            syntax tree (if *abstractify* is ``False``).

        Notes
        -----
        Populates the attributes :attr:`cst` and :attr:`ast` with the concrete and
        abstract syntax trees, respectively.

        """
        logger.info("Parsing...")
        encoding = "utf-8"
        self.cst = self._parser.parse(bytes(str(src), encoding))

        if logger.getEffectiveLevel() <= logging.DEBUG:
            logger.debug("concrete syntax tree:")
            if self.cst is not None:
                print_cst(self.cst)

        if not abstractify:
            if self.cst is None:
                raise RSMParserError("Failed to parse CST")
            return self.cst  # type: ignore[return-value]

        logger.info("Abstractifying...")
        try:
            if self.cst is None:
                raise RSMParserError("No CST to abstractify")
            self.ast = _abstractify(self.cst)
        except AttributeError as ex:
            raise RSMParserError(msg="Error abstractifying.") from ex

        if self.ast is None:
            raise RSMParserError(msg="The CST contains errors.")

        if logger.getEffectiveLevel() <= logging.DEBUG:
            logger.debug("abstract syntax tree:")
            print(self.ast.sexp())

        if self.cst.root_node.text is not None:
            self.ast.src = self.cst.root_node.text.decode(encoding)
        return self.ast


def print_cst(tree: TSTree, named_only: bool = False) -> None:
    """Print a tree-sitter concrete syntax tree.

    This is executed by default when processing a manuscript with logging level DEBUG.
    For examples, see :class:`TSParser` docstring.

    Parameters
    ----------
    tree
        A concrete syntax tree parsed by tree-sitter.
    named_only
        Whether to print only named nodes.

    Notes
    -----
    Named nodes are those that do not correspond to syntax-only nodes.

    """
    # this function prints to stdout rather than use logger for nicer output

    children_att = "named_children" if named_only else "children"
    stack = [(0, tree.root_node)]
    while stack:
        indent, node = stack.pop()
        if node is None:
            print(")", end="")
            continue
        if indent:
            print()
        print(
            f"{' ' * indent}({node.type} {node.start_point} - {node.end_point}",
            end="",
        )
        if node.type == "text" and node.text is not None:
            print(f' "{node.text.decode("utf-8")}"', end="")
        stack.append((None, None))
        stack += reversed([(indent + 2, n) for n in getattr(node, children_att)])
    print()


CST_TYPE_TO_AST_TYPE: dict[str, Callable] = {
    "abstract": nodes.Abstract,
    "appendix": nodes.Appendix,
    "algorithm": nodes.Algorithm,
    "author": nodes.Author,
    "enumerate": nodes.Enumerate,
    "cite": nodes.PendingCite,
    "code": nodes.Code,
    "codeblock": nodes.CodeBlock,
    "corollary": nodes.Corollary,
    "definition": nodes.Definition,
    "draft": nodes.Draft,
    "example": nodes.Example,
    "item": nodes.Item,
    "itemize": nodes.Itemize,
    "caption": nodes.Caption,
    "figure": nodes.Figure,
    "video": nodes.Video,
    "html": nodes.Html,
    "construct": nodes.Construct,
    "specialconstruct": nodes.Construct,
    "lemma": nodes.Lemma,
    "math": nodes.Math,
    "mathblock": nodes.MathBlock,
    "note": nodes.Note,
    "paragraph": nodes.Paragraph,
    "prev": nodes.PendingPrev,
    "prev2": nodes.PendingPrev,
    "prev3": nodes.PendingPrev,
    "previous": nodes.PendingPrev,
    "proof": nodes.Proof,
    "proposition": nodes.Proposition,
    "ref": nodes.PendingReference,
    "remark": nodes.Remark,
    "section": nodes.Section,
    "sketch": nodes.Sketch,
    "source_file": nodes.Manuscript,
    "spanemphas": lambda **kwargs: nodes.Span(emphas=True, **kwargs),
    "spanstrong": lambda **kwargs: nodes.Span(strong=True, **kwargs),
    "step": nodes.Step,
    "subproof": nodes.Subproof,
    "subsection": nodes.Subsection,
    "subsubsection": nodes.Subsubsection,
    "span": nodes.Span,
    "table": nodes.Table,
    "tbody": nodes.TableBody,
    "text": nodes.Text,
    "thead": nodes.TableHead,
    "theorem": nodes.Theorem,
    "td": nodes.TableDatum,
    "tdcontent": nodes.TableDatum,
    "toc": nodes.Contents,
    "tr": nodes.TableRow,
    "trshort": nodes.TableRow,
    "url": nodes.URL,
}


def _parse_metakey_list(cst_key: TSNode, cst_val: TSNode) -> tuple[str, list[str]]:
    key = cst_key.named_children[0].type
    if cst_val.named_children:
        val = [
            c.text.decode("utf-8").strip()
            for c in cst_val.named_children
            if c.text is not None
        ]
    else:
        val = [
            c.text.decode("utf-8").strip()
            for c in cst_val.named_children
            if c.text is not None
        ]
    return key, val


def _parse_metakey_text(cst_key: TSNode, cst_val: TSNode) -> tuple[str, str]:
    key = cst_key.named_children[0].type
    val = cst_val.text.decode("utf-8").strip() if cst_val.text is not None else ""
    return key, val


def _parse_metakey_any(cst_key: TSNode, cst_val: TSNode) -> tuple[str, str]:
    return _parse_metakey_text(cst_key, cst_val)


def _parse_metakey_bool(cst_key: TSNode, _: TSNode) -> tuple[str, bool]:
    key = cst_key.named_children[0].type
    return key, True


def _parse_meta_into_dict(node: TSNode) -> dict[str, Any]:
    pairs = {}
    for pair in [c for c in node.named_children if c.type.endswith("pair")]:
        if len(pair.named_children) == 1:  # bool meta key
            cst_key, cst_val = pair.named_children[0], None
        else:
            cst_key, cst_val = pair.named_children
        key, val = globals()[f"_parse_{cst_key.type}"](cst_key, cst_val)
        pairs[key] = val
    return pairs


def _normalize_text(root: TSNode) -> str:
    if root is None:
        return ""
    for node in root.traverse():
        # Merge consecutive text nodes (each text node ends at a newline, so consecutive
        # text nodes are just adjacent lines of text and can always be merged).  Also,
        # pad all text with spaces.  Spurious spaces added here are removed later.
        for run_is_text, run_generator in groupby(
            node.children, key=lambda c: isinstance(c, nodes.Text)
        ):
            if not run_is_text:
                continue
            run = list(run_generator)

            if len(run) == 2:
                first, last = run
                first.text = first.text.rstrip() + " " + last.text.lstrip()
                last.remove_self()

            elif len(run) > 2:
                # Watch the use of rstrip, strip, and lstrip here.
                first, rest = run[0], run[1:]
                first.text = (
                    first.text.rstrip()
                    + " "
                    + " ".join([t.text.strip() for t in run[1:-1]])
                    + " "
                    + run[-1].text.lstrip()
                )
                for t in rest:
                    t.remove_self()

        if not isinstance(node, nodes.Paragraph) and node.children:
            if isinstance((first := node.children[0]), nodes.Text):
                first.text = first.text.lstrip()
            if isinstance((last := node.children[-1]), nodes.Text):
                last.text = last.text.rstrip()

        # Strip both ends of a paragraph's text content.
        if isinstance(node, nodes.Paragraph):
            if (first := node.first_of_type(nodes.Text)) and not first.prev_sibling():
                first.text = first.text.lstrip()
            if (last := node.last_of_type(nodes.Text)) and not last.next_sibling():
                last.text = last.text.rstrip()

        # Return the space we borrowed from Construct nodes.
        if isinstance(node, nodes.Construct):
            if (first := node.first_of_type(nodes.Text)) and not first.prev_sibling():
                first.text = f" {first.text}"
            if (first := node.first_of_type(nodes.Math)) and not first.prev_sibling():
                node.prepend(nodes.Text(" "))
            node.prepend(nodes.Keyword().append(nodes.Text(node.keyword)))

        # At this point, the whitespace within non-paragraphs (e.g. Span, Claim) has
        # been dealt with, as has the leading and trailing whitespace of Paragraphs.
        # Since the text nodes have been merged, now every Paragraph's children look
        # like [..., Span, Text, Claim, Text, Span, ...].  We need to deal with the
        # whitespace at the boundaries between the Text and non-Text nodes in this list.
        # Since the inner whitespace of non-Texts has been dealt with, all we need to
        # care about is the outer whitespace of Text children.  Suppose we have a Text
        # node followed by a Span.  We want to give the user two options: either no
        # whitespace between them, or exactly one space.
        for child in node.children:
            if not isinstance(child, nodes.Text):
                continue
            child.text = re.sub(r"(.*?)\s+$", r"\1 ", child.text)
            child.text = re.sub(r"^\s+(.*?)", r" \1", child.text)

        # Finally we handle the space between non-Text children of a paragraph, for
        # example two Spans together, or a Span followed by a Construct.  In all cases,
        # we simply insert a single space between them.
        classes = [nodes.Span, nodes.Construct, nodes.Math]
        sibling = node.next_sibling()
        if sibling and type(node) in classes and type(sibling) in classes:
            node.replace_self([node, nodes.Text(" ")])

        # Manage escaped characters.
        if isinstance(node, nodes.Text) and not node.asis:
            node.text = EscapedString(node.text, DELIMS).escape()
        if isinstance(node, nodes.Section):
            node.title = EscapedString(node.title, DELIMS).escape()
        if isinstance(node, nodes.Manuscript):
            node.title = EscapedString(node.title, DELIMS).escape()

    return ""  # This function modifies nodes in place


def _abstractify(cst: TSTree) -> nodes.Manuscript:
    ast_root_node = None
    bibliography_node = None
    stack = [(None, cst.root_node)]
    while stack:
        parent, cst_node = stack.pop()
        skip_these_ids = set()
        if cst_node.type == "comment":
            continue

        # Handle bibliography-related nodes first and continue
        if (
            cst_node.type == "specialblock"
            and cst_node.children
            and cst_node.children[0].type == "bibliography"
        ):
            bibliography_node = nodes.Bibliography()
            ast_root_node.append(bibliography_node)
            continue
        if cst_node.type == "bibtex":
            if bibliography_node is None:
                logger.warning(msg="Found bibtex but no bibliography node")
                continue

            stack += reversed(
                [
                    (bibliography_node, c)
                    for c in cst_node.named_children
                    if c.type == "bibitem"
                ]
            )

            for c in [c for c in cst_node.named_children if c.type == "ERROR"]:
                logger.warning(msg=f"Bibitem at {(c.start_point)} has an error")

            continue
        if cst_node.type == "bibitem":
            bib_node = nodes.Bibitem()
            bib_node.kind = cst_node.child_by_field_name("kind").text.decode("utf-8")
            bib_node.label = cst_node.child_by_field_name("label").text.decode("utf-8")
            for pair in [c for c in cst_node.named_children if c.type == "bibitempair"]:
                key, value = pair.named_children
                key, value = key.text.decode("utf-8"), value.text.decode("utf-8")
                setattr(bib_node, key, value)

            parent.append(bib_node)
            continue

        # After this if statement, cst_node is the node that actually contains the
        # interesting stuff, and ast_node_type is a string with the type of syntax node
        # that we are currently analyzing.  NOTE: It may be the case that cst_node is
        # redirected to point to one of its children; ast_node_type may or may not be
        # equal to cst_node.type, or neither, or both!  For this reason, from now on, DO
        # NOT use cst_node.tpye, always use ast_node_type instead.
        ast_node_type = ""
        if cst_node.type == "source_file" or cst_node.type.endswith("section"):
            meta = cst_node.child_by_field_name("meta")
            ast_node_type = cst_node.type

            ast_node = CST_TYPE_TO_AST_TYPE[ast_node_type](
                start_point=cst_node.start_point,
                end_point=cst_node.end_point,
            )

            if section_title := cst_node.child_by_field_name("title"):
                # Sections with a hastag shurtcut ("# Section Title") have the title as
                # a text child node with field name 'title', so we must extract that
                # here. Sections with a tag (":section:") have the title as a meta key,
                # so that is handled when meta is ingested.
                ast_node.title = section_title.text.decode("utf-8")
                skip_these_ids.add(section_title.id)

            if isinstance(ast_node, nodes.Manuscript):
                ast_root_node = ast_node
            if meta:
                ast_node.ingest_dict_as_meta(_parse_meta_into_dict(meta))

            if parent and isinstance(parent, nodes.NodeWithChildren):
                parent.append(ast_node)

            stack += reversed(
                [
                    (ast_node, c)
                    for c in cst_node.named_children
                    if c.type in PUSH_THESE_TYPES and c.id not in skip_these_ids
                ]
            )
            continue

        elif cst_node.type in ["specialblock", "specialinline"]:
            ast_node_type = cst_node.named_children[0].type

            # Tables are special because the entire contents are in the first children,
            # so we might as well add that with the current parent and ignore the
            # current node
            if ast_node_type == "table":
                stack.append((parent, cst_node.named_children[0]))
                continue

        elif cst_node.type == "mathblock":
            ast_node_type = "mathblock"

        elif cst_node.type == "td":
            # td tags are special because the entire contents are in the first children,
            # so we might as well add that with the current parent and ignore the
            # current node
            stack.append((parent, cst_node.named_children[0]))
            continue

        elif cst_node.type == "paragraph":
            first = cst_node.named_children[0]
            if first.type in ["item", "caption"]:
                cst_node = first
            ast_node_type = cst_node.type

        elif cst_node.type in ["block", "inline"]:
            tag = cst_node.child_by_field_name("tag")
            ast_node_type = tag.type
            skip_these_ids.add(tag.id)

        else:
            ast_node_type = cst_node.type

        # make the correct type of AST node
        if ast_node_type in CST_TYPE_TO_AST_TYPE:
            ast_node = CST_TYPE_TO_AST_TYPE[ast_node_type](
                start_point=cst_node.start_point,
                end_point=cst_node.end_point,
            )
            if isinstance(ast_node, nodes.Manuscript):
                ast_root_node = ast_node
            elif isinstance(ast_node, nodes.Text):
                ast_node.text = cst_node.text.decode("utf-8")
        elif ast_node_type == "ERROR":
            start_row, start_col = cst_node.start_point
            end_row, end_col = cst_node.end_point
            logger.warning(
                "The CST contains errors.",
                extra=dict(
                    start_row=start_row,
                    start_col=start_col,
                    end_row=end_row,
                    end_col=end_col,
                ),
            )
            ast_node = nodes.Error(
                f"[CST error at ({start_row}, {start_col}) - ({end_row}, {end_col})]",
                start_point=cst_node.start_point,
                end_point=cst_node.end_point,
            )
        else:
            raise RSMParserError(msg=f"not found {ast_node_type}")

        # process meta
        meta = cst_node.child_by_field_name("meta")
        if meta:
            ast_node.ingest_dict_as_meta(_parse_meta_into_dict(meta))

        # process some special tags
        if ast_node_type in ["math", "code", "mathblock", "codeblock", "algorithm"]:
            # "asis_text" is not pushed to the stack for further processing so must
            # handle it here
            asis = cst_node.named_children[-1]
            assert asis.type == "asis_text"
            text = asis.text.decode("utf-8")
            if ast_node_type in ["code", "codeblock"]:
                child = nodes.SourceCode(text, lang=ast_node.lang)
            else:
                child = nodes.Text(text, asis=True)
            ast_node.append(child)

        # mathblocks that are marked as claims must be enclosed within a ClaimBlock
        if ast_node_type == "mathblock" and ast_node.isclaim:
            claimblock = nodes.ClaimBlock(
                start_point=cst_node.start_point, end_point=cst_node.end_point
            )
            claimblock.append(ast_node)
            ast_node = claimblock

        # set construct type and kind
        if ast_node_type in ["construct", "specialconstruct"]:
            if tag := cst_node.child_by_field_name("tag"):
                ast_node.kind = tag.type

        if ast_node_type in ["ref", "previous", "url"]:
            target_node = cst_node.named_children[1]
            ast_node.target = target_node.text.decode("utf-8")
            skip_these_ids.add(target_node.id)

            if len(cst_node.named_children) > 2:
                reftext_node = cst_node.named_children[2]
                ast_node.overwrite_reftext = reftext_node.text.decode("utf-8")
                skip_these_ids.add(reftext_node.id)

        if ast_node_type.startswith("prev") and ast_node_type != "previous":
            if ast_node_type == "prev":
                target = 1
            else:
                target = int(ast_node_type[4:])
            ast_node.target = target

        if ast_node_type == "cite":
            target_node = cst_node.named_children[1]
            labels = target_node.text.decode("utf-8").split(",")
            ast_node.targetlabels = [l.strip() for l in labels]
            skip_these_ids.add(target_node.id)

        # If a text node ends in a newline (i.e. if the next sibling is in a new row),
        # then we assume the user means to leave a space in between them...
        if ast_node_type == "text" and (sibling := cst_node.next_sibling):
            my_row, sib_row = cst_node.end_point[0], sibling.start_point[0]
            if sib_row > my_row:
                ast_node.text = ast_node.text + " "
        # ...and same thing for text that starts one line after the previous sibling.
        if ast_node_type == "text" and (sibling := cst_node.prev_sibling):
            my_row, sib_row = cst_node.start_point[0], sibling.end_point[0]
            if my_row > sib_row:
                ast_node.text = " " + ast_node.text

        # add the AST node to the correct place
        if parent and isinstance(parent, nodes.NodeWithChildren):
            parent.append(ast_node)

        # push the children that need to be processed
        stack += reversed(
            [
                (ast_node, c)
                for c in cst_node.named_children
                if c.type in PUSH_THESE_TYPES and c.id not in skip_these_ids
            ]
        )

    _normalize_text(ast_root_node)
    return ast_root_node
