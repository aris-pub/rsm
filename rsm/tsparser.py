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
from datetime import datetime
from itertools import groupby
from typing import Any, NamedTuple, cast

import tree_sitter
import tree_sitter_rsm
from tree_sitter import Node as TSNode
from tree_sitter import Tree as TSTree

from rsm import nodes

from .util import EscapedString

logger = logging.getLogger("RSM").getChild("parse")

_BIB_KINDS = {
    "article",
    "book",
    "conference",
    "incollection",
    "inproceedings",
    "mastersthesis",
    "misc",
    "phdthesis",
    "software",
    "techreport",
    "unpublished",
    "webpage",
}

_BIB_FIELDS = {
    "address",
    "author",
    "booktitle",
    "doi",
    "edition",
    "editor",
    "howpublished",
    "institution",
    "journal",
    "month",
    "note",
    "number",
    "organization",
    "pages",
    "publisher",
    "school",
    "series",
    "title",
    "url",
    "verbatim",
    "volume",
    "year",
}


def _user_position(
    start_point: tuple[int, int], end_point: tuple[int, int]
) -> dict[str, int]:
    """Make the position fields of a log record from tree-sitter points.

    Tree-sitter counts rows and columns from 0. Editors and the linter count
    from 1, so every position printed for a user is shifted by 1 here.
    """
    (start_row, start_col), (end_row, end_col) = start_point, end_point
    return {
        "start_row": start_row + 1,
        "start_col": start_col + 1,
        "end_row": end_row + 1,
        "end_col": end_col + 1,
    }


def _bib_field_name(pair: TSNode) -> str:
    key_node = pair.named_children[0]
    assert key_node.type == "key" and key_node.text is not None
    return key_node.text.decode("utf-8").split("=")[0].strip().lower()


# The grammar keeps a % in the text of a value, so that the comment does not
# take the closing brace and the later fields with it. RSM cuts the value here.
_BIB_COMMENT = re.compile(r"(?<!\\)%")


def _ingest_bib_field(bib_node: nodes.Bibitem, pair: TSNode) -> None:
    """Set one field of a BibTeX entry on `bib_node`, or warn and skip it."""
    key = _bib_field_name(pair)
    where = _user_position(pair.start_point, pair.end_point)
    entry = f"entry {bib_node.label}: field {key}"
    if key not in _BIB_FIELDS:
        logger.warning(f"{entry} is not used, skipped", extra=where)
        return
    value_node = pair.named_children[-1]
    if value_node.type == "quotedvalue":
        logger.warning(
            f"{entry} is in quotes, skipped. Write the value in braces, as in "
            f"{key} = {{...}}",
            extra=where,
        )
        return
    if value_node.type == "barevalue":
        logger.warning(
            f"{entry} is not in braces, skipped. Write the value in braces, as in "
            f"{key} = {{...}}",
            extra=where,
        )
        return
    if value_node.type != "value" or pair.has_error:
        logger.warning(
            f"{entry} cannot be read, skipped. Write it as {key} = {{...}}",
            extra=where,
        )
        return
    assert value_node.text is not None
    value = value_node.text.decode("utf-8")
    if _BIB_COMMENT.search(value):
        logger.warning(
            f"{entry} is cut at a % (a % starts a comment), skipped. Write a "
            "percent sign in a value as \\%",
            extra=where,
        )
        return
    if "{" in value:
        logger.warning(
            f"{entry} has braces inside its value. RSM ignores these braces and "
            "keeps the text inside them. Write accented letters as they are, "
            "such as ö, not as LaTeX commands.",
            extra=where,
        )
        value = value.replace("{", "").replace("}", "")
    value = value.replace("\\%", "%")
    # BibTeX calls the issue number "number", but on a node `number` is the
    # citation index assigned by autonumbering, so store the issue under
    # `issue` to keep it from being overwritten.
    if key == "number":
        key = "issue"
    setattr(bib_node, key, value)


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


DELIMS = ":%$`*{}#"
PUSH_THESE_TYPES = {
    "ERROR",
    "appendix",
    "bibitem",
    "references",
    "block",
    "caption",
    "codeblock",
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
    >>> src = \"Hello, RSM!\"

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
    (source_file <Point row=0, column=0> - <Point row=0, column=11>
      (paragraph <Point row=0, column=0> - <Point row=0, column=11>
        (text <Point row=0, column=0> - <Point row=0, column=11> "Hello, RSM!")
        (paragraph_end <Point row=0, column=11> - <Point row=0, column=11>)))
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
            return self.cst

        logger.info("Abstractifying...")
        try:
            if self.cst is None:
                raise RSMParserError("No CST to abstractify")
            self.ast = _abstractify(self.cst)
            if self.ast is not None:
                _group_nested_lists(self.ast)
        # The asserts in _abstractify fail on a broken CST, as attribute
        # lookups on None do.
        except (AttributeError, AssertionError) as ex:
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
    stack: list[tuple[int, TSNode | None]] = [(0, tree.root_node)]
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
        stack.append((indent, None))
        stack += reversed([(indent + 2, n) for n in getattr(node, children_att)])
    print()


CST_TYPE_TO_AST_TYPE: dict[str, Callable] = {
    "abstract": nodes.Abstract,
    "appendix": nodes.Appendix,
    "algorithm": nodes.Algorithm,
    "aside": nodes.Aside,
    "notation": nodes.Notation,
    "author": nodes.Author,
    "enumerate": nodes.Enumerate,
    "cite": nodes.PendingCite,
    "code": nodes.Code,
    "codeblock": nodes.CodeBlock,
    "corollary": nodes.Corollary,
    "definition": nodes.Definition,
    "draft": nodes.Draft,
    "example": nodes.Example,
    "exercise": nodes.Exercise,
    "porism": nodes.Porism,
    "problem": nodes.Problem,
    "item": nodes.Item,
    "itemize": nodes.Itemize,
    "caption": nodes.Caption,
    "figure": nodes.Figure,
    "video": nodes.Video,
    "html": nodes.RawHtml,
    "htmlblock": nodes.HtmlBlock,
    "construct": nodes.Construct,
    "specialconstruct": nodes.Construct,
    "lemma": nodes.Lemma,
    "math": nodes.Math,
    "mathblock": nodes.MathBlock,
    "note": nodes.Note,
    "notecall": nodes.NoteCall,
    "paragraph": nodes.Paragraph,
    "prev": nodes.PendingPrev,
    "prev2": nodes.PendingPrev,
    "prev3": nodes.PendingPrev,
    "previous": nodes.PendingPrev,
    "proof": nodes.Proof,
    "calc": nodes.Calc,
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
    "tab": nodes.Tab,
    "tabs": nodes.Tabs,
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


def _metaval_str(cst_val: TSNode) -> str:
    """Return a meta value as one line of text.

    A value is one text piece per line, with comments between them, so the
    pieces are joined with single spaces. A comma after a pair is optional and
    the grammar leaves it in the value before it, so it is dropped here.
    """
    pieces = [
        (c.text or b"").decode("utf-8") for c in cst_val.children if c.type != "comment"
    ]
    val = " ".join(" ".join(pieces).split())
    if val.endswith(","):
        val = val[:-1].rstrip()
    return val


def _parse_metakey_list(cst_key: TSNode, val: str) -> tuple[str, list[str]]:
    key = cst_key.named_children[0].type
    return key, [item.strip() for item in val.split(",") if item.strip()]


def _parse_metakey_text(cst_key: TSNode, val: str) -> tuple[str, str]:
    return cst_key.named_children[0].type, val


_parse_metakey_title = _parse_metakey_text
_parse_metakey_path = _parse_metakey_text
_parse_metakey_number = _parse_metakey_text
_parse_metakey_word = _parse_metakey_text
_parse_metakey_date = _parse_metakey_text


def _parse_metakey_bool(cst_key: TSNode, _: str | None) -> tuple[str, bool]:
    key = cst_key.named_children[0].type
    return key, True


_WORD_VALUES = {
    "accent": ("blue", "red", "green", "orange", "yellow", "purple", "pink", "gray"),
    "numbering": ("document", "section", "none"),
    "typography": ("sans-serif", "serif"),
    "citation_style": ("numeric", "parens-author-year", "author-parens-year"),
    "view": ("list", "tree"),
    "orientation": nodes.Contents.orientations,
}

_AUTHOR_DISPLAY_KEYS = {"author_display_first", "author_display_last"}
_WHOLE_NUMBER_KEYS = {"toc_depth"} | _AUTHOR_DISPLAY_KEYS

# The smallest and largest value of a whole-number key that has limits.
_WHOLE_NUMBER_RANGES = {"toc_depth": (1, 3)}

# The grammar gives number, word and date values one shared token, so the form
# of a number or a date is checked here.
_NUMBER = re.compile(r"\d+(\.\d+)?")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")

_LANG_CODE = re.compile(r"^[a-z]{2,3}(-[A-Z]{2})?$")
_LANG_CODE_ALLOWED = "a language code such as en, es, fr, en-US or zh-CN"

# What each key accepts, for the message logged when its value has the wrong
# shape.
_SHAPE_ALLOWED = {
    "metakey_path": "a file path",
    "metakey_number": "a number, such as 2 or 0.5",
    "metakey_word": "a single word",
    "metakey_date": "a date written YYYY-MM-DD, such as 2025-01-15",
}


def _allowed_values(key: str, keykind: str) -> str:
    if key in _WORD_VALUES:
        return ", ".join(_WORD_VALUES[key])
    if key in _WHOLE_NUMBER_RANGES:
        low, high = _WHOLE_NUMBER_RANGES[key]
        return f"a whole number from {low} to {high}"
    if key in _WHOLE_NUMBER_KEYS:
        return "a whole number, such as 2"
    return _SHAPE_ALLOWED[keykind]


def _log_bad_value(key: str, value: str, allowed: str, node: TSNode) -> None:
    pos = _user_position(node.start_point, node.end_point)
    logger.error(
        f"Invalid value for :{key.replace('_', '-')}: on line {pos['start_row']}: "
        f"{value!r}. Allowed values: {allowed}. The value is ignored and the "
        "default is used.",
        extra=pos,
    )


def _value_is_valid(key: str, value: Any, keykind: str, pair: TSNode) -> bool:
    if key in _WORD_VALUES:
        ok = value in _WORD_VALUES[key]
    elif key in _WHOLE_NUMBER_KEYS:
        ok = value.isdigit()
        if ok and key in _WHOLE_NUMBER_RANGES:
            low, high = _WHOLE_NUMBER_RANGES[key]
            ok = low <= int(value) <= high
    elif keykind == "metakey_number":
        ok = _NUMBER.fullmatch(value) is not None
    elif keykind == "metakey_date":
        # strptime alone also accepts one-digit months and days.
        ok = _DATE.fullmatch(value) is not None
        if ok:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                ok = False
    else:
        return True
    if not ok:
        _log_bad_value(key, value, _allowed_values(key, keykind), pair)
    return ok


def _log_meta_error(err: TSNode) -> list[str]:
    """Log an ERROR node found where meta is, and return the keys it holds.

    When the ERROR holds a path, number, word or date key, the message names
    that key and its allowed values.
    """
    keys = [
        n for n in _descendants(err) if n.type in _SHAPE_ALLOWED and n.named_children
    ]
    if not keys:
        logger.error(
            "Parse error in meta; the text at this position was ignored.",
            extra=_user_position(err.start_point, err.end_point),
        )
        return []
    text = err.text or b""
    for i, cst_key in enumerate(keys):
        end = keys[i + 1].start_byte if i + 1 < len(keys) else err.end_byte
        raw = text[cst_key.end_byte - err.start_byte : end - err.start_byte]
        value = raw.decode("utf-8").strip().rstrip("}").strip()
        key = cst_key.named_children[0].type
        _log_bad_value(key, value, _allowed_values(key, cst_key.type), cst_key)
    return [k.named_children[0].type for k in keys]


def _descendants(node: TSNode) -> list[TSNode]:
    out = []
    for c in node.named_children:
        out.append(c)
        out.extend(_descendants(c))
    return out


def _log_meta_errors_outside_meta(cst_node: TSNode) -> set[int]:
    """Log the ERROR children of *cst_node* that hold a meta key and return their ids.

    When the only pair of a meta has a value of the wrong shape, the parser
    replaces the whole meta with an ERROR child of the block, and the block has
    no meta field. The caller skips these ERROR nodes, so the value is ignored
    instead of being shown as an error in the output.

    An unknown key written like a real key (lowercase letters, digits and
    hyphens) forms a meta and is logged in _parse_meta_into_dict. A key with
    another shape (such as :Colour: or :colour_x:) does not, so when it is the
    only key of a multi-line meta, the braces with everything between them
    become one ERROR right after the tag. That ERROR is logged the same way. An
    ERROR that starts with "{" but goes on past the closing "}" holds content,
    so it is left to be reported as a CST error.
    """
    skip = {
        n.id
        for n in (
            cst_node.child_by_field_name("tag"),
            *cst_node.children_by_field_name("title"),
        )
        if n is not None
    }
    after_tag = [c for c in cst_node.named_children if c.id not in skip]
    first = after_tag[0] if after_tag else None
    ids = set()
    for c in cst_node.named_children:
        if c.type != "ERROR" or not (c.text or b"").startswith(b"{"):
            continue
        only_braces = (
            first is not None
            and c.id == first.id
            and c.children[0].type == "{"
            and c.children[-1].type == "}"
        )
        if only_braces or any(n.type in _SHAPE_ALLOWED for n in _descendants(c)):
            _log_meta_error(c)
            ids.add(c.id)
    return ids


_TAG = re.compile(r":[a-z0-9][a-z0-9-]*:")


def _check_plain_title(val: str, pair: TSNode, meta: TSNode) -> None:
    """Raise when a :plain-title: holds anything other than plain text.

    The parser ends a text value where a key starts after a space, so a tag
    such as :math: or :label: written after a space shows up as another pair on
    the same line rather than in the value.
    """
    row = pair.start_point[0]
    same_line = any(
        c.id != pair.id and c.start_point[0] == row
        for c in meta.named_children
        if c.type == "pair"
    )
    if "$" in val or _TAG.search(val) or same_line:
        raise RSMParserError(msg=f"plain-title takes plain text only (line {row + 1})")


def _parse_meta_into_dict(node: TSNode) -> dict[str, Any]:
    # Only the pair children are read below, so an ERROR child would otherwise
    # be dropped with no message.
    rejected = []
    for err in [c for c in node.named_children if c.type == "ERROR"]:
        rejected += _log_meta_error(err)
    pairs = {}
    for pair in [c for c in node.named_children if c.type.endswith("pair")]:
        if pair.named_children[0].type == "metakey_unknown":
            name = (pair.named_children[0].text or b"").decode("utf-8")
            logger.error(
                f"Unknown meta key {name}",
                extra=_user_position(pair.start_point, pair.end_point),
            )
            continue
        if len(pair.named_children) == 1:  # bool meta key
            cst_key, val = pair.named_children[0], None
        else:
            cst_key, cst_val = pair.named_children
            val = _metaval_str(cst_val)
        key, val = globals()[f"_parse_{cst_key.type}"](cst_key, val)
        if key == "plain_title":
            _check_plain_title(val, pair, node)
        if not _value_is_valid(key, val, cst_key.type, pair):
            rejected.append(key)
            continue
        pairs[key] = val
    # The translator shortens the author list only when neither value was
    # rejected, so a rejected value is kept as None instead of being dropped.
    for key in _AUTHOR_DISPLAY_KEYS.intersection(rejected):
        pairs[key] = None
    return pairs


def _normalize_text(root: nodes.Node | None) -> str:
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
            # groupby keyed the run on isinstance(c, nodes.Text).
            run = cast(list[nodes.Text], list(run_generator))
            if len(run) < 2:
                continue

            # Watch the use of rstrip, strip, and lstrip here.
            pieces = [
                run[0].text.rstrip(),
                *[t.text.strip() for t in run[1:-1]],
                run[-1].text.lstrip(),
            ]

            # Error is a subclass of Text, but it must stay its own node: merging
            # it into the text next to it drops the span that marks it as an
            # error.  Only plain Text nodes are merged.  The spaces that the merge
            # would put around an Error go into the plain Text next to it, so the
            # output text is the same as when everything was merged.
            kept: list[tuple[nodes.Text, list[str]]] = []
            for t, piece in zip(run, pieces, strict=True):
                if (
                    kept
                    and not isinstance(t, nodes.Error)
                    and not isinstance(kept[-1][0], nodes.Error)
                ):
                    kept[-1][1].append(piece)
                    t.remove_self()
                else:
                    kept.append((t, [piece]))

            for i, (t, node_pieces) in enumerate(kept):
                text = " ".join(node_pieces)
                is_last = i == len(kept) - 1
                if not isinstance(t, nodes.Error):
                    if i > 0:
                        text = " " + text
                    if not is_last:
                        text += " "
                elif not is_last and isinstance(kept[i + 1][0], nodes.Error):
                    text += " "
                t.text = text

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

        # Return the space we borrowed from Construct nodes. The keyword and its
        # content must stay separated whatever the first content node is: fold the
        # space into a leading Text, otherwise restore it as its own Text node.
        # (Math used to be the only non-Text case handled; a leading Reference,
        # Span, Cite, ... fell through, and inline-block links trim their own
        # leading space, so e.g. ":assume: :ref:..." rendered as "ASSUMEthe ...".)
        if isinstance(node, nodes.Construct):
            first = node.children[0] if node.children else None
            if isinstance(first, nodes.Text):
                first.text = f" {first.text}"
            elif first is not None:
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
        # we simply insert a single space between them.  References and citations are
        # inline too, so e.g. "$x$ :cite:..." must not render glued as "x[1]",
        # and so are note and aside calls (":aside:x,a space:: $R^m$").
        classes = [
            nodes.NoteCall,
            nodes.Span,
            nodes.Construct,
            nodes.Math,
            nodes.Cite,
            nodes.PendingCite,
            nodes.Reference,
            nodes.URL,
            nodes.PendingReference,
            nodes.RawHtml,
        ]
        sibling = node.next_sibling()
        if sibling and type(node) in classes and type(sibling) in classes:
            node.replace_self([node, nodes.Text(" ")])

        # Manage escaped characters.
        if isinstance(node, nodes.Text) and not node.asis:
            node.text = EscapedString(node.text, DELIMS).escape()
        # Any titled node (sections, theorems, titled paragraphs) unescapes its
        # title the same way, so an escaped colon in a title renders as a colon.
        title = getattr(node, "title", None)
        if isinstance(title, str) and title:
            # getattr above found a title on this node.
            node.title = EscapedString(title, DELIMS).escape()  # type: ignore[attr-defined]

    return ""  # This function modifies nodes in place


def _group_nested_lists(root: "nodes.Node") -> None:
    """Rebuild each itemize/enumerate so deeper items nest under the item above.

    Items parse flat, each carrying a ``.depth`` from its marker (:-: = 1,
    :--: = 2, :---: = 3). This turns that flat sequence into a tree. A depth that
    skips the level above gets an inline Error node, consistent with how CST
    errors are surfaced.
    """
    # Snapshot the original containers first: the sub-lists created below are
    # themselves itemize/enumerate and must not be regrouped again.
    containers = [
        n for n in root.traverse() if isinstance(n, (nodes.Itemize, nodes.Enumerate))
    ]
    for container in containers:
        _regroup_list(container)


def _regroup_list(container: "nodes.NodeWithChildren") -> None:
    items = [c for c in container.children if isinstance(c, nodes.Item)]
    if all(getattr(it, "depth", 1) == 1 for it in items):
        return
    list_type = type(container)
    for it in items:
        container.remove(it)
    # stack[d-1] is the list node that accepts items at depth d.
    stack: list = [container]
    for item in items:
        depth = getattr(item, "depth", 1)
        if depth == len(stack):
            stack[-1].append(item)
        elif depth == len(stack) + 1:
            parents = [c for c in stack[-1].children if isinstance(c, nodes.Item)]
            if not parents:
                stack[-1].append(_depth_jump_error(item))
                stack[-1].append(item)
                continue
            sublist = list_type(start_point=item.start_point, end_point=item.end_point)
            parents[-1].append(sublist)
            sublist.append(item)
            stack.append(sublist)
        elif depth < len(stack):
            while len(stack) > depth:
                stack.pop()
            stack[-1].append(item)
        else:  # depth > len(stack) + 1: a skipped level
            stack[-1].append(_depth_jump_error(item))
            stack[-1].append(item)


def _depth_jump_error(item: "nodes.Item") -> "nodes.Error":
    return nodes.Error(
        f"[list item at depth {getattr(item, 'depth', '?')} skips the level above]",
        start_point=item.start_point,
        end_point=item.end_point,
    )


# The grammar parses these tags in a heading or a :title: only so that they can
# be reported here: a title does not hold links, note calls or raw HTML.
_NOT_IN_HEADING = {
    "ref",
    "cite",
    "url",
    "note",
    "aside",
    "html",
    "previous",
    "prev",
    "prev2",
    "prev3",
}


def _drop_tags_not_allowed_in_heading(
    title_children: list[TSNode], where: str = "a heading"
) -> list[TSNode]:
    kept = []
    for c in title_children:
        tag = c.named_children[0].type if c.type == "specialinline" else ""
        if tag in _NOT_IN_HEADING:
            pos = _user_position(c.start_point, c.end_point)
            logger.error(
                f"A :{tag}: on line {pos['start_row']} is not allowed in {where} "
                "and is left out",
                extra=pos,
            )
            continue
        kept.append(c)
    return kept


def _markup_title_children(meta: TSNode) -> list[TSNode]:
    """The pieces of a :title: value in this meta, if the title holds markup.
    A plain title is read as text by _parse_meta_into_dict."""
    for pair in meta.named_children:
        if pair.type == "pair" and pair.named_children[0].type == "metakey_title":
            pieces = [
                c for c in pair.named_children[1].named_children if c.type != "comment"
            ]
            if any(c.type != "text" for c in pieces):
                return _drop_tags_not_allowed_in_heading(pieces, "a title")
    return []


def _join_title_text(children: list[nodes.Node]) -> list[nodes.Node]:
    """Merge neighbouring Text nodes, which are left where a tag was taken out
    of a heading, with one space where either side had one."""
    joined: list[nodes.Node] = []
    for c in children:
        if joined and isinstance(c, nodes.Text) and isinstance(joined[-1], nodes.Text):
            left, right = joined[-1].text, c.text
            gap = " " if left[-1:].isspace() or right[:1].isspace() else ""
            joined[-1].text = left.rstrip() + gap + right.lstrip()
            c.remove_self()
            continue
        joined.append(c)
    return joined


def _flatten_reftext(reftext_nodes: "list[nodes.Node]") -> str:
    """Plain-text version of a marked-up reftext, for string contexts (the link
    title / accessible name / fallback). Collects the text of every Text node in
    order, so *emph* and $math$ contribute their contents without the markup."""
    parts: list[str] = []
    for node in reftext_nodes:
        if isinstance(node, nodes.Text):
            parts.append(node.text)
        elif isinstance(node, nodes.NodeWithChildren):
            parts.append(_flatten_reftext(list(node.children)))
    return "".join(parts)


# The :alt: of a :html: is a text meta value, so the grammar does not parse
# the inline math in it. It is split here instead.
_ALT_MATH = re.compile(r"(?<!\\)\$(.+?)(?<!\\)\$")


def _alt_nodes(alt: str) -> list[nodes.Node]:
    """The fallback of a :html: as inline nodes: text, and inline math for
    each $...$ in its :alt:."""
    result: list[nodes.Node] = []
    pos = 0
    for match in _ALT_MATH.finditer(alt):
        if match.start() > pos:
            result.append(nodes.Text(alt[pos : match.start()]))
        math = nodes.Math()
        math.append(nodes.Text(match.group(1), asis=True))
        result.append(math)
        pos = match.end()
    if pos < len(alt):
        result.append(nodes.Text(alt[pos:]))
    return result


_SECTIONING = {
    "part",
    "chapter",
    "section",
    "subsection",
    "subsubsection",
    "paragraph",
    "subparagraph",
}
_NO_NUMBER = "does not remove the number in RSM. Use :nonum: on the block."
_REF = (
    "in math is not a reference in RSM. Write :ref:<label>:: outside the math instead."
)
_STRUCTURE_COMMANDS = {
    "label": "in math is ignored by RSM. Give the block a :label: instead.",
    "tag": (
        "in math does not set the number in RSM. RSM numbers the block. "
        "Use :nonum: on the block to remove the number."
    ),
    "notag": _NO_NUMBER,
    "nonumber": _NO_NUMBER,
    "ref": _REF,
    "eqref": _REF,
    "cite": (
        "in math is not a citation in RSM. Write :cite:<key>:: outside the math "
        "instead."
    ),
    "caption": (
        "in math is ignored by RSM. Use :caption: in a :figure: or a :table: instead."
    ),
} | dict.fromkeys(
    _SECTIONING,
    "in math does not start a section in RSM. Use a heading such as ## Title instead.",
)
_STARRED_ENVS = {"align*", "gather*", "multline*", "flalign*", "alignat*", "equation*"}
# \\ and \% are matched as control symbols, so that the letters after \\ are not
# read as a command and a % after \ does not start a comment.
_MATH_TOKEN = re.compile(
    r"\\begin\s*\{(?P<env>[A-Za-z]+\*)\}|\\(?P<cmd>[A-Za-z]+)|\\.|%[^\n]*", re.DOTALL
)


def _warn_structure_commands(
    text: str, start_point: tuple[int, int], numbered: bool
) -> None:
    """Warn about each LaTeX command in math that is about document structure.

    `numbered` is whether the math is a block that RSM numbers. Only then does a
    starred environment try to remove a number.
    """
    for m in _MATH_TOKEN.finditer(text):
        name = m.group("cmd")
        if name in _STRUCTURE_COMMANDS:
            msg = f"\\{name} {_STRUCTURE_COMMANDS[name]}"
        elif numbered and m.group("env") in _STARRED_ENVS:
            msg = f"{m.group('env')} {_NO_NUMBER}"
        else:
            continue
        before = text[: m.start()].encode("utf-8")
        row = start_point[0] + before.count(b"\n")
        line_start = before.rfind(b"\n") + 1
        col = len(before) - line_start
        if line_start == 0:
            col += start_point[1]
        width = len(m.group(0).encode("utf-8"))
        logger.warning(msg, extra=_user_position((row, col), (row, col + width)))


def _check_raw_html(raw: nodes.RawHtml) -> None:
    """Put the fallback of a :html: in its place when it is part of a link's
    text (a :ref: or :url: reftext, or the phrase of an aside call), and warn
    when it has no fallback at all.

    The grammar keeps :html: out of reftext, but a span inside reftext can
    still hold one, and a link cannot hold live HTML."""
    extra = _user_position(raw.start_point, raw.end_point)
    link = raw.parent
    while link is not None and not isinstance(
        link, (nodes.BaseReference, nodes.NoteCall)
    ):
        link = link.parent
    if link is None:
        if not raw.alt:
            logger.warning(
                "An inline :html: has no :alt:, so nothing stands in for it in "
                "reference previews and in output other than HTML",
                extra=extra,
            )
        return

    logger.warning(
        "An inline :html: inside the text of a link shows its :alt: instead",
        extra=extra,
    )
    fallback = list(raw.children)
    raw.clear()
    parent = raw.parent
    # A :html: inside the text of a link always has a parent.
    assert parent is not None
    if any(c is raw for c in parent.children):
        raw.replace_self(fallback)
        return
    # Directly in a reference's reftext_nodes, which are not its children.
    siblings = cast(nodes.BaseReference, parent).reftext_nodes
    index = next(i for i, c in enumerate(siblings) if c is raw)
    for c in fallback:
        c.parent = parent
    siblings[index : index + 1] = fallback
    raw.parent = None


def _missing_to_report(root: TSNode) -> list[TSNode]:
    """The MISSING nodes in the tree that stand for a mistake in the source.

    tree-sitter repairs some invalid input by inserting a token (a MISSING
    node) instead of making an ERROR node. A paragraph end inserted right
    before '::' is left out: the scanner cannot find a paragraph end between an
    inline tag and '::' on the same line, so correct text such as
    'First, $x$ is real.::' gets one.
    """
    src = root.text or b""
    found = []
    stack = [root]
    while stack:
        node = stack.pop()
        if node.is_missing:
            before_halmos = src[node.start_byte :].lstrip(b" \t")[:2] == b"::"
            if not (node.type == "paragraph_end" and before_halmos):
                found.append(node)
        stack.extend(reversed(node.children))
    return found


# The characters after which the scanner ends text at a colon so that a tag can
# start (is_punctuation in tree-sitter-rsm/src/scanner.c), and the colon itself.
_TAG_CAN_FOLLOW = "([\"')].,;!?/-‘“:"


class CallAfterWord(NamedTuple):
    start_point: tuple[int, int]
    end_point: tuple[int, int]
    # The start of the ERROR node that the mistake leaves at a stray '::', or
    # None when the mistake leaves no such node.
    error_byte: int | None
    message: str


_CALL_AFTER_WORD = {
    "note": (rb"(\S+):note:([^\s:]*)\Z", "A footnote call"),
    "aside": (rb"(\S+):aside:([^:]*)\Z", "An aside call"),
}


def _stray_halmos_bytes(root: TSNode) -> list[int]:
    """The start bytes of the ERROR nodes that hold only a '::', in source order."""
    found = []
    stack = [root]
    while stack:
        node = stack.pop()
        if node.type == "ERROR" and (node.text or b"").strip() == b"::":
            found.append(node.start_byte)
        stack.extend(reversed(node.children))
    return found


def _closes_a_block(text: TSNode, halmos: int) -> bool:
    """Whether the '::' at byte `halmos` right after `text` closes a block."""
    node = text.parent
    while node is not None:
        last = node.children[-1] if node.children else None
        if last is not None and last.type == "::" and last.start_byte == halmos:
            return True
        if node.end_byte > halmos + 2:
            return False
        node = node.parent
    return False


def _calls_after_a_word(root: TSNode) -> list[CallAfterWord]:
    """The footnote and aside calls written right after a word, as in
    'fact:note:n1::' or 'phrase:aside:a,words::'.

    The scanner ends text at a colon only after whitespace or punctuation, so
    such a call stays in the text and its closing '::' is left over as an
    ERROR, or closes the block around the paragraph. In the second case the
    block's own '::' is the first stray '::' after the block, and it comes from
    the same mistake.
    """
    src = root.text or b""
    stray = _stray_halmos_bytes(root)
    found = []
    stack = [root]
    while stack:
        node = stack.pop()
        stack.extend(reversed(node.children))
        if node.type != "text" or src[node.end_byte : node.end_byte + 2] != b"::":
            continue
        matches = [
            (tag, what, m, node)
            for tag, (pattern, what) in _CALL_AFTER_WORD.items()
            if (m := re.search(pattern, node.text or b"")) is not None
        ]
        if not matches:
            # Inline markup in an aside phrase ends the text, so the call
            # starts in an earlier text sibling.
            prev = node.prev_sibling
            while prev is not None and not matches:
                pattern, what = _CALL_AFTER_WORD["aside"]
                if prev.type == "text" and (m := re.search(pattern, prev.text or b"")):
                    matches = [("aside", what, m, prev)]
                prev = prev.prev_sibling
        if not matches:
            continue
        tag, what, m, first = matches[0]
        word = m.group(1).decode("utf-8", errors="replace")
        if word[-1] in _TAG_CAN_FOLLOW:
            continue
        rest = src[first.start_byte + m.start(2) : node.end_byte].decode(
            "utf-8", errors="replace"
        )
        halmos = node.end_byte
        later = [b for b in stray if b >= halmos]
        error_byte = None
        if later and (later[0] == halmos or _closes_a_block(node, halmos)):
            error_byte = later[0]
            stray.remove(error_byte)
        row, col = first.start_point
        found.append(
            CallAfterWord(
                start_point=(row, col + m.end(1)),
                end_point=(node.end_point[0], node.end_point[1] + 2),
                error_byte=error_byte,
                message=(
                    f"{what} must come after a space. Put a space before "
                    f":{tag}:, as in '{word} :{tag}:{rest}::'"
                ),
            )
        )
    return found


def _report_missing(cst: TSTree, root: nodes.Manuscript) -> None:
    """Log each MISSING node to report, and put a CST error in the page right
    after the deepest node whose source holds it, as for an ERROR node. After,
    not inside: some blocks drop their content (a :toc:, for one)."""
    for missing in _missing_to_report(cst.root_node):
        point = missing.start_point
        pos = _user_position(point, missing.end_point)
        logger.warning("The CST contains errors.", extra=pos)
        holder: nodes.NodeWithChildren = root
        for node in root.traverse(nodeclass=nodes.NodeWithChildren):
            start, end = tuple(node.start_point), tuple(node.end_point)
            if start != (-1, -1) and start <= tuple(point) <= end:
                holder = node
        error = nodes.Error(
            f"[CST error at ({pos['start_row']}, {pos['start_col']}) - "
            f"({pos['end_row']}, {pos['end_col']})]",
            start_point=point,
            end_point=missing.end_point,
        )
        if holder is root:
            root.append(error)
        else:
            holder.replace_self([holder, error])


def _abstractify(cst: TSTree) -> nodes.Manuscript | None:
    ast_root_node: nodes.Manuscript | None = None
    bibliography_node = None
    seen_config = False  # Track if we've seen a config block
    # (reference node, holder) pairs whose reftext carries inline markup. The
    # holder collects the inline children as the main loop builds them; after the
    # loop they move onto the reference node's reftext_nodes.
    reftext_builds: list[tuple[nodes.BaseReference, nodes.Span]] = []
    # The same for headings whose title carries inline markup.
    title_builds: list[tuple[nodes.Heading, nodes.Span]] = []
    raw_html_nodes: list[nodes.RawHtml] = []
    # A footnote or aside call right after a word leaves a stray '::' as an
    # ERROR. The call's own message covers that ERROR, so the log gets no second
    # message, and the page shows the call's message there.
    message_at_error: dict[int, str] = {}
    for call in _calls_after_a_word(cst.root_node):
        logger.error(
            call.message, extra=_user_position(call.start_point, call.end_point)
        )
        if call.error_byte is not None:
            message_at_error[call.error_byte] = call.message
    stack: list[tuple[nodes.Node | None, TSNode]] = [(None, cst.root_node)]
    # The asserts below that a tree-sitter field or its text is not None hold
    # because the grammar always makes these fields, and the tree keeps the
    # source bytes that it was parsed from.

    def ingest_meta(ast_node: nodes.Node, meta: TSNode) -> None:
        ast_node.ingest_dict_as_meta(_parse_meta_into_dict(meta))
        pieces = _markup_title_children(meta)
        if pieces and isinstance(ast_node, nodes.Heading):
            holder = nodes.Span()
            title_builds.append((ast_node, holder))
            stack.extend(reversed([(holder, c) for c in pieces]))

    while stack:
        parent, cst_node = stack.pop()
        skip_these_ids = set()
        if cst_node.type == "comment":
            continue

        # Handle references block
        if cst_node.type == "references":
            bibliography_node = nodes.Bibliography()
            # The source_file node comes first and makes the root.
            assert ast_root_node is not None
            ast_root_node.append(bibliography_node)

            stack += reversed(
                [
                    (bibliography_node, c)
                    for c in cst_node.named_children
                    if c.type == "bibitem"
                ]
            )

            for c in [c for c in cst_node.named_children if c.type == "ERROR"]:
                where = _user_position(c.start_point, c.end_point)
                line_col = f"line {where['start_row']}, column {where['start_col']}"
                label = next((n for n in c.named_children if n.type == "label"), None)
                fix = (
                    "Write it as @kind{key, name = {...}, name = {...}}, with a "
                    "comma between fields."
                )
                if label is not None and label.text is not None:
                    key = label.text.decode("utf-8").strip()
                    msg = f"entry {key}: RSM cannot read this entry at {line_col}, skipped. {fix}"
                else:
                    msg = f"RSM cannot read this entry at {line_col}, skipped. {fix}"
                logger.warning(msg, extra=where)

            for c in [c for c in cst_node.named_children if c.type == "bibstring"]:
                name = _bib_field_name(c.named_children[1])
                logger.warning(
                    f"@string {name} is not used, skipped. Write the value in "
                    "each entry that uses it.",
                    extra=_user_position(c.start_point, c.end_point),
                )

            continue
        if cst_node.type == "bibitem":
            bib_node = nodes.Bibitem()
            kind_node = cst_node.child_by_field_name("kind")
            label_node = cst_node.child_by_field_name("label")
            assert kind_node is not None and kind_node.text is not None
            assert label_node is not None and label_node.text is not None
            bib_node.label = label_node.text.decode("utf-8")
            kind = kind_node.text.decode("utf-8").lstrip("@").lower()
            if kind not in _BIB_KINDS:
                logger.warning(
                    f"entry {bib_node.label}: kind @{kind} is not known to RSM, "
                    "read as @misc",
                    extra=_user_position(kind_node.start_point, kind_node.end_point),
                )
                kind = "misc"
            bib_node.kind = kind
            for part in cst_node.named_children:
                if part.type == "bibitempair":
                    _ingest_bib_field(bib_node, part)
                elif part.type == "ERROR":
                    logger.warning(
                        f"entry {bib_node.label}: RSM cannot read part of this "
                        "entry, skipped. Write each field as name = {...}, with a "
                        "comma between fields.",
                        extra=_user_position(part.start_point, part.end_point),
                    )

            # Bibitems are pushed with the Bibliography as their parent.
            assert isinstance(parent, nodes.Bibliography)
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

            # Sections with a hastag shurtcut ("# Section Title") have the title as
            # children with field name 'title', so we must extract that here.
            # Sections with a tag (":section:") have the title as a meta key, so
            # that is handled when meta is ingested.
            title_children = cst_node.children_by_field_name("title")
            for c in title_children:
                skip_these_ids.add(c.id)
            title_children = _drop_tags_not_allowed_in_heading(title_children)
            if len(title_children) > 1 or any(c.type != "text" for c in title_children):
                holder = nodes.Span()
                title_builds.append((ast_node, holder))
                stack += reversed([(holder, c) for c in title_children])
            elif title_children:
                assert title_children[0].text is not None
                ast_node.title = title_children[0].text.decode("utf-8").strip()

            if isinstance(ast_node, nodes.Manuscript):
                ast_root_node = ast_node
            if meta:
                ingest_meta(ast_node, meta)
            else:
                skip_these_ids |= _log_meta_errors_outside_meta(cst_node)

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
            # The same tags open a definition (a special block) and a call (a
            # special inline).
            if cst_node.type == "specialinline" and ast_node_type in ["note", "aside"]:
                ast_node_type = "notecall"

            # Tables are special because the entire contents are in the first children,
            # so we might as well add that with the current parent and ignore the
            # current node
            if ast_node_type == "table":
                stack.append((parent, cst_node.named_children[0]))
                continue

        elif cst_node.type == "mathblock":
            ast_node_type = "mathblock"

        elif cst_node.type == "td":
            # The td node becomes the TableDatum, so that it gets the cell's meta.
            # Its tdcontent child is unpacked into it by the branch below.
            ast_node_type = "td"

        elif cst_node.type == "tdcontent" and isinstance(parent, nodes.TableDatum):
            # A tdcontent is a cell of its own only in the short row form (:tr:
            # a : b ::). Inside a :td: the cell already exists.
            stack += reversed(
                [
                    (parent, c)
                    for c in cst_node.named_children
                    if c.type in PUSH_THESE_TYPES
                ]
            )
            continue

        elif cst_node.type == "paragraph":
            first = cst_node.named_children[0]
            if first.type in ["item", "caption"]:
                cst_node = first
            ast_node_type = cst_node.type

        elif cst_node.type in ["block", "inline"]:
            tag = cst_node.child_by_field_name("tag")
            assert tag is not None
            ast_node_type = tag.type
            skip_these_ids.add(tag.id)

            # Special handling for config block - inject metadata into Manuscript
            if ast_node_type == "config":
                # Check for multiple config blocks
                if seen_config:
                    raise RSMParserError(
                        msg="Multiple config blocks found. Only one config block is allowed per document."
                    )
                seen_config = True

                meta = cst_node.child_by_field_name("meta")
                if meta:
                    config_dict = _parse_meta_into_dict(meta)

                    # :lang: also names the language of code blocks, so it
                    # is checked as a language code only here.
                    if "lang" in config_dict and not _LANG_CODE.match(
                        config_dict["lang"]
                    ):
                        pair = next(
                            p
                            for p in meta.named_children
                            if p.type == "pair"
                            and p.named_children[0].named_children[0].type == "lang"
                        )
                        _log_bad_value(
                            "lang", config_dict.pop("lang"), _LANG_CODE_ALLOWED, pair
                        )

                    # Handle override_date -> date mapping
                    if "override_date" in config_dict:
                        config_dict["date"] = config_dict.pop("override_date")
                    # Inject config into manuscript node
                    if ast_root_node:
                        ast_root_node.ingest_dict_as_meta(config_dict)
                else:
                    skip_these_ids |= _log_meta_errors_outside_meta(cst_node)
                # Don't create a node, skip this block entirely
                continue

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
                assert cst_node.text is not None
                ast_node.text = cst_node.text.decode("utf-8")
        elif ast_node_type == "ERROR":
            pos = _user_position(cst_node.start_point, cst_node.end_point)
            text = message_at_error.get(cst_node.start_byte)
            if text is None:
                logger.warning("The CST contains errors.", extra=pos)
                text = (
                    f"[CST error at ({pos['start_row']}, {pos['start_col']}) - "
                    f"({pos['end_row']}, {pos['end_col']})]"
                )
            ast_node = nodes.Error(
                text,
                start_point=cst_node.start_point,
                end_point=cst_node.end_point,
            )
        else:
            raise RSMParserError(msg=f"not found {ast_node_type}")

        # Record a list item's nesting depth from its marker (:-: = 1, :--: = 2,
        # :---: = 3). _group_nested_lists reads it to build the nested tree.
        if ast_node_type == "item":
            marker = cst_node.child_by_field_name("marker")
            ast_node.depth = (
                cast(bytes, marker.text).decode("utf-8").count("-") if marker else 1
            )

        # process meta
        meta = cst_node.child_by_field_name("meta")
        if meta:
            ingest_meta(ast_node, meta)
        else:
            skip_these_ids |= _log_meta_errors_outside_meta(cst_node)

        # process some special tags
        if ast_node_type in [
            "math",
            "code",
            "mathblock",
            "codeblock",
            "algorithm",
            "notation",
        ]:
            # "asis_text" is not pushed to the stack for further processing so must
            # handle it here
            # A :codeblock: may end with a caption, after its code.
            asis = next(c for c in cst_node.named_children if c.type == "asis_text")
            assert asis.text is not None
            text = asis.text.decode("utf-8")
            child: nodes.Node
            if ast_node_type in ["math", "mathblock"]:
                numbered = (
                    ast_node_type == "mathblock"
                    and not ast_node.nonum
                    and not ast_node.preamble
                    and getattr(ast_root_node, "numbering", "section") != "none"
                )
                _warn_structure_commands(text, asis.start_point, numbered)
            if ast_node_type in ["code", "codeblock"]:
                child = nodes.SourceCode(text, lang=ast_node.lang)
            else:
                child = nodes.Text(text, asis=True)
            ast_node.append(child)

        if ast_node_type in ["html", "htmlblock"]:
            asis = cst_node.named_children[-1]
            assert asis.type == "asis_text"
            assert asis.text is not None
            ast_node.html = asis.text.decode("utf-8").strip()
            for child in _alt_nodes(ast_node.alt):
                ast_node.append(child)
            if ast_node_type == "html":
                raw_html_nodes.append(ast_node)

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
            target_node = cst_node.child_by_field_name("target")
            assert target_node is not None and target_node.text is not None
            ast_node.target = target_node.text.decode("utf-8")
            skip_these_ids.add(target_node.id)

            # The reftext of :ref: and :url: may hold several inline children
            # (text plus *emph*, $math$, code, :span:); :previous: keeps a single
            # text node. children_by_field_name returns them all in order.
            reftext_children = cst_node.children_by_field_name("reftext")
            for c in reftext_children:
                skip_these_ids.add(c.id)
            if reftext_children:
                has_markup = any(c.type != "text" for c in reftext_children)
                if has_markup:
                    # Build the inline nodes through the main loop (a throwaway
                    # holder collects them), then move them onto the reference
                    # after the loop. overwrite_reftext is filled then too, from
                    # the built nodes, so it is the plain-text flattening.
                    holder = nodes.Span()
                    reftext_builds.append((ast_node, holder))
                    stack += reversed([(holder, c) for c in reftext_children])
                else:
                    # The grammar keeps the space after the comma in the reftext
                    # token; strip it so the link text has no surrounding space.
                    # Link text that wraps onto more source lines arrives as one
                    # text child per line, joined here with single spaces.
                    ast_node.overwrite_reftext = " ".join(
                        cast(bytes, c.text).decode("utf-8").strip()
                        for c in reftext_children
                    )

            meta = cst_node.child_by_field_name("meta")
            if meta:
                ingest_meta(ast_node, meta)

        if ast_node_type == "notecall":
            target_node = cst_node.child_by_field_name("target")
            tag_node = cst_node.child_by_field_name("tag")
            assert target_node is not None and target_node.text is not None
            assert tag_node is not None
            ast_node.target = target_node.text.decode("utf-8")
            ast_node.tag = tag_node.type
            skip_these_ids.add(target_node.id)
            # A call holds only a label. Anything else after the tag (such as the
            # removed inline-content form ":note: some text ::") shows up as an
            # ERROR inside the call. The transformer reports it, since an Error
            # node made here would be merged into the neighboring text.
            if any(c.type == "ERROR" for c in cst_node.named_children):
                ast_node.malformed = True

        if ast_node_type.startswith("prev") and ast_node_type != "previous":
            if ast_node_type == "prev":
                target = 1
            else:
                target = int(ast_node_type[4:])
            ast_node.target = target

        if ast_node_type == "cite":
            target_node = cst_node.named_children[1]
            assert target_node.text is not None
            labels = target_node.text.decode("utf-8").split(",")
            ast_node.targetlabels = [label.strip() for label in labels]
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

    # Move the inline reftext nodes off their holders and onto the references.
    # Reparent directly (not via append, which rejects a node that already has a
    # parent) so the reference becomes their parent for any upward walk during
    # rendering.
    for ref_node, holder in reftext_builds:
        children = list(holder.children)
        holder._children = []
        for child in children:
            # The reference is not a NodeWithChildren, but it is the parent of
            # its reftext nodes for any upward walk.
            child.parent = ref_node  # type: ignore[assignment]
        ref_node.reftext_nodes = children
        ref_node.overwrite_reftext = _flatten_reftext(children).strip()

    # The title nodes stay children of their holder (unlike reftext nodes), so
    # that a node in the title can find its siblings when it is rendered.
    for heading, holder in title_builds:
        children = _join_title_text(list(holder.children))
        for child in children:
            # A title written over several lines keeps each line's indent.
            if isinstance(child, nodes.Text):
                child.text = re.sub(r"\s+", " ", child.text)
        if isinstance(children[0], nodes.Text):
            children[0].text = children[0].text.lstrip()
        if isinstance(children[-1], nodes.Text):
            # A comma at the end of a meta pair is dropped (see _metaval_str).
            text = children[-1].text.rstrip()
            children[-1].text = text[:-1].rstrip() if text.endswith(",") else text
        heading.title_nodes = children
        heading.title = _flatten_reftext(children).strip()

    for raw in raw_html_nodes:
        _check_raw_html(raw)

    # A CST that is too broken has an ERROR node as its root, not a source_file.
    if ast_root_node is None:
        return None

    _report_missing(cst, ast_root_node)

    for fig in list(ast_root_node.traverse(nodeclass=nodes.Figure)):
        block = next((c for c in fig.children if isinstance(c, nodes.HtmlBlock)), None)
        if block is not None:
            block.remove_self()
            fig.htmlblock = block

    _normalize_text(ast_root_node)
    return ast_root_node
