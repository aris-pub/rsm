"""Pandoc bridge for RSM: export and import.

Export direction: :class:`PandocTranslator` converts an RSM AST
(``nodes.Manuscript``) to a pandoc JSON AST dict, which pandoc then renders to
any supported output format (LaTeX, PDF, EPUB, DOCX, …).

Import direction: :class:`PandocImporter` converts a pandoc JSON AST dict
(produced by ``pandoc --to=json``) back to RSM source text.

Neither class calls pandoc directly; the subprocess invocations live in
:mod:`rsm.app`.  These classes only handle the RSM ↔ pandoc-JSON boundary.

Analogy with the rest of the codebase:

- ``Translator``: RSM AST → HTML string  (HTML is the final output, we own it)
- ``PandocTranslator``: RSM AST → pandoc JSON dict  (pandoc owns the final output)
- ``PandocImporter``: pandoc JSON dict → RSM source text  (we own the RSM text)
"""

import logging
import re
from datetime import datetime

from rsm import nodes
from rsm.bibextract import sanitize_key

logger = logging.getLogger("RSM").getChild("pandoc")

PANDOC_API_VERSION = [1, 23, 1]

_ISO_DATE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")

# Pandoc gives \date{...} as free text; RSM's :override-date: wants ISO 8601.
# These are the common human-written forms; anything else is left for the LLM
# host pass rather than guessed at.
_DATE_FORMATS = (
    ("%B %d, %Y", "%Y-%m-%d"),   # April 13, 2024
    ("%d %B %Y", "%Y-%m-%d"),    # 13 April 2024
    ("%b %d, %Y", "%Y-%m-%d"),   # Apr 13, 2024
    ("%d %b %Y", "%Y-%m-%d"),    # 13 Apr 2024
    ("%Y/%m/%d", "%Y-%m-%d"),
    ("%m/%d/%Y", "%Y-%m-%d"),
    ("%B %Y", "%Y-%m"),          # April 2024
)


def _normalize_date_to_iso(raw: str) -> str:
    s = raw.strip()
    if not s or _ISO_DATE.match(s):
        return s if _ISO_DATE.match(s) else ""
    for fmt, out in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).strftime(out)
        except ValueError:
            continue
    return ""


# ─── Export: RSM AST → pandoc JSON ───────────────────────────────────────────


class PandocTranslator:
    """Convert a ``nodes.Manuscript`` tree to a pandoc JSON AST dict.

    Usage::

        from rsm.pandoc import PandocTranslator
        ast = PandocTranslator().translate(manuscript)
        # ast is a dict ready to be json.dumps'd and piped to pandoc

    Note on :static:: when a :class:`~rsm.nodes.Figure` has a ``static``
    path set, that path is used as the image source instead of ``path``.
    This allows authors to provide a vector/high-res version for non-web
    export (e.g. PDF via LaTeX).
    """

    def translate(self, tree: nodes.Manuscript) -> dict:
        meta = self._build_meta(tree)
        blocks = self._walk_children_as_blocks(tree)
        return {"pandoc-api-version": PANDOC_API_VERSION, "meta": meta, "blocks": blocks}

    # ── Meta ──────────────────────────────────────────────────────────────────

    def _build_meta(self, node: nodes.Manuscript) -> dict:
        meta: dict = {}
        if node.title:
            meta["title"] = {"t": "MetaInlines", "c": [{"t": "Str", "c": node.title}]}
        authors = [n for n in node.traverse() if isinstance(n, nodes.Author)]
        if authors:
            author_entries = []
            for a in authors:
                if not a.name:
                    continue
                inlines: list[dict] = [{"t": "Str", "c": a.name}]
                if getattr(a, "affiliation", None):
                    inlines += [{"t": "Str", "c": f" — {a.affiliation}"}]
                if getattr(a, "email", None):
                    inlines += [
                        {"t": "Str", "c": " — "},
                        {"t": "Link", "c": [["", [], []], [{"t": "Str", "c": a.email}], [f"mailto:{a.email}", ""]]},
                    ]
                author_entries.append({"t": "MetaInlines", "c": inlines})
            if author_entries:
                meta["author"] = {"t": "MetaList", "c": author_entries}
        abstract_node = next(
            (n for n in node.traverse() if isinstance(n, nodes.Abstract)), None
        )
        if abstract_node:
            abs_blocks = self._walk_children_as_blocks(abstract_node)
            meta["abstract"] = {"t": "MetaBlocks", "c": abs_blocks}
        if node.date:
            date_str = (
                node.date.date().isoformat()
                if hasattr(node.date, "date")
                else str(node.date)
            )
            meta["date"] = {"t": "MetaInlines", "c": [{"t": "Str", "c": date_str}]}
        return meta

    # ── Block walker ──────────────────────────────────────────────────────────

    # Maps node type → method name.  Uses MRO: if a type is not listed,
    # the first ancestor that IS listed wins.  None means "skip silently".
    _BLOCK_DISPATCH: dict = {
        nodes.Section: "_block_section",       # Subsection, Subsubsection via MRO
        nodes.Paragraph: "_block_paragraph",   # Step via MRO
        nodes.Note: None,       # Aside via MRO, exported at its call
        nodes.MathBlock: "_block_mathblock",
        nodes.CodeBlock: "_block_codeblock",
        nodes.Enumerate: "_block_enumerate",
        nodes.Itemize: "_block_itemize",
        nodes.Item: "_block_item",
        nodes.Theorem: "_block_theorem",       # all Theorem subclasses via MRO
        nodes.Proof: "_block_proof",
        nodes.Sketch: "_block_proof",          # Sketch is NOT a subclass of Proof
        nodes.Figure: "_block_figure",
        nodes.Table: "_block_table",
        nodes.Bibliography: "_block_bibliography",
        nodes.Abstract: "_block_abstract",
        nodes.Author: None,     # consumed by _build_meta
        nodes.AuthorBlock: None, # consumed by _build_meta
        nodes.AuthorNotes: None, # consumed by _build_meta
        nodes.Appendix: None,   # marker only, no output
        nodes.Caption: None,    # consumed inside _block_figure / _block_table
        nodes.Draft: None,
        nodes.Algorithm: None,
        nodes.Contents: "_block_toc",
        nodes.Html: "_block_asset_placeholder",
        nodes.Video: "_block_asset_placeholder",
        nodes.Subproof: "_block_proof",       # same as Proof — recurse into children
        nodes.ClaimBlock: "_block_construct",
        nodes.Construct: "_block_construct",
        nodes.Statement: "_block_construct",
    }

    def _walk_block(self, node: nodes.Node) -> list[dict]:
        for cls in type(node).__mro__:
            if cls in self._BLOCK_DISPATCH:
                method_name = self._BLOCK_DISPATCH[cls]
                if method_name is None:
                    return []
                return getattr(self, method_name)(node)
        return self._block_fallback(node)

    def _walk_children_as_blocks(self, node: nodes.Node) -> list[dict]:
        result: list[dict] = []
        for child in node.children:
            result.extend(self._walk_block(child))
        return result

    # ── Inline walker ─────────────────────────────────────────────────────────

    _INLINE_DISPATCH: dict = {
        nodes.Text: "_inline_text",
        nodes.SourceCode: "_inline_sourcecode",  # raw text inside Math nodes
        nodes.Span: "_inline_span",              # Keyword via MRO
        nodes.Math: "_inline_math",
        nodes.Code: "_inline_code",
        nodes.Reference: "_inline_reference",
        nodes.URL: "_inline_url",
        nodes.Cite: "_inline_cite",
        nodes.NoteCall: "_inline_notecall",
        nodes.Error: "_inline_text",
    }

    def _walk_inline(self, node: nodes.Node) -> list[dict]:
        for cls in type(node).__mro__:
            if cls in self._INLINE_DISPATCH:
                method_name = self._INLINE_DISPATCH[cls]
                if method_name is None:
                    return []
                return getattr(self, method_name)(node)
        return self._inline_fallback(node)

    def _walk_children_as_inlines(self, node: nodes.Node) -> list[dict]:
        result: list[dict] = []
        for child in node.children:
            result.extend(self._walk_inline(child))
        return result

    # ── Block handlers ────────────────────────────────────────────────────────

    def _block_fallback(self, node: nodes.Node) -> list[dict]:
        logger.warning("PandocTranslator: no block handler for %s", type(node).__name__)
        return []

    def _block_section(self, node: nodes.Section) -> list[dict]:
        level = max(1, node.__class__.level - 1)
        anchor = node.label or ""
        title_inlines = [{"t": "Str", "c": node.title}] if node.title else []
        header = {"t": "Header", "c": [level, [anchor, [], []], title_inlines]}
        return [header] + self._walk_children_as_blocks(node)

    def _block_abstract(self, node: nodes.Abstract) -> list[dict]:
        return []

    def _block_paragraph(self, node: nodes.Paragraph) -> list[dict]:
        # Emit label if the paragraph has one
        label = getattr(node, "label", None)
        result: list[dict] = []
        if label and " " not in label:
            result.append({"t": "RawBlock", "c": ["typst", f'<{label}>']})
        return result + self._paragraph_content_blocks(node)

    def _paragraph_content_blocks(self, node: nodes.BaseParagraph) -> list[dict]:
        # A paragraph may contain block-level MathBlock / CodeBlock children.
        # Split at each such child: flush accumulated inlines as Para, emit the block.
        _BLOCK_IN_PARA = (nodes.MathBlock, nodes.CodeBlock)
        result: list[dict] = []
        current_inlines: list[dict] = []
        for child in node.children:
            if isinstance(child, _BLOCK_IN_PARA):
                if current_inlines:
                    result.append({"t": "Para", "c": current_inlines})
                    current_inlines = []
                result.extend(self._walk_block(child))
            else:
                current_inlines.extend(self._walk_inline(child))
        if current_inlines:
            result.append({"t": "Para", "c": current_inlines})
        return result

    _LATEX_ENVS = {"align", "align*", "gather", "gather*", "multline", "multline*",
                   "flalign", "flalign*", "alignat", "alignat*", "split"}

    def _block_mathblock(self, node: nodes.MathBlock) -> list[dict]:
        src = self._extract_math_source(node)
        num = node.full_number
        label = node.label or ""
        label_raw = [{"t": "RawBlock", "c": ["typst", f'<{label}>']}] if label and " " not in label else []

        stripped = src.strip()
        has_env = any(stripped.startswith(rf"\begin{{{env}}}") for env in self._LATEX_ENVS)
        if has_env:
            return label_raw + [{"t": "RawBlock", "c": ["latex", stripped]}]

        if num and not node.nonum:
            math_block = {"t": "Para", "c": [{"t": "Math", "c": [{"t": "DisplayMath"}, src]}]}
            num_block = {"t": "RawBlock", "c": ["typst",
                f'#v(-2.2em)\n#align(right, text(fill: rgb("#0361A1"))[({num})])\n#v(0.5em)'
            ]}
            return label_raw + [math_block, num_block]
        return label_raw + [{"t": "Para", "c": [{"t": "Math", "c": [{"t": "DisplayMath"}, src]}]}]

    def _block_codeblock(self, node: nodes.CodeBlock) -> list[dict]:
        src = self._extract_code_source(node)
        lang = [node.lang] if node.lang else []
        return [{"t": "CodeBlock", "c": [["", lang, []], src]}]

    def _block_enumerate(self, node: nodes.Enumerate) -> list[dict]:
        # _walk_block(item) dispatches to _block_item → [Para(inlines)]; each item
        # in pandoc OrderedList is a list of blocks, so the result is [[Para], ...].
        items = [
            self._walk_block(child)
            for child in node.children
            if isinstance(child, nodes.Item)
        ]
        list_attrs = [1, {"t": "Decimal"}, {"t": "Period"}]
        return [{"t": "OrderedList", "c": [list_attrs, items]}]

    def _block_itemize(self, node: nodes.Itemize) -> list[dict]:
        items = [
            self._walk_block(child)
            for child in node.children
            if isinstance(child, nodes.Item)
        ]
        return [{"t": "BulletList", "c": items}]

    def _block_item(self, node: nodes.Item) -> list[dict]:
        inlines = self._walk_children_as_inlines(node)
        return [{"t": "Para", "c": inlines}] if inlines else []

    def _block_theorem(self, node: nodes.Theorem) -> list[dict]:
        classname = type(node).__name__.lower()
        anchor = node.label or ""
        kvs = []
        if node.title:
            kvs.append(["title", node.title])
        inner = self._walk_children_as_blocks(node)
        return [{"t": "Div", "c": [[anchor, [classname, "theorem"], kvs], inner]}]

    def _block_proof(self, node: nodes.Proof) -> list[dict]:
        cls = "sketch" if isinstance(node, nodes.Sketch) else "proof"
        inner = self._walk_children_as_blocks(node)
        return [{"t": "Div", "c": [["", [cls], []], inner]}]

    def _block_figure(self, node: nodes.Figure) -> list[dict]:
        # Use :static: path for non-web export when available
        path = str(node.static) if node.static else str(node.path)
        alt_text = node.alt or f"Figure {node.full_number or ''}".strip()
        image = {"t": "Image", "c": [["", [], []], [{"t": "Str", "c": alt_text}], [path, ""]]}

        caption_node = node.first_of_type(nodes.Caption)
        if caption_node:
            cap_inlines = self._walk_children_as_inlines(caption_node)
            caption = [None, [{"t": "Para", "c": cap_inlines}]]
        else:
            caption = [None, []]

        anchor = node.label or ""
        return [{
            "t": "Figure",
            "c": [[anchor, ["figure"], []], caption, [{"t": "Plain", "c": [image]}]],
        }]

    def _block_toc(self, node) -> list[dict]:
        return [
            {"t": "RawBlock", "c": ["latex",
                "{\\hypersetup{linkcolor=braiid-gray-900}\\tableofcontents}\\newpage"]},
            {"t": "RawBlock", "c": ["typst",
                '#{\n'
                '  show outline: it => {\n'
                '    v(0.2em)\n'
                '    text(font: ("Montserrat", "Source Sans 3", "Source Sans Pro", "Noto Sans"), size: 16.5pt, weight: "medium", fill: rgb("#0C456E"))[Contents]\n'
                '    v(0.2em)\n'
                '    it\n'
                '  }\n'
                '  outline(indent: auto, depth: 3, title: none)\n'
                '}\n'
                '#v(0.5em)'
            ]},
        ]

    def _block_asset_placeholder(self, node: nodes.Node) -> list[dict]:
        # If a :static: fallback image exists, render it as a figure
        static = getattr(node, "static", None)
        if static:
            return self._block_figure(node)
        kind = type(node).__name__
        path = getattr(node, "path", "")
        text = f"[{kind} asset: {path} — see online version]" if path else f"[{kind} — see online version]"
        return [{"t": "Para", "c": [{"t": "Emph", "c": [{"t": "Str", "c": text}]}]}]

    def _block_construct(self, node: nodes.Node) -> list[dict]:
        return self._walk_children_as_blocks(node)

    def _block_bibliography(self, node: nodes.Bibliography) -> list[dict]:
        header = {
            "t": "Header",
            "c": [1, ["references", [], []], [{"t": "Str", "c": "References"}]],
        }
        items = [
            [self._format_bibitem(child)]
            for child in node.children
            if isinstance(child, nodes.Bibitem)
        ]
        if not items:
            return [header]
        bib_list = {
            "t": "OrderedList",
            "c": [[1, {"t": "Decimal"}, {"t": "Period"}], items],
        }
        return [header, bib_list]

    def _format_bibitem(self, node: nodes.Bibitem) -> dict:
        parts = []
        if node.author:
            parts.append(node.author)
        if node.title:
            parts.append(f'"{node.title}"')
        if node.journal:
            parts.append(node.journal)
        if node.year:
            parts.append(str(node.year))
        text = ". ".join(p.strip(".") for p in parts) + "." if parts else "?"
        anchor = f"ref-{node.label}" if node.label else ""
        inlines: list[dict] = [{"t": "Str", "c": text}]
        # Add DOI or URL as a clickable link
        link_url = None
        if getattr(node, "doi", None):
            link_url = f"https://doi.org/{node.doi}" if not node.doi.startswith("http") else node.doi
        elif getattr(node, "url", None):
            link_url = str(node.url)
        if link_url:
            inlines.append({"t": "Space"})
            inlines.append({"t": "Link", "c": [["", [], []], [{"t": "Str", "c": link_url}], [link_url, ""]]})
        if anchor:
            inlines.insert(0, {"t": "Span", "c": [[anchor, [], []], []]})
            inlines.append({"t": "RawInline", "c": ["typst", f" <{anchor}>"]})
        return {"t": "Para", "c": inlines}

    def _block_table(self, node: nodes.Table) -> list[dict]:
        head = node.first_of_type(nodes.TableHead)
        body = node.first_of_type(nodes.TableBody)
        head_rows = self._table_rows(head) if head else []
        body_rows = self._table_rows(body) if body else []

        all_rows = head_rows + body_rows
        # Rows are pandoc tuples encoded as bare arrays: Row = [attr, [Cell]].
        col_count = max(
            (len(r[1]) for r in all_rows),
            default=1,
        ) if all_rows else 1
        col_specs = [[{"t": "AlignDefault"}, {"t": "ColWidthDefault"}] for _ in range(col_count)]

        caption_node = node.first_of_type(nodes.Caption)
        if caption_node:
            cap_inlines = self._walk_children_as_inlines(caption_node)
            caption = [None, [{"t": "Para", "c": cap_inlines}]]
        else:
            caption = [None, []]

        # TableHead/TableBody/TableFoot are pandoc tuples (bare arrays), not tagged
        # union nodes; only Block/Inline/Alignment use the {"t":..,"c":..} form.
        # The table's label becomes the block id so cross-references resolve.
        return [{"t": "Table", "c": [
            [node.label or "", [], []],
            caption,
            col_specs,
            [["", [], []], head_rows],
            [[["", [], []], 0, [], body_rows]],
            [["", [], []], []],
        ]}]

    def _table_rows(self, node: nodes.NodeWithChildren) -> list[dict]:
        rows = []
        for row in node.children:
            if not isinstance(row, nodes.TableRow):
                continue
            cells = []
            for cell in row.children:
                if isinstance(cell, nodes.TableDatum):
                    inlines = self._walk_children_as_inlines(cell)
                    # Cell = [attr, Alignment, RowSpan, ColSpan, [Block]] (bare array).
                    cells.append([
                        ["", [], []],
                        {"t": "AlignDefault"},
                        1, 1,
                        [{"t": "Plain", "c": inlines}],
                    ])
            # Row = [attr, [Cell]] (bare array).
            rows.append([["", [], []], cells])
        return rows

    # ── Inline handlers ───────────────────────────────────────────────────────

    def _inline_fallback(self, node: nodes.Node) -> list[dict]:
        logger.warning("PandocTranslator: no inline handler for %s", type(node).__name__)
        return []

    def _inline_text(self, node: nodes.Text) -> list[dict]:
        if not node.text:
            return []
        result: list[dict] = []
        parts = node.text.split(" ")
        for i, word in enumerate(parts):
            if word:
                result.append({"t": "Str", "c": word})
            if i < len(parts) - 1:
                result.append({"t": "Space"})
        return result

    def _inline_sourcecode(self, node: nodes.SourceCode) -> list[dict]:
        # SourceCode children appear inside Math nodes; emit their raw text.
        return [{"t": "Str", "c": node.text}] if node.text else []

    def _inline_span(self, node: nodes.Span) -> list[dict]:
        inlines = self._walk_children_as_inlines(node)
        if node.strong:
            inlines = [{"t": "Strong", "c": inlines}]
        if node.emphas:
            inlines = [{"t": "Emph", "c": inlines}]
        if node.delete:
            inlines = [{"t": "Strikeout", "c": inlines}]
        if node.little:
            inlines = [{"t": "SmallCaps", "c": inlines}]
        if node.insert:
            inlines = [{"t": "Span", "c": [["", ["inserted"], []], inlines]}]
        return inlines

    def _inline_math(self, node: nodes.Math) -> list[dict]:
        src = self._extract_math_source(node)
        return [{"t": "Math", "c": [{"t": "InlineMath"}, src]}]

    def _inline_code(self, node: nodes.Code) -> list[dict]:
        src = self._extract_code_source(node)
        lang = [node.lang] if node.lang else []
        return [{"t": "Code", "c": [["", lang, []], src]}]

    def _inline_reference(self, node: nodes.Reference) -> list[dict]:
        if node.target is None:
            return []
        text = node.overwrite_reftext or (
            node.target.reftext if hasattr(node.target, "reftext") else str(node.target)
        )
        # For PDF export, :html: widgets with a :static: fallback are rendered
        # as figures — use "Figure" instead of "Widget" in cross-references.
        if (isinstance(node.target, nodes.Html)
                and getattr(node.target, "static", None)
                and text.startswith("Widget")):
            text = "Figure" + text[6:]
        anchor = (
            f"#{node.target.label}"
            if hasattr(node.target, "label") and node.target.label
            else "#"
        )
        # A normal pandoc Link to the target's anchor works across all output
        # formats (LaTeX \hyperref, HTML <a>, Typst #link); a format-specific
        # RawInline would be silently dropped whenever the export target differs.
        return [{"t": "Link", "c": [["", [], []], [{"t": "Str", "c": text}], [anchor, ""]]}]

    def _inline_url(self, node: nodes.URL) -> list[dict]:
        target = str(node.target)
        display = node.overwrite_reftext or target
        return [{"t": "Link", "c": [["", [], []], [{"t": "Str", "c": display}], [target, ""]]}]

    def _inline_cite(self, node: nodes.Cite) -> list[dict]:
        if not node.targets:
            return []
        # Render as clickable links [N] pointing to bibliography entries.
        result: list[dict] = [{"t": "Str", "c": "["}]
        for i, tgt in enumerate(node.targets):
            if i > 0:
                result.append({"t": "Str", "c": ", "})
            num = getattr(tgt, "number", None)
            label = tgt.label if hasattr(tgt, "label") and tgt.label else ""
            if num is not None and not isinstance(num, str):
                display = str(num)
            elif label:
                display = label
            else:
                display = "?"
            if label:
                anchor = f"#ref-{label}"
                result.append({"t": "Link", "c": [["", [], []], [{"t": "Str", "c": display}], [anchor, ""]]})
            else:
                result.append({"t": "Str", "c": display})
        result.append({"t": "Str", "c": "]"})
        return result

    def _inline_notecall(self, node: nodes.NoteCall) -> list[dict]:
        # Pandoc has no asides, so both kinds export as a footnote.
        if node.definition is None:
            return []
        return [{"t": "Note", "c": self._paragraph_content_blocks(node.definition)}]

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _extract_math_source(self, node: nodes.Node) -> str:
        return "".join(
            c.text
            for c in node.children
            if isinstance(c, (nodes.Text, nodes.SourceCode))
        ).strip()

    def _extract_code_source(self, node: nodes.Node) -> str:
        # In a parsed RSM document, the SourceCode is a child of Code/CodeBlock.
        # When nodes are created programmatically, the text is in node.source.text.
        src_child = node.first_of_type(nodes.SourceCode)
        if src_child is not None:
            return src_child.text
        if hasattr(node, "source") and node.source:
            return node.source.text
        return ""


# ─── Import: pandoc JSON → RSM source text ───────────────────────────────────


def _is_display_math(inline: dict) -> bool:
    return (
        isinstance(inline, dict)
        and inline.get("t") == "Math"
        and isinstance(inline.get("c"), list)
        and len(inline["c"]) >= 1
        and isinstance(inline["c"][0], dict)
        and inline["c"][0].get("t") == "DisplayMath"
    )


def _math_label(src: str) -> str | None:
    m = re.search(r"\\label\{([^}]*)\}", src)
    return m.group(1) if m else None


def _strip_trailing_colon(text: str) -> str:
    # \paragraph titles often end in a colon ("Encoder:"), which breaks RSM meta
    # value parsing and is a run-in convention, not part of the title.
    return text[:-1].rstrip() if text.endswith(":") else text


def _escape_trailing_colon(text: str) -> str:
    # A literal colon at the end of a paragraph is mis-tokenized before a
    # following tag block (:itemize:, :table:, ...), so emit it escaped. It
    # still renders as a plain colon.
    stripped = text.rstrip()
    # A :: is a construct close (:url: ... ::, :math: ... ::), not a literal
    # trailing colon, so leave it alone.
    if (
        stripped.endswith(":")
        and not stripped.endswith("::")
        and not stripped.endswith("\\:")
    ):
        return stripped[:-1] + "\\:"
    return text


class PandocImporter:
    """Convert a pandoc JSON AST dict to RSM source text.

    The input is the JSON produced by ``pandoc --to=json``.  The output is
    valid RSM markup that can be parsed by the RSM toolchain.

    Usage::

        import json, subprocess
        proc = subprocess.run(
            ["pandoc", "--from=markdown", "--to=json"],
            input=markdown_text, capture_output=True, text=True,
        )
        rsm_text = PandocImporter().from_json(json.loads(proc.stdout))
    """

    def from_json(self, pandoc_ast: dict) -> str:
        meta = pandoc_ast.get("meta", {})
        blocks = pandoc_ast.get("blocks", [])
        # Assign generated labels (sec-N, thm-N, eqn-N) and map each source
        # \label to its generated name, so a \ref emitted before its target
        # still resolves.
        self._label_of: dict[int, str] = {}
        self._ref_map: dict[str, str] = {}
        self._label_n = {"sec": 0, "thm": 0, "eqn": 0, "fig": 0, "tab": 0, "note": 0}
        self._pending_notes: list[str] = []
        self._assign_labels(blocks)
        # A LaTeX \paragraph (pandoc level 4+) is a run-in titled paragraph, not
        # a section. _block_header stashes its title here so the next paragraph
        # can carry it as :paragraph: {:title: ...}. _heading_stack renumbers the
        # real heading levels so none skips, which RSM's strict nesting rejects.
        self._pending_para: tuple[str, str | None] | None = None
        self._heading_stack: list[int] = []
        parts = [self._render_meta(meta)]
        for b in blocks:
            if self._pending_para is not None and b.get("t") != "Para":
                parts.append(self._flush_pending_para())
            parts.append(self._render_block(b))
            parts.extend(self._pending_notes)
            self._pending_notes = []
        if self._pending_para is not None:
            parts.append(self._flush_pending_para())
        return "".join(p for p in parts if p)

    def _flush_pending_para(self) -> str:
        """Emit a stashed \\paragraph title that no body paragraph followed."""
        title, label = self._pending_para
        self._pending_para = None
        if label:
            return f":paragraph: {{:label: {label}}}\n  **{title}**\n\n"
        return f"**{title}**\n\n"

    def _heading_depth(self, level: int) -> int:
        """Map a pandoc heading level to a contiguous RSM depth (no skips)."""
        stack = self._heading_stack
        while stack and stack[-1] >= level:
            stack.pop()
        stack.append(level)
        return len(stack)

    # ── Cross-reference labels (bead rsm-ddx.4) ─────────────────────────────────

    _THEOREM_CLASSES = (
        "theorem", "lemma", "corollary", "example", "exercise",
        "proposition", "problem",
    )

    def _next_label(self, kind: str) -> str:
        self._label_n[kind] += 1
        return f"{kind}-{self._label_n[kind]}"

    def _assign_labels(self, blocks: list) -> None:
        """Walk the AST, give sections, theorem-likes, and equations a label.

        The generated name is keyed by the identity of the node the emit handler
        receives, so the two passes agree without re-counting. A node's source
        \\label (a header or div id, or the \\label inside an equation) is mapped
        to the generated name so references resolve.
        """
        for b in blocks:
            if not isinstance(b, dict):
                continue
            t, c = b.get("t"), b.get("c")
            if t == "Header":
                gen = self._next_label("sec")
                self._label_of[id(c)] = gen
                if c[1][0]:
                    self._ref_map[c[1][0]] = gen
            elif t == "Div":
                attr, inner_blocks = c
                if any(cls in self._THEOREM_CLASSES for cls in attr[1]):
                    gen = self._next_label("thm")
                    self._label_of[id(c)] = gen
                    if attr[0]:
                        self._ref_map[attr[0]] = gen
                self._assign_labels(inner_blocks)
            elif t in ("Para", "Plain"):
                for inl in c:
                    if _is_display_math(inl):
                        gen = self._next_label("eqn")
                        self._label_of[id(inl)] = gen
                        lbl = _math_label(inl["c"][1])
                        if lbl:
                            self._ref_map[lbl] = gen
            elif t == "BlockQuote":
                self._assign_labels(c)
            elif t == "BulletList":
                for item in c:
                    self._assign_labels(item)
            elif t == "OrderedList":
                for item in c[1]:
                    self._assign_labels(item)
            elif t == "Figure":
                gen = self._next_label("fig")
                self._label_of[id(c)] = gen
                if c[0][0]:
                    self._ref_map[c[0][0]] = gen
                self._assign_labels(c[2])
            elif t == "Table":
                gen = self._next_label("tab")
                self._label_of[id(c)] = gen
                if c[0][0]:
                    self._ref_map[c[0][0]] = gen

    # ── Meta ──────────────────────────────────────────────────────────────────

    def _render_meta(self, meta: dict) -> str:
        parts: list[str] = []
        if "title" in meta:
            title = self._meta_to_text(meta["title"])
            if title:
                parts.append(f"# {title}\n\n")
        if "date" in meta:
            iso = _normalize_date_to_iso(self._meta_to_text(meta["date"]))
            if iso:
                parts.append(f":config: {{\n  :override-date: {iso}\n}}\n::\n\n")
        if "author" in meta:
            av = meta["author"]
            items = av.get("c", []) if av.get("t") == "MetaList" else [av]
            for item in items:
                name = self._author_name(item)
                if name:
                    parts.append(f":author: {{\n  :name: {name}\n}} ::\n\n")
        if "abstract" in meta:
            abstract = self._render_abstract(meta["abstract"])
            if abstract:
                parts.append(abstract)
        return "".join(parts)

    def _render_abstract(self, val: dict) -> str:
        # Pandoc stores the abstract as MetaBlocks (a list of block elements).
        # RSM's :abstract: wraps block content indented beneath the tag.
        if val.get("t") != "MetaBlocks":
            return ""
        inner = "".join(self._render_block(b) for b in val.get("c", [])).strip()
        if not inner:
            return ""
        body = "\n".join(f"  {line}" if line else line for line in inner.splitlines())
        return f":abstract:\n\n{body}\n\n::\n\n"

    def _author_name(self, item: dict) -> str:
        # An author's inlines carry the name, then a \thanks footnote (a Note)
        # and sometimes affiliation text. Keep only the plain name before the
        # footnote, whitespace collapsed, so :name: stays a valid single value.
        inlines = item.get("c", []) if item.get("t") == "MetaInlines" else []
        kept: list[dict] = []
        for inl in inlines:
            if inl.get("t") == "Note":
                break
            kept.append(inl)
        return " ".join(self._render_inlines(kept).split())

    def _meta_to_text(self, val: dict) -> str:
        t = val.get("t", "")
        c = val.get("c", [])
        if t == "MetaInlines":
            return self._render_inlines(c)
        if t == "MetaList":
            return " ".join(self._meta_to_text(item) for item in c)
        if t == "MetaString":
            return str(c)
        return ""

    # ── Block rendering ───────────────────────────────────────────────────────

    def _render_block(self, block: dict) -> str:
        t = block.get("t", "")
        c = block.get("c", [])
        method = getattr(self, f"_block_{t.lower()}", None)
        if method is not None:
            return method(c)
        logger.warning("PandocImporter: no handler for block type '%s'", t)
        return ""

    def _block_header(self, c: list) -> str:
        level, _attrs, inlines = c
        text = self._render_inlines(inlines)
        label = self._label_of.get(id(c))
        if level >= 4:
            self._pending_para = (_strip_trailing_colon(text), label)
            return ""
        # RSM reserves a single leading # for the manuscript title; its sections
        # start at ## (section), ### (subsection), #### (subsubsection). So a
        # pandoc \section (level 1) maps to ##, one deeper than its nesting depth.
        prefix = "#" * (self._heading_depth(level) + 1)
        meta = f"\n  {{:label: {label}}}" if label else ""
        return f"{prefix} {text}{meta}\n\n"

    def _block_para(self, c: list) -> str:
        titled = self._pending_para
        self._pending_para = None
        # DisplayMath inside Para inlines must be flushed as a block construct.
        result: list[str] = []
        pending: list[dict] = []
        for inline in c:
            if (
                inline.get("t") == "Math"
                and isinstance(inline.get("c"), list)
                and len(inline["c"]) >= 1
                and inline["c"][0].get("t") == "DisplayMath"
            ):
                if pending:
                    text = self._render_inlines(pending)
                    if text:
                        result.append(f"{_escape_trailing_colon(text)}\n\n")
                    pending = []
                src = inline["c"][1] if len(inline["c"]) >= 2 else ""
                src = re.sub(r"\\label\{[^}]*\}", "", src)
                label = self._label_of.get(id(inline))
                meta = f" {{:label: {label}}}" if label else ""
                result.append(f":mathblock:{meta}\n  {src}\n::\n\n")
            else:
                pending.append(inline)
        if pending:
            text = self._render_inlines(pending)
            if text:
                result.append(f"{_escape_trailing_colon(text)}\n\n")
        body = "".join(result)
        if titled is None:
            return body
        title, label = titled
        # A meta value cannot hold a bare colon, so escape internal colons; the
        # grammar accepts \: and it renders as a plain colon.
        title = title.replace(":", "\\:")
        meta = f"{{:title: {title}}}" if not label else (
            f"{{:title: {title}, :label: {label}}}"
        )
        indented = "\n".join(
            f"  {line}" if line else line for line in body.rstrip().splitlines()
        )
        return f":paragraph: {meta}\n{indented}\n\n"

    def _block_plain(self, c: list) -> str:
        # Pandoc uses Plain (no trailing newline) in list items and table cells.
        text = self._render_inlines(c)
        return text if text else ""

    def _block_bulletlist(self, c: list) -> str:
        items = self._list_item_lines(c, 1)
        return ":itemize:\n\n" + "\n\n".join(items) + "\n\n::\n\n"

    def _block_orderedlist(self, c: list) -> str:
        _list_attrs, item_list = c
        items = self._list_item_lines(item_list, 1)
        return ":enumerate:\n\n" + "\n\n".join(items) + "\n\n::\n\n"

    def _list_item_lines(self, pandoc_items: list, depth: int) -> list[str]:
        # Emit a flat sequence of items with depth markers (:-:, :--:, :---:),
        # recursing one level deeper into a nested list. RSM has no mixed list
        # types and only three levels, so a nested ordered/bulleted list just
        # continues the outer container and the marker caps at three dashes.
        marker = ":" + "-" * min(depth, 3) + ":"
        lines: list[str] = []
        for item_blocks in pandoc_items:
            text_blocks: list = []
            sublists: list = []
            for b in item_blocks:
                t = b.get("t") if isinstance(b, dict) else None
                if t == "BulletList":
                    sublists.append(b.get("c", []))
                elif t == "OrderedList":
                    sublists.append(b.get("c", [None, []])[1])
                else:
                    text_blocks.append(b)
            text = "".join(self._render_block(b).strip() for b in text_blocks)
            # An item is a single inline paragraph, so fold internal paragraph or
            # line breaks (e.g. from a \\ in the source) into spaces; otherwise
            # the extra paragraph breaks out of the list and orphans later items.
            text = re.sub(r"\s*\n\s*", " ", text).strip()
            if text:
                lines.append(f"  {marker} {text}")
                child_depth = depth + 1
            else:
                # An item that is only a nested list keeps that list at this
                # level, so it still sits under a marker above it.
                child_depth = depth
            for subitems in sublists:
                lines.extend(self._list_item_lines(subitems, min(child_depth, 3)))
        return lines

    def _block_codeblock(self, c: list) -> str:
        attrs, code = c
        _id, classes, _kv = attrs
        lang = classes[0] if classes else ""
        meta = f" {{:lang: {lang}}}" if lang else ""
        indented = "\n".join("  " + line for line in code.splitlines())
        return f":codeblock:{meta}\n{indented}\n::\n\n"

    def _block_rawblock(self, c: list) -> str:
        fmt, raw = c
        if fmt == "latex":
            indented = "\n".join("  " + line for line in raw.strip().splitlines())
            return f":mathblock:\n{indented}\n::\n\n"
        logger.warning("PandocImporter: skipping RawBlock with format '%s'", fmt)
        return ""

    def _block_horizontalrule(self, c: list) -> str:
        return ""  # No RSM equivalent; silently skip

    def _block_blockquote(self, c: list) -> str:
        inner = "".join(self._render_block(b) for b in c)
        indented = "\n".join("  " + line for line in inner.splitlines() if line)
        return f"{indented}\n\n"

    def _block_div(self, c: list) -> str:
        attrs, blocks = c
        _id, classes, _kv = attrs
        # pandoc wraps a LaTeX bibliography in a Div with this class, but it drops
        # the \bibitem keys and collapses the entries into one paragraph. The real
        # references are recovered from the source by rsm.bibextract and emitted
        # separately (bead rsm-ddx.5.4), so drop pandoc's unusable copy here.
        if "thebibliography" in classes:
            return ""
        inner = "".join(self._render_block(b) for b in blocks).strip()
        label = self._label_of.get(id(c))
        meta = f" {{:label: {label}}}" if label else ""
        # Map well-known classes to RSM constructs
        for cls in classes:
            if cls == "proof":
                return f":proof:\n\n{inner}\n\n::\n\n"
            if cls in self._THEOREM_CLASSES:
                return f":{cls}:{meta}\n\n{inner}\n\n::\n\n"
        # Unknown Div: emit inner content directly
        return f"{inner}\n\n" if inner else ""

    def _block_figure(self, c: list) -> str:
        _attrs, caption_obj, content_blocks = c
        path = ""
        for block in content_blocks:
            if block.get("t") == "Plain":
                for inline in block.get("c", []):
                    if inline.get("t") == "Image":
                        path = inline["c"][2][0]
        caption_text = ""
        # A pandoc Figure caption is a list [short-caption, [blocks]], not a
        # node with a "c" key, so read the blocks positionally.
        if isinstance(caption_obj, list) and len(caption_obj) >= 2:
            cap_blocks = caption_obj[1]
            if cap_blocks:
                caption_text = "".join(
                    self._render_block(b).strip() for b in cap_blocks
                )
        caption_line = f"\n  :caption: {caption_text}" if caption_text else ""
        # A figure's :path: and :label: live in a multi-line block meta, not an
        # inline {...}; the inline form does not parse as a block. An empty path
        # (missing or a non-web image) is dropped so no broken {:path: } is left.
        label = self._label_of.get(id(c))
        meta_lines = []
        if path:
            meta_lines.append(f"  :path: {path}")
        if label:
            meta_lines.append(f"  :label: {label}")
        block_meta = " {\n" + "\n".join(meta_lines) + "\n}" if meta_lines else ""
        if not block_meta and not caption_text:
            return ""
        return f":figure:{block_meta}{caption_line}\n::\n\n"

    def _block_table(self, c: list) -> str:
        # pandoc Table: [attr, caption, colspecs, head, [bodies], foot].
        if len(c) < 5:
            logger.warning("PandocImporter: unexpected Table shape, skipping")
            return ""
        _attr, _caption, _colspecs, head, bodies = c[0], c[1], c[2], c[3], c[4]
        head_rows = head[1] if isinstance(head, list) and len(head) >= 2 else []
        body_rows: list = []
        for body in bodies:
            # TableBody: [attr, rowHeadColumns, intermediate_head_rows, rows].
            if isinstance(body, list) and len(body) >= 4:
                body_rows.extend(body[2])
                body_rows.extend(body[3])
        label = self._label_of.get(id(c))
        meta = f" {{\n  :label: {label}\n}}" if label else ""
        parts = [f":table:{meta}\n\n"]
        if head_rows:
            parts.append("  :thead:\n\n" + self._table_rows(head_rows) + "  ::\n\n")
        if body_rows:
            parts.append("  :tbody:\n\n" + self._table_rows(body_rows) + "  ::\n\n")
        parts.append("::\n\n")
        return "".join(parts)

    def _table_rows(self, rows: list) -> str:
        out = []
        for row in rows:
            # Row: [attr, [Cell]]; Cell: [attr, align, rowspan, colspan, [blocks]].
            cells = row[1] if isinstance(row, list) and len(row) >= 2 else []
            tds = []
            for cell in cells:
                blocks = cell[4] if isinstance(cell, list) and len(cell) >= 5 else []
                content = "".join(self._render_block(b).strip() for b in blocks)
                tds.append(f":td:{content}::")
            out.append("    :tr: " + " ".join(tds) + " ::\n\n")
        return "".join(out)

    def _block_lineblock(self, c: list) -> str:
        lines = [self._render_inlines(line) for line in c]
        return "\n".join(lines) + "\n\n"

    # ── Inline rendering ──────────────────────────────────────────────────────

    def _render_inlines(self, inlines: list) -> str:
        return "".join(self._render_inline(i) for i in inlines)

    def _render_inline(self, inline: dict) -> str:
        t = inline.get("t", "")
        c = inline.get("c", [])
        method = getattr(self, f"_inline_{t.lower()}", None)
        if method is not None:
            return method(c)
        logger.warning("PandocImporter: no handler for inline type '%s'", t)
        return ""

    def _inline_str(self, c) -> str:
        return c

    def _inline_space(self, c) -> str:
        return " "

    def _inline_softbreak(self, c) -> str:
        return " "

    def _inline_linebreak(self, c) -> str:
        return "\n\n"

    def _inline_emph(self, c: list) -> str:
        return f"*{self._render_inlines(c)}*"

    def _inline_strong(self, c: list) -> str:
        return f"**{self._render_inlines(c)}**"

    def _inline_strikeout(self, c: list) -> str:
        return f":span: {{:delete:}} {self._render_inlines(c)} ::"

    def _inline_smallcaps(self, c: list) -> str:
        return f":span: {{:little:}} {self._render_inlines(c)} ::"

    def _inline_code(self, c: list) -> str:
        attrs, code = c
        _id, classes, _kv = attrs
        lang = classes[0] if classes else ""
        meta = f" {{:lang: {lang}}}" if lang else ""
        return f":code:{meta} {code} ::"

    def _inline_math(self, c: list) -> str:
        math_type, src = c
        is_display = isinstance(math_type, dict) and math_type.get("t") == "DisplayMath"
        # $...$ sits directly against adjacent text; the verbose :math: ... ::
        # form cannot. Fall back to it for display math (handled by _block_para
        # normally) or when the TeX holds a $ that would close the delimiter.
        if is_display or "$" in src:
            return f":math: {src} ::"
        return f"${src}$"

    def _inline_link(self, c: list) -> str:
        attrs, _inlines, target = c
        kv = dict(attrs[2]) if len(attrs) >= 3 else {}
        # pandoc marks \ref/\eqref/\autoref links with a reference-type; emit an
        # RSM :ref: to the generated label instead of a URL link.
        if "reference-type" in kv:
            tgt = kv.get("reference") or target[0].lstrip("#")
            return f":ref:{sanitize_key(self._ref_map.get(tgt, tgt))}::"
        return f":url: {target[0]} ::"

    def _inline_image(self, c: list) -> str:
        _attrs, _alt, target = c
        path = target[0]
        if not path:
            return ""
        return f":figure: {{\n  :path: {path}\n}}\n::"

    def _inline_cite(self, c: list) -> str:
        citations, _fallback = c
        return "".join(
            f":cite:{sanitize_key(cite['citationId'])}::" for cite in citations
        )

    def _inline_note(self, c: list) -> str:
        # The note's text becomes a definition placed after the current top-level
        # block (see from_json), and only the call stays inline. A definition holds
        # one paragraph, so the note's paragraphs are joined into one. Rendering
        # the blocks here must not consume a stashed run-in paragraph title.
        saved_para, self._pending_para = self._pending_para, None
        inner = " ".join(self._render_block(b).strip() for b in c)
        self._pending_para = saved_para
        inner = re.sub(r"\n\s*\n", "\n", inner).strip()
        label = self._next_label("note")
        self._pending_notes.append(f":note: {{:label: {label}}} {inner} ::\n\n")
        # The leading space lets the tag be read as a tag after a word. The
        # transformer removes it so the marker sits against that word.
        return f" :note:{label}::"

    def _inline_rawinline(self, c: list) -> str:
        fmt, raw = c
        if fmt == "latex":
            return f":math: {raw} ::"
        logger.warning("PandocImporter: skipping RawInline with format '%s'", fmt)
        return ""

    def _inline_span(self, c: list) -> str:
        _attrs, inlines = c
        return self._render_inlines(inlines)

    def _inline_quoted(self, c: list) -> str:
        quote_type, inlines = c
        text = self._render_inlines(inlines)
        return f"'{text}'" if quote_type.get("t") == "SingleQuote" else f'"{text}"'

    def _inline_superscript(self, c: list) -> str:
        return self._render_inlines(c)

    def _inline_subscript(self, c: list) -> str:
        return self._render_inlines(c)
